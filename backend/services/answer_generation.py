from __future__ import annotations

import logging

from ..models.schemas import ParentSource
from .llm_client import ChatProvider


logger = logging.getLogger(__name__)


class GroundedAnswerGenerator:
    def __init__(self, client: ChatProvider, model: str) -> None:
        self.client = client
        self.model = model

    @staticmethod
    def context_text(sources: list[ParentSource]) -> str:
        return "\n\n".join(
            f"SOURCE {source.rank} [{source.parent_id}]\n"
            f"Heading: {' > '.join(source.heading_path) or 'Untitled section'}\n"
            f"{source.text}"
            for source in sources
        )

    def generate(self, query: str, sources: list[ParentSource]) -> tuple[str, str]:
        if not sources:
            return (
                "The provided source corpus does not contain sufficient information to answer this question.",
                "retrieval_only",
            )
        if not self.client.available:
            return (
                f"I found {len(sources)} relevant source section(s). "
                "Answer generation is unavailable because the generation provider is not configured; "
                "inspect the retrieved source sections below.",
                "retrieval_only",
            )
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a grounded research assistant. Answer only from the provided "
                            "source text. Cite claims using [parent_id]. If the sources do not verify "
                            "a detail, say so explicitly. Do not invent facts or citations. This is a "
                            "research aid, not professional advice. Format the answer as GitHub-flavored Markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nRetrieved sources:\n{self.context_text(sources)}",
                    },
                ],
            )
            return response["message"]["content"].strip(), "generated"
        except Exception:
            logger.warning("Answer generation unavailable; returning sources only", exc_info=True)
            return (
                f"I found {len(sources)} relevant source section(s), but grounded answer generation "
                "is temporarily unavailable. Inspect the retrieved source sections below.",
                "retrieval_only",
            )
