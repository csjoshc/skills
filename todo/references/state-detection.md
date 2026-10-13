# State Detection

Full state-detection reference for `/todo`: the artifact map, stage inference rules, and staleness warnings.

## Contents

- Artifact paths and what they mean
- Stage inference rules (fresh through all-complete), including the dag-done validator gate
- Staleness warnings (non-blocking)

## Artifact paths

Scan the repo root (from the current working directory) for these paths:

| Path | Meaning |
| --- | --- |
| `.plan/brownfield-context.md` | antiplan Phase 0 done (brownfield) |
| `.plan/PRD.md` | antiplan Phases 1–2 done |
| `.plan/task-sequence.md` | antiplan Phase 3 done |
| `.plan/challenger-report.md` | antiplan Phase 3 Challenger subagent ran (per-AP audit table; option-3 evidence) |
| `.plan/coverage-audit.md` | antiplan Phase 3.5 Coverage Auditor ran (transcript-vs-PRD diff; option-4 evidence) |
| `.tickets/*.md` | spec-writer has run |
| `.plan/critic-report.md` | ticket-critic has run |
| Any `.tickets/*.md` frontmatter with `Stage: BUILD` | a ticket build has started |
| Any `.tickets/*.md` frontmatter with `Stage: COMPLETE` | a ticket build has finished |
| `.tickets/tdd/toq-<ticket-id>.yaml` | /tdd Phase 0 has scoped this ticket |

Use `Glob` for path discovery and `Read` (or `Grep` on `Stage:`) for
frontmatter inspection. Do **not** use Bash for this — Glob/Grep are faster
and quieter.

## Stage inference rules

- **fresh** — none of the above paths exist → recommend `/todo start`
- **phase-0-done** — only `brownfield-context.md` exists → recommend
  resuming antiplan into Phase 1
- **prd-done-no-dag** — `PRD.md` exists but no `task-sequence.md` → recommend
  resuming antiplan into Phase 3
- **dag-done-no-audits** — `task-sequence.md` exists but
  `.plan/challenger-report.md` is missing OR (Standard/Heavy run)
  `.plan/coverage-audit.md` is missing → recommend resuming antiplan to
  run Phase 3 Challenger and/or Phase 3.5 Coverage Auditor. The plan is
  NOT ready for spec-writer — the per-AP audit + transcript-vs-PRD diff
  are the final pass. Light-mode plans may skip coverage-audit.md if the
  task-sequence.md transcript explicitly emits
  `COVERAGE-AUDIT: skipped — Light classification`.
- **dag-done** — `task-sequence.md` + `challenger-report.md` (+
  `coverage-audit.md` for Standard/Heavy) all present; no `.tickets/*.md` →
  **first** ask the user to run antiplan's pre-flight validator with all
  evidence flags:
  ```
  python ~/.skills/antiplan/validate.py \
    --project-dir . \
    --tickets .plan/task-sequence.md \
    --prd .plan/PRD.md \
    --challenger-report .plan/challenger-report.md \
    --coverage-report .plan/coverage-audit.md
  ```
  Drop `--coverage-report` only if the task-sequence/transcript declared
  `COVERAGE-AUDIT: skipped — Light classification`.
  - exit 0 → recommend spec-writer session (emit spec-writer-next template)
  - non-zero → recommend antiplan-resume instead; the plan is not ready
    for fan-out. Common failures: missing AP rows in challenger-report,
    short evidence on a BLOCK row, GAP/INVERTED in coverage-audit, or
    `RE_DERIVED < 5` (Coverage Auditor likely skimmed the transcript).
- **tickets-written-uncriticized** — `.tickets/*.md` exist; no
  `critic-report.md`, or critic-report.md older than any `.tickets/*.md` →
  recommend ticket-critic session
- **critic-failed** — critic-report.md contains the literal string `FAIL` →
  recommend fix-cycle: return to spec-writer for failing tickets
- **ready-for-build** — critic-report.md passes; some tickets still
  `Stage: NEW` → recommend `/todo build` (manual, one ticket per
  session) or `/todo run` (auto-driver) for the next `NEW` ticket. Bare `/todo` may
  ask which mode the user prefers if it's the first build session.
- **slice-gate-pending** — within a slice, every non-gate ticket is
  `Stage: COMPLETE` and exactly one gate ticket (0G/1G/2G/3G or any
  ticket with `gate: true` in frontmatter) is `Stage: NEW` → recommend
  `/todo gate <slice-id>` (subagent-validated review) before flipping
  the gate to BUILD/COMPLETE.
- **mid-build-resume** — exactly one ticket is `Stage: BUILD` AND no
  active session is running it (heuristic: invoked from a fresh /todo
  call with no in-conversation evidence of the build). Recommend
  `/todo resume` to pick up where the prior session left off.
- **partial-build** — some `Stage: BUILD` or `Stage: COMPLETE` → recommend
  continuing with `/todo build` or `/todo run` for remaining `NEW` tickets
- **build-unscoped** — a ticket is `Stage: BUILD` but no matching
  `.tickets/tdd/toq-<id>.yaml` exists → recommend invoking `/tdd` Phase 0
  before continuing the cycle (this catches BUILD sessions that were
  started before TOQ scoping was adopted)
- **all-complete** — every ticket `Stage: COMPLETE` → announce the
  pipeline is done

To show ticket state over days or sprints, run `/trackboard refresh`.

## Staleness warnings (non-blocking)

- `PRD.md` modified after `task-sequence.md` → warn: DAG may be stale vs PRD
- `task-sequence.md` modified after any `.tickets/*.md` → warn:
  fleshed tickets may be stale vs DAG
- Any `.tickets/*.md` modified after `critic-report.md` → warn:
  critic report is stale
- `task-sequence.md` modified after `challenger-report.md` → warn:
  Challenger audit is stale vs the DAG; re-run the Challenger before
  spec-writer
- `PRD.md` or `task-sequence.md` modified after `coverage-audit.md` →
  warn: Coverage Auditor diff is stale vs the current PRD/DAG; re-run
  the Coverage Auditor before spec-writer
- Orphan tickets (`.tickets/*.md` whose ID is not in `task-sequence.md`) →
  warn: orphan ticket present, possibly from a prior planning cycle
- Any `.tickets/*.md` modified after its `.tickets/tdd/toq-<id>.yaml` →
  warn: TOQ is stale vs ticket — /tdd Phase 0 should re-run before the
  next RED cycle
- Current `HEAD` has advanced past the `diff_base` recorded in a
  BUILD ticket's TOQ → warn: TOQ diff_base is stale; re-scope before
  continuing
- If an antiplan session transcript is available alongside
  `.plan/task-sequence.md`, optionally run
  `python ~/.skills/antiplan/validate.py --transcript <path> ...`
  and surface any `confidence: LOW`, `unresolved > 0`, or
  `Proceeding: no` hits as soft warnings. Do not block on these — they are
  advisory alongside the hard-gate `dag-done` validator run.
- `.plan/brownfield-context.md` has a non-empty `open_questions` list →
  warn: unresolved research questions; confirm they are answered or ticketed.
