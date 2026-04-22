# Ticket Pack: TaskBoard Threaded Comments with Reply Notifications

**This file is spec-writer's output**, derived from [ticket-dag.md](ticket-dag.md)
and [prd.md](prd.md). It demonstrates Ticket Contract (ticket-dag.md §3)
compliance and serves as the quality bar for `ticket-critic` before any
ticket transitions to `Stage: BUILD`.

All tickets modify existing packages. See
[brownfield-context.md](brownfield-context.md) for the pre-existing codebase
state and [prd.md](prd.md) §8b for the implementation topology.

---

---
id: T-1
title: "Core: Add parent_id + Thread Helpers to comments.py"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-2
Mode: confirm
Depends-On: []
Blocks: [T-2]
Gate: IG-1
Files:
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/comments.py
    test: false
    description: "Accept optional parent_id, derive thread_root_id + depth, publish reply event"
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/models.py
    test: false
    description: "Add parent_comment_id FK, thread_root_id, depth columns; add index"
  - action: MODIFY
    path: packages/taskboard-core/tests/test_comments.py
    test: true
    description: "New test cases for parent_id, thread_root_id, depth, publish-on-reply"
  - action: MODIFY
    path: packages/taskboard-core/tests/support/db_fixtures.py
    test: true
    description: "Extend fixtures to construct threaded comment histories"
Read-First:
  - packages/taskboard-core/src/taskboard_core/comments.py
  - packages/taskboard-core/tests/test_comments.py
  - packages/taskboard-core/src/taskboard_core/models.py
Exemplar-Files:
  - packages/taskboard-core/src/taskboard_core/comments.py
  - packages/taskboard-core/tests/support/db_fixtures.py
Assumptions-Validated: [A-5]
Regression-Baseline:
  - "uv run pytest packages/taskboard-core/tests/ -v"
---
# T-1: Core — Add parent_id + Thread Helpers to comments.py

## Scope
MODIFY `packages/taskboard-core/src/taskboard_core/comments.py` — extend
`create_comment()` with optional `parent_id: int | None = None`. When
provided, validate the parent exists and belongs to the same `task_id`,
derive `thread_root_id` (parent's `thread_root_id` or parent's `id` if
parent is itself a root), set `depth = parent.depth + 1`, persist. Add
`get_comment_thread(task_id)` returning a nested list of root nodes.
MODIFY `models.py` to add `parent_comment_id` FK, `thread_root_id`, and
`depth` columns with appropriate indexes on `(task_id, thread_root_id)`.

## User Story
As a product manager, I want the core library to accept a parent reference
on comment creation so replies can be stored and retrieved as a tree
without the API layer reconstructing the hierarchy on every read.

## Acceptance Criteria
- [ ] Given `create_comment(task_id=42, author_id=7, body="reply", parent_id=17)`
  with comment 17 on task 42 and `parent.depth == 0`, when called, then the
  returned comment has `parent_comment_id == 17`, `thread_root_id == 17`,
  `depth == 1` (grep: `rg "parent_comment_id == 17" packages/taskboard-core/tests/test_comments.py`)
- [ ] Given `create_comment(..., parent_id=99)` where comment 99 is on a
  different `task_id`, when called, then `CrossTaskParentError` is raised and
  no DB row is written (grep: `rg "CrossTaskParentError" packages/taskboard-core/tests/test_comments.py`)
- [ ] Given `get_comment_thread(task_id=42)` after two reply levels, then the
  returned structure is `[{..., "children": [{..., "children": [...]}]}]`
  with `children` fully populated recursively (failure-path: assert a
  dangling orphan comment is surfaced to the caller, not silently dropped)
- [ ] Given `create_comment(...)` without `parent_id`, then behavior is
  identical to pre-existing single-level comment (regression; parent
  columns are NULL, depth is 0, no thread event published)
- [ ] Given a reply create path, when the DB commit succeeds, then
  `events.publish_task_event(task_id, "comment.reply.posted", payload)`
  is called exactly once with `payload` containing `parent_author_id`,
  `reply_author_id`, `body_excerpt` (grep: `pytest -k publish_reply_event`)
- [ ] Given a reply whose parent has `depth >= THREAD_MAX_DEPTH`, when
  called, then `ThreadTooDeepError` is raised and no row is written

## Verify

```bash
uv run pytest packages/taskboard-core/tests/test_comments.py -k "threaded or parent_id or thread_root" -v
```

## Technical Notes
- `parent_id` is an int matching the PK of an existing `Comment`; validate
  via `session.get(Comment, parent_id)` — do NOT use ORM relationship
  autoloading (it issues separate queries per create).
- `thread_root_id` persistence follows the "materialized root" pattern —
  we store root id directly rather than deriving on every read.
- `depth` is capped at `THREAD_MAX_DEPTH = 6` (config-driven via `settings`).
- The reply-published event uses `events.publish_task_event`; the event
  type string MUST match the literal `"comment.reply.posted"` consumed by
  T-4 (`packages/taskboard-notifier/src/taskboard_notifier/handlers.py`).
- `body_excerpt` is the first 140 chars of the comment body, PII-scrubbed
  via existing `taskboard_core.log_redaction.scrub_body()`.
- ORM migration is NOT added here — the repo uses Alembic with a separate
  migration ticket convention; migration is assumed out-of-band for this
  example. Document the expected migration in Technical Notes for T-1
  review.

## Failure Protocol
- Max retries: 2. After 2 failed attempts, revert and exit; escalate to
  Phase 2 architecture review (likely AP-12: scope too large for one ticket).
- If `events.publish_task_event` signature conflict is discovered,
  re-interrogate assumption A-5 before proceeding.

---

---
id: T-2
title: "API: Accept parent_id + Add /comment-thread Endpoint + Bearer Auth"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-2
Mode: confirm
Depends-On: [T-1]
Blocks: [T-3]
Gate: IG-1
Files:
  - action: MODIFY
    path: packages/taskboard-api/src/taskboard_api/routes_comments.py
    test: false
    description: "Accept optional parent_id on POST; add GET /comment-thread"
  - action: MODIFY
    path: packages/taskboard-api/src/taskboard_api/auth.py
    test: false
    description: "Enforce bearer token on comment write + thread read"
  - action: MODIFY
    path: packages/taskboard-api/tests/test_routes_comments.py
    test: true
    description: "Tests for parent_id, thread endpoint, auth, permission"
  - action: MODIFY
    path: packages/taskboard-api/tests/support/http_client.py
    test: true
    description: "Extend fixture to send bearer tokens"
Read-First:
  - packages/taskboard-api/src/taskboard_api/routes_comments.py
  - packages/taskboard-api/src/taskboard_api/auth.py
  - packages/taskboard-api/tests/test_routes_comments.py
Exemplar-Files:
  - packages/taskboard-api/src/taskboard_api/routes_comments.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-api/tests/test_routes_comments.py -v"
---
# T-2: API — Accept parent_id + Add /comment-thread + Bearer Auth

## Scope
MODIFY `packages/taskboard-api/src/taskboard_api/routes_comments.py` — extend
`POST /v1/tasks/{task_id}/comments` to accept optional `parent_id` in the
request schema; add `GET /v1/tasks/{task_id}/comment-thread` returning the
nested JSON produced by `taskboard_core.comments.get_comment_thread()`.
MODIFY `auth.py` to enforce `TASKBOARD_API_BEARER_TOKEN` HMAC validation
on both endpoints.

## User Story
As a product manager, I want the API to expose a thread-shaped response so
the web client can render the hierarchy without making N requests.

## Acceptance Criteria
- [ ] Given a valid bearer token and `{"body": "reply", "parent_id": 17}`,
  when I `POST /v1/tasks/42/comments`, then 201 is returned with body
  `{id, body, parent_id: 17, thread_root_id: 17, depth: 1, created_at}`
  (grep: `pytest -k test_post_comment_with_parent_id`)
- [ ] Given no `Authorization: Bearer` header, when I
  `POST /v1/tasks/42/comments`, then 401 is returned and no DB row is
  created (failure-path: user-visible 401 JSON error body with
  `{"error": "missing_bearer_token"}`)
- [ ] Given a bearer token that fails HMAC comparison, when I call either
  endpoint, then 401 is returned with `{"error": "invalid_bearer_token"}`
- [ ] Given `parent_id` pointing to a comment on a different task, when I
  POST, then 400 is returned with `{"error": "cross_task_parent"}` and
  no DB row is created (grep: `pytest -k cross_task_parent`)
- [ ] Given an existing thread with 3 reply levels, when I
  `GET /v1/tasks/42/comment-thread`, then response.body matches the
  nested shape specified in [prd.md](prd.md) §9
  (`{nodes: [{id, body, author_id, created_at, depth, children: [...]}]}`)
- [ ] Given `POST /v1/tasks/{id}/comments` without `parent_id` (legacy
  clients), then behavior matches pre-existing single-comment path
  (regression)
- [ ] Given the DB raises `OperationalError`, then API returns 502 with
  `{"error": "db_unavailable"}` and no partial write occurs
- [ ] Given a caller whose `PermissionPolicy` forbids reading the parent
  comment, when POST reply, then 403 is returned (permission gate)

## Verify

```bash
uv run pytest packages/taskboard-api/tests/test_routes_comments.py -k "thread or parent_id or bearer" -v
```

## Technical Notes
- Schema validation uses Pydantic v2 `CommentCreate` model; add
  `parent_id: int | None = None` with `Field(ge=1)` validator.
- The thread endpoint calls `get_comment_thread(task_id)` directly from
  the imported core module; do NOT reimplement the nesting in the API
  layer — that would duplicate logic and risk drift.
- Bearer auth: reuse `taskboard_api.auth.verify_bearer_token(request)`
  (already exists for task routes). The function raises `HTTPException(401)`.
- `PermissionPolicy` is loaded at app startup from `config.permissions`
  YAML; do not hardcode policy in the route.
- Error mapping: `CrossTaskParentError` → 400, `ThreadTooDeepError` → 400,
  `PermissionDeniedError` → 403, `OperationalError` → 502, unknown → 500.

## Failure Protocol
- Max retries: 2. After 2 failed attempts at the bearer auth path, revert
  and exit; escalate to a security review (bearer HMAC is load-bearing).
- If `get_comment_thread` signature or return shape drifts from T-1,
  block on re-interrogation of T-1 acceptance criteria before retrying.

---

---
id: T-3
title: "Web: Render Threaded Tree + Send parent_id on Reply"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-1
Mode: confirm
Depends-On: [T-2]
Blocks: [IG-1]
Gate: IG-1
Files:
  - action: MODIFY
    path: packages/taskboard-web/src/pages/TaskDetailPage.tsx
    test: false
    description: "Replace flat CommentList with threaded renderer; wire reply composer"
  - action: MODIFY
    path: packages/taskboard-web/src/shared/apiClient.ts
    test: false
    description: "Add getCommentThread; extend postComment signature with parent_id"
  - action: MODIFY
    path: packages/taskboard-web/src/shared/apiClient.test.ts
    test: true
    description: "Client tests for new methods"
  - action: MODIFY
    path: packages/taskboard-web/e2e/threaded-comments.spec.ts
    test: true
    description: "Playwright test for reply-under-parent"
Read-First:
  - packages/taskboard-ui/src/components/CommentList.tsx
  - packages/taskboard-ui/src/index.ts
  - packages/taskboard-web/src/pages/TaskDetailPage.tsx
Exemplar-Files:
  - packages/taskboard-ui/showcase/pages/
Assumptions-Validated: [A-3]
Regression-Baseline:
  - "npm --prefix packages/taskboard-web run test"
---
# T-3: Web — Render Threaded Tree + Send parent_id on Reply

## Scope
MODIFY `packages/taskboard-web/src/pages/TaskDetailPage.tsx` to call
`GET /v1/tasks/{id}/comment-thread` and render each node indented by
`depth` CSS step; add a "Reply" button on each comment that opens a
composer and sends `parent_id` on submit. MODIFY `apiClient.ts` to
expose `getCommentThread(taskId)` and extend `postComment` with an
optional `parentId` argument.

## User Story
As a product manager, I want the task detail page to show replies nested
under their parents so the conversation context is obvious at a glance.

## Acceptance Criteria
- [ ] Given the task detail page with an existing thread, when it mounts,
  then `getCommentThread(taskId)` is called once and the rendered tree
  matches the server's `depth` values (Playwright:
  `e2e/threaded-comments.spec.ts::renders_nested_tree`)
- [ ] Given the user clicks "Reply" on comment 17, when they submit, then
  the network request body contains `parent_id: 17`
  (Playwright: `renders_nested_tree::submits_parent_id`)
- [ ] Given the API returns 401, when the page mounts, then the user sees
  a "Please sign in" banner — not a silent empty list (failure-path:
  user-visible banner text `"Please sign in"` asserted)
- [ ] Given legacy flat-list code paths on task list page, then they
  continue to function (regression)

## Verify

```bash
npm --prefix packages/taskboard-web run test -- --run apiClient && \
  npm --prefix packages/taskboard-web run e2e -- threaded-comments.spec.ts
```

## Technical Notes
- Use `packages/taskboard-ui/` `CommentList` primitive as the inner
  renderer; extend with `indentDepth` prop. Do NOT fork the primitive.
- Thread depth → indent CSS uses `calc(var(--depth) * 1.5rem)`; cap
  indent at `THREAD_MAX_DEPTH * 1.5rem` (shared constant in contracts).
- `getCommentThread` reuses the existing `apiClient` fetch wrapper;
  it MUST propagate `signal` for abort support.

## Failure Protocol
- Max retries: 2. If the UI cannot render the tree correctly on retry,
  revert and exit; escalate to a UI design review.

---

---
id: IG-1
title: "Integration Gate: Threaded Comment Display Works E2E"
Stage: NEW
Type: integration-gate
Depends-On: [T-1, T-2, T-3]
Blocks: [T-4, T-5]
Validates: [T-1, T-2, T-3]
Expected-Test-Artifacts:
  - path: packages/taskboard-api/tests/test_routes_comments.py
    min_tests: 8
    scope: "POST with parent_id, GET thread, cross-task 400, bearer 401, permission 403, flat regression, DB 502, nested shape"
  - path: packages/taskboard-core/tests/test_comments.py
    min_tests: 6
    scope: "create with parent, derive thread_root_id, depth increment, flat regression, publish event, depth cap"
---
# IG-1: Threaded Comment Display Works End-to-End

## Flows Under Test
- Given API + DB + web SPA running, when the user posts a top-level
  comment and then a reply referencing it, then the page shows the
  reply indented under the parent on reload.
- Given a cross-task `parent_id`, then the API rejects with 400 and the
  UI shows a user-visible error, not a silent failure.

## Proof Artifacts (required)
- [ ] curl transcript: `POST /v1/tasks/42/comments` with `parent_id`, then
  `GET /v1/tasks/42/comment-thread` showing nested response
- [ ] Playwright run: threaded reply visible on reload
  (trace URL recorded in Dev Agent Record)
- [ ] CI run URL with green pytest + vitest + Playwright stages

## Silent Failure Detection
- Thread endpoint returns `200 {nodes: []}` for a task with no comments
  (not `404`) — required so the web UI can distinguish "no comments" from
  "task missing"; IG-1 asserts this by creating a task with zero comments
  and hitting the endpoint.
- On DB unavailability, API returns 502 within 2s, not a hung connection.

## Dev Agent Record
- Verifier session id: `<captured at run time>`
- Model used: `<captured at run time>`
- Convention-drift check: run `scripts/lint-conventions.sh` against the
  three changed packages; zero drift warnings required.

## Failure Protocol
- Max retries: 2. After 2 consecutive failed gate runs, revert T-1/T-2/T-3
  and re-enter Phase 2 interrogation for the thread-shape decision.

## Verified by
CI job or human reviewer (not the implementing agent)

---

---
id: T-4
title: "Notifier: Handle comment.reply.posted"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-2
Mode: confirm
Depends-On: [IG-1]
Blocks: [T-4a]
Gate: IG-2
Files:
  - action: MODIFY
    path: packages/taskboard-notifier/src/taskboard_notifier/handlers.py
    test: false
    description: "Register handle_comment_reply_posted handler with PII redaction"
  - action: MODIFY
    path: packages/taskboard-notifier/src/taskboard_notifier/worker.py
    test: false
    description: "Add comment.reply.posted → handler mapping in dispatch table"
  - action: MODIFY
    path: packages/taskboard-notifier/tests/test_handlers.py
    test: true
    description: "Handler unit tests incl. PII redaction"
Read-First:
  - packages/taskboard-notifier/src/taskboard_notifier/worker.py
  - packages/taskboard-notifier/src/taskboard_notifier/handlers.py
  - packages/taskboard-notifier/tests/test_handlers.py
Exemplar-Files:
  - packages/taskboard-notifier/src/taskboard_notifier/handlers.py
  - packages/taskboard-notifier/src/taskboard_notifier/dispatchers/email.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-notifier/tests/ -v"
---
# T-4: Notifier — Handle comment.reply.posted

## Scope
MODIFY `packages/taskboard-notifier/src/taskboard_notifier/handlers.py` to
add `handle_comment_reply_posted(event)` that PII-redacts
`event.payload.body_excerpt`, looks up `parent_author_id` recipient,
and invokes the email dispatcher. Register the handler in `worker.py`'s
dispatch table under the `comment.reply.posted` event type.

## User Story
As a product manager, I want the notifier to deliver a scrubbed excerpt
of the reply to the parent author so that directed feedback reaches the
intended recipient without leaking PII from the original comment body.

## Acceptance Criteria
- [ ] Given a bus message with `type: "comment.reply.posted"` and payload
  `{parent_author_id: 9, reply_author_id: 7, task_id: 42, comment_id: 99,
  body_excerpt: "..."}`, when the worker dispatches, then the email
  dispatcher is called exactly once with recipient `9`
  (grep: `pytest -k handle_comment_reply_posted`)
- [ ] Given the body excerpt contains PII patterns (SSN-like digits,
  email addresses), when the handler processes, then the dispatched
  payload has those patterns replaced with `[redacted]`
- [ ] Given a `comment.posted` event (top-level, no reply), then the
  new handler is NOT invoked (regression — existing handler path intact)
- [ ] Given dispatcher raises `DispatcherError`, then the handler
  re-raises so the worker's at-least-once retry semantics engage
  (failure-path: user-visible outcome is that retries happen, asserted
  via dispatcher call count ≥ 2 with retry-counter metric)

## Verify

```bash
uv run pytest packages/taskboard-notifier/tests/test_handlers.py -k "reply_posted or redact" -v
```

## Technical Notes
- Handler signature matches the existing pattern in `handlers.py`:
  `def handle_<event_type>(event: Event, dispatchers: Dispatchers) -> None`.
- Reuse `taskboard_core.log_redaction.scrub_body()` for PII redaction;
  do NOT write a second redactor.
- Dispatch table in `worker.py` is a module-level `HANDLERS: dict[str, Handler]`;
  add the new entry next to existing entries, alphabetized.

## Failure Protocol
- Max retries: 2. If event shape mismatches contracts package, block on T-4a
  (that is specifically the assumption-validation ticket for shape).

---

---
id: T-4a
title: "Contracts: Add Thread + Reply DTOs, Regenerate"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-2
Mode: confirm
Depends-On: [T-4]
Blocks: [T-5]
Gate: IG-2
Files:
  - action: MODIFY
    path: packages/taskboard-contracts/schema.yaml
    test: false
    description: "Add CommentThreadNode and CommentReplyPosted DTOs"
  - action: MODIFY
    path: packages/taskboard-contracts/build.py
    test: false
    description: "Ensure codegen emits TS + Python for new DTOs"
  - action: MODIFY
    path: packages/taskboard-contracts/tests/test_generated.py
    test: true
    description: "Assertions on generated DTO shape"
  - action: MODIFY
    path: packages/taskboard-contracts/Makefile
    test: false
    description: "CI drift check target"
Read-First:
  - packages/taskboard-contracts/schema.yaml
  - packages/taskboard-contracts/build.py
  - packages/taskboard-contracts/Makefile
Exemplar-Files:
  - packages/taskboard-contracts/schema.yaml
  - packages/taskboard-contracts/build.py
Assumptions-Validated: [A-1]
Regression-Baseline:
  - "uv run pytest packages/taskboard-contracts/tests/ -v && make -C packages/taskboard-contracts contracts-check"
---
# T-4a: Contracts — Add Thread + Reply DTOs, Regenerate

## Scope
MODIFY `packages/taskboard-contracts/schema.yaml` to add `CommentThreadNode`
(id, body, author_id, created_at, depth, children[]) and
`CommentReplyPosted` (comment_id, parent_comment_id, parent_author_id,
reply_author_id, task_id, body_excerpt). Regenerate `types.ts` and
`models.py` via `make contracts`. Add `contracts-check` Makefile target
that exits non-zero if regeneration produces a diff (CI drift gate).

## User Story
As an integration QA engineer, I want the thread + reply DTOs generated
from a single source of truth so that the web client, the API, the
notifier, and the event bus cannot drift out of shape silently.

## Acceptance Criteria
- [ ] Given `make contracts`, when run, then `types.ts` and `models.py`
  include `CommentThreadNode` and `CommentReplyPosted` with matching field
  names (grep: `rg "CommentThreadNode" packages/taskboard-contracts/types.ts packages/taskboard-contracts/models.py`)
- [ ] Given `schema.yaml` edited but generated files not committed, when
  `make contracts-check` runs in CI, then exit code is non-zero and
  stderr includes `drift detected` (failure-path: drift blocks merge)
- [ ] Given the depth field exceeds `THREAD_MAX_DEPTH` at generation,
  then codegen truncates nested `children[]` nodes without breaking the
  outer envelope **[Validates A-1]**
- [ ] Given existing DTOs, then they remain generated unchanged (regression)

## Verify

```bash
uv run pytest packages/taskboard-contracts/tests/ -v && \
  make -C packages/taskboard-contracts contracts-check
```

## Technical Notes
- `schema.yaml` uses the existing `types:` top-level collection; append
  the two new types rather than restructuring.
- Codegen uses `datamodel-code-generator` for Python and a small
  in-repo TS generator (`build.py`); do NOT introduce a new codegen tool.
- `THREAD_MAX_DEPTH` is sourced from `schema.yaml` `constants:` block —
  single source of truth for core, API, web, notifier, contracts.

## Failure Protocol
- Max retries: 2. If codegen produces incompatible Python + TS shapes
  (e.g., field name casing drift), revert and interrogate A-1 before retrying.

---

---
id: T-5
title: "SSE: Fan comment.reply.posted to Subscribers"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-1
Mode: validate
Depends-On: [T-4a]
Blocks: [IG-2]
Gate: IG-2
Files:
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/events.py
    test: false
    description: "Add build_comment_reply_posted event constructor"
  - action: MODIFY
    path: packages/taskboard-api/src/taskboard_api/routes_sse.py
    test: false
    description: "Fan comment.reply.posted events to subscribers of /v1/sse/tasks/{id}"
  - action: MODIFY
    path: packages/taskboard-api/tests/test_routes_sse.py
    test: true
    description: "SSE subscriber tests for reply events"
  - action: MODIFY
    path: packages/taskboard-api/tests/support/sse_client.py
    test: true
    description: "Extend fixture to assert event types"
Read-First:
  - packages/taskboard-core/src/taskboard_core/events.py
  - packages/taskboard-api/src/taskboard_api/routes_sse.py
Exemplar-Files:
  - packages/taskboard-api/src/taskboard_api/routes_sse.py
Assumptions-Validated: [A-1]
Regression-Baseline:
  - "uv run pytest packages/taskboard-api/tests/test_routes_sse.py -v"
---
# T-5: SSE — Fan comment.reply.posted to Subscribers

## Scope
MODIFY `packages/taskboard-core/src/taskboard_core/events.py` to add
`build_comment_reply_posted(payload)` constructor conforming to the
`CommentReplyPosted` DTO from T-4a. MODIFY `routes_sse.py` to subscribe
to the bus for `comment.reply.posted` on `/v1/sse/tasks/{id}` and fan
matching events (same `task_id`) to connected SSE subscribers.

## User Story
As a product manager, I want the task detail page to receive reply
notifications without a page refresh so that live discussions feel
responsive instead of requiring manual reload.

## Acceptance Criteria
- [ ] Given a subscriber connected to `/v1/sse/tasks/42`, when a reply is
  posted to task 42, then the subscriber receives
  `event: comment.reply.posted\ndata: {...}` within 500ms
  (grep: `pytest -k sse_receives_reply_event`)
- [ ] Given a reply is posted to a different task, then no event is
  delivered to `/v1/sse/tasks/42`'s subscribers (regression / isolation)
- [ ] Given a top-level comment is posted, then no `comment.reply.posted`
  event is emitted over SSE
- [ ] **[Validates A-1]** Given two subscribers and one reply event, then
  both subscribers receive the event (at-least-once, deduplication safe)
- [ ] Given a subscriber disconnects mid-stream, then the server-side
  subscription is cleaned up and does not leak (failure-path: asserted
  via subscriber-count metric returning to baseline within 5s)

## Verify

```bash
uv run pytest packages/taskboard-api/tests/test_routes_sse.py -k "reply_event" -v && \
  uv run pytest packages/taskboard-core/tests/test_events.py -k "comment_reply" -v
```

## Technical Notes
- SSE framing uses native FastAPI `StreamingResponse` with manual
  `event: <type>\ndata: <json>\n\n` framing — Constitution #1 forbids
  new transport dependencies.
- Bus subscription uses `taskboard_eventbus.subscribe(topic, filter=...)`;
  filter closure MUST include `task_id == subscription.task_id` to avoid
  cross-task leakage.
- Event constructor output MUST serialize identically to
  `CommentReplyPosted` from T-4a; assert with a shared fixture.

## Failure Protocol
- Max retries: 2. If SSE framing/event-type drift is observed between
  fan-out and subscriber, block on A-1 re-validation before retrying.

---

---
id: IG-2
title: "Integration Gate: Reply Notifications + SSE Work E2E"
Stage: NEW
Type: integration-gate
Depends-On: [T-4, T-4a, T-5]
Blocks: [T-6, T-7]
Validates: [T-4, T-4a, T-5]
Expected-Test-Artifacts:
  - path: packages/taskboard-notifier/tests/test_handlers.py
    min_tests: 4
    scope: "handler dispatched, redaction applied, non-reply skipped, retry on dispatcher error"
  - path: packages/taskboard-api/tests/test_routes_sse.py
    min_tests: 4
    scope: "sse receives reply event, cross-task isolation, top-level not fanned, subscriber cleanup"
---
# IG-2: Reply Notifications + SSE Work End-to-End

## Flows Under Test
- Given all 3 processes running, when the user posts a reply to a comment,
  then the notifier consumes the bus event and dispatches to email
  within 2s; an SSE subscriber on the same task receives the event.
- Given PII in the reply body, then the dispatched payload is redacted.

## Proof Artifacts (required)
- [ ] curl transcript: `POST /v1/tasks/42/comments` with `parent_id`,
  then `curl -N /v1/sse/tasks/42` showing `event: comment.reply.posted`
- [ ] Notifier log line showing dispatcher invoked with redacted excerpt
- [ ] CI run URL with green pytest stages across core + api + notifier

## Silent Failure Detection
- If bus delivery is dropped, the IG-2 run hangs waiting for SSE event —
  treat timeout >10s as failure, not success.
- If PII redaction silently regresses, assert dispatcher payload against
  a fixture with known PII patterns; raw patterns present = failure.

## Dev Agent Record
- Verifier session id: `<captured at run time>`
- Model used: `<captured at run time>`
- Convention-drift check: run `scripts/lint-conventions.sh` on notifier +
  api + core; zero drift required.

## Failure Protocol
- Max retries: 2. After 2 failed gate runs, revert T-4/T-4a/T-5 and
  re-interrogate A-1 assumption about bus delivery semantics.

---

---
id: T-6
title: "Start-All Script + Local Dev Runbook"
Stage: NEW
Type: feature
Priority: P2
Origin: phase-1
Mode: autopilot
Depends-On: [IG-2]
Blocks: [IG-3]
Gate: IG-3
Files:
  - action: MODIFY
    path: scripts/start-local-stack.sh
    test: false
    description: "Ensure API + notifier + web processes all started with correct env"
  - action: MODIFY
    path: docs/local-dev.md
    test: false
    description: "Add threaded-reply walk-through"
  - action: MODIFY
    path: docs/secrets-and-env.md
    test: false
    description: "Document TASKBOARD_API_BEARER_TOKEN and bus env vars"
Read-First:
  - scripts/start-local-stack.sh
  - docs/local-dev.md
  - docs/secrets-and-env.md
Exemplar-Files:
  - scripts/start-local-stack.sh
Assumptions-Validated: []
Regression-Baseline: []
---
# T-6: Start-All Script + Local Dev Runbook

## Scope
MODIFY `scripts/start-local-stack.sh` and `docs/local-dev.md` so a new
developer can clone the repo, run one command, and post a threaded reply
within 10 minutes.

## User Story
As an integration QA engineer, I want a single command to bring up the
full local stack so that manual threaded-reply validation does not
require memorizing process orchestration details.

## Acceptance Criteria
- [ ] Given `.env` with `TASKBOARD_API_BEARER_TOKEN`, when I run
  `bash scripts/start-local-stack.sh`, then API, notifier, and Vite
  dev server are up on their declared ports within 20s
  (`curl -sf http://localhost:8000/health`, notifier log shows
  "subscribed to taskboard.events", Vite prints "Local: http://...")
- [ ] Given `docs/local-dev.md`, when a new developer reads it, then
  they can post a threaded reply end-to-end in under 10 minutes
  (failure-path: step-by-step walkthrough is verified by running a
  fresh-clone timing test once per release)
- [ ] Given Ctrl+C on the script, then all child processes are cleaned
  up (no orphaned uvicorn, vite, or worker procs; assert with
  `pgrep -f taskboard-` post-kill returning empty)

## Verify

```bash
bash scripts/start-local-stack.sh &
sleep 20 && curl -sf http://localhost:8000/health | jq -e '.status == "ok"' && \
  kill %1 2>/dev/null; wait 2>/dev/null
```

## Technical Notes
- Use `trap 'kill 0' SIGINT SIGTERM` in the script so all children are
  killed on interrupt.
- Do NOT add `docker-compose` — Constitution #1, no new process tooling.

## Failure Protocol
- Max retries: 2. If the script cannot reliably bring up all 3 processes,
  escalate to an ops review before retrying.

---

---
id: T-7
title: "Debug Logging (HTTP Trace, Comment Body Redaction)"
Stage: NEW
Type: feature
Priority: P2
Origin: phase-1
Mode: autopilot
Depends-On: [IG-2]
Blocks: [IG-3]
Gate: IG-3
Files:
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/debug_http.py
    test: false
    description: "Add TASKBOARD_DEBUG_HTTP=1 middleware, refine truncation"
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/log_redaction.py
    test: false
    description: "Add comment_body_digest() producing sorted-keys SHA-256"
  - action: MODIFY
    path: packages/taskboard-core/tests/test_log_redaction.py
    test: true
    description: "Digest + redaction tests"
Read-First:
  - packages/taskboard-core/src/taskboard_core/debug_http.py
  - packages/taskboard-core/src/taskboard_core/log_redaction.py
Exemplar-Files:
  - packages/taskboard-core/src/taskboard_core/debug_http.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-core/tests/ -k 'debug_http or log_redaction' -v"
---
# T-7: Debug Logging

## Scope
MODIFY `packages/taskboard-core/src/taskboard_core/debug_http.py` to honor
`TASKBOARD_DEBUG_HTTP=1` and log request/response bodies to stderr.
MODIFY `log_redaction.py` to add `comment_body_digest()` that returns a
sorted-keys SHA-256 digest of the body for INFO-level logs (never raw).

## User Story
As a TaskBoard operator, I want opt-in debug logging that never leaks raw
comment bodies in default INFO logs so that on-call engineers can debug
request flows without a compliance review for every log line.

## Acceptance Criteria
- [ ] Given `TASKBOARD_DEBUG_HTTP=1`, when a request flows through the API,
  then request + response bodies are written to stderr
  (grep: `pytest -k debug_http_emits_stderr`)
- [ ] Given default (no debug env var), then only truncated summary
  (first 40 chars + `...`) appears in INFO logs (regression)
- [ ] Given a comment create INFO log, then `body` appears as a 64-char
  hex digest, never raw body text (failure-path: log scraping assertion
  over a test fixture with known body fails if raw body present)

## Verify

```bash
uv run pytest packages/taskboard-core/tests/ -k "debug_http or log_redaction" -v
```

## Technical Notes
- `TASKBOARD_DEBUG_HTTP` middleware wraps FastAPI `BaseHTTPMiddleware`;
  do NOT reach into ASGI internals.
- Digest uses `hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()`.
- Existing `debug_http.py` already provides truncation — extend, do not replace.

## Failure Protocol
- Max retries: 2. If debug output accidentally leaks raw body (caught by
  the log-scraping AC), revert and exit immediately; this is a security
  regression, not a logic bug.

---

---
id: IG-3
title: "Integration Gate: Full System Validation"
Stage: NEW
Type: integration-gate
Depends-On: [T-6, T-7]
Blocks: []
Validates: [T-6, T-7]
Expected-Test-Artifacts: []
---
# IG-3: Full System Validation

## Flows Under Test
- Given `start-local-stack.sh`, then all processes start and `/health`
  returns 200 within 20s.
- Given the full stack, then a Playwright flow posts a top-level comment,
  then a reply, then verifies the reply is indented AND the notifier
  dispatched AND the SSE subscriber received the event.
- Given `TASKBOARD_DEBUG_HTTP=1`, then debug output on stderr contains
  digested bodies only, never raw comment bodies.

## Proof Artifacts (required)
- [ ] Playwright run output (threaded reply flow, all three processes)
  with trace URL recorded
- [ ] stderr log snippet showing debug output with digested comment body
- [ ] CI run URL with green stages across core + api + notifier + web

## Silent Failure Detection
- If any single process fails to start silently, IG-3 must fail — assert
  all 3 PIDs present via `pgrep` before proceeding with flow.
- If debug output silently loses the digest (regression to raw body),
  fixture-based log scraping catches it.

## Dev Agent Record
- Verifier session id: `<captured at run time>`
- Model used: `<captured at run time>`
- Convention-drift check: run `scripts/lint-conventions.sh` against
  all 5 modified packages; zero drift required.

## Failure Protocol
- Max retries: 2. After 2 failed runs, revert T-6/T-7 and file a
  "planning failed safely" report if the root cause is architectural.

## Verified by
CI job or human reviewer
