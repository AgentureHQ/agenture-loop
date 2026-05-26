---
status: backlog
slug: taskman_python
title: Taskman Python port and multi-project tool
---

# Taskman Python port and multi-project tool

## Problem statement

The bash `taskman.sh` enforces task management invariants reliably but is hitting three limits at once:

1. **Cross-project demand exists today.** Used across numio, agenture-loop, infra, and static-site projects. No clean install or share model — updates require manual copy or re-cloning, leading to drift.
2. **PM workflow gaps.** No dependency tracking between features. No view of in-flight work across worktrees. A 40-item backlog where duplicates slip through because search is not ergonomic.
3. **Bash is near its ceiling.** Adding `depends_on: [a, b]` (YAML lists) breaks the awk shim. Recursive dependency graph queries are painful. HTML/UI rendering is brittle. No realistic test substrate.

## Objective

Replace `taskman.sh` with a Python application installable via `uv tool install -e ./taskman`, usable in any project that defines a `tasks/` folder. Add dependency tracking, priority, search, multi-worktree visibility, and a local web UI for PM browsing and prioritization. Existing bash callers continue to work via a 3-line shim.

## Scope

**In scope:**

- Top-level `taskman/` directory (sibling of `plugins/`)
- Full port of the current CLI surface (`new`, `move`, `finalize`, `discard`, `list`, `validate`, `show`, `close`) with identical on-disk format and CLI flags
- `pyproject.toml` for `uv tool install` and `pipx install` compatibility
- Bash shim at `plugins/agn/scripts/taskman.sh` for back-compat
- New schema fields: `depends_on:` (list of slugs) and `priority:` (P0–P3), validated and queryable
- New commands: `search`, `ready`, `blocked-by`, `blocks`, `worktree-status`, `ui`
- Local web UI for browse / search / prioritize / dependency graph
- `TASKMAN_TASKS_DIR` envvar preserved for cross-project use
- pytest test suite covering core CLI commands

**Out of scope:**

- Publishing to PyPI (future, separate)
- Homebrew tap (future, separate)
- TUI mode — web UI is the chosen surface for human users
- Linear-style features (assignees, due dates, sprints, comments, capacity, estimates)
- Splitting taskman into its own repo (defer until cross-org demand)
- Multi-user, cloud, or API-server modes

## Acceptance criteria

1. After `uv tool install -e ./taskman`, the `taskman` CLI is in PATH and operates correctly in numio, agenture-loop, infra, and static-sites projects against each project's `tasks/` folder.
2. Every command from the current bash version works identically — same flags, same outputs, same on-disk format.
3. All `/agn:*` skills continue to work unchanged: existing `./scripts/taskman.sh ...` calls succeed via the shim.
4. `depends_on:` and `priority:` fields validate correctly; `ready`, `blocked-by`, `blocks` return correct results on a representative backlog.
5. `taskman ui` opens a local web UI showing: in-flight work aggregated across worktrees, ready and blocked backlog sorted by priority, full-text search, and a feature dependency graph.
6. `taskman search "<query>"` returns matching tasks across backlog, active, and done with titles and paths.
7. `/agn:define task` runs `taskman search` on the proposed title before creating the file and surfaces near-matches to the user.
8. pytest suite passes with meaningful coverage of the core CLI commands.

## Linked features

1. `taskman_python_core` — port the full CLI surface to Python at top-level `taskman/`; `pyproject.toml`; bash shim; pytest harness; parity with existing commands
2. `taskman_schema_extensions` — add `depends_on:` and `priority:` fields; extend `validate` to check graph consistency (no cycles, no unknown slugs)
3. `taskman_search_and_dedup` — `taskman search` command; update `/agn:define task` to check for duplicates before creating a task
4. `taskman_dependency_queries` — `ready`, `blocked-by`, `blocks` commands; JSON output mode for agent consumption
5. `taskman_worktree_status` — `worktree-status` command using `git worktree list --porcelain` to aggregate in-flight tasks across worktrees
6. `taskman_web_ui` — `taskman ui` local web UI: in-flight, ready, blocked, recently-done, Mermaid dependency graph; minimal deps
