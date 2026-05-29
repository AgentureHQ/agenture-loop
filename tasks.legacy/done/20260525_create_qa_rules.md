---
status: done
kind: task
feature: rules_split_and_new_files
title: Author rules/qa.md (QA mindset, role separation, validation principles)
---

# Author rules/qa.md (QA mindset, role separation, validation principles)


## Problem statement

The `qa_subagent_and_validation` feature will build a QA sub-agent that reads a `rules/qa.md` file. The file does not exist yet. Without it, the QA sub-agent has no behavioral guide separating the QA role from implementation.

## Scope

In scope: author `plugins/agn/rules/qa.md`. Content covers QA mindset (validate against spec, not implementation), role separation (fresh context; sees spec + result; no implementer reasoning), and validation principles (severity classification, focus on user paths and interfaces, escalation vs in-scope fix).

Out of scope: wiring `rules/qa.md` into any skill or sub-agent (covered by `qa_subagent_and_validation`).

## Acceptance criteria

- `plugins/agn/rules/qa.md` exists.
- File contains sections covering: QA mindset, role separation from implementation, validation principles (severity, scope, escalation).
- Style matches `rules/writing-guideline.md` — crisp prose, sentences under 30 words, no weasel words.
- File is short — focused on principles, not procedure. Procedure lives in the future QA sub-agent's body.

## Quality gates

- `./plugins/agn/scripts/taskman.sh validate` exits 0.
- Manual review confirms file is concise and role-focused.

## Summary

### Steps completed

1. Authored `plugins/agn/rules/qa.md` covering: QA mindset (validate against spec, not implementation), role separation (fresh context; sees spec + result; no implementer reasoning), what to check (spec coverage, user paths, interfaces, regression risk), severity classification (critical/major/minor), scope decisions (fix vs escalate), and output shape.
2. Held to writing-guideline style — short sentences, active voice, no weasel words.

### Changes made

Created `plugins/agn/rules/qa.md` (~55 lines, principle-focused).

### Notable decisions or deviations

- **Procedure deliberately omitted.** The file states what QA cares about, not how to invoke tests or write reports. Procedure lives in the future QA sub-agent body (`qa_subagent_and_validation`). Keeps the rule reusable across QA contexts.

### Links

- `plugins/agn/rules/qa.md`
