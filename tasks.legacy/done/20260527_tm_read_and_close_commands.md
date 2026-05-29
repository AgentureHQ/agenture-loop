---
status: done
kind: task
feature: workitem_model_and_core
title: list, show, close commands
---

# list, show, close commands

## Problem statement

Users and agents need to inspect the work-item tree (`list`, `show`) and close items when descendants are done (`close`). All three operate on the same nested-tree primitives and form the read/close surface of the CLI.

## Scope

**In:** `taskman list [--status <s>] [--type <t>] [--json]` walks the nested tree and prints items with priority/id/status/type/slug/title; `taskman show <id> [--json]` reads and prints the item's frontmatter+body; `taskman close <id>` flips status to done if every descendant is done and moves the subtree to `done/` if the item is top-level; pytest covering each path.

**Out:** dependency-graph queries (separate feature); search (separate feature); UI rendering (separate feature).

## Acceptance criteria

1. `taskman list` prints items grouped by status, one line per item showing priority/type/id/status/slug/title.
2. `taskman list --json` returns parseable JSON; no log lines on stdout.
3. `taskman list --status active` and `--type epic` filter correctly.
4. `taskman show <id>` prints the item's full body (frontmatter + body); `--json` returns structured fields.
5. `taskman close <id>` rejects when any descendant has status ≠ done, listing the offending descendants; on success, updates name token + frontmatter status to done, and moves the subtree to `done/` if it was top-level.
6. pytest covers list (empty tree, single item, nested tree, status/type filters, JSON), show (existing, missing, JSON), close (success on leaf, success on folder-with-all-done-children, rejection on undone descendants, missing ID).

## Quality gates

- pytest passes.
- `--json` produces parseable JSON on stdout; logs go to stderr.
- `show <id>` is read-only.

## Summary

### Steps completed
1. Implemented `taskman/src/taskman/commands/list_cmd.py` — `list_items` walks the tree, filters by status/type, groups by status for human output, supports `--json`. (Named `list_cmd` to avoid shadowing the `list` builtin.)
2. Implemented `taskman/src/taskman/commands/show.py` — `show` finds by ID, prints body file content; `--json` returns `{frontmatter, body, path}`.
3. Implemented `taskman/src/taskman/commands/close.py` — flips status to done; rejects with descendant list if any descendant not done; top-level moves to `done/`, nested stays in parent.
4. Wired all three into `cli.py`.
5. Wrote 7+4+6 tests in `tests/test_command_{list,show,close}.py`.
6. Full suite: 117 tests pass.

### Notable decisions
- **`list` file named `list_cmd.py`** to avoid shadowing the Python builtin.
- **show JSON converter (`_to_plain`)** recursively unwraps ruamel.yaml CommentedMap/CommentedSeq to plain dict/list — necessary for `json.dumps`. Falls back to `default=str` for any remaining unserializable types (e.g., date scalars if a user adds them).
- **`close` on nested item rewrites name+YAML in place**, doesn't move folders — only top-level items move between `backlog/active/done` folders. Nested item retains its position in the parent's directory; only its own in-name status token changes. The parent's status is unaffected.
- **`close` precondition uses in-name status of descendants** (cheap, no YAML reads). `validate` is the authority that catches name↔YAML drift; close trusts the name.

### AC verification
- AC 1 ✓ — `list` prints grouped output with priority/type/id/status/slug/title; `test_list_groups_by_status` covers.
- AC 2 ✓ — `list --json` returns parseable JSON; verified.
- AC 3 ✓ — `--status` and `--type` filters covered.
- AC 4 ✓ — `show` prints body; `--json` returns structured fields.
- AC 5 ✓ — `close` rejects with descendant list; success moves subtree to `done/` for top-level, rewrites name in place for nested.
- AC 6 ✓ — pytest covers empty tree, single item, nested tree, status/type filters, JSON for list; existing/missing/JSON for show; leaf/folder-success/undone-rejection/missing/nested-stays-in-parent/already-done for close.

### Quality gates
- pytest: 117/117 pass.
- `--json` writes only JSON on stdout (typer.echo to stdout); error messages use `err=True` → stderr (verified by inspection of command code).
- `show` is read-only — no writes.

### Links
- Feature: `tasks/features/20260527_workitem_model_and_core.md`
- Predecessor: `tasks/done/20260527_tm_convert_command.md`
