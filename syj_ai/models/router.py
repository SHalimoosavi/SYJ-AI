"""Routes a chat request to the correct specialist model.

Per the master system prompt: prefer local inference through Ollama
(QwenCoder for coding, DeepSeek for reasoning). If Ollama is unreachable and
a remote fallback is explicitly enabled, fall back gracefully — the workflow
must never simply stop because a model is unavailable.
"""

from __future__ import annotations

from syj_ai.config import SYJConfig
from syj_ai.models.base import ChatMessage, ModelBackendUnavailable, ModelResponse, ModelRole
from syj_ai.models.ollama_client import OllamaClient
from syj_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ModelRouter:
    def __init__(self, config: SYJConfig):
        self.config = config
        self.ollama = OllamaClient(
            host=config.ollama.host, timeout_seconds=config.ollama.timeout_seconds
        )

    def _model_for(self, role: ModelRole) -> str:
        if role == ModelRole.CODING:
            return self.config.ollama.coding_model
        return self.config.ollama.reasoning_model

    def chat(self, role: ModelRole, messages: list[ChatMessage]) -> ModelResponse:
        model = self._model_for(role)
        try:
            return self.ollama.chat(messages, model=model)
        except ModelBackendUnavailable as exc:
            logger.warning("Ollama unavailable (%s); attempting fallback.", exc)
            return self._fallback(role, messages, original_error=exc)

    def _fallback(
        self, role: ModelRole, messages: list[ChatMessage], original_error: Exception
    ) -> ModelResponse:
        if not self.config.fallback.enabled:
            raise ModelBackendUnavailable(
                "Ollama is unavailable and remote fallback is disabled. "
                "Start Ollama with `ollama serve`, or set "
                "SYJ_ENABLE_REMOTE_FALLBACK=true and configure "
                f"{self.config.fallback.api_key_env} to allow a remote fallback."
            ) from original_error

        try:
            import anthropic  # optional dependency, only needed for fallback
        except ImportError as exc:
            raise ModelBackendUnavailable(
                "Remote fallback is enabled but the 'anthropic' package is not "
                "installed. Run: pip install anthropic"
            ) from exc

        client = anthropic.Anthropic()
        system = next((m.content for m in messages if m.role == "system"), None)
        conv = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        resp = client.messages.create(
            model=self.config.fallback.model,
            max_tokens=4096,
            system=system,
            messages=conv,
        )
        text = "".join(block.text for block in resp.content if block.type == "text")
        logger.info("Served via remote fallback (%s).", self.config.fallback.model)
        return ModelResponse(content=text, model=self.config.fallback.model, backend="fallback")
