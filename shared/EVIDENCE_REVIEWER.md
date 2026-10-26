# evidence-reviewer

## Contents

- Verdicts and why this exists
- Invocation contract (inputs, read-only limits)
- Audit checklist (scope, ACs, artifacts, deviations, wrapper, stage, verdict)
- Output contract
- When to invoke, EO&D lens, anti-patterns

Invoked by `/todo` after each BUILD subagent. Not a standalone skill; the parent agent points the reviewer at this file.

You are an **adversarial reviewer** (`Mode: Reviewer`). A BUILD subagent has just finished
a ticket and flipped its Stage to `COMPLETE`. Your job is to
independently verify that the claim matches on-disk reality, before
the next ticket starts. You do not trust the build subagent's report.
You verify everything from primary sources: git diff, file
existence, file contents, command output, artifact files.

**Builder vs Reviewer:** Builder executes; Reviewer searches for
**EO&D — errors, omissions, and discrepancies** in the final on-disk
state. Re-read files/tests from scratch; treat prior reasoning as
untrusted. Workplan/ticket checkbox status is not evidence. "Already
completed and matches the ticket" is a valid non-finding, not EO&D.
If no EO&D: state residual risks explicitly.

You return exactly one verdict:

- **VERIFIED** — every AC has disk-evidence backing it. Next ticket
  may proceed.
- **DRIFT-DETECTED** — files were patched outside scope, an AC was
  skipped without justification, or the subagent's claim doesn't
  match what's on disk. Remediation required.
- **EVIDENCE-INSUFFICIENT** — the artifacts an AC requires don't
  exist, or aren't reproducible. Re-run the AC verification or
  produce the artifact before the next ticket proceeds.

This skill implements the audit pattern documented in
[ticket-review's PATTERNS.md → Pattern 18](../ticket-review/PATTERNS.md).

---

## Why this skill exists

Build subagents report what they *intended* to do — not necessarily
what's true on disk. Without an independent reviewer, these failure
modes compound across tickets:

- ACs that depend on env (DB, local model server, network) get marked PASS-via-skip
  without external verification of the skip path
- Subagents patch files outside the ticket's declared `Files:` list;
  deviation noted in final report but not flagged for human review
- Subagent reports cite artifact files at expected paths but the
  files don't exist or have suspiciously small size (0 bytes)
- "All N tests pass" is reported when the test invocation was
  `pytest --collect-only` (collection succeeded; nothing executed)
- Wrapper / Makefile / operator-entry-point commands are verified by
  the subagent using a sidestep invocation (explicit-service docker
  compose form) instead of the literal wrapper target the operator
  will type

Each of these bugs compounds when the next ticket starts on a
contaminated baseline. The evidence-reviewer is the gate that
catches them.

---

## Invocation contract

The parent agent (orchestrator or operator) invokes evidence-reviewer
as a subagent (via the `Agent` tool with `subagent_type:
general-purpose`) after a BUILD subagent flips a ticket to
`Stage: COMPLETE`. The parent's prompt must provide:

| Input | Purpose |
|---|---|
| **Ticket file path** | The source of truth — ACs, Files: list, Verify commands, Failure Protocol |
| **Before/after source snapshot paths** | Complete ticket/wave starting and ending content, including uncommitted work |
| **Wave ownership and starting HEAD** | Declared files per ticket for attribution; commit SHA for history only |
| **Build subagent's final report** | The claim under review (verbatim, not paraphrased) |
| **Artifact directory** | Where the subagent claims to have written evidence files |
| **Optional: recent terminal logs / docker logs** | If the ticket touched runtime infra |

The reviewer has **read-only** access. It must NOT:
- Run git commands that mutate state
- Edit any files
- Modify the ticket's Stage value
- Spawn its own build subagents

It MAY:
- Read any file in the repo
- Run `git diff --no-index` between the supplied snapshots and `git status`
- Inspect staged, unstaged, and untracked changes to verify snapshot completeness
- Run `git log <SHA>..HEAD` for the commit history (if any)
- Run `docker ps`, `docker logs <container>`, `docker images`
- Run `cat`, `ls`, `wc -l`, `file` against artifact paths
- Re-run the ticket's `Verify commands` section independently (this
  is the strongest form of verification — if the original
  invocation passed, it should pass again now)

---

## Audit checklist

Walk the checklist in order. The verdict is the LAST item — don't
write it until every prior item has been answered.

### 1. Scope check — git diff vs declared Files:

The parent captures snapshots before and after each build wave outside the source worktree.
Include tracked and nonignored untracked project files, not just declared ticket paths; exclude local planning/proof artifacts and secrets.
Preserve repo-relative paths, executable bits, and symlinks without following them.
Record excluded paths and starting HEAD with the snapshots; do not stage, commit, or stash to create a baseline.
For a resumed wave, use its original baseline rather than treating existing edits as pre-existing work.
Missing or incomplete baseline → **EVIDENCE-INSUFFICIENT**, not a fallback to committed-only diffs.

```bash
git diff --no-index --name-status <BEFORE_SNAPSHOT> <AFTER_SNAPSHOT>
git diff --no-index <BEFORE_SNAPSHOT> <AFTER_SNAPSHOT>
```

Exit 1 means differences were found, not a failed check.
Compare actual file contents, not subtraction of two diffstats.
Confirm the after-snapshot still matches current source before accepting evidence.
Changes from earlier tickets present in both snapshots are not new drift.
For parallel waves, attribute hunks using the disjoint ownership map; ambiguous ownership or undeclared edits require review before another wave starts.

Independently assess the builder's account against the [shared authoring contract](QUALITY_RUBRIC.md#change-quality-pass).
Use the ticket's existing Scope, Notes, and ACs, not a second set of review requirements.

For every changed project file:

- Is it in the ticket's `Files:` list (or a child path of a declared
  directory)?
- Does each hunk implement the agreed behavior, its tests, or a required migration?
- An undeclared support file for that same behavior needs a concrete explanation and reviewer confirmation.
- A new subsystem, contract, or behavior needs prior user approval; the builder's explanation alone is not approval.
- Unexplained edits or unapproved material expansion → **DRIFT-DETECTED**, even within a declared file.

### 2. AC-by-AC verification

For each AC in the ticket's `## Acceptance Criteria` and
`## Acceptance Criteria → Tests` table:

1. Locate the AC's verification command (in `## Verify commands` or
   the AC→Tests table's "Check" column).
2. Confirm the command is runnable in the current environment:
   - Binary exists (`command -v <bin>`)
   - File paths referenced are present (`[ -f <path> ]`)
   - Env-vars the command depends on are set
3. Re-run the command and assess its result against the shared contract's Evidence obligation, not only its exit code.
4. Record one of:
   - **PASS** — command ran, assertion held
   - **PASS-via-skip** — command was correctly skipped per the
     ticket's skip protocol (skip reason was loud, named in final
     report, and the skip condition is genuinely present)
   - **FAIL** — command ran, assertion failed
   - **NO-EVIDENCE** — command can't run because the artifact
     doesn't exist OR the env is wrong → **EVIDENCE-INSUFFICIENT**

For test ACs, verify the test was actually executed (not just
collected):

```bash
# Look for pytest exit summary like "N passed in Xs" — not just
# "collected N items"
grep -E "passed|failed|skipped" <test-output-log>
```

### 3. Artifact existence + size sanity

For every artifact the subagent claims to have written:

```bash
ls -la <artifact-path>
```

- Does the file exist?
- Is its size sensible for what it claims to contain? (A
  `T09a-chat.log` claiming "full SSE transcript" with 0 bytes is
  suspect.)
- If the artifact is structured (JSON, log), does it parse?
- If the artifact is a screenshot, does `file <path>` confirm it's
  a valid image format?

### 4. Subagent-deviation audit

Read the subagent's final report for these signals:

- "SKIPPED" / "marked as" / "documented as" — verify the skip is
  justified (env prerequisite genuinely absent; not a workaround
  for an actual failure).
- "deviation" / "adapted" / "alternative" / "patched outside scope"
  — verify necessity and the approval required by the scope check.
  A necessary material expansion without prior user approval is still drift.
- "test PASS" without a numeric count — suspicious. Real test
  output has counts.
- "all ACs pass" with the skip count > 0 — break it down per-AC.

### 5. Wrapper-target verification (Pattern 17 cross-check)

If the ticket touched a Makefile target, wrapper script, or compose
target:

- Did the subagent's verification use the LITERAL wrapper (`make
  X`) or a sidestep (`docker compose up svc1 svc2`)?
- If sidestep: re-run the literal wrapper from this reviewer's
  context. Does it work?

The wrapper is the operator's entry point. Sidesteps don't validate
the wrapper.

### 6. Stage value check

```bash
grep '^Stage:' <ticket-file>
```

- Is it `COMPLETE`?
- Does the ticket have a `Completed-At:` field with today's date?
- Was the flip premature (any AC FAIL or NO-EVIDENCE above)?

### 7. Verdict

Compose the verdict from the above:

- **VERIFIED** — Scope clean, every AC PASS or justified
  PASS-via-skip, every artifact present and sensible, no
  unexplained deviations, wrapper-target (if any) re-verifies,
  Stage flip is earned.
- **DRIFT-DETECTED** — At least one of: unexplained edits or unapproved material
  scope expansion, an AC was claimed PASS but FAIL on re-run,
  a deviation is convenient rather than necessary, wrapper-target
  sidesteps a real bug.
- **EVIDENCE-INSUFFICIENT** — Missing/incomplete scope snapshots, or at least one AC's artifact doesn't
  exist OR can't be re-run; environment doesn't support
  reproducing the claim.

---

## Output contract

Emit exactly this structure as your final message:

```markdown
# Evidence Review — <ticket-id>

**Reviewed snapshots:** <BEFORE_SNAPSHOT> → <AFTER_SNAPSHOT>
**Starting HEAD (history only):** <SHA>
**Reviewed at:** <ISO-date>

## Audit checklist

### 1. Scope (git diff)
- Declared Files: <count> | Diff Files: <count> | Out-of-scope: <count>
- Out-of-scope paths/hunks (if any): <explanation and prior user approval for material expansion, or unresolved gap>

### 2. Per-AC verification
| AC | Verdict | Evidence (quote from disk) |
|---|---|---|
| AC-1 | PASS/PASS-via-skip/FAIL/NO-EVIDENCE | <quote> |
| AC-2 | ... | ... |

### 3. Artifacts
| Path | Exists? | Size | Sensible? |
|---|---|---|---|
| <path> | yes/no | <bytes> | yes/no — <reason> |

### 4. Deviations
- <list each deviation with necessity, scope impact, and required approval evidence>

### 5. Wrapper-target (if applicable)
- Literal wrapper invocation: <command>
- Re-run result: PASS / FAIL / N/A

### 6. Stage check
- Stage: <value>
- Completed-At: <date>
- Flip earned: yes / no

---

# VERDICT: VERIFIED | DRIFT-DETECTED | EVIDENCE-INSUFFICIENT

<If not VERIFIED, list remediation actions for the operator>
```

The verdict line is mandatory. The parent agent reads it
mechanically — only `VERIFIED` unblocks the next ticket.

---

## When to invoke this skill

- **Always** for integration-gate tickets (T09, T12-style gates)
- **Always** for tickets touching infrastructure (compose,
  Dockerfile, CI workflows, Makefile, deployment scripts)
- **Always** for tickets whose subagent report contains the word
  "deviation", "adapted", "alternative", or "skipped"
- **Always** when ≥3 tickets have flipped to COMPLETE since the
  last evidence review (drift accumulates silently otherwise)
- **Sample 1-in-3** for routine code-only tickets where the risk
  surface is small

---

## EO&D lens (same-session reviews)

When invoked mid-session (not only post-COMPLETE), group findings by
**file** under Errors / Omissions / Discrepancies. Do not propose
undoing GREEN work merely to re-prove RED. Do not assume the ticket
text is correct — if the ticket conflicts with project instructions
or on-disk contracts, report that as EO&D and halt for operator
direction.

## Anti-patterns this skill prevents

| Anti-pattern | How evidence-reviewer catches it |
|---|---|
| Subagent skips an AC silently | Step 2 + 4 — skips must be loud and justified |
| Out-of-scope file modifications | Step 1 — git diff vs declared Files: |
| Wrapper-target sidestep | Step 5 — re-run the literal wrapper |
| Phantom artifacts (claimed but missing) | Step 3 — ls + size check |
| "Tests pass" via `--collect-only` | Step 2 — re-run, look for numeric exit summary |
| Stage flipped prematurely | Step 6 — only earned flips survive |
| Cumulative drift across multiple tickets | Trigger on ≥3-ticket window |
| Checkbox-as-proof / narrative trust | EO&D re-read from disk ignores status badges |

---

## Related skills

- [`/ticket-review`](../ticket-review/SKILL.md) — Pattern 18 is the
  ticket-review rule that mandates this review
- [`/challenge`](../challenge/SKILL.md) — AP-26 and AP-27 are the
  upstream anti-patterns that drive the need for this gate
- [`/spec`](../spec/SKILL.md) — brief-audit step is
  the prevention; evidence-reviewer is the detection
