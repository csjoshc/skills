# Audit Finding Examples

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
- [ ] API contract defined in STANDARDS.md, OR
- [ ] Task 0 added: "Verify backend endpoint exists"

Evidence: Section 2 "API contracts" assumes endpoint exists
```

## Example 2: Auto-Resolved via STANDARDS.md

**Ticket excerpt:**
> "Open question: Should API use REST or GraphQL?"

**Audit finding:**
```
### Pattern 6: Missing Decision Points — ⚠️ AUTO-RESOLVED

Issue: API pattern undecided

Resolution: STANDARDS.md section "API Pattern" says:
> "Default: REST with JSON responses"

Action: Applied REST pattern, updated ticket assumptions

Evidence: STANDARDS.md "API Pattern" section
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
- [ ] STANDARDS.md security checklist applied

Evidence: Section 2 "API contracts" lacks validation spec
```
