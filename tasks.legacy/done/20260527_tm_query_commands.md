---
status: done
kind: task
feature: dependency_queries
title: ready, dependents, waiting-on query commands
---

# ready, dependents, waiting-on query commands

## Problem statement

With `depends_on:` in the schema and graph validation in place, agents and humans need queries that walk the graph: "what can I start now?" (ready), "what is waiting on this item?" (dependents), and "what is this item waiting on?" (waiting-on). The old `blocks`/`blocked-by` naming was ambiguous and inverted; the new names retire that ambiguity.

## Scope

**In:** Three typer commands — `taskman ready`, `taskman dependents <id>`, `taskman waiting-on <id>` — all with `--json` output mode. Reads the same dependency graph used by `validate`. Handles unknown IDs gracefully (warning to stderr, non-zero exit).

**Out:** Visual dependency graph rendering (covered in `web_ui`); cycle detection in queries (already handled by `validate`; queries must not infinite-loop but don't re-report cycles); bulk dependency editing.

## Acceptance criteria

1. `taskman ready` returns items in non-done status whose every `depends_on` ID points to a done item. Items with empty or absent `depends_on` are included. Sorted: priority ascending, then ID.
2. `taskman dependents <id>` returns non-done items that list `<id>` in their `depends_on`.
3. `taskman waiting-on <id>` returns the non-done items that `<id>` lists in its `depends_on`.
4. Every command accepts `--json` and emits structured records `{id, type, status, priority, slug, title, path}`.
5. `dependents <id>` and `waiting-on <id>` exit non-zero with a stderr warning when `<id>` does not exist.
6. pytest covers: empty graph, single-edge graph, multi-edge graph, transitive closure (deep deps), missing-ID reference, cyclic graph (queries must not infinite-loop).

## Quality gates

- pytest passes.
- Commands are read-only.
- `--json` writes only JSON on stdout; logs go to stderr.
- O(n + e) traversal; no infinite loops on cycles.

## Summary

### Steps completed
1. New `taskman/src/taskman/commands/queries.py` — `_Item` dataclass, single `_load_graph` walker shared by all three commands, `_emit` formatter for table/JSON; typer commands `ready`, `dependents`, `waiting_on` (registered as `waiting-on`).
2. Wired three commands into `cli.py`.
3. 15 tests in `tests/test_command_queries.py`: ready (empty, no-deps, excludes-done, blocked, after-close, unknown-dep-blocks, transitive, cycle-no-loop), dependents (returns/excludes done/missing target), waiting-on (returns open deps/excludes done deps/missing target/unknown ref ignored).
4. Full suite: 184 tests pass (169 prior + 15 new).

### Notable decisions
- **Single shared `_load_graph` pass** for all three commands. Each subcommand walks the tree once via `iter_work_items`, builds the `_Item` dict, then filters. Cheap and clear; readability over micro-optimization.
- **Unknown deps treated as blocking** for `ready`. If an item's `depends_on` lists an ID that doesn't exist, the item is not ready (you're waiting on something that doesn't exist). `validate` catches the unknown ref separately as a warning.
- **`dependents` and `waiting-on` reject missing target** with non-zero exit per AC 5; `ready` is non-targeted and never errors on missing IDs (those become "blocking unknowns" silently — validate's role).
- **Cycle safety:** `ready` and `waiting-on` don't recurse on dep chains; they only check direct deps' statuses. A cycle therefore can't trigger infinite recursion. `dependents` is even safer (linear filter, no traversal).

### AC verification
- AC 1 ✓ `ready` returns non-done items with all deps in done (or no deps); sorted by priority then ID; transitive chain test verifies multi-step.
- AC 2 ✓ `dependents <id>` returns non-done items referencing `<id>`.
- AC 3 ✓ `waiting-on <id>` returns `<id>`'s non-done deps.
- AC 4 ✓ All three accept `--json`; emit `{id, type, status, priority, slug, title, path, depends_on}` per record.
- AC 5 ✓ `dependents`/`waiting-on` exit non-zero with stderr "not found" on missing target.
- AC 6 ✓ Tests cover empty, single-edge, multi-edge, transitive closure, missing-ID, cycle-no-infinite-loop.

### Quality gates
- pytest: 184/184 pass.
- Read-only commands; no writes.
- `--json` writes JSON to stdout; "warning" / "not found" goes to stderr.
- No infinite loops on cycles (verified by `test_ready_no_infinite_loop_on_cycle`).
