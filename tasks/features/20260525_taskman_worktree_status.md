---
status: backlog
slug: taskman_worktree_status
epic: taskman_python
title: Aggregate in-flight tasks across git worktrees
---

# Aggregate in-flight tasks across git worktrees

## Problem statement

When the user has 2–3 active git worktrees (one per in-flight feature), each worktree has its own `tasks/active/` state. There is no single command that aggregates "what is in flight across all my worktrees." Today the user must inspect each working directory separately.

## Objective

Add `taskman worktree-status` that walks `git worktree list --porcelain`, reads each worktree's `tasks/active/` folder, and prints one consolidated view: worktree path, branch, and active tasks.

## Scope

**In:** `worktree-status` command, JSON output, integration with `git worktree list --porcelain`, `TASKMAN_TASKS_DIR` honored per-worktree.

**Out:** Aggregating tasks across non-worktree project boundaries (multi-repo view) — separate concern, separate epic if ever needed.

## Acceptance criteria

1. `taskman worktree-status` runs from the main repo or any worktree and prints a table with columns: worktree path, branch, active tasks (one per line, with title).
2. The command honors `TASKMAN_TASKS_DIR` per worktree; falls back to `<worktree>/tasks/` otherwise.
3. Worktrees without an `active/` directory or with no active tasks show "(none)".
4. `--json` output mode returns structured data for agent consumption.
5. pytest covers: no worktrees beyond main, single additional worktree, multiple worktrees with mixed active-task counts.
