---
name: test-ui
description: Use when testing web application UIs, documenting bugs, or verifying frontend functionality across tabs, forms, and navigation.
---

# Test UI

## TL;DR (Quick Start)

Verify frontend functionality using Playwright (E2E) or manual browser testing. Prefers existing project tests (`npm run e2e`) but can generate custom scripts if needed.

**When to use:** "test UI", "fix visual bug", "verify form", "check accessibility".

**Invocation:**
```bash
cd react-app
npm run e2e
# OR custom script
node test-ui.mjs
```

## When to Use
- Testing frontend UI functionality and interactions.
- Documenting visual bugs with screenshots.
- Verifying cross-browser/cross-view state sync.
- **NOT for:** Backend-only logic testing (use `tdd` or `pytest`).

## Decision Tree

1. **Does the project have existing E2E tests?**
   - YES → Run them first (`npm run e2e`).
   - NO → Proceed to custom setup.

2. **Is it a visual/styling issue?**
   - YES → Take screenshots at multiple breakpoints.
   - NO → Focus on interaction logic.

3. **Are multiple services involved?**
   - YES → Ensure both Backend (port 8000) and Frontend (port 3000) are running.
   - NO → Run standalone frontend if possible.

## Workflow

### 1. Setup Services
Identify URLs and start backend/frontend. Verify connectivity with `curl`.

### 2. Run Tests
- **Option A:** Use `npm run e2e` (standard).
- **Option B:** Create `test-ui.mjs` for targeted interactions.

### 3. Document Results
Record pass/fail counts, capture screenshots on failure, and generate a structured bug report if issues are found.

## Assumptions & Escalation

- **Tier 1 (reversible):** Minor layout shifts — proceed, capture evidence, flag for review.
- **Tier 2 (logic):** Form submission failure — check API logs, block if data integrity is at risk.
- **Tier 3 (security):** UI leaks sensitive data (keys/PII) — **STOP**, block and alert.

## Examples (Few-Shot)

**Example 1: Running existing suite**
Input: "Run the E2E tests"
Output: Success/Failure report + screenshots of any failures.

**Example 2: Custom interaction**
Input: "Verify the login form handles empty passwords"
Output: Playwright script that fills email, leaves password empty, clicks submit, and confirms error message.

## Related Skills
| Skill | When to use instead |
|-------|---------------------|
| chrome-devtools | For manual exploration and performance debugging |
| make-ui | For building or styling components (not testing) |
