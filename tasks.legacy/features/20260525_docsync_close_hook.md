---
status: done
slug: docsync_close_hook
epic: agentic_sdlc_rework
title: Auto-fired doc maintenance on work-unit closure
---

# Auto-fired doc maintenance on work-unit closure


## Problem statement

CLAUDE.md states product docs evolve as work progresses, but no mechanism enforces this. After closing a feature or epic, agents move on; `docs/architecture.md`, `docs/spec.md`, and `docs/requirements.md` drift silently. Closure should trigger automatic review.

## Objective

PostClose hook fires on every `taskman.sh` close command. Hook invokes `/agn:docs-sync`. Agent reviews upstream docs, proposes diffs, user reviews before commit.

## Acceptance criteria

- Hook configured to fire on success of: `taskman.sh move <path> done`, `taskman.sh feature close <slug>`, `taskman.sh epic close <slug>`.
- `/agn:docs-sync` skill exists; reads closed unit's body and linked spec; reviews upstream `docs/` files for drift; proposes diffs.
- User reviews diffs in active session before commit.
- No-active-session fallback handled: if hook fires when no Claude session is active (e.g., direct CLI close), hook queues a note that surfaces at next session start.
- `/agn:docs-sync` follows `rules/doc-maintenance.md` for what to check.

## Scope

In scope: hook configuration; docs-sync skill; no-active-session fallback handling.

Out of scope: authoring `rules/doc-maintenance.md` (covered by `rules_split_and_new_files`).

## Tasks

- `design_postclose_hook`
- `create_docs_sync_skill`
- `handle_no_active_session_fallback`

## Summary

### Steps completed

1. Added PostClose hook directly to `plugins/agn/scripts/taskman.sh` rather than configuring a Claude Code plugin-level hook. New `emit_docs_sync_hint(kind, id)` helper appends to `tasks/docs-sync-queue.txt` and prints an INFO message; new `check_docs_sync_queue()` helper prints a WARN hint when the queue is non-empty.
2. Wired the emit helper into three close points: `cmd_move` (when `target_state == done`), `cmd_feature_close`, `cmd_epic_close`. Wired the check helper into `cmd_list` (covers all three list subcommands via the dispatch wrapper).
3. Extended `taskman.sh help` with a new "DOC-SYNC QUEUE (PostClose hook)" section documenting file path, line format, processing instructions, and the observability-record framing.
4. Created `plugins/agn/skills/docs-sync/SKILL.md` (~95 lines). Workflow: read queue → per-entry walk the dependency chain (vision → spec → requirements → architecture → linked spec) per `rules/doc-maintenance.md` → propose diffs or explicit no-op → apply approved diffs via Edit tool → clear entry from queue.
5. Added "PostClose hook and docs-sync" section to `plugins/agn/README.md`, including an opt-in SessionStart hook snippet for users who want automatic queue surfacing.
6. Updated CLAUDE.md: replaced "Architecture rework in flight" with "Architecture rework complete" listing all six shipped features; added `tasks/docs-sync-queue.txt` exception to the "taskman.sh is the only writer" carve-out (aligned with the existing `tasks/gaps/` pattern).
7. Updated `docs/agn-specification.md`: added `/agn:docs-sync` to Tool skills bullet, added PostClose hook bullet, converted "What is in flight" section to "Rework complete" listing all six features.
8. **End-to-end tested**: moving 3 tasks to done accumulated 3 entries in the queue; `taskman.sh list features` correctly surfaced the WARN hint. Claude Code auto-discovered the new docs-sync skill (appeared in available-skills list without plugin reinstall).

### Changes made

Created:
- `plugins/agn/skills/docs-sync/` (directory)
- `plugins/agn/skills/docs-sync/SKILL.md`
- `tasks/docs-sync-queue.txt` (auto-created on first hook fire)

Modified:
- `plugins/agn/scripts/taskman.sh` (DOCS_SYNC_QUEUE variable + 2 helpers + 4 call sites + 1 help section)
- `plugins/agn/README.md` (new code-and-maintenance skill row + new PostClose hook section with SessionStart snippet + plugin layout `gaps/` and `docs-sync-queue.txt` lines + plugin tree updates)
- `CLAUDE.md` (in-flight section → "rework complete" + queue file carve-out)
- `docs/agn-specification.md` (Tool skills bullet + PostClose hook bullet + in-flight section → "Rework complete")

Task files:
- 3 tasks created, finalized, executed, closed under `tasks/done/20260526_*.md`.

### Notable decisions or deviations

- **taskman.sh IS the hook — no Claude Code plugin-hook plumbing.** The simplest viable design. Adding a separate `hooks.json` or `.claude/hooks/` configuration would couple this feature to Claude Code's hook mechanism for no user-visible benefit. taskman.sh's INFO line surfaces via Bash tool output (Claude sees it); direct CLI users see it on stderr. Identical effect, fewer moving parts.
- **Hint on `cmd_list` only.** Lists are the natural "look at state" entry point; printing the hint on every command would be noise.
- **Queue is append-only, line-oriented.** `<ISO-8601 timestamp> <kind> <id-or-path>`. No JSON, no per-entry files. Simple to write, simple to read, line-stable.
- **Don't delete the queue file when fully processed.** Truncate to empty instead — taskman expects the file to exist for the next hook fire. `check_docs_sync_queue` correctly treats empty as no-op.
- **Opt-in SessionStart hook, not auto-installed.** The plugin documents the snippet but doesn't write to the user's settings.json. The user owns settings configuration.
- **/agn:docs-sync supports optional `$1` filter** (line number, slug, or path) for selective processing. Default processes all entries — covers the common case while leaving an escape hatch for partial triage.
- **Explicit no-op is mandatory** per `rules/doc-maintenance.md`. Encoded directly into the skill workflow so the skill never "moves on" without a verdict.

### Risk surfaced

The queue file lives under `tasks/` (alongside lifecycle folders) but is intentionally outside `taskman.sh validate`'s scope. If a future taskman extension naively widens the validation to "everything in `tasks/`", it would error on the queue file. Documented as an observability-record exception in both `taskman.sh help` and `CLAUDE.md`; the validate function explicitly only walks `epics/`, `features/`, and lifecycle task folders, not the directory root.

### Links

- Skill: `plugins/agn/skills/docs-sync/SKILL.md`
- Queue: `tasks/docs-sync-queue.txt` (auto-managed)
- Hook helper: `plugins/agn/scripts/taskman.sh` (`emit_docs_sync_hint`, `check_docs_sync_queue`)
- Rules: `plugins/agn/rules/doc-maintenance.md`
- Tasks (all in `tasks/done/20260526_*.md`): `design_postclose_hook`, `create_docs_sync_skill`, `handle_no_active_session_fallback`
- Parent epic: `tasks/epics/20260525_agentic_sdlc_rework.md`
