from __future__ import annotations

import json
import logging
import re

from .llm_client import ChatProvider


JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
logger = logging.getLogger(__name__)


class QueryFanout:
    def __init__(self, client: ChatProvider, model: str) -> None:
        self.client = client
        self.model = model

    @staticmethod
    def parse(content: str, fallback: str) -> list[str]:
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
            if normalized and normalized.casefold() not in seen:
                seen.add(normalized.casefold())
                cleaned.append(normalized)
        return cleaned or [fallback]

    def expand(self, query: str) -> list[str]:
        if not self.client.available:
            return [query]
        try:
            response = self.client.chat(
                model=self.model,
                format="json",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Decompose a research question into the smallest necessary set of "
                            "distinct, self-contained retrieval questions. Keep simple questions "
                            "unchanged. Split genuinely multi-part questions. Preserve every "
                            "distinct information need and return only JSON: "
                            '{"sub_queries": ["..."]}.'
                        ),
                    },
                    {"role": "user", "content": query},
                ],
            )
            return self.parse(response["message"]["content"], query)
        except Exception:
            logger.warning("Query fan-out unavailable; using the original query", exc_info=True)
            return [query]
