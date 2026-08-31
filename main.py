"""Compatibility entrypoint for the Constitution RAG API.

The implementation lives in :mod:`backend.app`; this module keeps the existing
``uvicorn main:app`` command and test imports working.
"""

from backend.app import app, create_app
from backend.services.sparse_retrieval import tokenize
from backend.utils.text import extract_article_references, make_excerpt

__all__ = ["app", "create_app", "extract_article_references", "make_excerpt", "tokenize"]
