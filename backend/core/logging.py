"""Structured, rotating logging for HTTP and retrieval-pipeline events."""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    exc_info: bool = False,
    **fields: Any,
) -> None:
    """Write one parseable JSON event without exposing logger formatting details."""
    payload = {"event": event, **fields}
    logger.log(
        level,
        json.dumps(payload, ensure_ascii=False, default=str),
        exc_info=exc_info,
    )


def configure_request_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("constitution_rag.requests")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    resolved_path = str(log_path.resolve())
    if not any(
        isinstance(handler, logging.FileHandler)
        and handler.baseFilename == resolved_path
        for handler in logger.handlers
    ):
        handler = RotatingFileHandler(
            log_path,
            maxBytes=20 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
        )
        logger.addHandler(handler)

    return logger
