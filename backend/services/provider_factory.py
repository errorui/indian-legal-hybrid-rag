from __future__ import annotations

from ..core.config import Settings
from .llm_client import ChatProvider, OllamaChatProvider


def create_chat_provider(config: Settings) -> ChatProvider:
    """Create the configured provider at the application composition boundary."""
    if config.chat_provider == "ollama":
        return OllamaChatProvider(config)
    raise ValueError(f"Unsupported chat provider: {config.chat_provider}")
