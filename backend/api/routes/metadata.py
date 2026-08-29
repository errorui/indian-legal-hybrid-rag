from fastapi import APIRouter

from ...core.constants import DISCLAIMER, PIPELINE_STAGES
from ...models.schemas import MetaResponse
from ..dependencies import RetrieverDependency, SettingsDependency


router = APIRouter(prefix="/api", tags=["metadata"])


@router.get("/meta", response_model=MetaResponse)
async def metadata(
    retriever: RetrieverDependency,
    settings: SettingsDependency,
) -> MetaResponse:
    return MetaResponse(
        corpus_name=settings.corpus_name,
        corpus_date=settings.corpus_date,
        parent_count=len(retriever.parents),
        child_count=len(retriever.children),
        pipeline=PIPELINE_STAGES,
        disclaimer=DISCLAIMER,
    )
