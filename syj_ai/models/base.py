"""Shared types for model backends."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ModelRole(str, Enum):
    """Which specialist model a workflow stage should talk to."""

    CODING = "coding"       # QwenCoder — generation, refactors, components
    REASONING = "reasoning"  # DeepSeek — planning, debugging, review


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class ModelResponse:
    content: str
    model: str
    backend: str  # "ollama" | "fallback"
    raw: dict | None = None


class ModelBackendUnavailable(RuntimeError):
    """Raised when a backend cannot be reached at all (used for fallback logic)."""


class ChatClient(Protocol):
    def chat(self, messages: list[ChatMessage], model: str) -> ModelResponse: ...
