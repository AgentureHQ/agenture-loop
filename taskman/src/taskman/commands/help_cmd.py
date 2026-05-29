"""`help` command — print the taskman persistence model documentation.

This is the in-tool source of truth for the storage layout, name grammar,
ID scheme, lifecycle, and invariants. For per-command syntax, use
``taskman <command> --help``.

Module named ``help_cmd`` (not ``help``) to avoid shadowing the builtin.
"""
from __future__ import annotations

import typer

_HELP_TEXT = """\
TASKMAN — Uniform recursive work-item management

This help documents the persistence model. For per-command syntax, run
`taskman <command> --help`. For the command list, run `taskman --help`.

================================================================================
STORAGE LAYOUT
================================================================================

  tasks/
    backlog/                                — top-level status folders.
    active/                                   Only top-level items live here
    done/                                     directly.
      <root-item>/                          — nested item directory
        _<id>.md                            — special body file (bare ID)
        <child-item>/                       — nested child (directory form)
          _<child-id>.md
          <grandchild>.md
        <leaf-child>.md                     — nested child (file form)

  Top-level items live directly under one of the status folders. Nested items
  sit inside their parent's directory. The top-level folder reflects the
  root's status; each nested item carries its own status in its name.

================================================================================
NAME GRAMMAR
================================================================================

  Directory item:  <priority>.<type>-<id>.<status>.<slug>
  File item:       <priority>.<type>-<id>.<status>.<slug>.md
  Special file:    _<id>.md      (inside a directory item; bare ID, no type)

  Fields:
    priority   2-digit numeric. Currently always "00"; reserved for ranking.
    type       epic | feat | task. Visual label, convertible via `convert`.
    id         9-digit YYMMDDnnn. The bare number is the stable identity.
    status     backlog | active | done.
    slug       [a-z0-9_]+. Lowercase, digits, underscores. No dots, no hyphens.

  The `<type>-<id>` form in the name renders the current type label for
  human scannability; on `convert`, the name is renamed but the underlying
  ID does not change. References between items (e.g. `depends_on:` in
  future features) use the bare ID.

================================================================================
ID GENERATION
================================================================================

  IDs are YYMMDDnnn — today's date (YYMMDD) + a 3-digit per-day sequence
  shared across all types. Gaps are allowed: deleting an item leaves a hole;
  allocation returns the max-used-today + 1. Once 999 is allocated for a
  given day, the day's counter is exhausted.

================================================================================
LIFECYCLE
================================================================================

  new       Create a draft work item (top-level or nested via --parent).
  finalize  Clear `draft: true` after the user reviews.
  move      Reposition a top-level item between backlog/active/done.
  convert   Relabel an item's type. Cannot relabel a directory item to `task`.
  close     Flip status to done. Rejects if any descendant is not yet done.
            Top-level items move their whole subtree to `done/`.
  list      Walk the tree and print items; --json for agent consumption.
  show      Print an item's frontmatter and body.
  validate  Integrity check: name↔frontmatter drift, parent references,
            grammar, task=leaf invariant.

================================================================================
INVARIANTS
================================================================================

  - task = leaf. A `task` item is always a file, never a directory. To add a
    child to a task, first `convert` it to `feat` or `epic`.

  - Free type ladder. Any nesting is allowed: epic > feat > task is one
    shape; epic > task and feat > task and feat > feat are equally valid.
    The epic > feat > task ladder is not enforced.

  - Subtree moves with root. Moving a top-level item moves all its
    descendants; nested children keep their own in-name status tokens.

  - Frontmatter is the source of truth for content (title, body). The
    on-disk name is a generated cache of (priority, type, id, status, slug).
    `validate` reconciles them and errors on drift.

================================================================================
ENVIRONMENT
================================================================================

  TASKMAN_TASKS_DIR    Selects the active tasks tree. Defaults to $PWD/tasks
                       if unset. Set per-worktree for cross-project use.
"""


def help_cmd() -> None:
    """Print the taskman persistence model documentation."""
    typer.echo(_HELP_TEXT)
