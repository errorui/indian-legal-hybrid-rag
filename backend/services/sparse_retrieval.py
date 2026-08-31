from __future__ import annotations

import math
import re
from collections import Counter, defaultdict


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class SparseRetriever:
    def __init__(self, documents: list[str], default_limit: int) -> None:
        self.default_limit = default_limit
        self._inverted_index: dict[str, list[int]] = defaultdict(list)
        self._term_frequencies: list[Counter[str]] = []
        self._document_lengths: list[int] = []
        for index, document in enumerate(documents):
            frequencies = Counter(tokenize(document))
            self._term_frequencies.append(frequencies)
            self._document_lengths.append(sum(frequencies.values()))
            for term in frequencies:
                self._inverted_index[term].append(index)
        count = len(documents)
        average_length = sum(self._document_lengths) / count if count else 0.0
        self._average_document_length = average_length or 1.0
        self._idf = {
            term: math.log((count - len(postings) + 0.5) / (len(postings) + 0.5) + 1)
            for term, postings in self._inverted_index.items()
        }

    def search(self, query: str, limit: int | None = None) -> list[int]:
        scores: dict[int, float] = defaultdict(float)
        k1, b = 1.5, 0.75
        for term in tokenize(query):
            for index in self._inverted_index.get(term, []):
                frequency = self._term_frequencies[index][term]
                length = self._document_lengths[index]
                denominator = frequency + k1 * (1 - b + b * length / self._average_document_length)
                scores[index] += self._idf[term] * frequency * (k1 + 1) / denominator
        ranked = sorted(scores, key=scores.get, reverse=True)
        return ranked[: limit or self.default_limit]
