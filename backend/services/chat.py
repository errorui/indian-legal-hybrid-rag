from __future__ import annotations

import json
import logging
import re
from typing import Any

from ..core.config import Settings
from ..models.schemas import ParentSource


JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, config: Settings) -> None:
        self.config = config
        self._client: Any = None

    @property
    def generation_available(self) -> bool:
        return bool(self.config.ollama_api_key)

    def _get_client(self) -> Any:
        if self._client is None:
            if not self.config.ollama_api_key:
                raise RuntimeError("OLLAMA_API_KEY is not configured")
            from ollama import Client

            self._client = Client(
                host=self.config.ollama_host,
                headers={"Authorization": f"Bearer {self.config.ollama_api_key}"},
            )
        return self._client

    def _parse_sub_queries(self, content: str, fallback: str) -> list[str]:
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError:
            match = JSON_OBJECT_RE.search(content)
            if match is None:
                return [fallback]
            try:
                candidate = json.loads(match.group(0))
            except json.JSONDecodeError:
                return [fallback]
        values = candidate.get("sub_queries", []) if isinstance(candidate, dict) else []
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            normalized = " ".join(str(value).split())
            key = normalized.casefold()
            if normalized and key not in seen:
                seen.add(key)
                cleaned.append(normalized)
        return cleaned or [fallback]

    def fanout(self, query: str) -> list[str]:
        if not self.generation_available:
            return [query]
        try:
            response = self._get_client().chat(
                model=self.config.fanout_model,
                format="json",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You decompose Indian constitutional-law questions for retrieval. "
                            "Map named doctrines to their relevant constitutional concepts and articles; "
                            "split genuinely multi-part questions; keep simple questions unchanged. "
                            "Return precise, self-contained retrieval questions that name the relevant "
                            "constitutional concept, provision, or article when known. Use exactly one "
                            "query for a simple question and the smallest necessary set for a genuinely "
                            "multi-part question. Cover every distinct question or retrieval need in the "
                            "user's request. Queries must be distinct and non-overlapping; do not create "
                            "paraphrase variants or omit a question merely to reduce the branch count. "
                            "Return only JSON: {\"sub_queries\": [\"...\"]}."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
            )
            return self._parse_sub_queries(response["message"]["content"], query)
        except Exception:
            logger.warning("Query fan-out unavailable; using the original query", exc_info=True)
            return [query]

    def generate(self, query: str, sources: list[ParentSource]) -> tuple[str, str]:
        if not sources:
            return (
                "The provided document corpus does not contain sufficient information to answer this question.",
                "retrieval_only",
            )
        if not self.generation_available:
            return (
                f"I found {len(sources)} relevant source section(s). "
                "Answer generation is unavailable because OLLAMA_API_KEY is not configured; "
                "inspect the retrieved parent chunks below.",
                "retrieval_only",
            )

        context = "\n\n".join(
            f"SOURCE {source.rank} [{source.parent_id}]\n"
            f"Heading: {' > '.join(source.heading_path) or 'Untitled section'}\n"
            f"{source.text}"
            for source in sources
        )
        try:
            response = self._get_client().chat(
                model=self.config.generation_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a constitutional-law research assistant. Answer only from the "
                            "provided Constitution of India source text. Cite claims using [parent_id]. "
                            "If the sources do not verify a requested detail, say so explicitly. "
                            "Do not invent cases, article numbers, clauses, or facts. This is not legal advice."
                            " Format the answer as GitHub-flavored Markdown. Use valid Markdown headings, "
                            "lists, and emphasis. If a table is useful, include a header row followed by "
                            "the required delimiter row; do not emit loose pipe-separated rows."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nRetrieved sources:\n{context}",
                    },
                ],
            )
            return response["message"]["content"].strip(), "generated"
        except Exception:
            logger.warning("Answer generation unavailable; returning sources only", exc_info=True)
            return (
                f"I found {len(sources)} relevant source section(s), but grounded answer generation "
                "is temporarily unavailable. Inspect the retrieved parent chunks below.",
                "retrieval_only",
            )
