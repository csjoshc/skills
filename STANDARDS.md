# Project Standards — Single Source of Truth

**Location:** `~/.skills/STANDARDS.md` (global) + optional project-level merge

**Purpose:** Resolve common architectural questions autonomously so agents don't block waiting for human clarification.

## When editing files, prioritize reading the file immediately before editing to capture exact indentation and whitespace. Use the shortest unique snippet possible for oldString to prevent matching failures.

## How to Use This File

**Agents:** Before blocking on an assumption or open question:

1. Check if it's answered in this file
2. If yes → apply the resolution, proceed without blocking
3. If no → block for human clarification, then propose addition to this file

**Humans:** When an agent blocks on a question you've already decided:

1. Add the decision to this file
2. Tell agent to re-check STANDARDS.md
3. Agent proceeds without further clarification

**Onboarding to new projects:**

- Check if `~/.skills/STANDARDS.md` exists
- If yes → read it, merge project-specific additions
- If no → create from template, populate as questions arise

---

## Pre-Flight Checklist — Blocker Detection

**Purpose:** Catch blocking issues during ticket review, not during implementation. Run this checklist BEFORE marking a ticket READY.

### 1. Dependency Detection

**Trigger:** Ticket mentions functionality that may not exist yet.

**Check for these patterns:**

- [ ] "Already returns X" without file reference
- [ ] "Backend provides X" without endpoint specification
- [ ] "Frontend calls X" without API contract
- [ ] "Uses existing X" without linking to existing implementation
- [ ] Depends on another ticket that's not merged

**If any match → Add to ticket:**

```markdown
### Dependencies

**Blocking Dependencies:**

- [ ] #TicketNumber — [what's needed, e.g., "POST /api/workflow/load endpoint"]
- [ ] #TicketNumber — [what's needed]

**Dependency Status:**

- [ ] All dependencies merged to main
- [ ] API contracts stable (no pending changes)
- [ ] OR Task 0 added: "Verify [dependency] exists"
```

**Action:** Create linked dependency ticket or add Task 0 verification.

---

### 2. Redesign / Redarchitecture Triggers

**Trigger:** Original design has flaws that block implementation.

**Check for these patterns:**

- [ ] "OUT of scope: X" but X is required for feature to work
- [ ] Security vulnerability (user input → sensitive operation without validation)
- [ ] Subprocess execution from HTTP endpoint
- [ ] Direct file path exposure (path traversal risk)
- [ ] Architecture contradicts existing patterns
- [ ] Layer confusion (domain logic + infrastructure in same module)

**If any match → Add to ticket:**

```markdown
### Design Issues

**Critical Flaws:**

- [ ] [Describe flaw, e.g., "Security: user input to subprocess without validation"]
- [ ] [Describe flaw, e.g., "Scope gap: X is OUT of scope but required for Y"]

**Required Redesign:**

- [ ] Security review completed
- [ ] Scope boundary updated (move X from OUT to IN scope)
- [ ] OR Task 0 added: "Redesign [component] to address [flaw]"

**Proposed Solution:** [brief description of fix]
```

**Action:** Redesign before implementation, or add Task 0 for redesign spike.

---

### 3. Contradicting Ticket Detection

**Trigger:** Multiple tickets make conflicting recommendations.

**Check for these patterns:**

- [ ] Ticket A says "split X", Ticket B says "keep X cohesive"
- [ ] Both tickets approved for same system with different approaches
- [ ] No coordinating ticket for related refactors
- [ ] Refactor tickets without dependency sequencing

**If any match → Add to ticket:**

```markdown
### Architectural Contradictions

**Conflicts With:**

- [ ] #TicketNumber — [describe contradiction, e.g., "says split api_types.py, this says keep as-is"]

**Resolution Required:**

- [ ] Coordinating ticket (#TicketNumber) approves this approach
- [ ] STANDARDS.md updated with architectural decision
- [ ] OR Task 0 added: "Resolve contradiction with #TicketNumber"

**Coordinating Ticket:** #TicketNumber (if applicable)
```

**Action:** Designate coordinating ticket, resolve contradiction before implementation.

---

### 4. Research / Vagueness Detection

**Trigger:** Ticket lacks detail needed for implementation.

**Check for these patterns:**

- [ ] "Open questions" section with unanswered items
- [ ] "TBD" or "FIXME" in spec
- [ ] Multiple approaches listed without selection
- [ ] UI location, API pattern, or data model undecided
- [ ] Success criteria without baseline/target/measurement
- [ ] "Works correctly" (not binary)
- [ ] No tests specified for refactor

**If any match → Add to ticket:**

```markdown
### Research Needed

**Unanswered Questions:**

- [ ] [Question 1, e.g., "Where does import UI live: Generator tab or settings modal?"]
- [ ] [Question 2, e.g., "What's the baseline coverage for target files?"]

**Required Research:**

- [ ] STANDARDS.md checked for resolved questions
- [ ] Task 0 added: "Research [topic]"
- [ ] OR decision made and documented in ticket

**Research Type:** [dependency / redesign / contradiction / vagueness]
```

**Action:** Add Task 0 research spike, or answer questions before implementation.

---

### Quick Reference: Blocker Patterns

| Pattern             | Example                              | Action                           |
| ------------------- | ------------------------------------ | -------------------------------- |
| **Dependency**      | "Backend returns X" without endpoint | Add dependency ticket or Task 0  |
| **Security**        | User input → subprocess              | Redesign + security review       |
| **Scope Gap**       | "OUT of scope: X" but X required     | Move to IN scope or split ticket |
| **Contradiction**   | Ticket A vs Ticket B conflict        | Coordinating ticket resolves     |
| **Vagueness**       | "Works correctly"                    | Define binary criteria           |
| **No Baseline**     | "≥90% coverage"                      | Measure baseline first           |
| **No Tests**        | Refactor without tests               | Add verification tests           |
| **Layer Confusion** | Domain + infrastructure mixed        | Clarify layer ownership          |

---

## Ticket Review Workflow

**Before marking ticket READY:**

1. **Run blocker detection checklist** (4 sections above)
2. **For each blocker found:**
   - Add appropriate section to ticket (Dependencies / Design Issues / Contradictions / Research)
   - Add Task 0 if verification/research needed
   - Link to coordinating ticket if contradiction
3. **Update ticket status:**
   - READY → No blockers found, or all blockers resolved
   - NEEDS_REVISION → Blockers found, add sections above
   - BLOCKED → Critical blocker (security, architecture contradiction)

**During ticket review meeting:**

1. Review blocker sections in each ticket
2. Make decisions on open questions
3. Assign coordinating tickets for contradictions
4. Approve Task 0 research spikes
5. Update STANDARDS.md with new decisions

---

## Examples from Recent Audit

### Example 1: Dependency Detection (Ticket 01)

**Pattern Found:** "Backend already returns `faceRefPath`" but no endpoint to serve image

**Added to Ticket:**

```markdown
### Dependencies

**Blocking Dependencies:**

- [ ] NEW — Backend endpoint to serve face reference images
  - Required: `GET /api/static/uploads/faces/:filename` or similar
  - Security: Path validation to prevent traversal attacks

**Dependency Status:**

- [ ] Endpoint implemented and merged
- [ ] OR Task 0 added: "Verify/create static file serving endpoint"
```

**Action:** Added Task 0 to verify endpoint exists, create if not.

---

### Example 2: Security Redesign (Ticket 03)

**Pattern Found:** Subprocess execution from HTTP endpoint (`pytest` via `subprocess.Popen`)

**Added to Ticket:**

```markdown
### Design Issues

**Critical Flaws:**

- [ ] Security: `POST /api/admin/tests/run` executes pytest via subprocess
  - Risk: Remote code execution if auth bypassed
  - Risk: Command injection via test name parameter

**Required Redesign:**

- [ ] Security review completed
- [ ] Choose mitigation:
  - Option A: Move to separate service/job queue (Celery, RQ)
  - Option B: Use `asyncio.create_subprocess_exec()` with strict validation
  - Option C: Document as DEV-ONLY, add multiple auth layers
- [ ] OR Task 0 added: "Redesign test execution for security"
```

**Action:** Blocked until security approach decided.

---

### Example 3: Contradiction Detection (Tickets 32 vs 36)

**Pattern Found:** Ticket 32 says "split api_types.py", Ticket 36 says "keep as-is"

**Added to Both Tickets:**

```markdown
### Architectural Contradictions

**Conflicts With:**

- [ ] #36 — Says "Keep as-is — DTOs are cohesive", this ticket says split

**Resolution Required:**

- [ ] Coordinating ticket (#36) approves split approach
- [ ] STANDARDS.md updated with architectural decision
- [ ] OR Task 0 added: "Resolve contradiction with #36"

**Coordinating Ticket:** #36
```

**Action:** Ticket 36 designated as gate for refactor tickets.

---

### Example 4: Research/Vagueness (Ticket 22)

**Pattern Found:** "OUT of scope: changing ComfyUI JSON" but workflow must affect backend somehow

**Added to Ticket:**

```markdown
### Research Needed

**Unanswered Questions:**

- [ ] What does workflow selection actually DO at backend level?
  - Select different ComfyUI workflow JSON files?
  - Apply different parameter constraints?
  - Modify generation pipeline behavior?

**Required Research:**

- [ ] Task 0 added: "Research workflow-to-backend mapping"
- [ ] Decision documented in ticket before Task 1

**Research Type:** vagueness + redesign
```

**Action:** Added Task 0 to clarify architecture.

---

### Example 5: No Baseline (Ticket 28)

**Pattern Found:** "≥90% line coverage" without baseline measurement

**Added to Ticket:**

```markdown
### Research Needed

**Unanswered Questions:**

- [ ] What is current baseline coverage for target files?

**Required Research:**

- [ ] Task 0b added: "Measure baseline coverage"
- [ ] Adjust 90% target if unrealistic (e.g., start with 70% → 80% → 90%)

**Research Type:** vagueness
```

**Action:** Added Task 0b to measure baseline before setting target.

---

## Ticket Review Template

**Copy this template into tickets that need blocker sections added:**

````markdown
---

## SECTION 4: BLOCKING ISSUES & SCOPE CLARIFICATIONS

### Status: READY / NEEDS_REVISION / BLOCKED

### Dependencies

**Blocking Dependencies:**
- [ ] #TicketNumber — [what's needed]
- [ ] OR Task 0 added: "Verify [dependency] exists"

**Dependency Status:**
- [ ] All dependencies merged to main
- [ ] API contracts stable

---

### Design Issues

**Critical Flaws:**

- [ ] [Describe flaw]

**Required Redesign:**

- [ ] Security review completed
- [ ] Scope boundary updated
- [ ] OR Task 0 added: "Redesign [component]"

**Proposed Solution:** [brief description]

---

### Architectural Contradictions

**Conflicts With:**

- [ ] #TicketNumber — [describe contradiction]

**Resolution Required:**

- [ ] Coordinating ticket (#TicketNumber) approves
- [ ] STANDARDS.md updated with decision
- [ ] OR Task 0 added: "Resolve contradiction"

**Coordinating Ticket:** #TicketNumber

---

### Research Needed

**Unanswered Questions:**

- [ ] [Question 1]
- [ ] [Question 2]

**Required Research:**

- [ ] STANDARDS.md checked
- [ ] Task 0 added: "Research [topic]"
- [ ] OR decision made

**Research Type:** [dependency / redesign / contradiction / vagueness]

---

### Pre-Flight Checklist

```markdown
- [ ] Task 0 (verify dependencies) completed
- [ ] Task 0b (research/redesign) completed
- [ ] STANDARDS.md checked for resolved questions
- [ ] Coordinating ticket approved (if applicable)
```
````

```

---

## Architecture Decisions

### API Pattern
- **Default:** REST with JSON responses
- **Endpoint structure:** `/api/{domain}/{action}` or `/api/{resource}/{id}`
- **Error format:** `{error: string, details?: object}`
- **Status codes:** 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation error), 500 (server error)

### Authentication & Authorization
- **Auth mechanism:** JWT via `Authorization: Bearer <token>` header
- **Session storage:** Stateless JWT (no server-side sessions)
- **Role-based access:** `is_admin` role for admin endpoints
- **Rate limiting:** 100 requests/minute per user (adjust per project)

### Data Layer
- **Database:** PostgreSQL (default), SQLAlchemy ORM
- **Migrations:** Alembic (Python) or Prisma (Node)
- **Connection pooling:** Use framework defaults unless performance requires tuning

### Testing Strategy
- **Backend:** pytest (Python) / Vitest (Node)
- **Frontend:** Vitest + React Testing Library
- **E2E:** Playwright (preferred) or Cypress
- **Coverage targets:** 80% line coverage for new code, 70% for refactors
- **Test structure:** Co-develop tests with implementation (TDD where specified)

### Code Organization
- **Backend structure:**
```

src/
├── api/
│ ├── routes/ # HTTP endpoint handlers
│ ├── dto/ # Data transfer objects (Pydantic models)
│ └── helpers.py # Shared helper functions
├── domain/ # Pure business logic (no external deps)
├── services/ # Orchestration, calls domain + infrastructure
├── config/ # Configuration loading
└── models/ # Database models

```

- **Frontend structure:**
```

react-app/src/
├── components/ # Reusable UI components
├── pages/ # Route-level components
├── hooks/ # Custom React hooks
├── stores/ # State management (Zustand, Redux, etc.)
├── api/ # API client functions
└── types/ # TypeScript types

````

### File Size Limits
- **Soft limit:** 300 lines (proactively suggest refactoring)
- **Hard limit:** 500 lines (must refactor before merging)
- **Exceptions:** DTO files, generated code, test fixtures

### Commenting & Docstrings

**Python:**
- **Format:** Google style ([reference](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings))
- **Enforcement:** Ruff with `pydocstyle` rule
- **Config:**
```toml
[lint]
extend-select = ["D"]

[lint.pydocstyle]
convention = "google"
```
- **Required for:** All public functions, classes, and modules

**JavaScript/TypeScript:**
- **Format:** JSDoc with TypeScript annotations
- **Enforcement:** ESLint with `eslint-plugin-jsdoc`
- **Config:**
```js
{
  plugins: ["jsdoc"],
  rules: {
    "jsdoc/require-description": "error",
    "jsdoc/require-param": "error",
    "jsdoc/require-returns": "error"
  }
}
```
- **Required for:** All exported functions, classes, and types

**When to document:**
- Every public function/method (including test helpers)
- Classes with non-trivial state
- Complex business logic
- API route handlers (brief summary + params)

**When to skip:**
- Private helpers under 5 lines
- Simple type aliases
- Test assertions (test names serve as documentation)

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
````

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

---

## Security Checklist

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

- Question answered in STANDARDS.md
- Assumption is Tier 1 (reversible, low impact)
- Change is behind feature flag
- Test coverage exists to catch mistakes

**Block for human clarification if:**

- Security vulnerability possible
- Architecture contradiction (conflicting tickets)
- Dependency not implemented/merged
- Success criteria undefined
- Tier 3 assumption (auth, data model, public API)

### Assumption Tiers

**Tier 1: Reversible (LOW impact)**

- Naming conventions, file locations, UI copy
- Library choices with easy migration path
- **Action:** Proceed, flag for post-review

**Tier 2: Architecture (MEDIUM impact)**

- API patterns, data model structure, layer ownership
- Harder to change but not breaking
- **Action:** Check STANDARDS.md, block if unresolved

**Tier 3: Safety/Security (HIGH impact)**

- Authentication, authorization, data sensitivity
- Public API contracts, database schema
- **Action:** Always block for human confirmation

---

## Project-Specific Additions

_(Merge project-specific standards below this line)_

### [Project Name] — Added [Date]

**Stack adjustments:**

- [Add any deviations from default stack]

**Architecture decisions:**

- [Add project-specific ADRs]

**Resolved questions:**

- [Add project-specific Q&A]

**Security requirements:**

- [Add project-specific security checklist items]

**Performance targets:**

- [Add project-specific performance budgets]

---

## Maintenance

**Update this file when:**

- Human clarifies a question that blocked an agent
- Architecture decision made during implementation
- Security pattern identified that should be reused
- Performance issue discovered that needs prevention

**Review cadence:** Every 3 months or when onboarding to significantly different project

**Merge strategy:** When onboarding to new project, preserve global standards, append project-specific section.
