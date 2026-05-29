---
status: done
slug: taskman_search_and_dedup
epic: taskman_python
title: Search command and duplicate detection at creation
---

# Search command and duplicate detection at creation

## Problem statement

A 40-item backlog has produced duplicate tasks because finding existing tasks requires reading or grepping files manually. Duplicates are created at the moment of writing, not detected after — and once they exist they fragment the work record.

## Objective

Add `taskman search <query>` that returns ranked matches across all task states with titles and paths. Update `/agn:define task` to call `taskman search` on the proposed title before persisting, surface near-matches, and require explicit confirmation before creating a duplicate.

## Scope

**In:** `search` command with JSON output mode, `/agn:define task` skill update for duplicate check at creation.

**Out:** Search UI (covered in `taskman_web_ui`). Fuzzy matching beyond what regex / token matching provide natively.

## Acceptance criteria

1. `taskman search "<query>"` searches across `tasks/backlog/`, `tasks/active/`, `tasks/done/`, `tasks/features/`, and `tasks/epics/`, returning matching files ranked by relevance with title, status, kind, and path.
2. `taskman search --json "<query>"` returns the same results as JSON for agent consumption.
3. `/agn:define task` runs `taskman search` on the proposed task title before invoking `taskman new task`. If results exist, the skill shows them to the user and asks for explicit "create anyway?" confirmation.
4. The dedup check does not block creation — it surfaces information and requires acknowledgement.
5. pytest covers the search ranking, the empty-result case, and the JSON output schema.

## Summary

Not implemented. Superseded on 2026-05-27 by the redefinition of epic `taskman_python`. Skill integration (the `/agn:define task` dedup hook) is now deferred to a follow-on epic `taskman_skill_integration`; only the `search` command itself stays in scope here. Successor feature: `search`. See `tasks/epics/20260525_taskman_python.md`.
