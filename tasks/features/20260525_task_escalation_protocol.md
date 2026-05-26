---
status: backlog
slug: task_escalation_protocol
epic: agentic_sdlc_rework
title: Escalation protocol for upstream design gaps detected during implementation
---

# Escalation protocol for upstream design gaps detected during implementation


## Problem statement

When `/agn:implement task` finds the task lacks design coverage, today the skill either silently improvises a design or stops and asks the user without a structured handoff. Both options corrupt the Design/Implementation separation. A halt-and-route protocol fixes this: detect the gap, log it, surface routing instructions, resume after upstream is updated.

## Objective

`/agn:implement task` halts on detected design gaps, writes a durable gap-log entry, and tells the user which upstream skill to invoke.

## Acceptance criteria

- `/agn:implement task` detects missing or ambiguous design before writing code.
- On detection, skill halts and writes a gap-log entry to a documented location (format defined in this feature).
- Gap-log entry contains: gap description, suspected upstream level (task/feature/epic/architecture), implementation context at detection.
- Skill surfaces routing instructions to user: `"Run /agn:design <level> to address before continuing."`
- Gap-log entries are durable on-disk; survive context compaction; feed the future feedback-loop work.
- User can resume `/agn:implement task` after upstream skill completes; skill re-reads task body to pick up updated design.

## Scope

In scope: detection logic; gap-log format and storage location; routing message format.

Out of scope: automated routing (user manually re-invokes upstream skill); feedback-loop consumption of gap-logs (separate backlog task).

## Tasks

- `design_gap_detection_logic`
- `gap_log_format_and_storage`
- `escalation_routing_message`
