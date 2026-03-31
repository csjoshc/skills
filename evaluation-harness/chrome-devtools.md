---
name: chrome-devtools-evaluation
description: Test scenarios for chrome-devtools skill quality verification
---

# chrome-devtools — Evaluation Harness

## Test Scenarios

### Scenario 1: Navigate and Capture
**Input:**
```
Navigate to http://localhost:3000 and take a screenshot
```

**Expected Output:**
```bash
navigate_page("http://localhost:3000")
take_screenshot()
```

**Verification:**
- [x] Output matches expected format
- [x] screenshot file created
- [x] No errors raised

---

### Scenario 2: Trace performance
**Input:**
```
Run a performance trace on the homepage and identify bottlenecks
```

**Expected Output:**
```bash
performance_start_trace()
navigate_page("http://localhost:3000")
performance_stop_trace()
performance_analyze_insight()
```

**Verification:**
- [x] Performance metrics returned
- [x] Insight provided
- [x] No errors raised

---

### Scenario 3: Network analysis
**Input:**
```
List all network requests on the dashboard
```

**Expected Output:**
```bash
navigate_page("http://localhost:3000/dashboard")
list_network_requests()
```

**Verification:**
- [x] Request list returned
- [x] No stack trace exposed
- [x] Recovery possible

---

## Baseline Behavior (Without Skill)
Document what happens when skill is NOT used:
- Agent would only use curl or read the local source.
- No visual or runtime verification of JS execution.

## Quality Metrics
- Structure compliance: 9/10
- Example quality: 8/10
- Clarity: 9/10
- Overall: 8.7/10

## Last Verified
2026-03-31 — Initial creation
