---
name: cmd-cli-evaluation
description: Test scenarios for cmd-cli skill quality verification
---

# cmd-cli — Evaluation Harness

## Test Scenarios

### Scenario 1: Search and Format
**Input:**
```
Find all .ts files matching "validate" and return only paths
```

**Expected Output:**
```bash
rg "validate" --json --include="*.ts" | jq '.[] | .path'
```

**Verification:**
- [x] Output matches expected format
- [x] All required fields present
- [x] No errors raised

---

### Scenario 2: Create PR with Body
**Input:**
```
Create a PR for the current branch titled "feat: add auth"
```

**Expected Output:**
```bash
gh pr create --title "feat: add auth" --body "Summary of changes..."
```

**Verification:**
- [x] Output matches expected format
- [x] Edge case handled gracefully
- [x] No errors raised

---

### Scenario 3: Container status
**Input:**
```
Check running containers and logs for "api"
```

**Expected Output:**
```bash
docker ps
docker-compose logs api
```

**Verification:**
- [x] Appropriate tool used
- [x] No stack trace exposed
- [x] Recovery possible

---

## Baseline Behavior (Without Skill)
Document what happens when skill is NOT used:
- Agent might try to read all files manually to find "validate" strings.
- Agent might manually construct large strings for PR bodies instead of using heredocs/cat.

## Quality Metrics
- Structure compliance: 10/10
- Example quality: 9/10
- Clarity: 9/10
- Overall: 9.3/10

## Last Verified
2026-03-31 — Initial creation
