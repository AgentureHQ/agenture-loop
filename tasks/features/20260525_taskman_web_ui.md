---
status: backlog
slug: taskman_web_ui
epic: taskman_python
title: Local web UI for browse, search, prioritize
---

# Local web UI for browse, search, prioritize

## Problem statement

The project manager needs a visual way to browse, search, and prioritize across 40+ tasks. CLI lists work for agents but not for human review. A static HTML report ships fastest but lacks interactivity. A local web UI gives interactive views without committing to a daemon or external service.

## Objective

Add `taskman ui` that starts a local web server (default `localhost:8080`) and opens the browser. The page renders five sections: in-flight (aggregated across worktrees), ready (priority-sorted backlog with deps satisfied), blocked (backlog with unmet deps, showing what blocks each), recently completed (last 7 days), and a Mermaid feature dependency graph.

## Scope

**In:** `taskman ui` command, local web server, page templates, Mermaid graph rendering, search filter, side-panel preview of the task body.

**Out:** Editing tasks through the UI (read-only at first). Authentication. Multi-user. Live websocket updates (page refresh is sufficient).

## Acceptance criteria

1. `taskman ui` starts a local web server and opens the default browser to the rendered page.
2. The page renders five sections: in-flight, ready, blocked, recently done, dependency graph.
3. A search box filters items across all sections by title and slug, client-side, with no page reload.
4. Clicking an item opens its full markdown body in a side panel.
5. Each section reflects the current state of files on disk; refreshing the page after a CLI change shows the new state.
6. Closing the browser tab does not kill the server; the user stops it via `taskman ui --stop` or `Ctrl+C` in the terminal.
7. Dependency graph renders via Mermaid in the browser (no server-side image generation).
8. Minimal Python deps — choice between FastAPI + Jinja2 + uvicorn and stdlib `http.server` made and justified in the implementation task.
9. pytest covers data-aggregation functions; UI itself is exercised by a smoke test (start server, fetch page, assert HTTP 200 and presence of key DOM elements).
