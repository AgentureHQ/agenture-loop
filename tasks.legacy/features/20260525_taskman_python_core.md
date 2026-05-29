---
status: done
slug: taskman_python_core
epic: taskman_python
title: Port taskman CLI surface to Python
---

# Port taskman CLI surface to Python

## Problem statement

The current bash `taskman.sh` (962 LOC) cannot grow further without losing maintainability — YAML parsing via awk only handles flat scalars, dependency-graph queries would triple the code, and testing 1500+ lines of bash is unrealistic. A Python rewrite at feature parity is the foundation that unblocks every subsequent feature in this epic.

## Objective

Port the current bash CLI surface to a Python application at top-level `taskman/`. Preserve every command, flag, exit code, and on-disk file format. Provide `pyproject.toml` for `uv tool install`. Replace `plugins/agn/scripts/taskman.sh` with a 3-line shim that execs the Python entry point. Establish a pytest harness.

## Scope

**In:** Python package layout, `pyproject.toml`, bash shim, pytest harness, feature parity with current bash CLI.

**Out:** New CLI commands, new schema fields, web UI, search — reserved for follow-up features in this epic.

## Acceptance criteria

1. `uv tool install -e ./taskman` succeeds; `taskman` is available in PATH globally.
2. Every command of the current bash version produces identical output and side effects on identical inputs: `new epic`, `new feature`, `new task`, `finalize`, `discard`, `move`, `list epics`, `list features`, `list tasks`, `epic show`, `epic close`, `feature show`, `feature close`, `validate`, `help`.
3. The bash shim at `plugins/agn/scripts/taskman.sh` execs `taskman "$@"`. Existing skills calling `./scripts/taskman.sh ...` continue to work without modification.
4. `TASKMAN_TASKS_DIR` environment variable continues to control which `tasks/` folder the CLI operates against.
5. pytest suite exists at `taskman/tests/` and exercises every command path with at least one positive and one negative case.
6. The Python package is structured for future extension: `src/taskman/cli.py`, `src/taskman/yaml_io.py`, `src/taskman/commands/`, `taskman/tests/`.

## Summary

Not implemented. Superseded on 2026-05-27 by the redefinition of epic `taskman_python`, which replaced the original 6-feature decomposition with 7 features oriented around the new uniform recursive work-item model. The "port at parity" framing was dropped — the model itself changes end-to-end. Successor feature: `workitem_model_and_core`. See `tasks/epics/20260525_taskman_python.md` for the current decomposition.
