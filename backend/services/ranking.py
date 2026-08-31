from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def reciprocal_rank_fusion(*rankings: Iterable[int], k: int = 60) -> list[int]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, document_index in enumerate(ranking):
            scores[int(document_index)] += 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
