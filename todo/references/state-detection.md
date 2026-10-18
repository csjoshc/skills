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
| `.plan/brownfield-context.md` | challenge Phase 0 done (brownfield) |
| `.plan/PRD.md` | challenge Phases 1–2 done |
| `.plan/task-sequence.md` | challenge Phase 3 done |
| `.plan/challenger-report.md` | challenge Phase 3 Challenger subagent ran (per-AP audit table; option-3 evidence) |
| `.plan/coverage-audit.md` | challenge Phase 3.5 Coverage Auditor ran (transcript-vs-PRD diff; option-4 evidence) |
| `.tickets/*.md` | spec has run |
| `.plan/critic-report.md` | ticket-review has run |
| Any `.tickets/*.md` frontmatter with `Stage: BUILD` | a ticket build has started |
| Any `.tickets/*.md` frontmatter with `Stage: COMPLETE` | a ticket build has finished |
| `.tickets/tdd/toq-<ticket-id>.yaml` | /tdd Phase 0 has scoped this ticket |

Use the harness's file-search and read tools for path discovery and
frontmatter inspection (search for `Stage:` lines rather than reading
whole files). Avoid shell loops for this; they are slower and noisier.

## Pipeline modes

- **Full** - `.plan/task-sequence.md` exists. Every rule below applies.
- **Lite** - `.tickets/*.md` exist but `.plan/task-sequence.md` does not
  (tickets came from spec directly or were hand-written). Skip the
  challenge, validator, Challenger, Coverage and orphan-ticket rules. DAG
  readiness uses any dependency the ticket declares (frontmatter field or a
  `Dependencies:` line), else numeric filename order. ticket-review is recommended once but is not a
  build gate in Manual mode. Auto mode runs ticket-review before build.

## Stage inference rules

- **fresh** - none of the above paths exist → recommend by size:
  - small, already-scoped frontend UI change → `/ui`
  - small, already-scoped non-UI change → skip `/todo`; use `tdd` or implement directly
  - defined feature, a few tickets → spec direct (Lite mode)
  - risky, contested or large → challenge (Full mode; Fast Mode by default)
  - Auto mode chooses from these routes; Manual mode emits the next skill prompt
- **phase-0-done** — only `brownfield-context.md` exists → recommend
  resuming challenge into Phase 1
- **prd-done-no-dag** — `PRD.md` exists but no `task-sequence.md` → recommend
  resuming challenge into Phase 3
- **dag-done-no-audits** — `task-sequence.md` exists but
  `.plan/challenger-report.md` is missing OR (Standard/Heavy run)
  `.plan/coverage-audit.md` is missing → recommend resuming challenge to
  run Phase 3 Challenger and/or Phase 3.5 Coverage Auditor. The plan is
  NOT ready for spec — the per-AP audit + transcript-vs-PRD diff
  are the final pass. Light-mode plans may skip coverage-audit.md if the
  task-sequence.md transcript explicitly emits
  `COVERAGE-AUDIT: skipped — Light classification`.
- **dag-done** — `task-sequence.md` + `challenger-report.md` (+
  `coverage-audit.md` for Standard/Heavy) all present; no `.tickets/*.md` →
  validate with all evidence flags before spec. Auto mode runs this
  command; Manual mode emits it as the next action:
  ```
  python3 ~/.skills/challenge/validate.py \
    --project-dir . \
    --tickets .plan/task-sequence.md \
    --prd .plan/PRD.md \
    --challenger-report .plan/challenger-report.md \
    --coverage-report .plan/coverage-audit.md
  ```
  Drop `--coverage-report` only if the task-sequence/transcript declared
  `COVERAGE-AUDIT: skipped — Light classification`.
  - exit 0 → recommend spec session (emit spec-next template)
  - non-zero → recommend challenge-resume instead; the plan is not ready
    for fan-out. Common failures: missing AP rows in challenger-report,
    short evidence on a BLOCK row, GAP/INVERTED in coverage-audit, or
    `RE_DERIVED < 5` (Coverage Auditor likely skimmed the transcript).
- **lite-ready** - Lite mode and some tickets `Stage: NEW` → Manual mode emits
  the build-ticket prompt; Auto mode runs ticket-review if needed, then builds
- **tickets-written-uncriticized** (Full mode) — `.tickets/*.md` exist; no
  `critic-report.md`, or critic-report.md older than any `.tickets/*.md` →
  recommend ticket-review session
- **critic-failed** — critic-report.md contains the literal string `FAIL` →
  recommend fix-cycle: return to spec for failing tickets
- **ready-for-build** — critic-report.md passes; some tickets still
  `Stage: NEW` → Manual mode emits the next build-ticket prompt; Auto mode
  continues the serial build loop.
- **slice-gate-pending** — within a slice, every non-gate ticket is
  `Stage: COMPLETE` and exactly one gate ticket (0G/1G/2G/3G or any
  ticket with `Type: integration-gate` or `gate: true` in frontmatter) is `Stage: NEW` → Manual mode emits
  the slice-gate prompt; Auto mode runs the gate review before building it.
- **mid-build-resume** — exactly one ticket is `Stage: BUILD` AND no
  active session is running it (heuristic: invoked from a fresh /todo
  call with no in-conversation evidence of the build). Manual mode emits the
  resume prompt; Auto mode resumes from the recorded diff and TDD artifacts.
- **partial-build** — some `Stage: BUILD` or `Stage: COMPLETE` → Manual mode
  emits the next build prompt; Auto mode resumes or builds the next ready ticket
- **build-unscoped** — a ticket is `Stage: BUILD` but no matching
  `.tickets/tdd/toq-<id>.yaml` exists → run `/tdd` Phase 0 before continuing
  (this catches BUILD sessions that were started before TOQ scoping was adopted)
- **all-complete** — every ticket `Stage: COMPLETE` → announce the
  pipeline is done

`/todo status` shows current progress as a Markdown table using the Status output
rules in `todo/SKILL.md`.

## Staleness warnings (non-blocking)

- `PRD.md` modified after `task-sequence.md` → warn: DAG may be stale vs PRD
- `task-sequence.md` modified after any `.tickets/*.md` → warn:
  fleshed tickets may be stale vs DAG
- Any `.tickets/*.md` modified after `critic-report.md` → warn:
  critic report is stale
- `task-sequence.md` modified after `challenger-report.md` → warn:
  Challenger audit is stale vs the DAG; re-run the Challenger before
  spec
- `PRD.md` or `task-sequence.md` modified after `coverage-audit.md` →
  warn: Coverage Auditor diff is stale vs the current PRD/DAG; re-run
  the Coverage Auditor before spec
- (Full mode only) Orphan tickets (`.tickets/*.md` whose ID is not in `task-sequence.md`) →
  warn: orphan ticket present, possibly from a prior planning cycle
- Any `.tickets/*.md` modified after its `.tickets/tdd/toq-<id>.yaml` →
  warn: TOQ is stale vs ticket — /tdd Phase 0 should re-run before the
  next RED cycle
- Current `HEAD` has advanced past the `diff_base` recorded in a
  BUILD ticket's TOQ → warn: TOQ diff_base is stale; re-scope before
  continuing
- If an challenge session transcript is available alongside
  `.plan/task-sequence.md`, optionally run
  `python3 ~/.skills/challenge/validate.py --transcript <path> ...`
  and surface any `confidence: LOW`, `unresolved > 0`, or
  `Proceeding: no` hits as soft warnings. Do not block on these — they are
  advisory alongside the hard-gate `dag-done` validator run.
- `.plan/brownfield-context.md` has a non-empty `open_questions` list →
  warn: unresolved research questions; confirm they are answered or ticketed.
