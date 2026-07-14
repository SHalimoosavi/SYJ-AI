import pytest

from syj_ai.config import SYJConfig
from syj_ai.models.base import ChatMessage, ModelBackendUnavailable, ModelResponse, ModelRole
from syj_ai.models.router import ModelRouter


def test_chat_uses_ollama_when_available(monkeypatch):
    router = ModelRouter(SYJConfig())

    def fake_chat(messages, model):
        return ModelResponse(content="hello from ollama", model=model, backend="ollama")

    monkeypatch.setattr(router.ollama, "chat", fake_chat)
    response = router.chat(ModelRole.CODING, [ChatMessage(role="user", content="hi")])
    assert response.backend == "ollama"
    assert response.content == "hello from ollama"


def test_chat_raises_when_ollama_down_and_fallback_disabled(monkeypatch):
    config = SYJConfig()
    config.fallback.enabled = False
    router = ModelRouter(config)

    def fake_chat(messages, model):
        raise ModelBackendUnavailable("down")

    monkeypatch.setattr(router.ollama, "chat", fake_chat)
    with pytest.raises(ModelBackendUnavailable):
        router.chat(ModelRole.REASONING, [ChatMessage(role="user", content="hi")])


def test_coding_and_reasoning_use_different_models():
    router = ModelRouter(SYJConfig())
    assert router._model_for(ModelRole.CODING) == router.config.ollama.coding_model
    assert router._model_for(ModelRole.REASONING) == router.config.ollama.reasoning_model
