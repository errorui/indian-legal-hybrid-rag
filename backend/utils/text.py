from __future__ import annotations

import re


def extract_article_references(text: str) -> list[str]:
    return re.findall(r"\bArticle\s+(\d+[A-Z]?)\b", text, flags=re.IGNORECASE)


def make_excerpt(text: str, limit: int = 280) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= limit else f"{normalized[: limit - 1].rstrip()}…"
