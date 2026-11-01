# Review runbook

Fixed phase sequence that both `pr-review` and `cleanup` follow. Modeled on
challenge's phase-gate pattern — the sequence is not negotiable; only the
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
HIGH or CRITICAL row is still `status: OPEN`. LOW/MEDIUM rows may stay OPEN;
they are reported, not gated.

### Phase 1 — lens or rubric application

- **cleanup**: apply rubric dimensions (M1–M12, Tier A–I) to files in scope.
  Source tag `rubric-derived`.
- **pr-review**: launch 5 specialist lenses with N-of-M checklist thresholds.
  Source tag `lens-derived`.

Both skills run a validation pass on each candidate finding (re-verify every
YES criterion independently) before admitting it to `REVIEW-FINDINGS`.
pr-review additionally runs the independent re-check (Local Mode section of
`reference/review-operations.md`): a harness subagent with a different chat
model, or at minimum fresh context with no view of this session's
conclusions, re-derives each verdict and verifies proof targets. Any
`OVERRULE` downgrade is recorded; a skipped re-check caps ledger confidence
at MEDIUM. This attack on the same-author-same-model correlation problem is
complementary to validate.py: the script gates shape deterministically, the
subagent is the unanchored second opinion on substance.

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

### Disposition (pr-review only)

Give every VALIDATED finding a disposition before report → post. FIX
(mechanical, unambiguous, localized blast radius) is applied to the working
tree with `pr-fix` safety rules and collected in a `REVIEW-FIXED` block;
COMMENT (open questions only) is carried forward to post/report. See
pr-review → Fix-first disposition. `cleanup` has no disposition step; it
never writes to GitHub and reports findings as-is.

### Post (pr-review only)

Only COMMENT-disposition findings reach this phase.
Before any `gh api` call, run `reviews/validate.py --transcript <transcript>`
on the assembled output. Only post if exit code is 0. Emit final
`REVIEW-GATE: report → post. Criteria: [validator exit 0: met]. Proceeding: yes.`

---

## Gate criteria

| Gate | Must verify | Fails if |
| --- | --- | --- |
| phase-0 → phase-1 | No OPEN HIGH/CRITICAL rows in REVIEW-PHASE-0 | Any OPEN HIGH/CRITICAL without override |
| phase-1 → report | Every finding validated independently | Any VALIDATED without evidence |
| report → post | Validator exit 0 | Ledger malformed, missing proof, wrong block order |

---

## Skill-specific deviations

- `pr-review` skips the standalone `REVIEW-PHASE-0` block — pre-flight tool
  output is folded directly into the lens findings with `source: tool-flagged`.
- `cleanup` skips `report → post` — cleanup does not post to GitHub. Its final
  gate is `phase-1 → report`.
- `pr-review` local mode skips `report → post` the same way; validate with
  `--local`.

---

## Validator invocation

```bash
python3 ~/.skills/reviews/validate.py --transcript <path>
```

Exit codes:

- `0` — transcript is well-formed; safe to post/report.
- `1` — one or more checks failed; fix and re-run before posting.

Every failure is printed with a short diagnostic. The validator never edits
the transcript — it only accepts or rejects.
