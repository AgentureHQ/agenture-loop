---
status: done
slug: workitem_model_and_core
epic: taskman_python
title: Uniform work-item model and core CLI
---

# Uniform work-item model and core CLI

## Problem statement

The bash taskman and old model do not support recursive nesting, name-encoded status, stable IDs, or graph queries. Nothing else in this epic can ship until the model and core CLI exist in Python.

## Objective

Deliver a Python package implementing the uniform recursive work-item model with the core CLI commands needed to create, list, show, move, convert, and close work items, and to validate model integrity.

## Scope

**In:** Python package at top-level `taskman/`; `pyproject.toml` for `uv tool install`; YAML I/O via `ruamel.yaml`; CLI via `typer`; commands `new`, `move`, `convert`, `list`, `show`, `close`, `validate`, `help`; ID generator (`YYMMDDnnn` shared daily counter, three digits, gaps allowed); name grammar parser for `[priority].<type>-<id>.[status].[slug]` (where `<type>` is `epic|feat|task` and `<id>` is the bare 9-digit `YYMMDDnnn`); file→directory auto-conversion on child add; `task = leaf` invariant; frontmatter↔name reconciliation in `validate`; pytest harness with shape fixtures.

**Out:** bash shim, skill callsite changes, doc-rule rewrites, migration of existing items, dependency-related commands or fields, search, worktree aggregation, web UI.

## Acceptance criteria

1. `uv tool install -e ./taskman` installs the `taskman` binary to PATH.
2. `taskman --help` and every subcommand's `--help` render via `typer`.
3. `taskman new` creates a work item at the correct nested location with the correct name grammar — dots as field separators in `[priority].<type>-<id>.[status].[slug]` where `<type>` is `epic|feat|task` and `<id>` is the bare 9-digit `YYMMDDnnn`; slug charset `[a-z0-9_]+`, no hyphens or dots inside the slug; `draft: true` frontmatter until finalized.
4. `taskman move <id> <backlog|active|done>` repositions a top-level work item between status folders and updates the in-name status token atomically.
5. `taskman convert <id> <epic|feat|task>` relabels type; rejects `→ task` when the item has children; accepts other transitions including `task → feat/epic`.
6. Adding a child to a leaf-file item auto-converts the file to a directory containing `_<id>.md` plus the new child.
7. `taskman validate` errors on name↔frontmatter drift (type, status, slug, priority, id mismatch), unknown parents implied by path, and broken name grammar.
8. `taskman list` walks the nested tree and prints items with type, status, ID, and slug; supports `--json`.
9. `taskman show <id>` prints the work item's body.
10. `taskman close <id>` enforces all descendants in done before flipping status to done.
11. pytest covers every command path with at least one positive and one negative case; suite passes.

## Summary

### Steps completed
Seven tasks delivered in sequence: `tm_scaffolding`, `tm_model_primitives`, `tm_new_command`, `tm_move_command`, `tm_convert_command`, `tm_read_and_close_commands`, `tm_validate_command`. Each task's own `## Summary` documents its specific scope; see linked tasks below.

### Changes made
- New package: `taskman/` at repo root with `pyproject.toml` (hatchling, typer, ruamel.yaml, pytest dev extra), `src/taskman/` (cli, model, commands), `tests/`, `README.md`, `.gitignore`.
- 10 typer subcommands: `version`, `new`, `finalize`, `move`, `convert`, `list`, `show`, `close`, `validate`, `help`.
- 4 model modules: `names.py` (grammar, parse/emit), `ids.py` (allocator), `yaml_io.py` (ruamel round-trip with comment preservation), `layout.py` (status folders, parents, tree walk, ID lookup).
- 135 pytest tests across 10 files; full suite runs in 0.31 s.
- `plugins/agn/scripts/taskman.sh` untouched per epic scope.

### Notable decisions (cross-task)
- **Bare ID is the stable identity; type label appears in the rendered name for scannability.** This came out of QA review: the spec wording said grammar was `[priority].[id].[status].[slug]` but the agreed model (per the earlier keystone) is the rendered form `[priority].<type>-<id>.[status].[slug]` with the bare ID being the stable key. Implementation matches the agreed model; spec wording amended to remove the ambiguity (this feature's AC3, AC7 and parent epic's AC2 + scope updated). Special files use bare ID (`_<id>.md`) so they survive type relabel without rename.
- **`get_tasks_dir()` reads `TASKMAN_TASKS_DIR` env var with `$PWD/tasks` fallback** — matches the bash version's cross-project envvar.
- **Pure-Python model layer, typer-only CLI layer.** Commands import from `model/`; no command directly does filesystem operations beyond what `model/yaml_io` and `model/layout` expose. Exception: file→dir auto-conversion in `commands/new.py` (structural op).
- **Move/convert/close use single `Path.rename`** — atomic on POSIX. YAML status/type update is a separate atomic write; failure between produces drift detectable by `validate`.
- **`task = leaf` strictly enforced** by `new`, `convert`, and `validate`.
- **`help` subcommand is the in-tool persistence-model reference** (per epic AC4): documents storage layout, name grammar, ID scheme, lifecycle, invariants, env var.

### QA findings + resolution
QA (agn:qa sub-agent, fresh-context review) returned "not ready" with two Major issues:

1. **Name grammar wording in spec diverged from implementation.** Resolved by amending the spec wording (this feature's AC3 and AC7, parent epic's AC2 and scope) — not the implementation, which correctly reflects the agreed keystone (bare ID + type label rendered in name).
2. **`taskman help` subcommand missing.** Resolved by adding `commands/help_cmd.py` + tests; CLI now exposes `help` and prints the full persistence model documentation.

Two Minor items accepted without code change:
- "Bidirectional auto-conversion" wording — amended scope to `file→directory auto-conversion on child add` (no remove command exists; the bidirectional claim was aspirational).
- "Convert error message off when directory is empty" — cosmetic; the message accurately rejects an impossible state via the current command set.

### AC verification (post-amendment)
All 11 ACs verified against running code:
- AC 1 ✓ `uv tool install -e ./taskman` → `taskman` on PATH.
- AC 2 ✓ `taskman --help` plus per-subcommand `--help` render via typer.
- AC 3 ✓ `new` produces correctly-shaped names (amended grammar), 9-digit IDs, slug charset, `draft: true`.
- AC 4 ✓ `move` repositions top-level item atomically; in-name status token + YAML status updated.
- AC 5 ✓ `convert` relabels type; rejects → task with children.
- AC 6 ✓ File→directory auto-conversion verified end-to-end.
- AC 7 ✓ `validate` detects all six drift codes (type/status/slug/priority/id mismatch, broken grammar).
- AC 8 ✓ `list` walks nested tree, `--json` parseable.
- AC 9 ✓ `show` prints body; `--json` returns structured fields.
- AC 10 ✓ `close` enforces descendant-done; subtree moves to `done/` for top-level.
- AC 11 ✓ 135 tests passing, every command covered with positive and negative cases.

### Links
- Tasks: `tasks/done/20260527_tm_{scaffolding,model_primitives,new_command,move_command,convert_command,read_and_close_commands,validate_command}.md`
- Epic: `tasks/epics/20260525_taskman_python.md`
- Successor (next feature): `tasks/features/20260527_legacy_migration.md`
