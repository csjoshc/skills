# Brownfield Context: Enterprise Chat Agent

Phase 0 research artifact — the agent's written understanding of the codebase
at planning time. This was written to file (not summarized verbally) and
reviewed by the user, who corrected the agent's interpretation where needed.
Corrections are tagged User-stated in the Assumption Register.

This artifact exists so the implementing agent knows what to MODIFY vs CREATE.
It also serves as an early AP-9 (Greenfield Hallucination) detector: if the
planning agent misunderstands the existing codebase here, it is caught before
any tickets are generated.

---

## Existing Package Inventory

These packages exist in the repo before any tickets are implemented:

| Package | Language | Path | Key modules |
|---------|----------|------|-------------|
| Orchestration | Python | `packages/c3-ai-orchestration/` | `turn.py` (run_chat_turn, run_chat_turn_stream), `types.py`, `mcp_invoke.py`, `debug_http.py`, `exceptions.py` |
| BFF | Python | `packages/c3-ai-bff/` | `app.py` (FastAPI create_app), `executor.py`, `settings.py`, `system_prompt.py`, `tools_catalog.py`, `http_debug.py` |
| React SPA | TypeScript | `react/` (does not exist yet) | **Not present at planning commit.** `packages/ui/` has chat component primitives (ChatMessageLog, ChatMessageComposer, ChatThreadSidebar) but no page-level app. T-3 creates a minimal chat page. |
| Core framework | Python | `packages/core/` | `runtime/executor.py` (AgentRuntime), `providers/`, `types.py`, `config/manager.py` |
| Guardrails | Python | `packages/guardrails/` | `factory.py` (create_pipeline), input/output/tool guardrails |
| Tool gateway | Python | `packages/c3-ai-mcp-bff/` | Pre-existing MCP invoke server (`app.py` FastAPI, `flight_tools.py`, `settings.py`) |
| MCP data server | TypeScript | `packages/mcp-data-server/` | Fastify server with DataConnector interface, catalog/query/ingest routes (not modified by this plan) |
| UI primitives | TypeScript | `packages/ui/` | Chat component primitives used by T-3 |

### Pre-Existing Component Capability Audit

| Component | Assumed capability | Verified? | Evidence | Gap |
|-----------|-------------------|-----------|----------|-----|
| Tool gateway (`packages/c3-ai-mcp-bff/`) | Accepts `POST /v1/mcp/invoke` with tool name + args | Yes | Route exists in `src/routes/` | — |
| Tool gateway | Has flight-specific tool definitions (list_searches, create_search, etc.) | **No** | No flight tool schemas in gateway code | **Capability gap:** flight tool definitions, OAuth token flow for Flight API, C3 HTTP client for upstream calls must be added — requires modification ticket or new package |
| Tool gateway | Returns `{ ok: true, result }` / `{ ok: false, error }` format | Yes | Response shape in existing route handler | — |

### Tool Gateway Internal Architecture (for T-4a)

The implementing agent for T-4a needs to understand the gateway's internals:

- **Language/framework:** Python, FastAPI (same as BFF — not TypeScript).
  Note: `packages/mcp-data-server/` is the TypeScript Fastify server;
  `packages/c3-ai-mcp-bff/` is the Python MCP invoke proxy.
- **Module structure:** `src/c3_ai_mcp_bff/` — `app.py` (FastAPI routes),
  `flight_tools.py` (flight tool definitions), `settings.py` (env config).
- **Tool routing:** The MCP invoke endpoint dispatches by tool name. Flight
  tools need to be registered with schemas and routed to the upstream
  Flight API via an HTTP client with OAuth.
- **Auth pattern:** The gateway needs OAuth client-credentials grant against
  the Flight API's token endpoint, with token caching and refresh on 401.
- **Existing pattern:** Follow `app.py` route structure for new endpoints;
  follow `settings.py` for env-var configuration.

## Existing Architecture (Observed)

```
React SPA (Vite) → POST /v1/chat/stream → BFF (FastAPI)
                                              ↓
                                         Orchestration (run_chat_turn)
                                              ↓
                                         SecureModelProvider + AgentRuntime
                                              ↓ (tool calls)
                                         POST /v1/mcp/invoke → Tool Gateway → Flight API
```

## Pre-Existing Behaviors That Must NOT Break

1. `GET /health` returns `{"status": "ok"}`
2. `GET /v1/meta` returns classification from agent YAML
3. `POST /v1/chat` (blocking, single message) returns assistant text
4. `POST /v1/chat/stream` (SSE, single message array) streams text + tool events
5. All existing guardrail tests pass (injection, PII, permission gate)
6. Tool gateway accepts `POST /v1/mcp/invoke` with `X-Mcp-Invoke-Secret`
7. React chat page renders streamed responses with tool status indicators

## Naming Conventions (Observed)

- Python packages: `packages/{name}/src/{name_underscored}/`
  (e.g., `packages/c3-ai-orchestration/src/c3_ai_orchestration/`)
- Test files: `packages/{name}/tests/test_{module}.py`
- Test support: `packages/{name}/tests/support/` (e.g., `scripted_provider.py`)
- Agent config: `packages/c3-ai-bff/config/agent.*.yaml`
- BFF settings: Pydantic `BaseSettings` in `settings.py`, env-var driven
- BFF routes: all in `app.py` via `create_app()` factory (no separate route files)
- React pages: `react/src/pages/{Name}Page.tsx`
- Shared utilities: `react/src/shared/`

## Key Existing Function Signatures

### Orchestration (`turn.py`)

```python
# BEFORE this plan — single-turn only
async def run_chat_turn(
    *, user_text: str, turn_config: ChatTurnConfig,
    session_id: str | None = None,
    tool_executor: StrToolExecutor, model_provider: ModelProvider,
    on_tool_event: ToolEventCallback | None = None,
) -> ChatTurnResult: ...

async def run_chat_turn_stream(
    *, user_text: str, turn_config: ChatTurnConfig,
    session_id: str | None = None,
    tool_executor: StrToolExecutor, model_provider: ModelProvider,
) -> AsyncIterator[ChatStreamEvent]: ...
```

### BFF (`app.py`)

```python
# BEFORE — /v1/chat/stream accepts messages but only uses last user message
@app.post("/v1/chat/stream")
async def chat_stream(body: ChatStreamRequest): ...
# No /v1/chat/full endpoint exists yet
```

### React (`chatStreamClient.ts`)

```typescript
// BEFORE — sends messages array but BFF ignores prefix
export async function streamAssistantReply(
  url: string,
  messages: ChatTurn[],
  options: { headers?: Record<string, string>; signal?: AbortSignal;
             onToolEvent?: (status: ToolStatus) => void;
             onText?: (delta: string) => void; }
): Promise<{ text: string; toolTrace: ToolStatus[] }>
```

## What This Plan Changes (Summary)

The central change is **true multi-turn conversation history**:
- Orchestration gains a `conversation_prefix` parameter
- BFF gains a `/v1/chat/full` blocking endpoint that accepts full history
- BFF's `/v1/chat/stream` forwards full message array as prefix
- React sends the complete conversation history on every turn
- Core framework gains `tool_exec_start`/`tool_exec_result` stream events

**No new packages or directories are created** (except a minimal React chat
page using existing `packages/ui/` primitives). All other tickets modify
existing files.
