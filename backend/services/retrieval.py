from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import threading
import time
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..core.config import Settings
from ..core.logging import log_event
from ..models.schemas import ChildMatch, ParentSource, PipelineStep


TOKEN_RE = re.compile(r"[a-z0-9]+")
MODEL_SNAPSHOT_METADATA = "snapshot.json"
logger = logging.getLogger("constitution_rag.requests")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(slots=True)
class RankedChild:
    index: int
    score: float


class HybridRetriever:
    """Notebook-equivalent BM25 + dense + RRF + cross-encoder retrieval."""

    def __init__(self, config: Settings) -> None:
        self.config = config
        self.parents = self._read_json(config.parent_chunks_path)
        self.children = self._read_json(config.child_chunks_path)
        self.parent_lookup = {item["parent_id"]: item for item in self.parents}
        self.documents = [
            f"{' '.join(item.get('heading_path') or [])} {item['text']}"
            for item in self.children
        ]
        self._build_bm25_index()
        self._model_lock = threading.Lock()
        self._embedder: Any = None
        self._dense_index: Any = None
        self._reranker: Any = None

    @staticmethod
    def _read_json(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            raise FileNotFoundError(f"Corpus artifact not found: {path}")
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list) or not data:
            raise ValueError(f"Corpus artifact is empty or invalid: {path}")
        return data

    @property
    def models_loaded(self) -> bool:
        return self._dense_index is not None and self._reranker is not None

    def _snapshot_path(self, kind: str, model_name: str) -> Path:
        model_hash = hashlib.sha256(model_name.encode("utf-8")).hexdigest()[:12]
        return self.config.model_snapshot_dir / f"{kind}-{model_hash}"

    @staticmethod
    def _snapshot_matches(path: Path, model_name: str) -> bool:
        metadata_path = path / MODEL_SNAPSHOT_METADATA
        if not metadata_path.is_file():
            return False
        try:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)
        except (OSError, json.JSONDecodeError):
            return False
        return metadata.get("model_name") == model_name

    @staticmethod
    def _mark_snapshot_ready(path: Path, model_name: str) -> None:
        metadata_path = path / MODEL_SNAPSHOT_METADATA
        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump({"model_name": model_name}, file, ensure_ascii=False, indent=2)

    def _load_embedder(self) -> Any:
        from sentence_transformers import SentenceTransformer

        snapshot_path = self._snapshot_path("embedding", self.config.embedding_model)
        started = time.perf_counter()
        if self._snapshot_matches(snapshot_path, self.config.embedding_model):
            model = SentenceTransformer(str(snapshot_path), trust_remote_code=True)
            source = "local_snapshot"
        else:
            self.config.huggingface_cache_dir.mkdir(parents=True, exist_ok=True)
            model = SentenceTransformer(
                self.config.embedding_model,
                trust_remote_code=True,
                cache_folder=str(self.config.huggingface_cache_dir),
            )
            snapshot_path.mkdir(parents=True, exist_ok=True)
            model.save(str(snapshot_path))
            self._mark_snapshot_ready(snapshot_path, self.config.embedding_model)
            source = "download_or_huggingface_cache"
        log_event(
            logger,
            "embedding_model_loaded",
            request_id="startup",
            model=self.config.embedding_model,
            source=source,
            snapshot_path=str(snapshot_path),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return model

    def _load_reranker(self) -> Any:
        from sentence_transformers import CrossEncoder

        snapshot_path = self._snapshot_path("reranker", self.config.reranker_model)
        started = time.perf_counter()
        if self._snapshot_matches(snapshot_path, self.config.reranker_model):
            model = CrossEncoder(str(snapshot_path), max_length=512)
            source = "local_snapshot"
        else:
            self.config.huggingface_cache_dir.mkdir(parents=True, exist_ok=True)
            model = CrossEncoder(
                self.config.reranker_model,
                max_length=512,
                cache_folder=str(self.config.huggingface_cache_dir),
            )
            snapshot_path.mkdir(parents=True, exist_ok=True)
            model.save(str(snapshot_path))
            self._mark_snapshot_ready(snapshot_path, self.config.reranker_model)
            source = "download_or_huggingface_cache"
        log_event(
            logger,
            "reranker_model_loaded",
            request_id="startup",
            model=self.config.reranker_model,
            source=source,
            snapshot_path=str(snapshot_path),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return model

    def _corpus_fingerprint(self) -> str:
        digest = hashlib.sha256()
        with self.config.child_chunks_path.open("rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def _load_saved_dense_index(
        self,
        expected_metadata: dict[str, Any],
    ) -> Any | None:
        import faiss

        index_path = self.config.dense_index_path
        metadata_path = self.config.dense_index_metadata_path
        if not index_path.is_file() or not metadata_path.is_file():
            return None
        try:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)
            if metadata != expected_metadata:
                return None
            index = faiss.read_index(str(index_path))
            if index.ntotal != expected_metadata["count"]:
                return None
            index.hnsw.efSearch = 64
            return index
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            logger.warning("Saved FAISS index is invalid; rebuilding", exc_info=True)
            return None

    def _save_dense_index(self, index: Any, metadata: dict[str, Any]) -> None:
        import faiss

        index_path = self.config.dense_index_path
        metadata_path = self.config.dense_index_metadata_path
        index_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = uuid.uuid4().hex
        temporary_index = index_path.with_name(f"{index_path.name}.{suffix}.tmp")
        temporary_metadata = metadata_path.with_name(
            f"{metadata_path.name}.{suffix}.tmp"
        )
        faiss.write_index(index, str(temporary_index))
        with temporary_metadata.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=2)
        os.replace(temporary_index, index_path)
        os.replace(temporary_metadata, metadata_path)

    def load_models(self) -> None:
        """Load persisted artifacts and warm inference before accepting traffic."""
        started = time.perf_counter()
        self._ensure_dense_index()
        self._ensure_reranker()

        warmup_started = time.perf_counter()
        self._embedder.encode(
            ["Constitution of India"],
            show_progress_bar=False,
        )
        self._reranker.predict(
            [("constitutional provision", "Constitution of India")],
            show_progress_bar=False,
        )
        log_event(
            logger,
            "retrieval_models_ready",
            request_id="startup",
            child_count=len(self.children),
            index_size=self._dense_index.ntotal,
            warmup_duration_ms=round(
                (time.perf_counter() - warmup_started) * 1000, 2
            ),
            total_duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )

    def _build_bm25_index(self) -> None:
        self._inverted_index: dict[str, list[int]] = defaultdict(list)
        self._term_frequencies: list[Counter[str]] = []
        self._document_lengths: list[int] = []

        for index, document in enumerate(self.documents):
            tokens = tokenize(document)
            frequencies = Counter(tokens)
            self._term_frequencies.append(frequencies)
            self._document_lengths.append(len(tokens))
            for token in frequencies:
                self._inverted_index[token].append(index)

        document_count = len(self.documents)
        self._average_document_length = (
            sum(self._document_lengths) / document_count if document_count else 0.0
        )
        self._idf = {
            term: math.log((document_count - len(postings) + 0.5) / (len(postings) + 0.5) + 1)
            for term, postings in self._inverted_index.items()
        }

    def bm25_search(self, query: str, limit: int | None = None) -> list[int]:
        scores: dict[int, float] = defaultdict(float)
        k1, b = 1.5, 0.75
        average_length = self._average_document_length or 1.0

        for term in tokenize(query):
            for document_index in self._inverted_index.get(term, []):
                frequency = self._term_frequencies[document_index][term]
                document_length = self._document_lengths[document_index]
                denominator = frequency + k1 * (
                    1 - b + b * document_length / average_length
                )
                scores[document_index] += (
                    self._idf[term] * frequency * (k1 + 1) / denominator
                )

        ranked = sorted(scores, key=scores.get, reverse=True)
        return ranked[: limit or self.config.bm25_limit]

    def _ensure_dense_index(self) -> None:
        if self._dense_index is not None:
            return
        with self._model_lock:
            if self._dense_index is not None:
                return
            import faiss
            import numpy as np

            started = time.perf_counter()
            embedder = self._load_embedder()
            embeddings = np.asarray(
                [child["embedding"] for child in self.children], dtype=np.float32
            )
            metadata = {
                "corpus_sha256": self._corpus_fingerprint(),
                "embedding_model": self.config.embedding_model,
                "count": len(self.children),
                "dimension": int(embeddings.shape[1]),
                "metric": "inner_product",
                "hnsw_m": 32,
            }
            index = self._load_saved_dense_index(metadata)
            if index is None:
                faiss.normalize_L2(embeddings)
                index = faiss.IndexHNSWFlat(
                    embeddings.shape[1], 32, faiss.METRIC_INNER_PRODUCT
                )
                index.hnsw.efConstruction = 200
                index.hnsw.efSearch = 64
                index.add(embeddings)
                self._save_dense_index(index, metadata)
                source = "rebuilt"
            else:
                source = "local_snapshot"
            self._embedder = embedder
            self._dense_index = index
            log_event(
                logger,
                "dense_index_loaded",
                request_id="startup",
                source=source,
                index_path=str(self.config.dense_index_path),
                vector_count=index.ntotal,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )

    def dense_search(self, query: str, limit: int | None = None) -> list[int]:
        import faiss
        import numpy as np

        self._ensure_dense_index()
        query_embedding = self._embedder.encode([query]).astype(np.float32)
        faiss.normalize_L2(query_embedding)
        _, indices = self._dense_index.search(
            query_embedding, limit or self.config.dense_limit
        )
        return [int(index) for index in indices[0] if index >= 0]

    @staticmethod
    def rrf_fusion(*rankings: Iterable[int], k: int = 60) -> list[int]:
        scores: dict[int, float] = defaultdict(float)
        for ranking in rankings:
            for rank, document_index in enumerate(ranking):
                scores[int(document_index)] += 1 / (k + rank + 1)
        return sorted(scores, key=scores.get, reverse=True)

    def _ensure_reranker(self) -> None:
        if self._reranker is not None:
            return
        with self._model_lock:
            if self._reranker is None:
                self._reranker = self._load_reranker()

    def rerank(self, query: str, indices: list[int]) -> list[RankedChild]:
        self._ensure_reranker()
        pairs: list[tuple[str, str]] = []
        valid_indices: list[int] = []
        oversized_table_indices: list[int] = []

        for index in indices[: self.config.fusion_limit]:
            child = self.children[index]
            text = child["text"]
            is_table = child.get("type") == "table" or text.lstrip().startswith("<table")
            if is_table and len(self._reranker.tokenizer.encode(query, text)) > 512:
                oversized_table_indices.append(index)
            else:
                pairs.append((query, text))
                valid_indices.append(index)

        scores = self._reranker.predict(pairs) if pairs else []
        score_lookup = {
            index: float(scores[position])
            for position, index in enumerate(valid_indices)
        }
        for index in oversized_table_indices:
            score_lookup[index] = 1.0

        ranked = sorted(score_lookup, key=score_lookup.get, reverse=True)
        return [RankedChild(index=index, score=score_lookup[index]) for index in ranked]

    def expand_parents(self, ranked_children: list[RankedChild]) -> list[ParentSource]:
        grouped: dict[str, list[RankedChild]] = {}
        for item in ranked_children[: self.config.rerank_limit]:
            if item.score < self.config.rerank_threshold:
                continue
            parent_id = self.children[item.index]["parent_id"]
            grouped.setdefault(parent_id, []).append(item)

        sources: list[ParentSource] = []
        for rank, (parent_id, matches) in enumerate(grouped.items(), start=1):
            parent = self.parent_lookup.get(parent_id)
            if parent is None:
                continue
            child_matches = [
                ChildMatch(
                    child_id=self.children[item.index]["child_id"],
                    text=self.children[item.index]["text"],
                    block_type=self.children[item.index].get("type", "mixed"),
                    reranker_score=round(item.score, 6),
                )
                for item in matches
            ]
            sources.append(
                ParentSource(
                    parent_id=parent_id,
                    doc_id=parent["doc_id"],
                    heading_path=parent.get("heading_path") or [],
                    text=parent["text"],
                    rank=rank,
                    score=round(max(item.score for item in matches), 6),
                    matched_children=child_matches,
                )
            )
        return sources

    @staticmethod
    def timed_step(step_id: str, label: str, started: float, detail: str) -> PipelineStep:
        return PipelineStep(
            id=step_id,
            label=label,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            detail=detail,
        )
