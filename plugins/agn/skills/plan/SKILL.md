---
name: plan
description: Focused revision of an existing unit's decomposition — epic or feature. Invoke with /agn:plan <level>. All levels delegate to the Planner sub-agent once the planner_subagent feature ships.
argument-hint: epic | feature
---

# Plan (`/agn:plan <level>`)

## Arguments

| Position | Variable | Value |
|----------|----------|-------|
| `$0` | level | `epic` or `feature` |

## Argument validation

If `$0` is missing, stop and ask:
> *"What level — epic or feature?"*

If `$0` is not one of `epic`, `feature`, stop and list the valid set.

## Dispatch

Read `$0`. Run exactly one of the branches below.

---

## $0 = epic

**Placeholder pending the `planner_subagent` feature of epic `agentic_sdlc_rework`.**

Standalone epic re-decomposition is not yet implemented. Today, epic decomposition into features is bundled inside `/agn:define epic`.

Until the Planner sub-agent ships:
- For a new epic: run `/agn:define epic` — the decomposition step lives there.
- For an existing epic that needs a feature-list revision: edit the epic file's `## Linked features` directly, then create new features via `/agn:define feature --epic <slug>` or discard obsolete ones with `taskman.sh discard`.

After `planner_subagent` ships, this branch will delegate to a level-aware Planner sub-agent that performs focused decomposition revision on an existing epic.

Stop. Do not proceed.

---

## $0 = feature

**Placeholder pending the `planner_subagent` feature of epic `agentic_sdlc_rework`.**

Standalone feature re-decomposition is not yet implemented. Today, feature decomposition into tasks is bundled inside `/agn:define feature`.

Until the Planner sub-agent ships:
- For a new feature: run `/agn:define feature` — the decomposition step lives there.
- For an existing feature that needs a task-list revision: edit the feature file's `## Tasks` directly, then create new tasks via `/agn:define task` with `--feature <slug>` or discard obsolete drafts with `taskman.sh discard`.

After `planner_subagent` ships, this branch will delegate to a level-aware Planner sub-agent that performs focused decomposition revision on an existing feature.

Stop. Do not proceed.
