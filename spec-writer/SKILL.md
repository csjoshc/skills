---
name: spec-writer
description: Takes a vague feature request and generates a structured spec, technical plan, and task breakdown ready for any coding agent. Aligns with PDCA-T (Plan-Do-Check-Act-Test) and can follow exchanet METHOD.md patterns (FR/NFR/RISK, ADR, micro-tasks, test-first) when the user asks for strict or PDCA-T mode. Use whenever you're about to build a feature and want to reduce ambiguity before writing code. Invoke with /spec-writer followed by your feature description.
---

## TL;DR (Quick Start)

Turns vague feature requests into structured technical specs, implementation plans (PLAN), and atomic micro-tasks (TASKS). Mark every decision as `[ASSUMPTION: ...]`.

**When to use:** "write a spec for...", "plan this feature", "break this down into tasks".

**Invocation:**
```bash
/spec-writer <feature-description>
```

## Companion files (progressive disclosure)

- **Parallel or batched markdown tickets** (e.g. many tickets for one Orchestra run with `--concurrency` / `-j`, explicit `Depends-On:`): when the user asks for parallel tickets, a ticket batch, or `-j` / multi-ticket concurrency, read **`PARALLEL_TICKETS_BATCH.md`** in this same directory (`~/.skills/spec-writer/`) before generating the batch.

## Decision Tree

1. **How much ambiguity exists?**
   - LOW (obvious stack/goals) → Generate full SPEC + PLAN + TASKS.
   - MEDIUM/HIGH → Generate SPEC + PLAN + **Assumptions Summary**; wait for user feedback before TASKS.

2. **Is strict quality required (PDCA-T / METHOD.md)?**
   - YES → **MANDATORY** use 8-phase mapping and ≤ 50 lines per task.
   - NO → Standard 3-section output.

3. **Does the task hit a blast radius limit (>5 files)?**
   - YES → **MANDATORY** split into child certificates/tickets via `01a-`, `01b-` pattern.
   - NO → Proceed.

4. **Is the user asking for parallel / batched runner tickets (`-j`, many `.tickets/` files, explicit DAG)?**
   - YES → Read **`PARALLEL_TICKETS_BATCH.md`** (this folder), then apply its checklist plus any project ticket skill (e.g. Orchestra `orchestra-decomposed-tickets`).
   - NO → Continue with the sections below.

## Workflow

---

## Operating principles

**Mandatory SPEC file (Section 1)**
Without a written spec, agents invent UX, edge cases, and scope — then the human pays in refusals and refactors. Section 1 is non-optional: purpose, users, requirements, edge cases, and acceptance criteria must exist before implementation planning is trustworthy.

**Atomic micro-instructions (Section 3)**
Tasks are numbered, directly executable steps: **one discrete action per task** (or per sub-bullet if you split inside a task). No vague roll-ups like "wire up the feature." Each step should be doable and verifiable on its own.

**Project-specific rules and skills**
Honor repo rules, `AGENTS.md`, Cursor rules, and linked skills: **strict context, zero ambiguity** for stack, conventions, and boundaries. When the user names a project standard, the spec and tasks must reference it explicitly instead of assuming a generic stack.

**Risk-tiered assumptions**
Not all assumptions need human review. Before blocking:
1. Check embedded Architecture Decisions below for resolved questions
2. Tier 1 (reversible, low impact) → proceed, flag for post-review
3. Tier 2 (architecture, medium impact) → check Architecture Decisions, block if unresolved
4. Tier 3 (security/safety, high impact) → always block for human confirmation

**PDCA-T cycle**
Canonical definition and full phase spec: [exchanet/method_pdca-t_coding — METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md). **T** means **Test**: quality is built in each increment (criteria + automated tests + evidence), not only inspected at the end. **Traceability** (requirements → tasks → tests) supports every phase but is not a substitute for **T**.

Use PDCA-T as the mental model for every spec; mirror it in the three sections:

| Letter | In this skill |
|--------|----------------|
| **P — Plan** | SECTION 1 (SPEC) nails objective, scope, and acceptance; SECTION 2 (PLAN) nails architecture, contracts, and test strategy *before* implementation stories. |
| **D — Do** | SECTION 3 (TASKS): ordered micro-work — each step implementable and reversible. |
| **C — Check** | Given/When/Then criteria, per-task acceptance, PLAN testing strategy, **Review checkpoint** — verify against the spec and test results, not intent. |
| **A — Act** | Assumptions summary and `[ASSUMPTION: ...]` — human adjusts scope/design; feed corrections into the next Plan pass (updated SPEC/PLAN), not silent drift. |
| **T — Test** | Every meaningful task has **verifiable** outcomes; PLAN calls out unit / integration / e2e as appropriate. Prefer **test-first** for the implementing agent when the user or project standards require it (per METHOD Phase 4). |

Short loop: Plan (SPEC + PLAN) → Do (TASKS) → **Test** (write/run tests per strategy; show real results when the workflow requires it) → Check (criteria + metrics) → Act (assumptions / rescope) → repeat until delivery bar is met.

---

### Alignment with METHOD.md (8 phases)

Use this mapping when the user asks for **PDCA-T**, **METHOD.md**, or **strict** quality gates. You do not need to paste the entire METHOD — embed what helps the implementer.

| METHOD phase | What to produce in this skill |
|----------------|-------------------------------|
| **1 — Planning** | One-line purpose; explicit **IN scope / OUT of scope**; external dependencies; acceptance criteria agreed in writing (block vague objectives — flag with `[ASSUMPTION]` until clarified). |
| **2 — Requirements analysis** | Optional but recommended for complex work: **FR-NN** / **NFR-NN** / **RISK-NN** blocks (see below) in addition to plain Requirements / edge cases. |
| **3 — Architecture design** | PLAN: non-trivial decisions as **ADR-NN**; API/contracts sketched before tasks; module or layer layout if it reduces ambiguity. |
| **4 — Micro-task cycle** | TASKS: small increments; note **≤ ~50 lines of production code per micro-task** when using strict PDCA-T (excluding tests/docs — per METHOD). Sub-task checklist: context/skills → contract exists → **test categories** (happy, error, edge, security, performance where relevant) → implement → review → run tests. |
| **5 — Integral validation** | PLAN **Testing strategy** + TASK criteria should enable full validation later (security, coverage targets, architecture checks) — state expectations if the user’s METHOD.md workflow applies. |
| **6 — Technical debt** | Known gaps: register as **DEBT-NN** (or defer to assumptions) instead of silent TODOs in “done” work. |
| **7 — Refinement** | Loop until agreed targets (e.g. coverage, failing tests) — specify targets in PLAN when user requires METHOD-grade gates. |
| **8 — Delivery** | Out of scope for spec-writer output unless the user asks: then add a short **Delivery evidence** stub (what to attach: test run, coverage, decisions, debt list). |

**Optional formats** (use when complexity or user request warrants):

```
FR-01: [Functional requirement]
  Acceptance: [How to verify]
  Priority: Must | Should | Could

NFR-01: [Constraint / quality attribute]
  Metric: [Measurable target]
  Verification: [How to measure]

RISK-01: [Risk]
  Probability: High | Medium | Low
  Impact: High | Medium | Low
  Mitigation: [Action]

ADR-01: [Decision title]
  Context: [Why decide]
  Decision: [One sentence]
  Alternatives: [What else was considered]
  Consequences: [Tradeoffs]

DEBT-01: [Title]
  Type: Technical | Test | Documentation | Architecture | Security | Performance
  Description: [What / why]
  Impact: High | Medium | Low
  Plan: [Next step]
```

---

## Architecture Decisions (Embedded from STANDARDS.md)

**Purpose:** Resolve common architectural questions autonomously. Check this section before blocking on assumptions.

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
```

### File Size Limits
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
**A:** `src/api/routes/{domain}.py` following FastAPI router pattern. One router per domain (wildcards, batches, generation, queue, uploads, presets, health).

**Q: How to handle validation errors?**
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

**Q: When to add tests?**
**A:** Every public function in domain/service layers; integration tests for all routes. Refactors that change public APIs require verification tests.

**Q: How to name batch output folders?**
**A:** Incremental numbering: `batch_0001`, `batch_0002`, etc. (4-digit zero-padded). Counter persists in `.batch_counter` JSON file.

**Q: How to handle file uploads securely?**
**A:**
1. Validate file type (magic bytes, not just extension)
2. Sanitize filename (remove path separators, limit length)
3. Store in dedicated uploads directory (not user-accessible paths)
4. Serve via controlled endpoint (not direct file access)

**Q: When is subprocess execution acceptable?**
**A:** Only when:
1. No alternative (e.g., must run external tool)
2. Arguments are fully validated (whitelist, regex)
3. Process is isolated (resource limits, no network)
4. User input cannot affect command (no shell injection)
5. Logged for audit trail

**Q: What state management pattern for frontend?**
**A:**
- Global state: Zustand stores (`src/stores/`)
- Page state: React local state or URL query params
- Form state: React Hook Form or similar
- Cleanup: Clear global state on navigation/logout

**Q: How to handle API response size limits?**
**A:**
- Default limit: 100 items per response
- Pagination: `?limit=20&offset=0` or cursor-based
- Large payloads: Return job ID, async completion notification

**Q: What's the refactoring priority?**
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

- Question answered in Architecture Decisions above
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
- **Action:** Check Architecture Decisions above, block if unresolved

**Tier 3: Safety/Security (HIGH impact)**

- Authentication, authorization, data sensitivity
- Public API contracts, database schema
- **Action:** Always block for human confirmation

---

## How to invoke

```
/spec-writer [feature description]
```

Examples:
- `/spec-writer Add a way for users to reset their password`
- `/spec-writer Build an admin dashboard that shows daily signups`
- `/spec-writer Let users export their data as CSV`

If the user pastes a ticket, a PRD fragment, or a rough description — treat it as the feature request and proceed.

---

## Output format

Produce three sections in order. Do not skip any section. Do not merge them.

---

### Ticket Stage Header Contract (mandatory for `.tickets/*.md` outputs)

When the output is a ticket file, include a YAML header and use the canonical stage field:

```yaml
---
Stage: BUILD
---
```

Use `Stage:` (not `Status:`) for canonical routing.
Allowed stage enum (single line): `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
When a ticket is implementation-ready, set **exactly** `Stage: BUILD`.

---

### SECTION 1: SPEC

**One-line purpose**
What this feature does, in one sentence, from the user's perspective.

**Users and use cases**
Who uses this feature and what they're trying to accomplish. List each use case as: `As a [user type], I want to [action] so that [outcome].`

**Requirements**
What must be true for this feature to work. Numbered list. Functional only — no implementation details.

**Scope boundary (recommended)**  
Short **IN scope** / **OUT of scope** lists so agents do not gold-plate or miss boundaries (METHOD Phase 1).

**Edge cases**
What can go wrong or behave unexpectedly. For each: describe the situation and the expected behavior.

**Acceptance criteria**
Use Given/When/Then format. One criterion per scenario. Cover the happy path first, then edge cases.

```
Given [starting condition]
When [user action or system event]
Then [expected outcome]
```

Mark every assumption with `[ASSUMPTION: ...]` inline. Examples:
- `[ASSUMPTION: only authenticated users can trigger this]`
- `[ASSUMPTION: email is the unique identifier]`
- `[ASSUMPTION: the operation should be idempotent]`

---

### SECTION 2: PLAN

**Stack and architecture**
State what you know about the user's stack from context. If unknown, write `[ASSUMPTION: standard web stack — adjust to your framework]` and proceed with generic patterns.

**Data model changes**
What needs to be created, modified, or deleted in the data layer. Be specific about fields and types.

**API contracts**
Endpoints or functions needed. For each: method, path or name, inputs, outputs, error states.

**Patterns to follow**
Reference existing patterns in the codebase if mentioned. If not mentioned, flag: `[ASSUMPTION: following standard CRUD pattern — point me to your auth/data layer if you want me to match your conventions]`

**Testing strategy**
What needs unit tests, integration tests, and end-to-end tests. Specify coverage expectations for critical paths. For PDCA-T / METHOD.md workflows: call out **test-first** where required, categories per feature (happy path, error, edge, security, performance as applicable), and any **quality targets** (e.g. coverage floor) the user or repo mandates.

**Security and performance constraints**
Authentication requirements, authorization rules, rate limits, response time targets. Mark each unknown as `[ASSUMPTION: ...]`.

**Architecture decisions (optional)**
For non-trivial choices, add **ADR-NN** entries (see Operating principles). Trivial patterns can stay prose-only.

---

### SECTION 3: TASKS

Break the plan into **ordered atomic micro-instructions**: numbered tasks where each one is a **single** concrete action an agent can execute without inventing missing steps.

Each task must:
- Be completable in a single agent session
- Produce a verifiable, testable change
- Contain all context needed — no assumptions, no "see previous task"
- Have its own mini acceptance criteria
- Stay **one action per task** where possible; if a task must bundle steps, use numbered sub-steps, each still verifiable (**Do** + **Check** + **Test** at micro scale)
- When aligning with [METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md) Phase 4: aim for **≤ ~50 lines** of production change per task (excluding tests/docstrings); split otherwise

Format each task as:

```
## Task N: [Title]

**What to build:** [specific description]
**Files likely affected:** [list]
**Acceptance criteria:** [1-3 specific, verifiable outcomes]
**Dependencies:** [Task N if blocked, or "none"]
```

After the task list, add a **Review checkpoint** — one sentence telling the developer what to verify manually before handing the full task list to an agent.

---

## Assumptions & Escalation

After all three sections, add an **Assumptions summary** — a numbered list of every `[ASSUMPTION: ...]` you marked, in order of importance. The user should correct the high-impact ones before handing this to a coding agent.

**Before listing assumptions:**
1. Check embedded Architecture Decisions above for resolved questions
2. If Architecture Decisions resolves it → auto-apply, mark as "Resolved via Architecture Decisions"
3. If not resolved → tier by impact and list for review

**Tier definitions:**
- **Tier 1 (LOW impact):** Reversible, naming, file locations, UI copy → proceed without blocking
- **Tier 2 (MEDIUM impact):** Architecture patterns, data model, library choices → check Architecture Decisions, block if unresolved
- **Tier 3 (HIGH impact):** Security, auth, public API, database schema → always block for human confirmation

Format:
```
## Assumptions to review

1. [ASSUMPTION text] — Impact: HIGH / MEDIUM / LOW — Tier: 1 / 2 / 3
   Correct this if: [when it matters]
   [Optional: Resolved via Architecture Decisions section X]

2. ...
```

**Blocking guidance:**
- Tier 1: No block needed, flag for post-review
- Tier 2: Block if Architecture Decisions doesn't resolve
- Tier 3: Always block before Task 1

---

## Quality rules

- Ticket files must include canonical YAML header with `Stage:`. For implementation-ready tickets generated by this skill, write `Stage: BUILD` and keep stage values within: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
- **SPEC is mandatory** (Section 1). Skipping it causes invented design; keep it technology-agnostic — no framework names, no library choices, no implementation details in requirements.
- **Size thresholds trigger refactoring**: If a planned change causes any file to exceed **300 lines** (or 500 lines for well-structured modules), the plan **must include a refactoring step** as a first-level acceptance criteria. See [ANTIPATTERNS.md](./ANTIPATTERNS.md) for common patterns to avoid.
- **Avoid antipatterns**: Before finalizing any spec, check [ANTIPATTERNS.md](./ANTIPATTERNS.md) to ensure the plan doesn't introduce known code smells.
- The plan must be concrete. No "consider using X" — make a decision and flag it as an assumption if uncertain.
- Every task must be independently deployable or testable. If a task can't be verified on its own, split it.
- Acceptance criteria must be binary. "Works correctly" is not a criterion. "Returns 401 when unauthenticated" is.
- Never write a task that says "implement the feature." That's the whole spec. Tasks are the pieces.
- Align outputs with **PDCA-T** ([METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md)): **Plan** before code; **Do** in small tasks; **Check** against criteria and runs; **Act** via assumptions and ADR updates; **Test** as a first-class gate (strategy in PLAN, proof in TASK acceptance). Keep **traceability**: requirements / FRs → tasks → tests via the assumptions summary and explicit criteria.
- When project rules or skills exist, **cite them** in PLAN (patterns) and TASKS (constraints) so execution stays unambiguous.

---

## Example

**Input:**
`/spec-writer Add a way for users to export their order history as CSV`

**Output (abbreviated):**

### SPEC

**One-line purpose**
Users can download their complete order history as a CSV file from their account settings.

**Users and use cases**
- As a customer, I want to export my order history so that I can keep records for expense reporting.
- As a customer, I want to filter the export by date range so that I only download what I need. `[ASSUMPTION: date range filter is required — remove if out of scope]`

**Requirements**
1. Authenticated users can trigger a CSV export from their account
2. The export includes all orders `[ASSUMPTION: or filtered by date — clarify scope]`
3. The CSV downloads directly to the user's device
4. Large exports do not block the UI `[ASSUMPTION: async generation for exports over 1,000 rows]`

**Acceptance criteria**
```
Given an authenticated user on the account settings page
When they click "Export order history"
Then a CSV file downloads containing all their orders with columns: order_id, date, items, total, status

Given an authenticated user requesting an export
When the export contains more than 1,000 rows [ASSUMPTION]
Then the export is generated asynchronously and the user is notified by email when ready

Given an unauthenticated user
When they attempt to access the export endpoint directly
Then they receive a 401 response
```

### PLAN

**Stack and architecture**
`[ASSUMPTION: REST API with a relational database — adjust endpoint pattern to your framework]`

**API contracts**
- `GET /account/orders/export?from=YYYY-MM-DD&to=YYYY-MM-DD`
- Returns: CSV file stream or 202 Accepted with job ID for async
- Errors: 401 (unauthenticated), 400 (invalid date range), 500 (generation failure)

...

### TASKS

## Task 1: Export endpoint — synchronous path

**What to build:** A GET endpoint that accepts optional date range parameters, queries the authenticated user's orders, and streams a CSV response.
**Files likely affected:** `routes/account.js`, `services/orderExport.js` (create), `tests/orderExport.test.js` (create)
**Acceptance criteria:**
1. Returns CSV with correct headers and one row per order
2. Returns 401 if user is not authenticated
3. Returns 400 if date range is invalid
**Dependencies:** none

...

## Assumptions to review

1. Date range filter is required — Impact: MEDIUM
   Correct this if: the first version should export all orders with no filtering
2. Async generation for exports over 1,000 rows — Impact: HIGH
   Correct this if: your order volumes are low and synchronous is fine
3. REST API pattern — Impact: HIGH
   Correct this if: you're using GraphQL, tRPC, or another pattern