---
status: backlog
slug: qa_subagent_and_validation
epic: agentic_sdlc_rework
title: QA sub-agent for system/integration; /agn:validate skills at every level
---

# QA sub-agent for system/integration; /agn:validate skills at every level


## Problem statement

Today validation runs in the same context as implementation. The agent that wrote the code also tests it, inheriting implicit context that may have biased its design choices. A QA sub-agent with fresh context, validating against specs only, catches issues the implementer overlooks.

## Objective

QA sub-agent handles feature/epic/product validation. Lightweight `/agn:validate task` skill runs in main session for task-level quality gates. Both wire to `rules/qa.md`.

## Acceptance criteria

- QA sub-agent file exists; loads `rules/qa.md`.
- `/agn:validate task` runs task-level quality gates in main session (lightweight; no sub-agent).
- `/agn:validate feature`, `/agn:validate epic`, `/agn:validate product` invoke the QA sub-agent.
- QA sub-agent receives spec + implementation result only; no implementer-decision context.
- QA produces verdict + report; failures surface specific findings to user.
- Existing `/agn:qa-integration` and `/agn:qa-system` content migrated into the new skills (logic preserved; entry-point changes).

## Scope

In scope: QA sub-agent; four `/agn:validate <level>` skills; migration of qa-integration and qa-system logic.

Out of scope: authoring `rules/qa.md` (covered by `rules_split_and_new_files`).

## Tasks

- `create_qa_subagent`
- `create_validate_task_skill`
- `create_validate_feature_epic_product_skills`
- `migrate_qa_skills_logic`
