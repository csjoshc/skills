---
name: pr-fix
description: "Works through PR review comments one at a time with a verification gate after each fix. Use when addressing PR review feedback."
---

# PR Fix

Address PR review comments systematically: one at a time, with a
verification gate after each fix to prevent regressions.

## Invocation

```
/pr-fix <owner/repo> <pr-number>
```

If already on the PR branch, detect the repo and PR number via `gh pr view`.

## Safety rules

These rules prevent the fix process from injecting new problems:

1. **One fix at a time** — never batch unrelated changes into a single
   edit. Each comment gets its own read-fix-verify cycle.

2. **Minimal diff** — touch only the lines the comment addresses. If
   you find an unrelated issue, do not fix it. Mention it to the user
   separately.

3. **Verify after every fix** — never skip verification, even for
   "trivial" changes. Trivial changes break builds too.

4. **Revert on repeated failure** — if a fix can't pass verification
   in 3 attempts, revert it entirely. A skipped comment is better
   than a broken build.

5. **Never modify the reviewer's suggestion** — if the comment contains
   a `suggestion` block, apply it exactly as written. If it doesn't
   compile, report the issue to the user rather than "improving" it.

6. **Preserve existing behavior** — unless the comment explicitly asks
   for a behavior change, the fix should be behavior-preserving. Add
   logging without changing control flow. Add types without changing
   runtime behavior.

7. **Don't cascade** — if fixing comment A reveals that comment B's
   fix needs to be different, finish A's cycle completely before
   starting B. Do not interleave fixes.

## Workflow

Full step detail, commands and templates: [workflow.md](workflow.md). Read it before the first fix.

1. **Gather** pending review comments and the diff. Skip resolved, outdated, question-only and bot comments.
2. **Plan** the order: bug fixes, error handling, standards/style, test gaps last. Show the numbered plan to the user first.
3. **Fix loop** per comment: read context, apply the minimal fix, verify, retry up to 3 times, else revert and skip.
4. **Test gap comments:** add new tests that match project conventions; if they fail, fix the test, not the source.
5. **Final verification** of the whole project, then report.

Before the suite runs after a fix, do the **test-staleness check**: if the fix touched a function with a claimed test, run `mutation-critic` in single-mutant mode (return-early). If the test still passes, emit the `TEST STALE` block from [workflow.md](workflow.md) and wait for the user (strengthen the assertion, add a test, or explicit `ack-stale`).

Comment handling for suggestion blocks and common types (logging, tests, types, renames, null checks, docstrings, slug renames): [comment-types.md](comment-types.md).

## Report

End with this summary:

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
