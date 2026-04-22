---
name: ticket-critic
description: Performs pre-implementation ticket audits to block high-risk work before build starts. Use when evaluating ticket readiness, validating Stage headers, or identifying dependency, security, and scope blockers before spec or code execution.
---

# Ticket Critic

Ticket Critic is a specialized pre-build reviewer. It does not write code. It blocks unsafe or underspecified tickets before implementation starts.

## Quick Start

1. Validate the `Stage:` header first.
2. Run deterministic ticket sanity checks.
3. Audit all 10 blocker patterns.
4. Auto-resolve only when standards already answer the question.
5. Return clear `PASS`, `AUTO-RESOLVED`, or `BLOCKED` verdict with evidence.

## Companion Files

- Pattern library: [PATTERNS.md](PATTERNS.md)
- Findings examples: [examples/audit-findings.md](examples/audit-findings.md)
- Cross-skill integration: [reference/integration.md](reference/integration.md)
- Prompt pack: [reference/super-prompts.md](reference/super-prompts.md)

## Role Definition

Use this concise specialist role:

- "Pre-implementation risk auditor for ticket readiness, dependency safety, and standards alignment."

Keep this role separate from implementation agents.

## Stage Header Gate (Mandatory)

Before pattern checks, verify metadata:

- Required fields: `Stage:`, `Ralph:`, `Ralph-Reason:`
- Allowed Stage enum: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`
- If implementation-ready, require exactly `Stage: BUILD`
- If `Ralph:` is present, validate it against [`~/.skills/shared/RALPH_DECISION_RULE.md`](~/.skills/shared/RALPH_DECISION_RULE.md)
  - `Ralph: true` requires all eligibility conditions met + no disqualifiers
  - `Ralph: false` requires disqualifier present (or explicit choice for small tickets)
  - Block if `Ralph-Reason:` is missing or vague

If missing or invalid, stop and block immediately.

## Deterministic Checks First

Run deterministic checks before subjective judgment:

1. Ticket file exists and is readable.
2. Header metadata is valid.
3. Declared dependencies are present or linked.
4. Referenced standards files are present:
- `~/.skills/STANDARDS.md`
- Local `./STANDARDS.md` (if project-local standards exist)
5. **AC→Test traceability table is present** (see below).

Only then run the 10-pattern review.

## AC → Test Traceability (Mandatory for Stage: BUILD)

Every acceptance criterion must name the test function or verification command that will verify it before the ticket can move to `Stage: BUILD`. The test does not have to exist yet — TDD's red phase is the correct place to create it — but the name, file, and behavior to be asserted must be chosen in advance. This is what prevents tautological tests: the assertion is committed before the implementation exists to copy from.

**Specific requirement for Ralph-eligible tickets:** Each AC must have a **machine-executable** verification command (grep, pytest -k, ruff check, etc.). If any AC has a manual or vague verification step, that AC violates Ralph eligibility and blocks the `Ralph: true` flag.

### Required section in every ticket

```markdown
## Acceptance Criteria → Tests

| AC | Test file / Command | Test name | Assertion shape |
|---|---|---|---|
| AC-1 Given a logged-in user, when they click "Save", then a toast appears | src/ui/__tests__/SaveButton.test.tsx | "shows toast on save" | `expect(screen.getByRole('alert'))` |
| AC-2 Given a 5xx response, retry up to 3 times | src/api/__tests__/retry.test.ts | "retries 3× on 5xx then throws" | counter-based mock |
| AC-3 Export CSV contains header row | `pytest -k test_csv_header` | "emits header as first line" | string match |
```

### Block conditions

- Any AC without a named test or command → **BLOCKED**
- Any test name matching `.*works.*`, `.*handles.*`, or `.*should.*` → **BLOCKED** (too vague; rename to describe the behavior)
- Any "Assertion shape" that is just `toBe(true)` → **BLOCKED** (describe what's being checked)
- Any test that exists but asserts only the return value of the function under test with no further condition → **WARN** (tautology risk; let mutation-critic decide on the implementation side)
- **(Ralph-specific)** Any AC with a manual verification step ("verify visually", "test manually") → **BLOCKED** if `Ralph: true` (machine-checkable ACs are load-bearing)

### Why this works

A test named and described before the implementation describes **user
intent**. A test written after the implementation describes **what the
code happens to do**. Locking the name and assertion shape at ticket
time forces the intent-first orientation.

## 10-Pattern Audit Workflow

Use [PATTERNS.md](PATTERNS.md) as the canonical checklist.

For each pattern:

1. Score it: `PASS`, `AUTO-RESOLVED`, or `BLOCKER`.
2. Include explicit evidence.
3. Provide required remediation for blockers.

Do not skip any pattern.

## Auto-Resolution Policy

Auto-resolve only when the answer is already explicit in standards.

- Global standards: `~/.skills/STANDARDS.md`
- Project standards: local `./STANDARDS.md`

If standards are ambiguous or missing, mark as `BLOCKER`.

## Output Contract

Return findings using this structure:

```markdown
## Ticket Critic Verdict
- Overall: PASS | PASS WITH AUTO-RESOLUTIONS | BLOCKED
- Stage Gate: PASS | BLOCKED
- Standards Checked: [global], [local]

## Pattern Results
- Pattern 1: PASS | AUTO-RESOLVED | BLOCKER
- Pattern 2: ...
- ...
- Pattern 10: ...

## Evidence
- [file/line/section and verification]

## Required Actions Before Build
- [ ] ...
- [ ] ...

## Risk Tier Summary
- Tier 1 assumptions:
- Tier 2 assumptions:
- Tier 3 assumptions:
```

## Assumptions and Escalation

Canonical assumption tiers: [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md)

Escalate immediately when:

- Tier 3 safety/security concerns are present
- Architecture decisions conflict and no authority is declared
- Required evidence cannot be established from ticket + standards

## Specialized Review Rules

This skill must follow specialist-review principles:

1. Specialist lens only (ticket readiness/risk), not generic code review.
2. Deterministic checks before LLM interpretation.
3. Evidence-backed findings only.
4. Clear separation from build/spec agents.

## E2E Validation Gap (The Hidden Blocker)

A ticket can pass all unit tests and still fail when run through a complex pipeline
(orchestration, deployment, integration).
This gap is not a bug in the ticket; it's a systems-level correctness issue that
must be caught **before** handoff to implementation.

### The Failure Pattern

- Thousands of unit tests pass locally ✓
- Single real ticket fails in pipeline ✗
- Root cause: Infrastructure assumptions (state, initialization, contracts), not application logic

### How to Detect the Gap

Audit the ticket's test strategy:

1. **Are there E2E tests that run the ticket through the full pipeline?**
   - If no: **WARN**. Unit tests verify implementation; they don't verify system-level correctness.
   - If yes: Ask — are they run on realistic conditions (branches, state, dependencies)?
     Are they testing actual artifacts or mocks?

2. **Classify test coverage:**

   | Coverage Type | What It Validates | When It Fails |
   |---|---|---|
   | Unit tests | Implementation logic in isolation | Never catches infrastructure issues |
   | Integration tests (local) | Multiple modules together | Never catches pipeline constraints |
   | E2E tests (real pipeline) | Full artifact through system | Catches infrastructure + integration + state bugs |

3. **If this is a first-time pipeline ticket (e.g., smoke test):**
   - Declare it as such in the ticket body: `<!-- SMOKE TEST: validates E2E pipeline -->`
   - Require a minimal implementation (10–20 lines of code max)
   - Ensure acceptance criteria test against the real system, not stubs

### Bug Classification Framework

When volume (many tests) conflicts with quality (single ticket fails):

| Bug Type | Indicator | Root Cause | Fix Owner |
|----------|-----------|-----------|-----------|
| **Application-level** | Fails in isolated unit test; fails locally | Implementation error | Builder/Developer |
| **Integration-level** | Passes unit tests; fails local integration test | Module contract mismatch | Architect/Developer |
| **Infrastructure-level** | Passes local tests; fails in real pipeline | State not initialized, contracts broken, assumptions violated | Architect/Infrastructure |

**Key insight:** If a ticket passes all *local* tests but fails in the *real* pipeline, the
root cause is infrastructure, not application code.

### Minimal Reproducible Artifact (MRA) Strategy

When debugging pipeline failures:

1. Create the **simplest possible ticket** that exercises the same failure mode
   - Minimal code (10–20 lines)
   - Minimal dependencies
   - Isolated to a single concern

2. Run it through the **real pipeline** (not unit tests or stubs)

3. Classify the result:
   - **Fails in MRA**: Root cause is infrastructure/system-level. Fix there first.
   - **Passes in MRA, fails in complex ticket**: Root cause is interaction/state. Debug systematically.
   - **Both pass**: Root cause may be load, timing, or environmental. Escalate.

4. After infrastructure is proven correct, re-run the full ticket suite.

### Required Remediation

If a ticket lacks E2E validation strategy:

- [ ] Document whether this is a smoke test or a regular feature ticket
- [ ] If regular: list any existing E2E tests. If none exist, escalate for architecture review.
- [ ] If smoke test: ensure the implementation is minimal and acceptance criteria test against the real system
- [ ] If this is the first ticket of a new feature area: require it to be an MRA (minimal) to prove the pipeline infrastructure works before scaling to complexity

## Maintenance

- Keep SKILL.md as routing + execution contract.
- Keep pattern depth in [PATTERNS.md](PATTERNS.md).
- Keep examples in [examples/audit-findings.md](examples/audit-findings.md).
