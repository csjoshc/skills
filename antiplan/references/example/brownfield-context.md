# Brownfield Context: TaskBoard Threaded Comments

Phase 0 research artifact — the agent's written understanding of the codebase
at planning time. This was written to file (not summarized verbally) and
reviewed by the user, who corrected the agent's interpretation where needed.
Corrections are tagged User-stated in the Assumption Register.

This artifact exists so the implementing agent knows what to MODIFY vs CREATE.
It also serves as an early AP-9 (Greenfield Hallucination) detector: if the
planning agent misunderstands the existing codebase here, it is caught before
any tickets are generated.

TaskBoard is a fictional multi-user task-tracking application used here as a
domain-neutral worked example. Substitute your own project's packages, paths,
and signatures when using this file as a reference.

---

## Existing Package Inventory

These packages exist in the repo before any tickets are implemented:

| Package | Language | Path | Key modules |
|---------|----------|------|-------------|
| Core domain | Python | `packages/taskboard-core/` | `tasks.py` (create_task, list_tasks), `comments.py` (create_comment, list_comments_for_task), `models.py`, `db.py`, `events.py`, `debug_http.py` |
| HTTP API | Python | `packages/taskboard-api/` | `app.py` (FastAPI create_app), `routes_tasks.py`, `routes_comments.py`, `routes_sse.py`, `settings.py`, `auth.py` |
| Web SPA | TypeScript | `packages/taskboard-web/` | Vite + React app: `src/pages/TaskListPage.tsx`, `src/pages/TaskDetailPage.tsx`, `src/shared/apiClient.ts`, `src/shared/sseClient.ts` |
| Shared contracts | TypeScript + Python | `packages/taskboard-contracts/` | `schema.yaml` (canonical), generated `types.ts` + `models.py`, `build.py` codegen, `Makefile` |
| Notifier worker | Python | `packages/taskboard-notifier/` | `worker.py` (consume_events), `handlers.py`, `settings.py`, `dispatchers/email.py`, `dispatchers/webhook.py` |
| UI primitives | TypeScript | `packages/taskboard-ui/` | `CommentList`, `CommentComposer`, `TaskBadge`, `UserAvatar` — used by web SPA |
| Event bus client | Python | `packages/taskboard-eventbus/` | Thin publish/subscribe wrapper over in-repo broker; `publish.py`, `subscribe.py` (not modified by this plan) |
| Dev tooling | shell + Python | `scripts/` + `docs/` | `start-local-stack.sh`, `seed-db.py`, `local-dev.md`, `secrets-and-env.md` |

### Pre-Existing Component Capability Audit

| Component | Assumed capability | Verified? | Evidence | Gap |
|-----------|-------------------|-----------|----------|-----|
| HTTP API (`packages/taskboard-api/`) | Accepts `POST /v1/tasks/{id}/comments` with body | Yes | Route exists in `routes_comments.py` | — |
| HTTP API | Accepts `parent_id` on comment creation for threaded replies | **No** | `CommentCreate` schema omits `parent_id`; handler stores comment flat | **Capability gap:** thread-aware fields (`parent_id`, `thread_root_id`, `depth`), thread retrieval endpoint, and event-bus `comment.reply.posted` message must be added — requires modification tickets across core, api, contracts |
| HTTP API | Returns `{ ok: true, data }` / `{ ok: false, error }` format | Yes | Response shape in existing route handlers | — |

### Core Internal Architecture (for T-1 and T-5)

The implementing agent for T-1 needs to understand the core's internals:

- **Language/framework:** Python, SQLAlchemy 2.0 ORM, Pydantic v2 models,
  synchronous DB access via `db.session_scope()` context manager.
  Note: `taskboard-eventbus` is the publish/subscribe wrapper;
  `taskboard-core` owns domain logic and must not import `taskboard-api`.
- **Module structure:** `src/taskboard_core/` — `tasks.py` (task CRUD),
  `comments.py` (comment CRUD + queries), `models.py` (SQLAlchemy ORM),
  `db.py` (engine + session factory), `events.py` (event-bus publish shims).
- **Relationship routing:** Comments are currently stored flat with
  `task_id` FK only. Threading requires a self-referential FK
  `parent_comment_id` plus derived `thread_root_id` + `depth` columns.
- **Event pattern:** `events.publish_task_event(task_id, event_type, payload)`
  fans an event onto the in-repo bus. Notifier subscribes by `event_type`.
- **Existing pattern:** Follow `comments.py` query structure for new
  thread-traversal helpers; follow `events.py` for new event types.

## Existing Architecture (Observed)

```
Web SPA (Vite) → POST /v1/tasks/{id}/comments → API (FastAPI)
                                                    ↓
                                               taskboard-core (comments.py)
                                                    ↓
                                               SQLAlchemy ORM → Postgres
                                                    ↓ (publish)
                                               taskboard-eventbus → Notifier worker
```

## Pre-Existing Behaviors That Must NOT Break

1. `GET /health` returns `{"status": "ok"}`
2. `GET /v1/meta` returns API version + build SHA from env vars
3. `POST /v1/tasks` (create task) returns created task with assigned `id`
4. `POST /v1/tasks/{id}/comments` (flat comment) returns created comment
5. `GET /v1/tasks/{id}/comments` lists flat comments ordered by created_at
6. `GET /v1/sse/tasks/{id}` streams server-sent events for a task
7. Web SPA renders existing task detail page with flat comment list

## Naming Conventions (Observed)

- Python packages: `packages/{name}/src/{name_underscored}/`
  (e.g., `packages/taskboard-core/src/taskboard_core/`)
- Test files: `packages/{name}/tests/test_{module}.py`
- Test support: `packages/{name}/tests/support/` (e.g., `db_fixtures.py`)
- API config: Pydantic `BaseSettings` in `settings.py`, env-var driven
- API routes: one module per resource (`routes_tasks.py`, `routes_comments.py`)
- Web pages: `packages/taskboard-web/src/pages/{Name}Page.tsx`
- Web shared utilities: `packages/taskboard-web/src/shared/`
- Contracts: edit `schema.yaml`; run `make contracts` to regenerate

## Key Existing Function Signatures

### Core (`comments.py`)

```python
# BEFORE this plan — flat comments only
def create_comment(
    *, task_id: int, author_id: int, body: str,
    session: Session | None = None,
) -> Comment: ...

def list_comments_for_task(
    *, task_id: int,
    session: Session | None = None,
) -> list[Comment]: ...
```

### API (`routes_comments.py`)

```python
# BEFORE — endpoint accepts body but no parent_id
@router.post("/v1/tasks/{task_id}/comments", response_model=CommentRead)
def post_comment(task_id: int, payload: CommentCreate, ...): ...
# No thread retrieval endpoint exists yet
```

### Web (`apiClient.ts`)

```typescript
// BEFORE — sends body but no parent_id field
export async function postComment(
  taskId: number,
  payload: { body: string },
  options: { headers?: Record<string, string>; signal?: AbortSignal }
): Promise<{ id: number; body: string; createdAt: string }>
```

## What This Plan Changes (Summary)

The central change is **threaded comments with live reply notifications**:
- Core gains a `parent_comment_id` FK plus `thread_root_id`/`depth` traversal helpers
- API gains `parent_id` on `POST /v1/tasks/{id}/comments` and a new
  `GET /v1/tasks/{id}/comment-thread` endpoint returning nested JSON
- Web SPA renders an indented thread with collapse/expand controls
- Notifier emits reply notifications when a comment has non-null `parent_id`
- SSE channel gains a `comment.reply.posted` event type
- Contracts package adds `CommentThreadNode` and `CommentReplyPosted` DTOs

**No new packages or directories are created.** All tickets modify existing
files within existing packages.
