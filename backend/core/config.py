from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    parent_chunks_path: Path = PROJECT_ROOT / "data" / "chunks" / "parentchunks2.json"
    child_chunks_path: Path = PROJECT_ROOT / "data" / "chunks" / "childrenchunks.json"
    request_log_path: Path = PROJECT_ROOT / "logs" / "requests.txt"
    model_snapshot_dir: Path = PROJECT_ROOT / ".cache" / "models"
    huggingface_cache_dir: Path = PROJECT_ROOT / ".cache" / "huggingface"
    dense_index_path: Path = PROJECT_ROOT / ".cache" / "indexes" / "children_hnsw.faiss"
    dense_index_metadata_path: Path = (
        PROJECT_ROOT / ".cache" / "indexes" / "children_hnsw.json"
    )
    corpus_name: str = os.getenv("CORPUS_NAME", "Research corpus")
    corpus_date: str = os.getenv("CORPUS_DATE", "")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"
    )
    embedding_query_prefix: str = os.getenv("EMBEDDING_QUERY_PREFIX", "")
    embedding_warmup_text: str = os.getenv("EMBEDDING_WARMUP_TEXT", "warmup")
    reranker_warmup_query: str = os.getenv("RERANKER_WARMUP_QUERY", "warmup query")
    reranker_warmup_document: str = os.getenv(
        "RERANKER_WARMUP_DOCUMENT", "warmup document"
    )
    reranker_model: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    fanout_model: str = os.getenv("FANOUT_MODEL", "gemma4:31b-cloud")
    generation_model: str = os.getenv("GENERATION_MODEL", "gpt-oss:120b")
    chat_provider: str = os.getenv("CHAT_PROVIDER", "ollama")
    ollama_api_key: str | None = os.getenv("OLLAMA_API_KEY")
    ollama_host: str = os.getenv("OLLAMA_HOST", "https://ollama.com")
    bm25_limit: int = 100
    dense_limit: int = 100
    fusion_limit: int = 30
    rerank_limit: int = 20
    rerank_threshold: float = 0.35


settings = Settings()
