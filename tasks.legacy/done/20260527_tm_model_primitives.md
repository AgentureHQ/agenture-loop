---
status: done
kind: task
feature: workitem_model_and_core
title: Model primitives: name grammar, ID generator, YAML I/O
---

# Model primitives: name grammar, ID generator, YAML I/O

## Problem statement

Every command needs primitives to parse and emit the `[priority].[id].[status].[slug]` name grammar, allocate `YYMMDDnnn` IDs (shared daily counter), round-trip YAML frontmatter via `ruamel.yaml` without losing comments, and reason about on-disk layout (parent path, status folder, file↔directory representation). These primitives have no user-visible CLI surface but are the foundation for every subsequent command task.

## Scope

**In:** Pure-Python module(s) under `taskman/src/taskman/model/`: name parser/emitter (slug charset `[a-z0-9_]+`, dots as field separators, type token `epic|feat|task`); ID allocator (`YYMMDDnnn`, shared per-day counter, gap-allowed, recomputed by scanning the tree for max sequence used today); YAML frontmatter reader/writer via `ruamel.yaml` preserving comments and round-trip formatting; layout helpers (parent path resolution, status folder ↔ in-name status token sync, file↔directory representation toggle, special-file `_<id>.md` resolution); pytest coverage for each primitive.

**Out:** any CLI command (typer); validation logic (`validate` task owns the integrity report); migration logic (separate feature); dependency graph (separate feature).

## Acceptance criteria

1. Name parser decodes `00.feat-260527001.backlog.workitem_model.md` into priority `00`, id `260527001`, type `feat`, status `backlog`, slug `workitem_model`; rejects malformed names with a clear error.
2. Name emitter produces the same string from the structured fields, idempotent with the parser.
3. ID allocator returns `YYMMDDnnn` strings; same-day collisions allocate sequential `nnn`; gaps in the sequence are tolerated; the allocator is deterministic given the tree state.
4. YAML frontmatter round-trips through ruamel.yaml without losing comments or reflowing keys.
5. Layout helpers correctly determine parent directory from a child path and child path from a parent + name; correctly identify whether an item is file-represented or directory-represented.
6. pytest covers each primitive with at least one positive and one negative case.

## Quality gates

- All primitives unit-tested.
- No imports of `typer` from the model module (model is pure).
- pytest exits 0.

## Summary

### Steps completed
1. Implemented `taskman/src/taskman/model/names.py` — `WorkItemName` dataclass + `parse_name` + `emit_name` + `name_is_special_file` + `special_file_name`. Charset validation in `__post_init__` so any constructed `WorkItemName` is well-formed.
2. Implemented `taskman/src/taskman/model/ids.py` — `today_prefix(date)` and `allocate_id(tasks_dir, today=)`. Scans tree for max sequence with today's `YYMMDD` prefix; returns `prefix + (max+1)` zero-padded to 3 digits. Raises `RuntimeError` on day-counter exhaustion.
3. Implemented `taskman/src/taskman/model/yaml_io.py` — `parse_frontmatter`, `emit_frontmatter`, `read_file`, `write_file` on `ruamel.yaml` round-trip mode.
4. Implemented `taskman/src/taskman/model/layout.py` — `STATUS_FOLDERS`, `is_status_folder`, `special_file_path`, `is_directory_item`, `is_top_level_item`, `parent_item_path`, `iter_work_items`, `find_item_by_id`.
5. Wrote 61 new unit tests across `tests/test_model_{names,ids,yaml_io,layout}.py`. Full suite: 65 tests (61 new + 4 smoke from task 1) — all pass in 0.18s.

### Changes made
- New: `taskman/src/taskman/model/{names.py, ids.py, yaml_io.py, layout.py}`.
- New: `taskman/tests/test_model_{names,ids,yaml_io,layout}.py`.
- Untouched: `cli.py`, `commands/`, task 1 scaffolding files.

### Notable decisions
- **`is_directory` moved out of `WorkItemName`** — kept the dataclass as a pure identity record; representation (file vs directory) is a property of the on-disk path. Callers use `emit_name(..., as_directory=...)` and `is_directory_item(path)` explicitly. Cleaner separation than coupling representation to identity.
- **`special_file_name` uses bare ID** (`_260527001.md`), not typed (`_feat-260527001.md`). Survives type conversion without rename — the keystone identity decision.
- **`iter_work_items` is the single tree-walk primitive.** Skips special files, status folders, and unparseable names. Reused by `find_item_by_id` and (in future tasks) by `list`/`validate`.
- **Module functions over methods** for `parse_name`/`emit_name` — Pythonic and easier to mock in tests.
- **`ruamel.yaml` round-trip preserves comments** — explicit test verifies `# comment above status` and inline `# inline comment` survive parse→emit.

### AC verification
- AC 1 ✓ — Parser decodes the canonical example into 5 expected fields; malformed inputs raise `NameParseError` with the offending field cited (11 negative cases covered).
- AC 2 ✓ — `emit_name` ↔ `parse_name` round-trip parametrized over file and directory forms.
- AC 3 ✓ — `allocate_id` returns `YYMMDDnnn`; same-day collisions sequential; gaps tolerated; exhaustion (`260527999` already used) raises.
- AC 4 ✓ — `parse_frontmatter`/`emit_frontmatter` round-trip preserves comments and list-valued fields.
- AC 5 ✓ — Layout helpers verified against a 3-tier nested fixture (top-level leaf, top-level directory item, nested directory item, nested leaf).
- AC 6 ✓ — Every primitive carries at least one positive + one negative test; total 61 new tests.

### Quality gates
- All primitives unit-tested; `pytest tests/` exits 0.
- `taskman.model.*` modules contain no `typer` imports (verified by inspection).

### Links
- Feature: `tasks/features/20260527_workitem_model_and_core.md`
- Epic: `tasks/epics/20260525_taskman_python.md`
- Predecessor: `tasks/done/20260527_tm_scaffolding.md`
