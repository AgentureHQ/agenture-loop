"""`move` command — relocate a top-level work item between status folders.

The item's directory or file is renamed atomically (single ``os.rename``)
and its YAML ``status`` field is updated. Children retain their own
in-name status tokens; the subtree moves with the root.

Nested items do not move via this command — they change status by
``convert`` (status-token rewrite) or by their root's move.
"""
from __future__ import annotations

import typer

from taskman.commands.new import get_tasks_dir
from taskman.model.layout import find_item_by_id, is_top_level_item
from taskman.model.names import (
    WorkItemName,
    WorkItemStatus,
    emit_name,
    parse_name,
    special_file_name,
)
from taskman.model.yaml_io import read_file, write_file

_TARGETS: tuple[WorkItemStatus, ...] = ("backlog", "active", "done")


class MoveCommandError(ValueError):
    """User-visible error from ``move``."""


def move(
    item_id: str = typer.Argument(..., help="Item ID (9 digits)."),
    target_status: str = typer.Argument(..., help="One of: backlog, active, done."),
) -> None:
    """Move a top-level work item between backlog/active/done."""
    if target_status not in _TARGETS:
        typer.echo(
            f"Error: target status must be one of {list(_TARGETS)}, got: {target_status!r}",
            err=True,
        )
        raise typer.Exit(2)

    tasks_dir = get_tasks_dir()
    path = find_item_by_id(tasks_dir, item_id)
    if path is None:
        typer.echo(f"Error: item not found: {item_id}", err=True)
        raise typer.Exit(1)
    if not is_top_level_item(path, tasks_dir):
        typer.echo(
            f"Error: only top-level items move via this command. "
            f"{item_id} is nested under {path.parent.name}.",
            err=True,
        )
        raise typer.Exit(1)

    wi = parse_name(path.name)
    if wi.status == target_status:
        typer.echo(f"No change: {item_id} already in {target_status}.")
        return

    is_dir = path.is_dir()
    new_wi = WorkItemName(
        priority=wi.priority,
        item_id=wi.item_id,
        item_type=wi.item_type,
        status=target_status,  # type: ignore[arg-type]
        slug=wi.slug,
    )
    new_name = emit_name(new_wi, as_directory=is_dir)
    target_dir = tasks_dir / target_status
    target_dir.mkdir(parents=True, exist_ok=True)
    new_path = target_dir / new_name

    if new_path.exists():
        typer.echo(f"Error: target path already exists: {new_path}", err=True)
        raise typer.Exit(1)

    # Atomic rename (single syscall on POSIX) moves the file or whole dir tree.
    path.rename(new_path)

    # Update YAML status to match the new in-name token.
    body_file = (
        new_path / special_file_name(item_id) if new_path.is_dir() else new_path
    )
    data, body = read_file(body_file)
    data["status"] = target_status
    write_file(body_file, data, body)

    typer.echo(str(new_path))
