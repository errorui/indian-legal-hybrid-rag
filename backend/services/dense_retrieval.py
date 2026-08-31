from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import hashlib
import numpy as np

from ..core.config import Settings
from ..core.logging import log_event
from .corpus import CorpusStore
from .model_loader import EmbeddingModelLoader


logger = logging.getLogger("research_tool.retrieval")


class DenseRetriever:
    def __init__(self, config: Settings, corpus: CorpusStore) -> None:
        self.config = config
        self.corpus = corpus
        self.model_loader = EmbeddingModelLoader(config)
        self._index: Any = None
        self._lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        return self._index is not None and self.model_loader.loaded

    def _metadata(self, dimension: int) -> dict[str, Any]:
        return {
            "corpus_sha256": self.corpus.fingerprint(),
            "embedding_model": self.config.embedding_model,
            "count": len(self.corpus.children),
            "dimension": dimension,
            "metric": "inner_product",
            "hnsw_m": 32,
        }

    def _load_saved(self, expected: dict[str, Any]) -> Any | None:
        import faiss

        if not self.config.dense_index_path.is_file() or not self.config.dense_index_metadata_path.is_file():
            return None
        try:
            metadata = json.loads(self.config.dense_index_metadata_path.read_text(encoding="utf-8"))
            if metadata != expected:
                return None
            index = faiss.read_index(str(self.config.dense_index_path))
            if index.ntotal != expected["count"]:
                return None
            index.hnsw.efSearch = 64
            return index
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            logger.warning("Saved dense index is invalid; rebuilding", exc_info=True)
            return None

    def _save(self, index: Any, metadata: dict[str, Any]) -> None:
        import faiss

        self.config.dense_index_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = uuid.uuid4().hex
        temp_index = self.config.dense_index_path.with_name(f"{self.config.dense_index_path.name}.{suffix}.tmp")
        temp_metadata = self.config.dense_index_metadata_path.with_name(
            f"{self.config.dense_index_metadata_path.name}.{suffix}.tmp"
        )
        faiss.write_index(index, str(temp_index))
        temp_metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp_index, self.config.dense_index_path)
        os.replace(temp_metadata, self.config.dense_index_metadata_path)

    def load(self) -> None:
        if self._index is not None:
            return
        with self._lock:
            if self._index is not None:
                return
            import faiss

            started = time.perf_counter()
            self.model_loader.load()
            embeddings = np.asarray(
                [child["embedding"] for child in self.corpus.children], dtype=np.float32
            )
            metadata = self._metadata(int(embeddings.shape[1]))
            index = self._load_saved(metadata)
            if index is None:
                faiss.normalize_L2(embeddings)
                index = faiss.IndexHNSWFlat(embeddings.shape[1], 32, faiss.METRIC_INNER_PRODUCT)
                index.hnsw.efConstruction = 200
                index.hnsw.efSearch = 64
                index.add(embeddings)
                self._save(index, metadata)
                source = "rebuilt"
            else:
                source = "local_snapshot"
            self._index = index
            log_event(
                logger,
                "dense_index_loaded",
                request_id="startup",
                source=source,
                index_path=str(self.config.dense_index_path),
                vector_count=index.ntotal,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )

    def search(self, query: str, limit: int | None = None) -> list[int]:
        import faiss

        self.load()
        query_text = self._query_text(query)
        query_embedding = self.model_loader.load().encode([query_text]).astype(np.float32)
        faiss.normalize_L2(query_embedding)
        _, indices = self._index.search(query_embedding, limit or self.config.dense_limit)
        return [int(index) for index in indices[0] if index >= 0]

    def warmup(self) -> None:
        self.model_loader.load().encode(
            [self._query_text(self.config.embedding_warmup_text)], show_progress_bar=False
        )

    def _query_text(self, query: str) -> str:
        prefix = self.config.embedding_query_prefix.strip()
        return f"{prefix} {query}" if prefix else query
