# Auto mode

Auto mode drives the current pipeline from its detected state to completion.
The user chooses it with `/todo auto` or selects Auto after invoking `/todo`.
Do not ask the user to copy a prompt or invoke a skill between stages.

## Cycle

1. Detect state using [state-detection.md](state-detection.md).
2. Invoke the specialist skill for that state, following its full instructions.
3. If it completes without a human gate, detect state again and continue.
4. Stop only when the pipeline is complete, the user interrupts, or an
   escalation condition below requires a decision.

| State | Auto action |
|---|---|
| `fresh` | If no feature is supplied, ask for it. For a small scoped change, route to the implementation skill. Use Lite ticketing for a defined feature; use antiplan for large, risky, or contested work. Ask when the route is genuinely unclear. |
| `phase-0-done`, `prd-done-no-dag`, `dag-done-no-audits` | Resume antiplan at the next incomplete phase. Honor its approval gates. |
| `dag-done` | Run the antiplan validator with all required evidence. On failure, resume antiplan; on success, invoke spec-writer. |
| `tickets-written-uncriticized` | Invoke ticket-critic. Auto mode also runs the critic in Lite mode. |
| `critic-failed` | Invoke spec-writer to fix failing tickets only, then rerun ticket-critic once. If any ticket still fails, escalate. |
| `ready-for-build`, `partial-build`, `lite-ready` | Build the next dependency-ready ticket using the serial build loop below. |
| `slice-gate-pending` | Run the slice-gate review. Continue only after it passes. |
| `mid-build-resume` | Resume the in-flight ticket from its diff and TDD artifacts. |
| `build-unscoped` | Run `/tdd` Phase 0 before resuming implementation. |
| `all-complete` | Report completion and stop. |

An unrecognized or inconsistent state is an escalation, not a guess.

## Ticket build loop

1. Confirm the source worktree is clean before the first source change. Ignore
   `.plan/`, `.tickets/`, and other configured local planning artifacts. If
   unrelated source changes exist, stop and ask the user to commit, stash, or
   choose a separate worktree.
2. Select one dependency-ready `Stage: NEW` ticket. Follow DAG dependencies in
   Full mode and the Lite dependency rule otherwise. Build serially.
3. Run the build-ticket template in an implementation subagent. It runs `/tdd`
   including Phase 0, implements the ticket ACs, runs `/verify-claim`, lint,
   and typecheck, and sets `Stage: COMPLETE` only when those checks pass. It
   makes no commit.
4. Run an independent evidence review against the ticket ACs, diff, and proof.
   If review passes, commit the reviewed source changes as one ticket-scoped
   checkpoint. Do not add `.plan/` or `.tickets/`; never push.
5. Re-detect state and repeat. Run the slice-gate review automatically when a
   gate becomes the next required ticket.

The Auto choice authorizes these local ticket-scoped checkpoint commits.

## Human escalation

Pause, describe the evidence, and ask one focused question when:

- antiplan or another specialist skill requests a user decision or sign-off;
- a Tier 2 or Tier 3 assumption has no answer in the project or global
  standards;
- the feature route is unclear between direct implementation, Lite, and Full;
- validator, critic, gate, or evidence review still fails after one repair;
- implementation cannot meet an AC, the diff exceeds ticket scope, or the
  repository state/dependency graph is ambiguous;
- a commit or required tool fails twice.

Do not weaken a gate, accept a failed review, discard user changes, or push to
resolve a blocker. After the user answers, continue from the updated artifacts
and state. If the run is interrupted, report the current stage, ticket stage,
changed files, completed checkpoint SHAs, and the next action.

## Completion

At every stage boundary, give a short progress update. On completion, report
the finished pipeline, ticket IDs, and checkpoint SHAs. On escalation, report
the blocker, evidence, and the question or action needed to continue.
