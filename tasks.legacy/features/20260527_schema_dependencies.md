---
status: done
slug: schema_dependencies
epic: taskman_python
title: depends_on field and graph integrity validation
---

# depends_on field and graph integrity validation

## Problem statement

`taskman ready`, `dependents`, and `waiting-on` queries require a graph defined by an explicit dependency field. The new schema must support `depends_on: [id, id]` referencing stable IDs and `validate` must enforce graph integrity (no cycles, no unknown IDs).

## Objective

Add the `depends_on:` frontmatter field to every work item and extend `taskman validate` to traverse the dependency graph, rejecting cycles and emitting warnings for references to unknown IDs.

## Scope

**In:** optional `depends_on:` field (list of stable item-IDs) in work-item frontmatter; ID-based references only (never slug or status); `validate` extension for graph integrity (DFS cycle detection, unknown-ID warnings, structured `--json` output mode).

**Out:** `ready`/`dependents`/`waiting-on` commands (covered in `dependency_queries`); bulk dependency editing; UI rendering; priority field (the filename `00` placeholder is sufficient for now).

## Acceptance criteria

1. Work-item frontmatter accepts an optional `depends_on:` list of stable item-IDs. Missing field means no dependencies.
2. `taskman validate` errors on a cyclic `depends_on` chain and prints the cycle.
3. `taskman validate` warns on `depends_on:` references to unknown IDs.
4. `validate --json` includes graph-integrity findings in structured form.
5. pytest covers acyclic graphs, single-cycle, multi-cycle, transitive cycle, unknown-ID reference, and empty-deps cases.

## Summary

### Steps completed
Single task delivered: `tm_depends_on_validation` — added `taskman/src/taskman/model/graph.py` (pure-Python `find_cycles` + `unknown_references`) and extended `commands/validate.py` to build a graph during the tree walk and run both checks post-walk. 18 new tests; 169 total pass. See `tasks/done/20260527_tm_depends_on_validation.md` for detail.

### Changes made
- New: `taskman/src/taskman/model/graph.py`.
- Edit: `taskman/src/taskman/commands/validate.py` (import; in-loop graph collection; post-walk graph checks; docstring lists 3 new finding codes).
- New: `taskman/tests/test_model_graph.py` (10 unit tests) and `taskman/tests/test_validate_graph.py` (8 integration tests).

### Notable decisions
- **Graph algorithms in `model/`** (pure, no IO) so the upcoming `dependency_queries` feature reuses them without depending on validate.
- **Cycles → error, unknown refs + malformed depends_on → warning.** A cycle definitively breaks any topological reasoning; an unknown ref is recoverable (perhaps not yet created).
- **No new CLI commands** — feature scope is schema + validation only.

### AC verification
- AC 1 ✓ `depends_on:` (list of stable IDs) read from frontmatter; missing = empty.
- AC 2 ✓ Cycles → `dependency_cycle` error printing the cycle.
- AC 3 ✓ Unknown refs → `unknown_dependency` warning naming the missing ID.
- AC 4 ✓ JSON output carries graph findings in standard shape.
- AC 5 ✓ pytest covers acyclic, self-loop, simple cycle, transitive cycle, multi-edge, unknown ref, malformed, independent cycles.

### Self-certification
This is a single-task feature with pure-Python algorithms (10 unit tests) + integration through the CLI (8 tests). No cross-component surface; QA agent invocation skipped per the trade-off documented in feature 2's summary.

### Links
- Task: `tasks/done/20260527_tm_depends_on_validation.md`
- Reusable module: `taskman/src/taskman/model/graph.py`
- Successor feature: `tasks/features/20260527_dependency_queries.md`
