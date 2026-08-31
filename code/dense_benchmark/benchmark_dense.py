from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHILDREN = ROOT / "data" / "chunks" / "childrenchunks.json"
DEFAULT_MODELS = Path(__file__).with_name("models.json")
DEFAULT_QUERIES = Path(__file__).with_name("queries.json")
DEFAULT_OUTPUT = Path(__file__).with_name("results")
PROJECT_MODEL_CACHE = ROOT / ".cache" / "models"
HUGGINGFACE_CACHE = ROOT / ".cache" / "huggingface"
RECALL_CUTOFFS = (1, 5, 10, 20, 100)


@dataclass(frozen=True)
class ModelSpec:
    name: str
    model_id: str
    query_prefix: str = ""
    document_prefix: str = ""
    trust_remote_code: bool = False


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def corpus_text(child: dict[str, Any]) -> str:
    heading = " ".join(child.get("heading_path") or [])
    return f"{heading} {child['text']}".strip()


def cache_path(cache_dir: Path, spec: ModelSpec, corpus_path: Path) -> Path:
    digest = hashlib.sha256()
    digest.update(spec.model_id.encode("utf-8"))
    digest.update(spec.document_prefix.encode("utf-8"))
    with corpus_path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return cache_dir / f"{spec.name}-{digest.hexdigest()[:16]}.npy"


def model_source(spec: ModelSpec, use_project_snapshots: bool = True) -> tuple[str, str]:
    """Prefer the application's immutable local snapshot when it is available."""
    if not use_project_snapshots:
        return spec.model_id, "huggingface"
    model_hash = hashlib.sha256(spec.model_id.encode("utf-8")).hexdigest()[:12]
    snapshot = PROJECT_MODEL_CACHE / f"embedding-{model_hash}"
    metadata_path = snapshot / "snapshot.json"
    if metadata_path.is_file():
        metadata = read_json(metadata_path)
        if metadata.get("model_name") == spec.model_id:
            return str(snapshot), "project_snapshot"
    return spec.model_id, "huggingface"


def encode_documents(
    model: SentenceTransformer,
    spec: ModelSpec,
    documents: list[str],
    corpus_path: Path,
    cache_dir: Path,
    batch_size: int,
) -> tuple[np.ndarray, float, str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path(cache_dir, spec, corpus_path)
    if path.is_file():
        started = time.perf_counter()
        embeddings = np.load(path)
        return embeddings, time.perf_counter() - started, "cache"

    started = time.perf_counter()
    embeddings = model.encode(
        [f"{spec.document_prefix}{text}" for text in documents],
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype(np.float32)
    elapsed = time.perf_counter() - started
    np.save(path, embeddings)
    return embeddings, elapsed, "encoded"


def relevant_rank(ranked_indices: np.ndarray, relevant_indices: set[int]) -> int | None:
    for rank, index in enumerate(ranked_indices.tolist(), start=1):
        if index in relevant_indices:
            return rank
    return None


def validate_queries(
    children: list[dict[str, Any]], queries: list[dict[str, Any]]
) -> tuple[int, int]:
    child_ids = {child["child_id"] for child in children}
    seen_query_ids: set[str] = set()
    positive_queries = 0
    negative_queries = 0

    for query in queries:
        query_id = query.get("id")
        if not query_id:
            raise ValueError("Every query must have a non-empty id.")
        if query_id in seen_query_ids:
            raise ValueError(f"Duplicate query id: {query_id}")
        seen_query_ids.add(query_id)

        text = query.get("query", "").strip()
        if not text:
            raise ValueError(f"Query {query_id} is missing text.")

        relevant_ids = query.get("relevant_child_ids")
        if not isinstance(relevant_ids, list):
            raise ValueError(f"Query {query_id} must define relevant_child_ids as a list.")
        missing = [child_id for child_id in relevant_ids if child_id not in child_ids]
        if missing:
            raise ValueError(f"Unknown relevant_child_ids for {query_id}: {missing}")

        if relevant_ids:
            positive_queries += 1
        else:
            negative_queries += 1

    return positive_queries, negative_queries


def evaluate_model(
    spec: ModelSpec,
    children: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    corpus_path: Path,
    cache_dir: Path,
    batch_size: int,
    device: str | None,
    use_project_snapshots: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from sentence_transformers import SentenceTransformer

    load_started = time.perf_counter()
    source, source_kind = model_source(spec, use_project_snapshots)
    model = SentenceTransformer(
        source,
        trust_remote_code=spec.trust_remote_code,
        device=device,
        cache_folder=str(HUGGINGFACE_CACHE),
    )
    load_seconds = time.perf_counter() - load_started

    documents = [corpus_text(child) for child in children]
    document_embeddings, indexing_seconds, index_source = encode_documents(
        model, spec, documents, corpus_path, cache_dir, batch_size
    )
    child_index = {child["child_id"]: index for index, child in enumerate(children)}

    detail_rows: list[dict[str, Any]] = []
    query_latencies: list[float] = []
    reciprocal_ranks: list[float] = []
    recall_hits = {cutoff: 0 for cutoff in RECALL_CUTOFFS}
    all_hits = {cutoff: 0 for cutoff in RECALL_CUTOFFS}
    coverage_sums = {cutoff: 0.0 for cutoff in RECALL_CUTOFFS}
    negative_top_scores: list[float] = []
    positive_query_count = 0
    negative_query_count = 0

    for query in queries:
        relevant_ids = query["relevant_child_ids"]
        relevant = {child_index[item] for item in relevant_ids}
        query_category = "negative" if not relevant_ids else query.get("category", "positive")

        started = time.perf_counter()
        query_embedding = model.encode(
            [f"{spec.query_prefix}{query['query']}"],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0].astype(np.float32)
        scores = document_embeddings @ query_embedding
        ranked = np.argsort(-scores)
        latency_ms = (time.perf_counter() - started) * 1000
        top_index = int(ranked[0])
        top_score = float(scores[top_index])

        if relevant:
            positive_query_count += 1
            rank = relevant_rank(ranked, relevant)
            reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
            for cutoff in RECALL_CUTOFFS:
                top_k = set(ranked[:cutoff].tolist())
                retrieved_relevant = len(top_k & relevant)
                coverage = retrieved_relevant / len(relevant)
                coverage_sums[cutoff] += coverage
                recall_hits[cutoff] += int(rank is not None and rank <= cutoff)
                all_hits[cutoff] += int(retrieved_relevant == len(relevant))
        else:
            negative_query_count += 1
            rank = None
            negative_top_scores.append(top_score)

        query_latencies.append(latency_ms)
        top_5_ids = [children[index]["child_id"] for index in ranked[:5].tolist()]
        retrieved_relevant_top_10 = [
            children[index]["child_id"] for index in ranked[:10].tolist() if index in relevant
        ]
        detail_rows.append(
            {
                "model": spec.name,
                "query_id": query["id"],
                "category": query_category,
                "relevant_count": len(relevant_ids),
                "first_relevant_rank": rank,
                "query_latency_ms": round(latency_ms, 2),
                "top_child_id": children[top_index]["child_id"],
                "top_score": round(top_score, 6),
                "relevant_score": (
                    round(max(float(scores[index]) for index in relevant), 6) if relevant else None
                ),
                "top_5_child_ids": "|".join(top_5_ids),
                "retrieved_relevant_top_10": "|".join(retrieved_relevant_top_10),
            }
        )
        for cutoff in RECALL_CUTOFFS:
            if relevant:
                top_k = set(ranked[:cutoff].tolist())
                retrieved_relevant = len(top_k & relevant)
                detail_rows[-1][f"any_hit_at_{cutoff}"] = int(retrieved_relevant > 0)
                detail_rows[-1][f"all_hit_at_{cutoff}"] = int(retrieved_relevant == len(relevant))
                detail_rows[-1][f"coverage_at_{cutoff}"] = round(
                    retrieved_relevant / len(relevant), 6
                )
            else:
                detail_rows[-1][f"any_hit_at_{cutoff}"] = None
                detail_rows[-1][f"all_hit_at_{cutoff}"] = None
                detail_rows[-1][f"coverage_at_{cutoff}"] = None

    count = len(queries)
    summary: dict[str, Any] = {
        "model": spec.name,
        "model_id": spec.model_id,
        "model_source": source_kind,
        "query_prefix": spec.query_prefix,
        "document_prefix": spec.document_prefix,
        "queries": count,
        "positive_queries": positive_query_count,
        "negative_queries": negative_query_count,
        "mrr": round(float(np.mean(reciprocal_ranks)), 6) if reciprocal_ranks else 0.0,
        "median_query_latency_ms": round(float(np.median(query_latencies)), 2),
        "model_load_seconds": round(load_seconds, 2),
        "document_index_seconds": round(indexing_seconds, 2),
        "document_index_source": index_source,
    }
    if positive_query_count:
        summary.update(
            {
                f"recall_at_{cutoff}": round(recall_hits[cutoff] / positive_query_count, 6)
                for cutoff in RECALL_CUTOFFS
            }
        )
        summary.update(
            {
                f"all_recall_at_{cutoff}": round(all_hits[cutoff] / positive_query_count, 6)
                for cutoff in RECALL_CUTOFFS
            }
        )
        summary.update(
            {
                f"mean_coverage_at_{cutoff}": round(
                    coverage_sums[cutoff] / positive_query_count, 6
                )
                for cutoff in RECALL_CUTOFFS
            }
        )
    if negative_top_scores:
        summary["negative_mean_top_score"] = round(float(np.mean(negative_top_scores)), 6)
        summary["negative_p90_top_score"] = round(float(np.percentile(negative_top_scores, 90)), 6)
    return summary, detail_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare dense retrievers on Constitution chunks.")
    parser.add_argument("--children", type=Path, default=DEFAULT_CHILDREN)
    parser.add_argument("--models", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--cache-dir", type=Path, default=ROOT / ".cache" / "dense_benchmark"
    )
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", default=None, help="For example: cpu, cuda, cuda:0")
    parser.add_argument("--only", nargs="*", help="Run only these model names from models.json")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate query ids, syntax, and relevant child ids without loading embedding models.",
    )
    parser.add_argument(
        "--ignore-project-snapshots",
        action="store_true",
        help="Load model IDs from Hugging Face instead of application snapshots.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    children = read_json(args.children)
    queries = read_json(args.queries)
    positive_queries, negative_queries = validate_queries(children, queries)
    print(
        f"Validated {len(queries)} queries "
        f"({positive_queries} positive, {negative_queries} negative) against {len(children)} child chunks."
    )
    if args.validate_only:
        return

    specs = [ModelSpec(**item) for item in read_json(args.models)]
    if args.only:
        requested = set(args.only)
        specs = [spec for spec in specs if spec.name in requested]
        missing = requested - {spec.name for spec in specs}
        if missing:
            raise ValueError(f"Unknown model names: {sorted(missing)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    for spec in specs:
        print(f"\nEvaluating {spec.name} ({spec.model_id})")
        summary, rows = evaluate_model(
            spec,
            children,
            queries,
            args.children,
            args.cache_dir,
            args.batch_size,
            args.device,
            not args.ignore_project_snapshots,
        )
        summaries.append(summary)
        details.extend(rows)
        print(json.dumps(summary, indent=2))

    summaries.sort(
        key=lambda row: (row.get("all_recall_at_10", 0), row.get("recall_at_10", 0), row["mrr"]),
        reverse=True,
    )
    write_csv(args.output_dir / "summary.csv", summaries)
    write_csv(args.output_dir / "per_query.csv", details)
    with (args.output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summaries, handle, ensure_ascii=False, indent=2)
    print(f"\nResults written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
