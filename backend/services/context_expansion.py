from __future__ import annotations

from collections import OrderedDict

from ..core.config import Settings
from ..models.schemas import ChildMatch, ParentSource
from .corpus import CorpusStore
from .reranking import RankedChild


class ParentContextExpander:
    def __init__(self, config: Settings, corpus: CorpusStore) -> None:
        self.config = config
        self.corpus = corpus

    def expand(self, ranked_children: list[RankedChild]) -> list[ParentSource]:
        grouped: OrderedDict[str, list[RankedChild]] = OrderedDict()
        for item in ranked_children[: self.config.rerank_limit]:
            if item.score < self.config.rerank_threshold:
                continue
            parent_id = self.corpus.children[item.index]["parent_id"]
            grouped.setdefault(parent_id, []).append(item)

        sources: list[ParentSource] = []
        for rank, (parent_id, matches) in enumerate(grouped.items(), start=1):
            parent = self.corpus.parent_lookup.get(parent_id)
            if parent is None:
                continue
            children = [self.corpus.children[item.index] for item in matches]
            sources.append(
                ParentSource(
                    parent_id=parent_id,
                    doc_id=parent["doc_id"],
                    heading_path=parent.get("heading_path") or [],
                    text=parent["text"],
                    rank=rank,
                    score=round(max(item.score for item in matches), 6),
                    matched_children=[
                        ChildMatch(
                            child_id=child["child_id"],
                            text=child["text"],
                            block_type=child.get("type", "mixed"),
                            reranker_score=round(match.score, 6),
                        )
                        for child, match in zip(children, matches)
                    ],
                )
            )
        return sources
