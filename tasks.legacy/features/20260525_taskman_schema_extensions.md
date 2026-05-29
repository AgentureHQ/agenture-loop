---
status: done
slug: taskman_schema_extensions
epic: taskman_python
title: Add depends_on and priority schema fields
---

# Add depends_on and priority schema fields

## Problem statement

Dependency tracking and prioritization both require new YAML frontmatter fields. The current bash awk-based YAML parser cannot read list values like `depends_on: [a, b]`. Once the Python port is in place, the schema can grow safely.

## Objective

Add two new optional frontmatter fields — `depends_on: [slug, slug]` (list) and `priority: P0|P1|P2|P3` — to epics, features, and tasks. Extend `taskman validate` to check graph integrity: no cycles, no references to unknown slugs.

## Scope

**In:** Two new schema fields, validation extension for graph integrity, list-command filter and sort by priority.

**Out:** Dependency-related queries (`ready`, `blocked-by`, `blocks`) — reserved for `taskman_dependency_queries`.

## Acceptance criteria

1. Epic, feature, and task files accept an optional `depends_on:` list of slugs. Missing field means no dependencies.
2. Epic, feature, and task files accept an optional `priority:` field with values `P0`, `P1`, `P2`, `P3`. Default is `P3` when absent.
3. `taskman validate` errors on cyclic `depends_on` chains and prints the cycle.
4. `taskman validate` warns on `depends_on:` references to unknown slugs (matching the existing convention for `epic:` / `feature:` references).
5. `taskman list` accepts a `--priority <level>` filter and a `--sort priority` option.
6. pytest coverage includes acyclic graphs, cyclic graphs, missing-slug references, and priority sort.

## Summary

Not implemented. Superseded on 2026-05-27 by the redefinition of epic `taskman_python`. Under the new model, priority is the `00` placeholder in the filename grammar (no schema work this iteration), and dependencies reference stable item-IDs not slugs. Successor feature: `schema_dependencies` (depends_on only). See `tasks/epics/20260525_taskman_python.md`.
