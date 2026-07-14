"""SYJ AI command-line interface.

Usage:
    syj doctor                 Check that Ollama and required models are reachable
    syj build "<task>"         Run a task through the full engineering workflow
    syj build "<task>" --stage plan,research   Run only specific stages
    syj chat                   Freeform chat with SYJ AI using the system prompt
"""

from __future__ import annotations

import argparse
import sys

from syj_ai.agent import SYJAgent
from syj_ai.config import get_config
from syj_ai.models.base import ChatMessage
from syj_ai.models.ollama_client import OllamaClient
from syj_ai.workflow.stages import WORKFLOW


def cmd_doctor(_args: argparse.Namespace) -> int:
    config = get_config()
    client = OllamaClient(host=config.ollama.host, timeout_seconds=10)
    print(f"Workspace:        {config.workspace}")
    print(f"Ollama host:      {config.ollama.host}")

    if not client.is_available():
        print("Ollama:           UNREACHABLE — start it with `ollama serve`")
        return 1
    print("Ollama:           reachable")

    models = client.list_models()
    print(f"Installed models: {', '.join(models) if models else '(none found)'}")

    for role, wanted in (
        ("coding", config.ollama.coding_model),
        ("reasoning", config.ollama.reasoning_model),
    ):
        status = "OK" if any(wanted in m for m in models) else "MISSING — run `ollama pull " + wanted + "`"
        print(f"  {role:9s} -> {wanted:20s} [{status}]")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    agent = SYJAgent()
    stages = None
    if args.stage:
        wanted_keys = {s.strip() for s in args.stage.split(",")}
        stages = [s for s in WORKFLOW if s.key in wanted_keys]
        if not stages:
            print(f"No matching stages for: {args.stage}", file=sys.stderr)
            return 1

    result = agent.run(args.task, stages=stages)
    print(result.summary())
    return 0


def cmd_chat(_args: argparse.Namespace) -> int:
    from syj_ai.models.router import ModelRouter
    from syj_ai.models.base import ModelRole

    config = get_config()
    router = ModelRouter(config)
    history = [ChatMessage(role="system", content=config.load_system_prompt())]

    print("SYJ AI chat — type 'exit' to quit.")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if user_input.lower() in {"exit", "quit"}:
            return 0
        if not user_input:
            continue
        history.append(ChatMessage(role="user", content=user_input))
        response = router.chat(ModelRole.REASONING, history)
        history.append(ChatMessage(role="assistant", content=response.content))
        print(f"syj ({response.backend})> {response.content}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="syj", description="SYJ AI — local-first AI software engineering agent")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Check Ollama connectivity and required models")
    doctor.set_defaults(func=cmd_doctor)

    build = sub.add_parser("build", help="Run a task through the full engineering workflow")
    build.add_argument("task", help="Description of what to build")
    build.add_argument("--stage", help="Comma-separated stage keys to run, e.g. plan,design")
    build.set_defaults(func=cmd_build)

    chat = sub.add_parser("chat", help="Freeform chat with SYJ AI")
    chat.set_defaults(func=cmd_chat)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
