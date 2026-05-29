"""`ui` command — local read-only web UI for browse / search / dependency graph.

Library choice: **stdlib** ``http.server.ThreadingHTTPServer`` + inline
HTML/JS. Justification: zero new runtime dependencies; the UI is read-only,
single-user, single-page, and serves a small amount of data — FastAPI's
features (validation, async, OpenAPI) buy nothing here while adding three
non-trivial deps (fastapi, uvicorn, jinja2). Mermaid is loaded from a CDN
client-side.

Page renders five sections:
  1. Nested tree (hierarchical view of all items)
  2. Ready (items whose deps are all done, or have no deps)
  3. Blocked (items with open deps)
  4. Recently done (last 7 days by file mtime)
  5. Mermaid dependency graph

Two endpoints:
  GET /                — the page
  GET /api/show/<id>   — JSON ``{frontmatter, body}`` for the side panel
"""
from __future__ import annotations

import html
import json
import os
import signal
import tempfile
import time
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import typer

from taskman.commands.new import get_tasks_dir
from taskman.model.layout import iter_work_items
from taskman.model.names import NameParseError, parse_name, special_file_name
from taskman.model.yaml_io import FrontmatterError, read_file


# ---- data preparation ----


@dataclass(frozen=True, slots=True)
class _Item:
    item_id: str
    item_type: str
    status: str
    priority: str
    slug: str
    title: str
    path: str
    depends_on: tuple[str, ...]
    mtime: float


@dataclass(slots=True)
class _Page:
    items: list[_Item] = field(default_factory=list)
    ready: list[_Item] = field(default_factory=list)
    blocked: list[_Item] = field(default_factory=list)
    recent: list[_Item] = field(default_factory=list)
    graph_mermaid: str = ""


def _load_items(tasks_dir: Path) -> list[_Item]:
    items: list[_Item] = []
    for path in iter_work_items(tasks_dir):
        try:
            wi = parse_name(path.name)
        except NameParseError:
            continue
        body_file = (
            path / special_file_name(wi.item_id) if path.is_dir() else path
        )
        if not body_file.exists():
            continue
        try:
            data, _ = read_file(body_file)
        except FrontmatterError:
            continue
        deps_raw = data.get("depends_on") or []
        deps = tuple(str(d) for d in deps_raw) if isinstance(deps_raw, list) else ()
        items.append(
            _Item(
                item_id=wi.item_id,
                item_type=wi.item_type,
                status=wi.status,
                priority=wi.priority,
                slug=wi.slug,
                title=str(data.get("title", "")),
                path=str(path),
                depends_on=deps,
                mtime=body_file.stat().st_mtime,
            )
        )
    return items


def collect_page(tasks_dir: Path) -> _Page:
    items = _load_items(tasks_dir)
    by_id = {i.item_id: i for i in items}
    page = _Page(items=sorted(items, key=lambda i: (i.priority, i.item_id)))

    # Ready / blocked: applies only to non-done items.
    for i in items:
        if i.status == "done":
            continue
        deps_done = all(
            by_id.get(d) is not None and by_id[d].status == "done"
            for d in i.depends_on
        )
        if deps_done:
            page.ready.append(i)
        else:
            page.blocked.append(i)
    page.ready.sort(key=lambda i: (i.priority, i.item_id))
    page.blocked.sort(key=lambda i: (i.priority, i.item_id))

    # Recently done: status=done, mtime within last 7 days.
    cutoff = time.time() - 7 * 24 * 60 * 60
    page.recent = sorted(
        (i for i in items if i.status == "done" and i.mtime >= cutoff),
        key=lambda i: -i.mtime,
    )

    page.graph_mermaid = _build_mermaid(items)
    return page


def _build_mermaid(items: list[_Item]) -> str:
    """Build a Mermaid flowchart string from non-done items' depends_on edges."""
    open_items = [i for i in items if i.status != "done"]
    if not open_items:
        return "flowchart TD\n  empty[no open items]"
    lines = ["flowchart TD"]
    for i in open_items:
        label = f"{i.item_type}-{i.item_id}<br/>{html.escape(i.slug)}"
        lines.append(f'  {i.item_id}["{label}"]')
    for i in open_items:
        for d in i.depends_on:
            lines.append(f"  {d} --> {i.item_id}")
    return "\n".join(lines)


# ---- HTML rendering ----


_CSS = """
body { font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 1rem;
       display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; }
header { grid-column: 1 / -1; padding-bottom: 0.5rem; border-bottom: 1px solid #ccc; }
input#search { width: 100%; padding: 0.4rem; font-size: 1rem; }
main { overflow-y: auto; max-height: 90vh; }
aside { background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-y: auto;
        max-height: 90vh; font-family: monospace; white-space: pre-wrap; font-size: 0.9rem; }
section { margin-bottom: 1.5rem; }
section h2 { margin: 0.5em 0 0.3em 0; font-size: 1.1rem; color: #333; }
.item { display: flex; gap: 0.5rem; padding: 0.2rem 0.4rem; cursor: pointer;
        border-radius: 3px; font-family: monospace; font-size: 0.9rem; }
.item:hover { background: #eef; }
.item .type { color: #888; min-width: 3em; }
.item .id { color: #666; }
.item .slug { color: #060; min-width: 14em; }
.item .status { color: #c40; min-width: 5em; }
.empty { color: #888; font-style: italic; padding-left: 0.5rem; }
pre.mermaid { background: white; padding: 0.5rem; border: 1px solid #eee; }
"""

_JS = """
function setupSearch() {
  const box = document.getElementById('search');
  box.addEventListener('input', () => {
    const q = box.value.toLowerCase();
    document.querySelectorAll('.item').forEach(el => {
      const text = el.dataset.search || el.textContent.toLowerCase();
      el.style.display = text.includes(q) ? '' : 'none';
    });
  });
}
async function setupPreview() {
  document.querySelectorAll('.item').forEach(el => {
    el.addEventListener('click', async () => {
      const id = el.dataset.id;
      const r = await fetch(`/api/show/${id}`);
      const data = await r.json();
      const aside = document.getElementById('preview');
      aside.textContent = JSON.stringify(data.frontmatter, null, 2) + '\\n\\n' + data.body;
    });
  });
}
document.addEventListener('DOMContentLoaded', () => {
  setupSearch();
  setupPreview();
});
"""


def _render_item(i: _Item) -> str:
    search_blob = html.escape(
        f"{i.item_id} {i.item_type} {i.status} {i.slug} {i.title}".lower()
    )
    return (
        f'<div class="item" data-id="{html.escape(i.item_id)}" data-search="{search_blob}">'
        f'<span class="type">{html.escape(i.item_type)}</span>'
        f'<span class="id">{html.escape(i.item_id)}</span>'
        f'<span class="status">{html.escape(i.status)}</span>'
        f'<span class="slug">{html.escape(i.slug)}</span>'
        f'<span class="title">{html.escape(i.title)}</span>'
        f"</div>"
    )


def _render_section(title: str, items: list[_Item], section_id: str) -> str:
    if not items:
        body = '<div class="empty">(none)</div>'
    else:
        body = "\n".join(_render_item(i) for i in items)
    return f'<section id="{section_id}"><h2>{html.escape(title)}</h2>{body}</section>'


def render_page(page: _Page) -> str:
    sections = "\n".join(
        [
            _render_section("Nested tree", page.items, "tree"),
            _render_section("Ready", page.ready, "ready"),
            _render_section("Blocked", page.blocked, "blocked"),
            _render_section("Recently done (7 days)", page.recent, "recent"),
            f'<section id="graph"><h2>Dependency graph</h2><pre class="mermaid">{html.escape(page.graph_mermaid)}</pre></section>',
        ]
    )
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Taskman</title>
<style>{_CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad: true }});</script>
</head>
<body>
<header><input id="search" placeholder="Filter…"></header>
<main>
{sections}
</main>
<aside id="preview">Click an item to preview.</aside>
<script>{_JS}</script>
</body>
</html>"""


# ---- server ----


def _pid_file() -> Path:
    return Path(tempfile.gettempdir()) / "taskman_ui.pid"


def _make_handler(tasks_dir: Path):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A002
            # Silence default access log; uncomment for debugging.
            return

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                self._send_html(render_page(collect_page(tasks_dir)))
            elif self.path.startswith("/api/show/"):
                item_id = self.path[len("/api/show/") :]
                self._send_show(item_id)
            else:
                self.send_error(404)

        def _send_html(self, html_str: str) -> None:
            body = html_str.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_show(self, item_id: str) -> None:
            from taskman.model.layout import find_item_by_id

            path = find_item_by_id(tasks_dir, item_id)
            if path is None:
                self.send_error(404, f"item not found: {item_id}")
                return
            body_file = (
                path / special_file_name(item_id) if path.is_dir() else path
            )
            try:
                data, body = read_file(body_file)
            except Exception as exc:  # noqa: BLE001
                self.send_error(500, str(exc))
                return
            payload = json.dumps(
                {
                    "frontmatter": {k: str(v) for k, v in data.items()},
                    "body": body,
                    "path": str(path),
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return _Handler


def _start_server(host: str, port: int, tasks_dir: Path, open_browser: bool = True) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), _make_handler(tasks_dir))
    _pid_file().write_text(str(os.getpid()), encoding="utf-8")
    if open_browser:
        webbrowser.open(f"http://{host}:{port}/")
    return server


def _stop_server() -> bool:
    """Return True if a server was running and stopped, False otherwise."""
    pf = _pid_file()
    if not pf.exists():
        return False
    try:
        pid = int(pf.read_text())
        os.kill(pid, signal.SIGTERM)
    except (ValueError, ProcessLookupError, PermissionError):
        pass
    pf.unlink(missing_ok=True)
    return True


def ui(
    port: int = typer.Option(8080, "--port", help="Port to bind on localhost."),
    stop: bool = typer.Option(False, "--stop", help="Stop a running UI server."),
) -> None:
    """Start (or stop) a local web UI for browsing the work-item tree."""
    if stop:
        if _stop_server():
            typer.echo("Stopped UI server.")
        else:
            typer.echo("No running UI server.")
        return

    tasks_dir = get_tasks_dir()
    if not tasks_dir.exists():
        typer.echo(f"Error: tasks dir does not exist: {tasks_dir}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Serving taskman UI at http://localhost:{port}/  (Ctrl+C to stop)")
    server = _start_server("localhost", port, tasks_dir)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        typer.echo("\nShutting down.")
    finally:
        server.shutdown()
        server.server_close()
        _pid_file().unlink(missing_ok=True)
