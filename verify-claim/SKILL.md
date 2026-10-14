---
name: verify-claim
description: "Blocks done or fixed claims without proof: passing tests, a regression test for bugs, screenshots for UI, a curl for APIs. Use when about to report completion or open a PR."
---

# verify-claim

Catches false completion claims before they reach the user. Every "done"
must be backed by machine-checkable evidence. If the evidence does not exist,
this skill blocks the claim and emits a specific list of what's missing.

## When to invoke

Always invoke before:

- Reporting "task complete" to the user
- Running `pr-create`
- Closing out a `ticket-critic` or `spec-writer` cycle
- Writing the `## Evidence` section of a PR description
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
| Docstring / inline-doc addition | Content explains *why*, not just labels an artifact (ADR/ticket ID alone fails) | Excerpt of the new docstring + a one-line "what a cold reader learns" summary |
| Package / module deletion | Cross-reference scrub ran clean (or remaining hits explicitly resolved) | `git grep` output showing zero residual mentions across docs, diagrams, CI, helm, manifests |
| Rename (file / config / endpoint) | All referrers updated | `git grep -l <old-name>` output empty, OR each remaining mention is explicitly justified |

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

If the gap table is empty → pass. Delete `CLAIM_UNVERIFIED.md` if it exists. Agent may proceed with the claim.

If non-empty → emit:

```markdown
## CLAIM UNVERIFIED — proceeding with user caution

The following claims lack evidence:

<paste gap table>

Options:
1. Generate the missing evidence now (recommended)
2. Downgrade the claim ("attempted" / "likely works" / "needs verification")
3. Explicit user override: user types "override: <reason>"
```

Write the block to `CLAIM_UNVERIFIED.md` at the repo root (only there), and
add `CLAIM_UNVERIFIED.md` to `.git/info/exclude` so it is never committed.
The `verify-claim-gate` hook blocks `git commit` and `gh pr create` while it exists.

### Marker lifecycle

- **Evidence produced:** re-run this skill; a clean pass deletes the marker.
- **Claim downgraded:** drop that row; delete the marker once no rows remain.
- **User override:** only on the user's own `override: <reason>`. Delete the
  marker and record the reason in the PR body's `## Evidence` section or the final report. Never
  override on your own judgment.

The marker catches shipping past a failed check. It cannot catch a check
that never ran; the "always invoke" rule above covers that.

## Regression test requirement (bug fixes)

For any diff that a commit message or PR describes as a "fix":

1. Check out the state before the fix in a separate worktree, not with `git stash` (the stash is shared by every worktree of the repo, so another session can pop it):
   `pre=$(mktemp -d) && git worktree add --detach "$pre" HEAD~1`, then copy the new test file(s) into `$pre`.
2. Run the new test(s) in `$pre`. They MUST fail. If they pass on the broken state, the test does not exercise the bug.
3. Run them again on HEAD. They MUST pass. Then `git worktree remove "$pre"`.
4. Record both outputs as the Before and After in the PR body's `## Evidence` section.

The test must sit at a correct seam: one that exercises the real bug pattern as it occurs at the call site.
A test at a seam too shallow to reproduce the bug (one caller when the bug needs several, a unit test that skips the triggering chain) gives false confidence.

If no correct seam exists, that is the finding.
Record it as a gap row and in the PR body's `## Evidence` section: the fix is unverified because the architecture blocks a regression test, and name the seam that would be needed.
The user can ship it with an `override: <reason>`; the missing seam is a candidate for `cleanup` or a follow-up ticket.
(Seam rule adapted from Matt Pocock's `diagnosing-bugs` skill, MIT.)

If a correct seam exists and no new test is in the diff, the fix is not verified.

## Interaction with other skills

- `pr-create`: refuses to run if `CLAIM_UNVERIFIED.md` exists at repo root.
- `pr-review`: the Spec-Traceability lens reads the same gap table.
- `pr-fix`: after each fix, reruns verify-claim for that specific comment's
  scope before moving to the next.
- `project-onboarding/WORKFLOW_GATES.md`: lists verify-claim at phase transitions.

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
