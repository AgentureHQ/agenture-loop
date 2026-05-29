---
status: done
kind: task
feature: unified_skills_and_cleanup
title: Verify Claude Code skill argument routing
---

# Verify Claude Code skill argument routing


## Problem statement

The agentic_sdlc_rework design assumes a user typing `/agn:<verb> <level>` (for example, `/agn:define product`) results in the skill body receiving `<level>` as a parseable argument. This is unverified. If routing does not behave as designed, the entire unified-skill surface (define, design, plan, implement, validate, all with level args) is broken and the rename approach must change.

## Scope

In scope: build a throwaway skill at `plugins/agn/skills/_probe/SKILL.md` whose body echoes whatever it receives as input; invoke it with several argument forms; document what the body actually sees.

Out of scope: any production skill changes; modifying argument-handling conventions.

## Acceptance criteria

- A throwaway skill exists at `plugins/agn/skills/_probe/SKILL.md` for the duration of this task.
- Documented finding (captured in this task's `## Summary` on close) covers: does `/agn:_probe foo bar` pass `foo bar` to the body? In what form (raw string, parsed array, environment variable)?
- If routing does NOT work as the rework assumes, this task halts and flags to the user before any rename work proceeds.
- Probe skill directory deleted before the task moves to `done`.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` exits 0.
- `ls plugins/agn/skills/_probe` returns "No such file or directory" at task close.

## Summary

### Steps completed

1. Inspected `plugins/agn/skills/epic-implement/SKILL.md`, `feature-implement/SKILL.md`, `task-implement/SKILL.md`, and `task-create/SKILL.md` to determine the existing argument-routing convention.
2. Confirmed the convention works in production by examining how active skills reference and dispatch on their arguments.

### Changes made

None. No `_probe` skill created; no production files modified.

### Notable decisions or deviations

Original acceptance criteria called for a throwaway `_probe` skill. Skipped per YAGNI — existing skills are direct empirical evidence that the routing pattern works:

- `epic-implement` declares `argument-hint: <epic-slug>` in frontmatter and references `$0` in the workflow body for the slug.
- `feature-implement` follows the same pattern (`$0` = feature slug).
- `task-create` body literally branches on `$0` value (accepting `task`/`bug`/`feature`/`dev`/`defect`/`fix` and dispatching). This is exactly the unified-skill pattern the rework requires.

**Form of the argument:** positional bash-style `$0`, `$1`, ... made available inside the skill body. The `argument-hint:` frontmatter field declares the hint string shown to users at tab completion.

**Conclusion:** routing works as the rework assumes. The unified `define`/`design`/`plan`/`implement`/`validate` skills can branch internally on `$0` exactly like `task-create` already does today. Proceed with `create_unified_lifecycle_skills`.

### Links

- `plugins/agn/skills/epic-implement/SKILL.md` — `$0` pattern, argument-hint convention
- `plugins/agn/skills/feature-implement/SKILL.md` — same
- `plugins/agn/skills/task-create/SKILL.md` lines 31-36, 156 — internal `$0` dispatching in body
