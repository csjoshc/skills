---
name: spec-writer
description: >-
  Defined feature -> spec, ADR, micro-tasks (PDCA-T, FR/NFR/RISK). Use when
  requirements are clear and an engineering breakdown is needed for a coding
  agent. Not for fuzzy ideas (use make-prd) or contested requirements
  (use antiplan).
  In: .plan/PRD.md + .plan/task-sequence.md, or a single defined feature request.
  Process: expand each placeholder via FR/NFR/RISK + ADR.
  Out: .tickets/NN-<slug>.md files.
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

**Source-driven framework patterns:** see `references/docs-first.md` for fetch-and-cite discipline when filling PLAN with framework-specific guidance.

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

<!-- pattern: not-doing-scope -->
### Not Doing (scope discipline)

Every spec ends with a `## Not Doing` section listing things that were intentionally skipped, with one-line reason each. Cheap to write, prevents scope creep mid-implementation.

Example:
- Mobile responsive tweaks — out of scope for v1, separate ticket
- Email templating engine — using existing hardcoded HTML
- Audit log — covered by global middleware, no local code needed

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

**Preferred input (from upstream `antiplan` or `make-prd`):**
- `.plan/PRD.md` — narrative, scope, decisions
- `.plan/task-sequence.md` — ordered placeholders to expand

When both files exist, read them first and expand each placeholder in `task-sequence.md` into a fully-fleshed `.tickets/NN-<slug>.md`. Do not re-debate decisions already settled in the PRD. If only a free-text feature request is provided, generate without the upstream contract.

**Naming hygiene exception (AP-25):** Naming hygiene is not a requirements debate. Before fleshing any stub, apply the AP-25 substitution test to every identifier the stub introduces or names: *if the plan declares a concept as multi-valued (a set, enum, list of equivalents, or configurable abstraction), does this identifier still make sense if a different member of that set is substituted?* If the answer is no — the name only makes sense for one specific member — it fails the test. Annotate the ticket draft with `[NAMING: AP-25 — '<ident>' couples to a single instantiation of '<abstraction>'; the name should describe the role, not the member]`. This annotation is not a hard block but must not be silently omitted. Do not copy a self-contradicting name from the PRD into a ticket AC without surfacing it here.

**Refactor mode:** If the request is a refactor ("refactor X", "clean up Y", "restructure Z", "RFC"), load [`REFACTOR_MODE.md`](REFACTOR_MODE.md) and follow its interview process instead of the three-section output below.

---

## Output format

Produce three sections in order. Do not skip any section. Do not merge them.

---

### Ticket Stage Header Contract (mandatory for `.tickets/*.md` outputs)

When the output is a ticket file, include a YAML header and use the canonical stage field:

```yaml
---
Stage: BUILD
---
```

Use `Stage:` (not `Status:`) for canonical routing.
Allowed stage enum (single line): `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
When a ticket is implementation-ready, set **exactly** `Stage: BUILD`.

---

### Section summary

Full templates, field lists and rules: read [`references/ticket-template.md`](./references/ticket-template.md) before drafting or editing any ticket body.

- **SECTION 1: SPEC** (mandatory): purpose, users/use cases, requirements, IN/OUT scope, edge cases, Given/When/Then ACs. Turn vague verbs into measurable targets. Mark every unstated decision `[ASSUMPTION: ...]`.
- **SECTION 2: PLAN**: stack, data model, API contracts, patterns, a per-AC Test Obligation Profile table (consumed by `/tdd`), security/performance, failure paths for `[FALLIBLE_IO]`, ADRs and design alternatives. Test files use permanent committed paths.
- **SECTION 3: TASKS**: ordered atomic tasks, one primary source file each, producers before consumers, 1-3 binary ACs, a mandatory **Docs to update** line, then a **Review checkpoint**. Slice vertically; split XL tasks.


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

## Author-side brief audit (mandatory before subagent delegation)

Before delegating any ticket to a subagent, run the audit in `references/brief-audit.md` and
fix every finding in the ticket body. Do not delegate a ticket that fails it.

## Quality rules

- Ticket files must include canonical YAML header with `Stage:`. For implementation-ready tickets generated by this skill, write `Stage: BUILD` and keep stage values within: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
- **SPEC is mandatory** (Section 1). Skipping it causes invented design; keep it technology-agnostic — no framework names, no library choices, no implementation details in requirements.
- **Size thresholds trigger refactoring**: If a planned change causes any file to exceed **300 lines** (or 500 lines for well-structured modules), the plan **must include a refactoring step** as a first-level acceptance criteria. See [ANTIPATTERNS.md](./ANTIPATTERNS.md) for common patterns to avoid.
- **Avoid antipatterns**: Before finalizing any spec, check [ANTIPATTERNS.md](./ANTIPATTERNS.md) to ensure the plan doesn't introduce known code smells.
- **Deploy-time ACs (container / helm / k8s tickets)** ([`references/deploy-time-acs.md`](./references/deploy-time-acs.md)): Before finalizing any ticket whose `Files:` list touches `Dockerfile`, `helm/**/*.yaml`, or a `*-entry.sh` / `start-*.sh` / `entrypoint*.sh` / `docker-entrypoint*` script, apply the three deploy-time AC conventions (helm install --wait smoke; Read-First on base-image write paths; NetworkPolicy cross-pod probe + namespace-label setup). `helm lint` PASS is not deploy proof. Cross-referenced with `ticket-critic` patterns 11/12/13.
- **Run prose through stop-slop**: After generating Section 1 (SPEC) prose and all assumption descriptions, invoke `/stop-slop` to remove AI writing patterns and filler. The final spec must be direct and precise.
- **Artifact + naming hygiene** ([`references/artifact-hygiene.md`](./references/artifact-hygiene.md)): no cycle/gate/ticket IDs in committed paths or filenames; no vendor/runtime tokens in supposedly-agnostic identifiers; no internal-label drops in docstrings or doc prose; every ticket includes a mandatory `## Docs to Update` checklist enumerating every doc, diagram, README, runbook, and env-example that mentions the surface being changed; review-time codes (`F-NN`, `RISK-NN`, `Pattern N`) live in commit messages and PR threads, never in committed prose.
- The plan must be concrete. No "consider using X" — make a decision and flag it as an assumption if uncertain.
- Every task must be independently deployable or testable. If a task can't be verified on its own, split it.
- Acceptance criteria must be binary. "Works correctly" is not a criterion. "Returns 401 when unauthenticated" is.
- Never write a task that says "implement the feature." That's the whole spec. Tasks are the pieces.
- Align outputs with **PDCA-T** ([METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md)): **Plan** before code; **Do** in small tasks; **Check** against criteria and runs; **Act** via assumptions and ADR updates; **Test** as a first-class gate (strategy in PLAN, proof in TASK acceptance). Keep **traceability**: requirements / FRs → tasks → tests via the assumptions summary and explicit criteria.
- When project rules or skills exist, **cite them** in PLAN (patterns) and TASKS (constraints) so execution stays unambiguous.

---

## Example

Worked examples (additive Python ticket and generic CSV-export feature): read [`EXAMPLE.md`](./EXAMPLE.md) when you need a concrete output shape.
