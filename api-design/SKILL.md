---
name: api-design
description: >-
  API contract design (REST/GraphQL/RPC). Use when designing endpoints,
  writing schema, or evolving an existing API. Covers Hyrum's Law, branded
  types, error semantics, versioning. Not for PR-time review (use
  /security-review or pr-review).
---

<!-- imported from addyosmani/agent-skills api-and-interface-design -->

# API and Interface Design

Design stable, hard-to-misuse contracts. Applies to REST, GraphQL, module boundaries, component props, anywhere code talks to code.

## When to Use

| Trigger | Example |
|---|---|
| New endpoint | `POST /api/tasks` |
| Module boundary | Service-to-service contract |
| Component props | Public component API |
| Schema change | Field add/remove/retype |

## Core Principles

**Hyrum's Law.** Every observable behavior — undocumented quirks, error text, ordering — becomes a de facto contract. Design implications:

| Implication | Consequence |
|---|---|
| Be intentional about what's exposed | Each public behavior is a commitment |
| Don't leak implementation details | Observable = depended on |
| Plan deprecation at design time | See `deprecate` skill |
| Tests are not enough | Contract tests miss observable quirks |

**One-Version Rule.** Don't force consumers to choose between versions. Extend, don't fork.

**Contract First.** Define the interface before implementing. The contract is the spec.

```typescript
interface TaskAPI {
  createTask(input: CreateTaskInput): Promise<Task>;
  listTasks(params: ListTasksParams): Promise<PaginatedResult<Task>>;
  getTask(id: string): Promise<Task>;
  updateTask(id: string, input: UpdateTaskInput): Promise<Task>;
  deleteTask(id: string): Promise<void>;
}
```

**Consistent Error Semantics.** Pick one strategy, use it everywhere.

```typescript
interface APIError {
  error: {
    code: string;        // "VALIDATION_ERROR"
    message: string;     // "Email is required"
    details?: unknown;
  };
}
```

| Status | Meaning |
|---|---|
| 400 | Client sent invalid data |
| 401 | Not authenticated |
| 403 | Authenticated, not authorized |
| 404 | Not found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Validation failed (semantically invalid) |
| 500 | Server error (never expose internals) |

**Validate at boundaries** — API routes, form handlers, third-party responses, env loading. Not between trusted internal functions.

> Third-party API responses are untrusted. Validate shape and content before use.

**Prefer addition over modification.** Add optional fields; don't retype or remove.

## Naming

| Pattern | Convention | Example |
|---|---|---|
| REST endpoints | Plural nouns, no verbs | `GET /api/tasks` |
| Query params | camelCase | `?sortBy=createdAt&pageSize=20` |
| Response fields | camelCase | `{ createdAt, taskId }` |
| Booleans | is/has/can prefix | `isComplete`, `hasAttachments` |
| Enums | UPPER_SNAKE | `"IN_PROGRESS"` |

### No vendor / runtime / cycle tokens in identifiers

API paths, query-param names, response fields, enum values, error
codes, and config filenames must not bake in a specific vendor,
runtime, or cycle slug when the design supports more than one. The
name asserts a coupling the architecture denies, and every future
contributor who tries to swap the vendor / runtime / cycle either
edits the name everywhere or learns to live with a lie.

| Bad | Good | Why |
|---|---|---|
| `GET /api/agents/docker-model-runner/status` | `GET /api/agents/runtime/status` | Runtime is configurable; the path should name the role |
| `enum Provider { DMR, OLLAMA_LOCAL, AWS_BEDROCK }` | `enum Provider { LOCAL, CLOUD }` if granularity allows; otherwise keep vendor names but lock them behind a `runtime_id` field, not a path segment | Enum values land in DBs and logs; rename cost is N× higher than a path |
| `{ "ollamaModel": "..." }` | `{ "model": "..." }` | Response field names should reflect the abstraction; runtime-specific metadata goes in a `runtime: { id, ... }` sub-object |
| `error: "DMR_UNREACHABLE"` | `error: "RUNTIME_UNREACHABLE"` with `details.runtime: "dmr"` | Error *codes* are the stable contract; details carry the specifics |
| Config file `agent.local-dmr.yaml` | `agent.local.yaml` (runtime picked by `LLM_RUNTIME` env) | Filename is a public API too |

Allowed exceptions: code paths, modules, or sub-routes that exist
*to implement that vendor* (`packages/c3-flight-mcp/dmr-adapter.ts`,
`POST /api/internal/dmr/probe`) earn the vendor token because they
literally implement that vendor's protocol. Anything that *consumes*
the abstraction must use the abstract name.

### Configuration naming

The same rule extends to config files, env var names, and YAML keys
your service reads — these are part of the API surface even though
they don't ship over HTTP.

| Bad | Good |
|---|---|
| `OLLAMA_BASE_URL`, `DMR_MODEL` | `LLM_BASE_URL`, `LLM_MODEL` (project-prefixed, vendor-agnostic) |
| `agent.dmr.yaml`, `provider-ollama.json` | `agent.yaml` + a `runtime:` field selecting `dmr` / `ollama` |
| `dmr_pull_tag = "hf.co/unsloth/..."` | catalog file keyed by alias × runtime; consumers reference the alias |

Vendor-specific values stay confined to the *catalog data file* or
the *vendor adapter module*. The surfaces the rest of the system
reads stay agnostic.

## REST Patterns

```
GET    /api/tasks              List
POST   /api/tasks              Create
GET    /api/tasks/:id          Read
PATCH  /api/tasks/:id          Partial update
DELETE /api/tasks/:id          Delete
GET    /api/tasks/:id/comments Sub-resource
```

Pagination response shape:

```typescript
{
  "data": [...],
  "pagination": { "page": 1, "pageSize": 20, "totalItems": 142, "totalPages": 8 }
}
```

PATCH accepts partial; only provided fields change.

## TypeScript Patterns

**Discriminated unions for variants:**

```typescript
type TaskStatus =
  | { type: 'pending' }
  | { type: 'in_progress'; assignee: string; startedAt: Date }
  | { type: 'completed'; completedAt: Date; completedBy: string }
  | { type: 'cancelled'; reason: string; cancelledAt: Date };
```

**Input/Output separation.** Input = what caller provides. Output = includes server-generated fields.

**Branded types for IDs:**

```typescript
type TaskId = string & { readonly __brand: 'TaskId' };
type UserId = string & { readonly __brand: 'UserId' };
function getTask(id: TaskId): Promise<Task> { ... }
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll document the API later" | Types ARE the documentation. Define them first. |
| "We don't need pagination for now" | You will at 100 items. Add it from the start. |
| "PATCH is complicated, use PUT" | PUT requires full object every time. PATCH is what clients want. |
| "We'll version when we need to" | Breaking changes without versioning break consumers. |
| "Nobody uses that undocumented behavior" | Hyrum's Law: somebody does. |
| "We can maintain two versions" | Diamond dependencies + double maintenance. |
| "Internal APIs don't need contracts" | Internal consumers are still consumers. |

## Red Flags

- Endpoints returning different shapes by condition
- Inconsistent error formats
- Validation scattered through internal code
- Breaking changes to existing fields
- List endpoints without pagination
- Verbs in REST URLs (`/api/createTask`)
- Third-party responses used without validation

## Verification

- [ ] Every endpoint has typed input/output schemas
- [ ] Errors follow one consistent format
- [ ] Validation only at boundaries
- [ ] List endpoints paginate
- [ ] New fields are additive and optional
- [ ] Naming is consistent
- [ ] Docs/types committed alongside implementation

## See Also

- [`deprecate`](../deprecate/SKILL.md) — removing or replacing an API
- [`harden`](../harden/SKILL.md) — security boundaries on input
