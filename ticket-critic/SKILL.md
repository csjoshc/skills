---
name: ticket-critic
description: "Audits .tickets/ before build for dependency, security and scope blockers. Use when checking ticket readiness before implementation."
---

# Ticket Critic

Ticket Critic is a specialized pre-build reviewer: "pre-implementation risk auditor for ticket readiness, dependency safety, and standards alignment." It does not write code, and stays separate from implementation agents. It blocks unsafe or underspecified tickets before implementation starts.

## Quick Start

1. Validate the `Stage:` header first.
2. Run the deterministic checks.
3. Audit all 18 patterns in [PATTERNS.md](PATTERNS.md).
4. Auto-resolve only when standards already answer the question.
5. Return `PASS`, `PASS WITH AUTO-RESOLUTIONS` or `BLOCKED` with evidence.

## Stage Header Gate (Mandatory)

Before pattern checks, verify metadata:

- Required field: `Stage:`
- Allowed values: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`
- If implementation-ready, require exactly `Stage: BUILD`

If missing or invalid, stop and block immediately.

## Deterministic Checks First

Run these before subjective judgment:

1. Ticket file exists and is readable.
2. Header metadata is valid.
3. Declared dependencies are present or linked.
4. Standards are reachable: `~/.skills/STANDARDS.md` (a thin index; topic files in `~/.skills/standards/`) and the local `./STANDARDS.md` if the project has one.
5. The AC→Test traceability table is present (next section).

Only then run the 18-pattern audit.

## AC → Test Traceability (Mandatory for Stage: BUILD)

Every ticket carries an `## Acceptance Criteria → Tests` table with columns `AC | Test file / Command | Test name | Assertion shape | Risk Tier`. Each AC must name its test or verification command before `Stage: BUILD`; the test need not exist yet. Template and rationale: [reference/ac-test-traceability.md](reference/ac-test-traceability.md).

Block conditions:

- Any AC without a named test or command → **BLOCKED**
- Any test name matching `.*works.*`, `.*handles.*`, or `.*should.*` → **BLOCKED** (too vague; rename to describe the behavior)
- Any "Assertion shape" that is just `toBe(true)` → **BLOCKED** (describe what's being checked)
- Any test that exists but asserts only the return value of the function under test with no further condition → **WARN** (tautology risk; let mutation-critic decide on the implementation side)
- **Risk Tier missing** on any row → **BLOCKED** (spec-writer Test Obligation Profile is incomplete; send back to spec-writer, do not patch in the critic)
- **T1 AC with no concrete target** (Test file / Command is vague or points at a non-existent file the ticket does not create) → **BLOCKED** (T1 ACs must be load-bearing; /tdd Phase 0 cannot score what it cannot locate)
- `Test file / Command` cell contains `tests/tickets/` → **BLOCKED** (deprecated gitignored staging area; specify the permanent destination: `tests/infra/`, `tests/docs/`, or `packages/<pkg>/tests/`)

The Risk Tier column feeds `/tdd` Phase 0 scoping and mirrors the ticket's Test Obligation Profile (spec-writer output). The critic enforces that the mirror is honest; it does not re-derive tiers.

## 18-Pattern Audit

[PATTERNS.md](PATTERNS.md) is the canonical checklist. Score every pattern `PASS`, `AUTO-RESOLVED` or `BLOCKER` with explicit evidence, and give required remediation for each blocker. Do not skip any pattern.

- Patterns 1-10: foundational hygiene (scope, dependencies, architecture, success criteria, tests).
- Patterns 11-14: container-image and Kubernetes failure modes that only surface in a real pod. Always check them for tickets touching a `Dockerfile`, a `helm/` chart or a `securityContext` block.
- Pattern 15: source-prose hygiene (naming, identifiers, leaked planning labels).
- Pattern 16: AC shell commands must be runnable in the target environment.
- Pattern 17: operator entry-point smoke gate (AP-26 gatekeeper).
- Pattern 18: subagent claims need adversarial evidence review (delegates to `shared/EVIDENCE_REVIEWER.md`).

**More than 5 tickets:** subagents are suggested (see `~/.skills/shared/SUBAGENTS.md`); otherwise audit tickets in batches inline. When delegating, brief each with the ticket path, the relevant PATTERNS.md subset and the PRD/brownfield context, returning one verdict block per pattern. Aggregate into `.plan/critic-report.md`; any subagent BLOCKER halts the parent until the user resolves it. Brief contract and the pattern-relevance table by ticket surface: [reference/scaled-audit.md](reference/scaled-audit.md).

## E2E Validation Gap

Passing unit tests do not prove a ticket survives the real pipeline. If the ticket has no E2E test that runs it through the full pipeline against real artifacts, **WARN**. A first-time pipeline ticket must declare `<!-- SMOKE TEST: validates E2E pipeline -->`, stay minimal (10-20 lines) and test against the real system, not stubs. Detection, bug classification and the MRA strategy: [reference/e2e-validation-gap.md](reference/e2e-validation-gap.md).

## Auto-Resolution Policy

Auto-resolve only when the answer is already explicit in standards: read the matching topic file under `~/.skills/standards/` (via the `~/.skills/STANDARDS.md` index) and the project's local `./STANDARDS.md`. If standards are ambiguous or missing, mark `BLOCKER`.

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
- Pattern 18: ...

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

Canonical assumption tiers: [`~/.skills/shared/ASSUMPTION_TIERS.md`](../shared/ASSUMPTION_TIERS.md)

Escalate immediately when:

- Tier 3 safety/security concerns are present
- Architecture decisions conflict and no authority is declared
- Required evidence cannot be established from ticket + standards

## Specialized Review Rules

1. Specialist lens only (ticket readiness/risk), not generic code review.
2. Deterministic checks before LLM interpretation.
3. Evidence-backed findings only.
4. Clear separation from build/spec agents.

## Companion files

Read only when the situation matches:

- [PATTERNS.md](PATTERNS.md): the 18-pattern checklist, detection signals and remediation (read for every audit)
- [reference/ac-test-traceability.md](reference/ac-test-traceability.md): the AC→Test table template and rationale
- [reference/scaled-audit.md](reference/scaled-audit.md): auditing more than 5 tickets; which patterns apply to which ticket surface
- [reference/e2e-validation-gap.md](reference/e2e-validation-gap.md): the ticket has no E2E validation strategy
- [examples/audit-findings.md](examples/audit-findings.md): what good findings look like
- [reference/integration.md](reference/integration.md): how this skill hands off to spec-writer, tdd, project-onboarding and cleanup
- [reference/super-prompts.md](reference/super-prompts.md): ready-made prompt pack
- [`~/.skills/shared/QUALITY_RUBRIC.md`](../shared/QUALITY_RUBRIC.md): supplementary rubric (M1-M12, Tiers A-I)
