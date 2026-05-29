---
status: done
kind: task
feature: qa_subagent_and_validation
title: Create QA sub-agent
---

# Create QA sub-agent

# Create QA sub-agent

## Problem statement

Validation today runs in the same context as implementation — the agent that wrote the code also tests it, inheriting the implicit context that biased its design choices. A fresh-context QA sub-agent validates against specs only, catching issues the implementer overlooked because the design space had already collapsed in their head.

## Scope

In scope:
- Create `plugins/agn/agents/qa.md` with YAML frontmatter, tools, system prompt.
- System prompt loads `plugins/agn/rules/qa.md` (mindset, role separation, what to check, severity, scope decisions, output shape).
- Inputs: level (feature | epic | product), spec paths, implementation result paths, optional regression scope.
- Tools: full set including Bash (test runs), Write/Edit (reports and in-scope glue-code fixes).
- Output contract: verdict (ready | not ready), per-requirement pass/fail, per-severity issues list.

Out of scope:
- Wiring the skills to invoke the agent (sibling tasks).
- The qa.md rules themselves (already shipped in `rules_split_and_new_files`).

## Acceptance criteria

- File `plugins/agn/agents/qa.md` exists with valid YAML frontmatter.
- System prompt explicitly cites `rules/qa.md` and tells the agent to read it first.
- Inputs and outputs documented in the system prompt.
- Fix-vs-escalate boundary explicit.

## Quality gates

- File parses; YAML frontmatter intact.
- `taskman.sh validate` still passes.

## Summary

### Steps completed

1. Wrote `plugins/agn/agents/qa.md` (~110 lines). YAML frontmatter, full tool set (Read/Glob/Grep/LS/NotebookRead/Bash/Write/Edit/WebFetch/WebSearch), system prompt covering: identity (fresh context), "read rules/qa.md first" instruction, brief contract (level, scope, spec_paths, implementation_paths, regression_scope), per-level expectations (feature/epic/product), output contract (Verdict / Per-requirement results / Issues / What I fixed / What I escalated / Report / Next steps), hard constraints.
2. Validated taskman tree still passes.

### Changes made

Created:
- `plugins/agn/agents/qa.md`

### Notable decisions

- **Full tool set including Edit/Bash.** Sub-agent isolation is via fresh context, not tool restriction. QA needs Bash to run tests and Edit to apply in-scope glue-code fixes (per `rules/qa.md` Scope decisions). The role boundary lives in the prompt.
- **System prompt loads `rules/qa.md` rather than duplicating it.** Mindset, severity, fix-vs-escalate, output shape — all live in the rule file. The agent prompt cites it and tells the agent to read first. Keeps a single source of truth.
- **One invocation per scope.** Same pattern as Planner: if the brief covers two features, return one verdict and ask the parent to invoke again. Keeps each sub-agent context focused.
- **Output contract uses "ready | not ready" verdict + structured sections.** Forces specific findings ("Login fails on empty password — no validation; 500 error") rather than vague conclusions. Sections required even if empty (write "None.") so parsers downstream don't need to handle missing fields.

### Links

- Agent file: `plugins/agn/agents/qa.md`
- Rules loaded: `plugins/agn/rules/qa.md`
