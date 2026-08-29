"""Validated API request and response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    corpus_loaded: bool
    hybrid_models_loaded: bool
    generation_available: bool


class MetaResponse(BaseModel):
    corpus_name: str
    corpus_date: str
    parent_count: int
    child_count: int
    pipeline: list[str]
    disclaimer: str


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Query cannot be blank")
        return normalized


class ChildMatch(BaseModel):
    child_id: str
    text: str
    block_type: str
    reranker_score: float


class ParentSource(BaseModel):
    parent_id: str
    doc_id: str
    heading_path: list[str]
    text: str
    rank: int
    score: float
    matched_children: list[ChildMatch]


class PipelineStep(BaseModel):
    id: str
    label: str
    status: Literal["complete", "skipped", "error"] = "complete"
    duration_ms: float
    detail: str
    branch_number: int | None = None
    branch_query: str | None = None


class SearchResponse(BaseModel):
    query: str
    sources: list[ParentSource]
    steps: list[PipelineStep]


class ChatResponse(SearchResponse):
    answer: str
    sub_queries: list[str]
    mode: Literal["generated", "retrieval_only"]
