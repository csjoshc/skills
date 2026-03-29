---
name: pr-review
description: >-
  Performs automated PR code review using parallel sub-agents for bug detection,
  standards compliance, error handling, and test coverage analysis. Use when
  reviewing pull requests, providing code review feedback, or when the user
  mentions PR review, code review, or reviewing changes. Uses criteria-based
  checklists (not arbitrary scores) to filter false positives. Posts results
  to GitHub with Claude attribution.
---

# PR Review

Automated pull request review using parallel specialized sub-agents with
criteria-based checklists to filter false positives. Every flagged issue
must pass a binary checklist — no arbitrary scores.

## Invocation

```
/pr-review <owner/repo> <pr-number>
```

If already on the PR branch, detect the repo and PR number automatically via `gh pr view`.

---

## Workflow

### Step 1: Pre-flight checks

Gather PR context and decide whether to proceed.

```bash
gh pr view <PR> --json title,body,state,isDraft,author,baseRefName,headRefName
gh pr diff <PR>
gh pr view <PR> --comments --json comments
```

**Skip review if any of these are true:**
- PR is closed or merged
- PR is a draft
- PR is trivial (dependency bumps, auto-generated, single typo fix)
- This agent has already commented on the PR

### Step 2: Gather standards

Collect all applicable coding standards:
1. Read [STANDARDS.md](STANDARDS.md) from this skill
2. Read any project-level standards files in the repo (CLAUDE.md, .cursorrules,
   AGENTS.md, copilot-instructions.md) at the root and in directories containing
   modified files
3. Merge into a single standards context for the agents

### Step 2b: C3 platform context (backend changes)

If the PR modifies any C3 backend code — `.c3typ` files, Type definitions,
`fetch()` / `evalMetric()` calls, server-side JavaScript actions, logger
initialization (`PerLogger`), test setup (`Jasmine`, `TestApi`), or C3
platform patterns — query the **C3AI-MCP** server for platform-specific
context before launching review agents.

**What qualifies as C3 backend code:**
- `.c3typ` / `.c3doc` type definition files
- Server-side `.js` files using C3 APIs (`Type.fetch()`, `.merge()`,
  `.upsert()`, `Obj.make()`, `HttpRequest`, `ContentValue`, etc.)
- Test files using C3's `Jasmine` / `TestApi` harness
- `PerLogger` or `Log` logging calls
- `seed/` data files or `canonicalize` scripts
- C3 package metadata (`package.json` with `c3` dependencies)

**How to use C3AI-MCP:**
- Query the MCP for documentation on any C3 API or Type referenced in
  the diff that the agent is unsure about
- Use MCP-provided context to validate whether C3 API usage is correct
  (e.g., correct `fetch()` filter syntax, proper `spec` parameter
  conventions, valid Type method signatures)
- Pass relevant C3 platform context to the review agents alongside the
  standards so they can evaluate C3-specific correctness

**Do NOT** skip this step for backend changes — C3 is a proprietary
platform and general-purpose knowledge will not cover its APIs, Type
system semantics, or runtime behavior.

### Step 3: Summarize the PR

Create a brief summary before launching agents:
- What changed and why (from PR title + description)
- Files modified with change types (added / modified / deleted)
- Risk areas (auth, data layer, API surface, UI, config)

### Step 4: Launch parallel review agents

Launch **4 sub-agents in parallel**. Pass each the PR diff, summary, and
merged standards. Each agent returns a list of issues. Every issue must
include evidence, the checklist evaluation, and the reason it was flagged.

**Reporting rule**: An issue is only reported if it passes the agent's
checklist (meets the minimum number of criteria). No arbitrary numeric
scores — every criterion is binary (yes/no) and auditable.

---

#### Agent 1 — Bug Hunter

**Focus**: Runtime bugs and security issues in changed code only.

**Look for:**
- Null/undefined dereferences that will crash at runtime
- Off-by-one errors in loops or array access
- Race conditions and concurrency bugs
- Resource leaks (file handles, connections, memory)
- Logic errors that produce wrong results
- Missing return statements, incorrect operators (= vs ==, && vs ||)
- Type coercion bugs
- SQL injection, XSS, command injection, path traversal
- Hardcoded secrets or credentials
- Missing authentication/authorization checks

**Do NOT flag:** Style preferences, "potential" issues, suggestions,
performance concerns (unless catastrophic), missing tests, code
organization opinions, anything requiring context outside the diff.

**Checklist — report if 4 of 5 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Can trace the exact code path to the failure | |
| 2 | Failure occurs regardless of external state or input | |
| 3 | No defensive code in the diff prevents this scenario | |
| 4 | Issue is in changed code, not pre-existing | |
| 5 | Can describe a concrete failing input or test case | |

---

#### Agent 2 — Standards Compliance

**Focus**: Violations of project coding standards from Step 2.

For each violation, **quote the exact rule** being broken (e.g., "LG-001:
Use the project logger").

**Check for:**
- Naming convention violations (NM-xxx rules)
- Logging violations — console.log / print instead of project logger (LG-xxx)
- Missing type/interface declarations for new functions (FN-001)
- Banned patterns — regex, inline styles, etc. (RT-xxx, FE-xxx)
- Documentation/docstring formatting (DC-xxx)
- Unbounded queries or hard-coded limits (DA-xxx)
- Test coverage gaps for new functions (TS-001)

**Do NOT flag:** Subjective concerns, pre-existing violations in unchanged
code, issues a linter would catch, rules not documented in the standards.

**Checklist — report if 4 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Can quote the exact rule code and text being violated | |
| 2 | The rule applies to this file type and context | |
| 3 | The violation is in changed code, not pre-existing | |
| 4 | No documented override or exception exists for this case | |

---

#### Agent 3 — Error Handling Auditor

**Focus**: Silent failures and inadequate error handling.

**For each error handler (try-catch, error callbacks, fallback logic), check:**
- Is the error logged with appropriate severity and context?
- Does the user receive clear, actionable feedback?
- Does the catch block catch only expected error types?
- Could the fallback mask the underlying problem?

**Do NOT flag:** Error handling that follows established project patterns,
intentional documented fallbacks, test code error handling.

**Checklist — report if 3 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Error handler exists in changed code (not pre-existing) | |
| 2 | Can demonstrate a concrete scenario where the error is silently lost | |
| 3 | No upstream handler catches and logs this error | |
| 4 | A developer debugging production would be unable to diagnose this | |

**Severity (for labeling only, not filtering):**
- CRITICAL: Criteria 1–4 all YES (silent failure, invisible to operators)
- HIGH: 3 of 4 YES
- MEDIUM: Issues flagged but did not meet the 3-of-4 threshold — do not report

---

#### Agent 4 — Test Analyzer

**Focus**: Critical gaps in test coverage for changed code.

**Check for:**
- New public functions without corresponding tests (TS-001)
- Missing edge case or error path coverage (TS-004)
- Tests that violate project test conventions (TS-002 through TS-007)
- Missing or weak assertions (TS-005)
- Test data leaking between tests (TS-003, TS-006)

**Do NOT flag:** Academic completeness concerns, trivial getters/setters,
behavior already covered by integration/e2e tests.

**Checklist — report if 3 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | New or modified public function has no corresponding test | |
| 2 | Can name a specific bug or regression this gap would miss | |
| 3 | No integration or e2e test covers this behavior elsewhere | |
| 4 | The untested code is in the changed files, not pre-existing | |

---

### Step 5: Validate issues

For each issue from Step 4 that met its checklist threshold, launch a
**validation sub-agent** to independently re-evaluate the checklist. The
validator receives the issue description, the filled checklist, the PR
title/body (for context only — author intent does not validate code), and
the relevant source code.

**Validation process:**
1. Read the flagged issue and its completed checklist
2. For each criterion marked YES, independently verify it:
   - Trace the code path to confirm the failure scenario
   - Check if defensive code prevents the flagged scenario
   - For standards violations, confirm the rule exists and applies to this file type
   - For test gaps, search for tests elsewhere in the repo
3. Flip any criterion from YES to NO if the evidence doesn't hold

**VALIDATED** if the issue still meets the checklist threshold after
re-evaluation.

**NOT VALIDATED** if re-evaluation drops it below threshold.

**When in doubt, VALIDATE.** A dismissed false positive costs nothing; a
missed real issue can be expensive.

### Step 6: Filter and deduplicate

1. Remove issues that **failed validation** (below checklist threshold)
2. Merge duplicate issues flagged by multiple agents
3. Sort by category: Bug > Error Handling > Standards > Test Gap

### Step 7: Post review

**IMPORTANT**: Every comment and review posted by this skill must end with
the following attribution line:

```
---
*Generated by Claude*
```

**If issues were found**, post inline comments on the PR:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
  --method POST \
  -f body="[issue description + checklist]

---
*Generated by Claude*" \
  -f commit_id="$(gh pr view <PR> --json headRefOid -q .headRefOid)" \
  -f path="file.py" \
  -F line=42 \
  -f side="RIGHT"
```

For small, self-contained fixes, include a GitHub suggestion block:
````
```suggestion
fixed code here
```
````

For larger fixes (6+ lines, structural, multi-file), describe the issue
and suggested approach without a suggestion block.

After all inline comments, post a summary comment:

```bash
gh pr comment <PR> --body "## Code Review Summary

**Issues found**: [count] across [files]
**Categories**: [Bug / Standards / Error Handling / Test Gap]

Each issue includes the checklist criteria it was evaluated against.

---
*Generated by Claude*"
```

**If no issues were found**, post a summary comment:

```bash
gh pr comment <PR> --body "## Code Review — No Issues Found

Checked for bugs, standards compliance, error handling, and test coverage.

---
*Generated by Claude*"
```

---

## Issue Output Format

Each issue includes the filled checklist so reviewers can see exactly why
it was flagged and challenge any criterion they disagree with.

```
## [Category]: [Brief description]

**File**: [path]:[line]
**Rule**: [Quoted standard code + text, or "N/A"]

**Checklist**:
- [x] [Criterion 1 that was met]
- [x] [Criterion 2 that was met]
- [x] [Criterion 3 that was met]
- [ ] [Criterion 4 that was NOT met, if any]

**Evidence**:
[Relevant code from the diff]

**Why this is an issue**:
[Specific failure scenario or rule violation]

**Suggested fix**:
[Concrete code fix or explanation]

---
*Generated by Claude*
```

---

## False Positive Checklist

Do NOT flag any of the following — these are known false positive patterns:

- Pre-existing issues not introduced in this PR
- Code that looks wrong but is actually correct
- Pedantic nitpicks a senior engineer wouldn't flag
- Issues a linter will catch (do not run the linter to verify)
- General code quality concerns not backed by a documented standard
- Issues explicitly silenced via comments (lint-ignore, noqa, etc.)
- Author intent from PR description (we review code, not intentions)

---

## Additional Resources

- For project coding standards reference, see [STANDARDS.md](STANDARDS.md)
