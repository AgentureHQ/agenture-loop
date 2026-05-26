---
status: backlog
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
