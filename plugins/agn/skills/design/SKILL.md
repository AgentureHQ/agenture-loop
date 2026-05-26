---
name: design
description: Focused revision of an existing unit's design at any tier — product, epic, or feature. Invoke with /agn:design <level>. Product produces docs/architecture.md; epic and feature delegate to the Planner sub-agent once the planner_subagent feature ships.
argument-hint: product | epic | feature
---

# Design (`/agn:design <level>`)

## Arguments

| Position | Variable | Value |
|----------|----------|-------|
| `$0` | level | `product`, `epic`, or `feature` |

## Argument validation

If `$0` is missing, stop and ask:
> *"What level — product, epic, or feature?"*

If `$0` is not one of `product`, `epic`, `feature`, stop and list the valid set.

## Dispatch

Read `$0`. Run exactly one of the branches below.

---

## $0 = product

### Preconditions
**Required before starting:**
- `docs/vision.md`
- `docs/spec.md`
- `docs/requirements.md`

If any are missing, stop and tell the user: *Cannot run `/agn:design product` — definition documents not found. Run `/agn:define product` first.*

### Output
| Artifact | Path |
|----------|------|
| High-level architecture | `docs/architecture.md` |

**In scope:** technology choices, system architecture, domain dictionary (key terms), workflows and **key** APIs, security mechanisms.

**Out of scope:** detailed API signatures, database schemas, function-level design — those belong in task-level detailed design during implementation.

### Workflow

1. Draft `docs/architecture.md` from the definition documents.

2. **Review cycle** with the user: incorporate feedback.

3. **Self-validation** — produce a report covering: completeness, consistency with specs, over/under-engineering, design-principle issues.

4. **Document consistency** — If architectural decisions change scope (e.g. defer a feature), update `docs/spec.md` and/or `docs/requirements.md` and state why. Chain: vision → spec → requirements → architecture.

5. **Gate** — User explicitly approves before `/agn:define epic` or `/agn:define feature`.

### Product-branch discipline
- Do not invent requirements; align with definition docs or flag conflicts to the user.
- Architecture impact that contradicts prior commitments requires explicit user agreement.

---

## $0 = epic

**Placeholder pending the `planner_subagent` feature of epic `agentic_sdlc_rework`.**

Standalone epic design is not yet implemented. Today, epic-level design is bundled inside `/agn:define epic` (the epic-decomposition dialog also captures design constraints).

Until the Planner sub-agent ships:
- For a new epic: run `/agn:define epic` — design considerations are captured there.
- For an existing epic that needs a design revision: edit the epic file directly under `tasks/epics/`, or open a focused `/agn:define task` for the architectural change.

After `planner_subagent` ships, this branch will delegate to a level-aware Planner sub-agent that performs focused design revision on an existing epic without re-walking the entire decomposition.

Stop. Do not proceed.

---

## $0 = feature

**Placeholder pending the `planner_subagent` feature of epic `agentic_sdlc_rework`.**

Standalone feature design is not yet implemented. Today, feature-level design is bundled inside `/agn:define feature` (the feature-planning dialog captures design constraints).

Until the Planner sub-agent ships:
- For a new feature: run `/agn:define feature` — design considerations are captured there.
- For an existing feature that needs a design revision: edit the feature file directly under `tasks/features/`, or update the linked spec under `docs/<area>/.../-spec.md`.

After `planner_subagent` ships, this branch will delegate to a level-aware Planner sub-agent that performs focused design revision on an existing feature without re-walking the entire planning dialog.

Stop. Do not proceed.
