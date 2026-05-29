---
status: done
slug: unified_skills_and_cleanup
epic: agentic_sdlc_rework
title: Unify skill naming under verb-noun pattern; retire obsolete artifacts
---

# Unify skill naming under verb-noun pattern; retire obsolete artifacts


## Problem statement

Existing skill names mix patterns (`epic-create`, `task-implement`, `qa-system`) and hide the recursive SDLC structure. The `session-load` skill and `stc` agent references in docs are leftovers from an abandoned design and confuse users about how rules load.

## Objective

Single verb-noun naming surface (`/agn:<verb> <level>`) for lifecycle skills. Obsolete artifacts deleted.

## Acceptance criteria

- Lifecycle skills migrated to verbs: `define`, `design`, `plan`, `implement`, `validate`. Each takes the level (`product|epic|feature|task` as applicable) as the skill argument.
- Tool skills unchanged: `/agn:code-review`, `/agn:code-comment`, `/agn:code-commit`.
- `plugins/agn/skills/session-load/` directory deleted.
- `settings.json.disabled` deleted.
- README, CLAUDE.md, and `docs/agenture-loop--specification.md` updated; no remaining references to old skill names or the `stc` agent.
- Workflow logic preserved within each renamed skill — only naming and argument structure change in this feature.

## Scope

In scope: file renames; content migration into argument-driven skills; deletion of obsolete artifacts; documentation updates.

Out of scope: behavioral changes (Planner sub-agent, QA sub-agent, escalation, hook — covered by sibling features).

## Tasks

To be decomposed during `/agn:implement feature` of this feature.

## Summary

### Steps completed

1. Decomposed the feature into 5 sequential tasks; filed each via `taskman.sh new task --feature unified_skills_and_cleanup` (all 5 in `done/`).
2. **`verify_skill_arg_routing`** — confirmed the `/agn:<verb> <level>` routing works as designed. Skipped the throwaway `_probe` skill in favor of code inspection of existing skills (`epic-implement`, `feature-implement`, `task-create` all use the `$0` positional-argument pattern in production).
3. **`create_unified_lifecycle_skills`** — composed 5 new SKILL.md files (`define`, `design`, `plan`, `implement`, `validate`), each branching internally on `$0`. Workflows for fully-supported levels migrated from old skills; unsupported levels left as actionable placeholders pointing at the relevant sibling feature.
4. **`delete_obsolete_artifacts`** — removed `plugins/agn/skills/session-load/` and `settings.json.disabled`.
5. **`switch_docs_to_new_skill_names`** — updated `README.md`, `CLAUDE.md`, `docs/agn-specification.md`, `plugins/agn/README.md` to reference verb-noun skills exclusively; removed transitional callouts and the `stc`/`session-load` mentions. Final grep confirms zero hits on the stale-token list.
6. **`delete_old_lifecycle_skills`** — removed the 10 old skill directories. `plugins/agn/skills/` now contains exactly 8 directories (5 new lifecycle + 3 tool). Claude Code's skill manifest confirms only the new surface is visible.

### Changes made

- Created `plugins/agn/skills/{define,design,plan,implement,validate}/SKILL.md` (5 files).
- Deleted 11 directories: 10 old lifecycle skills + `session-load`.
- Deleted `settings.json.disabled`.
- Modified 4 documentation files (README.md, CLAUDE.md, docs/agn-specification.md, plugins/agn/README.md).

### Notable decisions or deviations

- **Skill structure: one body per verb, internal branching on `$0`.** Picked over per-level files for simplicity (mirrors what `task-create` already did with `task`/`bug` dispatch). Accepted cost: each invocation loads the full body even when only one level is used.
- **Placeholders provide actionable interim guidance** rather than failing or doing nothing. Each placeholder names the sibling feature it depends on and the interim workflow available today (typically: use the bundled `define <level>` instead).
- **`validate task` is documented as a placeholder pending the QA-sub-agent feature**, per the parent feature's acceptance criteria, even though the eventual task-level path will run lightweight gates in the main session and not actually use the sub-agent. `qa_subagent_and_validation` will fill the body.
- **Docs reflect post-task-5 state from task 4 onwards** — i.e., during the brief window between task 4 closing and task 5 closing, docs claimed 8 skills while the dir still held 18. Resolved by the time the feature closed.

### Gap surfaced for sibling feature

`taskman.sh` has no command for transitioning epics/features from `backlog` to `active` — only `feature close` and `epic close`. Per the rule "Skills must not write task files directly", the `status` field cannot be hand-edited either. This gap should be addressed by `rules_split_and_new_files` (which is moving persistence rules into `taskman.sh help`).

### Links

- Tasks: `tasks/done/20260525_verify_skill_arg_routing.md`, `tasks/done/20260525_create_unified_lifecycle_skills.md`, `tasks/done/20260525_delete_obsolete_artifacts.md`, `tasks/done/20260525_switch_docs_to_new_skill_names.md`, `tasks/done/20260525_delete_old_lifecycle_skills.md`
- New skills: `plugins/agn/skills/{define,design,plan,implement,validate}/SKILL.md`
- Parent epic: `tasks/epics/20260525_agentic_sdlc_rework.md`
