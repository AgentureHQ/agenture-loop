# taskman

Uniform recursive work-item management. A CLI for tracking epic/feature/task hierarchies stored as nested directories with name-encoded status, ID, and priority.

This is a work-in-progress rewrite of the bash `taskman.sh` in `plugins/agn/scripts/`. See the parent repo's `tasks/epics/20260525_taskman_python.md` for the design and decomposition.

## Install (end-user)

    uv tool install -e ./taskman

After install, `taskman --help` is on PATH.

## Develop

    cd taskman
    uv sync --extra dev
    uv run pytest

## Layout

    taskman/
      pyproject.toml
      src/taskman/
        cli.py              # typer entry point
        model/              # name grammar, ID allocator, YAML I/O, layout
        commands/           # subcommand implementations
      tests/                # pytest suite

## Status

Scaffolding only. Real commands land in subsequent tasks under feature `workitem_model_and_core`.
