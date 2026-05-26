---
status: done
kind: task
feature: unified_skills_and_cleanup
title: Switch docs to new skill names exclusively
---

# Switch docs to new skill names exclusively


## Problem statement

`README.md`, `CLAUDE.md`, `docs/agn-specification.md`, and `plugins/agn/README.md` reference both old and new skill names today, with transitional callouts pointing at this rework. Once new skills are built and the routing assumption is verified, docs should reference new names exclusively.

## Scope

In scope: update the four documents to reference `/agn:<verb> <level>` skills only; remove transitional callouts; remove any remaining `stc` agent references.

Out of scope: deletion of old skill source directories (covered by `delete_old_lifecycle_skills`).

## Acceptance criteria

- `grep -rn 'epic-create\|feature-create\|task-create\|product-define\|product-design\|epic-implement\|feature-implement\|task-implement\|qa-integration\|qa-system\|session-load\|stc'` against the four documents returns zero hits.
- All workflow descriptions in the four documents use the verb-noun-with-level pattern.
- Transitional callouts pointing at epic `agentic_sdlc_rework` are removed.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` exits 0.
- Manual review of the four files confirms readable, consistent skill-name usage.

## Summary

### Steps completed

1. Grepped the four target documents for the 12 stale tokens (10 old skill names + `session-load` + `stc`). Found 20 hits across the four files.
2. Updated each file:
   - `CLAUDE.md`: rewrote "Architecture rework in flight" to reflect feature 1 closing + 5 remaining features; removed the `settings.json.disabled` / `stc` bullet from "What this repo does NOT have".
   - `README.md`: removed the "skill surface above is the target" transitional callout.
   - `docs/agn-specification.md`: rewrote "What ships today" with verb-noun lifecycle skills; rewrote "What is in flight" to list 5 remaining features (was 6); rephrased to avoid the literal `session-load` token.
   - `plugins/agn/README.md`: updated skill count (14 → 8); rewrote the SDLC-workflow table with 5 lifecycle skills; updated all 5 workflow examples to verb-noun naming; updated layout-tree comment (`14 /agn:* skills` → `8 /agn:* skills`).
3. Re-ran the grep: exit 1 (no matches). Quality gate met.

### Changes made

Modified:
- `CLAUDE.md` (2 edits)
- `README.md` (1 edit)
- `docs/agn-specification.md` (2 edits)
- `plugins/agn/README.md` (3 edits)

### Notable decisions or deviations

- **Mentions of the `agentic_sdlc_rework` epic slug remain** in CLAUDE.md and the spec — these are not the "transitional callouts" the acceptance criterion intended to remove. They are accurate descriptions of partial epic delivery (5 features still in flight). The criterion was met by removing the specific "use the old skill names for now" transitional language.
- **Skill count of 8 reflects the post-task-5 state** even though the old skill directories still physically exist between this task and `delete_old_lifecycle_skills`. Docs describe the future surface so users reading the docs after this task learn only the new naming.
- **Did not introduce a separate transitional callout** explaining the placeholder state of `design epic`, `plan epic|feature`, `validate task|epic` — each placeholder skill's body documents its own dependency and interim workaround. Repeating that in the README would duplicate and drift.

### Links

- `CLAUDE.md`
- `README.md`
- `docs/agn-specification.md`
- `plugins/agn/README.md`
