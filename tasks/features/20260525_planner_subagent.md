---
status: backlog
slug: planner_subagent
epic: agentic_sdlc_rework
title: Planner sub-agent for Design + Plan; define and refinement skills delegate
---

# Planner sub-agent for Design + Plan; define and refinement skills delegate


## Problem statement

`/agn:define <level>` skills today bundle Design and Plan in the main session, loading all composition rules into the parent context. A level-aware Planner sub-agent encapsulates Design + Plan, isolates rules from the parent context, and produces design rationale plus work-unit files.

## Objective

One Planner sub-agent serves Design + Plan at every tier. Define skills delegate to it. Standalone `/agn:design <level>` and `/agn:plan <level>` skills exist for revising existing units.

## Acceptance criteria

- Single Planner sub-agent file exists; system prompt covers Design + Plan rules for all applicable tiers.
- `/agn:define <level>` invokes the Planner. User dialog flows through the parent session.
- Planner outputs persist via `taskman.sh` (script remains the only file writer).
- `/agn:design <level>` and `/agn:plan <level>` invoke the same Planner for focused revisions of existing work units.
- Refinement skills do not require creating new units — they operate on existing files.

## Scope

In scope: Planner sub-agent; refactor of define skills to delegate; new standalone design/plan refinement skills.

Out of scope: escalation protocol; task validation; doc sync (sibling features).

## Tasks

- `create_planner_subagent`
- `refactor_define_skills_to_delegate`
- `create_design_skill`
- `create_plan_skill`
