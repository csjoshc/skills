# Backend Evidence (Phase 3B)

## Contents

- When to capture
- Checklist
- Test commands by stack
- Test output requirements

## 3B: Backend Evidence (backend changes)

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

# Other platforms
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
