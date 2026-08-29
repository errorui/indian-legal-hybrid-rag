from fastapi import APIRouter, Request

from ...models.schemas import HealthResponse
from ...services.chat import ChatService
from ...services.retrieval import HybridRetriever


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    retriever: HybridRetriever | None = request.app.state.retriever
    chat_service: ChatService = request.app.state.chat_service
    return HealthResponse(
        status="ok" if retriever is not None else "degraded",
        corpus_loaded=retriever is not None,
        hybrid_models_loaded=bool(retriever and retriever.models_loaded),
        generation_available=chat_service.generation_available,
    )
