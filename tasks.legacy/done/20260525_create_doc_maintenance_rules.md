---
status: done
kind: task
feature: rules_split_and_new_files
title: Author rules/doc-maintenance.md (what to check on work-unit closure)
---

# Author rules/doc-maintenance.md (what to check on work-unit closure)


## Problem statement

The `docsync_close_hook` feature will build a `/agn:docs-sync` skill that follows `rules/doc-maintenance.md`. The file does not exist yet. Without it, the docs-sync skill has no behavioral guide for what to check or how to propose updates.

## Scope

In scope: author `plugins/agn/rules/doc-maintenance.md`. Content covers what to check after closing a work unit (`docs/vision.md`, `docs/spec.md`, `docs/requirements.md`, `docs/architecture.md`), the dependency-chain order (vision → spec → requirements → architecture), the threshold for proposing a diff (behavior or intent in docs is wrong or incomplete), and the user-review gate (no auto-commit).

Out of scope: wiring `rules/doc-maintenance.md` into a skill or hook (covered by `docsync_close_hook`).

## Acceptance criteria

- `plugins/agn/rules/doc-maintenance.md` exists.
- File contains: what to check (which docs), dependency order, propose-don't-commit rule, user-review gate.
- Style matches `rules/writing-guideline.md`.
- File is short — focused on principles, not procedure.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` exits 0.
- Manual review confirms file is concise and principle-focused.

## Summary

### Steps completed

1. Authored `plugins/agn/rules/doc-maintenance.md` covering: what to check (the four product docs + linked spec), dependency-chain order (vision → spec → requirements → architecture), when to propose an update (drift threshold), what NOT to propose updates for, how to propose (show diff, wait for approval, no auto-commit), and the explicit no-op note when nothing needs change.

### Changes made

Created `plugins/agn/rules/doc-maintenance.md` (~35 lines, principle-focused).

### Notable decisions or deviations

- **Explicit "no-op note" guidance.** Without it, doc-sync runs may default to silence on common no-change cases. A deliberate "no doc updates needed" note keeps the audit trail honest and signals to the user that the check ran.
- **Implementation-details exclusion stated explicitly.** Without it, doc-sync may propose to add file paths or function names to product docs — that drifts code review concerns into product specs.

### Links

- `plugins/agn/rules/doc-maintenance.md`
