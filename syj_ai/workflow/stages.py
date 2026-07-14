"""The fixed engineering workflow every SYJ AI task moves through.

Per the master system prompt: never skip verification, never produce code
without first planning. Each stage declares which specialist model it needs.
"""

from __future__ import annotations

from dataclasses import dataclass

from syj_ai.models.base import ModelRole


@dataclass(frozen=True)
class Stage:
    key: str
    title: str
    role: ModelRole
    instruction: str


WORKFLOW: list[Stage] = [
    Stage(
        key="plan",
        title="Plan",
        role=ModelRole.REASONING,
        instruction=(
            "Break the request into a clear objective and an ordered list of "
            "concrete engineering tasks. State any assumptions explicitly."
        ),
    ),
    Stage(
        key="research",
        title="Research",
        role=ModelRole.REASONING,
        instruction=(
            "Identify relevant prior art, libraries, or approaches. Compare at "
            "least two alternatives where a real choice exists and recommend the "
            "most maintainable one, with reasoning."
        ),
    ),
    Stage(
        key="design",
        title="Design",
        role=ModelRole.REASONING,
        instruction=(
            "Produce a concrete architecture: folder structure, modules, data "
            "model, and how components interact. Favor SQLite, FastAPI, and "
            "Termux-friendly dependencies unless the plan says otherwise."
        ),
    ),
    Stage(
        key="code",
        title="Code",
        role=ModelRole.CODING,
        instruction=(
            "Implement the design as complete, runnable source files — no "
            "placeholders or TODOs unless explicitly requested. Include "
            "configuration, error handling, and typing."
        ),
    ),
    Stage(
        key="review",
        title="Review",
        role=ModelRole.REASONING,
        instruction=(
            "Critically review the generated code for correctness, security "
            "(input validation, secrets handling, injection risks), and "
            "adherence to the design. List concrete issues, not vague praise."
        ),
    ),
    Stage(
        key="verify",
        title="Verify",
        role=ModelRole.CODING,
        instruction=(
            "Write or update tests that verify the implementation, and state "
            "how to run them. Flag anything that could not be verified."
        ),
    ),
    Stage(
        key="optimize",
        title="Optimize",
        role=ModelRole.REASONING,
        instruction=(
            "Identify concrete performance, memory, or clarity improvements. "
            "Apply the ones that are low-risk; note the rest as follow-ups."
        ),
    ),
    Stage(
        key="document",
        title="Document",
        role=ModelRole.CODING,
        instruction=(
            "Write or update README/architecture docs covering installation, "
            "configuration, usage, testing, and troubleshooting."
        ),
    ),
]
