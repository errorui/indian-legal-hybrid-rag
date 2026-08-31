from __future__ import annotations

from typing import Any, Protocol

from ..core.config import Settings


class ChatProvider(Protocol):
    """Provider contract required by query fan-out and answer generation."""

    @property
    def available(self) -> bool: ...

    def chat(self, **kwargs: Any) -> dict[str, Any]: ...


class OllamaChatProvider:
    """Ollama implementation of the provider contract."""

    def __init__(self, config: Settings) -> None:
        self.config = config
        self._client: Any = None

    @property
    def available(self) -> bool:
        return bool(self.config.ollama_api_key)

    def chat(self, **kwargs: Any) -> dict[str, Any]:
        if self._client is None:
            if not self.config.ollama_api_key:
                raise RuntimeError("Generation provider credentials are not configured")
            from ollama import Client

            self._client = Client(
                host=self.config.ollama_host,
                headers={"Authorization": f"Bearer {self.config.ollama_api_key}"},
            )
        return self._client.chat(**kwargs)
