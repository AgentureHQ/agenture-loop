---
status: backlog
kind: task
feature: rules_split_and_new_files
title: Split task-management.md into composition rules + persistence in taskman.sh help
---

# Split task-management.md into composition rules + persistence in taskman.sh help


## Problem statement

`rules/task-management.md` mixes composition concerns (frontmatter, body sections, completion-summary template) with persistence concerns (storage layout, lifecycle, `taskman.sh` CLI, validation rules). Every skill that touches tasks today loads all 200 lines even when it only needs one half. This blocks the Planner sub-agent design (sub-agent cannot own the file if composer skills also need parts of it).

## Scope

In scope:
- Move composition content (YAML frontmatter, body section requirements, completion-summary template) to a new file `rules/task-composition.md`.
- Identify persistence content (lifecycle, CLI, validation rules) and stage for the sibling task `migrate_persistence_to_taskman_help`.
- Delete `rules/task-management.md` once content has migrated.

Out of scope:
- Authoring `rules/qa.md` (sibling task `create_qa_rules`).
- Authoring `rules/doc-maintenance.md` (sibling task `create_doc_maintenance_rules`).
- Updating skill references to the new files (covered by sibling features that introduce those skills).

## Acceptance criteria

- `rules/task-composition.md` exists with composition-only content.
- `rules/task-management.md` deleted.
- Persistence content from the original file accounted for — either already moved to `taskman.sh help` by the sibling task, or staged for it.
- Every section of the original lives in exactly one new location; nothing lost; nothing duplicated.
- `./plugins/agn/scripts/taskman.sh validate` exits 0 on existing task tree.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` passes.
- Manual review: open `rules/task-composition.md` and confirm only composition content; confirm no persistence-related sections remain.
