"""LLM client abstraction and OpenAI implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


class LLMClient(Protocol):
    """Simple interface to support dependency injection and testing."""

    def chat(self, messages: List[dict], model: str) -> str:
        """Return the assistant text response for a chat completion call."""


@dataclass
class OpenAILLMClient:
    """OpenAI chat-completions adapter."""

    api_key: str | None = None

    def __post_init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "openai package is not installed. Install dependencies first."
            ) from exc

        self._client = OpenAI(api_key=self.api_key)

    def chat(self, messages: List[dict], model: str) -> str:
        completion = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        return completion.choices[0].message.content or ""
