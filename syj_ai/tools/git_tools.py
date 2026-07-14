"""Thin wrapper around git for the Open Source Maintainer role.

Kept deliberately small: SYJ AI shells out to the system `git` binary rather
than bundling a git implementation, since Termux already ships git.
"""

from __future__ import annotations

from pathlib import Path

from syj_ai.tools.shell import ShellResult, run_command


def git_init(repo_path: Path) -> ShellResult:
    return run_command("git init", cwd=repo_path, require_confirmation=False)


def git_status(repo_path: Path) -> ShellResult:
    return run_command("git status --short", cwd=repo_path, require_confirmation=False)


def git_add_all(repo_path: Path) -> ShellResult:
    return run_command("git add -A", cwd=repo_path, require_confirmation=False)


def git_commit(repo_path: Path, message: str) -> ShellResult:
    safe_message = message.replace('"', '\\"')
    return run_command(
        f'git commit -m "{safe_message}"', cwd=repo_path, require_confirmation=False
    )
