from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import Settings
from .services.chat import ChatService
from .services.pipeline import RetrievalPipeline
from .services.retrieval import HybridRetriever


logger = logging.getLogger("constitution_rag.requests")


def create_lifespan(config: Settings) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = config
        app.state.chat_service = ChatService(config)
        app.state.retriever = None
        app.state.pipeline = None
        app.state.startup_error = None

        try:
            retriever = HybridRetriever(config)
            await asyncio.to_thread(retriever.load_models)
            app.state.retriever = retriever
            app.state.pipeline = RetrievalPipeline(retriever)
        except Exception as exc:
            app.state.startup_error = str(exc)
            logger.exception("Corpus or retrieval-model initialization failed")

        yield

    return lifespan
