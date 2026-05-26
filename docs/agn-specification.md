# agn: Vision, Specification and Requirements

## Vision


### agn goals:
- Provide a framework and mechanisms for accelerated software development using AI coding tools (Claude Code).
- Establish AI-assisted SDLC where repeatable steps in the lifecycle are automated or assisted using AI agents, accelerating overall delivery.
- Stretch goal: establish a feedback loop for incremental improvements of agn artifacts (skills, rules, agents, hooks, tools/MCPs) — the more users use it, the better it serves their projects (tracked by backlog task `feedback_loop_infrastructure`).

### SDLC model

agn's SDLC is a **recursive decomposition** pattern. Each tier (product → epic → feature → task) runs the same six phases at a different level of abstraction:

```
Requirements → Spec → Design → Plan → Implementation → Validation
                                          ↓
                                  (recurses to next tier)
```

Tier-specific notes:
- **Product:** no direct implementation. Implementation expands to a portfolio of epics over time.
- **Epic:** Design = high-level. Plan produces features or tasks. Validation = integration / system test at epic boundary.
- **Feature:** Design = detailed. Plan produces tasks. Optional tier — skip if 2-3 tasks suffice.
- **Task:** Design is mostly cross-check against upstream. If gaps surface, halt and escalate — gaps signal insufficient upstream design.

Documentation evolves continuously. Each completed unit triggers automatic review of upstream artifacts (architecture, spec, requirements) for drift.

#### New product development

- **Definition (Requirements + Spec)**
    - **Objective**: establish vision document, product specification, and requirements documents that will be used in subsequent stages of SDLC.
    - **Inputs**:
        - Product owner's vision and requirements.
        - Any other available sources of information (e.g., similar product available online, or online documentation).
    - **Outputs**:
        - Vision document (`docs/vision.md`) — one-pager that captures the problem this product solves, key functional capabilities, how it solves the user problem, and answers "So what?".
        - Product specification (`docs/spec.md`) — detailed document describing product functionality, user flows, and user interactions. Focuses on overall UX, functionality, and flows.
        - Requirements (`docs/requirements.md`) — addendum to spec. Goes in depth for specific areas that may not be fully detailed in spec. More formal description that complements the spec.
    - **How it is done**:
        1. The agent composes an initial draft of the vision document collaboratively with the product owner.
        2. The agent drafts the specification using the vision and any other available sources. Product owner reviews and iterates.
        3. The agent drafts requirements that disambiguate the spec. Product owner reviews and iterates. Updates flow back to vision and spec as needed.
        4. Output validation: agent reviews outputs against two rubrics and produces a report. Product owner addresses findings. Cycle repeats until critical issues are cleared or the user moves on.
            - **Business case**: do we understand the business and user problem? Does the spec solve it? Is there a better way? Is the monetization case sound? Are risks addressed?
            - **Functional completeness**: is the functionality consistent across all documents? Any gaps, ambiguities, inconsistencies, or missing details? Sufficient detail for the next stage?

- **Design (High-level architecture)**
    - **Objective**: establish high-level architecture that serves as input for the Plan phase and for detailed design during implementation. Sets high-level technical direction — choice of technologies, software architecture and system design, domain dictionary (key elements only, no detailed schemas), workflows, key APIs, security mechanisms. Detailed APIs, schemas, function names are explicitly out of scope — they emerge during implementation.
    - **Inputs**: vision, specification, requirements.
    - **Outputs**: `docs/architecture.md`.
    - **How it is done**:
        - Agent drafts the architecture document. Product owner reviews and iterates.
        - QA: the agent reviews the architecture for incomplete or inconsistent design, over-engineering, under-engineering, violations of core design principles, ambiguities, missing details, or unaddressed requirements. Findings go into a report; product owner provides answers; agent updates. Cycle repeats until critical issues are cleared.
        - Doc consistency: before moving to Plan, agent checks whether specs or requirements need updating (e.g., a feature deferred due to cost). Updates all affected documents to keep them consistent.
        - Final user review and approval.

- **Plan (Decomposition)**

    - **Objective**: decompose the product into a four-tier hierarchy — **product → epic → feature → task** — that gives implementation agents executable units of work and the user a clear view of scope and sequencing. Epics are functional-block-sized initiatives. Features are coherent slices within an epic (or stand-alone if no epic tier is needed). Tasks are the units of implementation work. Each tier is optional one level up. See `rules/task-composition.md` for the body and frontmatter shape of each tier; see `./scripts/taskman.sh help` for the persistence model (storage, naming, lifecycle).
    - **Inputs**: specs, requirements, architecture.
    - **Outputs**: epic files (`tasks/epics/`), feature files (`tasks/features/`), task files (`tasks/backlog/`). The hierarchy is the plan — there is no separate implementation-plan document.
    - **How it is done**:
        - The agent decomposes the product collaboratively with the user, choosing the appropriate tier for each unit of work. Large functional blocks become epics with linked features. Smaller initiatives become features directly with linked tasks. One-off work becomes ad-hoc tasks.
        - QA validation: the agent reviews each artifact to find issues that could cause problems during implementation — incomplete or ambiguous task definitions, over-engineering, inconsistencies, missing coverage of functionality outlined in the vision and specs. A key cross-check at this stage is that each task provides sufficient non-ambiguous detail for an implementation agent to proceed with detailed design and coding — this is the last gate before handing work to automated agents.
        - Feedback to prior stages: if decomposition surfaces a need to change specs or requirements, the agent updates the relevant definition documents alongside the decomposition artifacts to keep all artifacts consistent.
        - The user reviews and approves the decomposition before implementation begins.

- **Implementation**
    - **Objective**: execute the plan by completing tasks in the order defined by the hierarchy, producing working, tested, and documented code. The user controls execution granularity — single task, a feature, an epic, or the full product. Each task goes through a design cross-check before coding begins to confirm the upstream design covers it. The stage is largely autonomous — agents work independently and escalate to the product owner when upstream design gaps are surfaced.
    - **Inputs**: hierarchy (epics, features, tasks), architecture, specs, requirements.
    - **Outputs**: working codebase, per-task detailed design notes (where appropriate), per-feature integration test results, and updated artifacts reflecting any decisions made during implementation.
    - **How it is done**:
        - The agent processes tasks in the order defined by the plan, respecting feature and epic boundaries.
        - For each task, the agent first cross-checks the upstream design against the task. If the design is complete, it proceeds with code + unit tests. If gaps are detected, it halts (see Escalation protocol below).
        - **Escalation protocol**: when the cross-check reveals a missing or ambiguous design decision, the implement skill halts, writes a durable gap-log entry (description, suspected upstream level, implementation context), and surfaces routing instructions to the user (`"Run /agn:design <level> to address before continuing."`). The user manually re-invokes the upstream skill. After upstream is updated, the user re-invokes `/agn:implement task`, which re-reads the task body to pick up the revised design.
        - The agent writes unit tests and verifies that the implementation passes all relevant tests without breaking existing functionality.
        - Doc consistency: implementation discoveries that require updates to specs, requirements, or architecture trigger updates to those documents to keep all artifacts consistent.
        - **Integration test (per feature)**: when all tasks in a feature are complete, the QA sub-agent runs integration tests against the live application. The integration test validates: (1) all functional requirements delivered by this feature work end-to-end, and (2) functionality from previous features continues to work — no regressions. Issues found are fixed before proceeding. The product owner reviews phase output and approves progression.
        - The stage concludes when all features are complete, all integration tests pass, and the product owner approves the implementation as ready for system testing.

- **Validation (System Test)**
    - **Objective**: full system test once the implementation scope is complete. Integration tests during Implementation validate each feature in isolation; this stage tests the product as a whole — all features work together, all functional and non-functional requirements are met, the product is ready for release.
    - **Inputs**: fully implemented codebase, specs, requirements, integration test results.
    - **Outputs**: system test report; verified, release-ready codebase with all critical issues resolved.
    - **How it is done**:
        - The QA sub-agent reviews the full codebase against specs and requirements, checking that all specified functionality is present, behaves correctly end-to-end, and handles edge cases appropriately.
        - QA runs the full test suite, identifies coverage gaps in critical paths, and adds missing tests.
        - QA validates end-to-end user flows as specified.
        - Findings are categorized by severity (critical, major, minor) in a system test report. Critical and major issues are resolved before release. Issues requiring product owner decisions are escalated.
        - Affected areas are re-tested after fixes. Cycle repeats until critical and major issues are cleared.
        - Product owner reviews the final report and approves the product as ready for release.

#### Bug fixes

Bug fixes apply to an existing product where all definition documents and architecture are present in `docs/`. The workflow is streamlined — Definition and Design (Architecture) are skipped, and the process begins from a defect task.

- **Defect task (input)**
    - **Objective**: capture a well-defined, actionable description of the bug so the agent has everything it needs to investigate and fix it without ambiguity.
    - **How it is done**: the user creates a task of kind `bug` in `tasks/backlog/` containing: observed problem, expected result, actual result, reproduction steps, environment context, logs, screenshots. The task serves as the primary input for all subsequent stages.

- **Plan (fix planning)**
    - **Objective**: understand the root cause and produce a targeted fix plan without touching architecture unless absolutely necessary.
    - **Inputs**: defect task, existing docs, codebase.
    - **Outputs**: root cause analysis note and a fix plan — a concise set of tasks describing exactly what needs to change.
    - **How it is done**:
        - The agent investigates the codebase to identify the root cause, tracing through relevant components, data flows, and logic.
        - The agent produces a root cause analysis and a fix plan added to the defect task or as a linked task set.
        - **Architecture impact check**: if the root cause reveals that fixing the defect requires an architectural change, the agent must stop, document the architectural impact clearly, and enter interactive discussion with the user. No fix work begins until the user explicitly approves the approach.
        - For straightforward bugs with no architectural impact, the agent proceeds to implementation after the fix plan is drafted.

- **Implementation**
    - **Objective**: apply the fix as defined in the fix plan.
    - **How it is done**: same as in new product development. Detailed design first, then code, then unit tests. If the fix reveals that specs, requirements, or architecture need minor updates, the agent updates those documents to keep all artifacts consistent. Scope creep is flagged and not pursued without user instruction.

- **Validation (integration + system test)**
    - **How it is done**: the QA sub-agent runs an integration test against the live application validating (1) the defect is resolved and the expected behavior is now observed, and (2) functionality related to or touched by the fix continues to work. Then QA runs the full system test for regression. Any regressions are fixed and re-tested. QA produces a brief report. Product owner reviews and approves the fix as ready for release.

#### Maintenance

Maintenance covers ongoing work on an existing product that does not introduce new user-facing features. Two scenarios:

**Scenario 1: Ad-hoc maintenance tasks**

The user identifies a specific maintenance need — refactoring a module, migrating a database, upgrading a dependency, improving test coverage — and initiates it through the standard task workflow.

- **How it is done**:
    - The user creates a task in `tasks/backlog/` with a clear problem statement, scope, and acceptance criteria. The task type reflects the nature of the work (`task`, `bug`, `refactor`, `upgrade`, `chore`).
    - The agent picks up the task and executes it following the same Implementation process. Architecture impact check applies — if the task requires architectural changes, the agent flags this and discusses with the user before proceeding.
    - Integration and regression tests run after the task is complete. Same process as in bug fixes.
    - The user approves the task as done once all quality gates pass.

**Scenario 2: Codebase optimization**

Over time, as agents implement individual tasks with narrow focus, the codebase can become fragmented — locally optimized per task but globally degraded in quality, consistency, and structure. Codebase optimization is a periodic process where the agent audits the full codebase and proposes a holistic improvement plan.

- **How it is done**:
    - **Audit (agent-driven)**: `/agn:code-review` produces a report identifying technical debt, fragmentation, inconsistency, duplication, over-complexity, performance issues, or deviations from architecture. This replaces the user-driven Definition stage — the agent surfaces the problems. Findings go to the product owner for review and prioritization.
    - **Design**: if the optimization plan requires structural changes, the agent produces or updates the architecture document to reflect the target state. The product owner reviews and approves before planning begins.
    - **Plan**: the agent translates the approved optimization plan into a set of tasks via `/agn:define epic` or `/agn:define feature`. Same process as in new product development.
    - **Implementation, Integration test, Validation**: same process as new product development.

#### Incremental features to an existing product

Same overall workflow as new product development, with one difference: Definition, Design, and Plan stages operate on existing artifacts rather than starting from scratch.

- **Definition**: agent drafts additions and amendments to the existing vision, spec, and requirements to cover the new feature. Output validation follows the same rubric. After this stage the existing docs fully describe the product including the new feature — no separate "feature docs."
- **Design**: agent reviews the existing architecture and decides whether the new feature can be implemented within it or whether changes are needed. If no changes are needed, lightweight — agent documents the assessment and proceeds.
- **Plan**: same process as new product development. The agent identifies which existing components are touched by the new feature so those areas are explicitly covered in the plan and in testing scope.
- **Implementation, Integration test, Validation**: same as new product development. Scope discipline applies — the agent does not modify functionality outside the approved feature scope without explicit user instruction.


## Current Implementation State

`agn` is packaged as a Claude Code plugin (plugin name: `agn`) in the `agenture` marketplace. Users install it via `/plugin install agn@agenture`.

### What ships today

- **Lifecycle skills** under the verb-noun pattern (`/agn:<verb> <level>`):
  - `/agn:define <product|epic|feature|task>` — define a work unit at the named tier.
  - `/agn:design <product|epic|feature>` — focused revision of an existing unit's design. Product is fully implemented; epic and feature are placeholders pending `planner_subagent`.
  - `/agn:plan <epic|feature>` — focused revision of an existing unit's decomposition. Placeholder pending `planner_subagent`.
  - `/agn:implement <task|feature|epic>` — execute implementation; task = detailed design → code → tests; feature/epic = iterate children.
  - `/agn:validate <task|feature|epic|product>` — quality gates. Feature and product are fully implemented; task and epic are placeholders pending `qa_subagent_and_validation`.
- **Tool skills:** `/agn:code-review`, `/agn:code-comment`, `/agn:code-commit`.
- **Rules** in `rules/first-principles.md` (always-on design discipline), `rules/task-composition.md` (frontmatter and body shapes), `rules/writing-guideline.md` (prose style), `rules/qa.md` (validation principles), `rules/doc-maintenance.md` (closure-time doc checks). Loaded into a user's project by `@`-importing them in the project's `CLAUDE.md`. Persistence rules live in `./scripts/taskman.sh help`.
- **Tooling:** `scripts/taskman.sh` — single writer for create / move / close / list operations on epics, features, and tasks.

### What is in flight

Epic `agentic_sdlc_rework` (see `tasks/epics/`) continues to restructure the plugin to match this specification's recursive SDLC. Two features have shipped:

- `unified_skills_and_cleanup` — verb-noun surface live; abandoned fossils from the prior agent design removed.
- `rules_split_and_new_files` — composition in `rules/task-composition.md`; persistence in `taskman.sh help`; role-specific rule files `rules/qa.md` and `rules/doc-maintenance.md` authored; rule import blocks updated.

Remaining linked features:

1. `planner_subagent` — one level-aware Planner sub-agent for Design + Plan; replaces the design/plan placeholders.
2. `task_escalation_protocol` — halt-and-route protocol in `/agn:implement task` for upstream design gaps.
3. `qa_subagent_and_validation` — QA sub-agent + fills the `/agn:validate task|epic` placeholders.
4. `docsync_close_hook` — PostClose hook + `/agn:docs-sync` skill.

The remainder of this document describes the **target** state once those four features ship.


# Specification and Requirements

## Workflows: User Experience

agn supports four workflows. Each is a sequence of stages driven by skill invocations. At every stage the user invokes a skill, the agent executes it (often via a sub-agent), and the user approves the output before moving forward.

### New Product Development

Starting point: the user has an idea for a new product and no existing documents.

**Definition** — `/agn:define product`

The Planner sub-agent guides the user through producing three documents:

1. *Vision* (`docs/vision.md`): the agent interviews the user about the problem, target users, and key capabilities. It drafts a one-page vision. The user reviews and iterates.
2. *Specification* (`docs/spec.md`): using the approved vision and any additional inputs (reference products, online docs, domain knowledge), the agent drafts a product specification. The user reviews and iterates.
3. *Requirements* (`docs/requirements.md`): the agent drafts requirements that disambiguate and complement the spec with formal detail. The user reviews and iterates.

After all three are drafted, the agent validates them against business-case and functional-completeness rubrics, produces a report, and addresses findings until all critical issues are resolved or the user approves moving forward.

**Design (Architecture)** — `/agn:design product`

The Planner sub-agent drafts `docs/architecture.md` covering technology choices, system architecture, domain dictionary (key terms only), workflows, key APIs, and security mechanisms. Detailed design (API signatures, schemas) is out of scope.

Review cycle: user feedback → agent updates → QA review → consistency check against specs → user approval.

**Plan (Decomposition)** — `/agn:define epic`, `/agn:define feature`, `/agn:define task`

The agent decomposes the product into a four-tier hierarchy. There is no single implementation plan document — the epic, feature, and task files together are the plan.

- Large functional blocks become epics via `/agn:define epic`. The epic file lists linked features (optionally pre-created in the same Planner session).
- Coherent slices become features via `/agn:define feature`. The feature file lists linked tasks. A feature can be attached to an epic via `--epic <slug>` or stand alone.
- One-off work or units inside a feature become tasks via `/agn:define task`. A task can be attached to a feature via `--feature <slug>` or be ad-hoc.

The same Planner sub-agent handles Design + Plan at every tier. Each tier is optional one level up. Most product work is a feature; epics are for genuinely larger blocks.

Review cycle: user reviews each definition → Planner self-validates against rubrics → specs/requirements updated if needed → user approves.

**Refinement** — `/agn:design <level>`, `/agn:plan <level>`

For revising existing work units rather than creating new ones, `/agn:design <product|epic|feature>` and `/agn:plan <epic|feature>` invoke the same Planner sub-agent in focused mode against an existing file.

**Implementation** — `/agn:implement epic`, `/agn:implement feature`, `/agn:implement task`

- `/agn:implement task <path>` — single task execution.
- `/agn:implement feature <slug>` — every open task of a feature in order, stop-per-task for review.
- `/agn:implement epic <slug>` — every linked feature of an epic in order, stop-per-feature for review.

Per task, the agent: (1) cross-checks upstream design, halting via the escalation protocol if gaps surface; (2) produces detailed design (if not already locked upstream); (3) implements; (4) writes and runs tests. Blockers and ambiguities are surfaced via the escalation protocol.

At feature and epic boundaries, the QA sub-agent runs integration tests via `/agn:validate feature` or `/agn:validate epic`. User reviews before advancing. Documents are updated if implementation reveals necessary changes (PostClose hook automates the check).

**Validation** — `/agn:validate task | feature | epic | product`

- `/agn:validate task` — task-level quality gates run in the main session (lightweight).
- `/agn:validate feature` and `/agn:validate epic` — integration tests run by the QA sub-agent (fresh context, sees spec + result only).
- `/agn:validate product` — full system test by the QA sub-agent. Produces a system test report (critical/major/minor). Fixes what it can; escalates the rest. Re-tests until all critical and major issues are cleared.

---

### Bug Fix

Precondition: existing product with documents in `docs/`.

1. User creates a bug ticket: `/agn:define task --kind bug` — observed problem, expected result, actual result, reproduction steps.
2. User runs `/agn:implement task <defect-task>`.
3. Agent investigates root cause. Produces root cause analysis and fix plan.
4. **Architecture gate**: if the fix requires architectural changes, the agent stops and discusses with the user before proceeding.
5. Agent implements: detailed design → code → tests.
6. `/agn:validate task` — task-level quality gates.
7. `/agn:validate feature` (or `/agn:validate epic` if the touched scope crosses features) — integration tests via QA sub-agent.
8. `/agn:validate product` — full regression via QA sub-agent.
9. User approves.

---

### Maintenance

Precondition: existing product with documents in `docs/`.

**Ad-hoc task:**

1. User creates a task: `/agn:define task` (kind: `refactor`, `upgrade`, `chore`, etc.).
2. User runs `/agn:implement task <task>`. Architecture gate applies.
3. `/agn:validate task` → `/agn:validate feature` → user approves.

**Codebase optimization:**

1. User invokes `/agn:code-review`.
2. Agent audits the full codebase. Produces a report: technical debt, fragmentation, inconsistency, duplication, performance issues.
3. User reviews and prioritizes findings.
4. If structural changes are needed: agent updates architecture via `/agn:design product`, user approves.
5. Agent decomposes the work via `/agn:define feature` (or `/agn:define epic` for larger scope). User approves.
6. Execution follows the standard `/agn:implement feature` → `/agn:validate feature` → `/agn:validate product` flow.

---

### Incremental Feature

Precondition: existing product with documents in `docs/`.

Same stages as new product development, but the agent operates on existing documents:

1. `/agn:define product` (or focused `/agn:design product`) — agent drafts additions/amendments to existing vision, spec, requirements, and architecture as needed. After this stage, the existing docs describe the product including the new feature — no separate "feature docs."
2. `/agn:define feature` (or `/agn:define epic` if the work spans multiple features) — scoped to the new feature but accounts for dependencies on existing code.
3. `/agn:implement feature` (or `/agn:implement epic`), then `/agn:validate feature`, `/agn:validate product` — same as new product development.

---

## Plugin Specification

Derived from the workflows above. Everything below exists to support the user experience described in the previous section.

### Skills

agn is a Claude Code plugin named `agn`. All skills are namespaced as `/agn:<skill>`. Lifecycle skills follow the verb-noun pattern (`<verb> <level>`); tool skills are level-agnostic.

#### Lifecycle skills

| Verb | Levels | Phase(s) driven | Mechanism |
|------|--------|-----------------|-----------|
| `define` | `product\|epic\|feature\|task` | Full creation: Requirements + Spec + Design + Plan at the chosen level | Delegates to Planner sub-agent |
| `design` | `product\|epic\|feature` | Focused revision of an existing unit's design | Delegates to Planner sub-agent |
| `plan` | `epic\|feature` | Focused revision of an existing unit's decomposition | Delegates to Planner sub-agent |
| `implement` | `epic\|feature\|task` | Implementation. At task level: cross-check + code + unit tests. Halts on design gaps via escalation protocol | Main session (orchestration); recursive descent at higher levels |
| `validate` | `task\|feature\|epic\|product` | Validation. Task level: lightweight quality gates in main session. Higher levels: QA sub-agent | Mixed |

#### Tool skills

| Skill | Drives | Input | Output |
|-------|--------|-------|--------|
| `/agn:code-review` | Codebase audit | Full codebase | Audit report, backlog tasks for findings |
| `/agn:code-comment` | Code commenting | Source files | Commented source files |
| `/agn:code-commit` | Version control | Staged changes | Git commit |
| `/agn:docs-sync` | Doc maintenance on closure | Closed work unit + linked spec | Proposed diffs to `docs/architecture.md`, `docs/spec.md`, `docs/requirements.md` |

#### Skill behavior contract

Every lifecycle skill must:
1. **Validate preconditions** before starting. Skills tell the user what is missing if preconditions are not met.
2. **Produce artifacts** as specified by the verb.
3. **Run a validation cycle** after producing artifacts: self-review against rubrics, produce a report, address findings with user input.
4. **Maintain document consistency**: changes flow forward along `vision → spec → requirements → architecture → epics → features → tasks`. Upstream documents are updated only when downstream work reveals the need.
5. **Get user approval** before the stage is considered complete.

### Sub-agents

agn uses two sub-agents to enforce role separation and isolate rules from the main session.

#### Planner

- **Owns**: `rules/task-composition.md` (and `rules/writing-guideline.md` for doc-producing tiers).
- **Invoked by**: `/agn:define <level>`, `/agn:design <level>`, `/agn:plan <level>`.
- **Behavior**: receives the user's context from the parent session, dialogs with the user via the parent for clarifications, drives Design + Plan phases. Persists outputs via `taskman.sh`.
- **Why a sub-agent**: composition rules stay out of the parent session's context; the same agent can be reused across all four tiers (it is level-aware).

#### QA

- **Owns**: `rules/qa.md`.
- **Invoked by**: `/agn:validate feature`, `/agn:validate epic`, `/agn:validate product`.
- **Behavior**: receives spec + implementation result only (not the implementer's reasoning or decisions). Reviews code against spec, runs tests, identifies coverage gaps, validates end-to-end flows. Produces a verdict + report.
- **Why a sub-agent**: fresh context catches issues the implementer overlooks due to implicit context bias.

`/agn:validate task` runs in the main session (lightweight; just runs the task's quality gates) because the cost of a sub-agent is not warranted for a single task's validation.

### Hooks

- **PostClose** — fires on success of `taskman.sh move <path> done`, `taskman.sh feature close <slug>`, or `taskman.sh epic close <slug>`. Invokes `/agn:docs-sync` to review upstream `docs/` files for drift and propose diffs. User reviews diffs before commit. If no active Claude session at hook fire time, the hook queues a note that surfaces at next session start.

### Escalation protocol

When `/agn:implement task` cross-checks the task body against upstream design and detects missing or ambiguous design decisions, the skill halts immediately and:

1. Writes a gap-log entry to a durable on-disk location (survives compaction; feeds the future feedback loop).
2. The entry contains: gap description, suspected upstream level (task / feature / epic / architecture), implementation context at point of detection.
3. Surfaces routing instructions to the user: `"Gap at <level>. Run /agn:design <level> to address before continuing."`
4. The user manually runs the upstream skill. After it completes, the user re-invokes `/agn:implement task`; the skill re-reads the task body to pick up the revised design.

This protocol prevents silent intermixing of Design and Implementation work. Frequent escalations are a signal of insufficient upstream design and feed into the long-term feedback loop (backlog task `feedback_loop_infrastructure`) to improve prompts and rules.

### Behavioral Guardrails

Rules live in `plugins/agn/rules/`. To activate them in a user's project, the user `@`-imports them in their project's `CLAUDE.md`.

| Guardrail | Content | Source | Loaded by |
|-----------|---------|--------|-----------|
| Core Principles | YAGNI, KISS, DRY, readability over performance, single-task focus, clarify ambiguity, step-by-step approval, root-cause troubleshooting | `rules/first-principles.md` | Always — every session |
| Task Composition | Frontmatter shapes, body section requirements, completion-summary template | `rules/task-composition.md` | Planner sub-agent |
| Task Persistence | Lifecycle (backlog → active → done), CLI surface, validation rules | `taskman.sh help` | Authoritative reference; consulted by skills that touch lifecycle |
| QA | Validation mindset, role separation, integration / system test protocols | `rules/qa.md` | QA sub-agent + `/agn:validate task` |
| Doc Maintenance | What to check on closure (drift in architecture / spec / requirements) | `rules/doc-maintenance.md` | `/agn:docs-sync` |
| Writing Guideline | Crisp, no-fluff document style: short sentences, active voice, absolute dates, no weasel/peacock words | `rules/writing-guideline.md` | Document-producing skills (Planner sub-agent, `/agn:docs-sync`) |

Skills themselves contain only workflow instructions — no inlined rules. They rely on the rules being present in their context (loaded by sub-agent system prompt, by skill `!cat`, or by the user's `CLAUDE.md`).

### User's Project Structure

agn skills create the following layout in the user's project as they progress through SDLC stages:

```
user-project/
├── docs/
│   ├── vision.md
│   ├── spec.md
│   ├── requirements.md
│   ├── architecture.md
│   └── <area>/.../-spec.md       # feature-scoped specs
├── tasks/
│   ├── epics/                     # YYYYMMDD_<slug>.md
│   ├── features/                  # YYYYMMDD_<slug>.md
│   ├── backlog/                   # YYYYMMDD[_NN]_<slug>.md
│   ├── active/
│   └── done/
```

`/agn:define product` creates the `docs/` directory and initial documents if they don't exist. `/agn:define <epic|feature|task>` create files under `tasks/`. The project structure is created incrementally as the user progresses through stages — no upfront scaffolding required.

### Workflow State

Each skill checks its own preconditions by examining which artifacts exist. There is no separate workflow state file. The documents ARE the state:

- Definition complete → `vision.md`, `spec.md`, `requirements.md` exist with validated content.
- Architecture complete → `architecture.md` exists and is consistent with definition docs.
- Decomposition complete → epic / feature / task files exist.
- Feature complete → all member tasks in `tasks/done/`, feature `status: done`.
- Epic complete → all member features `status: done`, epic `status: done`.
- Implementation complete → all tasks in `tasks/done/` and all epics/features closed.
- Validation complete → system test report shows all critical/major issues resolved.

The user can always look at `docs/` and `tasks/` to understand where they are.

---

## Requirements

Cross-cutting concerns that apply across all workflows.

### Document Consistency

When any document changes, the skill that made the change must check dependent documents for inconsistencies and update them. The dependency order is: vision → spec → requirements → architecture → epics → features → tasks. The agent must explicitly state which documents it is updating and why. The PostClose hook automates this check at closure.

### Precondition Enforcement

Every skill validates its preconditions before starting work. Missing preconditions produce a clear message ("Cannot run `/agn:design product` — definition documents not found. Run `/agn:define product` first."). No skill silently proceeds with incomplete inputs.

### User Approval Gates

Stage transitions require explicit user approval. The agent must not proceed to the next stage until the user says to. Within a stage the agent can iterate autonomously (draft → validate → update), but completing a stage and moving forward is always a user decision.

### Architecture Impact Gate

Any change that touches the high-level architecture — whether discovered during bug fixing, maintenance, or implementation — triggers a mandatory discussion with the user before proceeding. The agent presents the architectural impact, proposes options, and waits for explicit approval. The escalation protocol routes architecture-level gaps to `/agn:design product`.

### Task DAG Execution

When executing multiple tasks (`/agn:implement feature` or `/agn:implement epic`), the agent respects feature and epic boundaries. In v1, tasks run sequentially within a feature, and features run sequentially within an epic; parallel execution is deferred. Integration tests (`/agn:validate feature` or `/agn:validate epic`) run at boundaries. The user can interrupt execution at any boundary.

### Validation Rubrics

Two rubrics applied during Definition and reused as quality gates throughout:

**Business case:**
- Do we demonstrate understanding of the business and user problem?
- Does the spec actually solve the business problem? Is there a better way?
- Is the monetization case sound?
- Are risks identified and addressed?

**Functional:**
- Is functionality defined consistently across all documents?
- Are there gaps, ambiguities, inconsistencies, or missing details?
- Is the level of detail sufficient for the next stage to proceed without guesswork?

### Scope Discipline

During implementation, the agent does not modify functionality outside the scope of the current task, feature, or epic. Any scope creep is flagged to the user. This applies to all workflows.

---

## Traceability: Workflows → Plugin Components

Cross-reference confirming that every workflow step maps to a plugin component.

| Workflow Step | Skill (`/agn:*`) | Agent | Artifacts Produced |
|--------------|------------------|-------|--------------------|
| New product → Definition | `define product` | Planner | vision, spec, requirements |
| New product → Architecture | `design product` | Planner | architecture |
| New product → Epic decomposition | `define epic` | Planner | epic file, linked feature files |
| New product → Feature decomposition | `define feature` | Planner | feature file, linked task files |
| New product → Implementation (epic) | `implement epic` | main session | code, tests, integration reports per feature |
| New product → Implementation (feature) | `implement feature` | main session | code, tests, integration report |
| New product → Implementation (task) | `implement task` | main session | code, tests (escalates on design gap) |
| New product → Integration test (feature/epic) | `validate feature` / `validate epic` | QA | integration test report |
| New product → System test | `validate product` | QA | system test report |
| Bug fix → Task creation | `define task --kind bug` | Planner | bug ticket file |
| Bug fix → Fix | `implement task` | main session | code, tests, root cause analysis |
| Bug fix → Integration test | `validate feature` | QA | integration test report |
| Bug fix → Regression | `validate product` | QA | system test report |
| Maintenance → Ad-hoc | `define task`, `implement task` | Planner, main session | task file, code, tests |
| Maintenance → Ad-hoc → Test | `validate task`, `validate feature` | main session, QA | test reports |
| Maintenance → Optimization | `code-review`, `define feature` (or `define epic`), `implement feature` | main session, Planner | audit report, decomposition artifacts, code |
| Incremental feature | `define feature` + `implement feature` + `validate feature` | Planner, main, QA | same as new product (amended) |
| Doc sync after closure | `docs-sync` (PostClose hook) | main session | proposed diffs to `docs/` |

All workflows are fully covered by the lifecycle and tool skills, the Planner and QA sub-agents, and the PostClose hook. Behavioral guardrails are loaded according to the table in **Behavioral Guardrails** above. No workflow step requires a component not listed.
