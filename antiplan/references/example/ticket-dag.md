# Ticket DAG: TaskBoard Threaded Comments with Reply Notifications

This file is **antiplan's Phase 3 output** — the ordered ticket DAG, per-ticket
stubs, and the Ticket Contract that spec-writer must honor when fleshing each
ticket. See [ticket-pack.md](ticket-pack.md) for the fleshed downstream output.

Antiplan's output boundary stops here. Spec-writer consumes this file plus
[prd.md](prd.md) and [brownfield-context.md](brownfield-context.md) to produce
`ticket-pack.md`. ticket-critic validates `ticket-pack.md` against the Ticket
Contract below before any ticket transitions to `Stage: BUILD`.

---

## §1. DAG

```
T-1 ──► T-2 ──► T-3 ──► IG-1 ──► T-4 ──► T-4a ──► T-5 ──► IG-2 ──► T-6 ──► IG-3
                                                                   T-7 ──►
```

| ID   | Title                                                   | Gate | Depends-On | Blocks      |
|------|---------------------------------------------------------|------|------------|-------------|
| T-1  | Core: add parent_id + thread helpers                    | IG-1 | —          | T-2         |
| T-2  | API: accept parent_id + thread endpoint + bearer auth   | IG-1 | T-1        | T-3         |
| T-3  | Web: render threaded tree + send parent_id on reply     | IG-1 | T-2        | IG-1        |
| IG-1 | Integration gate: threaded display works e2e            | —    | T-1,T-2,T-3| T-4,T-5     |
| T-4  | Notifier: handle comment.reply.posted                   | IG-2 | IG-1       | T-4a        |
| T-4a | Contracts: add thread + reply DTOs, regenerate          | IG-2 | T-4        | T-5         |
| T-5  | SSE: fan comment.reply.posted to subscribers            | IG-2 | T-4a       | IG-2        |
| IG-2 | Integration gate: reply notifications + SSE e2e         | —    | T-4,T-4a,T-5| T-6,T-7    |
| T-6  | Start-all script + local dev runbook                    | IG-3 | IG-2       | IG-3        |
| T-7  | Debug logging (HTTP trace, comment body redaction)      | IG-3 | IG-2       | IG-3        |
| IG-3 | Integration gate: full system validation                | —    | T-6,T-7    | —           |

Scope-box: 8 feature tickets + 3 integration gates = 11 nodes (≤10 feature
scope-box respected; gates excluded from count).

---

## §2. Per-Ticket Stubs

Each stub is antiplan's hardened contract for the ticket: frontmatter + a
one-paragraph scope + 2–3 invariant acceptance criteria that must survive into
`ticket-pack.md`. spec-writer expands these into the full AC sets, Verify
commands, Technical Notes, and Failure Protocol required by the Ticket Contract.

### T-1

```yaml
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
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/models.py
  - action: MODIFY
    path: packages/taskboard-core/tests/test_comments.py
Read-First:
  - packages/taskboard-core/src/taskboard_core/comments.py
  - packages/taskboard-core/tests/test_comments.py
Exemplar-Files:
  - packages/taskboard-core/src/taskboard_core/comments.py
Assumptions-Validated: [A-5]
Regression-Baseline:
  - "uv run pytest packages/taskboard-core/tests/ -v"
```

**Scope:** Extend the `Comment` ORM model with `parent_comment_id`,
`thread_root_id`, `depth`; extend `create_comment` to accept optional
`parent_id` and derive root/depth; add `get_comment_thread(task_id)` returning
a nested structure.

**Invariant ACs:**
- Given a reply to an existing root comment, then persisted row has
  `parent_comment_id`, `thread_root_id == parent.thread_root_id or parent.id`,
  `depth == parent.depth + 1`.
- Given `get_comment_thread(task_id)`, then returned structure is a list of
  root nodes with fully populated `children` lists.
- Given no `parent_id`, then behavior matches pre-existing single-level
  comment (regression).

---

### T-2

```yaml
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
  - action: MODIFY
    path: packages/taskboard-api/src/taskboard_api/auth.py
  - action: MODIFY
    path: packages/taskboard-api/tests/test_routes_comments.py
Read-First:
  - packages/taskboard-api/src/taskboard_api/routes_comments.py
  - packages/taskboard-api/src/taskboard_api/auth.py
Exemplar-Files:
  - packages/taskboard-api/src/taskboard_api/routes_comments.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-api/tests/test_routes_comments.py -v"
```

**Scope:** Extend `POST /v1/tasks/{id}/comments` with optional `parent_id`;
add `GET /v1/tasks/{id}/comment-thread`; enforce bearer auth on both.

**Invariant ACs:**
- Given a request with valid bearer and `parent_id`, then response includes
  `parent_id`, `thread_root_id`, `depth`.
- Given a missing/invalid bearer, then 401 with no DB write.
- Given a cross-task `parent_id`, then 400 and no DB write.

---

### T-3

```yaml
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
  - action: MODIFY
    path: packages/taskboard-web/src/shared/apiClient.ts
Read-First:
  - packages/taskboard-ui/src/components/
  - packages/taskboard-web/src/shared/apiClient.ts
Exemplar-Files:
  - packages/taskboard-ui/src/components/
Assumptions-Validated: [A-3]
Regression-Baseline:
  - "npm --prefix packages/taskboard-web run test"
```

**Scope:** Use `GET /v1/tasks/{id}/comment-thread` to render indented tree on
task detail; add reply composer that sends `parent_id`.

**Invariant ACs:**
- Given user clicks "Reply" on comment 17 and submits, then the request body
  includes `parent_id: 17`.
- Given the thread endpoint returns nested nodes, then the UI renders each
  child indented under its parent by `depth` CSS step.
- Given the existing flat list path, then it continues to function (regression).

---

### IG-1

```yaml
id: IG-1
title: "Integration Gate: Threaded Comment Display Works E2E"
Stage: NEW
Type: integration-gate
Depends-On: [T-1, T-2, T-3]
Blocks: [T-4, T-5]
Validates: [T-1, T-2, T-3]
```

**Scope:** Prove that a reply posted through the web UI lands indented under
its parent on a fresh page load and that direct curl against the thread
endpoint returns the same nested shape.

**Invariant ACs:**
- curl transcript captured showing threaded POST then nested GET.
- Playwright run captured showing reply indented under parent.

---

### T-4

```yaml
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
  - action: MODIFY
    path: packages/taskboard-notifier/src/taskboard_notifier/worker.py
  - action: MODIFY
    path: packages/taskboard-notifier/tests/test_handlers.py
Read-First:
  - packages/taskboard-notifier/src/taskboard_notifier/worker.py
  - packages/taskboard-notifier/src/taskboard_notifier/handlers.py
Exemplar-Files:
  - packages/taskboard-notifier/src/taskboard_notifier/handlers.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-notifier/tests/ -v"
```

**Scope:** Register a `comment.reply.posted` handler in the worker dispatch
table; redact PII in the reply-body excerpt before dispatcher call.

**Invariant ACs:**
- Given a reply event on the bus, then handler invokes email dispatcher with
  `{parent_author_id, reply_author_id, body_excerpt}`.
- Given a top-level comment (no `parent_id`), then handler is NOT invoked
  (regression).

---

### T-4a

```yaml
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
  - action: MODIFY
    path: packages/taskboard-contracts/build.py
  - action: MODIFY
    path: packages/taskboard-contracts/tests/test_generated.py
Read-First:
  - packages/taskboard-contracts/schema.yaml
  - packages/taskboard-contracts/build.py
Exemplar-Files:
  - packages/taskboard-contracts/schema.yaml
Assumptions-Validated: [A-1]
Regression-Baseline:
  - "uv run pytest packages/taskboard-contracts/tests/ -v"
```

**Scope:** Add `CommentThreadNode` and `CommentReplyPosted` DTOs to
`schema.yaml`; regenerate TS + Python types; add CI drift check.

**Invariant ACs:**
- Given `make contracts`, then `types.ts` and `models.py` include both new
  DTOs with identical field names.
- Given `schema.yaml` edited without regenerating, then CI exits non-zero.

---

### T-5

```yaml
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
  - action: MODIFY
    path: packages/taskboard-api/src/taskboard_api/routes_sse.py
  - action: MODIFY
    path: packages/taskboard-api/tests/test_routes_sse.py
Read-First:
  - packages/taskboard-core/src/taskboard_core/events.py
  - packages/taskboard-api/src/taskboard_api/routes_sse.py
Exemplar-Files:
  - packages/taskboard-api/src/taskboard_api/routes_sse.py
Assumptions-Validated: [A-1]
Regression-Baseline:
  - "uv run pytest packages/taskboard-api/tests/test_routes_sse.py -v"
```

**Scope:** Add event constructor + SSE fan-out for `comment.reply.posted`;
subscribers get event immediately after DB commit.

**Invariant ACs:**
- Given an SSE subscriber on `/v1/sse/tasks/{id}`, when a reply is posted,
  then subscriber receives `event: comment.reply.posted`.
- Given a top-level comment, then no reply event on SSE (regression).

---

### IG-2

```yaml
id: IG-2
title: "Integration Gate: Reply Notifications + SSE Work E2E"
Stage: NEW
Type: integration-gate
Depends-On: [T-4, T-4a, T-5]
Blocks: [T-6, T-7]
Validates: [T-4, T-4a, T-5]
```

**Scope:** End-to-end from reply POST → bus event → notifier dispatch → SSE
fan-out to a connected subscriber.

**Invariant ACs:**
- curl transcript of reply POST captured.
- Notifier log line confirming dispatcher called.
- SSE subscriber log confirming event received.

---

### T-6

```yaml
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
  - action: MODIFY
    path: docs/local-dev.md
  - action: MODIFY
    path: docs/secrets-and-env.md
Read-First:
  - scripts/start-local-stack.sh
  - docs/local-dev.md
Exemplar-Files:
  - scripts/start-local-stack.sh
Assumptions-Validated: []
Regression-Baseline: []
```

**Scope:** Update stack script + runbook so a new developer can post a
threaded reply within 10 minutes.

**Invariant ACs:**
- Given `bash scripts/start-local-stack.sh`, then API + notifier + web all
  respond on their declared ports.
- Given `docs/local-dev.md`, then the doc walks through posting a reply end-to-end.

---

### T-7

```yaml
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
  - action: MODIFY
    path: packages/taskboard-core/src/taskboard_core/log_redaction.py
Read-First:
  - packages/taskboard-core/src/taskboard_core/debug_http.py
Exemplar-Files:
  - packages/taskboard-core/src/taskboard_core/debug_http.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/taskboard-core/tests/ -k 'debug_http or log_redaction' -v"
```

**Scope:** Add `TASKBOARD_DEBUG_HTTP` middleware tracing + sorted-keys
SHA-256 digest of comment body in logs (never raw body).

**Invariant ACs:**
- Given `TASKBOARD_DEBUG_HTTP=1`, then request + response bodies logged to stderr.
- Given a comment create log entry, then body appears as digest not raw text.

---

### IG-3

```yaml
id: IG-3
title: "Integration Gate: Full System Validation"
Stage: NEW
Type: integration-gate
Depends-On: [T-6, T-7]
Blocks: []
Validates: [T-6, T-7]
```

**Scope:** Full stack up, threaded reply posted, notifier dispatched, SSE
received, debug logs verified clean of raw comment bodies.

**Invariant ACs:**
- Playwright run captured across all layers.
- stderr log snippet shows digested body, not raw text.

---

## §3. Ticket Contract

Every ticket in `ticket-pack.md` MUST satisfy the following. ticket-critic
blocks `Stage: BUILD` transitions if any hard gate fails.

### Frontmatter (YAML, required fields)

- `id`, `title`, `Stage`, `Type`, `Priority`, `Origin`, `Mode`, `Depends-On`, `Blocks`, `Gate`
- `Files[]`: `{ action: MODIFY|CREATE, path, test: bool, description }` — ≥1 entry
- `Read-First[]`: ≥2 repo-relative paths (paths MUST exist at plan time)
- `Exemplar-Files[]`: ≥1 repo-relative path (path MUST exist at plan time)
- `Assumptions-Validated[]`: list of assumption IDs from PRD §14 (may be empty)
- `Regression-Baseline[]`: ≥1 executable shell command (or `[]` only for
  doc-only tickets with explicit justification)

### Body (required sections, in order)

1. **Scope** — one paragraph, file-level (names specific files from `Files[]`)
2. **User Story** — "As a [persona from PRD §3], I want […] so that […]"
3. **Acceptance Criteria** — ≥3 items, each:
   - grep-verifiable (the body includes a concrete `rg`/`pytest -k`/`curl`/shell snippet)
   - ≥1 item MUST be a failure-path AC asserting user-visible behavior
     (not a log line; must be observable by the user or an integration test)
4. **Verify** — single shell command block that exits non-zero on AC failure
5. **Technical Notes** — implementation anchors (concrete APIs, config keys,
   existing functions to reuse). Not design speculation.
6. **Failure Protocol** — max retry count (default 2), revert-and-exit
   condition (after N consecutive failed attempts), escalation target

### Additional requirements for integration-gate tickets

- **Silent Failure Detection:** ≥1 AC that would catch a silent regression
  in a real running system (not just unit tests passing)
- **Dev Agent Record:** verifier session ID, model used, convention-drift check
- **Proof Artifacts:** curl transcript path, trace URL (Playwright/browser
  session/recording), CI run URL
- Gate is a hard dependency — downstream tickets cannot start until
  gate reaches `Stage: COMPLETE`

### Hard gates (ticket-critic enforces)

- No `[NEEDS CLARIFICATION]` markers anywhere in the ticket body
- Every `Files[]` path resolves against repo root (ticket-critic runs `test -e`
  for MODIFY actions; CREATE paths MUST resolve to a valid parent directory)
- Every `Read-First[]` / `Exemplar-Files[]` path exists at plan time
- Every AC's grep/test command is executable as written (ticket-critic dry-runs it)
- Ticket production file count ≤ 5 (AP-12 prevention)
- `Assumptions-Validated[]` references resolve to PRD §14 IDs

---

## §4. Handoff

1. Feed `prd.md` + this file (`ticket-dag.md`) + `brownfield-context.md` into
   `spec-writer`. spec-writer expands each stub into the full body required
   by §3 (Ticket Contract) and emits `ticket-pack.md`.
2. Run `ticket-critic` against `ticket-pack.md` with this file's §3 as the
   contract. If any hard gate fails, ticket-critic emits a report; the
   offending ticket remains `Stage: NEW` until re-drafted.
3. Tickets that pass ticket-critic transition to `Stage: BUILD` and are
   executed via `orchestrate`.
4. Integration gates (`IG-*`) block their downstream tickets until
   `Stage: COMPLETE` — enforced by the orchestrator, not by convention alone.
