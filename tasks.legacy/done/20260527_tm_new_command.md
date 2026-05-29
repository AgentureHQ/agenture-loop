---
status: done
kind: task
feature: workitem_model_and_core
title: new command with file-to-directory auto-conversion
---

# new command with file-to-directory auto-conversion

## Problem statement

`taskman new` is the primary creation surface. It must place a new work item at the correct nested location with the correct name grammar, allocate a fresh ID, and — when added as a child of an existing leaf-file item — auto-convert the parent from a single file to a directory containing `_<parent-id>.md` plus the new child.

## Scope

**In:** `taskman new` subcommand built on typer with `--title`, `--type` (epic|feat|task; default task), `--parent <id>` flags; slug derived from title (lowercase, `_`-joined, charset `[a-z0-9_]+`); ID allocation; placement under the parent's directory or top-level status folder; `draft: true` frontmatter until finalized via a `finalize` action; file↔directory auto-conversion of the parent when a child is added; `task = leaf` invariant enforced; pytest covering every path.

**Out:** other commands (`move`, `convert`, `list`, `show`, `close`, `validate`); dependency-graph fields; migration.

## Acceptance criteria

1. `taskman new --title "X" --type epic` (no parent) creates a top-level item at `tasks/backlog/00.epic-YYMMDDnnn.backlog.<slug>.md` with `draft: true`.
2. `taskman new --title "Y" --type task --parent <parent-id>` adds a child file under the parent's directory; if the parent was previously a single file, it is auto-converted to a directory containing `_<parent-id>.md` (the original body) plus the new child.
3. `--parent <task-id>` rejects with a clear message naming the `task = leaf` constraint.
4. Slug is derived from title (lowercase, `_`-joined, charset enforced); same-day name collisions add a deterministic suffix.
5. ID is unique within the day; sequence is deterministic given the tree state.
6. pytest covers top-level creation; nested creation under existing folder-parent; nested creation triggering file→dir auto-conversion; task=leaf rejection; slug derivation and collision; charset rejection.

## Quality gates

- pytest passes.
- No raw file I/O outside the model layer.
- `taskman new --help` renders.

## Summary

### Steps completed
1. Implemented `taskman/src/taskman/commands/new.py` with `slugify`, `_ensure_unique_slug`, `_convert_file_to_directory`, `_make_item`, and the typer commands `new` and `finalize`.
2. Wired `new` and `finalize` into `taskman/src/taskman/cli.py` via `app.command("new")(_new)` / `app.command("finalize")(_finalize)`.
3. Added `get_tasks_dir()` helper that reads `TASKMAN_TASKS_DIR` env var with `$PWD/tasks` fallback (matches epic AC).
4. Wrote 17 tests in `tests/test_command_new.py` covering slugify, top-level creation, nested-under-dir parent, nested-trigger file→dir conversion, second-child-no-reconvert, task=leaf rejection, bad type, missing parent, slug uniqueness suffix, ID uniqueness, finalize on file item, finalize on directory item, finalize missing ID.
5. Live-tested via the installed `taskman` binary against a tmp dir — creates items with correct names, finalizes correctly.
6. Full suite: 82 tests pass (65 from prior tasks + 17 new).

### Changes made
- New: `taskman/src/taskman/commands/new.py`.
- Edit: `taskman/src/taskman/cli.py` (imports + 2 registrations).
- New: `taskman/tests/test_command_new.py`.

### Notable decisions
- **`get_tasks_dir()` placed in `commands/new.py`** for now. Will extract to a shared `context.py` (or similar) when more commands need it. YAGNI: don't add a module yet.
- **Slug uniqueness suffix** appends `_2`, `_3`, … per AC 4 ("deterministic suffix"). IDs prevent file-name collisions on their own, but matching slugs within a day reduce searchability — the suffix keeps slugs distinct per day.
- **File→dir auto-conversion is non-atomic.** Order: `mkdir` → write `_<id>.md` → `unlink` original. Interruption mid-sequence leaves discoverable anomalies (both file and directory present), surfaced later by `validate`. Sufficient for v1; revisit if atomicity becomes a requirement.
- **Frontmatter shape:** `id`, `type`, `status`, `priority`, `slug`, `title`, `draft`. Body is just `# {title}\n` — content composition is the caller's job.
- **Cannot pre-create children of a task.** `--parent <task-id>` rejects with a remediation hint ("Convert the parent first with: taskman convert <id> feat") — `convert` lands in task 5.

### AC verification
- AC 1 ✓ — Top-level `taskman new --title X --type epic` creates file under `backlog/` with the correct name grammar and `draft: true`.
- AC 2 ✓ — `--parent <id>` adds a child; if parent was a file, it auto-converts to directory with `_<id>.md` holding the original body. Test `test_new_nested_under_directory_parent` verifies both the directory shape and the special file.
- AC 3 ✓ — `--parent <task-id>` rejects with the leaf-invariant message naming both the constraint and the remediation.
- AC 4 ✓ — Slug derived from title (lowercase, `_`-joined, charset `[a-z0-9_]+`); same-slug-today gets `_2`, `_3`, … suffix.
- AC 5 ✓ — ID is unique per day; sequence test confirms `id2 == id1 + 1` for back-to-back creations.
- AC 6 ✓ — pytest covers top-level; nested under dir; nested triggering file→dir; second child no re-convert; task=leaf rejection; slug derivation + collision; charset rejection (via slugify); bad type; missing parent; finalize on file; finalize on dir; finalize missing.

### Quality gates
- pytest: 82/82 pass.
- All filesystem I/O routes through `model/yaml_io.read_file` and `model/yaml_io.write_file`, with raw `Path.unlink`/`mkdir`/`write_text` only in the file↔dir conversion helper (which is a structural operation, not content).
- `taskman new --help` and `taskman finalize --help` render via typer.

### Links
- Feature: `tasks/features/20260527_workitem_model_and_core.md`
- Predecessor: `tasks/done/20260527_tm_model_primitives.md`
