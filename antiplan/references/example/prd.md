# PRD: TaskBoard Threaded Comments with Reply Notifications

## Status: APPROVED
## Date: [project start date]
## Author: [developer] + antiplan skill
## Classification: Light → Standard (upgraded after notifier scope identified)

---

## 1. Problem Statement

Product managers using TaskBoard need to hold focused discussions on a single
task without the conversation degrading into a flat, chronological wall of
comments. The current implementation stores every comment as a sibling of
every other comment on the same task, so replies lose their context and
reviewers cannot tell what a reply is responding to. Users have begun
simulating threads by copy-pasting "> quoted text" into comment bodies, which
does not scale and cannot drive notifications. Reviewers also miss replies
directed at them because the notifier has no signal that distinguishes a
reply from a top-level comment.

## 2. Constitution

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | No new packages unless existing ones can't handle it | AP-9 prevention; every new package is a naming/integration risk |
| 2 | The internal event bus is the only transport between services | Avoid speculative architecture; the bus already works and is observable |
| 3 | TDD for all domain logic in `taskboard-core` | Domain bugs are invisible until integration; tests catch them early |
| 4 | Browser never holds worker or DB credentials | Security constraint — secrets stay server-side |
| 5 | One forward-looking PRD, not retrospective design docs | AP-2 prevention |

## 3. Users

| User | Role | Primary workflow | Pain without this system |
|------|------|-----------------|-------------------------|
| Product manager | Runs task reviews with stakeholders | Opens a task, reads comment history, replies to specific points, expects reviewers to see their replies | Replies lose context; reviewers miss direct responses; discussions fragment |
| Integration QA engineer | Validates the TaskBoard pipeline works e2e | Runs start-all script, posts threaded conversation, verifies reply notifications reach dispatchers | Manual curl against separate services; no threaded-conversation continuity testing |

## 4. Minimum Testable Product (MTP)

The smallest set of features that proves the design works end-to-end:

1. **Threaded comment display** — user posts reply N to comment M, UI shows N indented under M
2. **Reply notifications emitted** — a reply (comment with `parent_id`) emits a `comment.reply.posted` event that the notifier consumes

**MTP validation:** After T-1, T-2, T-3, integration gate IG-1 confirms:
- Given API + web running, when user posts a top-level comment then a reply
  referencing it, then the task detail page shows the reply indented under the parent
- Given API + worker + bus running, when a reply is posted, then the notifier
  consumes one `comment.reply.posted` event with the correct parent and author ids

## 5. Features

### 5.1 Threaded Comment Storage and Retrieval

**Priority:** P1
**User story:** As a product manager, I want comments to be stored with an
explicit parent link so replies can be rendered under the comments they
respond to.

**Acceptance criteria:**
- [ ] Given API running with DB, when I POST to `/v1/tasks/{id}/comments`
  with `{"body": "reply", "parent_id": 17}`, then the response comment has
  `parent_id == 17`, `thread_root_id == 17`, `depth == 1`
- [ ] Given the web task detail page, when I click "Reply" on comment 17 and
  submit, then the request body includes `parent_id: 17`
- [ ] Given `GET /v1/tasks/{id}/comment-thread`, then the response is a
  nested JSON tree rooted at top-level comments, with children under each parent
- [ ] Given a DB error mid-write, then a `type: error` JSON response is
  returned and the web UI shows a user-friendly error without losing the draft

**Out of scope:** Persistent draft storage across page reloads. Server-side
comment versioning. Multi-user typing indicators.

**Ticket(s):** T-1, T-2, T-3
**Gate:** IG-1

### 5.2 Reply Notifications via Event Bus

**Priority:** P1
**User story:** As a product manager, I want reviewers to be notified when
someone replies to their comment, so that directed feedback does not get lost.

**Acceptance criteria:**
- [ ] Given API + worker + bus running, when a reply with `parent_id` is
  created, then the notifier consumes exactly one `comment.reply.posted` event
  with `{parent_author_id, reply_author_id, task_id, comment_id}`
- [ ] Given a reply event, when the worker dispatches, then the email
  dispatcher receives a render payload containing the reply body excerpt
- [ ] Given a top-level comment (no `parent_id`), then no
  `comment.reply.posted` event is emitted (regression)

**Out of scope:** Dedicated notification service. Push notifications to
browsers. Digest scheduling (the event bus path is sufficient per
Constitution #2).

**Ticket(s):** T-4, T-5
**Gate:** IG-2

### 5.3 Shared Contracts for Thread DTOs

**Priority:** P1
**User story:** As an integration QA engineer, I want the TypeScript and
Python sides to share thread DTO definitions so the web client and the
notifier cannot drift out of shape.

**Acceptance criteria:**
- [ ] Given `packages/taskboard-contracts/schema.yaml` defines
  `CommentThreadNode` and `CommentReplyPosted`, when `make contracts`
  regenerates, then both `types.ts` and `models.py` include the new types
- [ ] Given `schema.yaml` changes, then `make contracts` exits non-zero
  unless generated files are committed (catches drift in CI)
- [ ] Given the DTO exceeds the depth limit, then the codegen truncates
  nested nodes without breaking the outer envelope

**Ticket(s):** T-4a (wired as part of assumption validation)
**Gate:** IG-2

### 5.4 Security & Guardrails

**Priority:** P1
**User story:** As a TaskBoard operator, I want all comment writes to pass
through auth and PII guardrails (bearer auth on API, PII redaction on event
payloads, permission gates on cross-task parents) so the system meets
organizational security standards.

**Acceptance criteria:**
- [ ] Given a comment body containing PII patterns (SSN, email), when the
  notifier builds the reply event payload, then the redaction pass scrubs
  them before publish
- [ ] Given a reply whose `parent_id` references a comment on a different
  task, then the API returns 400 and no write occurs (cross-task parent
  permission gate)
- [ ] Given a reply whose `parent_id` references a comment the caller is
  not authorized to view, then the permission gate blocks it with 403
- [ ] Given `POST /v1/tasks/{id}/comments` or
  `GET /v1/tasks/{id}/comment-thread` without a valid
  `Authorization: Bearer <token>` header, then the API returns 401
  (token validated via `TASKBOARD_API_BEARER_TOKEN` env var with HMAC check)
- [ ] Given a comment create path, when the request is dispatched, then
  `PermissionPolicy` from `config.permissions` YAML evaluates the caller
  before the DB write proceeds

**Out of scope:** Production-grade auth (OAuth, OIDC). Bearer token is a
shared-secret gate for demo scope, acknowledged as upgradeable.

**Ticket(s):** T-1 (guardrails wired in core), T-2 (bearer auth)
**Gate:** IG-1

### 5.5 Operational Tooling

**Priority:** P2
**User story:** As a developer running TaskBoard locally, I want a start-all
script, debug logging, and env documentation so I can get the stack running
without reading source code.

**Acceptance criteria:**
- [ ] Given `scripts/start-local-stack.sh`, when I run it, then all
  3 processes (API, notifier, Vite) start on correct ports
- [ ] Given `TASKBOARD_DEBUG_HTTP=1`, when a request flows through the API,
  then request/response bodies are logged to stderr
- [ ] Given `docs/local-dev.md`, when a new developer reads it, then they
  can start the stack and post a threaded comment within 10 minutes

**Ticket(s):** T-6, T-7
**Gate:** IG-3

## 6. Success Criteria

| ID | Criterion | Target | Measurement |
|----|-----------|--------|-------------|
| SC-001 | Thread retrieval latency | <200ms (p95) on 50-comment thread | Timed from GET to response on seeded task |
| SC-002 | Thread correctness | Reply renders under correct parent | Manual review of 3 multi-reply threads |
| SC-003 | New developer setup time | <10 min from clone to posted reply | Timed walkthrough of local-dev.md |

## 7. Architecture Decisions

| Decision | Options considered | Chosen | Justification |
|----------|-------------------|--------|---------------|
| Thread state | Client-side tree build vs server-side nested JSON | Server-side nested JSON | Constitution #1 — no new caching process. Server already does the join. Client stays presentational. |
| Event transport | Bus only vs bus + HTTP webhook to notifier vs direct DB poll | Bus only | Constitution #2. One path. HTTP webhook adds a port and a retry policy for no user-visible benefit. |
| Contract source of truth | Two separate schemas vs one YAML with codegen | One YAML with codegen | Drift-proof. Swap producers by editing one file. |
| Streaming transport | WebSocket vs SSE | SSE | Simpler. Unidirectional (server→client) is sufficient for thread updates. No connection upgrade needed. |
| API language | Python (FastAPI) vs TypeScript (Fastify) | Python (FastAPI) | Core domain is Python. Same language avoids a cross-process boundary. |

## 8. Component Map

| Component | Responsibility | Owner tickets | Existing path |
|-----------|---------------|---------------|---------------|
| Core domain | Comment CRUD, thread traversal helpers, event publish shims, permission policy evaluation | T-1 | `packages/taskboard-core/src/` |
| HTTP API | FastAPI HTTP facade: routes, CORS, SSE streaming, bearer auth, schema validation, thread endpoint | T-2 | `packages/taskboard-api/src/` |
| Notifier worker | Translates `comment.reply.posted` bus events into dispatcher calls. **Capability audit:** pre-existing worker handles generic task events but lacks reply-specific handler, PII redaction for reply bodies, and render payload shape — requires modification ticket | T-4 | `packages/taskboard-notifier/` |
| Web SPA | Task detail page with threaded comment tree, SSE streaming, markdown rendering, reply composer, security banner. **Modified by T-3** from `packages/taskboard-ui/` primitives | T-3 | `packages/taskboard-web/` + `packages/taskboard-ui/` (existing primitives) |
| Contracts | Pydantic + TS types generated from `schema.yaml` — all declarative | T-4a (schema extended + regenerated) | `packages/taskboard-contracts/` |

## 8b. Implementation Topology

**No new packages or directories are created.** All tickets modify existing
files within existing packages.

| Ticket | Action | Path | What changes |
|--------|--------|------|-------------|
| T-1 | MODIFY | `packages/taskboard-core/src/taskboard_core/comments.py` | Add `parent_id`, thread traversal helpers, event publish on reply |
| T-1 | MODIFY | `packages/taskboard-core/src/taskboard_core/models.py` | Add `parent_comment_id`, `thread_root_id`, `depth` columns + FK |
| T-1 | MODIFY | `packages/taskboard-core/tests/test_comments.py` | Add thread test cases |
| T-2 | MODIFY | `packages/taskboard-api/src/taskboard_api/routes_comments.py` | Accept `parent_id` on POST, add `GET /v1/tasks/{id}/comment-thread` |
| T-2 | MODIFY | `packages/taskboard-api/src/taskboard_api/auth.py` | Accept + enforce bearer token on thread endpoint |
| T-2 | MODIFY | `packages/taskboard-api/tests/test_routes_comments.py` | Add tests for threaded POST and thread retrieval |
| T-3 | MODIFY | `packages/taskboard-web/src/pages/TaskDetailPage.tsx` | Render threaded tree, send `parent_id` on reply |
| T-3 | MODIFY | `packages/taskboard-web/src/shared/apiClient.ts` | Add `getCommentThread` and extend `postComment` signature |
| T-4 | MODIFY | `packages/taskboard-notifier/src/taskboard_notifier/handlers.py` | Add `handle_comment_reply_posted` handler + PII redaction |
| T-4 | MODIFY | `packages/taskboard-notifier/src/taskboard_notifier/worker.py` | Register new event type in dispatch table |
| T-4a | MODIFY | `packages/taskboard-contracts/schema.yaml` | Add `CommentThreadNode` and `CommentReplyPosted` DTOs, regen |
| T-5 | MODIFY | `packages/taskboard-core/src/taskboard_core/events.py` | Add `comment.reply.posted` event constructor |
| T-5 | MODIFY | `packages/taskboard-api/src/taskboard_api/routes_sse.py` | Fan `comment.reply.posted` events to SSE subscribers |
| T-6 | MODIFY | `scripts/start-local-stack.sh` | Already exists — update ports/process list if needed |
| T-7 | MODIFY | `packages/taskboard-core/src/taskboard_core/debug_http.py` | Refine truncation, add comment-body digest |

## 9. API Contracts

### Web SPA → API

```
POST /v1/tasks/{task_id}/comments
Request: { body: string, parent_id?: integer }
  — When parent_id present, comment is a reply; thread_root_id is derived
    server-side to the ultimate root of the parent's chain.
  — When parent_id absent, comment is top-level (existing behavior).
Response: { id, body, author_id, task_id, parent_id?, thread_root_id?, depth, created_at }
Headers: Authorization: Bearer <required — validated against TASKBOARD_API_BEARER_TOKEN>
Errors: 400 (schema error | cross-task parent | permission block),
        401 (missing/invalid bearer token),
        403 (permission gate blocks viewing parent),
        502 (DB connection failure), 503 (DB timeout), 500 (unknown)
```

```
GET /v1/tasks/{task_id}/comment-thread   [NEW — added by T-2]
Request: none
Response: { nodes: CommentThreadNode[] }
  CommentThreadNode: { id, body, author_id, created_at, depth, children: CommentThreadNode[] }
Headers: Authorization: Bearer <required — validated against TASKBOARD_API_BEARER_TOKEN>
Errors: 401 (missing/invalid bearer token),
        502 (DB connection failure), 503 (DB timeout), 500 (unknown)
```

```
GET /v1/tasks/{task_id}/comments
Response: [ { id, body, author_id, created_at } ]
  — Flat list (existing). Unchanged.
```

```
GET /v1/sse/tasks/{task_id}   [EXISTING — extended by T-5]
Request: none
Response: SSE stream
  event: comment.posted
  data: { id, body, author_id, created_at }
  event: comment.reply.posted        [NEW — added by T-5]
  data: { comment_id, parent_comment_id, parent_author_id,
          reply_author_id, task_id, body_excerpt }
  event: done
Headers: Authorization: Bearer <required>
```

```
GET /health → { status: "ok" }
GET /v1/meta → { version: "x.y.z", build: "<sha>" }
```

### API → event bus

```
Topic: taskboard.events
Message: { type: "comment.reply.posted",
           payload: { comment_id, parent_comment_id, parent_author_id,
                      reply_author_id, task_id, body_excerpt } }
Headers: x-taskboard-event-version: 1
```

## 10. Explicitly Out of Scope

1. **New packages or directories** — Constitution #1; modify existing code
2. **Dedicated notification microservice** — cut (Deletion Test; Constitution #2)
3. **Composite event dispatcher** — cut (only needed if HTTP webhook exists)
4. **Persistent draft storage** — no user story; client holds state
5. **Typing indicators / presence** — AP-1 (no user asked for it)
6. **`resolve_thread` action** — deferred to post-MTP (P3)
7. **Production authentication** — demo scope only
8. **Multiple design documents** — Constitution #5

## 11. Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Event payload shape incompatible between producer + notifier | Medium | High | **Tracer bullet:** validate shape via contracts codegen before T-4 |
| Deep thread retrieval bloats response size | Medium | Medium | Server-side depth cap; test in IG-1 |
| Notifier dispatcher latency adds >2s to reply feedback | Low | Medium | Monitor in IG-2; optimize bus consumer batching if needed |

## 12. Ticket Dependency Graph

```
T-1: Core: add parent_id + thread helpers to comments.py [confirm]
     [origin: phase-2, P1, MODIFY packages/taskboard-core/]
  └─→ T-2: API: accept parent_id + add /comment-thread + bearer auth [confirm]
       [origin: phase-2, P1, MODIFY packages/taskboard-api/]
       └─→ T-3: Web: render threaded tree + send parent_id on reply [confirm]
            [origin: phase-1, P1, MODIFY packages/taskboard-web/]
            └─→ IG-1: Threaded comment display works e2e
                 [Proof: curl threaded POST → GET thread returns nested tree]
                 [Proof: Playwright reply-under-comment test]
                 └─→ T-4: Notifier: handle comment.reply.posted [confirm]
                      [origin: phase-2, P1, MODIFY packages/taskboard-notifier/]
                      └─→ T-4a: Contracts: add thread + reply DTOs, regenerate [confirm]
                           [origin: phase-2, P1, MODIFY packages/taskboard-contracts/]
                           └─→ T-5: SSE: fan comment.reply.posted to subscribers [validate]
                           [origin: phase-1, P1, MODIFY packages/taskboard-core/ + packages/taskboard-api/]
                           └─→ IG-2: Reply notifications + SSE work e2e
                                [Proof: reply → notifier consumes event; SSE subscriber receives]
                                └─→ T-6: Start-all script + local dev docs [autopilot]
                                     [origin: phase-1, P2, MODIFY scripts/ + docs/]
                                └─→ T-7: Debug logging (HTTP trace, body redaction) [autopilot]
                                     [origin: phase-1, P2, MODIFY packages/taskboard-core/]
                                     └─→ IG-3: Full system validation
```

**DAG Readiness Gate:** READY
- All tickets trace to Phase 1 features ✓
- No Inferred assumptions unaccepted ✓
- Integration gate every ≤3 feature tickets ✓
- Total: 8 feature + 3 gate = 11 tickets ≤ scope limit ✓
- No `[NEEDS CLARIFICATION]` markers ✓
- No P3 features in DAG ✓
- Every ticket specifies MODIFY + file path ✓
- Zero new packages (AP-9 check; all tickets MODIFY existing packages) ✓
- Every ticket has execution mode assigned ✓

## 13. Convergence Ledger (Final)

- Resolved: 13 — product scope, users (2), MTP, thread state model (server-side tree),
  streaming transport (SSE), contract source (codegen from YAML), API language (Python),
  event transport (bus only), permission source (YAML policy), security model
  (guardrails + shared secrets), deployment model (3 processes), thread depth
  modeling (parent_comment_id + thread_root_id + depth)
- Cut: 8 — notification microservice, composite dispatcher, template scaffolding,
  presence, `resolve_thread`, multiple design docs, persistent storage, production auth
- Deferred: 1 — `resolve_thread` action (P3, post-MTP)

## 14. Assumption Register

| ID | Statement | Source | Confidence | Impact if wrong | Validation | Blocking? |
|----|-----------|--------|------------|----------------|------------|-----------|
| A-1 | Event bus delivers messages in at-least-once semantics with deduplication | Inferred → User-stated | HIGH | Duplicate notifications | Tracer bullet | Yes (resolved) |
| A-2 | Notifier worker correctly subscribes to new event types via existing dispatch table | Observed | HIGH | Events dropped | IG-2 | No |
| A-3 | `packages/taskboard-ui/` CommentList primitive is sufficient to render an indented tree | Observed | HIGH | Web page requires more UI work than planned | Code inspection of ui components | No |
| A-4 | Agent YAML config sufficient for permission policy tuning | Observed | HIGH | Custom permission code needed | IG-1 | No |
| A-5 | Adding `parent_comment_id` FK does not break existing flat-list query performance | Inferred → User-stated | HIGH | Index/query refactor needed | T-1 tests | Yes (resolved) |

## 15. Artifact Ingestion Log

*No reference artifacts were provided for this project.*

## 16. Complexity Justification Register

| Violation | Why needed | Simpler alternative rejected because |
|-----------|-----------|--------------------------------------|
| 3 separate processes (API + notifier + Vite) | Notifier needs dispatcher credentials that must not reach the browser | Single process would expose credentials (violates Constitution #4) |
| YAML schema loaded at codegen time for contracts | TypeScript and Python must agree on DTO shape without manual sync | Hardcoded dual definitions rejected — they drift from each other |

## 17. Implementation Readiness Checklist

- [x] Every ticket specifies MODIFY or CREATE for each file it touches
- [x] No ticket creates a new package (AP-9 verified)
- [x] Event payloads reference verified schema field names
- [x] API contracts show what changed vs pre-existing state
- [x] Plan lists existing tests that must still pass
- [x] Plan names test runner (pytest, vitest), framework conventions, import patterns
- [x] Existing behaviors that must NOT break are enumerated
- [x] Every ticket maps to at least one PRD §5 acceptance criterion
- [x] Integration gates named for what they validate, not what they are
- [x] Assumption Register has zero Inferred-unaccepted blocking entries
