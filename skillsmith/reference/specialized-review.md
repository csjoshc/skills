# Specialized Review Reference

Source: `https://jdforsythe.github.io/10-principles/principles/specialized-review/`

## Contents

- Principle summary
- Requirements for review skills
- Specialist lens template
- Required output behavior

## Principle Summary

Generalist review underperforms specialist review for high-stakes quality gates.
Review quality improves when each reviewer is scoped to a specific domain with domain vocabulary.

## Requirements for Review Skills

1. Use specialist lenses.
- Define explicit domains (for example: security, performance, accessibility, reliability).
- Avoid single-pass "review everything" behavior.

2. Use concise, real specialist roles.
- Role framing should be brief and domain-specific.
- Prioritize vocabulary used by senior practitioners in that domain.

3. Require deterministic checks first.
- Run build/lint/test/static checks before LLM critique when available.

4. Require evidence-based findings.
- Every finding must cite concrete evidence (file, line, command output, behavior trace).
- Reject bare approvals like "LGTM" without support.

5. Separate generation and review roles.
- The agent that writes code should not be the sole reviewer of that code.

## Specialist Lens Template

Use this template when authoring review skills:

- Lens name: `<domain>`
- Role: `<short job title>`
- Vocabulary anchors: 15-30 domain terms
- Anti-pattern list: 5-10 named anti-patterns
- Deterministic checks: required tools/commands
- Output contract: severity, evidence, required remediation

## Required Output Behavior

Review outputs should include:

1. Findings ordered by severity.
2. Evidence for each finding.
3. Explicit pass/fail criteria per lens.
4. Residual risks and uncovered areas.

