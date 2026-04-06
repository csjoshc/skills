# PR Fix — Complete Workflow

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

### Step 1b: C3 platform context (backend changes)

If any comment targets C3 backend code — `.c3typ` files, Type definitions, `fetch()` / `evalMetric()` calls, server-side JavaScript actions, logger initialization (`PerLogger`), test setup (`Jasmine`, `TestApi`), or C3 platform patterns — query the **C3AI-MCP** server before attempting fixes.

**What qualifies as C3 backend code:**
- `.c3typ` / `.c3doc` type definition files
- Server-side `.js` files using C3 APIs (`Type.fetch()`, `.merge()`, `.upsert()`, `Obj.make()`, `HttpRequest`, `ContentValue`, etc.)
- Test files using C3's `Jasmine` / `TestApi` harness
- `PerLogger` or `Log` logging calls
- `seed/` data files or `canonicalize` scripts
- C3 package metadata (`package.json` with `c3` dependencies)

**How to use C3AI-MCP:**
- Query the MCP for documentation on any C3 API or Type referenced in the comment or surrounding code that you are unsure about
- Use MCP-provided context to ensure your fix uses correct C3 syntax (e.g., `fetch()` filter expressions, `spec` parameter conventions, valid Type method signatures, proper `PerLogger` initialization)
- For test-related comments, query the MCP for the project's C3 test harness patterns (`Jasmine` setup, `TestApi` usage, seed data conventions) before writing or modifying tests

**Do NOT** guess at C3 APIs — it is a proprietary platform and general-purpose knowledge will not cover its Type system, runtime behavior, or API surface. Always query the MCP first.

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

Process each comment using a **fix-verify cycle**. This is the core of the skill — never batch multiple fixes without verification between them.

### 3a. Read before writing

Before touching a file, read at minimum:
- The lines referenced by the comment (± 30 lines of context)
- Any imports or types the changed code depends on
- The reviewer's comment in full — do not skim

If the comment includes a `suggestion` block, prefer applying it verbatim. Reviewer suggestions are pre-approved fixes.

### 3b. Apply minimal fix

**Golden rule: change only what the comment asks for.**

- Do NOT refactor nearby code
- Do NOT "also fix" something you noticed
- Do NOT rename variables the reviewer didn't mention
- Do NOT change formatting outside the fix scope
- If the fix requires changes in multiple files, make all of them before running verification

If the comment is ambiguous, implement the smallest reasonable interpretation. The user can always ask for more.

### 3c. Verify

Run the project's verification commands after each fix. Detect the stack and use the appropriate commands:

| Stack | Commands |
|-------|----------|
| TypeScript | `npx tsc --noEmit` |
| JavaScript (ESLint) | `npx eslint --no-warn <changed-files>` |
| Python | `python -m py_compile <file>` or `mypy <file>` |
| Go | `go build ./...` |
| Rust | `cargo check` |
| General | Whatever `scripts.lint` or `scripts.check` is in package.json |

If the project has a test suite and the fix is in a tested file, also run the relevant tests:

```bash
npx jest --findRelatedTests <changed-file> --passWithNoTests
```

### 3d. Retry on failure (max 3 attempts)

```
Attempt 1: Fix applied → verify fails → read error
Attempt 2: Adjust fix based on error → verify again
Attempt 3: Different approach → verify again
Attempt 4: SKIP — report failure to user, revert to last good state
```

On each retry:
- Read the full error output
- Check if the error is in the code you just changed (your fault) or in unrelated code (pre-existing — skip)
- Apply the smallest correction that resolves the error
- Never widen the scope of changes to "fix" a cascading issue

If all 3 attempts fail, **revert the file to its state before the fix** and add the comment to a "skipped" list with the reason.

## Step 4: Handle test gap comments

Test-related comments get special treatment because they are additive (new files, not edits to existing code) and carry lower regression risk.

For each test gap comment:

1. Read the function/module under test thoroughly
2. Write tests following the project's existing test conventions:
   - Match naming: `*.test.ts`, `test_*.py`, `*_test.go`, etc.
   - Match location: colocated or in a `__tests__`/`test` directory
   - Match framework: jest, pytest, go test, etc.
3. Run the new tests to confirm they pass
4. If tests fail, fix the test (not the source) — the review comment asked for tests, not source changes

## Step 5: Final verification

After all fixes are applied, run a full verification pass:

```bash
npx tsc --noEmit
npx jest --passWithNoTests
git diff --stat
```

If the full verification reveals a regression introduced by one of the fixes, identify which fix caused it and apply the retry logic from Step 3d to that specific fix only.

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

Do NOT commit or push automatically. Let the user review the changes and decide when to commit.
