# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-07-15

### Added
- Initial public release of SYJ AI.
- Master system prompt defining the agent's identity, philosophy, and workflow.
- Local-first model router (Ollama) with QwenCoder (coding) / DeepSeek (reasoning) roles.
- Fixed Plan → Research → Design → Code → Review → Verify → Optimize → Document workflow.
- Sandboxed workspace filesystem tool, gated shell execution, git helper.
- File-annotated code block parser that writes coding-stage output to disk.
- CLI: `syj doctor`, `syj build`, `syj chat`.
- Optional, disabled-by-default remote fallback for when Ollama is unreachable.
- Test suite (pytest) covering tools, router fallback behavior, and code block parsing.
