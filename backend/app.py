"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import Settings, settings
from .core.logging import configure_request_logger
from .lifespan import create_lifespan
from .middleware.request_logging import RequestLoggingMiddleware


def create_app(config: Settings = settings) -> FastAPI:
    request_logger = configure_request_logger(config.request_log_path)
    application = FastAPI(
        title="Constitution Hybrid RAG API",
        version="1.0.0",
        description=(
            f"Citation-forward retrieval over the {config.corpus_name}, "
            f"as on {config.corpus_date}."
        ),
        lifespan=create_lifespan(config),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.add_middleware(RequestLoggingMiddleware, logger=request_logger)
    application.include_router(api_router)
    return application


app = create_app()
