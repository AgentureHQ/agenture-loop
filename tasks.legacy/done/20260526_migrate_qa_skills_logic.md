---
status: done
kind: task
feature: qa_subagent_and_validation
title: Migrate qa-integration and qa-system logic into the new skills/agent
---

# Migrate qa-integration and qa-system logic into the new skills/agent

# Migrate qa-integration and qa-system logic into the new skills/agent

## Problem statement

The QA workflows that originally lived in `/agn:qa-integration` and `/agn:qa-system` were partially migrated into `/agn:validate feature` and `/agn:validate product` during feature 1. The sibling task `create_validate_feature_epic_product_skills` moves execution into the QA sub-agent. This task is the explicit migration audit: confirm no logic was dropped, document where each original step now lives, update any remaining references.

## Scope

In scope:
- Audit `/agn:validate feature` against the original qa-integration workflow (output shape, scope inference, manual checks, interface-focused testing).
- Audit `/agn:validate product` against the original qa-system workflow (preconditions, output shape, full-suite run, severity categorization, sign-off).
- Confirm each capability is now expressed in either the validate skill branch (parent-session context capture) or the QA sub-agent brief / system prompt (execution).
- Update CLAUDE.md and `docs/agn-specification.md` if they still reference the old skill names (they shouldn't — already cleaned in feature 1 — but verify).

Out of scope:
- Re-implementing dropped logic; this is an audit task.
- Creating the QA sub-agent (sibling task).

## Acceptance criteria

- Every step from the original qa-integration workflow appears somewhere in the new system.
- Every step from the original qa-system workflow appears somewhere in the new system.
- No remaining `/agn:qa-integration` or `/agn:qa-system` references in current docs.
- One-paragraph audit note in the task Summary confirming what moved where.

## Quality gates

- `grep -rn 'qa-integration\|qa-system' .` returns only references in `tasks/done/` summaries (historical record) and possibly in task body Problem statements (also historical).
- Audit summary in this task's `## Summary` lists the mapping per original capability.

## Summary

### Steps completed

1. Ran `grep -rn 'qa-integration\|qa-system'` across the repo. Result: matches only in `tasks/backlog/` task body Problem statements (now moved to `tasks/done/`) describing historical migration context. No live docs reference the obsolete skill names.
2. Audited `/agn:validate feature` against the original qa-integration workflow. All capabilities preserved, redistributed.
3. Audited `/agn:validate product` against the original qa-system workflow. All capabilities preserved, redistributed.

### Audit: qa-integration → new system

| Original capability | New location |
|---------------------|--------------|
| Purpose (validate new + check regression) | `validate/SKILL.md $0=feature` workflow + `agents/qa.md` "Feature" section |
| Preconditions (runnable app, enough impl) | `validate/SKILL.md $0=feature` Preconditions |
| Output: integration test report | `agents/qa.md` — recommended path `docs/integration/<feature-slug>-test-report.md` |
| Workflow: infer scope | Parent (`validate/SKILL.md` step 1, "Resolve scope") |
| Workflow: run integration/e2e tests | Sub-agent (`agents/qa.md` per-level process) |
| Workflow: focus on interfaces and user paths | Sub-agent (`agents/qa.md` per-level process step 4) |
| Workflow: don't claim release readiness | Parent (`validate/SKILL.md $0=feature` Discipline) |

### Audit: qa-system → new system

| Original capability | New location |
|---------------------|--------------|
| Preconditions (docs exist, feature-complete) | `validate/SKILL.md $0=product` Preconditions |
| Purpose (verify whole product, full suite, e2e flows) | `validate/SKILL.md $0=product` workflow + `agents/qa.md` "Product" section |
| Output: system test report with Critical/Major/Minor | `agents/qa.md` output contract + recommended path `docs/system/system-test-report.md` |
| Workflow: re-read specs and requirements | Sub-agent (`agents/qa.md` Product process step 1) |
| Workflow: run full test suite | Sub-agent (`agents/qa.md` Product process step 2) |
| Workflow: walk e2e scenarios by risk | Sub-agent (`agents/qa.md` Product process step 3) |
| Workflow: categorize issues (Critical/Major/Minor) | Sub-agent (`agents/qa.md` Product process step 4) — severity tiers from `rules/qa.md` |
| Workflow: fix autonomously / escalate decisions | Sub-agent (`agents/qa.md` per-level + `rules/qa.md` Scope decisions) |
| Workflow: re-test after fixes | Parent (`validate/SKILL.md $0=product` step 5, "Re-run loop") |
| Workflow: user-approved release gate | Parent (`validate/SKILL.md $0=product` step 6, "Sign-off gate") |

### Changes made

No code changes — this was an audit task. The migration itself happened in feature 1 (`unified_skills_and_cleanup`) and was completed by the sibling task `create_validate_feature_epic_product_skills`.

### Notable decisions

- **No logic dropped.** Every capability of the original two skills has a documented home. The new system distributes responsibilities (parent: capture context + lifecycle offers; sub-agent: execute + categorize + report) but covers the same surface.
- **No further doc cleanup needed.** Live docs were already cleaned in feature 1. The remaining `qa-integration` / `qa-system` references are inside task body Problem statements (historical context) and `tasks/done/` Summaries (historical record) — these correctly cite the original skill names as part of the migration story.

### Links

- Modified files: none (audit task)
- Audited: `plugins/agn/skills/validate/SKILL.md`, `plugins/agn/agents/qa.md`, `plugins/agn/rules/qa.md`
- Sibling tasks: `create_qa_subagent`, `create_validate_task_skill`, `create_validate_feature_epic_product_skills`
