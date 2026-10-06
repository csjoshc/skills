# Auto-driver: `/todo run`

`/todo run` is the **only** sub-command that violates Invariant 1's
"advise only" rule. It is an explicit operator opt-in to auto-drive
the planning→implementation pipeline without paste-into-a-new-session
round trips. The Invariant override is scoped: only `/todo run` may
invoke skills as subagents, only `/todo run` may modify pipeline
artifacts (and only via the skills it invokes), only `/todo run` may
make checkpoint commits (under the operator's standing authorization).

## Contents


Every other sub-command remains advise-only. The user always retains
the right to interrupt `/todo run` mid-stride; the auto-driver halts
gracefully on any structured halt condition.

### Invocation

```
/todo run                       # drive until DAG complete or halt
/todo run <N>                   # advance at most N more tickets
/todo run until <condition>     # halt on loose state match
                                # e.g. "until phase-3-complete",
                                #      "until critic-report.md",
                                #      "until T09 complete"
```

### State machine

On each tick, the auto-driver runs the same state detection as bare
`/todo`, then maps state to action:

| Detected state | Auto-driver action |
|---|---|
| `fresh` | **HALT** — needs a feature description; emit `/todo start` prompt and stop. Cannot fabricate goals. |
| `phase-0-done` | Invoke antiplan-resume via Skill tool; antiplan continues Phase 1 |
| `prd-done-no-dag` | Invoke antiplan-resume; antiplan continues to Phase 3 |
| `dag-done-no-audits` | Invoke antiplan-audit-resume; Challenger + Coverage subagents run within antiplan |
| `dag-done` (and `validate.py` exit 0; reports show 0 BLOCKs / 0 INVERTED / 0 GAP) | Invoke spec-writer via Skill tool |
| `audit-blockers-present` (`validate.py` exit 0 but challenger-report contains BLOCKs OR coverage-audit shows INVERTED/GAP) | Invoke `audit-fix-resume` template — auto-driver pastes one section per finding, inlining verbatim quotes from the reports. Halts when validate.py + verdicts all clean + staleness clean. |
| `dag-done` (and `validate.py` exit non-zero) | **HALT** — surface validator failures (schema-level malformations: missing AP rows, evidence too short, etc.). Distinct from BLOCKs above; validator failures are structural, not architectural. Return to user for direction. |
| `tickets-written-uncriticized` | Invoke ticket-critic (per-ticket subagent delegation if N > 5, per ticket-critic SKILL.md) |
| `critic-failed` | Invoke spec-writer in fix mode for failing tickets only |
| `ready-for-build` | Enter the **build loop** (see below) |
| `slice-gate-pending` | Invoke gate review (subagent-validated per `/todo gate` template) |
| `mid-build-resume` | Resume in-flight ticket via the mid-build-resume template; spawn a subagent that picks up where prior session left off |
| `all-complete` | Emit final-status summary and **HALT — pipeline done** |

### The build loop

When entering `ready-for-build`:

1. **Identify the next wave.** Read the DAG (`.plan/task-sequence.md`)
   to find all tickets whose `Depends-On` chain is fully satisfied
   (every dep ticket is `Stage: COMPLETE`).
2. **Filter for parallel-safety.** Within the wave, group tickets
   whose `Files:` lists are fully disjoint AND whose risk tags
   permit parallel build. Tickets tagged `Risk: medium` or higher,
   OR tickets marked as the DAG's "mutation hub" / "integration
   gate", run **solo** even if the wave has multiple ready
   candidates.
3. **Spawn the wave in parallel.** For each ticket in the wave,
   spawn a BUILD subagent (via the `Agent` tool with
   `subagent_type: general-purpose`) in a single message — multiple
   `Agent` calls in one turn run concurrently. Each subagent's
   prompt is the `build-ticket-manual` template plus the ticket's
   absolute path. Use `run_in_background: true` so the auto-driver
   continues to monitor without blocking on any single agent.
4. **Wait for all wave subagents to complete.** Notifications arrive
   as each finishes. After ALL have returned:
5. **Spawn evidence-reviewer per ticket** (via `Agent` tool, parallel
   batch if multiple tickets completed). Each reviewer gets:
   - The ticket file path
   - The prior checkpoint commit SHA (the last checkpoint from
     `git log --oneline -1`)
   - The build subagent's final report (verbatim)
   - The artifact directory path
   - The ticket's ACs (source of truth)
   See `~/.skills/evidence-reviewer/SKILL.md` if present, else
   inline the audit checklist (scope-check via git diff, per-AC
   re-verification, artifact existence + size sanity,
   subagent-deviation audit, wrapper-target re-verification, Stage
   flip earned).
6. **Gate on evidence-reviewer verdicts:**
   - ALL `VERIFIED` → proceed to step 7
   - ANY `DRIFT-DETECTED` or `EVIDENCE-INSUFFICIENT` → **HALT** with
     a structured report quoting the reviewer's findings; await
     operator direction (typically: re-run the build subagent
     with corrections, or accept the deviation and proceed)
7. **Checkpoint commit.** Under the operator's standing authorization, run:
   ```bash
   cd <repo-root> && git add -A && git commit -m "<wave summary>"
   ```
   The commit message names the tickets that just landed and the
   evidence-reviewer verdict for each. **Never push** unless the
   operator has explicitly authorized push for this repo (check
   memory; default deny).
8. **Loop back to state detection.** Re-detect state, find the next
   wave, repeat.

### Halt conditions

The auto-driver halts immediately on any of these:

- `fresh` state (no feature description; cannot proceed)
- `dag-done` with `validate.py` non-zero exit
- `critic-failed` and the failing tickets exceed an automatic-fix
  heuristic (the operator must decide whether to rewrite specs or
  accept blockers)
- ANY BUILD subagent returns `Stage: BUILD` (i.e. did not flip to
  COMPLETE) after one auto-retry
- ANY evidence-reviewer returns `DRIFT-DETECTED` or
  `EVIDENCE-INSUFFICIENT`
- The user-supplied stop condition matches (`/todo run until X`)
- The user-supplied ticket cap is hit (`/todo run N`)
- Tool-use error budget exceeded (≥3 consecutive Bash/Agent failures
  without progress)
- Operator interrupts (the operator may always interrupt; the
  auto-driver honors interrupts gracefully and emits a resumable
  state summary)

### Halt output contract

On every halt — graceful or fault — the auto-driver emits a
structured final message:

```markdown
# /todo run halted

**Reason:** <one of: pipeline-complete | needs-input | validator-failed |
critic-blocker | build-blocker | drift-detected | evidence-insufficient |
user-condition-met | ticket-cap-hit | error-budget |
operator-interrupt>

**Progress this run:**
- Tickets advanced: <count> (<ticket-IDs>)
- Checkpoints created: <count> (<commit-SHAs>)
- Subagents spawned: <count> total (<count-build>, <count-evidence>,
  <count-critic>)

**Current pipeline state:** <detected-state-from-state-detection>

**Next step (if applicable):** <copy-pasteable prompt or
explicit-action description>
```

This contract guarantees the operator can always know exactly where
the pipeline stopped and what the next action is.

### Things `/todo run` may NOT do

- **Never push** to any git remote without explicit per-repo
  operator authorization stored in memory
- **Never invent feature descriptions** when state is `fresh` —
  halt and ask
- **Never auto-accept** DRIFT-DETECTED or EVIDENCE-INSUFFICIENT
  verdicts — halt and surface
- **Never invoke `/todo run` recursively** — the auto-driver runs
  in one process; subagents it spawns must not themselves invoke
  `/todo run`
- **Never bypass the constitution / sign-off phases** in antiplan
  — these are operator-gated by design and the auto-driver halts
  when antiplan halts
- **Never modify ticket `Stage:` directly** — only BUILD subagents
  flip Stage to COMPLETE; the auto-driver only orchestrates
- **Never skip evidence-reviewer** on any BUILD subagent's output
  (skipping defeats the structural fix that AP-26/27 + Pattern 18
  add to the pipeline)

### Tools the auto-driver uses

- `Glob` / `Read` / `Grep` — state detection
- `Bash` — git commands (status, log, diff, add, commit; never push
  without explicit auth), validate.py invocation
- `Skill` — invoke antiplan, spec-writer, ticket-critic when the
  state machine routes there
- `Agent` (`subagent_type: general-purpose`, `run_in_background:
  true`) — spawn BUILD subagents, evidence-reviewer subagents
- `TodoWrite` — track wave progress visibly
- `Edit` / `Write` — only on `.plan/critic-report.md` to materialize
  ticket-critic verdicts when the skill itself doesn't persist them;
  NEVER on PRD.md, task-sequence.md, or `.tickets/*.md` directly

### Relationship to other sub-commands

`/todo run` complements but does not replace the manual sub-commands:

- `/todo run` halts → operator inspects → operator may invoke
  `/todo next` / `/todo build` for finer-grained control
- `/todo handoff` is still useful before `/clear`/`/compact` even
  mid-run; the auto-driver can emit a handoff prompt and stop
- `/todo gate` is invoked AUTOMATICALLY by the auto-driver when
  state is `slice-gate-pending`; no manual call needed
