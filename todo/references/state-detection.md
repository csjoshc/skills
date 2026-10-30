# State Detection

Artifact map, stage inference, and staleness warnings for `/todo`.

## Contents

- Artifact paths
- Pipeline modes
- Stage inference
- Staleness warnings

## Artifact paths

Scan the repo root for these paths:

| Path | Meaning |
| --- | --- |
| `.agent-local/plan/brownfield-context.md` | challenge Phase 0 done (brownfield) |
| `.agent-local/plan/PRD.md` | challenge Phases 1–2 done |
| `.agent-local/plan/task-sequence.md` | DAG: ticket ids, deps, one-line intent |
| `.agent-local/plan/challenger-report.md` | challenge Challenger ran |
| `.agent-local/plan/coverage-audit.md` | challenge Coverage Auditor ran |
| `.agent-local/tickets/*.md` | spec has run |
| Any `.agent-local/tickets/*.md` with `Stage: BUILD` | a ticket build has started |
| Any `.agent-local/tickets/*.md` with `Stage: COMPLETE` | a ticket build has finished |
| `.agent-local/tickets/tdd/toq-<ticket-id>.yaml` | /tdd Phase 0 has scoped this ticket |

Use file-search and read tools for path discovery and `Stage:` lines.
Do not read whole ticket bodies in the orchestrator.

## Pipeline modes

- **Full** - `.agent-local/plan/task-sequence.md` exists.
- **Lite** - `.agent-local/tickets/*.md` exist but no DAG. Skip challenge and orphan-ticket
  rules. Readiness uses `Depends-On` (or a `Dependencies:` line), else numeric
  filename order.

## Stage inference

- **fresh** - none of the above. Size the work:
  - small, already-scoped frontend UI → `/ui`
  - small, already-scoped non-UI → skip tickets; implement (tdd if test-first)
  - defined feature → write Lite tickets and drive
  - risky, contested or large → challenge, then spec, then drive
- **phase-0-done** — only `brownfield-context.md` → continue challenge Phase 1
- **prd-done-no-dag** — `PRD.md`, no `task-sequence.md` → continue challenge Phase 3
- **dag-done-no-audits** — DAG present, Challenger missing, or Coverage missing
  on Standard/Heavy → continue challenge audits. Light may skip coverage with
  `COVERAGE-AUDIT: skipped — Light classification`.
- **audit findings** — Challenger BLOCK or Coverage GAP/INVERTED → fix or ask
- **dag-done** — DAG present, no tickets → spec
- **lite-ready / ready-for-build / partial-build** — `Stage: NEW` remain →
  build waves
- **slice-gate-pending** — in a slice, non-gate tickets COMPLETE and the gate
  (`gate: true` or `0G/1G/2G/3G`) is NEW → independent gate review
- **mid-build-resume** — exactly one `Stage: BUILD` and no active subagent or
  harness run → resume that ticket. A paused harness run is a hint, not state;
  the ticket `Stage:` decides.
- **build-unscoped** — `Stage: BUILD` without `.agent-local/tickets/tdd/toq-<id>.yaml` →
  tdd Phase 0 in that subagent first
- **all-complete** — every ticket COMPLETE → aggregate PR scope/size checkpoint in the drive loop, then stop

ticket-review is optional. Missing critic output is not a stage.

## Staleness warnings (non-blocking)

- `PRD.md` newer than `task-sequence.md` → DAG may be stale
- `task-sequence.md` newer than any `.agent-local/tickets/*.md` → tickets may be stale
- `task-sequence.md` newer than `challenger-report.md` → Challenger may be stale
- `PRD.md` or DAG newer than `coverage-audit.md` → Coverage may be stale
- Full mode: `.agent-local/tickets/*.md` whose id is not in the DAG → orphan
- Ticket newer than its TOQ → re-scope before the next RED cycle
- HEAD past a BUILD ticket's TOQ `diff_base` → re-scope
- `.agent-local/plan/brownfield-context.md` has a non-empty `open_questions` list →
  confirm they are answered or ticketed
