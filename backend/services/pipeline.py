from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator

from ..models.schemas import ParentSource, PipelineStep
from .retrieval import HybridRetriever


StageResult = tuple[PipelineStep, list[ParentSource] | None]


def timed_step(step_id: str, label: str, started: float, detail: str) -> PipelineStep:
    """Build a pipeline-stage result from its start time."""
    return PipelineStep(
        id=step_id,
        label=label,
        duration_ms=round((time.perf_counter() - started) * 1000, 2),
        detail=detail,
    )


class RetrievalPipeline:
    """Coordinates retrieval stages without depending on FastAPI."""

    def __init__(self, retriever: HybridRetriever) -> None:
        self.retriever = retriever

    async def stages(self, query: str) -> AsyncIterator[StageResult]:
        started = time.perf_counter()
        sparse = await asyncio.to_thread(self.retriever.bm25_search, query)
        yield timed_step(
            "sparse", "BM25 sparse retrieval", started, f"{len(sparse)} candidates"
        ), None

        started = time.perf_counter()
        dense = await asyncio.to_thread(self.retriever.dense_search, query)
        yield timed_step(
            "dense", "Dense retrieval", started, f"{len(dense)} candidates"
        ), None

        started = time.perf_counter()
        fused = self.retriever.rrf_fusion(sparse, dense)
        yield timed_step(
            "fusion", "Reciprocal Rank Fusion", started, f"{len(fused)} fused candidates"
        ), None

        started = time.perf_counter()
        reranked = await asyncio.to_thread(self.retriever.rerank, query, fused)
        yield timed_step(
            "rerank", "Cross-encoder reranking", started, f"{len(reranked)} scored children"
        ), None

        started = time.perf_counter()
        sources = self.retriever.expand_parents(reranked)
        yield timed_step(
            "parents", "Unique parent-context expansion", started, f"{len(sources)} unique parents"
        ), sources

    async def run(self, query: str) -> tuple[list[ParentSource], list[PipelineStep]]:
        sources: list[ParentSource] = []
        steps: list[PipelineStep] = []
        async for step, stage_sources in self.stages(query):
            steps.append(step)
            if stage_sources is not None:
                sources = stage_sources
        return sources, steps
