"""Shell command execution, scoped to a working directory.

Security rules from the master system prompt apply: never fabricate silent
side effects. Destructive-looking commands require confirmation unless the
caller explicitly disables it (e.g. for non-interactive CI use).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

_DANGEROUS_PATTERNS = ("rm -rf /", "mkfs", ":(){ :|:& };:", "> /dev/sda", "dd if=")


@dataclass
class ShellResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class ShellPermissionDenied(RuntimeError):
    pass


def _looks_dangerous(command: str) -> bool:
    return any(pattern in command for pattern in _DANGEROUS_PATTERNS)


def run_command(
    command: str,
    cwd: Path,
    require_confirmation: bool = True,
    confirmed: bool = False,
    timeout_seconds: int = 120,
) -> ShellResult:
    if _looks_dangerous(command):
        raise ShellPermissionDenied(f"Refusing to run a destructive command: {command}")

    if require_confirmation and not confirmed:
        raise ShellPermissionDenied(
            f"Command '{command}' requires explicit confirmation before running. "
            "Pass confirmed=True once the user has approved it."
        )

    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return ShellResult(
        command=command, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr
    )
