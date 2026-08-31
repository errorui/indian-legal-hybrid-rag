from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.config import Settings
from .corpus import CorpusStore
from .model_loader import RerankerModelLoader


@dataclass(slots=True)
class RankedChild:
    index: int
    score: float


class ChildReranker:
    def __init__(self, config: Settings, corpus: CorpusStore) -> None:
        self.config = config
        self.corpus = corpus
        self.model_loader = RerankerModelLoader(config)

    @property
    def loaded(self) -> bool:
        return self.model_loader.loaded

    def load(self) -> None:
        self.model_loader.load()

    def warmup(self) -> None:
        self.model_loader.load().predict(
            [(self.config.reranker_warmup_query, self.config.reranker_warmup_document)],
            show_progress_bar=False,
        )

    def rank(self, query: str, indices: list[int]) -> list[RankedChild]:
        model = self.model_loader.load()
        pairs: list[tuple[str, str]] = []
        valid: list[int] = []
        oversized_tables: list[int] = []
        for index in indices[: self.config.fusion_limit]:
            child = self.corpus.children[index]
            text = child["text"]
            is_table = child.get("type") == "table" or text.lstrip().startswith("<table")
            if is_table and len(model.tokenizer.encode(query, text)) > 512:
                oversized_tables.append(index)
            else:
                pairs.append((query, text))
                valid.append(index)
        scores = model.predict(pairs) if pairs else []
        score_lookup = {index: float(scores[position]) for position, index in enumerate(valid)}
        score_lookup.update({index: 1.0 for index in oversized_tables})
        return [RankedChild(index=index, score=score_lookup[index]) for index in sorted(score_lookup, key=score_lookup.get, reverse=True)]
