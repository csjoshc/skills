# Resolved Questions

### Q: Where do new endpoints go?
**A:** `src/api/routes/{domain}.py` following FastAPI router pattern. One router per domain (wildcards, batches, generation, queue, uploads, presets, health).

### Q: How to handle validation errors?
**A:** Return 422 Unprocessable Entity with schema:
```json
{
  "error": "Validation failed",
  "details": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "password", "message": "Must be at least 8 characters"}
  ]
}
```

### Q: When to add tests?
**A:** Every public function in domain/service layers; integration tests for all routes. Refactors that change public APIs require verification tests.

### Q: How to name batch output folders?
**A:** Incremental numbering: `batch_0001`, `batch_0002`, etc. (4-digit zero-padded). Counter persists in `.batch_counter` JSON file.

### Q: What's the workflow-to-backend mapping?
**A:** Workflows select different ComfyUI workflow JSON files. Mapping defined in `configs/workflows/{workflow_name}.json`.

### Q: How to handle file uploads securely?
**A:**
1. Validate file type (magic bytes, not just extension)
2. Sanitize filename (remove path separators, limit length)
3. Store in dedicated uploads directory (not user-accessible paths)
4. Serve via controlled endpoint (not direct file access)

### Q: When is subprocess execution acceptable?
**A:** Only when:
1. No alternative (e.g., must run external tool)
2. Arguments are fully validated (whitelist, regex)
3. Process is isolated (resource limits, no network)
4. User input cannot affect command (no shell injection)
5. Logged for audit trail

### Q: What state management pattern for frontend?
**A:**
- Global state: Zustand stores (`src/stores/`)
- Page state: React local state or URL query params
- Form state: React Hook Form or similar
- Cleanup: Clear global state on navigation/logout

### Q: How to handle API response size limits?
**A:**
- Default limit: 100 items per response
- Pagination: `?limit=20&offset=0` or cursor-based
- Large payloads: Return job ID, async completion notification

### Q: What's the refactoring priority?
**A:** Pain-based, not line-count-based:
1. Files with highest merge conflict frequency
2. Files with highest churn (commits in last 3 months)
3. Files blocking feature work
4. Files >500 lines (only if causing problems)
