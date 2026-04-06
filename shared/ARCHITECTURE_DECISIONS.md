# Architecture Decisions

Canonical reference for API patterns, authentication, data layer, testing strategy, code organization, and resolved questions.

**Used by:** spec-writer, ticket-critic, cleanup, tdd, and other planning skills.

**Project-specific overrides:** See `./STANDARDS.md` in the target project.

---

## API Pattern

- **Default:** REST with JSON responses
- **Endpoint structure:** `/api/{domain}/{action}` or `/api/{resource}/{id}`
- **Error format:** `{error: string, details?: object}`
- **Status codes:** 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation error), 500 (server error)

## Authentication & Authorization

- **Auth mechanism:** JWT via `Authorization: Bearer <token>` header
- **Session storage:** Stateless JWT (no server-side sessions)
- **Role-based access:** `is_admin` role for admin endpoints
- **Rate limiting:** 100 requests/minute per user (adjust per project)

## Data Layer

- **Database:** PostgreSQL (default), SQLAlchemy ORM
- **Migrations:** Alembic (Python) or Prisma (Node)
- **Connection pooling:** Use framework defaults unless performance requires tuning

## Testing Strategy

- **Backend:** pytest (Python) / Vitest (Node)
- **Frontend:** Vitest + React Testing Library
- **E2E:** Playwright (preferred) or Cypress
- **Coverage targets:** 80% line coverage for new code, 70% for refactors
- **Test structure:** Co-develop tests with implementation (TDD where specified)

## Code Organization

### Backend structure:
```
src/
├── api/
│   ├── routes/    # HTTP endpoint handlers
│   ├── dto/       # Data transfer objects (Pydantic models)
│   └── helpers.py # Shared helper functions
├── domain/        # Pure business logic (no external deps)
├── services/      # Orchestration, calls domain + infrastructure
├── config/        # Configuration loading
└── models/        # Database models
```

### Frontend structure:
```
react-app/src/
├── components/ # Reusable UI components
├── pages/      # Route-level components
├── hooks/      # Custom React hooks
├── stores/     # State management (Zustand, Redux, etc.)
├── api/        # API client functions
└── types/      # TypeScript types
```

## File Size Limits

- **Soft limit:** 300 lines (proactively suggest refactoring)
- **Hard limit:** 500 lines (must refactor before merging)
- **Exceptions:** DTO files, generated code, test fixtures

---

## Layer Ownership

### Domain Layer
- **Purpose:** Pure business logic, business rules
- **Dependencies:** Standard library only
- **No:** Database calls, HTTP requests, file I/O, external APIs
- **Examples:** `TaskRecord`, `TaskState`, validation logic, business calculations

### Service Layer
- **Purpose:** Orchestration, business workflows
- **Dependencies:** Domain layer + infrastructure (DB, HTTP, files)
- **Responsibilities:** Transaction management, error handling, logging
- **Examples:** `generation_service.py`, `batch_service.py`

### Application Layer (if used)
- **Purpose:** Adapters for external interfaces
- **Dependencies:** Service layer + frameworks
- **Responsibilities:** HTTP handlers, CLI commands, message queue consumers
- **Examples:** FastAPI route handlers, CLI commands

### Infrastructure Layer
- **Purpose:** External system adapters
- **Dependencies:** Frameworks, drivers, SDKs
- **Responsibilities:** Database access, HTTP clients, file operations
- **Examples:** Database repositories, ComfyUI client, S3 client

---

## Resolved Questions

**Q: Where do new endpoints go?**
**A:** `src/api/routes/{domain}.py` following FastAPI router pattern. One router per domain.

**Q: How to handle validation errors?**
**A:** Return 422 Unprocessable Entity with `{error, details}` schema.

**Q: When to add tests?**
**A:** Every public function in domain/service layers; integration tests for all routes.

**Q: How to handle file uploads securely?**
**A:** Validate file type (magic bytes), sanitize filename, store in dedicated uploads directory, serve via controlled endpoint.

**Q: When is subprocess execution acceptable?**
**A:** Only when: no alternative, arguments fully validated, process isolated, user input cannot affect command, logged for audit.

**Q: What state management pattern for frontend?**
**A:** Global state: Zustand stores. Page state: React local state or URL query params. Form state: React Hook Form.

**Q: How to handle API response size limits?**
**A:** Default limit: 100 items. Pagination: `?limit=20&offset=0` or cursor-based. Large payloads: return job ID, async notification.

**Q: What's the refactoring priority?**
**A:** Pain-based: 1) highest merge conflict frequency, 2) highest churn, 3) blocking feature work, 4) >500 lines (only if causing problems).

---

## Security Checklist

Before implementing any feature, verify:

- [ ] **User input validation:** All user input validated (type, length, format, range)
- [ ] **Path traversal prevention:** File paths sanitized, allowlist directories
- [ ] **Subprocess isolation:** Arguments validated, `shell=False`, resource limits
- [ ] **Auth requirements:** Endpoints require authentication if sensitive
- [ ] **Authorization checks:** User has permission for requested action
- [ ] **Rate limiting:** Endpoints protected from abuse
- [ ] **Audit logging:** Sensitive operations logged (who, what, when)
- [ ] **Error messages:** No sensitive info in error responses

---

## Performance Budgets

**Default targets (adjust per project):**

- **API response time:** <200ms for simple queries, <1s for complex
- **Frontend render:** <3s for initial load, <100ms for interactions
- **File upload:** <10s for files <10MB
- **Queue processing:** <60s per job (timeout at 90s)
- **Memory usage:** <500MB per process (alert at 400MB)

**Cleanup strategies:**

- In-memory caches: LRU eviction, max 100 entries, 1-hour TTL
- Temp files: Clean on startup, 24-hour TTL
- Run history: Keep last 10 entries, archive older

---

## Decision Framework

### When to Block vs. Proceed

**Proceed without blocking if:**
- Question answered in this file
- Assumption is Tier 1 (reversible, low impact)
- Change is behind feature flag
- Test coverage exists to catch mistakes

**Block for human clarification if:**
- Security vulnerability possible
- Architecture contradiction (conflicting tickets)
- Dependency not implemented/merged
- Success criteria undefined
- Tier 3 assumption (auth, data model, public API)

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for tier definitions.
