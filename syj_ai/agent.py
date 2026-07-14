"""SYJ AI's core orchestrator.

Runs a user task through the fixed Plan -> Research -> Design -> Code ->
Review -> Verify -> Optimize -> Document workflow, keeping a running
conversation so each stage has the full context of the ones before it.
Coding-stage output is scanned for file-annotated code blocks and written
into the active workspace.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from syj_ai.config import SYJConfig, get_config
from syj_ai.models.base import ChatMessage, ModelBackendUnavailable
from syj_ai.models.router import ModelRouter
from syj_ai.tools.filesystem import Workspace
from syj_ai.utils.logger import get_logger
from syj_ai.workflow.codeblocks import extract_file_blocks
from syj_ai.workflow.stages import WORKFLOW, Stage

logger = get_logger(__name__)


@dataclass
class StageResult:
    stage: Stage
    output: str
    backend: str
    files_written: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    task: str
    stage_results: list[StageResult] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"SYJ AI task: {self.task}", ""]
        for result in self.stage_results:
            lines.append(f"## {result.stage.title} ({result.backend})")
            lines.append(result.output.strip())
            if result.files_written:
                lines.append("")
                lines.append("Files written:")
                lines.extend(f"  - {f}" for f in result.files_written)
            lines.append("")
        return "\n".join(lines)


class SYJAgent:
    def __init__(self, config: SYJConfig | None = None):
        self.config = config or get_config()
        self.router = ModelRouter(self.config)
        self.workspace = Workspace(self.config.workspace)
        self.system_prompt = self.config.load_system_prompt()

    def run(self, task: str, stages: list[Stage] | None = None) -> TaskResult:
        stages = stages if stages is not None else WORKFLOW
        result = TaskResult(task=task)

        history: list[ChatMessage] = [ChatMessage(role="system", content=self.system_prompt)]
        history.append(ChatMessage(role="user", content=f"Task: {task}"))

        for stage in stages:
            logger.info("Running stage: %s", stage.title)
            history.append(
                ChatMessage(
                    role="user",
                    content=f"[Stage: {stage.title}]\n{stage.instruction}",
                )
            )
            try:
                response = self.router.chat(stage.role, history)
            except ModelBackendUnavailable as exc:
                logger.error("Stage '%s' failed: %s", stage.title, exc)
                stage_result = StageResult(stage=stage, output=f"ERROR: {exc}", backend="none")
                result.stage_results.append(stage_result)
                # Per the master prompt, never silently stop the whole workflow —
                # record the failure and continue so later stages can still run.
                continue

            history.append(ChatMessage(role="assistant", content=response.content))

            files_written: list[str] = []
            if stage.key == "code":
                files_written = self._write_file_blocks(response.content)

            result.stage_results.append(
                StageResult(
                    stage=stage,
                    output=response.content,
                    backend=response.backend,
                    files_written=files_written,
                )
            )

        return result

    def _write_file_blocks(self, content: str) -> list[str]:
        written = []
        for block in extract_file_blocks(content):
            try:
                path = self.workspace.write_file(block.path, block.content)
                written.append(str(path.relative_to(self.workspace.root)))
            except Exception as exc:  # noqa: BLE001 - log and keep going
                logger.warning("Could not write '%s': %s", block.path, exc)
        return written
