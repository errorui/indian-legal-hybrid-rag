from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path

import faiss
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CHILDREN = ROOT / "data" / "chunks" / "childrenchunks.json"
INDEX = ROOT / ".cache" / "indexes" / "children_hnsw.faiss"
METADATA = ROOT / ".cache" / "indexes" / "children_hnsw.json"
MODEL = "BAAI/bge-base-en-v1.5"


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    with CHILDREN.open("r", encoding="utf-8") as handle:
        children = json.load(handle)
    embeddings = np.asarray([child["embedding"] for child in children], dtype=np.float32)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexHNSWFlat(embeddings.shape[1], 32, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = 200
    index.hnsw.efSearch = 64
    index.add(embeddings)

    metadata = {
        "corpus_sha256": fingerprint(CHILDREN),
        "embedding_model": MODEL,
        "count": len(children),
        "dimension": int(embeddings.shape[1]),
        "metric": "inner_product",
        "hnsw_m": 32,
    }
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    suffix = uuid.uuid4().hex
    temporary_index = INDEX.with_name(f"{INDEX.name}.{suffix}.tmp")
    temporary_metadata = METADATA.with_name(f"{METADATA.name}.{suffix}.tmp")
    faiss.write_index(index, str(temporary_index))
    temporary_metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    os.replace(temporary_index, INDEX)
    os.replace(temporary_metadata, METADATA)
    print(json.dumps(metadata, indent=2))
    print(f"Rebuilt index: {INDEX.resolve()}")


if __name__ == "__main__":
    main()
