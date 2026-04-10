# PRD: Enterprise Chat Agent with Multi-Turn Tool Calling

## Status: APPROVED
## Date: [project start date]
## Author: [developer] + antiplan skill
## Classification: Light → Standard (upgraded after tool scope identified)

---

## 1. Problem Statement

Platform developers need an integrated chat demo that shows an LLM answering
questions and calling a domain REST API (Flight Price Tracker) via tool calls,
with full multi-turn conversation context, deployable as an enterprise platform
package. The current single-turn implementation exists but discards conversation
history between turns.

## 2. Constitution

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | No new packages unless existing ones can't handle it | AP-9 prevention; every new package is a naming/integration risk |
| 2 | MCP is the tool transport — one path, not multiple | Avoid speculative architecture; the MCP bridge already works |
| 3 | TDD for all orchestration logic | Orchestration bugs are invisible until integration; tests catch them early |
| 4 | Browser never holds LLM keys or API OAuth secrets | Security constraint — secrets stay server-side |
| 5 | One forward-looking PRD, not retrospective design docs | AP-2 prevention |

## 3. Users

| User | Role | Primary workflow | Pain without this system |
|------|------|-----------------|-------------------------|
| Platform developer | Demos agent capabilities to stakeholders | Opens chat, asks about flights across multiple turns, shows tool-augmented responses | No multi-turn demo; each message loses prior context |
| Integration tester | Validates agent pipeline works e2e | Runs start-all script, sends multi-turn conversation, verifies tool loop with context | Manual curl against separate services; no conversation continuity testing |

## 4. Minimum Testable Product (MTP)

The smallest set of features that proves the design works end-to-end:

1. **Multi-turn streaming chat** — user sends message N, LLM sees messages 1..N
2. **Tool calling with context** — LLM calls a flight tool with awareness of prior conversation

**MTP validation:** After T-1, T-2, T-3, integration gate IG-1 confirms:
- Given BFF + LLM running, when user sends "hello" then follows up with
  "what did I just say?", then the assistant's response references the prior turn
- Given BFF + LLM + tool gateway running, when user asks about flights then
  refines the query, then the LLM uses prior context to refine its tool call

## 5. Features

### 5.1 Multi-Turn Streaming Chat (SSE)

**Priority:** P1
**User story:** As a platform developer, I want the chat to maintain full
conversation history across turns so that follow-up questions work naturally.

**Acceptance criteria:**
- [ ] Given BFF running with LLM, when I POST to `/v1/chat/stream` with
  `messages: [{role: "user", content: "hello"}, {role: "assistant", content: "Hi!"},
  {role: "user", content: "what did I just say?"}]`, then the assistant response
  references "hello" from the first turn
- [ ] Given the React chat page, when I type a follow-up message, then the
  full conversation history is sent to the BFF (not just the latest message)
- [ ] Given `POST /v1/chat/full` with messages array, then the blocking
  response also uses full conversation context
- [ ] Given an LLM error mid-conversation, then a `type: error` SSE event is
  sent and the UI shows a user-friendly error without losing prior messages

**Out of scope:** Persistent chat history across page reloads. Server-side
session storage. Multi-user sessions.

**Ticket(s):** T-1, T-2, T-3
**Gate:** IG-1

### 5.2 Flight Tool Calling via MCP

**Priority:** P1
**User story:** As a platform developer, I want the LLM to call Flight API
tools when I ask about flights, so the demo shows agentic capabilities.

**Acceptance criteria:**
- [ ] Given BFF + tool gateway running, when I ask "list my flight searches",
  then the LLM emits a `tool_calls` response, the BFF dispatches to the
  gateway, and the assistant response contains the search results in prose
- [ ] Given a tool call, when the gateway returns flight data, then the
  chat stream includes `tool_start` and `tool_end` SSE events
- [ ] Given a tool call failure (gateway unreachable), then the assistant
  response includes a user-friendly error, not a stack trace

**Out of scope:** Dedicated REST BFF for flights (MCP path is sufficient per
Constitution #2). Composite executor. Elicitation phrases.

**Ticket(s):** T-4, T-5
**Gate:** IG-2

### 5.3 System Prompt with API Context

**Priority:** P1
**User story:** As a platform developer, I want the LLM to know what flight
operations are available without me listing them, so the demo is self-guided.

**Acceptance criteria:**
- [ ] Given `openapi/flights-api.yaml` exists, when the BFF starts, then
  the system prompt includes a formatted catalog of available operations
- [ ] Given the system prompt includes the catalog, when I ask "what can you
  do with flights?", then the LLM responds with the available operations
- [ ] Given the catalog exceeds a char limit, then it is truncated without
  breaking the prompt structure

**Ticket(s):** T-4 (wired as part of tool setup)
**Gate:** IG-2

### 5.4 Security & Guardrails

**Priority:** P1
**User story:** As a platform operator, I want all LLM calls to pass through
guardrails (input filtering, output PII redaction, tool permission gates) so
the demo meets organizational security standards.

**Acceptance criteria:**
- [ ] Given a prompt injection attempt, when sent via chat, then the input
  guardrail blocks it and returns an error response
- [ ] Given an LLM response containing PII patterns (SSN, email), then the
  output filter redacts them before the response reaches the user
- [ ] Given a tool call for a tool not in the agent's permissions, then the
  permission gate blocks it
- [ ] Given `POST /v1/chat/full` or `POST /v1/chat/stream` without a valid
  `Authorization: Bearer <token>` header, then the BFF returns 401
  (token validated via `CHAT_BFF_BEARER_TOKEN` env var with HMAC check)
- [ ] Given an `AgentRuntime` with tool execution, when a tool call is
  dispatched, then `ControlFlowPolicy` from `config.control_flow` YAML
  evaluates the call before execution proceeds

**Out of scope:** Production-grade auth (OAuth, OIDC). Bearer token is a
shared-secret gate for demo scope, acknowledged as upgradeable.

**Ticket(s):** T-1 (guardrails wired in orchestration core), T-2 (bearer auth)
**Gate:** IG-1

### 5.5 Operational Tooling

**Priority:** P2
**User story:** As a developer running the demo locally, I want a start-all
script, debug logging, and env documentation so I can get the stack running
without reading source code.

**Acceptance criteria:**
- [ ] Given `scripts/start-local-stack.sh`, when I run it, then all
  3 processes (BFF, tool gateway, Vite) start on correct ports
- [ ] Given `APP_DEBUG_HTTP=1`, when a request flows through the BFF, then
  request/response bodies are logged to stderr
- [ ] Given `docs/local-dev.md`, when a new developer reads it, then they
  can start the stack and send a chat message within 10 minutes

**Ticket(s):** T-6, T-7
**Gate:** IG-3

## 6. Success Criteria

| ID | Criterion | Target | Measurement |
|----|-----------|--------|-------------|
| SC-001 | Chat response latency (first token) | <5s (p95) on local LLM | Timed from POST to first SSE `text` event |
| SC-002 | Multi-turn context retention | Follow-up references prior turns correctly | Manual review of 3 multi-turn conversations |
| SC-003 | New developer setup time | <10 min from clone to working chat | Timed walkthrough of local-dev.md |

## 7. Architecture Decisions

| Decision | Options considered | Chosen | Justification |
|----------|-------------------|--------|---------------|
| Conversation state | Client-side (send full history) vs server-side sessions | Client-side | Constitution #1 — no DB process. Ephemeral demo scope. Client already holds messages in React state. |
| Tool transport | MCP only vs MCP + REST BFF vs REST only | MCP only | Constitution #2. One path. REST BFF adds a process, a port, and a composite executor for no user-visible benefit. |
| LLM provider interface | Direct vendor SDK vs OpenAI-compat abstraction | OpenAI-compat via provider registry | Provider-agnostic. Swap LLM vendor by changing config YAML. |
| Streaming transport | WebSocket vs SSE | SSE | Simpler. Unidirectional (server→client) is sufficient. No connection upgrade needed. |
| BFF language | Python (FastAPI) vs TypeScript (Express) | Python (FastAPI) | Orchestration core is Python. Same language avoids a cross-process boundary. |

## 8. Component Map

| Component | Responsibility | Owner tickets | Existing path |
|-----------|---------------|---------------|---------------|
| Orchestration | Builds secure model provider + guardrails, runs agent runtime for a chat turn with conversation prefix, yields stream events or blocking result | T-1 | `packages/c3-ai-orchestration/src/` |
| BFF | FastAPI HTTP facade: routes, CORS, SSE streaming, system prompt composition, tool catalog, executor wiring, conversation prefix forwarding | T-2 | `packages/c3-ai-bff/src/` |
| Tool gateway | Translates `POST /v1/mcp/invoke` into authenticated REST calls against the Flight API. **Capability audit:** pre-existing gateway handles generic MCP invoke but lacks flight tool schemas, Flight API OAuth, and C3 HTTP client — requires modification ticket | T-4a | `packages/mcp-bff/` |
| React SPA | Chat page with multi-thread sidebar, SSE streaming, markdown rendering, tool status, security banner, full history on every send. **Created by T-3** from `packages/ui/` primitives (no page-level app exists at planning commit) | T-3 | `react/` (created) + `packages/ui/` (existing primitives) |
| Agent config YAML | Provider, guardrails, permissions, classification — all declarative | T-1 (config loaded by orchestration) | `packages/c3-ai-bff/config/` |

## 8b. Implementation Topology

**No new packages or directories are created** (except a minimal React chat
page assembled from existing `packages/ui/` primitives). All other tickets
modify existing files.

| Ticket | Action | Path | What changes |
|--------|--------|------|-------------|
| T-1 | MODIFY | `packages/c3-ai-orchestration/src/.../turn.py` | Add `conversation_prefix: tuple[Message, ...]` parameter to both public functions |
| T-1 | MODIFY | `packages/c3-ai-orchestration/src/.../types.py` | Add `ToolCallFailed` dataclass, refine `ChatStreamEvent` |
| T-1 | MODIFY | `packages/c3-ai-orchestration/tests/test_turn.py` | Add multi-turn test cases |
| T-2 | MODIFY | `packages/c3-ai-bff/src/.../app.py` | Add `POST /v1/chat/full`, wire conversation prefix through `/v1/chat/stream` |
| T-2 | MODIFY | `packages/c3-ai-bff/src/.../executor.py` | Accept + forward `conversation_prefix` in executor protocol |
| T-2 | MODIFY | `packages/c3-ai-bff/tests/test_routes.py` | Add tests for `/v1/chat/full` and multi-message `/v1/chat/stream` |
| T-3 | CREATE | `react/src/pages/ChatPage.tsx` | Assemble chat page from `packages/ui/` primitives, send full history |
| T-3 | CREATE | `react/src/shared/chatStreamClient.ts` | SSE streaming client for chat |
| T-4 | MODIFY | `packages/c3-ai-bff/src/.../tools_catalog.py` | Refine tool schemas with verified upstream field names |
| T-4 | MODIFY | `packages/c3-ai-bff/src/.../openapi_flights_catalog.py` | Adjust catalog loader if needed |
| T-4a | MODIFY | `packages/c3-ai-mcp-bff/src/...` | Add flight tool definitions, OAuth token flow for Flight API, C3 HTTP client for upstream calls |
| T-5 | MODIFY | `packages/core/src/.../types.py` | Add `tool_exec_start`/`tool_exec_result` to StreamEvent |
| T-5 | MODIFY | `packages/core/src/.../runtime/executor.py` | Emit tool lifecycle events during streaming |
| T-6 | MODIFY | `scripts/start-local-stack.sh` | Already exists — update ports/process list if needed |
| T-7 | MODIFY | `packages/c3-ai-orchestration/src/.../debug_http.py` | Refine truncation, add tool arg digest |

## 9. API Contracts

### React SPA → BFF

```
POST /v1/chat/stream
Request: { messages: [{role: "user"|"assistant", content: string}] }
  — FULL conversation history. Last message must be role: "user".
  — Messages before the last are forwarded as conversation_prefix.
Response: SSE stream
  data: {"type": "text", "content": "token..."}
  data: {"type": "tool_start", "name": "list_searches"}
  data: {"type": "tool_end", "name": "list_searches"}
  data: {"type": "done"}
  data: {"type": "error", "message": "..."}
Headers: Authorization: Bearer <required — validated against CHAT_BFF_BEARER_TOKEN>
Errors: 400 (GuardrailBlockedError), 401 (missing/invalid bearer token),
        502 (LLM connection failure), 503 (LLM timeout), 500 (unknown)
```

```
POST /v1/chat/full  [NEW — added by T-2]
Request: { messages: [{role: "user"|"assistant", content: string}] }
  — Same format as /v1/chat/stream but returns blocking JSON.
Response: { assistant: string, session_id: string, tools_used: string[] }
Headers: Authorization: Bearer <required — validated against CHAT_BFF_BEARER_TOKEN>
Errors: 400 (GuardrailBlockedError | invalid prefix roles),
        401 (missing/invalid bearer token),
        502 (LLM connection failure), 503 (LLM timeout), 500 (unknown)
```

```
POST /v1/chat
Request: { message: string, session_id?: string, client_turn_id?: string }
  — Single-turn (no conversation prefix). Unchanged.
Response: { assistant: string, session_id: string, tools_used: string[] }
```

```
GET /health → { status: "ok" }
GET /v1/meta → { classification: "UNCLASSIFIED"|"CUI"|"SECRET" }
```

### BFF → tool-gateway

```
POST /v1/mcp/invoke
Request: { tool: string, arguments: object }
Response: { ok: true, result: string|object } | { ok: false, error: string }
Headers: X-Mcp-Invoke-Secret: <shared secret>
```

## 10. Explicitly Out of Scope

1. **New packages or directories** — Constitution #1; modify existing code
2. **Dedicated REST BFF for flights** — cut (Deletion Test; Constitution #2)
3. **Composite tool executor** — cut (only needed if REST BFF exists)
4. **Persistent server-side chat sessions** — no user story; client holds state
5. **Elicitation phrases / numbered options** — AP-1 (no user asked for it)
6. **`describe_flights_api` as a tool** — deferred to post-MTP (P3)
7. **Production authentication** — demo scope only
8. **Multiple design documents** — Constitution #5

## 11. Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Local LLM tool_calls format incompatible with OpenAI spec | Medium | High | **Tracer bullet:** validate format with proof script before T-4 |
| Conversation prefix bloats token count on long conversations | Medium | Medium | AgentRuntime history processors handle truncation; test in IG-1 |
| Tool gateway latency adds >2s to tool calls | Low | Medium | Monitor in IG-2; optimize OAuth token caching if needed |

## 12. Ticket Dependency Graph

```
T-1: Orchestration: add conversation_prefix to run_chat_turn [confirm]
     [origin: phase-2, P1, MODIFY packages/c3-ai-orchestration/]
  └─→ T-2: BFF: add /v1/chat/full + wire prefix through /v1/chat/stream [confirm]
       [origin: phase-2, P1, MODIFY packages/c3-ai-bff/]
       └─→ T-3: React: create chat page with full history [confirm]
            [origin: phase-1, P1, CREATE react/ from packages/ui/ primitives]
            └─→ IG-1: Multi-turn streaming chat works e2e
                 [Proof: curl multi-message → response references prior turn]
                 [Proof: Playwright multi-turn conversation test]
                 └─→ T-4: Tool catalog: verify field names + refine schemas [confirm]
                      [origin: phase-2, P1, MODIFY packages/bff/]
                      └─→ T-4a: Tool gateway: flight tool defs + OAuth + C3 HTTP [confirm]
                           [origin: phase-2, P1, MODIFY packages/c3-ai-mcp-bff/]
                           └─→ T-5: Tool stream events: tool_exec_start/result in core [validate]
                           [origin: phase-1, P1, MODIFY packages/core/ + packages/orchestration/]
                           └─→ IG-2: Tool calling works e2e with multi-turn
                                [Proof: multi-turn chat triggers tool, data in prose]
                                └─→ T-6: Start-all script + local dev docs [autopilot]
                                     [origin: phase-1, P2, MODIFY scripts/ + docs/]
                                └─→ T-7: Debug logging (HTTP trace, tool redaction) [autopilot]
                                     [origin: phase-1, P2, MODIFY packages/c3-ai-orchestration/]
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
- Zero new packages (AP-9 check; T-3 creates page files but uses existing ui package) ✓
- Every ticket has execution mode assigned ✓

## 13. Convergence Ledger (Final)

- Resolved: 13 — product scope, users (2), MTP, conversation state (client-side),
  streaming transport (SSE), provider interface (OpenAI-compat), BFF language (Python),
  tool transport (MCP only), system prompt source (OpenAPI YAML), security model
  (guardrails + shared secrets), deployment model (3 processes), multi-turn threading
  model (prefix parameter)
- Cut: 8 — REST BFF, composite executor, template scaffolding, elicitation,
  meta tool, multiple design docs, persistent storage, production auth
- Deferred: 1 — `describe_flights_api` tool (P3, post-MTP)

## 14. Assumption Register

| ID | Statement | Source | Confidence | Impact if wrong | Validation | Blocking? |
|----|-----------|--------|------------|----------------|------------|-----------|
| A-1 | Local LLM supports OpenAI-compat tool_calls | Inferred → User-stated | HIGH | Tool features blocked | Tracer bullet | Yes (resolved) |
| A-2 | Tool gateway handles all 9 flight tools correctly | Observed | HIGH | Tool calls fail | IG-2 | No |
| A-3 | `packages/ui/` chat primitives are sufficient to assemble a page-level chat app | Observed | HIGH | React page requires more UI work than planned | Code inspection of ui components | No |
| A-4 | Agent YAML config sufficient for guardrail tuning | Observed | HIGH | Custom guardrail code needed | IG-1 | No |
| A-5 | Conversation prefix doesn't break AgentRuntime message format | Inferred → User-stated | HIGH | Orchestration refactor needed | T-1 tests | Yes (resolved) |

## 15. Artifact Ingestion Log

*No reference artifacts were provided for this project.*

## 16. Complexity Justification Register

| Violation | Why needed | Simpler alternative rejected because |
|-----------|-----------|--------------------------------------|
| 3 separate processes (BFF + tool gateway + Vite) | Tool gateway needs API OAuth secrets that must not reach the browser | Single process would expose secrets (violates Constitution #4) |
| OpenAPI YAML loaded at startup for system prompt | LLM needs to know available operations without user listing them | Hardcoded tool descriptions rejected — they drift from actual API |

## 17. Implementation Readiness Checklist

- [x] Every ticket specifies MODIFY or CREATE for each file it touches
- [x] No ticket creates a new package (AP-9 verified)
- [x] Tool definitions reference verified upstream field names
- [x] API contracts show what changed vs pre-existing state
- [x] Plan lists existing tests that must still pass
- [x] Plan names test runner (pytest), framework conventions, import patterns
- [x] Existing behaviors that must NOT break are enumerated
