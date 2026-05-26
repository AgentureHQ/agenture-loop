---
status: done
kind: task
feature: unified_skills_and_cleanup
title: Create unified lifecycle skills side-by-side
---

# Create unified lifecycle skills side-by-side


## Problem statement

Lifecycle workflow today lives in 10 separate skills (`product-define`, `product-design`, `epic-create`, `feature-create`, `task-create`, `epic-implement`, `feature-implement`, `task-implement`, `qa-integration`, `qa-system`). The rework target is 5 verb-named skills (`define`, `design`, `plan`, `implement`, `validate`) — each branching on a `<level>` argument internally. Side-by-side creation avoids breaking the in-session toolchain during the rename.

## Scope

In scope: create 5 new skill directories with `SKILL.md` files. Each body reads the level argument and dispatches to the level-appropriate workflow. Content migrated from current skills; workflow behavior preserved.

Out of scope: behavioral changes (Planner sub-agent, QA sub-agent, escalation protocol, PostClose hook — all covered by sibling features). Deletion of old skills (covered by `delete_old_lifecycle_skills`). Doc updates (covered by `switch_docs_to_new_skill_names`).

## Acceptance criteria

- 5 new skill directories exist: `plugins/agn/skills/{define,design,plan,implement,validate}/`.
- Each `SKILL.md` body branches on the level argument and dispatches.
- `define <level>` handles `product|epic|feature|task` — content from `product-define`, `epic-create`, `feature-create`, `task-create`.
- `design <level>` handles `product` — content from `product-design`. Other levels are explicit placeholders documenting Planner-sub-agent dependency.
- `plan <level>` is an explicit placeholder documenting Planner-sub-agent dependency for all levels.
- `implement <level>` handles `epic|feature|task` — content from `epic-implement`, `feature-implement`, `task-implement`.
- `validate <level>` handles `feature|product` — content from `qa-integration` (feature) and `qa-system` (product). `epic|task` are explicit placeholders documenting QA-sub-agent dependency.
- Old skill directories untouched.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` exits 0.
- All 5 new skills load when Claude Code reads the plugin (`/agn:` tab completion shows them after `/reload-plugins`).

## Summary

### Steps completed

1. Read all 10 existing lifecycle skill bodies (`product-define`, `product-design`, `epic-create`, `feature-create`, `task-create`, `epic-implement`, `feature-implement`, `task-implement`, `qa-integration`, `qa-system`).
2. Composed 5 new unified skill files: `define`, `design`, `plan`, `implement`, `validate`. Each branches on `$0` and embeds the level-specific workflow.
3. Updated all cross-skill references in new bodies to use the new naming (e.g., `/agn:design product` instead of `/agn:product-design`).
4. Confirmed all 5 new skills loaded into Claude Code's skill list (visible via the system-reminder skill manifest).
5. Ran `taskman.sh validate` — passed.

### Changes made

Created:
- `plugins/agn/skills/define/SKILL.md` — covers `product|epic|feature|task` (full migrated workflows for all four).
- `plugins/agn/skills/design/SKILL.md` — covers `product` (migrated). Epic and feature are explicit placeholders pending `planner_subagent`.
- `plugins/agn/skills/plan/SKILL.md` — placeholders for epic and feature pending `planner_subagent`.
- `plugins/agn/skills/implement/SKILL.md` — covers `task|feature|epic` (full migrated workflows for all three).
- `plugins/agn/skills/validate/SKILL.md` — covers `feature` (qa-integration migrated) and `product` (qa-system migrated). Task and epic are explicit placeholders pending `qa_subagent_and_validation`.

No deletions in this task. Old skills untouched.

### Notable decisions or deviations

- **Skill-name references within new skill bodies use the NEW naming** even though task 4 (`switch_docs_to_new_skill_names`) is scoped to documentation files. Rationale: skill bodies steer user behavior at invocation time; mixing old/new names inside a new skill would mislead users. The four-document scope of task 4 remains correct — skill-body references are an implementation detail of task 2.
- **Placeholder bodies provide actionable interim guidance** rather than just "TODO". Users invoking `/agn:design epic` today are told to use `/agn:define epic` (which still bundles design) and what will change after `planner_subagent` ships. This avoids dead-end user experiences during the rework window.
- **`validate task` documented as a placeholder pending QA-sub-agent feature** per the parent feature's acceptance criteria, even though the task-level path won't actually use the sub-agent (per the epic, task validation is "lightweight, main session"). Decision: respect the acceptance criteria as written; `qa_subagent_and_validation` will fill the body.

### Links

- `plugins/agn/skills/define/SKILL.md`
- `plugins/agn/skills/design/SKILL.md`
- `plugins/agn/skills/plan/SKILL.md`
- `plugins/agn/skills/implement/SKILL.md`
- `plugins/agn/skills/validate/SKILL.md`
