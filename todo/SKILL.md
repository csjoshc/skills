---
name: todo
description: Routes the multi-session planning-to-implementation pipeline (antiplan → spec-writer → ticket-critic → build via /todo build or /todo run, with tdd). Antiplan is optional; /todo spec starts a Lite pipeline straight from spec-writer. Detects pipeline state from artifacts on disk and emits copy-pasteable prompts for the next session or cold-start handoffs before clearing or compacting context. Advise-only. Use when starting a non-trivial feature, resuming mid-pipeline, or about to compact context. Skip for implementation-only tasks (PR fix, UI tweak, review).
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
build        → mutates .tickets/NNN-slug.md frontmatter (Stage: NEW → BUILD → COMPLETE)
             via /todo build (manual, one ticket per session) or /todo run (auto-driver)
tdd          → runs inside each build session for red-green-refactor on ONE ticket
             → writes .tickets/tdd/toq-<ticket-id>.yaml (ranked Test Obligation Queue, Phase 0)
```

Antiplan is optional. In **Lite mode** (tickets with no `.plan/task-sequence.md`),
the pipeline is spec-writer → (optional ticket-critic) → build.

Each skill runs in its own session. Artifacts on disk are the handoff medium.
"Subagent" below means an agent in a separate context; if the harness has none,
use a fresh session instead.
Your job is to tell the user exactly what prompt to paste next, never to do
the pipeline work yourself.

## Invariants

1. **Advise only.** Never run antiplan, spec-writer, ticket-critic, or
   /todo run's build waves on the user's behalf. Never write or modify pipeline
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
  User is beginning a new planning cycle for risky or large work.
- `/todo spec <feature description>` → **Emit spec-writer-direct prompt.**
  Lite mode: defined feature, no antiplan.
- `/todo next` → **Emit the next-stage prompt.** Detect state and output
  only the prompt (no status summary). Same recommendation as bare `/todo`
  but terse.
- `/todo handoff` → **Emit a cold-start resume prompt.** For when the user
  is about to clear or compact context. Output a prompt that reopens the
  current stage in a fresh session.
- `/todo status` → **Detailed state dump.** Every artifact path, modified
  time, per-ticket `Stage:` value, staleness warnings.
- `/todo build` → **Emit per-ticket manual-execution prompt** for the next
  `Stage: NEW` ticket (DAG-respecting). Uses `/tdd` + `/verify-claim`
  inline; does NOT spawn implementer subagents per ticket.
- `/todo build <ticket-id>` → Same but for a specific ticket file. Skips
  the DAG-readiness check (assumes user knows what they're doing).
- `/todo gate <slice-id>` → **Emit slice-gate review prompt** with a
  independent review (subagent suggested) of all tickets in the slice plus the gate
  artifact. Use when every non-gate ticket in a slice is `Stage: COMPLETE`
  and the gate ticket is `Stage: NEW`.
- `/todo resume` → **Emit mid-build resume prompt.** For continuing a
  ticket whose `Stage: BUILD` was set in a prior session that ended.
  Detects the in-flight ticket, lists what's already done (via git diff
  vs. ticket ACs), and emits a prompt that picks up where the prior
  session left off.

If the user passes an unrecognized argument, default to the bare `/todo`
behavior and note that the argument was ignored.

## State Detection and Routing

Scan the repo root with the harness's file-search and read tools (paths, plus frontmatter `Stage:` lines only); avoid shell loops.
Artifact map, full inference rules and staleness warnings: [references/state-detection.md](references/state-detection.md). Read it before detecting state.

| Stage | Condition (summary) | Recommend | Template |
| --- | --- | --- | --- |
| fresh | no `.plan/` or `.tickets/` artifacts | by size: implement directly, `/todo spec`, or `/todo start` | spec-writer-direct / antiplan-start |
| lite-ready | tickets, no `task-sequence.md`, `Stage: NEW` remain | `/todo build` (ticket-critic optional) | build-ticket-manual |
| phase-0-done | only `brownfield-context.md` | resume antiplan Phase 1 | antiplan-resume |
| prd-done-no-dag | `PRD.md`, no `task-sequence.md` | resume antiplan Phase 3 | antiplan-resume |
| dag-done-no-audits | DAG present, `challenger-report.md` (or `coverage-audit.md` for Standard/Heavy) missing | resume antiplan Phase 3 / 3.5; plan NOT ready for spec-writer | antiplan-audit-resume |
| audit findings | Challenger BLOCK or Coverage GAP/INVERTED | fix the finding | audit-fix-resume |
| dag-done | DAG + audits present, no tickets | **gate:** run `antiplan/validate.py` with all evidence flags first (command in state-detection.md); exit 0 then spec-writer, non-zero then antiplan resume | spec-writer-next |
| tickets-written-uncriticized | Full mode: tickets exist, no or stale `critic-report.md` | ticket-critic | ticket-critic-next |
| critic-failed | `critic-report.md` contains `FAIL` | back to spec-writer for failing tickets | spec-writer-fix |
| ready-for-build / partial-build | critic passes; `Stage: NEW` tickets remain | `/todo build` (manual) or `/todo run` (auto-driver) | build-ticket-manual |
| slice-gate-pending | all non-gate tickets in a slice `COMPLETE`, gate ticket `NEW` | `/todo gate <slice-id>` | slice-gate-review |
| mid-build-resume | exactly one ticket `Stage: BUILD`, no active session | `/todo resume` | build-ticket-resume |
| build-unscoped | `Stage: BUILD` ticket without `.tickets/tdd/toq-<id>.yaml` | run `/tdd` Phase 0 first | (none) |
| all-complete | every ticket `COMPLETE` | announce pipeline done | (none) |

Staleness and orphan warnings are non-blocking and listed in state-detection.md. To show ticket state over time, run `/trackboard refresh`.

## Prompt Templates

Inline the matching template body from [references/prompt-templates.md](references/prompt-templates.md), filling slots from detected state; build, resume and gate prompts are in [references/execution-templates.md](references/execution-templates.md). Each prompt is stand-alone. The `handoff` template is the generic cold-start prompt for the current stage.

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

After pasting, clear or compact THIS session if you want to free context
before the next stage begins.
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

For `/todo spec <feature>`: same shape, with the spec-writer-direct template.

## Things NOT to do

- Do **not** invoke other skills yourself. /todo is a
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

## Auto-driver: `/todo run`

`/todo run` is the only sub-command that is not advise-only. It is an explicit opt-in: it
invokes skills as subagents, may modify pipeline artifacts through them, and may make
checkpoint commits under the operator's standing authorization. It halts on any structured
halt condition and the user can interrupt it at any time.

Full spec (invocation, state machine, build loop, halt conditions, forbidden actions, tools):
`references/auto-driver.md`. Read it before running `/todo run`.

## Companion files

Read only when the situation matches:

- [references/state-detection.md](references/state-detection.md): detecting pipeline state, inference rules, staleness warnings
- [references/prompt-templates.md](references/prompt-templates.md): emitting any antiplan, spec-writer, ticket-critic or handoff prompt
- [references/execution-templates.md](references/execution-templates.md): emitting build-ticket-manual, build-ticket-resume or slice-gate-review prompts
- [references/auto-driver.md](references/auto-driver.md): running `/todo run`
- [../shared/EVIDENCE_REVIEWER.md](../shared/EVIDENCE_REVIEWER.md): reviewing a BUILD subagent's ticket claims (used by `/todo run` and ticket-critic Pattern 18)
