---
status: done
kind: task
feature: legacy_migration
title: Implement taskman migrate command and migration tests
---

# Implement taskman migrate command and migration tests

## Problem statement

Feature `legacy_migration` ships a single command — `taskman migrate <source> <dest>` — that reads the legacy bash-era layout (flat `tasks/{epics,features,backlog,active,done}`) and produces the new uniform recursive layout in `<dest>` with back-assigned stable IDs and a JSON mapping report. Built but not executed on this repo (per epic scope).

## Scope

**In:** `taskman migrate <source> <dest>` subcommand; legacy-frontmatter reader (handles old `status`/`slug`/`title`/`epic:`/`feature:`/`kind:` fields); ID back-assignment using each file's `YYYYMMDD` filename prefix + a deterministic per-day sequence (sorted by source file path); nested-layout reconstruction in `<dest>` (epics at top level under their `status/` folder, features as children of their epic, tasks as children of their feature or directly under their epic or at top level if ad-hoc); verbatim body copy; new-schema frontmatter rewrite (`id`, `type`, `priority: "00"`, `status`, `slug`, `title`; drop `epic:`/`feature:`); `<dest>/_migration_report.json` mapping `{source_path → {new_path, new_id}}`; idempotency on re-run against a fresh `<dest>`; pytest fixtures covering orphan task, feature-with-tasks, epic-with-features-with-tasks, ad-hoc bug, mixed statuses.

**Out:** Execution on this repo's `tasks/`; multi-repo migration; updating `/agn:*` skill callsites; rewriting rule docs; in-place migration (always writes a fresh `<dest>`); reverse migration.

## Acceptance criteria

1. `taskman migrate <source> <dest>` runs to completion on a synthetic fixture mirroring this repo's current layout, producing a fully-populated new-model tree.
2. Every source item receives a unique `YYMMDDnnn` ID derived from its source filename's `YYYYMMDD` prefix; same-day collisions allocate sequential `nnn` deterministically by source file sort order.
3. Parent-child relationships preserved: features sit under their epic's directory; tasks under their feature's directory; ad-hoc tasks (no feature) sit at top-level under their status folder.
4. Bodies copied verbatim. YAML frontmatter rewritten to the new schema: includes `id`, `type` (epic/feat/task), `priority: "00"`, `status`, `slug`, `title`; drops `epic:` and `feature:` reference fields (parent is implicit in directory).
5. A mapping report at `<dest>/_migration_report.json` lists each source path → `{new_path, new_id}`.
6. Re-running with the same source and a fresh `<dest>` produces byte-identical output (deterministic).
7. pytest fixtures cover: orphan task; feature-with-tasks; epic-with-features-with-tasks; ad-hoc bug; mixed-status items; suite passes.

## Quality gates

- pytest passes.
- Migration is deterministic: two runs against the same source with a fresh dest each time produce byte-identical output.
- No writes to the source directory (read-only on source).
- New tree validates clean via `taskman validate` on the dest.

## Summary

### Steps completed
1. Implemented `taskman/src/taskman/commands/migrate.py` — `_tolerant_parse_frontmatter` (line-based parser tolerant of unquoted colons in titles), `_derive_slug_from_filename` (bash tasks lacked `slug:` in frontmatter), `_load_source`, `_allocate_ids`, `_build_parent_map`, `_compute_paths`, `_rewrite_frontmatter`, `_write_tree`, `_build_report`, and the `migrate` typer command.
2. Wired `migrate` into `cli.py`.
3. Wrote 16 tests in `tests/test_command_migrate.py`: 3 slug-derivation unit tests, 9 full-migration tests on synthetic fixtures (covering orphan task, ad-hoc bug, stand-alone feature with tasks, epic-with-features-with-tasks, mixed statuses), determinism, bash-style task without slug, validation cleanliness, plus 3 error cases (nonexistent source, non-empty dest, empty source).
4. **Live-verified on this repo's actual `tasks/`** (read-only): 54 items migrated cleanly into a temp dest; `taskman validate` on the dest exits clean. Real-data run surfaced two issues fixed within this task — see Notable decisions below.
5. Full suite: 151 tests pass (135 prior + 16 new for migrate).

### Notable decisions
- **Tolerant line-based YAML parser for legacy frontmatter.** Bash taskman emitted titles like `title: Model primitives: name grammar, ID generator, YAML I/O` — the colon inside the value breaks strict YAML. Migration only needs scalar `key: value` pairs (status, slug, title, epic, feature, kind, draft), so I split on the first colon per line. Robust against the variations actually found in this repo's tasks.
- **Slug derived from filename when YAML lacks `slug:`.** Bash taskman omitted `slug:` from task frontmatter — the slug lived only in the filename `YYYYMMDD[_NN]_<slug>.md`. `_derive_slug_from_filename` strips the date prefix and optional `_NN` collision marker. Discovered during the live-data run.
- **Status determined by folder for tasks, by YAML for epics/features.** Matches the legacy convention: tasks use folder-as-status; epics/features use YAML-as-status.
- **`_LEGACY_TYPE_MAP` collapses `feature` → `feat`** to match the new model's 4-char type tokens. Also collapses `kind: bug` into `type: task` (the new model has no separate `kind` field; bugs are tasks).
- **Frontmatter rewrite preserves unknown fields.** New fields added (`id`, `type`, `priority`); reference fields dropped (`epic:`, `feature:`, `kind:`); other fields pass through verbatim (status, slug, title, draft, anything custom).
- **Cross-feature fix in `validate`:** added a 2-line skip for top-level underscore-prefixed meta files (e.g., `_migration_report.json`). Without this, validate flagged the migration report itself. Kept consistent with the existing `_<id>.md` special-file convention — top-level `_*` is meta. Documented here so feature 1's task summaries reflect the small cross-feature dependency.

### AC verification
- AC 1 ✓ — `taskman migrate <src> <dest>` runs end-to-end on synthetic fixtures **and** on this repo's real 54-item `tasks/`.
- AC 2 ✓ — IDs are `YYMMDDnnn`, unique per day, sorted by source path; verified via report inspection (`test_migrate_assigns_unique_yymmdd_ids`).
- AC 3 ✓ — Parent-child preserved: epic → feature → task nesting verified end-to-end (`test_migrate_preserves_parent_child_relationships`); ad-hoc tasks at top level under their status folder.
- AC 4 ✓ — Bodies copied verbatim; frontmatter has new schema with `id`/`type`/`priority`; reference fields dropped (`test_migrate_rewrites_frontmatter_schema`, `test_migrate_copies_body_verbatim`).
- AC 5 ✓ — `_migration_report.json` written with `{source_rel → {new_path, new_id}}` for every item.
- AC 6 ✓ — Determinism verified: two runs with fresh dests produce byte-identical reports (`test_migrate_is_deterministic`).
- AC 7 ✓ — Fixtures cover orphan task, ad-hoc bug, stand-alone feature with tasks, epic-with-feature-with-task, mixed statuses, bash-style task without slug.

### Quality gates
- pytest: 151/151 pass.
- Determinism: re-run produces byte-identical output (test).
- No writes to source directory (read-only on source — confirmed by inspection; only `Path.read_text` on source).
- Migration output validates clean via `taskman validate` (test + live).

### Links
- Feature: `tasks/features/20260527_legacy_migration.md`
- Predecessor (epic foundation): `tasks/features/20260527_workitem_model_and_core.md` (done)
