# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Foundational rules to always follow

@.claude/rules/first-principles.md

## Architecture rework in flight

Epic `agentic_sdlc_rework` (see `tasks/epics/`) is partly delivered. Feature `unified_skills_and_cleanup` is closing — the verb-noun skill surface (`/agn:define|design|plan|implement|validate <level>`) is live. Five features remain in flight: `rules_split_and_new_files` (split task-management rules; persistence moves to `taskman.sh help`), `planner_subagent` (level-aware Planner for Design + Plan), `task_escalation_protocol` (halt-and-route for upstream design gaps), `qa_subagent_and_validation` (QA sub-agent for feature/epic/product), and `docsync_close_hook` (PostClose hook + `/agn:docs-sync`). Until those ship, the Planner and QA sub-agents are placeholders inside the unified skills, and doc sync remains manual.

## What this repo is

A Claude Code **plugin marketplace** (`agenture`) that ships one plugin today: `agn` — an agentic SDLC loop. There is no application code, no build, and no test framework. The deliverables are:

- `.claude-plugin/marketplace.json` — marketplace manifest
- `plugins/<name>/` — self-contained plugin directories (skills, rules, scripts, optional agents/commands/hooks/.mcp.json)
- `docs/` — product docs for the marketplace itself
- `tasks/` — this repo's own SDLC tracking, dogfooded through `agn`

## Dogfooding pattern (important)

The repo runs its own plugin via symlinks under `.claude/`:

```
.claude/skills -> ../plugins/agn/skills
.claude/rules  -> ../plugins/agn/rules
```

Consequences:
- `/agn:*` skills are loaded automatically when Claude Code opens this repo — no `/plugin install` needed during local development.
- The rule files referenced as project instructions (`rules/first-principles.md`, `rules/task-management.md`, `rules/writing-guideline.md`) live at `plugins/agn/rules/` and are exposed at `.claude/rules/`. Edit them in `plugins/agn/rules/`; the `.claude/rules` path is a symlink.
- When editing a skill, edit `plugins/agn/skills/<skill>/SKILL.md`, not the symlinked copy.

## taskman.sh is the only writer for task state

All epic / feature / task mutations go through `plugins/agn/scripts/taskman.sh`. Skills compose content in dialog with the user, then hand off to taskman as the save step. Never write files under `tasks/` directly — invariants (folder ↔ `status` YAML field, draft markers, lifecycle preconditions) are enforced by the script.

From the repo root, invoke it as `./plugins/agn/scripts/taskman.sh ...`. When working inside the plugin, `./scripts/taskman.sh` is equivalent. The script resolves `TASKS_DIR` relative to itself, so the active task tree is `plugins/agn/tasks/` *if invoked from inside the plugin* — but this repo's tracked tasks live in the **top-level** `tasks/` folder. Set `TASKMAN_TASKS_DIR=$PWD/tasks` when running from the root if the tasks folder being mutated isn't the one you expect.

Common commands:

```bash
./plugins/agn/scripts/taskman.sh help
./plugins/agn/scripts/taskman.sh validate
./plugins/agn/scripts/taskman.sh list tasks   [--status backlog|active|done] [--kind task|bug]
./plugins/agn/scripts/taskman.sh move <task-path> <backlog|active|done>
./plugins/agn/scripts/taskman.sh feature close <slug>   # fails unless all member tasks are done
./plugins/agn/scripts/taskman.sh epic close    <slug>   # fails unless all member features are done
```

`taskman.sh new ...` writes files with `draft: true` in the YAML header for preview, then `finalize <path>` clears the marker or `discard <path>` deletes the draft (refuses non-drafts).

## Adding a new plugin to the marketplace

1. Create `plugins/<your-plugin>/` containing its own `.claude-plugin/plugin.json`. All referenced paths (skills, agents, commands, hooks, MCP) must be self-contained inside that plugin directory — Claude Code resolves them relative to the plugin root.
2. Add a new entry to the `plugins` array in `.claude-plugin/marketplace.json`.
3. Update the **Available plugins** table in the top-level `README.md`.

To test the marketplace locally before publishing:

```
/plugin marketplace add ./
/plugin install <plugin-name>@agenture
```

## Work-unit hierarchy (when using /agn:* skills)

```
product → epic → feature → task
```

Each tier is optional one level up. A task may have no feature; a feature may have no epic. The hierarchy is open, not enforced — `taskman.sh validate` downgrades legacy / stale references to warnings.

File locations:
- Product docs: `docs/vision.md`, `docs/spec.md`, `docs/requirements.md`, `docs/architecture.md`
- Epics: `tasks/epics/YYYYMMDD_<slug>.md` (flat, no lifecycle subfolders; `status` field tracks state)
- Features: `tasks/features/YYYYMMDD_<slug>.md` (same shape as epics)
- Tasks: `tasks/{backlog,active,done}/YYYYMMDD[_NN]_<slug>.md` (folder is source of truth, `status` YAML must agree)

Slug format: `[a-z][a-z0-9_]*` — lowercase, underscores only, no hyphens or dots.

See `plugins/agn/rules/task-management.md` for the full model (frontmatter shapes, body sections, lifecycle preconditions, mandatory `## Summary` on close).

## Editing skills

A skill lives at `plugins/agn/skills/<name>/SKILL.md`. The frontmatter `name:` field becomes the `/agn:<name>` invocation. The body is the prompt that runs when the skill is invoked. Skills should never write task files directly — they call `taskman.sh` for any persistence.

## What this repo does NOT have

- No package manager, no `package.json`, no `requirements.txt`, no language toolchain.
- No automated tests. Validation is `./plugins/agn/scripts/taskman.sh validate`, which checks frontmatter and folder/status consistency.
- No CI configuration in-tree.
- No `settings.json` at the repo root.
