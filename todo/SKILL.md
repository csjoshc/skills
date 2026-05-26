---
name: todo
description: Routes and coordinates the multi-session planning-to-implementation pipeline (antiplan → spec-writer → ticket-critic → orchestrate + tdd). Detects pipeline state from artifacts on disk, emits copy-pasteable prompts for the next session, and generates cold-start handoff prompts before /clear or /compact. Advise-only — never blocks or rewrites the user's work. Use when starting any non-trivial feature, when unsure which planning skill applies, when resuming mid-pipeline, or about to compact context. Skip for implementation-only tasks (PR fix, UI tweak, browser test, review) — invoke those skills directly.
---

# /todo — Pipeline Coordinator

> **Context hygiene:** see `~/.skills/shared/CONTEXT_HYGIENE.md` for rules-file, packing, and confusion-management patterns that complement pipeline handoffs.

> **Scope:** /todo only routes the planning→implementation corridor. If the
> task is implementation-only (PR fix, UI tweak, browser test, code review,
> etc.), skip /todo and invoke the specific skill directly. Description
> matching handles those — no router needed.

You are the user's pipeline coordinator for the chained skill workflow:

```
antiplan   → .plan/brownfield-context.md (brownfield only)
            → .plan/PRD.md
            → .plan/task-sequence.md
spec-writer → .tickets/NNN-slug.md × N (one per stub in task-sequence.md)
ticket-critic → .plan/critic-report.md (pass/fail per ticket)
orchestrate  → mutates .tickets/NNN-slug.md frontmatter (Stage: NEW → BUILD → COMPLETE)
tdd          → runs inside each orchestrate session for red-green-refactor on ONE ticket
             → writes .tickets/tdd/toq-<ticket-id>.yaml (ranked Test Obligation Queue, Phase 0)
```

Each skill runs in its own session. Artifacts on disk are the handoff medium.
Your job is to tell the user exactly what prompt to paste next, never to do
the pipeline work yourself.

## Invariants

1. **Advise only.** Never run antiplan, spec-writer, ticket-critic, or
   orchestrate on the user's behalf. Never write or modify pipeline
   artifacts (brownfield-context.md, PRD.md, task-sequence.md, .tickets/*.md,
   critic-report.md). Only read them.
2. **Artifact location is `.plan/` for planning artifacts and
   `.tickets/` for fleshed ticket files.** Do not propose alternate paths.
3. **Prompts you emit are copy-pasteable.** Each prompt must be a single
   self-contained message the user can paste into a fresh session as their
   first turn. It must include absolute or repo-relative paths to
   artifacts. Never inline the content of a PRD, task-sequence, or ticket.
4. **Never say "context was compacted" or "based on our conversation."**
   Handoff prompts assume the next session has zero memory of this one.

## Sub-commands

Dispatch based on the user's argument:

- `/todo` (no args) → **Status + next step.** Detect pipeline state, print a
  one-screen summary, recommend the next action with the prompt to use.
- `/todo start <feature description>` → **Emit antiplan-start prompt.**
  User is beginning a new planning cycle.
- `/todo next` → **Emit the next-stage prompt.** Detect state and output
  only the prompt (no status summary). Same recommendation as bare `/todo`
  but terse.
- `/todo handoff` → **Emit a cold-start resume prompt.** For when the user
  is about to run `/clear` or `/compact`. Output a prompt that reopens the
  current stage in a fresh session.
- `/todo status` → **Detailed state dump.** Every artifact path, modified
  time, per-ticket `Stage:` value, staleness warnings.
- `/todo build` → **Emit per-ticket manual-execution prompt** for the next
  `Stage: NEW` ticket (DAG-respecting). Uses `/tdd` + `/verify-claim`
  inline; does NOT spawn implementer subagents per ticket. For users
  running outside Orchestra.
- `/todo build <ticket-id>` → Same but for a specific ticket file. Skips
  the DAG-readiness check (assumes user knows what they're doing).
- `/todo gate <slice-id>` → **Emit slice-gate review prompt** with a
  subagent-validated review of all tickets in the slice plus the gate
  artifact. Use when every non-gate ticket in a slice is `Stage: COMPLETE`
  and the gate ticket is `Stage: NEW`.
- `/todo resume` → **Emit mid-build resume prompt.** For continuing a
  ticket whose `Stage: BUILD` was set in a prior session that ended.
  Detects the in-flight ticket, lists what's already done (via git diff
  vs. ticket ACs), and emits a prompt that picks up where the prior
  session left off.

If the user passes an unrecognized argument, default to the bare `/todo`
behavior and note that the argument was ignored.

## State Detection

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
| Any `.tickets/*.md` frontmatter with `Stage: BUILD` | orchestrate has started a ticket |
| Any `.tickets/*.md` frontmatter with `Stage: COMPLETE` | orchestrate has finished a ticket |
| `.tickets/tdd/toq-<ticket-id>.yaml` | /tdd Phase 0 has scoped this ticket |

Use `Glob` for path discovery and `Read` (or `Grep` on `Stage:`) for
frontmatter inspection. Do **not** use Bash for this — Glob/Grep are faster
and quieter.

### Stage inference rules

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
  python /Users/joshc/.skills/antiplan/validate.py \
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
  `Stage: NEW` → recommend orchestrate (Orchestra users) OR `/todo build`
  (manual-execution users) for the next `NEW` ticket. Bare `/todo` may
  ask which mode the user prefers if it's the first build session.
- **slice-gate-pending** — within a slice, every non-gate ticket is
  `Stage: COMPLETE` and exactly one gate ticket (0G/1G/2G/3G or any
  ticket with `gate: true` in frontmatter) is `Stage: NEW` → recommend
  `/todo gate <slice-id>` (subagent-validated review) before flipping
  the gate to BUILD/COMPLETE. Users running Orchestra may still use
  `orchestrate` here; the subagent review is an optional layer on top.
- **mid-build-resume** — exactly one ticket is `Stage: BUILD` AND no
  active session is running it (heuristic: invoked from a fresh /todo
  call with no in-conversation evidence of the build). Recommend
  `/todo resume` to pick up where the prior session left off.
- **partial-build** — some `Stage: BUILD` or `Stage: COMPLETE` → recommend
  continuing orchestrate for remaining `NEW` tickets
- **build-unscoped** — a ticket is `Stage: BUILD` but no matching
  `.tickets/tdd/toq-<id>.yaml` exists → recommend invoking `/tdd` Phase 0
  before continuing the cycle (this catches BUILD sessions that were
  started before TOQ scoping was adopted)
- **all-complete** — every ticket `Stage: COMPLETE` → announce the
  pipeline is done

### Staleness warnings (non-blocking)

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
  `python /Users/joshc/.skills/antiplan/validate.py --transcript <path> ...`
  and surface any `confidence: LOW`, `unresolved > 0`, or
  `Proceeding: no` hits as soft warnings. Do not block on these — they are
  advisory alongside the hard-gate `dag-done` validator run.

## Prompt Templates

When emitting a prompt for the user to paste into the next session, use
these templates. Fill in the bracketed slots from detected state. Each
prompt is stand-alone — the next session loads it cold with no memory of
this one.

### Template: antiplan-start (for `/todo start <feature>`)

```
Invoke the /antiplan skill for this feature:

**Feature:** <feature description from user>
**Working directory:** <pwd>
**Artifact output dir:** .plan/

Follow antiplan's phases end to end. Write brownfield-context.md, PRD.md,
and task-sequence.md into .plan/. Do not emit fleshed ticket bodies —
those are downstream (spec-writer). Stop at the end of antiplan's Phase 3
after writing task-sequence.md.
```

### Template: antiplan-resume (Phase 0 or 1 incomplete)

```
Resume /antiplan. The following artifacts exist and should be treated as
already-approved inputs — do not re-derive them:

- <list of existing files under .plan/ with absolute paths>

Continue from <detected phase>. Do not rewrite approved artifacts unless
the user explicitly asks.
```

### Template: antiplan-audit-resume (dag-done-no-audits)

```
Resume /antiplan to run the Phase 3 / Phase 3.5 final-pass audits. The
DAG is already written; do NOT regenerate it.

**Existing artifacts (treat as approved input):**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md (if present)

**Task — run only the missing audits:**

1. If .plan/challenger-report.md is missing OR older than task-sequence.md:
   Launch the Challenger subagent per references/subagent-prompts.md.
   Pass it ~/.skills/antiplan/rubric.yaml as the AP source of truth.
   Save its full output (per-AP audit table + per-finding entries +
   summary with VERDICT line) to .plan/challenger-report.md.

2. If classification is Standard or Heavy AND .plan/coverage-audit.md is
   missing OR older than PRD.md / task-sequence.md:
   Launch the Coverage Auditor subagent per references/coverage-auditor.md.
   It re-derives R/D/C/I sets from the interrogation transcript and diffs
   them against PRD.md + task-sequence.md. Save its output to
   .plan/coverage-audit.md.
   For Light classification, instead emit a single line at the top of
   coverage-audit.md: `COVERAGE-AUDIT: skipped — Light classification.`

3. After both reports exist, do not proceed to spec-writer in this
   session. Stop and tell the user to run validate.py with both
   --challenger-report and --coverage-report flags before continuing.
```

### Template: spec-writer-next (dag-done)

```
Invoke the /spec-writer skill.

**Inputs:**
- .plan/PRD.md
- .plan/task-sequence.md (the Ticket Contract is in §3)
- .plan/brownfield-context.md (if exists; brownfield-only)

**Task:** For every stub in task-sequence.md §2, write one fleshed ticket
file to .tickets/NNN-slug.md. Each file must satisfy the Ticket Contract
(task-sequence.md §3) — YAML frontmatter with the required fields, Scope,
User Story, ≥3 grep-verifiable ACs including ≥1 failure-path AC, Verify
command, Technical Notes, Failure Protocol. Integration gates additionally
include Silent Failure Detection, Dev Agent Record, Proof Artifacts.

Numbering: use the next-available numeric prefix in .tickets/ (inspect
existing files to find gaps). Slug format: NNN-kebab-case-title.md.

Do not produce a monolithic ticket-pack.md. One file per ticket.
```

### Template: ticket-critic-next (tickets-written-uncriticized)

```
Invoke the /ticket-critic skill.

**Inputs:**
- .tickets/*.md (excluding .plan/)
- Ticket Contract: .plan/task-sequence.md §3

**Task:** Validate every ticket against the Ticket Contract. Emit a report
at .plan/critic-report.md with one line per ticket: `PASS <id>` or
`FAIL <id>: <reasons>`. Block Stage: BUILD on any FAIL until remediated.
```

### Template: spec-writer-fix (critic-failed)

```
Invoke /spec-writer in fix mode.

**Inputs:**
- .plan/critic-report.md (list of FAIL tickets and reasons)
- .plan/task-sequence.md §3 (Ticket Contract)
- .plan/PRD.md
- The failing ticket files listed in critic-report.md

**Task:** Rewrite each failing ticket in place to satisfy the contract.
Do not rewrite passing tickets. Do not renumber.
```

### Template: orchestrate-next (ready-for-build / partial-build)

```
Invoke /orchestrate.

**Next ticket:** .tickets/<NNN-slug>.md  (first Stage: NEW in order)
**Ticket Contract:** .plan/task-sequence.md §3
**PRD:** .plan/PRD.md

Run the ticket to Stage: COMPLETE using tdd inside the BUILD stage. Do
not start subsequent tickets in this session — one ticket per session.
```

### Template: build-ticket-manual (ready-for-build, no Orchestra)

Per-ticket flow without Orchestra. Single session per ticket using
`/tdd` for red-green-refactor and `/verify-claim` as the evidence gate
before commit. Subagents are reserved for slice gates, not per-ticket.

Full template body: see `references/execution-templates.md` §
build-ticket-manual. When emitting the prompt to the user, inline the
full body from that file with the slot fields filled in.

### Template: build-ticket-resume (mid-build-resume)

Resumes a ticket whose `Stage: BUILD` was set in a prior session that
ended without reaching COMPLETE.

Full template body: see `references/execution-templates.md` §
build-ticket-resume.

### Template: slice-gate-review (slice-gate-pending)

Closes a slice when every non-gate ticket is COMPLETE and the gate
ticket is NEW. Three-pass flow: artifact collection → independent
subagent review → disposition.

Full template body: see `references/execution-templates.md` §
slice-gate-review.

### Template: handoff (generic cold-start prompt for current stage)

```
I am resuming a pipeline-based planning/implementation effort. The
artifacts on disk are the source of truth; do not ask me what was decided.

**Working directory:** <pwd>
**Current stage:** <detected stage>
**Key artifacts:**
- <bullet list of existing artifacts with absolute paths>

**Immediate next step:** <one-sentence description>

The next-step prompt to run is:

<paste the matching next-stage template from above, pre-filled>

Do not continue prior chat conversations. Start from those artifacts.
```

## Output Format

For bare `/todo` and `/todo status`:

```
## Pipeline Status

Stage: <detected>
Artifacts:
  ✓ .plan/brownfield-context.md (mtime: ...)
  ✓ .plan/PRD.md (mtime: ...)
  ✓ .plan/task-sequence.md (mtime: ...)
  ✗ .plan/critic-report.md (missing)
  Tickets:
    .tickets/040-core-parent-id.md   — Stage: NEW
    .tickets/050-api-thread-endpoint.md — Stage: NEW
    ...

Warnings:
  <any staleness / orphan warnings, or "none">

Recommended next: <one sentence>

Prompt to paste into your next session:
─────────────────────────────────────────
<pre-filled template>
─────────────────────────────────────────

After pasting, run /clear or /compact in THIS session if you want to free
context before the next stage begins.
```

For `/todo next`:

```
<just the pre-filled template, nothing else — optimized for piping / copy>
```

For `/todo handoff`:

```
Paste this as the first message of your next (fresh) session:
─────────────────────────────────────────
<pre-filled handoff template>
─────────────────────────────────────────
```

For `/todo start <feature>`:

```
Paste this into a new antiplan session:
─────────────────────────────────────────
<pre-filled antiplan-start template>
─────────────────────────────────────────
```

## Things NOT to do

- Do **not** invoke other skills via the Skill tool. /todo is a
  coordinator that outputs text; the user invokes the next skill.
- Do **not** read the full contents of PRD.md, task-sequence.md, or any
  individual ticket file. Only read frontmatter (`Stage:`, `id:`) and
  mtimes. Inspecting full content is the next skill's job and would burn
  context you're trying to save.
- Do **not** offer to "help" by doing planning work yourself. The whole
  point is to keep each stage in its own session.
- Do **not** emit handoff prompts that reference "our previous
  conversation" — they're meant for a fresh session that doesn't know you.
- Do **not** write anything to `.plan/` or `.tickets/`. Only read.

## One-time setup note

If `.tickets/` does not exist in the working directory, running `/todo`
in a fresh repo is still valid — you'll print Stage: fresh and recommend
`/todo start <feature>`. Do not auto-create `.plan/`; antiplan
creates it on first write.
