---
status: done
kind: task
feature: task_escalation_protocol
title: Gap-log file format and storage location
---

# Gap-log file format and storage location

# Gap-log file format and storage location

## Problem statement

Detected design gaps need durable on-disk capture so they survive context compaction and feed the future feedback-loop work. The format must be machine-readable enough to enumerate later, human-readable enough to act on, and lightweight enough that writing one does not become a friction point.

## Scope

In scope:
- Define gap-file path convention: `tasks/gaps/<YYYYMMDD-HHMMSS>_<task-slug>.md`.
- Define gap-file YAML frontmatter: `detected` (ISO 8601), `task` (slug), `task_path`, `suspected_level` (`task | feature | epic | architecture`), `status` (`open | resolved`).
- Define body sections: `## Description`, `## Detection context`, `## Suspected upstream`, `## Resolution`.
- Document writing convention (Write tool directly; not through taskman.sh — gaps are observability records, not lifecycle units).
- Create `tasks/gaps/` directory placeholder (e.g., `.gitkeep`) so it exists in fresh clones.

Out of scope:
- A `taskman.sh gap` command surface — defer to a future feedback-loop feature.
- Detection logic and routing message (sibling tasks).

## Acceptance criteria

- `tasks/gaps/` directory exists in the repo.
- Format documented in `plugins/agn/skills/implement/SKILL.md` (or a small companion doc) — implementers reading the skill can write a valid gap file without further reference.
- Each gap file is self-contained: includes its own `## Resolution` slot for the upstream skill to fill on close.

## Quality gates

- `ls tasks/gaps/` returns a result (directory exists).
- Format documentation includes a concrete example block.

## Summary

### Steps completed

1. Created `tasks/gaps/` directory with `.gitkeep` so it survives fresh clones.
2. Documented the gap-log file format in `plugins/agn/skills/implement/SKILL.md` under a new top-level "Design gap escalation protocol" section. Path convention (`tasks/gaps/<YYYYMMDD-HHMMSS>_<task-slug>.md`), YAML frontmatter shape (detected, task, task_path, suspected_level, status), and body sections (Description, Detection context, Suspected upstream, Resolution) all defined with a concrete example block.
3. Documented the writing convention: Write tool directly, not through taskman.sh — gaps are observability records, not lifecycle units.
4. Updated `CLAUDE.md` "taskman.sh is the only writer for task state" section with an explicit exception note for `tasks/gaps/`.

### Changes made

Created:
- `tasks/gaps/` directory
- `tasks/gaps/.gitkeep`

Modified:
- `plugins/agn/skills/implement/SKILL.md` (new "Design gap escalation protocol" section)
- `CLAUDE.md` (carve-out for gap files in the taskman-sole-writer rule)
- `plugins/agn/README.md` (added `gaps/` to the project-layout tree)

### Notable decisions

- **No `taskman.sh gap` subcommand.** Gaps are append-only observability records — no folder transitions, no lifecycle preconditions. Adding a CLI surface would invent invariants where none exist. Defer to a future feedback-loop feature if structured access becomes necessary.
- **`status: open | resolved` rather than richer states.** Two values is enough for the resume protocol; more states (in-progress, blocked) would require more semantics for no current benefit.
- **Filename uses timestamp + slug, not a counter.** Timestamps avoid collisions across worktrees/sessions without needing global state. Slug makes findability easy by `task`.

### Links

- Format spec: `plugins/agn/skills/implement/SKILL.md` (Design gap escalation protocol)
- Storage: `tasks/gaps/`
- Sibling tasks: `design_gap_detection_logic`, `escalation_routing_message`
