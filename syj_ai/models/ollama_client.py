"""Client for a locally running Ollama instance.

SYJ AI is local-first: this is the primary and preferred path for all model
calls. It talks to Ollama's REST API (default http://localhost:11434), which
Ollama exposes automatically once `ollama serve` is running — including
inside Termux on Android.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from syj_ai.models.base import ChatMessage, ModelBackendUnavailable, ModelResponse
from syj_ai.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", timeout_seconds: int = 180):
        self.host = host.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError, TimeoutError):
            return False

    def chat(self, messages: list[ChatMessage], model: str) -> ModelResponse:
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
        }
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            raise ModelBackendUnavailable(
                f"Could not reach Ollama at {self.host}. "
                f"Is it running? Try `ollama serve`. ({exc})"
            ) from exc

        content = body.get("message", {}).get("content", "")
        return ModelResponse(content=content, model=model, backend="ollama", raw=body)

    def list_models(self) -> list[str]:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in body.get("models", [])]
        except (urllib.error.URLError, OSError, TimeoutError, KeyError):
            return []
