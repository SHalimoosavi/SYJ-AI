"""Extracts file-annotated code blocks from a model's markdown response.

SYJ AI asks the coding model to annotate each fenced block with its target
path, e.g.:

    ```python:app/main.py
    ...
    ```

This module parses that convention back into (path, content) pairs so the
agent can write real files instead of leaving code trapped in chat text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_BLOCK_RE = re.compile(
    r"```[a-zA-Z0-9_+\-]*:(?P<path>[^\n`]+)\n(?P<content>.*?)```",
    re.DOTALL,
)


@dataclass
class FileBlock:
    path: str
    content: str


def extract_file_blocks(markdown_text: str) -> list[FileBlock]:
    blocks = []
    for match in _BLOCK_RE.finditer(markdown_text):
        path = match.group("path").strip()
        content = match.group("content")
        if content.endswith("\n"):
            content = content[:-1]
        blocks.append(FileBlock(path=path, content=content))
    return blocks
