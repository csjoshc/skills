---
name: spec-writer
description: Takes a vague feature request and generates a structured spec, technical plan, and task breakdown ready for any coding agent. Aligns with PDCA-T (Plan-Do-Check-Act-Test) and can follow exchanet METHOD.md patterns (FR/NFR/RISK, ADR, micro-tasks, test-first) when the user asks for strict or PDCA-T mode. Use whenever you're about to build a feature and want to reduce ambiguity before writing code. Invoke with /spec-writer followed by your feature description.
---

## TL;DR (Quick Start)

Turns vague feature requests into structured technical specs, implementation plans (PLAN), and atomic micro-tasks (TASKS). Mark every decision as `[ASSUMPTION: ...]`.

**When to use:** "write a spec for...", "plan this feature", "break this down into tasks".

**Invocation:**
```bash
/spec-writer <feature-description>
```

## Companion files (progressive disclosure)

- **Parallel or batched markdown tickets** (e.g. many tickets for one Orchestra run with `--concurrency` / `-j`, explicit `Depends-On:`): when the user asks for parallel tickets, a ticket batch, or `-j` / multi-ticket concurrency, read **[`PARALLEL_TICKETS_BATCH.md`](~/.skills/spec-writer/PARALLEL_TICKETS_BATCH.md)** before generating the batch.

## Decision Tree

1. **How much ambiguity exists?**
   - LOW (obvious stack/goals) → Generate full SPEC + PLAN + TASKS.
   - MEDIUM/HIGH → Generate SPEC + PLAN + **Assumptions Summary**; wait for user feedback before TASKS.

2. **Is strict quality required (PDCA-T / METHOD.md)?**
   - YES → **MANDATORY** use 8-phase mapping and ≤ 50 lines per task.
   - NO → Standard 3-section output.

3. **Does the task hit a blast radius limit (>5 files)?**
   - YES → **MANDATORY** split into child certificates/tickets via `01a-`, `01b-` pattern.
   - NO → Proceed.

4. **Is the user asking for parallel / batched runner tickets (`-j`, many `.tickets/` files, explicit DAG)?**
   - YES → Read **[`PARALLEL_TICKETS_BATCH.md`](~/.skills/spec-writer/PARALLEL_TICKETS_BATCH.md)**, then apply its checklist plus any project ticket skill (e.g. Orchestra `orchestra-decomposed-tickets`).
   - NO → Continue with the sections below.

## Workflow

---

## Operating principles

**Mandatory SPEC file (Section 1)**
Without a written spec, agents invent UX, edge cases, and scope — then the human pays in refusals and refactors. Section 1 is non-optional: purpose, users, requirements, edge cases, and acceptance criteria must exist before implementation planning is trustworthy.

**Atomic micro-instructions (Section 3)**
Tasks are numbered, directly executable steps: **one discrete action per task** (or per sub-bullet if you split inside a task). No vague roll-ups like "wire up the feature." Each step should be doable and verifiable on its own.

**Project-specific rules and skills**
Honor repo rules, `AGENTS.md`, Cursor rules, and linked skills: **strict context, zero ambiguity** for stack, conventions, and boundaries. When the user names a project standard, the spec and tasks must reference it explicitly instead of assuming a generic stack.

**Risk-tiered assumptions**
Not all assumptions need human review. Before blocking:
1. Check embedded Architecture Decisions below for resolved questions
2. Tier 1 (reversible, low impact) → proceed, flag for post-review
3. Tier 2 (architecture, medium impact) → check Architecture Decisions, block if unresolved
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

## Architecture Decisions

See [`~/.skills/shared/ARCHITECTURE_DECISIONS.md`](~/.skills/shared/ARCHITECTURE_DECISIONS.md)
for canonical API patterns, authentication, data layer, testing strategy, code organization,
layer ownership, resolved questions, security checklist, and performance budgets.

**Project-specific overrides:** See `./STANDARDS.md` in the target project.

### Assumption Tiers

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for spec-writer:**
- **Tier 1:** Naming conventions, file locations, UI copy → proceed without blocking
- **Tier 2:** API patterns, data model structure, library choices → check Architecture Decisions, block if unresolved
- **Tier 3:** Security, auth, public API, database schema → always block for human confirmation

Format:
```
## Assumptions to review

1. [ASSUMPTION text] — Impact: HIGH / MEDIUM / LOW — Tier: 1 / 2 / 3
   Correct this if: [when it matters]
   [Optional: Resolved via Architecture Decisions section X]

2. ...
```

**Blocking guidance:**
- Tier 1: No block needed, flag for post-review
- Tier 2: Block if Architecture Decisions doesn't resolve
- Tier 3: Always block before Task 1

---

## Quality rules

- Ticket files must include canonical YAML header with `Stage:`. For implementation-ready tickets generated by this skill, write `Stage: BUILD` and keep stage values within: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
- **SPEC is mandatory** (Section 1). Skipping it causes invented design; keep it technology-agnostic — no framework names, no library choices, no implementation details in requirements.
- **Size thresholds trigger refactoring**: If a planned change causes any file to exceed **300 lines** (or 500 lines for well-structured modules), the plan **must include a refactoring step** as a first-level acceptance criteria. See [ANTIPATTERNS.md](~/.skills/spec-writer/ANTIPATTERNS.md) for common patterns to avoid.
- **Avoid antipatterns**: Before finalizing any spec, check [ANTIPATTERNS.md](~/.skills/spec-writer/ANTIPATTERNS.md) to ensure the plan doesn't introduce known code smells.
- The plan must be concrete. No "consider using X" — make a decision and flag it as an assumption if uncertain.
- Every task must be independently deployable or testable. If a task can't be verified on its own, split it.
- Acceptance criteria must be binary. "Works correctly" is not a criterion. "Returns 401 when unauthenticated" is.
- Never write a task that says "implement the feature." That's the whole spec. Tasks are the pieces.
- Align outputs with **PDCA-T** ([METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md)): **Plan** before code; **Do** in small tasks; **Check** against criteria and runs; **Act** via assumptions and ADR updates; **Test** as a first-class gate (strategy in PLAN, proof in TASK acceptance). Keep **traceability**: requirements / FRs → tasks → tests via the assumptions summary and explicit criteria.
- When project rules or skills exist, **cite them** in PLAN (patterns) and TASKS (constraints) so execution stays unambiguous.
- For architecture decisions, see [`~/.skills/shared/ARCHITECTURE_DECISIONS.md`](~/.skills/shared/ARCHITECTURE_DECISIONS.md).

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

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.