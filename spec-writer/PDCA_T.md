# PDCA-T / METHOD.md Mapping

Canonical definition: [exchanet/method_pdca-t_coding — METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md). **T** means **Test**: quality is built in each increment (criteria + automated tests + evidence), not only inspected at the end. **Traceability** (requirements → tasks → tests) supports every phase but is not a substitute for **T**.

Use PDCA-T as the mental model for every spec; mirror it in the three sections:

| Letter | In this skill |
|--------|----------------|
| **P — Plan** | SECTION 1 (SPEC) nails objective, scope, and acceptance; SECTION 2 (PLAN) nails architecture, contracts, and test strategy *before* implementation stories. |
| **D — Do** | SECTION 3 (TASKS): ordered micro-work — each step implementable and reversible. |
| **C — Check** | Given/When/Then criteria, per-task acceptance, PLAN testing strategy, **Review checkpoint** — verify against the spec and test results, not intent. |
| **A — Act** | Assumptions summary and `[ASSUMPTION: ...]` — human adjusts scope/design; feed corrections into the next Plan pass (updated SPEC/PLAN), not silent drift. |
| **T — Test** | Every meaningful task has **verifiable** outcomes; PLAN calls out unit / integration / e2e as appropriate. Prefer **test-first** for the implementing agent when the user or project standards require it (per METHOD Phase 4). |

## METHOD 8-Phase Mapping

| METHOD phase | What to produce in this skill |
|----------------|-------------------------------|
| **1 — Planning** | One-line purpose; explicit **IN scope / OUT of scope**; external dependencies; acceptance criteria agreed in writing (block vague objectives — flag with `[ASSUMPTION]` until clarified). |
| **2 — Requirements analysis** | Optional but recommended for complex work: **FR-NN** / **NFR-NN** / **RISK-NN** blocks (see below) in addition to plain Requirements / edge cases. |
| **3 — Architecture design** | PLAN: decisions that pass the ADR test below as **ADR-NN**; API/contracts sketched before tasks; module or layer layout if it reduces ambiguity. |
| **4 — Micro-task cycle** | TASKS: small increments; note **≤ ~50 lines of production code per micro-task** when using strict PDCA-T (excluding tests/docs — per METHOD). Sub-task checklist: context/skills → contract exists → **test categories** (happy, error, edge, security, performance where relevant) → implement → review → run tests. |
| **5 — Integral validation** | PLAN **Testing strategy** + TASK criteria should enable full validation later (security, coverage targets, architecture checks) — state expectations if the user's METHOD.md workflow applies. |
| **6 — Technical debt** | Known gaps: register as **DEBT-NN** (or defer to assumptions) instead of silent TODOs in "done" work. |
| **7 — Refinement** | Loop until agreed targets (e.g. coverage, failing tests) — specify targets in PLAN when user requires METHOD-grade gates. |
| **8 — Delivery** | Out of scope for spec-writer output unless the user asks: then add a short **Delivery evidence** stub (what to attach: test run, coverage, decisions, debt list). |

## When an ADR Is Warranted

<!-- adapted from mattpocock/skills domain-modeling ADR-FORMAT (MIT) -->

Write an **ADR-NN** only when all three are true:

1. **Hard to reverse**: changing your mind later costs real time or money.
2. **Surprising without context**: a future reader would look at the code and ask why it was done this way.
3. **A real trade-off**: there were genuine alternatives and one was picked for specific reasons.

If a decision is easy to reverse, obvious, or had no real alternative, keep it as a line of PLAN prose instead.
Typical qualifiers: architectural shape, integration patterns between contexts, technology choices with lock-in, boundary and ownership decisions, deliberate deviations from the obvious path, constraints not visible in the code, and rejections a reader would otherwise re-propose.
An ADR can be one paragraph: context, decision, why.
Add Alternatives and Consequences only when they carry information.

## Optional Formats

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
