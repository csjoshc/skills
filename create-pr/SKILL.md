---
name: create-pr
description: >-
  Creates GitHub PRs from local changes with proper branch management, evidence collection,
  and rich descriptions. Handles branch creation from dirty main, UI recording attachments
  via browser tools, and backend test/coverage log attachments. Use when the user says
  "create PR", "open PR", "push and PR", "submit changes", or wants to finalize work
  for review.
---

## TL;DR (Quick Start)

Creates a GitHub PR from local changes with proper git hygiene, descriptive branch naming, and evidence-based descriptions (UI recordings for frontend, test logs for backend).

**When to use:** "create PR", "open PR", "push and PR", "submit changes".

**Invocation:**
```bash
git checkout -b feat/new-feature
git commit -m "feat: add feature"
git push -u origin HEAD
gh pr create --title "feat: add feature" --body "$(cat <<'EOF'
## Summary
- Detailed explanation...
EOF
)"
```

## Decision Tree

1. **Are you on `main` with uncommitted changes?**
   - YES → Create a feature branch first (`git checkout -b feat/...`).
   - NO → Continue.

2. **Is this a UI change?**
   - YES → **MANDATORY** Capture screenshots/recordings before pushing.
   - NO → Continue.

3. **Does the project have a test suite?**
   - YES → **MANDATORY** Run tests and include logs in PR body.
   - NO → Note manual verification steps.

4. **Is the change trivial (<5 lines, non-functional)?**
   - YES → Skip evidence collection; denote as "Trivial change".
   - NO → Full Phase 3 evidence collection.

## Workflow

```
Phase 1: Git Preparation
Phase 2: Commit & Push
Phase 3: Evidence Collection (conditional)
Phase 4: Create PR with rich description
```

## Phase 1: Git Preparation

1. Run `git status` and `git log --oneline -5` to assess state
2. Determine current branch and divergence from remote
3. If on main with uncommitted/unpushed changes → create feature branch
4. If already on feature branch → continue on it
5. Verify no secrets in staged files (.env, credentials, tokens)

### Branch from dirty main

```bash
git add -A
git checkout -b <type>/<short-description>
```

**Branch name rules:** lowercase, hyphens only, max 50 chars, derive from diff content. Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`.

### Already on feature branch

```bash
git fetch origin
git log --oneline origin/main..HEAD
```

## Phase 2: Commit & Push

```bash
git add -A
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body — explain WHY, not WHAT>
EOF
)"
git push -u origin HEAD
```

**Commit conventions:** First line `type(scope): summary` under 72 chars. Body explains motivation, not line-by-line changelog.

## Phase 3: Evidence Collection

> **Evidence files must NOT persist in final branch HEAD.** Use the ephemeral commit pattern.

Determine change type by analyzing the diff:
- UI changes? → Phase 3A
- Backend changes? → Phase 3B
- Both? → Do both

### 3A: UI Evidence (frontend changes)

**MANDATORY** for UI-heavy PRs. Capture when: visual changes, form/input changes, modal/dialog changes, navigation/flow changes, theme changes, responsive changes.

**In Cursor (IDE browser available):**
1. Navigate to running app using browser tools
2. Lock browser, walk through each affected user flow, take screenshots at key states
3. For theme changes: capture both light and dark mode
4. For form changes: show empty, filled, and error states
5. Unlock browser, collect screenshots into PR description

**Screenshot requirements:**
1. Change in default state (REQUIRED)
2. Dark mode screenshot if theme exists (REQUIRED if applicable)
3. Interactive states: empty → filled → error (REQUIRED for forms)
4. Before/after comparison if refactoring

**Screen recording (preferred for complex flows):** Use Chrome DevTools MCP or cursor's built-in recording.

**Minimum evidence for ANY frontend PR:**
1. Screenshot/description of change in default state (REQUIRED)
2. Both themes shown if dark mode exists (REQUIRED if applicable)
3. Key interaction states documented if interactive (REQUIRED if applicable)
4. Screen recording for complex flows (RECOMMENDED)

### 3B: Backend Evidence (backend changes)

**MANDATORY** for code changes. Capture when: backend code changes, configuration changes, database/schema changes, external service integration, refactoring.

1. Run the project's test suite (REQUIRED)
2. Capture test output (pass/fail summary) (REQUIRED)
3. Run coverage if available (REQUIRED if applicable)
4. Format results for PR description

```bash
# Python projects
python -m pytest --tb=short -q 2>&1 | tail -20 > /tmp/test-results.txt
python -m pytest --cov --cov-report=term-missing 2>&1 | tail -30 > /tmp/coverage.txt

# Node projects
npm test 2>&1 | tail -20 > /tmp/test-results.txt
npx vitest --coverage 2>&1 | tail -30 > /tmp/coverage.txt
```

**Test output requirements:** Pass/fail summary with counts; failed test names if any; coverage report if available; error messages from failures.

Save logs to `/tmp/` only. Paste into PR body as fenced code blocks. For large logs, use the ephemeral commit pattern from Phase 3A.

## Phase 4: Create PR

1. Analyze ALL commits on the branch (not just latest)
2. Draft PR title and body
3. Create PR using gh cli
4. If evidence was collected, edit PR body to include it
5. Return the PR URL

See [templates/pr-body.md](templates/pr-body.md) for PR body template and ephemeral commit pattern.

## Conditional Paths

**Trivial change (< 5 lines, single file, no functional change):** Skip Phase 3 only if truly trivial (typo fix, comment, whitespace). Note in PR: "Trivial change — no visual/test evidence needed".

**No test suite available:** Note in PR: "No automated tests — manual verification required." Still describe what was tested manually.

**No running dev server for UI evidence:** Start dev server. If unable: note in PR what browser steps reviewer should follow. NEVER skip UI evidence just because "it's inconvenient".

**Draft PR requested:** Add `--draft` flag to `gh pr create`.

## Assumptions & Escalation

- **Tier 1 (reversible):** commit message typos — proceed, amend before push, flag for review
- **Tier 2 (architecture):** branch naming conflicts — check existing branches, block if overlap
- **Tier 3 (security):** accidentally staged secrets — **STOP**, unstage, run `git filter-repo` if necessary, block and alert.

## Examples (Few-Shot)

**Example 1: UI Change**
Input: "Create a PR for the new login page"
Output: Commit + Push + Browser screenshot capture + `gh pr create` with evidence.

**Example 2: Backend Fix**
Input: "Push my API fix and open a PR"
Output: Commit + Push + Pytest log capture + `gh pr create` with logs.
