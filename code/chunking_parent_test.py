from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARENT_CHUNKS_PATH = PROJECT_ROOT / "data" / "chunks" / "parentchunks2.json"


def load_parent_chunks() -> list[dict]:
    with PARENT_CHUNKS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    parent_chunks = load_parent_chunks()

    for chunk in parent_chunks[:5]:
        print(json.dumps(chunk, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
