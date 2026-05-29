"""YAML frontmatter read/write that preserves comments and key order.

Uses ``ruamel.yaml`` round-trip mode so YAML comments and formatting survive
parse-modify-emit cycles. Frontmatter is delimited by ``---`` fences at the
top of the file; everything after the closing fence is body.
"""
from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

_FENCE = "---"

_yaml = YAML(typ="rt")
_yaml.indent(mapping=2, sequence=4, offset=2)
_yaml.preserve_quotes = True


class FrontmatterError(ValueError):
    """Raised on malformed frontmatter (missing or unbalanced fences)."""


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split markdown text into ``(frontmatter dict, body string)``.

    The file must start with ``---``, contain YAML, then a closing ``---``,
    then the body. An empty frontmatter block (``---\\n---``) yields an
    empty dict.
    """
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != _FENCE:
        raise FrontmatterError(f"expected first line to be {_FENCE!r}")
    try:
        end_idx = lines.index(_FENCE, 1)
    except ValueError as exc:
        raise FrontmatterError(f"no closing {_FENCE!r} found") from exc
    yaml_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])
    if body.startswith("\n"):
        body = body[1:]
    data = _yaml.load(yaml_text)
    if data is None:
        data = {}
    return data, body


def emit_frontmatter(data: dict[str, Any], body: str) -> str:
    """Render ``data`` + ``body`` as a frontmatter-style markdown document."""
    buf = StringIO()
    _yaml.dump(data, buf)
    yaml_text = buf.getvalue()
    if not yaml_text.endswith("\n"):
        yaml_text += "\n"
    return f"{_FENCE}\n{yaml_text}{_FENCE}\n\n{body}"


def read_file(path: Path) -> tuple[dict[str, Any], str]:
    """Read a markdown file with frontmatter; return ``(data, body)``."""
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_file(path: Path, data: dict[str, Any], body: str) -> None:
    """Write a markdown file with frontmatter."""
    path.write_text(emit_frontmatter(data, body), encoding="utf-8")
