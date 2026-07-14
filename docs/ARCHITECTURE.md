# SYJ AI — Architecture

## Package Layout

```
syj-ai/
├── syj_ai/
│   ├── __main__.py        CLI entry point (syj doctor|build|chat)
│   ├── agent.py           Core orchestrator: runs a task through the workflow
│   ├── config.py          All configuration, read from env / .env
│   ├── models/
│   │   ├── base.py        Shared types: ChatMessage, ModelResponse, ModelRole
│   │   ├── ollama_client.py   HTTP client for local Ollama (/api/chat, /api/tags)
│   │   └── router.py      Picks coding vs. reasoning model; handles fallback
│   ├── tools/
│   │   ├── filesystem.py  Workspace — sandboxed read/write scoped to one root
│   │   ├── shell.py       Gated command execution (confirmation + blocklist)
│   │   └── git_tools.py   Thin wrapper around the system git binary
│   ├── workflow/
│   │   ├── stages.py      The fixed Plan→...→Document stage definitions
│   │   └── codeblocks.py  Parses ```lang:path fenced blocks into files
│   └── utils/logger.py    Stdlib logging setup
├── prompts/master_system_prompt.md   The identity/behavior contract for the agent
├── tests/                 pytest suite covering tools, router, and parsing
└── docs/                  This file, plus anything else worth documenting
```

## Data Flow

1. `syj build "<task>"` constructs a `SYJAgent`, which loads `config.py` and
   the master system prompt from `prompts/master_system_prompt.md`.
2. The agent walks the ordered `WORKFLOW` list from `workflow/stages.py`. Each
   `Stage` declares which model role (`coding` or `reasoning`) it needs and an
   instruction appended to a running conversation.
3. `ModelRouter.chat()` resolves the role to a concrete model name from
   `config.ollama.coding_model` / `reasoning_model` and calls
   `OllamaClient.chat()`, which POSTs to `http://localhost:11434/api/chat`.
4. If Ollama can't be reached, the router raises `ModelBackendUnavailable`.
   The agent logs the failure for that stage and **continues to the next
   stage** rather than aborting the whole run — matching the master prompt's
   "never stop the workflow because a model is unavailable" rule. If
   `SYJ_ENABLE_REMOTE_FALLBACK=true`, the router instead retries through a
   remote API before giving up.
5. For the `code` stage specifically, the response text is scanned by
   `workflow/codeblocks.py` for fenced blocks annotated with a path
   (` ```python:app/main.py `). Each match is written to disk through
   `tools/filesystem.Workspace`, which resolves every path against the
   workspace root and refuses anything that would escape it.
6. `TaskResult.summary()` renders every stage's output plus the list of files
   written, which the CLI prints to stdout.

## Why these design choices

- **Two models, one router.** Coding and reasoning have different strengths;
  keeping them as separate roles (rather than one general-purpose call) lets
  each stage use the model best suited to it, and lets users swap either
  model independently via `.env`.
- **File-annotated code fences instead of a tool-calling loop.** Termux and
  small local models don't reliably support function-calling APIs. Parsing a
  simple, explicit text convention is more portable and easier to debug than
  depending on structured tool use from the coding model.
- **Sandboxed workspace, not the whole filesystem.** The agent should never
  be able to write outside its project directory, even if a model
  hallucinates an absolute path.
- **Shell confirmation by default.** Destructive commands are blocklisted
  outright; everything else requires an explicit `confirmed=True`, so no
  command runs without a human (or an explicit non-interactive override) in
  the loop.
- **Fail a stage, not the run.** A single unreachable model shouldn't discard
  the plan/design work already produced by earlier stages.

## Extending SYJ AI

- **Add a workflow stage:** append a `Stage(...)` to `WORKFLOW` in
  `workflow/stages.py` with a `key`, `title`, `role`, and `instruction`.
- **Add a tool:** create a module in `tools/`, keep it small and typed, and
  wire it into `agent.py` where relevant.
- **Swap models:** change `SYJ_CODING_MODEL` / `SYJ_REASONING_MODEL` in
  `.env` to any model name known to your local Ollama install.
- **Enable remote fallback:** set `SYJ_ENABLE_REMOTE_FALLBACK=true`,
  `ANTHROPIC_API_KEY`, and `pip install -e ".[fallback]"`.
