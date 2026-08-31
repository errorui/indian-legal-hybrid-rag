from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEST_SUITE = ROOT / "data" / "evaluation" / "test_suite.json"
DEFAULT_PARENTS = ROOT / "data" / "chunks" / "parentchunks2.json"
DEFAULT_CHILDREN = ROOT / "data" / "chunks" / "childrenchunks.json"
DEFAULT_OUTPUT = Path(__file__).with_name("queries_from_test_suite.json")
DEFAULT_REVIEW = Path(__file__).with_name("test_suite_mapping_review.json")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def article_heading_pattern(article: str) -> re.Pattern[str]:
    """Match a provision number at the beginning of a line, not cross-references."""
    escaped = re.escape(article.strip())
    return re.compile(
        rf"(?im)^[ \t]*(?:<sup>[^<]*</sup>[ \t]*)?(?:\[[ \t]*)?{escaped}[ \t]*\."
    )


def find_parent_matches(parents: list[dict[str, Any]], article: str) -> list[str]:
    pattern = article_heading_pattern(article)
    preferred: list[str] = []
    fallback: list[str] = []
    for parent in parents:
        parent_id = parent["parent_id"]
        try:
            ordinal = int(parent_id.rsplit("_", 1)[1])
        except (IndexError, ValueError):
            continue
        # parent_0069 onward is the canonical constitution text in this corpus;
        # later schedule/appendix chunks reuse small list numbers such as 1, 12,
        # and 14, while earlier chunks are an alternate duplicate extraction.
        heading = " ".join(parent.get("heading_path") or []).upper()
        excluded = any(re.search(rf"\b{token}\b", heading) for token in ("SCHEDULE", "APPENDIX", "CONTENTS"))
        excluded = excluded or bool(re.fullmatch(r"PART [A-Z]", heading.strip()))
        if excluded:
            continue
        match = pattern.search(parent.get("text", ""))
        if not match:
            continue
        line = parent["text"][match.start() :].splitlines()[0]
        # These are amendment footnotes, not the constitutional provision.
        if re.search(r"(?:\bSubs\.|\bIns\.|\bAdded by|\bomitted by)", line, re.IGNORECASE):
            continue
        if 69 <= ordinal <= 259:
            preferred.append(parent_id)
        elif ordinal < 69:
            fallback.append(parent_id)
    return preferred or fallback


def convert(
    test_suite: dict[str, Any],
    parents: list[dict[str, Any]],
    children: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    parent_by_id = {parent["parent_id"]: parent for parent in parents}
    children_by_parent: dict[str, list[str]] = {}
    for child in children:
        children_by_parent.setdefault(child["parent_id"], []).append(child["child_id"])

    converted: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}
    for item in test_suite["questions"]:
        source_id = item["id"]
        seen_ids[source_id] = seen_ids.get(source_id, 0) + 1
        query_id = source_id if seen_ids[source_id] == 1 else f"{source_id}_v{seen_ids[source_id]}"
        articles = [str(article).strip() for article in item.get("target_articles", [])]
        matches_by_article = {article: find_parent_matches(parents, article) for article in articles}
        parent_ids = sorted({parent_id for ids in matches_by_article.values() for parent_id in ids})
        child_ids = [child_id for parent_id in parent_ids for child_id in children_by_parent.get(parent_id, [])]
        missing_articles = [article for article, ids in matches_by_article.items() if not ids]
        ambiguous_articles = {
            article: ids for article, ids in matches_by_article.items() if len(ids) > 1
        }

        record = {
            "id": query_id,
            "source_id": source_id,
            "category": item.get("category", "test_suite"),
            "user_input": item["question"],
            "question": item["question"],
            "query": item["question"],
            "target_articles": articles,
            "relevant_parent_ids": parent_ids,
            "relevant_child_ids": child_ids,
            "reference_contexts": [parent_by_id[parent_id]["text"] for parent_id in parent_ids],
        }
        converted.append(record)

        if missing_articles or ambiguous_articles or not child_ids:
            review.append(
                {
                    "id": query_id,
                    "source_id": source_id,
                    "question": item["question"],
                    "target_articles": articles,
                    "matches_by_article": matches_by_article,
                    "missing_articles": missing_articles,
                    "ambiguous_articles": ambiguous_articles,
                    "matched_parent_ids": parent_ids,
                    "matched_child_ids": child_ids,
                    "status": "needs_manual_review",
                }
            )
    return converted, review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert article-labelled questions to dense benchmark format.")
    parser.add_argument("--test-suite", type=Path, default=DEFAULT_TEST_SUITE)
    parser.add_argument("--parents", type=Path, default=DEFAULT_PARENTS)
    parser.add_argument("--children", type=Path, default=DEFAULT_CHILDREN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    test_suite = read_json(args.test_suite)
    parents = read_json(args.parents)
    children = read_json(args.children)
    converted, review = convert(test_suite, parents, children)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(converted, ensure_ascii=False, indent=2), encoding="utf-8")
    args.review.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Converted {len(converted)} questions.")
    print(f"Questions requiring manual review: {len(review)}")
    print(f"Benchmark queries: {args.output.resolve()}")
    print(f"Review report: {args.review.resolve()}")


if __name__ == "__main__":
    main()
