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

## Safety Rules

- NEVER force-push to main/master
- NEVER commit .env, credentials, or secret files
- NEVER skip the secrets check (Phase 1.5)
- NEVER use `git push --force` unless explicitly asked
- NEVER amend commits that have been pushed to remote
- NEVER leave evidence files (.evidence/) in the final branch HEAD — always remove them after capturing the commit SHA
- Always verify `git status` shows clean after commit before pushing

## Phase 0: Pre-flight gates

Before any git work, run the enforcement skills that prevent shipping
false completions or scope-creep PRs.

```
Checklist:
- [ ] 0.1 Run `verify-claim` on the current session's claims. If it
        writes CLAIM_UNVERIFIED.md at the repo root, halt and surface
        the gap table to the user. Do not proceed without evidence or
        an explicit `override: <reason>`.
- [ ] 0.2 Self-review the pending diff with the harness's built-in code
        review if it has one; otherwise run `pr-review` in advisory mode
        (no posting). Fix or acknowledge findings before continuing.
- [ ] 0.3 If the changed files touch backend production code, run
        `tdd/MUTATION.md` in single-mutant mode on the touched
        functions. Survivors → user decides whether to strengthen the
        test or acknowledge.
- [ ] 0.4 If the changed files introduce a new boundary mock, run
        `tdd/MOCK_CONTRACT.md`. Missing contract refs → BLOCK.
```

These gates are cheap relative to opening and re-opening a PR. Skipping
them costs far more in review cycles than it saves now.

<!-- pattern: evidence-gate -->
### Evidence gate (Phase 0 mandatory)

Before opening a PR, paste evidence inline in the description. No PR ships without:

- [ ] Test output (command + last 20 lines, exit 0)
- [ ] Screenshot or recording (UI changes only)
- [ ] curl response (API changes only)
- [ ] Reproduction test (bug fixes only — must fail on `main`, pass on branch)

A claim of "fixed" without one of the above is a /verify-claim block. See `~/.skills/verify-claim/SKILL.md`.

**Production-bound PRs** (ship to production directly or behind a flag) also need the pre-launch checklist and a rollback plan in the description: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md). Skip for purely internal changes.

## Phase 1: Git Preparation

```
Checklist:
- [ ] 1.1 Run `git status` and `git log --oneline -5` to assess state
- [ ] 1.2 Determine current branch and divergence from remote
- [ ] 1.3 If on main with uncommitted or unpushed changes → create feature branch
- [ ] 1.4 If already on feature branch → continue on it
- [ ] 1.5 Verify no secrets in staged files (.env, credentials, tokens)
```

Branch name: `<type>/<short-description>`, lowercase with hyphens, max 50 chars, derived from the actual diff.
Branch-from-main commands and naming examples: [GIT_PREP.md](GIT_PREP.md).

## Phase 2: Commit & Push

```
Checklist:
- [ ] 2.1 Stage all relevant files (exclude secrets, build artifacts)
- [ ] 2.2 Write commit message from diff analysis (why, not what)
- [ ] 2.3 Commit using HEREDOC format
- [ ] 2.4 Push branch to remote with -u flag
```

Commit message: `type(scope): summary` under 72 chars, body explains why. Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`.
HEREDOC commit and push commands: [GIT_PREP.md](GIT_PREP.md).

## Phase 3: Evidence Collection

> **Evidence files (screenshots, recordings, test logs) must NOT persist in the final
> branch HEAD.** Use the **ephemeral commit** pattern (in EVIDENCE_UI.md) to embed images in
> the PR description without polluting the codebase.

Determine the change type by analyzing the diff:

```
UI changes? → 3A (recording)
Backend changes? → 3B (test logs)
Both? → Do both 3A and 3B
Deleted or renamed a package, symbol, route or config? → also 3C
```

- **3A UI evidence is MANDATORY for any PR touching components, styles, pages or themes.** Never skip it. Minimum: default-state screenshot (REQUIRED), both themes if dark mode exists, key interaction states if interactive; recording recommended for complex flows. Procedure and the ephemeral commit recipe: [EVIDENCE_UI.md](EVIDENCE_UI.md).
- **3B backend evidence is MANDATORY for backend code, config, schema or integration changes.** Run the test suite and capture pass/fail counts, failed test names, coverage and error messages. Logs go to `/tmp/` and are pasted into the PR body, never committed. Commands per stack: [EVIDENCE_BACKEND.md](EVIDENCE_BACKEND.md).
- **3C cross-reference scrub** when a package, public symbol, endpoint or config file is deleted: grep docs, diagrams, CI filters, manifests for the old name; every hit is removed, updated or escalated, and the PR states `Cross-reference scrub: ran for <NAME>; N hits, all resolved.` Commands: [DOC_XREF_SCRUB.md](DOC_XREF_SCRUB.md).

## Phase 4: Create PR

```
Checklist:
- [ ] 4.1 Analyze ALL commits on the branch (not just latest)
- [ ] 4.2 Draft PR title and body
- [ ] 4.3 Create PR using gh cli
- [ ] 4.4 If evidence was collected, edit PR body to include it
- [ ] 4.5 Return the PR URL
```

Title: `<type>(<scope>): <summary>`. Body sections: `## Summary` (1-3 bullets: what and why), `## Changes`, `## Evidence` (UI Validation, Test Results, Coverage), `## Test Plan`.
Full `gh pr create` template and how to edit the body after creation: [PR_BODY.md](PR_BODY.md).

<!-- pattern: not-doing-callout -->
### "Not Doing" callout in PR body

Include a `## Not Doing` section in every non-trivial PR. Lists what was deliberately left out:

- Adjacent refactors that were tempting but out of scope
- Edge cases handled by upstream/middleware
- Follow-up tickets created instead of inlined fixes

Reviewers stop asking "why didn't you also..." when they can see what was deferred and why.

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

## Companion files

Read only when the situation matches:

- [GIT_PREP.md](GIT_PREP.md): creating the branch, writing the commit, pushing
- [EVIDENCE_UI.md](EVIDENCE_UI.md): the PR touches UI; also the ephemeral commit recipe for any evidence
- [EVIDENCE_BACKEND.md](EVIDENCE_BACKEND.md): the PR touches backend code
- [DOC_XREF_SCRUB.md](DOC_XREF_SCRUB.md): the PR deletes or renames a package, symbol, route or config
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md): the PR ships to production
- [PR_BODY.md](PR_BODY.md): drafting or editing the PR body
