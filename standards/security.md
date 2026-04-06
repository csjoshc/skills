# Security Checklist

**Before implementing any feature, verify:**

- [ ] **User input validation:** All user input validated (type, length, format, range)
- [ ] **Path traversal prevention:** File paths sanitized, allowlist directories
- [ ] **Subprocess isolation:** Arguments validated, `shell=False`, resource limits
- [ ] **Auth requirements:** Endpoints require authentication if sensitive
- [ ] **Authorization checks:** User has permission for requested action
- [ ] **Rate limiting:** Endpoints protected from abuse
- [ ] **Audit logging:** Sensitive operations logged (who, what, when)
- [ ] **Error messages:** No sensitive info in error responses

**If any box unchecked → block for security review before Task 1**

## Subprocess Execution Guidelines

Subprocess execution is only acceptable when ALL conditions are met:

1. **No alternative** — must run external tool, no library equivalent
2. **Fully validated arguments** — whitelist allowed commands, regex-validate parameters
3. **Process isolation** — resource limits (CPU, memory, timeout), no network access
4. **No shell injection** — `shell=False`, use argument arrays, never interpolate user input
5. **Audit trail** — log command, arguments, exit code, and duration

**Never:**
- Pass user input directly to shell commands
- Use `shell=True` with any external input
- Execute commands from uploaded files
- Run subprocesses from public-facing endpoints without auth
