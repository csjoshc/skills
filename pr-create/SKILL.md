---
name: pr-create
description: >-
  Creates GitHub PRs from local changes with proper branch management, evidence collection,
  and rich descriptions. Handles branch creation from dirty main, UI recording attachments
  via browser tools, and backend test/coverage log attachments. Use when the user says
  "create PR", "open PR", "push and PR", "submit changes", or wants to finalize work
  for review.
---

# Create PR

Creates a GitHub PR from local changes with proper git hygiene, descriptive branch naming,
and evidence-based descriptions (UI recordings for frontend, test logs for backend).

## Workflow

```
Phase 0: Pre-flight gates (verify-claim, pr-review self-check)
Phase 1: Git Preparation
Phase 2: Commit & Push
Phase 3: Evidence Collection (conditional)
Phase 4: Create PR with rich description
```

## Phase 0: Pre-flight gates

Before any git work, run the enforcement skills that prevent shipping
false completions or scope-creep PRs.

```
Checklist:
- [ ] 0.1 Run `verify-claim` on the current session's claims. If it
        writes CLAIM_UNVERIFIED.md at the repo root, halt and surface
        the gap table to the user. Do not proceed without evidence or
        an explicit `override: <reason>`.
- [ ] 0.2 Run `pr-review` self-check in advisory mode against the
        pending diff. Report BLOCKs from the 5 sub-agents (Bug Hunter,
        Standards Compliance, Error Handling, Test Analyzer, Spec-
        Traceability Auditor). Fix or acknowledge before continuing.
- [ ] 0.3 If the changed files touch backend production code, run
        `tdd/MUTATION.md` in single-mutant mode on the touched
        functions. Survivors → user decides whether to strengthen the
        test or acknowledge.
- [ ] 0.4 If the changed files introduce a new boundary mock, run
        `tdd/MOCK_CONTRACT.md`. Missing contract refs → BLOCK.
```

These gates are cheap relative to opening and re-opening a PR. Skipping
them costs far more in review cycles than it saves now.

---

## Phase 1: Git Preparation

```
Checklist:
- [ ] 1.1 Run `git status` and `git log --oneline -5` to assess state
- [ ] 1.2 Determine current branch and divergence from remote
- [ ] 1.3 If on main with uncommitted or unpushed changes → create feature branch
- [ ] 1.4 If already on feature branch → continue on it
- [ ] 1.5 Verify no secrets in staged files (.env, credentials, tokens)
```

### Branch from dirty main

When on `main` (or `master`) with local changes not on remote:

```bash
# Stage changes
git add -A

# Create descriptive branch name from the changes
# Pattern: <type>/<short-description>
# Types: feat, fix, refactor, style, docs, test, chore
git checkout -b <type>/<short-description>
```

Branch name rules:
- Lowercase, hyphens only (no spaces, underscores, or uppercase)
- Max 50 chars
- Derive from the actual diff content, not a generic name
- Examples: `feat/c3-theme-migration`, `fix/date-picker-dark-mode`, `refactor/api-error-handling`

### Already on feature branch

If already on a feature branch, just verify it's up to date with remote main:

```bash
git fetch origin
git log --oneline origin/main..HEAD  # show what will be in the PR
```

---

## Phase 2: Commit & Push

```
Checklist:
- [ ] 2.1 Stage all relevant files (exclude secrets, build artifacts)
- [ ] 2.2 Write commit message from diff analysis (why, not what)
- [ ] 2.3 Commit using HEREDOC format
- [ ] 2.4 Push branch to remote with -u flag
```

```bash
git add -A
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body — explain WHY, not WHAT>
EOF
)"
git push -u origin HEAD
```

Commit message conventions:
- First line: `type(scope): summary` under 72 chars
- Body: explain the motivation, not a line-by-line changelog
- Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`

---

## Phase 3: Evidence Collection

> **Evidence files (screenshots, recordings, test logs) must NOT persist in the final
> branch HEAD.** Use the **ephemeral commit** pattern below to embed images in the PR
> description without polluting the codebase.

Determine the change type by analyzing the diff:

```
UI changes? → 3A (recording)
Backend changes? → 3B (test logs)
Both? → Do both 3A and 3B
```

### 3A: UI Evidence (frontend changes)

**Goal:** Attach visual documentation of the UI changes to the PR. This is MANDATORY for UI-heavy PRs — an agent MUST NOT skip this step.

> ⚠️ **CRITICAL:** If the PR touches any UI (components, styles, pages, themes), you MUST capture visual evidence. Skipping this makes review harder and delays merging.

**When to capture:**
- Any visual change (new component, style change, theme change)
- Form/input changes (empty, filled, error states)
- Modal/dialog changes
- Navigation/flow changes
- Dark mode/light mode changes
- Responsive layout changes

**In Cursor (IDE browser available):**

```
Checklist:
- [ ] Navigate to the running app using browser tools (browser_navigate)
- [ ] Lock browser (browser_lock)
- [ ] Walk through each affected user flow, taking screenshots at key states
- [ ] For theme changes: capture both light and dark mode
- [ ] For form changes: show empty, filled, and error states
- [ ] For new components: show all visual states
- [ ] Unlock browser (browser_unlock)
- [ ] Collect screenshots into PR description as inline images
```

**Screen recording (preferred for complex flows):**
```bash
# Use Chrome DevTools MCP or cursor's built-in recording
# Capture: full user flow from start to finish
# Include: all interactions, state changes, edge cases
```

**Screenshot requirements:**
1. Screenshot of change in default state (REQUIRED)
2. Dark mode screenshot if theme exists (REQUIRED if applicable)
3. Interactive states: empty → filled → error (REQUIRED for forms)
4. Before/after comparison if refactoring

Upload screenshots to the PR using the **ephemeral commit** pattern:

```bash
# The ephemeral commit pattern:
# 1. Commit evidence files to .evidence/ and push
# 2. Capture the commit SHA (pinned URL survives forever)
# 3. Remove .evidence/ in the next commit and push
# 4. Use raw.githubusercontent.com/{owner}/{repo}/{SHA}/.evidence/{file} in PR body
#
# Why it works: the "add" commit is an ancestor of HEAD, so GitHub never
# garbage-collects it. The SHA-pinned URL renders images inline permanently,
# even after the file is deleted from the branch tip.

# Step 1: Save screenshots to .evidence/ in the repo root
mkdir -p .evidence
cp /tmp/screenshot-dark.png .evidence/
cp /tmp/screenshot-light.png .evidence/

# Step 2: Force-add (overrides .gitignore) and commit
git add -f .evidence/
git commit -m "evidence: PR screenshots [skip ci]"

# Step 3: Capture the SHA and push
EVIDENCE_SHA=$(git rev-parse HEAD)
git push

# Step 4: Remove evidence and push again
git rm -r .evidence/
git commit -m "chore: remove evidence files"
git push

# Step 5: Build image URLs from the pinned SHA
# Pattern: https://raw.githubusercontent.com/{owner}/{repo}/{EVIDENCE_SHA}/.evidence/{filename}
# Example:
#   https://raw.githubusercontent.com/acme/app/a1b2c3d/.evidence/dashboard-dark.png

# Step 6: Embed in PR body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
## Evidence
![Dark mode](https://raw.githubusercontent.com/{owner}/{repo}/${EVIDENCE_SHA}/.evidence/dashboard-dark.png)
![Light mode](https://raw.githubusercontent.com/{owner}/{repo}/${EVIDENCE_SHA}/.evidence/dashboard-light.png)
EOF
)"
```

> **Tip:** Add `.evidence/` to `.gitignore` so evidence files are ignored by default.
> The flow uses `git add -f` to override the ignore for the ephemeral commit.

**In terminal agent (no IDE browser):**

```bash
# Start a recording session with Chrome DevTools Protocol
# Or use mcp-cli to interact with browser tools
# CRITICAL: Do NOT skip this step - start dev server if needed
# Save screenshots to /tmp/, then use the ephemeral commit pattern above.
```

**Minimum UI evidence for ANY frontend PR:**
1. Screenshot or description of the change in default state (REQUIRED)
2. If dark mode exists: both themes shown (REQUIRED if applicable)
3. If interactive: key interaction states documented (REQUIRED if applicable)
4. Screen recording for complex flows (RECOMMENDED)

### 3B: Backend Evidence (backend changes)

**Goal:** Attach test results and coverage to the PR. This is MANDATORY for code changes — an agent MUST capture test evidence.

> ⚠️ **CRITICAL:** If the PR touches backend code (Python, API routes, services), you MUST run tests and capture evidence. Skipping test results makes review harder and risks regressions.

**When to capture:**
- Any backend code change (new endpoint, service, model)
- Configuration changes
- Database/schema changes
- Integration with external services
- Refactoring of backend logic

```
Checklist:
- [ ] Run the project's test suite (REQUIRED)
- [ ] Capture test output (pass/fail summary) (REQUIRED)
- [ ] Run coverage if available (REQUIRED if applicable)
- [ ] Format results for PR description (REQUIRED)
- [ ] Save logs to file for attachment
```

```bash
# Python projects
python -m pytest --tb=short -q 2>&1 | tail -20 > /tmp/test-results.txt
python -m pytest --cov --cov-report=term-missing 2>&1 | tail -30 > /tmp/coverage.txt

# Node projects
npm test 2>&1 | tail -20 > /tmp/test-results.txt
npx vitest --coverage 2>&1 | tail -30 > /tmp/coverage.txt

# C3 platform (js-rhino)
# Use the project's test runner as documented in AGENTS.md

# IMPORTANT: Save logs to /tmp/ only. Paste contents into the PR body
# as fenced code blocks. For large logs, use the ephemeral commit pattern
# from 3A (save to .evidence/, commit, capture SHA, remove, embed URL).
```

**Test output requirements:**
1. Pass/fail summary with counts (REQUIRED)
2. Failed test names if any failures (REQUIRED if applicable)
3. Coverage report (REQUIRED if available)
4. Error messages from failures (REQUIRED if applicable)

---

## Phase 4: Create PR

```
Checklist:
- [ ] 4.1 Analyze ALL commits on the branch (not just latest)
- [ ] 4.2 Draft PR title and body
- [ ] 4.3 Create PR using gh cli
- [ ] 4.4 If evidence was collected, edit PR body to include it
- [ ] 4.5 Return the PR URL
```

### PR creation

```bash
gh pr create --title "<type>(<scope>): <summary>" --body "$(cat <<'EOF'
## Summary

<1-3 bullet points explaining WHAT changed and WHY>

## Changes

<grouped list of file changes by category>

## Evidence

### UI Validation
<screenshots, recordings, or manual validation steps>

### Test Results
```
<paste from /tmp/test-results.txt>
```

### Coverage
```
<paste from /tmp/coverage.txt>
```

## Test Plan

- [ ] <specific thing to verify>
- [ ] <specific thing to verify>

EOF
)"
```

### Editing PR body after creation (for attaching evidence)

If you need to create the PR first then add evidence:

```bash
# Create PR first
gh pr create --title "..." --body "## Summary\n\n..."

# Collect evidence...

# Then update the body
gh pr edit <PR_NUMBER> --body "$(cat <<'EOF'
<full updated body with evidence>
EOF
)"
```

---

## Conditional Paths

> ⚠️ **IMPORTANT:** These paths are ONLY for trivial changes. If your change touches UI or backend code, you MUST complete Phase 3.

**Trivial change (< 5 lines, single file, no functional change):**
- [ ] Skip Phase 3 only if truly trivial (typo fix, comment, whitespace)
- [ ] Note in PR: "Trivial change — no visual/test evidence needed"

**No test suite available:**
- [ ] Note in PR: "No automated tests — manual verification required."
- [ ] Still describe what was tested manually

**No running dev server for UI evidence:**
- [ ] Start dev server: `npm run dev` or `python -m flask run`
- [ ] If unable to start: note in PR what browser steps reviewer should follow
- [ ] NEVER skip UI evidence just because "it's inconvenient"

**Draft PR requested:**
Add `--draft` flag to `gh pr create`.

---

## Safety Rules

- NEVER force-push to main/master
- NEVER commit .env, credentials, or secret files
- NEVER skip the secrets check (Phase 1.5)
- NEVER use `git push --force` unless explicitly asked
- NEVER amend commits that have been pushed to remote
- NEVER leave evidence files (.evidence/) in the final branch HEAD — always remove them after capturing the commit SHA
- Always verify `git status` shows clean after commit before pushing
