# PR Fix - Full Workflow

## Contents

- Step 1: Gather context (and 1b platform context)
- Step 2: Plan the work
- Step 3: Fix loop (3a read, 3b minimal fix, 3c verify and test-staleness check, 3d retry)
- Step 4: Handle test gap comments
- Step 5: Final verification
- Step 6: Report

## Step 1: Gather context

Fetch all pending review comments and the current diff.

```bash
gh pr view <PR> --json title,body,headRefName,baseRefName
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments
gh pr diff <PR>
```

Parse the comments into a work list. Each item needs:
- `id` — the comment ID
- `path` — file path
- `line` — line number
- `body` — the reviewer's comment text
- `suggestion` — extracted suggestion block, if any

**Skip** comments that are:
- Already resolved / outdated
- Pure questions with no actionable request
- Bot-generated status comments (CI, coverage, etc.)

### Step 1b: Platform context

If any comment targets platform-specific code (custom type
systems, platform-specific server APIs, in-house test harnesses), load
the matching platform-context skill or MCP server if one is installed
(e.g. a `<platform>-pr-context` skill) before attempting fixes. Do not
guess at platform APIs; general-purpose knowledge will not cover them.

## Step 2: Plan the work

Sort actionable comments into a fix order:

1. **Bug fixes** first (highest risk of cascading if deferred)
2. **Error handling** improvements
3. **Standards / style** fixes
4. **Test gaps** last (additive, lowest regression risk)

Within each category, group by file so related context is loaded once.

Display the plan to the user as a numbered checklist before starting:

```
Fix plan (N comments):
1. [Bug]  ExportImportDialog.tsx:101 — reset file input value
2. [Error] ExportImportDialog.tsx:91 — add logging to export catch
3. [Test]  csvParser.ts — add unit tests
```

## Step 3: Fix loop

Process each comment using a **fix-verify cycle**. This is the core of
the skill — never batch multiple fixes without verification between them.

```
┌─────────────────────────────────────┐
│          For each comment:          │
│                                     │
│  1. Read surrounding context        │
│  2. Apply minimal fix               │
│  3. Verify (type-check / lint)      │
│  4. If verify fails → revert, fix   │
│     the fix, re-verify (max 3 tries)│
│  5. Mark done, move to next         │
│                                     │
│  If 3 attempts fail → skip,         │
│  report to user, continue           │
└─────────────────────────────────────┘
```

### 3a. Read before writing

Before touching a file, read at minimum:
- The lines referenced by the comment (± 30 lines of context)
- Any imports or types the changed code depends on
- The reviewer's comment in full — do not skim

If the comment includes a `suggestion` block, prefer applying it
verbatim. Reviewer suggestions are pre-approved fixes.

### 3b. Apply minimal fix

**Golden rule: change only what the comment asks for.**

- Do NOT refactor nearby code
- Do NOT "also fix" something you noticed
- Do NOT rename variables the reviewer didn't mention
- Do NOT change formatting outside the fix scope
- If the fix requires changes in multiple files, make all of them
  before running verification

If the comment is ambiguous, implement the smallest reasonable
interpretation. The user can always ask for more.

**Docstrings and comments must explain *why*, not just label.** When a
review comment asks for "add a docstring" or "comment this", do not
ship a bare label drop like `"""ADR-CHAT-1: ..."""` or `# Per
Constitution P5`. The docstring must say what the code does
differently and why; an ADR pointer is allowed as a trailing reference
("Background: docs/ADR-CHAT-1.md"), not as a substitute for the
explanation. If the comment is "add a docstring" and you cannot
articulate the why in two sentences, ask the user — adding a label
without rationale is no better than the missing docstring.

### 3c. Verify (includes test-staleness check)

Run the project's verification commands after each fix. Detect the
stack and use the appropriate commands.

**Before running the suite, perform a test-staleness check:** if the
fix modified lines inside a function that has a claimed test, run
`mutation-critic` in single-mutant mode (return-early) against that
function. If the test still passes under the mutant, the test does
not actually exercise this branch — escalate:

```markdown
## TEST STALE — fix landed but test does not cover the branch

File: src/cart.ts
Function: applyDiscount
Test: cart.test.ts::"applies 10% discount"

A return-early mutant of `applyDiscount` did not fail the test. The
test passes whether the code runs or not. Options:

1. Strengthen the assertion (describe what changed, not that a value
   was returned). Recommended.
2. Add a second test that fails when the function short-circuits.
3. Acknowledge and proceed (requires explicit user "ack-stale").
```

Only after the staleness check is GREEN or ack'd, run the suite:

| Stack | Commands |
|-------|----------|
| TypeScript | `npx tsc --noEmit` |
| JavaScript (ESLint) | `npx eslint --no-warn <changed-files>` |
| Python | `python -m py_compile <file>` or `mypy <file>` |
| Go | `go build ./...` |
| Rust | `cargo check` |
| General | Whatever `scripts.lint` or `scripts.check` is in package.json |

If the project has a test suite and the fix is in a tested file, also
run the relevant tests:

```bash
# Example: run only tests related to the changed file
npx jest --findRelatedTests <changed-file> --passWithNoTests
```

### 3d. Retry on failure (max 3 attempts)

If verification fails after a fix:

```
Attempt 1: Fix applied → verify fails → read error
Attempt 2: Adjust fix based on error → verify again
Attempt 3: Different approach → verify again
Attempt 4: SKIP — report failure to user, revert to last good state
```

On each retry:
- Read the full error output
- Check if the error is in the code you just changed (your fault)
  or in unrelated code (pre-existing — skip)
- Apply the smallest correction that resolves the error
- Never widen the scope of changes to "fix" a cascading issue

If all 3 attempts fail, **revert the file to its state before the fix**
and add the comment to a "skipped" list with the reason.

## Step 4: Handle test gap comments

Test-related comments get special treatment because they are additive
(new files, not edits to existing code) and carry lower regression risk.

For each test gap comment:

1. Read the function/module under test thoroughly
2. Write tests following the project's existing test conventions:
   - Match naming: `*.test.ts`, `test_*.py`, `*_test.go`, etc.
   - Match location: colocated or in a `__tests__`/`test` directory
   - Match framework: jest, pytest, go test, etc.
3. Run the new tests to confirm they pass
4. If tests fail, fix the test (not the source) — the review comment
   asked for tests, not source changes

## Step 5: Final verification

After all fixes are applied, run a full verification pass:

```bash
# Type check the whole project
npx tsc --noEmit

# Run the full test suite (or at least related tests)
npx jest --passWithNoTests

# Check the total diff matches expectations
git diff --stat
```

If the full verification reveals a regression introduced by one of the
fixes, identify which fix caused it and apply the retry logic from
Step 3d to that specific fix only.

## Step 6: Report

Display a summary to the user:

```
## PR Fix Summary

**Fixed**: N of M comments
**Skipped**: K comments (with reasons)

### Changes made:
| # | File | Comment | Status |
|---|------|---------|--------|
| 1 | ExportImportDialog.tsx:101 | Reset file input value | Fixed |
| 2 | ExportImportDialog.tsx:91  | Add export error logging | Fixed |
| 3 | csvParser.ts               | Add unit tests          | Fixed |

### Skipped:
| # | File | Comment | Reason |
|---|------|---------|--------|
| — | — | — | — |

### Verification:
- Type check: PASS
- Tests: PASS (N passed, 0 failed)
```

Use this exact layout. Both tables always carry `#`, `File`, `Comment`
and the last column, even when every row touches the same file; put the
file in the `File` cell, not in a heading. Skipped table columns are
`# | File | Comment | Reason`. End the output at the Verification list:
no prose after it, and put notes in the Comment, Status or Reason cells.

Do NOT commit or push automatically. Let the user review the changes
and decide when to commit.
