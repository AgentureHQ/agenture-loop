---
name: validate
description: Quality gates at any tier — task, feature, epic, or product. Invoke with /agn:validate <level>. Task runs the task's own gates in the main session. Feature and product use the migrated qa-integration / qa-system workflows. Epic and task placeholders depend on the QA sub-agent.
argument-hint: task | feature | epic | product
---

# Validate (`/agn:validate <level>`)

## Arguments

| Position | Variable | Value |
|----------|----------|-------|
| `$0` | level | `task`, `feature`, `epic`, or `product` |
| `$1` | id | Optional task path (for `task`) or scope hint (for `feature` / `epic`) |

## Argument validation

If `$0` is missing, stop and ask:
> *"What level — task, feature, epic, or product?"*

If `$0` is not one of `task`, `feature`, `epic`, `product`, stop and list the valid set.

## Dispatch

Read `$0`. Run exactly one of the branches below.

---

## $0 = task

**Placeholder pending the `qa_subagent_and_validation` feature of epic `agentic_sdlc_rework`.**

Lightweight task-level validation in the main session is not yet implemented. Today, the task's `## Quality gates` section is executed inline at the end of `/agn:implement task` (step 5: "Complete after user confirms").

Until `qa_subagent_and_validation` ships:
- Read the task file's `## Quality gates` section and run each gate command manually, or rely on the inline gate run inside `/agn:implement task`.

After the feature ships, this branch will run the task's `## Quality gates` end-to-end in the main session, report results, and offer to move the task to `done`. The QA sub-agent is NOT involved at the task level — that role is reserved for feature/epic/product.

Stop.

---

## $0 = feature

### Purpose
Validate that:
1. **New functionality** delivered in the current feature scope behaves end-to-end.
2. **Existing functionality** (prior features or related areas) still works.

### Preconditions
- A runnable app or test environment the project uses (tests, dev server, etc.).
- Enough implementation exists to exercise the scope (otherwise say what is missing).

### Output
Write an **integration test report** (markdown — `docs/` or user-chosen path), including:
- Scope (feature slug, task IDs, or "ad-hoc: ...")
- What was executed (commands, URLs, scenarios)
- Pass/fail per scenario
- Regressions found and severity
- Open issues

### Usage
```
/agn:validate feature
```
Optionally scope in the user message: *"feature worktree_isolated_dev_stacks only"*, *"after defect TASK-xxx"*, etc.

### Workflow

1. Infer scope from context (recent feature, task just completed, or explicit user instruction).

2. Run the project's integration/e2e tests if present; supplement with **manual checks** where needed.

3. Focus on **interfaces between components** and **realistic user paths** for this slice of work.

4. Do not claim release readiness — that is **`/agn:validate product`**.

### Feature-branch discipline
- Fix failures you can within scope; escalate product decisions.
- Keep the report factual and actionable.

---

## $0 = epic

**Placeholder pending the `qa_subagent_and_validation` feature of epic `agentic_sdlc_rework`.**

Standalone epic validation via a fresh-context QA sub-agent is not yet implemented. Today, epic-level integration verification is handled by `/agn:validate feature` scoped to the whole epic (inherited from the old `qa-integration` skill called at the epic boundary inside `/agn:implement epic`).

Until `qa_subagent_and_validation` ships:
- Use `/agn:validate feature` and pass the epic scope as a hint in the user message.
- Or run `/agn:validate feature` iteratively for each member feature to confirm no regressions across the epic.

After the feature ships, this branch will dispatch to a QA sub-agent with fresh context — the sub-agent sees the epic spec and the integrated result but not the implementer's reasoning, removing the bias that the agent who wrote the code also tests it.

Stop.

---

## $0 = product

### Preconditions
- `docs/spec.md` and `docs/requirements.md` (or equivalent product docs) exist.
- Implementation is intended to be **feature-complete** for the release under test.

If docs are missing, say so and ask whether to proceed with a reduced checklist.

### Purpose
- Verify the **whole product** against documented behavior.
- Run the **full automated test suite**; add or extend tests where critical paths lack coverage.
- Exercise **end-to-end user flows** from the spec.
- Produce a **system test report** with **Critical / Major / Minor** findings.

### Output
System test report including:
- Coverage summary (what was exercised)
- Issues with severity
- What was fixed vs escalated
- Sign-off recommendation (ready / not ready)

### Usage
```
/agn:validate product
```

### Workflow

1. Re-read specs and requirements; build a checklist of flows and non-functional expectations.

2. Run full test suite; inspect failures; add tests for critical gaps.

3. Walk end-to-end scenarios in order of risk.

4. Categorize issues; fix autonomously where clear; escalate decisions.

5. Re-test after fixes until **Critical** and **Major** are cleared (per product policy).

6. **Gate** — User approves release readiness.
