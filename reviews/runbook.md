# Review runbook

Fixed phase sequence that both `pr-review` and `cleanup` follow. Modeled on
antiplan's phase-gate pattern — the sequence is not negotiable; only the
*content* inside each phase is LLM-generated.

## Contents

- Phase sequence
- Gate criteria
- Skill-specific deviations
- Validator invocation

---

## Phase sequence

```
┌──────────┐     ┌──────────┐     ┌─────────┐     ┌──────┐
│ phase-0  │ ──► │ phase-1  │ ──► │ report  │ ──► │ post │
│ mechanic │     │ lens /   │     │ ledger  │     │ gh   │
│ tools    │     │ rubric   │     │ + gate  │     │ api  │
└──────────┘     └──────────┘     └─────────┘     └──────┘
     │                │                │              │
 REVIEW-        REVIEW-           REVIEW-        validator
 PHASE-0       FINDINGS          LEDGER           exit 0
     │                │                │              │
 REVIEW-GATE   REVIEW-GATE      REVIEW-GATE       (pr-review
 phase-0→1    phase-1→report   report→post        only)
```

### Phase 0 — mechanical pass

- **cleanup**: run the deterministic tool matrix (ruff, eslint, vulture,
  ts-prune, madge, jscpd, etc.). Emit `REVIEW-PHASE-0` block. Every row is a
  `tool-flagged` source.
- **pr-review**: run pre-flight gh + deterministic checks (build/typecheck,
  project lint, layer-boundary-critic if imports changed). These findings
  are carried forward as `tool-flagged` entries when they surface in lens
  review.

Exit gate: `REVIEW-GATE: phase-0 → phase-1`. `Proceeding: no` if any
`status: OPEN` row remains without override.

### Phase 1 — lens or rubric application

- **cleanup**: apply rubric dimensions (M1–M12, Tier A–I) to files in scope.
  Source tag `rubric-derived`.
- **pr-review**: launch 5 specialist lenses with N-of-M checklist thresholds.
  Source tag `lens-derived`.

Both skills run a validation pass on each candidate finding (re-verify every
YES criterion independently) before admitting it to `REVIEW-FINDINGS`.

Exit gate: `REVIEW-GATE: phase-1 → report`. Criteria must include
`validation_pass: met`.

### Report — ledger emission

Emit `REVIEW-LEDGER` YAML. Compute counts mechanically from the
`REVIEW-FINDINGS` blocks:

- `findings_total` = sum of rows across all blocks.
- `validated` = count with `status: VALIDATED`.
- `dismissed` = count with `status: DISMISSED`.
- `deferred` = count with `status: DEFERRED`.
- `critical` = count of VALIDATED rows with `severity: CRITICAL`.
- `confidence`:
  - HIGH if validator passes and all CRITICAL have `proof:`.
  - MEDIUM if validator passes with warnings.
  - LOW otherwise.

### Post (pr-review only)

Before any `gh api` call, run `reviews/validate.py --transcript <transcript>`
on the assembled output. Only post if exit code is 0. Emit final
`REVIEW-GATE: report → post. Criteria: [validator exit 0: met]. Proceeding: yes.`

---

## Gate criteria

| Gate | Must verify | Fails if |
| --- | --- | --- |
| phase-0 → phase-1 | No OPEN rows in REVIEW-PHASE-0 | Any OPEN without override |
| phase-1 → report | Every finding validated independently | Any VALIDATED without evidence |
| report → post | Validator exit 0 | Ledger malformed, missing proof, wrong block order |

---

## Skill-specific deviations

- `pr-review` skips the standalone `REVIEW-PHASE-0` block — pre-flight tool
  output is folded directly into the lens findings with `source: tool-flagged`.
- `cleanup` skips `report → post` — cleanup does not post to GitHub. Its final
  gate is `phase-1 → report`.

---

## Validator invocation

```bash
python3 /Users/joshc/.skills/reviews/validate.py --transcript <path>
```

Exit codes:

- `0` — transcript is well-formed; safe to post/report.
- `1` — one or more checks failed; fix and re-run before posting.

Every failure is printed with a short diagnostic. The validator never edits
the transcript — it only accepts or rejects.
