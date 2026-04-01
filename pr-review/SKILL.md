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

## TL;DR (Quick Start)

Automated code review using specialized parallel agents (Bug Hunter, Standards, Error Handling, Tests). Filters false positives via binary checklists and independent validation.

**When to use:** "review this PR", "PR review", "code review".

**Invocation:**
```bash
/pr-review <owner/repo> <pr-number>
```

## Decision Tree

1. **Is the PR trivial (<5 lines, dependency update, typo)?**
   - YES → **SKIP** review; note "Trivial change" to user.
   - NO → Continue.

2. **Is it a draft PR or already closed?**
   - YES → **SKIP** review; block and alert user.
   - NO → Continue.

3. **Does the PR modify C3 backend?**
   - YES → **MANDATORY** query C3AI-MCP for platform context before launching agents.
   - NO → Proceed with standard agents.

4. **Have issues been found?**
   - YES → Filter by checklist threshold, validate, and post to GitHub.
   - NO → Post "No issues found" summary.

## Workflow

```
/pr-review <owner/repo> <pr-number>
```

If already on the PR branch, detect the repo and PR number automatically via `gh pr view`.

## Workflow

### Step 1: Pre-flight checks

Gather PR context and decide whether to proceed.

```bash
gh pr view <PR> --json title,body,state,isDraft,author,baseRefName,headRefName
gh pr diff <PR>
gh pr view <PR> --comments --json comments
```

**Skip review if:** PR is closed/merged; PR is a draft; PR is trivial (dependency bumps, auto-generated, single typo fix); this agent has already commented on the PR.

### Step 2: Gather standards

1. Read **Architecture Decisions** in `~/.skills/spec-writer/SKILL.md`
2. Read any project-level standards files (CLAUDE.md, .cursorrules, AGENTS.md, copilot-instructions.md) at root and in directories containing modified files
3. Merge into a single standards context for the agents

### Step 2b: C3 platform context (backend changes)

If the PR modifies C3 backend code, query the C3AI-MCP server for platform-specific context before launching review agents. See [reference/c3-context.md](reference/c3-context.md) for details.

### Step 3: Summarize the PR

Create a brief summary: what changed and why; files modified with change types; risk areas (auth, data layer, API surface, UI, config).

### Step 4: Launch parallel review agents

Launch **4 sub-agents in parallel**. Pass each the PR diff, summary, and merged standards. Each agent returns a list of issues. An issue is only reported if it passes the agent's checklist.

#### Agent 1 — Bug Hunter

**Focus**: Runtime bugs and security issues in changed code only.

**Look for:** Null/undefined dereferences; off-by-one errors; race conditions; resource leaks; logic errors; missing returns, incorrect operators; type coercion bugs; SQL injection, XSS, command injection, path traversal; hardcoded secrets; missing auth checks.

**Do NOT flag:** Style preferences, "potential" issues, suggestions, performance concerns (unless catastrophic), missing tests, code organization opinions, anything requiring context outside the diff.

**Checklist — report if 4 of 5 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Can trace the exact code path to the failure | |
| 2 | Failure occurs regardless of external state or input | |
| 3 | No defensive code in the diff prevents this scenario | |
| 4 | Issue is in changed code, not pre-existing | |
| 5 | Can describe a concrete failing input or test case | |

#### Agent 2 — Standards Compliance

**Focus**: Violations of project coding standards from Step 2. Quote the exact rule being broken.

**Check for:** Naming conventions (NM-xxx); logging violations (LG-xxx); missing type/interface declarations (FN-001); banned patterns (RT-xxx, FE-xxx); documentation formatting (DC-xxx); unbounded queries (DA-xxx); test coverage gaps (TS-001).

**Do NOT flag:** Subjective concerns, pre-existing violations, linter-catchable issues, rules not in standards.

**Checklist — report if 4 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Can quote the exact rule code and text being violated | |
| 2 | The rule applies to this file type and context | |
| 3 | The violation is in changed code, not pre-existing | |
| 4 | No documented override or exception exists for this case | |

#### Agent 3 — Error Handling Auditor

**Focus**: Silent failures and inadequate error handling.

**For each error handler, check:** Is the error logged with appropriate severity and context? Does the user receive clear, actionable feedback? Does the catch block catch only expected error types? Could the fallback mask the underlying problem?

**Do NOT flag:** Error handling following established project patterns, intentional documented fallbacks, test code error handling.

**Checklist — report if 3 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | Error handler exists in changed code (not pre-existing) | |
| 2 | Can demonstrate a concrete scenario where the error is silently lost | |
| 3 | No upstream handler catches and logs this error | |
| 4 | A developer debugging production would be unable to diagnose this | |

**Severity:** CRITICAL (4/4 YES); HIGH (3/4 YES); MEDIUM (below threshold — do not report).

#### Agent 4 — Test Analyzer

**Focus**: Critical gaps in test coverage for changed code.

**Check for:** New public functions without tests (TS-001); missing edge case/error path coverage (TS-004); test convention violations (TS-002 through TS-007); missing/weak assertions (TS-005); test data leaking between tests (TS-003, TS-006).

**Do NOT flag:** Academic completeness concerns, trivial getters/setters, behavior already covered by integration/e2e tests.

**Checklist — report if 3 of 4 criteria are YES:**

| # | Criterion | Yes/No |
|---|-----------|--------|
| 1 | New or modified public function has no corresponding test | |
| 2 | Can name a specific bug or regression this gap would miss | |
| 3 | No integration or e2e test covers this behavior elsewhere | |
| 4 | The untested code is in the changed files, not pre-existing | |

### Step 5: Validate issues

For each issue that met its checklist threshold, launch a **validation sub-agent** to independently re-evaluate the checklist. The validator receives the issue description, filled checklist, PR title/body, and relevant source code.

**Validation process:**
1. Read the flagged issue and its completed checklist
2. For each YES criterion, independently verify it (trace code path, check defensive code, confirm rule exists, search for tests elsewhere)
3. Flip any criterion from YES to NO if evidence doesn't hold

**VALIDATED** if issue still meets checklist threshold after re-evaluation. **NOT VALIDATED** if dropped below threshold. **When in doubt, VALIDATE.**

### Step 6: Filter and deduplicate

1. Remove issues that failed validation
2. Merge duplicate issues flagged by multiple agents
3. Sort by category: Bug > Error Handling > Standards > Test Gap

### Step 7: Post review

**IMPORTANT**: Every comment must end with attribution:
```
---
*Generated by Claude*
```

**If issues found:** Post inline comments on the PR using `gh api repos/{owner}/{repo}/pulls/{pr_number}/comments`. For small fixes, include a GitHub suggestion block. For larger fixes, describe the issue and approach. Then post a summary comment.

**If no issues found:** Post a summary comment noting no issues were found.

See [Issue Output Format](#issue-output-format) for the exact format.

## Issue Output Format

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

## False Positive Checklist

Do NOT flag: pre-existing issues; code that looks wrong but is correct; pedantic nitpicks; linter-catchable issues; general quality concerns without documented standards; silenced issues (lint-ignore, noqa); author intent from PR description.

## Assumptions & Escalation

- **Tier 1 (reversible):** Flagged issue is a minor style nit — proceed, categorize as "Standards", post.
- **Tier 2 (logic):** Reviewer disagrees with agent's finding — check Architecture Decisions, block if unresolved.
- **Tier 3 (security):** Critical security bug (M1-M4) detected — **STOP**, block and alert human immediately (top-level comment).

## Examples (Few-Shot)

**Example 1: Bug Detection**
Input: "Review PR #12 for security"
Output: `Bug Hunter` flags an XSS vulnerability with trace evidence; `Validation` confirms; `Post` to GitHub.

**Example 2: Standards Violation**
Input: "Audit PR #42 for project standards"
Output: `Standards Compliance` flags a naming convention violation (LG-001); `Post` to GitHub with rule quote.
