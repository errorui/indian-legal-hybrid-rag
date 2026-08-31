from __future__ import annotations

import argparse
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHILDREN = ROOT / "data" / "chunks" / "childrenchunks.json"
MODEL_ID = "BAAI/bge-base-en-v1.5"
BACKUP_DIR = ROOT / ".cache" / "backups"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def corpus_text(child: dict[str, Any]) -> str:
    heading = " ".join(child.get("heading_path") or [])
    return f"{heading} {child['text']}".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace child embeddings with BGE without changing chunk boundaries."
    )
    parser.add_argument("--children", type=Path, default=DEFAULT_CHILDREN)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", default=None, help="For example: cpu, cuda, cuda:0")
    parser.add_argument("--model", default=MODEL_ID)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    children = read_json(args.children)
    if not isinstance(children, list) or not children:
        raise ValueError(f"Invalid child artifact: {args.children}")

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        args.model,
        device=args.device,
        cache_folder=str(ROOT / ".cache" / "huggingface"),
    )
    embeddings = model.encode(
        [corpus_text(child) for child in children],
        batch_size=args.batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    if len(embeddings) != len(children):
        raise RuntimeError("Embedding count does not match child count.")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{args.children.stem}.nomic-before-bge.json"
    if not backup.exists():
        shutil.copy2(args.children, backup)

    updated = []
    for child, embedding in zip(children, embeddings):
        item = dict(child)
        item["embedding"] = embedding.tolist()
        item["embedding_model"] = args.model
        item["embedding_text"] = "heading_path + text"
        updated.append(item)

    temporary = args.children.with_name(f"{args.children.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, args.children)
    print(f"Re-embedded {len(updated)} child chunks with {args.model}.")
    print(f"Boundaries unchanged. Backup: {backup.resolve()}")
    print(f"Updated: {args.children.resolve()}")


if __name__ == "__main__":
    main()
