from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def read_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Corpus artifact not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list) or not data:
        raise ValueError(f"Corpus artifact is empty or invalid: {path}")
    return data


def document_text(item: dict[str, Any]) -> str:
    heading = " ".join(item.get("heading_path") or [])
    return f"{heading} {item['text']}".strip()


@dataclass(slots=True)
class CorpusStore:
    parents: list[dict[str, Any]]
    children: list[dict[str, Any]]
    child_documents: list[str]
    parent_lookup: dict[str, dict[str, Any]]
    child_path: Path

    @classmethod
    def from_paths(cls, parent_path: Path, child_path: Path) -> "CorpusStore":
        parents = read_records(parent_path)
        children = read_records(child_path)
        return cls(
            parents=parents,
            children=children,
            child_documents=[document_text(child) for child in children],
            parent_lookup={parent["parent_id"]: parent for parent in parents},
            child_path=child_path,
        )

    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        with self.child_path.open("rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()
