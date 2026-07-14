# SYJ AI

**An open-source, local-first, autonomous AI software engineering agent — built to run entirely from Android + Termux.**

SYJ AI acts as a full engineering team (architect, backend/frontend engineer, DevOps, security, QA, docs, and research) driven by a single master system prompt, and orchestrates two local models through [Ollama](https://ollama.com):

- **QwenCoder** — code generation, refactors, components
- **DeepSeek** — planning, research, debugging, review

Every task runs through a fixed workflow: **Plan → Research → Design → Code → Review → Verify → Optimize → Document.** Nothing skips verification, and generated code is written straight into a real project workspace on disk.

## Why

Most AI coding agents assume a laptop, cloud credits, and always-on network access. SYJ AI assumes none of that: it's designed to be fully usable offline, on-device, from a phone.

## Features

- 🔒 **Local-first** — runs against Ollama on `localhost`; no data leaves the device by default
- 📴 **Offline-capable** — no internet required once models are pulled
- 🧩 **Modular** — swap models, add workflow stages, or add tools without touching the core
- 🗂️ **Real files, not chat text** — coding-stage output is parsed and written into a workspace directory
- 📱 **Termux-native** — every dependency installs cleanly on Android via Termux
- 🛡️ **Safety-conscious** — shell commands require explicit confirmation; filesystem access is sandboxed to the workspace
- ☁️ **Optional remote fallback** — if Ollama is unreachable, can gracefully fall back to a remote API (off by default)

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed and running (`ollama serve`)
- The coding and reasoning models pulled locally:
  ```bash
  ollama pull qwen2.5-coder:7b
  ollama pull deepseek-r1:7b
  ```

## Installation

### Android (Termux)

```bash
pkg update && pkg install python git -y
git clone https://github.com/SHalimoosavi/syj-ai.git
cd syj-ai
pip install -e .
cp .env.example .env
```

### Linux / macOS

```bash
git clone https://github.com/SHalimoosavi/syj-ai.git
cd syj-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
```

### Windows (PowerShell)

```powershell
git clone https://github.com/SHalimoosavi/syj-ai.git
cd syj-ai
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

### Windows (CMD)

```cmd
git clone https://github.com/SHalimoosavi/syj-ai.git
cd syj-ai
python -m venv .venv && .venv\Scripts\activate.bat
pip install -e .
copy .env.example .env
```

## Usage

Check that Ollama and your models are reachable:

```bash
syj doctor
```

Run a full task through the engineering workflow:

```bash
syj build "Build a FastAPI todo API with SQLite and JWT auth"
```

Run only specific stages:

```bash
syj build "Add rate limiting to the API" --stage plan,design,code
```

Freeform chat, using the SYJ AI system prompt:

```bash
syj chat
```

Generated files land in `./syj_workspace` by default (configurable via `SYJ_WORKSPACE` in `.env`).

## Configuration

All configuration lives in `.env` — see [`.env.example`](.env.example) for the full list of options (workspace path, Ollama host, model names, timeouts, optional remote fallback, shell confirmation, logging).

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown of the package layout, the model router, the workflow engine, and the sandboxed tools.

## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `syj doctor` reports Ollama unreachable | Ollama isn't running | `ollama serve` |
| A stage errors with `ModelBackendUnavailable` | Wanted model isn't pulled | `ollama pull <model>` |
| `WorkspaceEscapeError` | Model tried to write outside the workspace | Expected — this is the sandbox working correctly |
| `ShellPermissionDenied` | Command needs confirmation, or matches a destructive pattern | Re-run with explicit confirmation, or don't run it |

## Roadmap

- [ ] Streaming responses in `syj chat` and `syj build`
- [ ] Pluggable tool registry (beyond filesystem/shell/git)
- [ ] Web dashboard as an alternative to the CLI
- [ ] Multi-file diff review before writing to the workspace

## Contributing

Issues and PRs are welcome. Keep changes modular, typed, and tested — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) before adding new stages or tools.

## License

[MIT](LICENSE) © Syed Ali Hasan Moosavi / SAYANJALI NEXUS PRIVATE LIMITED
