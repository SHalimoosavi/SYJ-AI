"""Central configuration for SYJ AI.

All configuration is read from environment variables (optionally loaded from a
.env file via python-dotenv). Nothing here is hardcoded that shouldn't be —
per the master system prompt's security rules, no secrets live in source.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; SYJ AI still works with real env vars only.
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DEFAULT_WORKSPACE = Path(os.getenv("SYJ_WORKSPACE", Path.cwd() / "syj_workspace"))


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class OllamaConfig:
    host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    coding_model: str = field(default_factory=lambda: os.getenv("SYJ_CODING_MODEL", "qwen2.5-coder:7b"))
    reasoning_model: str = field(default_factory=lambda: os.getenv("SYJ_REASONING_MODEL", "deepseek-r1:7b"))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("SYJ_OLLAMA_TIMEOUT", "180")))


@dataclass
class FallbackConfig:
    """Remote fallback used only if Ollama is unreachable. Never required."""

    enabled: bool = field(default_factory=lambda: _bool_env("SYJ_ENABLE_REMOTE_FALLBACK", False))
    api_key_env: str = "ANTHROPIC_API_KEY"
    model: str = field(default_factory=lambda: os.getenv("SYJ_FALLBACK_MODEL", "claude-sonnet-4-6"))


@dataclass
class SYJConfig:
    workspace: Path = DEFAULT_WORKSPACE
    system_prompt_path: Path = PROMPTS_DIR / "master_system_prompt.md"
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    fallback: FallbackConfig = field(default_factory=FallbackConfig)
    log_level: str = field(default_factory=lambda: os.getenv("SYJ_LOG_LEVEL", "INFO"))
    require_shell_confirmation: bool = field(
        default_factory=lambda: _bool_env("SYJ_REQUIRE_SHELL_CONFIRMATION", True)
    )

    def load_system_prompt(self) -> str:
        return self.system_prompt_path.read_text(encoding="utf-8")


def get_config() -> SYJConfig:
    return SYJConfig()
