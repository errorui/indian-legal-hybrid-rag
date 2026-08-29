from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ...core.logging import log_event
from ...models.schemas import ChatResponse, ParentSource, PipelineStep, QueryRequest
from ..dependencies import (
    ChatServiceDependency,
    PipelineDependency,
    RequestLoggerDependency,
    SettingsDependency,
)


router = APIRouter(prefix="/api/chat", tags=["chat"])
SLOW_STAGE_MS = 10_000


def format_sse(event: str, payload: object) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/stream", response_class=StreamingResponse)
async def chat_stream(
    request: Request,
    payload: QueryRequest,
    pipeline: PipelineDependency,
    chat_service: ChatServiceDependency,
    settings: SettingsDependency,
    request_logger: RequestLoggerDependency,
) -> StreamingResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    request_started = time.perf_counter()
    log_event(
        request_logger,
        "chat_started",
        request_id=request_id,
        query=payload.query,
        query_length=len(payload.query),
        fanout_model=settings.fanout_model,
        generation_model=settings.generation_model,
        generation_available=chat_service.generation_available,
    )

    async def events() -> AsyncIterator[str]:
        steps: list[PipelineStep] = []
        all_sources: list[ParentSource] = []
        branch_parent_ids: dict[int, set[str]] = {}
        try:
            yield format_sse(
                "status",
                {"id": "query", "label": "Query accepted", "detail": payload.query},
            )
            started = time.perf_counter()
            sub_queries = await asyncio.to_thread(chat_service.fanout, payload.query)
            fanout_duration_ms = round((time.perf_counter() - started) * 1000, 2)
            fanout_step = PipelineStep(
                id="fanout",
                label="Query fan-out",
                duration_ms=fanout_duration_ms,
                detail=f"{len(sub_queries)} retrieval branch(es)",
                status="complete" if chat_service.generation_available else "skipped",
            )
            steps.append(fanout_step)
            log_event(
                request_logger,
                "chat_fanout_completed",
                request_id=request_id,
                original_query=payload.query,
                branch_count=len(sub_queries),
                sub_queries=sub_queries,
                duration_ms=fanout_duration_ms,
                status=fanout_step.status,
            )
            yield format_sse("step", fanout_step.model_dump())

            seen_parents: set[str] = set()
            for branch_number, sub_query in enumerate(sub_queries, start=1):
                branch_started = time.perf_counter()
                branch_sources: list[ParentSource] = []
                yield format_sse(
                    "branch",
                    {
                        "number": branch_number,
                        "query": sub_query,
                        "total": len(sub_queries),
                    },
                )
                log_event(
                    request_logger,
                    "chat_branch_started",
                    request_id=request_id,
                    branch_number=branch_number,
                    branch_query=sub_query,
                )
                async for step, stage_sources in pipeline.stages(sub_query):
                    step.id = f"{step.id}-{branch_number}"
                    step.detail = f"Branch {branch_number}: {step.detail}"
                    step.branch_number = branch_number
                    step.branch_query = sub_query
                    steps.append(step)
                    log_event(
                        request_logger,
                        "chat_stage_completed",
                        request_id=request_id,
                        branch_number=branch_number,
                        branch_query=sub_query,
                        step=step.model_dump(),
                    )
                    if step.duration_ms >= SLOW_STAGE_MS:
                        log_event(
                            request_logger,
                            "chat_anomaly",
                            level=logging.WARNING,
                            request_id=request_id,
                            anomaly="slow_stage",
                            threshold_ms=SLOW_STAGE_MS,
                            branch_number=branch_number,
                            branch_query=sub_query,
                            step=step.model_dump(),
                        )
                    yield format_sse("step", step.model_dump())
                    if stage_sources is not None:
                        branch_sources = stage_sources

                branch_parent_ids[branch_number] = {
                    source.parent_id for source in branch_sources
                }
                log_event(
                    request_logger,
                    "chat_branch_completed",
                    request_id=request_id,
                    branch_number=branch_number,
                    branch_query=sub_query,
                    duration_ms=round((time.perf_counter() - branch_started) * 1000, 2),
                    source_count=len(branch_sources),
                    sources=[source.model_dump() for source in branch_sources],
                )
                if not branch_sources:
                    log_event(
                        request_logger,
                        "chat_anomaly",
                        level=logging.WARNING,
                        request_id=request_id,
                        anomaly="branch_without_retrieved_sources",
                        branch_number=branch_number,
                        branch_query=sub_query,
                    )
                for source in branch_sources:
                    if source.parent_id not in seen_parents:
                        seen_parents.add(source.parent_id)
                        all_sources.append(source)

            unique_source_count = len(all_sources)
            selected_parent_ids = {source.parent_id for source in all_sources}
            unrepresented_branches = [
                branch_number
                for branch_number, parent_ids in branch_parent_ids.items()
                if not parent_ids.intersection(selected_parent_ids)
            ]
            log_event(
                request_logger,
                "chat_sources_selected",
                request_id=request_id,
                unique_source_count=unique_source_count,
                selected_source_count=len(all_sources),
                selected_parent_ids=[source.parent_id for source in all_sources],
                branch_parent_ids={
                    str(number): sorted(parent_ids)
                    for number, parent_ids in branch_parent_ids.items()
                },
                unrepresented_branches=unrepresented_branches,
            )
            if unrepresented_branches:
                log_event(
                    request_logger,
                    "chat_anomaly",
                    level=logging.WARNING,
                    request_id=request_id,
                    anomaly="branch_without_selected_source",
                    unrepresented_branches=unrepresented_branches,
                )
            started = time.perf_counter()
            answer, mode = await asyncio.to_thread(
                chat_service.generate, payload.query, all_sources
            )
            generation_duration_ms = round(
                (time.perf_counter() - started) * 1000, 2
            )
            generation_step = PipelineStep(
                id="generation",
                label="Grounded answer generation",
                status="complete" if mode == "generated" else "skipped",
                duration_ms=generation_duration_ms,
                detail=(
                    "Grounded answer created"
                    if mode == "generated"
                    else "Retrieval-only mode"
                ),
            )
            steps.append(generation_step)
            log_event(
                request_logger,
                "chat_generation_completed",
                request_id=request_id,
                mode=mode,
                duration_ms=generation_duration_ms,
                answer_length=len(answer),
                selected_source_count=len(all_sources),
            )
            if mode != "generated":
                log_event(
                    request_logger,
                    "chat_anomaly",
                    level=logging.WARNING,
                    request_id=request_id,
                    anomaly="generation_fell_back_to_retrieval_only",
                    mode=mode,
                    selected_source_count=len(all_sources),
                )
            yield format_sse("step", generation_step.model_dump())
            response = ChatResponse(
                query=payload.query,
                answer=answer,
                sub_queries=sub_queries,
                mode=mode,
                sources=all_sources,
                steps=steps,
            )
            log_event(
                request_logger,
                "chat_completed",
                request_id=request_id,
                total_duration_ms=round(
                    (time.perf_counter() - request_started) * 1000, 2
                ),
                response=response.model_dump(),
            )
            yield format_sse("result", response.model_dump())
        except Exception as exc:
            log_event(
                request_logger,
                "chat_failed",
                level=logging.ERROR,
                exc_info=True,
                request_id=request_id,
                query=payload.query,
                error_type=type(exc).__name__,
                error_message=str(exc),
                total_duration_ms=round(
                    (time.perf_counter() - request_started) * 1000, 2
                ),
                completed_steps=[step.model_dump() for step in steps],
                collected_parent_ids=[source.parent_id for source in all_sources],
            )
            yield format_sse("error", {"message": str(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
