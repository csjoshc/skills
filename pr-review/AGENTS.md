# PR Review — Agent Definitions and Output

## Parallel Review Agents

### Agent 1 — Bug Hunter

**Focus**: Runtime bugs and security issues in changed code only.

**Look for:** Null/undefined dereferences; off-by-one errors; race conditions; resource leaks; logic errors; missing returns, incorrect operators; type coercion bugs; SQL injection, XSS, command injection, path traversal; hardcoded secrets; missing auth checks.

**Do NOT flag:** Style preferences, "potential" issues, suggestions, performance concerns (unless catastrophic), missing tests, code organization opinions, anything requiring context outside the diff.

**Checklist — report if 4 of 5 criteria are YES:**

| #   | Criterion                                            | Yes/No |
| --- | ---------------------------------------------------- | ------ |
| 1   | Can trace the exact code path to the failure         |        |
| 2   | Failure occurs regardless of external state or input |        |
| 3   | No defensive code in the diff prevents this scenario |        |
| 4   | Issue is in changed code, not pre-existing           |        |
| 5   | Can describe a concrete failing input or test case   |        |

### Agent 2 — Standards Compliance

**Focus**: Violations of project coding standards. Quote the exact rule being broken.

**Check for:** Naming conventions; logging violations; missing type/interface declarations; banned patterns; documentation formatting; unbounded queries; test coverage gaps.

**Do NOT flag:** Subjective concerns, pre-existing violations, linter-catchable issues, rules not in standards.

**Checklist — report if 4 of 4 criteria are YES:**

| #   | Criterion                                                | Yes/No |
| --- | -------------------------------------------------------- | ------ |
| 1   | Can quote the exact rule code and text being violated    |        |
| 2   | The rule applies to this file type and context           |        |
| 3   | The violation is in changed code, not pre-existing       |        |
| 4   | No documented override or exception exists for this case |        |

### Agent 3 — Error Handling Auditor

**Focus**: Silent failures and inadequate error handling.

**For each error handler, check:** Is the error logged with appropriate severity and context? Does the user receive clear, actionable feedback? Does the catch block catch only expected error types? Could the fallback mask the underlying problem?

**Do NOT flag:** Error handling following established project patterns, intentional documented fallbacks, test code error handling.

**Checklist — report if 3 of 4 criteria are YES:**

| #   | Criterion                                                            | Yes/No |
| --- | -------------------------------------------------------------------- | ------ |
| 1   | Error handler exists in changed code (not pre-existing)              |        |
| 2   | Can demonstrate a concrete scenario where the error is silently lost |        |
| 3   | No upstream handler catches and logs this error                      |        |
| 4   | A developer debugging production would be unable to diagnose this    |        |

**Severity:** CRITICAL (4/4 YES); HIGH (3/4 YES); MEDIUM (below threshold — do not report).

### Agent 4 — Test Analyzer

**Focus**: Critical gaps in test coverage for changed code.

**Check for:** New public functions without tests; missing edge case/error path coverage; test convention violations; missing/weak assertions; test data leaking between tests.

**Do NOT flag:** Academic completeness concerns, trivial getters/setters, behavior already covered by integration/e2e tests.

**Checklist — report if 3 of 4 criteria are YES:**

| #   | Criterion                                                   | Yes/No |
| --- | ----------------------------------------------------------- | ------ |
| 1   | New or modified public function has no corresponding test   |        |
| 2   | Can name a specific bug or regression this gap would miss   |        |
| 3   | No integration or e2e test covers this behavior elsewhere   |        |
| 4   | The untested code is in the changed files, not pre-existing |        |

## Validation Process

For each issue that met its checklist threshold, launch a **validation sub-agent** to independently re-evaluate the checklist. The validator receives the issue description, filled checklist, PR title/body, and relevant source code.

1. Read the flagged issue and its completed checklist
2. For each YES criterion, independently verify it (trace code path, check defensive code, confirm rule exists, search for tests elsewhere)
3. Flip any criterion from YES to NO if evidence doesn't hold

**VALIDATED** if issue still meets checklist threshold after re-evaluation. **NOT VALIDATED** if dropped below threshold. **When in doubt, VALIDATE.**

## Filter and Deduplicate

1. Remove issues that failed validation
2. Merge duplicate issues flagged by multiple agents
3. Sort by category: Bug > Error Handling > Standards > Test Gap

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
