from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from ..core.config import Settings
from ..services.chat import ChatService
from ..services.pipeline import RetrievalPipeline
from ..services.retrieval import HybridRetriever


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_retriever(request: Request) -> HybridRetriever:
    retriever = request.app.state.retriever
    if retriever is None:
        raise HTTPException(
            status_code=503,
            detail=request.app.state.startup_error or "Corpus is unavailable",
        )
    return retriever


def get_pipeline(request: Request) -> RetrievalPipeline:
    pipeline = request.app.state.pipeline
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail=request.app.state.startup_error or "Corpus is unavailable",
        )
    return pipeline


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_request_logger() -> logging.Logger:
    return logging.getLogger("constitution_rag.requests")


SettingsDependency = Annotated[Settings, Depends(get_settings)]
RetrieverDependency = Annotated[HybridRetriever, Depends(get_retriever)]
PipelineDependency = Annotated[RetrievalPipeline, Depends(get_pipeline)]
ChatServiceDependency = Annotated[ChatService, Depends(get_chat_service)]
RequestLoggerDependency = Annotated[logging.Logger, Depends(get_request_logger)]
