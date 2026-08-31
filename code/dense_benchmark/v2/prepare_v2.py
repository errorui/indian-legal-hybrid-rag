from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = ROOT / "code" / "dense_benchmark"
FULL_QUERIES = BENCHMARK_DIR / "queries_from_test_suite.json"
REVIEW = BENCHMARK_DIR / "test_suite_mapping_review.json"
OUTPUT = Path(__file__).with_name("queries.json")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    queries = read_json(FULL_QUERIES)
    review = read_json(REVIEW)
    review_ids = {item["id"] for item in review}
    clean = [
        query
        for query in queries
        if query["id"] not in review_ids and query["relevant_child_ids"]
    ]
    OUTPUT.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(clean)} clean benchmark queries.")
    print(f"Excluded {len(queries) - len(clean)} queries pending manual review.")
    print(f"Output: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
