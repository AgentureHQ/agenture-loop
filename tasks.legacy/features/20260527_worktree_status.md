---
status: done
slug: worktree_status
epic: taskman_python
title: Aggregate active subtrees across git worktrees
---

# Aggregate active subtrees across git worktrees

## Problem statement

When the user has multiple active git worktrees (one per in-flight feature), each worktree has its own `tasks/active/` subtree. No single command aggregates "what is in flight across all my worktrees."

## Objective

Add `taskman worktree-status` that walks `git worktree list --porcelain`, reads each worktree's active subtree in the new model, and prints one consolidated view.

## Scope

**In:** `worktree-status` subcommand using `git worktree list --porcelain`; aggregation of active subtrees per worktree; `--json` output mode; per-worktree `TASKMAN_TASKS_DIR` honored.

**Out:** aggregation across non-worktree project boundaries (multi-repo view); editing across worktrees.

## Acceptance criteria

1. `taskman worktree-status` runs from the main repo or any worktree and prints a table with columns: worktree path, branch, active items (title and ID per line).
2. The command honors per-worktree `TASKMAN_TASKS_DIR`; falls back to `<worktree>/tasks/` otherwise.
3. Worktrees without an `active/` tree or with no active items show "(none)".
4. `--json` returns structured data.
5. pytest covers no-additional-worktree, single-additional-worktree, and multi-worktree-with-mixed-active-counts fixtures.

## Summary

Single task `tm_worktree_status_command`: porcelain parser + per-worktree aggregation + `taskman worktree-status` typer command + `--json`. 9 tests; 203 total pass. All 5 ACs verified. Live-checked on this repo.

Self-certification — single-task feature with focused parser unit tests + aggregation tests; QA agent skipped per the trade-off documented in feature 2.

### Links
- Task: `tasks/done/20260527_tm_worktree_status_command.md`
- Successor: `tasks/features/20260527_web_ui.md` (final feature)
