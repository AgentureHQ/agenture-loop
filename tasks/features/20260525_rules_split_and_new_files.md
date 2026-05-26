---
status: backlog
slug: rules_split_and_new_files
epic: agentic_sdlc_rework
title: Split task-management rules; add QA and doc-maintenance rule files
---

# Split task-management rules; add QA and doc-maintenance rule files


## Problem statement

`rules/task-management.md` mixes composition concerns (frontmatter, body sections, summary template) and persistence concerns (lifecycle, CLI, validation). Persistence rules duplicate what `taskman.sh help` could authoritatively own. The new Planner, QA, and docs-sync roles need dedicated rule files.

## Objective

Rule files reorganized so each loadable rule serves exactly one role. Persistence centralized in `taskman.sh help`.

## Acceptance criteria

- `rules/task-composition.md` exists; contains body shapes, frontmatter, completion-summary template (composition only).
- `rules/qa.md` exists; contains QA mindset, role separation, validation principles.
- `rules/doc-maintenance.md` exists; contains what to check on closure (drift in `docs/architecture.md`, `docs/spec.md`, `docs/requirements.md`).
- Persistence rules removed from rule files; equivalent content lives in `taskman.sh help` output.
- `./plugins/agn/scripts/taskman.sh validate` passes on existing task tree after the split.
- README import block updated to reference the new rule file set.

## Scope

In scope: split `task-management.md`; author the two new rule files; migrate persistence content into `taskman.sh help`.

Out of scope: wiring the new files into specific skills or agents (covered by sibling features).

## Tasks

- `split_task_management_rules` (will be re-filed and linked to this feature)
- `create_qa_rules`
- `create_doc_maintenance_rules`
- `migrate_persistence_to_taskman_help`
