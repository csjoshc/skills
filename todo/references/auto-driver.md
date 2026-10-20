# Drive loop

Bare `/todo` and `/todo auto` use this loop. `/todo auto <N>` caps tickets;
`/todo auto until <condition>` stops on a loose state match.

## Contents

- State → action
- Build waves
- Halt conditions
- Halt output
- Forbidden actions

## State → action

| Detected state | Action |
|---|---|
| `fresh` | If the user named work: write thin DAG + tickets (or skip tickets for a small change) and continue. Small scoped frontend UI → `ui`. If no feature description: **HALT** and ask. |
| `phase-0-done` / `prd-done-no-dag` / `dag-done-no-audits` | Continue challenge |
| `audit findings` | Fix or **HALT** with the finding |
| `dag-done` | Invoke spec |
| `lite-ready` / `ready-for-build` / `partial-build` | Build waves |
| `slice-gate-pending` | Independent gate review |
| `mid-build-resume` | Resume the in-flight ticket in a subagent |
| `all-complete` | Stop |

ticket-review is optional. Do not wait on a critic report.

## Build waves

1. Confirm the source worktree is clean before the first source change. Ignore
   `.plan/`, `.tickets/`, and other local planning artifacts. If unrelated
   source changes exist, stop and ask.
2. **Next wave.** From the DAG, take tickets whose `Depends-On` are COMPLETE.
   Lite mode: one ticket at a time unless `Depends-On` is explicit.
3. **Parallel-safety.** Group only tickets with disjoint `Files:` and low risk.
   `Risk: medium` or higher, mutation hubs, and integration gates run solo.
4. **Spawn.** One `Agent` call per ticket in the wave, same turn, background.
   Brief is the build template plus the ticket's absolute path. Pointers only.
   For frontend UI scope, the brief tells the subagent to invoke `ui`.
5. **Review.** After the wave returns, check each ticket against
   `~/.skills/shared/EVIDENCE_REVIEWER.md`.
6. **Gate.** ALL VERIFIED → optional ticket-scoped checkpoint commit (never
   add `.plan/` or `.tickets/`; never push). ANY drift or missing evidence → **HALT**.
7. **Loop.** Re-detect state.

## Halt conditions

- `fresh` with no feature description
- Load-bearing question (Tier 3, conflicting tickets, undefined success)
- BUILD subagent still `Stage: BUILD` after one retry
- Evidence reviewer: DRIFT-DETECTED or EVIDENCE-INSUFFICIENT
- User stop condition or ticket cap
- ≥3 consecutive tool failures without progress
- Operator interrupt

## Halt output

```markdown
# /todo halted

**Reason:** <pipeline-complete | needs-input | build-blocker | drift-detected |
evidence-insufficient | user-condition-met | ticket-cap-hit | error-budget |
operator-interrupt>

**Progress this run:**
- Tickets advanced: <count> (<ids>)
- Checkpoints: <count> (<SHAs>)
- Subagents: <count>

**State:** <detected>
**Next:** <question or action>
```

## Forbidden

- Push without per-repo authorization
- Invent a feature when `fresh` has no description
- Auto-accept drift or missing evidence
- Recurse `/todo auto` from a subagent
- Flip `Stage:` in the parent; only the BUILD subagent writes COMPLETE
- Skip evidence review
- Bypass challenge sign-off when challenge is in use
- Commit `.plan/` or `.tickets/`
