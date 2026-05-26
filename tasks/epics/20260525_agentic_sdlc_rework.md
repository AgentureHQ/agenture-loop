---
status: backlog
slug: agentic_sdlc_rework
title: Agentic SDLC rework — recursive workflow, unified skills, role separation
---

# Agentic SDLC rework — recursive workflow, unified skills, role separation


## Problem statement

The plugin's skill surface conflates phases that should be distinct (`epic-create` bundles Design and Plan). Validation runs in the same context as implementation, so the agent that wrote the code also tests it — inheriting the implicit context that biased its design choices. No protocol exists for handling upstream design gaps discovered mid-implementation; agents either improvise silently or stop without structured handoff. No mechanism keeps product docs current after work closes; architecture and specs drift.

## Objective

A recursive SDLC where every tier (product → epic → feature → task) runs the same six phases: Requirements → Spec → Design → Plan → Implementation → Validation. Skills follow a verb-noun pattern (`/agn:<verb> <level>`). Planner and QA sub-agents enforce role separation. An escalation protocol routes upstream design gaps. A PostClose hook keeps docs current automatically.

## Scope

In scope:
- Verb-noun skill renaming; single skill per verb with level as argument.
- One level-aware Planner sub-agent for Design + Plan at all tiers.
- QA sub-agent for feature/epic/product validation; lightweight `/agn:validate task` skill.
- Escalation protocol in `/agn:implement task` with gap-log capture.
- PostClose hook + `/agn:docs-sync` skill.
- Rule file reorganization (`task-composition.md`, `qa.md`, `doc-maintenance.md`); persistence centralized in `taskman.sh help`.
- Cleanup of `session-load` skill, `stc` agent fossils, `settings.json.disabled`.

Out of scope:
- Feedback-loop infrastructure for autonomous task design. Tracked as separate backlog task; depends on this epic's escalation gap-logs accumulating.
- Behavioral changes to workflow rules beyond what role separation requires.

## Acceptance criteria

- All lifecycle skills follow `/agn:<verb> <level>` (verbs: define, design, plan, implement, validate; levels: product/epic/feature/task as applicable). Tool skills (`code-review`, `code-comment`, `code-commit`) unchanged.
- Planner sub-agent handles Design + Plan at every tier; invoked by `/agn:define <level>` and standalone `/agn:design`/`/agn:plan <level>` skills.
- QA sub-agent handles feature/epic/product validation; sees spec + result only, not implementer reasoning. `/agn:validate task` is light, runs in main session.
- `/agn:implement task` halts on detected design gaps; writes durable gap-log; surfaces routing instructions to user.
- PostClose hook fires on `taskman.sh` close commands; `/agn:docs-sync` proposes upstream doc diffs; user reviews before commit.
- Rule files reorganized; persistence rules in `taskman.sh help`; `taskman.sh validate` passes; README import block updated.
- `session-load` skill directory deleted; `settings.json.disabled` deleted; spec and README scrubbed of `stc` agent references.

## Linked features

1. `unified_skills_and_cleanup`
2. `rules_split_and_new_files`
3. `planner_subagent`
4. `task_escalation_protocol`
5. `qa_subagent_and_validation`
6. `docsync_close_hook`
