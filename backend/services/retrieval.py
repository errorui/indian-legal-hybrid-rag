from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..core.config import Settings
from ..models.schemas import ParentSource
from .context_expansion import ParentContextExpander
from .corpus import CorpusStore
from .dense_retrieval import DenseRetriever
from .ranking import reciprocal_rank_fusion
from .reranking import ChildReranker, RankedChild
from .sparse_retrieval import SparseRetriever


@dataclass(slots=True)
class RetrieverComponents:
    corpus: CorpusStore
    sparse: SparseRetriever
    dense: DenseRetriever
    reranker: ChildReranker
    expander: ParentContextExpander


class HybridRetriever:
    """Compatibility facade over focused retrieval components."""

    def __init__(self, config: Settings) -> None:
        corpus = CorpusStore.from_paths(config.parent_chunks_path, config.child_chunks_path)
        self.config = config
        self.components = RetrieverComponents(
            corpus=corpus,
            sparse=SparseRetriever(corpus.child_documents, config.bm25_limit),
            dense=DenseRetriever(config, corpus),
            reranker=ChildReranker(config, corpus),
            expander=ParentContextExpander(config, corpus),
        )

    @property
    def parents(self) -> list[dict]:
        return self.components.corpus.parents

    @property
    def children(self) -> list[dict]:
        return self.components.corpus.children

    @property
    def models_loaded(self) -> bool:
        return self.components.dense.loaded and self.components.reranker.loaded

    def load_models(self) -> None:
        self.components.dense.load()
        self.components.reranker.load()
        self.components.dense.warmup()
        self.components.reranker.warmup()

    def bm25_search(self, query: str, limit: int | None = None) -> list[int]:
        return self.components.sparse.search(query, limit)

    def dense_search(self, query: str, limit: int | None = None) -> list[int]:
        return self.components.dense.search(query, limit)

    @staticmethod
    def rrf_fusion(*rankings: Iterable[int], k: int = 60) -> list[int]:
        return reciprocal_rank_fusion(*rankings, k=k)

    def rerank(self, query: str, indices: list[int]) -> list[RankedChild]:
        return self.components.reranker.rank(query, indices)

    def expand_parents(self, ranked_children: list[RankedChild]) -> list[ParentSource]:
        return self.components.expander.expand(ranked_children)
