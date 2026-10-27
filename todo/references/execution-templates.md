# Execution Templates

Subagent briefs. Pointers, not pasted ticket bodies.
The same text is the per-agent prompt inside a harness run (auto-driver.md,
Runner selection); the ticket path is the only argument.

## Contents

- build-ticket — one ticket, one subagent
- build-ticket-resume — pick up Stage: BUILD
- slice-gate-review — independent gate review

## build-ticket

```
You are implementing one ticket. The ticket file is the source of truth.

**Ticket:** <absolute path to .tickets/<NNN-slug>.md>
**PRD (if present):** <absolute path>
**DAG (if present):** <absolute path to .plan/task-sequence.md>
**Exploration notes (if present):** <absolute path outside the repo>

1. Read the ticket, its Read-First files, any pointers, and the change-quality
   pass in `~/.skills/shared/QUALITY_RUBRIC.md`.
   Carry its authoring contract from the ticket into implementation and the final report.
2. Set Stage: BUILD.
3. Invoke tdd. Phase 0 writes .tickets/tdd/toq-<id>.yaml. Then red-green
   against the ticket ACs. Do not skip Phase 0.
   If the ticket changes frontend UI, invoke `/ui` for visual implementation
   and browser review within ticket scope; keep `/tdd` as owner of AC order.
4. When ACs are green, run the project's lint + typecheck.
   Fix issues introduced by this change; report pre-existing failures separately.
5. Review the final diff against the contract, then invoke verify.
   Do not claim done until it passes.
6. Do not commit. Return the concise, updated account of the change and
   per-AC evidence (command + result), with remaining risks or questions.
   Do not repeat the ticket or substitute a file inventory for the account.
7. Set Stage: COMPLETE and Completed-At: <today> only when verify passes.
   Do not start another ticket.

If tdd or verify fails: do not flip COMPLETE.
Leave Stage: BUILD or FAILED, and report the blocker.

Auth, public API, data-model, or security gaps: stop and report the
question. Do not guess Tier 3.
```

## build-ticket-resume

```
You are resuming a ticket whose Stage is BUILD.

**Ticket:** <absolute path>
**TOQ (if exists):** <absolute path to .tickets/tdd/toq-<id>.yaml>
**PRD / DAG (if present):** <absolute paths>

1. Read the ticket and TOQ. If no TOQ, run tdd Phase 0 first.
2. git diff against the ticket ACs: which are green, which are still red.
3. If TOQ diff_base is behind HEAD, re-scope.
4. Resume tdd at the first un-green AC, applying the shared change-quality pass.
5. Then follow build-ticket steps 4-7.

Do not re-derive scope or rewrite already-passing code.
```

## slice-gate-review

```
You are reviewing slice <slice-id>. Non-gate tickets are COMPLETE.
The gate ticket is NEW.

**Gate ticket:** <absolute path>
**Slice tickets:** <absolute paths>
**PRD parity / demo policy:** .plan/PRD.md (if present)

1. Collect the gate's proof artifact to the path the ticket names.
2. Independent review (subagent or fresh session; inline only if needed,
   mark run: inline):
   - Every gate AC has named evidence in the artifact.
   - The artifact hits real services, not mocks.
   - Failure paths have visible assertions.
3. PASS → Stage COMPLETE. FAIL → leave NEW, name the missing evidence.
   Do not start the next slice on FAIL.
```
