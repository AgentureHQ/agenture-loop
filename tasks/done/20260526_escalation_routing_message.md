---
status: done
kind: task
feature: task_escalation_protocol
title: Escalation routing message and resume protocol
---

# Escalation routing message and resume protocol

# Escalation routing message and resume protocol

## Problem statement

When a gap is detected and logged, the user needs a clear, actionable message naming which upstream skill to invoke and which path to address. After the upstream skill closes the gap, the user should be able to re-invoke `/agn:implement task <path>` and have the skill detect the open/resolved state of prior gaps before continuing.

## Scope

In scope:
- Define the routing message format the skill prints on detection:
  - Names the gap file path.
  - Names the upstream skill to invoke (`/agn:design <level>`, `/agn:plan <level>`, or "edit the task body" for task-level gaps).
  - Tells the user to re-invoke `/agn:implement task <task-path>` after upstream closes.
- Define the resume protocol on re-entry:
  - At task start (after activation), scan `tasks/gaps/` for files where `task == <this task slug>` and `status == open`.
  - If any open gaps exist, surface them to the user before proceeding.
  - Offer: re-route (open gaps still need upstream work), or mark resolved (upstream addressed the gap and user confirms task body is now sufficient).

Out of scope:
- Automated re-routing (user manually re-invokes upstream skills).
- Feedback-loop consumption of accumulated gap logs.

## Acceptance criteria

- Routing message format is explicit in `plugins/agn/skills/implement/SKILL.md`, with a concrete example.
- Resume protocol is documented as the first step of `$0 = task` execution (before activation, or as part of activation).
- Marking a gap resolved updates its frontmatter `status: resolved` and appends a `## Resolution` body — done via Edit tool, not taskman.sh.

## Quality gates

- Skill body parses; YAML frontmatter intact.
- Routing message and resume protocol are clearly distinguishable from regular workflow steps.

## Summary

### Steps completed

1. Documented the routing message format in the "Design gap escalation protocol" section of `plugins/agn/skills/implement/SKILL.md` — a fenced block with the literal lines the skill prints, parameterized by gap-log path, suspected upstream level, recommended next step, and task path. Notes the multi-gap case (one file per gap, list all in the message).
2. Documented the resume protocol in the same section: scan `tasks/gaps/` for `task == <this task slug>` and `status == open`; surface to user; offer mark-resolved (Edit each gap file: status → resolved, fill in `## Resolution`) or re-route (reprint routing message and stop).
3. Wired the resume protocol into `$0 = task` execution as new step 0 — runs before activation so reentry happens cleanly without the side effect of moving a task to `active` only to bounce back to `backlog`.

### Changes made

Modified:
- `plugins/agn/skills/implement/SKILL.md` (Routing message subsection, Resume protocol subsection, Execution-step 0)

### Notable decisions

- **Routing message uses a fenced code block, not prose.** Implementers reading the skill see the exact output verbatim. Reduces drift between "what the skill says it prints" and "what the skill actually prints."
- **Resume check is step 0, before activation.** If the check were inside step 1 (Activate), an open-gap task would move backlog → active before being told to wait. Step 0 keeps lifecycle clean.
- **Mark-resolved is a user-confirmed action, not automatic.** The skill cannot reliably detect whether an upstream skill actually addressed a gap. Requiring the user to confirm keeps the trust boundary right.
- **No `--resolve <gap-file>` flag on the skill.** The Edit-the-file flow is self-evident once the user reads the gap file's frontmatter. Adding a flag would be new surface area for negligible savings.

### Links

- Modified file: `plugins/agn/skills/implement/SKILL.md`
- Sibling tasks: `design_gap_detection_logic`, `gap_log_format_and_storage`
