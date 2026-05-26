# Execution Templates

Long prompt templates extracted from `SKILL.md` to satisfy the
500-line body budget. The dispatcher in `SKILL.md` references these
sections by name; when emitting a prompt, /todo inlines the full
template into the user-facing output.

## Contents

- build-ticket-manual — per-ticket flow without Orchestra
- build-ticket-resume — pick up a Stage: BUILD ticket mid-flight
- slice-gate-review — gate closure with subagent-validated review

---

## build-ticket-manual

For users executing tickets without Orchestra. Single-session per ticket
using `/tdd` for red-green-refactor and `/verify-claim` as the evidence
gate before commit. Subagents are reserved for slice gates, not per-ticket.

```
You are implementing one ticket from a planned multi-slice rebase. The
ticket file is the source of truth; the PRD and task-sequence are
read-only context.

**Ticket file:** <absolute path to .tickets/<NNN-slug>.md>
**PRD:** <absolute path to .plan/PRD.md>
**Task-sequence (DAG + Reconciliation notes):** <absolute path to .plan/task-sequence.md>
**Brownfield context (if present):** <absolute path to .plan/brownfield-context.md>

**Execution flow (do these in order, in THIS session):**

1. Read the ticket file end to end. Read its `Read First` files. Read
   any `Exemplar Files` it points at.
2. Set the ticket's frontmatter `Stage: BUILD` (edit the file directly).
3. Invoke /tdd. Phase 0 writes the Test Obligation Queue at
   .tickets/tdd/toq-<ticket-id>.yaml. Phase 1 runs red-green-refactor
   against the ticket's ACs one at a time. Do NOT skip Phase 0.
4. When all ACs are green per /tdd, invoke /verify-claim. It will
   require: passing test log, grep-verifiable AC output, and (for
   bug-fix tickets) a regression test. Do not declare done until
   /verify-claim passes.
5. Run the project's lint + typecheck commands. Fix any issues.
6. Stage and commit using the project's commit conventions (see
   AGENTS.md / CLAUDE.md). Commit message references the ticket ID.
7. Set the ticket's frontmatter `Stage: COMPLETE`. Commit that change.
8. STOP. Do not start the next ticket in this session — invoke /clear
   first, then run /todo to get the next prompt.

**Subagent escalation (exception, not default):** If the ticket touches
adversarial-review-worthy code (audit logging, auth, transport plumbing,
data-deletion flows), invoke /pr-review as a subagent BEFORE step 6.
Otherwise skip — per-ticket subagent review is not the default flow.

**If /tdd or /verify-claim refuses to pass:** stop, do not commit, do
not flip Stage to COMPLETE. Document the blocker in the ticket's
"Failure Protocol" section and surface it to the user.
```

---

## build-ticket-resume

```
You are resuming a ticket whose `Stage: BUILD` was set in a prior
session that ended without reaching COMPLETE. Artifacts on disk are
the source of truth.

**Ticket file:** <absolute path to .tickets/<NNN-slug>.md>
**TOQ (if exists):** <absolute path to .tickets/tdd/toq-<id>.yaml>
**PRD:** <absolute path to .plan/PRD.md>
**Task-sequence:** <absolute path to .plan/task-sequence.md>

**Resume protocol:**

1. Read the ticket file. Read the TOQ if it exists. If no TOQ exists,
   the prior session pre-dated /tdd Phase 0 — invoke /tdd Phase 0 now
   to scope before continuing.
2. Run `git diff <main-branch>...HEAD` (or `git log --since=<prior session>`)
   to see what's already been written. Map each diff against the
   ticket's ACs to identify which ACs are already green vs. still red.
3. If TOQ has a `diff_base` field, compare against current HEAD. If
   HEAD has advanced past `diff_base`, re-scope before continuing
   (the staleness warning).
4. Run the test suite. Capture which tests pass and fail.
5. Resume /tdd at the first un-green AC. Continue red-green-refactor.
6. After all ACs green, follow steps 4-7 of the build-ticket-manual
   template (verify-claim, lint, commit, Stage: COMPLETE, stop).

Do not re-derive the ticket scope or rewrite already-passing code.
```

---

## slice-gate-review

For when every non-gate ticket in a slice is COMPLETE and the gate
ticket itself is NEW. The gate is where subagent review earns its cost.

```
You are reviewing slice <slice-id> for integration-gate closure. Every
non-gate ticket in this slice is `Stage: COMPLETE`; the gate ticket is
`Stage: NEW` and pending review.

**Gate ticket:** <absolute path to .tickets/<gate-id>.md>
**Slice tickets (all COMPLETE):**
  <bullet list of every non-gate ticket in the slice with absolute paths>
**PRD parity gate:** .plan/PRD.md §10 (per-slice closure criteria)
**Demo regression policy:** .plan/PRD.md §14
**Reconciliation notes:** .plan/task-sequence.md "Phase 3 Reconciliation"
  and "Spec-writer follow-ups" sections

**Two-pass review (do these IN ORDER):**

### Pass 1 — Main session: collect gate artifact

Per the gate ticket's `Proof Artifacts` section, produce the required
artifact (e.g., for Slice 1: MCP transcript + curl headers + audit log
line). Save the artifact to a path referenced in the gate ticket
(typically `.plan/gate-evidence/<slice-id>/`).

### Pass 2 — Subagent: independent gate review

Launch a /pr-review subagent (general-purpose) with this prompt:

  > You are an independent gate reviewer. You have NO context from prior
  > conversations. Read each path below cold:
  > - Gate ticket: <path>
  > - Gate artifact (just collected): <path>
  > - Each slice ticket file: <list of paths>
  > - PRD parity gate: .plan/PRD.md §10
  >
  > Verify, with verbatim quotes from the artifact:
  > 1. Every gate-ticket AC is satisfied by named evidence in the artifact.
  > 2. Every slice-ticket AC that the gate validates appears in the artifact.
  > 3. The artifact runs against REAL services (no mocks per AP-5).
  > 4. The demo flow named in PRD §14 succeeds end-to-end.
  > 5. No silent-failure suppression (AP-10): error paths in the slice
  >    tickets have visible assertions, not just "no exception thrown."
  >
  > Output VERDICT: PASS | FAIL with per-AC evidence citations. If FAIL,
  > name the specific AC and missing evidence. Do not propose fixes.

### Pass 3 — Disposition

- Subagent VERDICT: PASS → flip gate ticket Stage to COMPLETE, commit
  evidence, advance to next slice.
- Subagent VERDICT: FAIL → flip gate ticket back to a diagnostic state;
  return failing ACs to the relevant slice tickets (re-open them as
  NEW with specific remediation notes); do NOT proceed to next slice.

Per PRD Constitution §5: "A slice closes only when the existing demo
flow works end-to-end on the rebased code. Demo regression blocks
merge." Gate failure is non-negotiable.
```
