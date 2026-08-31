from __future__ import annotations

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..core.config import Settings
from ..core.logging import log_event


MODEL_SNAPSHOT_METADATA = "snapshot.json"
logger = logging.getLogger("research_tool.models")


class ModelLoader(ABC):
    """Loads one model family and owns its local snapshot policy."""

    def __init__(self, config: Settings, kind: str, model_name: str) -> None:
        self.config = config
        self.kind = kind
        self.model_name = model_name
        self._model: Any = None

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def _snapshot_path(self) -> Path:
        model_hash = hashlib.sha256(self.model_name.encode("utf-8")).hexdigest()[:12]
        return self.config.model_snapshot_dir / f"{self.kind}-{model_hash}"

    def _snapshot_matches(self, path: Path) -> bool:
        metadata_path = path / MODEL_SNAPSHOT_METADATA
        if not metadata_path.is_file():
            return False
        try:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)
        except (OSError, json.JSONDecodeError):
            return False
        return metadata.get("model_name") == self.model_name

    def load(self) -> Any:
        if self._model is not None:
            return self._model
        started = time.perf_counter()
        snapshot_path = self._snapshot_path()
        if self._snapshot_matches(snapshot_path):
            self._model = self._load_from_snapshot(snapshot_path)
            source = "local_snapshot"
        else:
            self._model = self._load_from_registry()
            snapshot_path.mkdir(parents=True, exist_ok=True)
            self._model.save(str(snapshot_path))
            with (snapshot_path / MODEL_SNAPSHOT_METADATA).open("w", encoding="utf-8") as file:
                json.dump({"model_name": self.model_name}, file, ensure_ascii=False, indent=2)
            source = "download_or_registry_cache"
        log_event(
            logger,
            f"{self.kind}_model_loaded",
            request_id="startup",
            model=self.model_name,
            source=source,
            snapshot_path=str(snapshot_path),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return self._model

    @abstractmethod
    def _load_from_snapshot(self, path: Path) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _load_from_registry(self) -> Any:
        raise NotImplementedError


class EmbeddingModelLoader(ModelLoader):
    def __init__(self, config: Settings) -> None:
        super().__init__(config, "embedding", config.embedding_model)

    def _load_from_snapshot(self, path: Path) -> Any:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(str(path), trust_remote_code=True)

    def _load_from_registry(self) -> Any:
        from sentence_transformers import SentenceTransformer

        self.config.huggingface_cache_dir.mkdir(parents=True, exist_ok=True)
        return SentenceTransformer(
            self.model_name,
            trust_remote_code=True,
            cache_folder=str(self.config.huggingface_cache_dir),
        )


class RerankerModelLoader(ModelLoader):
    def __init__(self, config: Settings) -> None:
        super().__init__(config, "reranker", config.reranker_model)

    def _load_from_snapshot(self, path: Path) -> Any:
        from sentence_transformers import CrossEncoder

        return CrossEncoder(str(path), max_length=512)

    def _load_from_registry(self) -> Any:
        from sentence_transformers import CrossEncoder

        self.config.huggingface_cache_dir.mkdir(parents=True, exist_ok=True)
        return CrossEncoder(
            self.model_name,
            max_length=512,
            cache_folder=str(self.config.huggingface_cache_dir),
        )
