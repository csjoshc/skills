---
name: verify-claim
description: >-
  Evidence gate that blocks any "task complete" / "done" / "fixed" claim without
  corroborating proof. Requires passing test output, a screenshot + URL for UI
  changes, a regression test for bug fixes, or a curl response for API changes.
  Use when the agent is about to report completion, when opening a PR, or whenever
  the agent is about to claim success.
---

# verify-claim

Catches false completion claims before they reach the user. Every "done"
must be backed by machine-checkable evidence. If the evidence does not exist,
this skill blocks the claim and emits a specific list of what's missing.

## When to invoke

Always invoke before:

- Reporting "task complete" to the user
- Running `create-pr`
- Closing out a `ticket-critic` or `spec-writer` cycle
- Writing the "Changes" section of a PR description
- Checking off an AC

Skip only for:

- Documentation-only edits (`.md`, `.txt`)
- Rename-only diffs (no logic change, verified via `git log --name-status`)

## Evidence requirements

Determine the change type by reading the diff. Apply the matching requirement.

| Change type | Required evidence | Format |
|---|---|---|
| Bug fix | Regression test that fails on `HEAD~1`, passes on `HEAD` | `pytest`/`jest` output, both runs |
| New feature | At least one test per AC, all passing | Test runner output, AC→test table |
| Refactor | Full suite passes; no behavior diff | Test runner output + `git diff --stat` |
| UI change | Screenshot at visible URL | `.png` file + URL + viewport size |
| API change | Curl/httpie against running server | Request + full response, incl. status |
| Infra / config | Command output proving the change works | Shell output |
| Perf improvement | Before/after measurement | Two numbered runs, units, environment |

## Workflow

### Phase 1: Classify the claim

Read the most recent agent message. Extract every success claim:

- "done", "complete", "fixed", "implemented", "passes", "works", "ready"
- Implicit claims: "I've added X", "Updated Y", "Here's the Z"

For each claim, map to the change type table above.

### Phase 2: Locate evidence

For each claim, find its evidence in the session or on disk.

```bash
# Tests
git log --since="1 hour ago" --name-only | grep -E 'test_|\.test\.'
ls /tmp/*test*.txt /tmp/*coverage*.txt 2>/dev/null

# Screenshots
ls /tmp/*.png /tmp/screenshots/ 2>/dev/null

# Curl outputs
grep -l "HTTP/" /tmp/*.txt 2>/dev/null
```

### Phase 3: Gap check

For every claim with no evidence, add an entry to the gap table:

```markdown
| Claim | Required evidence | Gap |
|-------|-------------------|-----|
| "Fixed null crash in parseConfig" | Regression test | No test named `test_parseConfig_null*` in diff |
| "Added dark mode toggle" | Screenshot at URL | No PNG found, no URL mentioned |
```

### Phase 4: Block or pass

If the gap table is empty → pass. Agent may proceed with the claim.

If non-empty → emit:

```markdown
## CLAIM UNVERIFIED — proceeding with user caution

The following claims lack evidence:

<paste gap table>

Options:
1. Generate the missing evidence now (recommended)
2. Downgrade the claim ("attempted" / "likely works" / "needs verification")
3. Explicit user override: user types "override" to bypass
```

Write the block to `CLAIM_UNVERIFIED.md` at the repo root. `create-pr` and
`pr-review` should refuse to run while this file exists.

## Regression test requirement (bug fixes)

For any diff that a commit message or PR describes as a "fix":

1. Checkout the state before the fix: `git stash` or `git worktree add`
2. Run the new test(s) — they MUST fail. If they pass on the broken state,
   the test does not exercise the bug.
3. Return to HEAD, run again — they MUST pass.
4. Record both outputs in the evidence section of the PR body.

If no new test is in the diff, the fix is not verified. Ask the user to
add one or explicitly acknowledge they want to ship without regression
coverage.

## Interaction with other skills

- `create-pr`: refuses to run if `CLAIM_UNVERIFIED.md` exists at repo root.
- `pr-review`: the 5th Spec-Traceability Auditor reads the same gap table.
- `pr-fix`: after each fix, reruns verify-claim for that specific comment's
  scope before moving to the next.
- `workflow-guard`: injects verify-claim at phase transitions.

<!-- pattern: common-rationalizations -->
## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It compiled, so it works" | Type-check is not a behavior test. Run the thing. |
| "I added the test, that's enough" | Did the test fail before the fix? If not, you wrote a tautology. |
| "The CI link will land later" | If you can't paste evidence now, the claim isn't ready. |
| "It worked locally" | Reproduction evidence (command + output) or it didn't happen. |

## Hard rules

- Never mark a task done if `CLAIM_UNVERIFIED.md` exists and the user has
  not explicitly overridden.
- Never fabricate evidence. Missing test output is missing — do not
  invent "`5 passed`" lines.
- Never count "looks right" or "should work" as evidence. Observation > reasoning.
- Never skip this skill to save time. The cost of a false completion claim
  is always higher than the cost of verification.

## Output contract

Emit exactly one of:

1. `VERIFIED: N claims, all evidenced.` + one-line summary per claim.
2. `CLAIM_UNVERIFIED.md` written, table of gaps, recommended next action.
