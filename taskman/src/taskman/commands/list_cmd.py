"""`list` command — walk the tree and print items, optionally filtered/JSON."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from taskman.commands.new import get_tasks_dir
from taskman.model.layout import iter_work_items
from taskman.model.names import NameParseError, parse_name, special_file_name
from taskman.model.yaml_io import read_file


def _read_title(path: Path, item_id: str) -> str:
    """Return the title from a work item's body file, or empty on failure."""
    body_file = path / special_file_name(item_id) if path.is_dir() else path
    if not body_file.exists():
        return ""
    try:
        data, _ = read_file(body_file)
        return str(data.get("title", ""))
    except Exception:
        return ""


def list_items(
    status: str | None = typer.Option(None, "--status", help="Filter by status."),
    item_type: str | None = typer.Option(None, "--type", help="Filter by type."),
    as_json: bool = typer.Option(False, "--json", help="Emit structured JSON."),
) -> None:
    """List work items in the tree, optionally filtered, optionally as JSON."""
    tasks_dir = get_tasks_dir()
    rows: list[dict[str, str]] = []
    for path in iter_work_items(tasks_dir):
        try:
            wi = parse_name(path.name)
        except NameParseError:
            continue
        if status is not None and wi.status != status:
            continue
        if item_type is not None and wi.item_type != item_type:
            continue
        rows.append(
            {
                "priority": wi.priority,
                "type": wi.item_type,
                "id": wi.item_id,
                "status": wi.status,
                "slug": wi.slug,
                "title": _read_title(path, wi.item_id),
                "path": str(path),
            }
        )
    rows.sort(key=lambda r: (r["status"], r["priority"], r["id"]))

    if as_json:
        typer.echo(json.dumps(rows, indent=2))
        return

    if not rows:
        typer.echo("(no items)")
        return

    by_status: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_status.setdefault(row["status"], []).append(row)
    for s in ("backlog", "active", "done"):
        if s not in by_status:
            continue
        typer.echo(f"\n[{s.upper()}]")
        for row in by_status[s]:
            typer.echo(
                f"  {row['priority']} {row['type']:5} {row['id']} "
                f"{row['slug']:30} {row['title']}"
            )
