# Audit Finding Examples

---

## Example 0A: Ralph flag — PASS (eligible ticket, correct schema)

**Ticket excerpt:**
```yaml
---
Stage: BUILD
Ralph: true
Ralph-Reason: "7 additive ACs: new parser module + tests, each grep/pytest-checkable, no bootstrap"
---
```
AC→Tests table has 7 rows, each with a `grep -nE` or `pytest -k` command. Failure Protocol says "revert new files" (not "revert all callers"). No bootstrap language.

**Audit finding:**
```
### Ralph Flag Audit — ✅ PASS

Ralph: true — Verified:
- AC count: 7 ✓ (≥6)
- Scope: additive (new module, new tests) ✓
- All ACs machine-checkable (grep/pytest) ✓
- No bootstrap or "after BUILD" ACs ✓
- Failure Protocol: revert new files only (not all) ✓
- Ralph-Reason: present and specific ✓
```

---

## Example 0B: Ralph flag — BLOCKED (flag contradicts scope)

**Ticket excerpt:**
```yaml
---
Stage: BUILD
Ralph: true
Ralph-Reason: "6 ACs, each checkable"
---
```
Scope section says: "Replace all callers of `run_attempt()` with the new `run_attempt_v2()` signature across the codebase."

**Audit finding:**
```
### Ralph Flag Audit — ❌ BLOCKER

Ralph: true — INVALID. Disqualifier detected:
- Scope is a cross-cutting refactor ("Replace all callers") — per-box commits leave
  callers broken between iterations. Half-done state is worse than not-done.
- This ticket must use Ralph: false.

Required action:
- [ ] Change Ralph: true → Ralph: false
- [ ] Update Ralph-Reason: "Refactor: cross-cutting caller rename, half-done state invalid"
```

---

## Example 0C: Ralph flag — BLOCKED (AC not machine-checkable)

**Ticket excerpt:**
```yaml
Ralph: true
Ralph-Reason: "8 ACs, all checkable"
```
AC→Tests table row: `AC-5 | Verify visually that the progress bar updates smoothly | manual | -`

**Audit finding:**
```
### Ralph Flag Audit — ❌ BLOCKER

Ralph: true — INVALID for AC-5.
- AC-5 uses manual verification. Under Ralph mode, ACs are load-bearing:
  the loop checks the box only when a command exits 0.
- A manual AC breaks the loop — the agent cannot verify it mechanically.

Required action:
- [ ] Replace AC-5 with a machine-checkable command, OR
- [ ] Change Ralph: false with Ralph-Reason explaining the manual AC
```

---

## Example 1: Unimplemented Dependency

**Ticket excerpt:**
> "Frontend calls `POST /api/workflow/load` to import workflow JSON"

**Audit finding:**
```
### Pattern 1: Unimplemented Dependencies — ❌ BLOCKER

Issue: Ticket assumes `POST /api/workflow/load` endpoint exists

Verification:
- Checked `src/server.py`: endpoint not found
- Checked open PRs: no PR for this endpoint
- Ticket dependencies: lists `fixes/implement/11-workflow-load-endpoint.md` (status: in progress)

Required before Task 1:
- [ ] Backend endpoint merged and deployed, OR
- [ ] API contract defined in Architecture Decisions, OR
- [ ] Task 0 added: "Verify backend endpoint exists"

Evidence: Section 2 "API contracts" assumes endpoint exists
```

## Example 2: Auto-Resolved via Architecture Decisions

**Ticket excerpt:**
> "Open question: Should API use REST or GraphQL?"

**Audit finding:**
```
### Pattern 6: Missing Decision Points — ⚠️ AUTO-RESOLVED

Issue: API pattern undecided

Resolution: Architecture Decisions section "API Pattern" says:
> "Default: REST with JSON responses"

Action: Applied REST pattern, updated ticket assumptions

Evidence: Architecture Decisions "API Pattern" section
```

## Example 3: Security Vulnerability

**Ticket excerpt:**
> "Endpoint accepts file path from user, serves file directly"

**Audit finding:**
```
### Pattern 5: Security Vulnerabilities — ❌ BLOCKER

Issue: User-provided file path served without validation

Risk: Path traversal attack (e.g., `../../../etc/passwd`)

Touchpoints needing security review:
- User input: file path parameter
- File access: direct file serving
- Missing: path validation, allowlist directories

Required before Task 1:
- [ ] Path validation strategy (sanitize, allowlist)
- [ ] Directory allowlist defined
- [ ] Architecture Decisions security checklist applied

Evidence: Section 2 "API contracts" lacks validation spec
```
