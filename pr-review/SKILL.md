---
name: pr-review
description: >-
  Reviews pull requests using specialist lenses for bugs, standards, error
  handling, tests, and scope traceability. Use when reviewing pull requests,
  preparing review feedback, or posting GitHub PR comments. Applies
  deterministic pre-flight checks, criteria-based issue filters, and
  evidence-backed findings rather than subjective scoring.
---

# pr-review

Reviews pull requests with specialist review lenses and criteria-based
checklists. Every reported issue must pass an explicit binary checklist.

Use this skill for live PR review and GitHub review comments. For local
codebase audits not tied to a pull request, use `cleanup`.

## Contents

- When to use
- Invocation
- Workflow summary
- Output contracts
- Mandatory companions
- Scope boundary
- Output rules

---

## When to Use

- Reviewing an open pull request
- Preparing code review feedback before posting
- Auditing a PR diff for bugs, standards, tests, error handling, or scope drift
- Posting inline PR comments and a summary review

Do not use for:

- Full codebase audits unrelated to a PR → use `cleanup`
- Editing ticket/spec markdown → use `ticket-critic`

---

## Invocation

```bash
/pr-review <owner/repo> <pr-number>
```

If already on the PR branch, detect repo and PR automatically via `gh pr view`.

---

## Workflow Summary

1. Run pre-flight checks and fetch the PR context.
2. Gather standards from `reference/review-standards.md` and repo-local policy files.
3. Run deterministic checks before LLM critique when available.
4. Launch specialist review lenses from `reference/review-lenses.md`.
5. Validate, deduplicate, and sort findings into `REVIEW-FINDINGS` blocks.
6. Emit `REVIEW-LEDGER` and `REVIEW-GATE: report → post`.
7. Run `python3 ~/.skills/reviews/validate.py --transcript <draft>`; exit 0
   required before posting.
8. Post inline comments and a summary using `reference/review-operations.md`.

Do not expand the full lens definitions or posting templates here. Load the
companions below.

---

## Output Contracts

Every `/pr-review` session emits, in order:

1. One or more `REVIEW-FINDINGS` fenced blocks (schema in
   [`~/.skills/reviews/schemas.md`](../reviews/schemas.md)).
2. `REVIEW-GATE: phase-1 → report. Criteria: [...]. Proceeding: yes.`
3. `REVIEW-LEDGER` YAML summarizing counts and confidence.
4. `REVIEW-GATE: report → post. Criteria: [validator exit 0: met]. Proceeding: yes.`

Findings use `source: lens-derived` (or `tool-flagged` for pre-flight
results folded in). Structural findings require a `proof:` field — a
reproducible command, failing test, curl, or CI link. The rule fires on
`severity: CRITICAL` (any category), `category: Architectural Drift`,
or `category: Layer` at `HIGH`/`CRITICAL`. The validator at
[`~/.skills/reviews/validate.py`](../reviews/validate.py) blocks
posting without it.

Fixed phase sequence is documented in
[`~/.skills/reviews/runbook.md`](../reviews/runbook.md).

---

## Mandatory Companions

| File                                                       | Role                                                                    | Load when        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------- |
| [`reference/review-lenses.md`](reference/review-lenses.md)         | Specialist agents, checklists, validation, output format                | Every invocation |
| [`reference/review-standards.md`](reference/review-standards.md)   | Standards cited by the standards compliance lens                        | Every invocation |
| [`reference/review-operations.md`](reference/review-operations.md) | Pre-flight, commands, posting flow, C3 handling, traceability execution | Every invocation |
| [`../reviews/schemas.md`](../reviews/schemas.md)                   | Fenced-block schemas + source-tag rules                                 | Every invocation |
| [`../reviews/runbook.md`](../reviews/runbook.md)                   | Fixed phase sequence shared with cleanup                                | Every invocation |
| [`../reviews/validate.py`](../reviews/validate.py)                 | Pre-post validator (stdlib-only)                                        | Before posting   |
| [`../reviews/arch-violations/`](../reviews/arch-violations/)       | Architectural-violation catalog (11 files; index in README.md)          | Lens 6 runs      |

---

## Scope Boundary

| In scope                           | Out of scope                             |
| ---------------------------------- | ---------------------------------------- |
| PR diff review                     | Full repo health audit                   |
| GitHub inline comments             | Ticket editing                           |
| Code-review findings with evidence | Generic “LGTM” approval without evidence |

---

## Output Rules

- Every finding must cite concrete evidence from changed code.
- Every finding must pass its lens checklist threshold.
- Findings are ordered by severity/category after deduplication.
- Every posted PR comment ends with:

```markdown
---

_Generated by Claude_
```
