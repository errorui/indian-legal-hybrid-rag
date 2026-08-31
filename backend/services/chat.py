from __future__ import annotations

from ..core.config import Settings
from ..models.schemas import ParentSource
from .answer_generation import GroundedAnswerGenerator
from .llm_client import ChatProvider
from .query_fanout import QueryFanout


class ChatService:
    """Application facade combining independent query and answer services."""

    def __init__(self, provider: ChatProvider, config: Settings) -> None:
        self._fanout = QueryFanout(provider, config.fanout_model)
        self._generator = GroundedAnswerGenerator(provider, config.generation_model)

    @property
    def generation_available(self) -> bool:
        return self._fanout.client.available

    def fanout(self, query: str) -> list[str]:
        return self._fanout.expand(query)

    def generate(self, query: str, sources: list[ParentSource]) -> tuple[str, str]:
        return self._generator.generate(query, sources)
