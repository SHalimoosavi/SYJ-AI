"""Filesystem access scoped to the active workspace.

Every path is resolved relative to the workspace root and checked to ensure
it can't escape that root (no writing to arbitrary system paths).
"""

from __future__ import annotations

from pathlib import Path


class WorkspaceEscapeError(ValueError):
    pass


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if self.root not in candidate.parents and candidate != self.root:
            raise WorkspaceEscapeError(
                f"Refusing to access '{relative_path}': outside workspace {self.root}"
            )
        return candidate

    def write_file(self, relative_path: str, content: str) -> Path:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_file(self, relative_path: str) -> str:
        return self._resolve(relative_path).read_text(encoding="utf-8")

    def exists(self, relative_path: str) -> bool:
        return self._resolve(relative_path).exists()

    def list_files(self, relative_dir: str = ".") -> list[str]:
        base = self._resolve(relative_dir)
        if not base.exists():
            return []
        return sorted(
            str(p.relative_to(self.root)) for p in base.rglob("*") if p.is_file()
        )

    def delete_file(self, relative_path: str) -> None:
        path = self._resolve(relative_path)
        if path.exists():
            path.unlink()
