import logging
import time

from fastapi import APIRouter, Request

from ...core.logging import log_event
from ...models.schemas import QueryRequest, SearchResponse
from ..dependencies import PipelineDependency, RequestLoggerDependency


router = APIRouter(prefix="/api", tags=["retrieval"])


@router.post("/search", response_model=SearchResponse)
async def search(
    request: Request,
    payload: QueryRequest,
    pipeline: PipelineDependency,
    request_logger: RequestLoggerDependency,
) -> SearchResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    started = time.perf_counter()
    log_event(
        request_logger,
        "search_started",
        request_id=request_id,
        query=payload.query,
    )
    try:
        sources, steps = await pipeline.run(payload.query)
        response = SearchResponse(query=payload.query, sources=sources, steps=steps)
        log_event(
            request_logger,
            "search_completed",
            request_id=request_id,
            total_duration_ms=round((time.perf_counter() - started) * 1000, 2),
            response=response.model_dump(),
        )
        return response
    except Exception as exc:
        log_event(
            request_logger,
            "search_failed",
            level=logging.ERROR,
            exc_info=True,
            request_id=request_id,
            query=payload.query,
            error_type=type(exc).__name__,
            error_message=str(exc),
            total_duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        raise
