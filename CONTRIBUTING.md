# Contributing to SYJ AI

Thanks for considering a contribution. SYJ AI is built and maintained
primarily from an Android/Termux workflow, so contributions that keep the
project lightweight and dependency-light are especially welcome.

## Ground rules

These come directly from the project's master system prompt
(`prompts/master_system_prompt.md`) and apply to code contributions too:

- Prefer the standard library over new dependencies where reasonable.
- Anything added must install cleanly in Termux (avoid heavy native builds).
- SQLite before PostgreSQL, unless a change is explicitly cloud/production-only.
- No hardcoded secrets — configuration goes through `.env` / `config.py`.
- New behavior needs tests; new tools/stages need a docs update.

## Development setup

```bash
git clone https://github.com/SHalimoosavi/syj-ai.git
cd syj-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Running tests

```bash
pytest -q
```

## Making changes

1. Open an issue first for anything non-trivial (new workflow stage, new
   tool, behavior change) so the approach can be discussed.
2. Keep pull requests focused — one logical change per PR.
3. Add or update tests under `tests/` for any new behavior.
4. Update `README.md` and/or `docs/ARCHITECTURE.md` if the change is
   user-facing or architectural.
5. Make sure `pytest -q` passes before opening the PR.

## Reporting issues

Please include: your OS/Termux version, Python version, the output of
`syj doctor`, and steps to reproduce.

## Code of conduct

Be respectful, assume good faith, and keep discussion focused on the work.
