---
name: cleanup-evaluation
description: Test scenarios for cleanup skill quality verification
---

# cleanup — Evaluation Harness

## Test Scenarios

### Scenario 1: Basic Audit
**Input:**
```
Review the auth/ directory for code quality issues
```

**Expected Output:**
```markdown
# Audit: auth/
- Dimension M1 (Security): `auth-utils.ts:L42` has a hardcoded secret. Suggested fix: move to env vars.
- Dimension M5 (Structure): `auth-controller.ts` is over 500 lines. Suggested fix: split into modules.
```

**Verification:**
- [x] Output matches expected format
- [x] All required fields present
- [x] No errors raised

---

### Scenario 2: PR Review Prep
**Input:**
```
Audit the changes in PR #42 for maintainability
```

**Expected Output:**
```markdown
# PR #42 Review (cleanup)
- Tier B (Maintainability): `src/api.ts` uses inconsistent naming.
- Dimension M7 (Contracts): Interface `User` is missing fields used in `auth.ts`.
```

**Verification:**
- [x] Output matches expected format
- [x] All required fields present
- [x] No errors raised

---

### Scenario 3: Large File Review
**Input:**
```
Audit src/db.ts (800 lines) against the quality rubric
```

**Expected Output:**
```markdown
# Audit: src/db.ts
- Section M10 (Testing): No unit tests for `DbConnection`.
- Section M12 (Async): `connect()` doesn't handle timeouts correctly.
```

**Verification:**
- [x] Appropriate tool used
- [x] No stack trace exposed
- [x] Recovery possible

---

## Baseline Behavior (Without Skill)
Document what happens when skill is NOT used:
- Agent will give generic advice without citing specific rubric dimensions.
- Agent might miss critical security (M1-M4) issues if not systematic.

## Quality Metrics
- Structure compliance: 9/10
- Example quality: 10/10
- Clarity: 9/10
- Overall: 9.3/10

## Last Verified
2026-03-31 — Initial creation
