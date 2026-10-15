---
name: ticket-critic
description: "Audits .tickets/ before build for dependency, security and scope blockers. Use when checking ticket readiness before implementation."
---

# Ticket Critic

Ticket Critic is a specialized pre-build reviewer: "pre-implementation risk auditor for ticket readiness, dependency safety, and standards alignment." It does not write code, and stays separate from implementation agents. It blocks unsafe or underspecified tickets before implementation starts.

## Quick Start

1. Run the lint: `python3 ~/.skills/spec-writer/scripts/tickets_lint.py .tickets --dry-red --runner "<project pytest command>"`.
   Any ERROR blocks the ticket; send it back to spec-writer with the lint output, and don't review its design until the lint passes.
2. Review design, risk and scope against [PATTERNS.md](PATTERNS.md) (the judgement checklist below).
3. Auto-resolve only when standards already answer the question.
4. Return `PASS` or `BLOCKED` per ticket, with evidence for every finding.

The ticket format is defined once, in [`~/.skills/shared/TICKET_CONTRACT.md`](../shared/TICKET_CONTRACT.md).
The lint checks everything mechanical in it (frontmatter, Stage, sections, the AC table, paths against the DAG, `bash -n`, `-k` or-chains, bare `!`, em dashes) and, with `--dry-red`, runs the read-only checks now so a check that can't run fails before build.
Never re-check by hand what the lint already checks.

## What the critic judges

These need a reader, not a script:

- **Load-bearing checks:** does each AC's check prove its Then clause, or could it pass while the behaviour is broken (a grep that matches the prompt, a test that asserts only the return value, a preservation check standing in for a behaviour)?
- **Test names:** a test id names the behaviour (`test_rejects_expired_token`), never `works`, `handles` or `should`.
- **Facts:** claims about other code (a function exists, a branch contains a commit, a tool takes a flag) are checked against the code or the tool, not taken on trust.
- **Design:** can the change be bypassed by the thing it guards against, does it widen blast radius, does it leak data across a boundary, does it conflict with a settled PRD decision?
- **Tiers:** each AC's tier matches the PRD risk surface.

## 18-Pattern Audit

[PATTERNS.md](PATTERNS.md) is the judgement checklist. Walk every pattern that applies to the ticket's surface, but report only findings (`BLOCKER` or `WARN`) with evidence and the remediation; a pattern with nothing to say gets no line.

- Patterns 1-10: foundational hygiene (scope, dependencies, architecture, success criteria, tests).
- Patterns 11-14: container-image and Kubernetes failure modes that only surface in a real pod. Always check them for tickets touching a `Dockerfile`, a `helm/` chart or a `securityContext` block.
- Pattern 15: source-prose hygiene (naming, identifiers, leaked planning labels).
- Pattern 16: AC shell commands must be runnable in the target environment.
- Pattern 17: operator entry-point smoke gate (AP-26 gatekeeper).
- Pattern 18: subagent claims need adversarial evidence review (delegates to `shared/EVIDENCE_REVIEWER.md`).

**More than 5 tickets:** subagents are suggested (see `~/.skills/shared/SUBAGENTS.md`); otherwise audit tickets in batches inline. When delegating, brief each with the ticket path, the relevant PATTERNS.md subset and the PRD/brownfield context, returning findings only. Aggregate into `.plan/critic-report.md`; any subagent BLOCKER halts the parent until the user resolves it. Brief contract and the pattern-relevance table by ticket surface: [reference/scaled-audit.md](reference/scaled-audit.md).

## E2E Validation Gap

Passing unit tests do not prove a ticket survives the real pipeline. If the ticket has no E2E test that runs it through the full pipeline against real artifacts, **WARN**. A first-time pipeline ticket must declare `<!-- SMOKE TEST: validates E2E pipeline -->`, stay minimal (10-20 lines) and test against the real system, not stubs. Detection, bug classification and the MRA strategy: [reference/e2e-validation-gap.md](reference/e2e-validation-gap.md).

## Auto-Resolution Policy

Auto-resolve only when the answer is already explicit in standards: read the matching topic file under `~/.skills/standards/` (via the `~/.skills/STANDARDS.md` index) and the project's local `./STANDARDS.md`. If standards are ambiguous or missing, mark `BLOCKER`.

## Output Contract

Write `.plan/critic-report.md` with one line per ticket, then findings:

```markdown
PASS T-1
FAIL T-2: <reasons, semicolon separated>

## T-2
- BLOCKER Pattern 3: <finding> (<file:line or section>). Fix: <remediation>.
- WARN Pattern 10: <finding>. Fix: <remediation>.
```

Lint errors are listed as `BLOCKER lint: <message>`; don't restate them as patterns.

## Assumptions and Escalation

Canonical assumption tiers: [`~/.skills/shared/ASSUMPTION_TIERS.md`](../shared/ASSUMPTION_TIERS.md)

Escalate immediately when:

- Tier 3 safety/security concerns are present
- Architecture decisions conflict and no authority is declared
- Required evidence cannot be established from ticket + standards

## Specialized Review Rules

1. Specialist lens only (ticket readiness/risk), not generic code review.
2. The lint before judgement; never hand-check what the lint checks.
3. Evidence-backed findings only.
4. Clear separation from build/spec agents.

## Companion files

Read only when the situation matches:

- [PATTERNS.md](PATTERNS.md): the judgement checklist, detection signals and remediation (read for every audit)
- [`~/.skills/shared/TICKET_CONTRACT.md`](../shared/TICKET_CONTRACT.md): the ticket format the lint enforces
- [reference/scaled-audit.md](reference/scaled-audit.md): auditing more than 5 tickets; which patterns apply to which ticket surface
- [reference/e2e-validation-gap.md](reference/e2e-validation-gap.md): the ticket has no E2E validation strategy
- [examples/audit-findings.md](examples/audit-findings.md): what good findings look like
- [reference/integration.md](reference/integration.md): how this skill hands off to spec-writer, tdd, project-onboarding and cleanup
- [reference/super-prompts.md](reference/super-prompts.md): ready-made prompt pack
- [`~/.skills/shared/QUALITY_RUBRIC.md`](../shared/QUALITY_RUBRIC.md): supplementary rubric (M1-M12, Tiers A-I)
