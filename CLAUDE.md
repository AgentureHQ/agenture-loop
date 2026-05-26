# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Foundational rules to always follow

@.claude/rules/first-principles.md

## Architecture rework in flight

Epic `agentic_sdlc_rework` (see `tasks/epics/`) is partly delivered. Four features have shipped: `unified_skills_and_cleanup` (the verb-noun skill surface `/agn:define|design|plan|implement|validate <level>` is live), `rules_split_and_new_files` (composition rules in `rules/task-composition.md`; persistence in `taskman.sh help`; new role-specific rule files `rules/qa.md` and `rules/doc-maintenance.md`), `planner_subagent` (Planner sub-agent at `plugins/agn/agents/planner.md`; `/agn:define`, `/agn:design`, and `/agn:plan` delegate composition to it), and `task_escalation_protocol` (`/agn:implement task` detects design gaps, writes a gap-log to `tasks/gaps/`, halts with a routing message, and supports resume). Two features remain in flight: `qa_subagent_and_validation` (QA sub-agent for feature/epic/product) and `docsync_close_hook` (PostClose hook + `/agn:docs-sync`). Until those ship, the QA sub-agent is a placeholder inside `/agn:validate task|epic`, and doc sync remains manual.

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
- The rule files (`rules/first-principles.md`, `rules/task-composition.md`, `rules/writing-guideline.md`, `rules/qa.md`, `rules/doc-maintenance.md`) live at `plugins/agn/rules/` and are exposed at `.claude/rules/`. Edit them in `plugins/agn/rules/`; the `.claude/rules` path is a symlink. Persistence rules (storage, naming, lifecycle) live in `./plugins/agn/scripts/taskman.sh help`, not in any rule file.
- When editing a skill, edit `plugins/agn/skills/<skill>/SKILL.md`, not the symlinked copy.

## taskman.sh is the only writer for task state

All epic / feature / task mutations go through `plugins/agn/scripts/taskman.sh`. Skills compose content in dialog with the user, then hand off to taskman as the save step. Never write epic, feature, or task files under `tasks/{epics,features,backlog,active,done}/` directly — invariants (folder ↔ `status` YAML field, draft markers, lifecycle preconditions) are enforced by the script.

**Exception:** gap-log files under `tasks/gaps/` are written via the Write tool directly. They are observability records produced by `/agn:implement task` when a design gap halts coding; they are not lifecycle units and have no taskman invariants. Format documented in `plugins/agn/skills/implement/SKILL.md` under "Design gap escalation protocol".

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

See `plugins/agn/rules/task-composition.md` for frontmatter shapes, body sections, and the mandatory `## Summary` template. See `./plugins/agn/scripts/taskman.sh help` for storage layout, naming, lifecycle preconditions, and validation behavior.

## Editing skills

A skill lives at `plugins/agn/skills/<name>/SKILL.md`. The frontmatter `name:` field becomes the `/agn:<name>` invocation. The body is the prompt that runs when the skill is invoked. Skills should never write task files directly — they call `taskman.sh` for any persistence.

## Editing agents

Sub-agents live at `plugins/agn/agents/<name>.md`. The frontmatter `name:` field becomes the `subagent_type` used when a skill invokes them via the Agent tool. Today only one agent ships: `planner` (level-aware Design + Plan composer used by `/agn:define`, `/agn:design`, `/agn:plan`). Sub-agents have restricted toolsets — the Planner has no Write/Edit/Bash; it returns text, and the parent skill persists via `taskman.sh`.

## What this repo does NOT have

- No package manager, no `package.json`, no `requirements.txt`, no language toolchain.
- No automated tests. Validation is `./plugins/agn/scripts/taskman.sh validate`, which checks frontmatter and folder/status consistency.
- No CI configuration in-tree.
- No `settings.json` at the repo root.
