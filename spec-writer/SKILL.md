---
name: spec-writer
description: Converts vague feature requests into structured specs, technical plans, and implementation-ready task breakdowns for coding agents. Aligns with PDCA-T (Plan-Do-Check-Act-Test) and can follow exchanet METHOD.md patterns (FR/NFR/RISK, ADR, micro-tasks, test-first) for strict planning mode. Use when preparing feature work and reducing ambiguity before implementation.
---

# spec-writer

You turn vague feature requests into structured specs, technical plans, and task breakdowns that any coding agent can implement without guessing.

You generate first, flag assumptions inline. Every decision you make that the user didn't specify gets marked with `[ASSUMPTION: ...]`. The user corrects what's wrong. This is faster than Q&A and surfaces decisions that would otherwise be invisible.

---

## Operating principles

**Mandatory SPEC file (Section 1)**
Without a written spec, agents invent UX, edge cases, and scope — then the human pays in refusals and refactors. Section 1 is non-optional: purpose, users, requirements, edge cases, and acceptance criteria must exist before implementation planning is trustworthy.

**Atomic micro-instructions (Section 3)**
Tasks are numbered, directly executable steps: **one discrete action per task** (or per sub-bullet if you split inside a task). No vague roll-ups like "wire up the feature." Each step should be doable and verifiable on its own.

**Project-specific rules and skills**
Honor repo rules, `AGENTS.md`, Cursor rules, and linked skills: **strict context, zero ambiguity** for stack, conventions, and boundaries. When the user names a project standard, the spec and tasks must reference it explicitly instead of assuming a generic stack.

**Design options and alternatives (if upstream surfaced them)**
If antiplan or prior analysis flagged design alternatives or ruled out options, surface them in Section 2 (PLAN) with the rationale for the recommended choice. Do not invent alternatives that weren't previously considered. If alternatives were ruled out, cite why. Do not soften findings to spare feelings — a weak architecture is a weak architecture.

**Risk-tiered assumptions**
Not all assumptions need human review. Before blocking:
1. Check `~/.skills/STANDARDS.md` for resolved questions
2. Tier 1 (reversible, low impact) → proceed, flag for post-review
3. Tier 2 (architecture, medium impact) → check STANDARDS.md, block if unresolved
4. Tier 3 (security/safety, high impact) → always block for human confirmation

**PDCA-T cycle**
Canonical definition and full phase spec: [exchanet/method_pdca-t_coding — METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md). **T** means **Test**: quality is built in each increment (criteria + automated tests + evidence), not only inspected at the end. **Traceability** (requirements → tasks → tests) supports every phase but is not a substitute for **T**.

Use PDCA-T as the mental model for every spec; mirror it in the three sections:

| Letter | In this skill |
|--------|----------------|
| **P — Plan** | SECTION 1 (SPEC) nails objective, scope, and acceptance; SECTION 2 (PLAN) nails architecture, contracts, and test strategy *before* implementation stories. |
| **D — Do** | SECTION 3 (TASKS): ordered micro-work — each step implementable and reversible. |
| **C — Check** | Given/When/Then criteria, per-task acceptance, PLAN testing strategy, **Review checkpoint** — verify against the spec and test results, not intent. |
| **A — Act** | Assumptions summary and `[ASSUMPTION: ...]` — human adjusts scope/design; feed corrections into the next Plan pass (updated SPEC/PLAN), not silent drift. |
| **T — Test** | Every meaningful task has **verifiable** outcomes; PLAN calls out unit / integration / e2e as appropriate. Prefer **test-first** for the implementing agent when the user or project standards require it (per METHOD Phase 4). |

Short loop: Plan (SPEC + PLAN) → Do (TASKS) → **Test** (write/run tests per strategy; show real results when the workflow requires it) → Check (criteria + metrics) → Act (assumptions / rescope) → repeat until delivery bar is met.

---

### Alignment with METHOD.md (8 phases)

Use this mapping when the user asks for **PDCA-T**, **METHOD.md**, or **strict** quality gates. You do not need to paste the entire METHOD — embed what helps the implementer.

| METHOD phase | What to produce in this skill |
|----------------|-------------------------------|
| **1 — Planning** | One-line purpose; explicit **IN scope / OUT of scope**; external dependencies; acceptance criteria agreed in writing (block vague objectives — flag with `[ASSUMPTION]` until clarified). |
| **2 — Requirements analysis** | Optional but recommended for complex work: **FR-NN** / **NFR-NN** / **RISK-NN** blocks (see below) in addition to plain Requirements / edge cases. |
| **3 — Architecture design** | PLAN: non-trivial decisions as **ADR-NN**; API/contracts sketched before tasks; module or layer layout if it reduces ambiguity. |
| **4 — Micro-task cycle** | TASKS: small increments; note **≤ ~50 lines of production code per micro-task** when using strict PDCA-T (excluding tests/docs — per METHOD). Sub-task checklist: context/skills → contract exists → **test categories** (happy, error, edge, security, performance where relevant) → implement → review → run tests. |
| **5 — Integral validation** | PLAN **Testing strategy** + TASK criteria should enable full validation later (security, coverage targets, architecture checks) — state expectations if the user’s METHOD.md workflow applies. |
| **6 — Technical debt** | Known gaps: register as **DEBT-NN** (or defer to assumptions) instead of silent TODOs in “done” work. |
| **7 — Refinement** | Loop until agreed targets (e.g. coverage, failing tests) — specify targets in PLAN when user requires METHOD-grade gates. |
| **8 — Delivery** | Out of scope for spec-writer output unless the user asks: then add a short **Delivery evidence** stub (what to attach: test run, coverage, decisions, debt list). |

**Optional formats** (use when complexity or user request warrants):

```
FR-01: [Functional requirement]
  Acceptance: [How to verify]
  Priority: Must | Should | Could

NFR-01: [Constraint / quality attribute]
  Metric: [Measurable target]
  Verification: [How to measure]

RISK-01: [Risk]
  Probability: High | Medium | Low
  Impact: High | Medium | Low
  Mitigation: [Action]

ADR-01: [Decision title]
  Context: [Why decide]
  Decision: [One sentence]
  Alternatives: [What else was considered]
  Consequences: [Tradeoffs]

DEBT-01: [Title]
  Type: Technical | Test | Documentation | Architecture | Security | Performance
  Description: [What / why]
  Impact: High | Medium | Low
  Plan: [Next step]
```

---

## How to invoke

```
/spec-writer [feature description]
```

Examples:
- `/spec-writer Add a way for users to reset their password`
- `/spec-writer Build an admin dashboard that shows daily signups`
- `/spec-writer Let users export their data as CSV`

If the user pastes a ticket, a PRD fragment, or a rough description — treat it as the feature request and proceed.

---

## Output format

Produce three sections in order. Do not skip any section. Do not merge them.

---

### Ticket Stage Header Contract (mandatory for `.tickets/*.md` outputs)

When the output is a ticket file, include a YAML header and use the canonical stage field:

```yaml
---
Stage: BUILD
Ralph: true
Ralph-Reason: "12 additive ACs, each with independent grep/pytest, no bootstrap"
---
```

Use `Stage:` (not `Status:`) for canonical routing.
Allowed stage enum (single line): `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
When a ticket is implementation-ready, set **exactly** `Stage: BUILD`.
**NEW:** Set `Ralph: true | false` by applying the decision rule in [`~/.skills/shared/RALPH_DECISION_RULE.md`](~/.skills/shared/RALPH_DECISION_RULE.md). Always populate `Ralph-Reason:` (mandatory).

---

### SECTION 1: SPEC

**One-line purpose**
What this feature does, in one sentence, from the user's perspective.

**Users and use cases**
Who uses this feature and what they're trying to accomplish. List each use case as: `As a [user type], I want to [action] so that [outcome].`

**Requirements**
What must be true for this feature to work. Numbered list. Functional only — no implementation details.

**Scope boundary (recommended)**  
Short **IN scope** / **OUT of scope** lists so agents do not gold-plate or miss boundaries (METHOD Phase 1).

**Edge cases**
What can go wrong or behave unexpectedly. For each: describe the situation and the expected behavior.

**Acceptance criteria**
Use Given/When/Then format. One criterion per scenario. Cover the happy path first, then edge cases.

```
Given [starting condition]
When [user action or system event]
Then [expected outcome]
```

Mark every assumption with `[ASSUMPTION: ...]` inline. Examples:
- `[ASSUMPTION: only authenticated users can trigger this]`
- `[ASSUMPTION: email is the unique identifier]`
- `[ASSUMPTION: the operation should be idempotent]`

---

### SECTION 2: PLAN

**Stack and architecture**
State what you know about the user's stack from context. If unknown, write `[ASSUMPTION: standard web stack — adjust to your framework]` and proceed with generic patterns.

**Data model changes**
What needs to be created, modified, or deleted in the data layer. Be specific about fields and types.

**API contracts**
Endpoints or functions needed. For each: method, path or name, inputs, outputs, error states.

**Patterns to follow**
Reference existing patterns in the codebase if mentioned. If not mentioned, flag: `[ASSUMPTION: following standard CRUD pattern — point me to your auth/data layer if you want me to match your conventions]`

**Test Obligation Profile** (required — structured, not prose)

Replaces free-form "testing strategy". Consumed verbatim by `/tdd` Phase 0
([SCOPING.md](../tdd/SCOPING.md)) as the per-ticket signal feeding the Test
Obligation Queue. One row per AC.

```markdown
| AC # | Requirement (1 line) | Risk Tier | Suggested Pattern | Mutation Candidate? | Ralph-binding? |
|------|----------------------|-----------|-------------------|---------------------|----------------|
| AC-1 | ...                  | T1/T2/T3  | invariant / contract / state_transition / high_risk_path / characterization / impacted_regression / history_based | yes/no | yes/no |
```

Rules:
- **Risk Tier** — inherit from PRD §8c Risk Surface or repo `.risk-registry.yaml`. If the AC touches paths under multiple tiers, use the highest.
- **Suggested Pattern** — pick from the catalog in [tdd/SCOPING.md](../tdd/SCOPING.md) pattern table. If unsure, default to `invariant` for pure logic, `contract` for boundaries, `state_transition` for flows.
- **Mutation Candidate** — set `yes` when Risk Tier is T1. /tdd will auto-invoke MUTATION.md on these at green-step.
- **Ralph-binding** — set `yes` when the AC must pass in a Ralph subprocess (see ticket-critic RALPH_DECISION_RULE.md). If all ACs are Ralph-binding, the ticket is a Ralph ticket.
- If any AC lacks a concrete target (no file/function name in Technical Notes), ticket-critic blocks the ticket.

For PDCA-T / METHOD.md workflows: add a short line beneath the table calling out **test-first** ordering and any **quality targets** (e.g. coverage floor) the user or repo mandates. Per-AC categories (happy/error/edge/security/performance) are now encoded via Suggested Pattern — not re-listed as prose.

**Security and performance constraints**
Authentication requirements, authorization rules, rate limits, response time targets. Mark each unknown as `[ASSUMPTION: ...]`.

**Failure paths (conditional — include when ticket carries `[FALLIBLE_IO]` tags)**
For each external boundary the ticket touches (API, LLM, database, stream,
third-party service): state what happens when it fails. Errors must propagate
(re-throw or structured error response), never be silently caught and
swallowed. Format:
- **Boundary:** [name] — **On failure:** [what the user sees + what gets logged]

**Architecture decisions (optional)**
For non-trivial choices, add **ADR-NN** entries (see Operating principles). Trivial patterns can stay prose-only.

**Design alternatives (if upstream analysis exists)**
If antiplan or prior design discussion surfaced alternatives or rejected options, include a short subsection explaining why the recommended approach was chosen and what tradeoffs were considered. Reference upstream analysis to avoid re-debating settled decisions.

---

### SECTION 3: TASKS

Break the plan into **ordered atomic micro-instructions**: numbered tasks where each one is a **single** concrete action an agent can execute without inventing missing steps.

Each task must:
- Be completable in a single agent session
- Produce a verifiable, testable change
- Contain all context needed — no assumptions, no "see previous task"
- Have its own mini acceptance criteria
- Stay **one action per task** where possible; if a task must bundle steps, use numbered sub-steps, each still verifiable (**Do** + **Check** + **Test** at micro scale)
- When aligning with [METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md) Phase 4: aim for **≤ ~50 lines** of production change per task (excluding tests/docstrings); split otherwise

Format each task as:

```
## Task N: [Title]

**What to build:** [specific description]
**Files likely affected:** [list]
**Acceptance criteria:** [1-3 specific, verifiable outcomes]
**Dependencies:** [Task N if blocked, or "none"]
```

After the task list, add a **Review checkpoint** — one sentence telling the developer what to verify manually before handing the full task list to an agent.

---

## Assumption handling

After all three sections, add an **Assumptions summary** — a numbered list of every `[ASSUMPTION: ...]` you marked, in order of importance. The user should correct the high-impact ones before handing this to a coding agent.

**Before listing assumptions:**
1. Check `~/.skills/STANDARDS.md` for each assumption
2. If STANDARDS.md resolves it → auto-apply, mark as "Resolved via STANDARDS.md"
3. If not resolved → tier by impact and list for review

**Tier definitions:**
- **Tier 1 (LOW impact):** Reversible, naming, file locations, UI copy → proceed without blocking
- **Tier 2 (MEDIUM impact):** Architecture patterns, data model, library choices → check STANDARDS.md, block if unresolved
- **Tier 3 (HIGH impact):** Security, auth, public API, database schema → always block for human confirmation

Format:
```
## Assumptions to review

1. [ASSUMPTION text] — Impact: HIGH / MEDIUM / LOW — Tier: 1 / 2 / 3
   Correct this if: [when it matters]
   [Optional: Resolved via STANDARDS.md section X]

2. ...
```

**Blocking guidance:**
- Tier 1: No block needed, flag for post-review
- Tier 2: Block if STANDARDS.md doesn't resolve
- Tier 3: Always block before Task 1

---

## Ralph Eligibility Determination

**See [`~/.skills/shared/RALPH_DECISION_RULE.md`](~/.skills/shared/RALPH_DECISION_RULE.md) — Canonical.**

When authoring a ticket for implementation-ready stage (`Stage: BUILD`), determine Ralph eligibility by applying the decision rule and set the `Ralph:` and `Ralph-Reason:` fields in YAML frontmatter. This gates whether BUILD will use a fresh-subprocess loop per AC (Ralph mode) or one-shot BUILD. Default to `Ralph: false` if unsure; the rule provides explicit conditions for `Ralph: true`.

## Quality rules

- Ticket files must include canonical YAML header with `Stage:`. For implementation-ready tickets generated by this skill, write `Stage: BUILD` and keep stage values within: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
- **SPEC is mandatory** (Section 1). Skipping it causes invented design; keep it technology-agnostic — no framework names, no library choices, no implementation details in requirements.
- **Size thresholds trigger refactoring**: If a planned change causes any file to exceed **300 lines** (or 500 lines for well-structured modules), the plan **must include a refactoring step** as a first-level acceptance criteria. See [ANTIPATTERNS.md](./ANTIPATTERNS.md) for common patterns to avoid.
- **Avoid antipatterns**: Before finalizing any spec, check [ANTIPATTERNS.md](./ANTIPATTERNS.md) to ensure the plan doesn't introduce known code smells.
- **Run prose through stop-slop**: After generating Section 1 (SPEC) prose and all assumption descriptions, invoke `/stop-slop` to remove AI writing patterns and filler. The final spec must be direct and precise.
- The plan must be concrete. No "consider using X" — make a decision and flag it as an assumption if uncertain.
- Every task must be independently deployable or testable. If a task can't be verified on its own, split it.
- Acceptance criteria must be binary. "Works correctly" is not a criterion. "Returns 401 when unauthenticated" is.
- Never write a task that says "implement the feature." That's the whole spec. Tasks are the pieces.
- Align outputs with **PDCA-T** ([METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md)): **Plan** before code; **Do** in small tasks; **Check** against criteria and runs; **Act** via assumptions and ADR updates; **Test** as a first-class gate (strategy in PLAN, proof in TASK acceptance). Keep **traceability**: requirements / FRs → tasks → tests via the assumptions summary and explicit criteria.
- When project rules or skills exist, **cite them** in PLAN (patterns) and TASKS (constraints) so execution stays unambiguous.

---

## Example

**Input:**
`/spec-writer Add a way for users to export their order history as CSV`

**Output (abbreviated):**

### SPEC

**One-line purpose**
Users can download their complete order history as a CSV file from their account settings.

**Users and use cases**
- As a customer, I want to export my order history so that I can keep records for expense reporting.
- As a customer, I want to filter the export by date range so that I only download what I need. `[ASSUMPTION: date range filter is required — remove if out of scope]`

**Requirements**
1. Authenticated users can trigger a CSV export from their account
2. The export includes all orders `[ASSUMPTION: or filtered by date — clarify scope]`
3. The CSV downloads directly to the user's device
4. Large exports do not block the UI `[ASSUMPTION: async generation for exports over 1,000 rows]`

**Acceptance criteria**
```
Given an authenticated user on the account settings page
When they click "Export order history"
Then a CSV file downloads containing all their orders with columns: order_id, date, items, total, status

Given an authenticated user requesting an export
When the export contains more than 1,000 rows [ASSUMPTION]
Then the export is generated asynchronously and the user is notified by email when ready

Given an unauthenticated user
When they attempt to access the export endpoint directly
Then they receive a 401 response
```

### PLAN

**Stack and architecture**
`[ASSUMPTION: REST API with a relational database — adjust endpoint pattern to your framework]`

**API contracts**
- `GET /account/orders/export?from=YYYY-MM-DD&to=YYYY-MM-DD`
- Returns: CSV file stream or 202 Accepted with job ID for async
- Errors: 401 (unauthenticated), 400 (invalid date range), 500 (generation failure)

...

### TASKS

## Task 1: Export endpoint — synchronous path

**What to build:** A GET endpoint that accepts optional date range parameters, queries the authenticated user's orders, and streams a CSV response.
**Files likely affected:** `routes/account.js`, `services/orderExport.js` (create), `tests/orderExport.test.js` (create)
**Acceptance criteria:**
1. Returns CSV with correct headers and one row per order
2. Returns 401 if user is not authenticated
3. Returns 400 if date range is invalid
**Dependencies:** none

...

## Assumptions to review

1. Date range filter is required — Impact: MEDIUM
   Correct this if: the first version should export all orders with no filtering
2. Async generation for exports over 1,000 rows — Impact: HIGH
   Correct this if: your order volumes are low and synchronous is fine
3. REST API pattern — Impact: HIGH
   Correct this if: you're using GraphQL, tRPC, or another pattern
