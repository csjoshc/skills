# Ticket Pack: Enterprise Chat Agent with Multi-Turn Tool Calling

All tickets modify existing packages. See
[brownfield-context.md](brownfield-context.md) for the pre-existing codebase
state and [prd.md](prd.md) §8b for the implementation topology.

---

---
id: T-1
title: "Orchestration: Add conversation_prefix to run_chat_turn"
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
    path: packages/c3-ai-orchestration/src/c3_ai_orchestration/turn.py
    test: false
    description: "Add conversation_prefix parameter, insert prefix into thread messages"
  - action: MODIFY
    path: packages/c3-ai-orchestration/src/c3_ai_orchestration/types.py
    test: false
    description: "Add ToolCallFailed type, frozen trace dataclasses"
  - action: MODIFY
    path: packages/c3-ai-orchestration/tests/test_turn.py
    test: true
    description: "New test cases for conversation_prefix"
  - action: MODIFY
    path: packages/c3-ai-orchestration/tests/support/scripted_provider.py
    test: true
    description: "Extend for multi-turn"
Read-First:
  - packages/c3-ai-orchestration/src/c3_ai_orchestration/turn.py
  - packages/c3-ai-orchestration/tests/test_turn.py
  - packages/core/src/agent_core/config/manager.py
Exemplar-Files:
  - packages/c3-ai-orchestration/src/c3_ai_orchestration/turn.py
  - packages/c3-ai-orchestration/tests/support/scripted_provider.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/c3-ai-orchestration/tests/ -v"
---
# T-1: Orchestration — Add conversation_prefix to run_chat_turn

## Scope
MODIFY `packages/c3-ai-orchestration/src/.../turn.py` — add
`conversation_prefix: tuple[Message, ...] = ()` parameter to both
`run_chat_turn()` and `run_chat_turn_stream()`. Prefix messages are
inserted between the system prompt and the latest user message in the
RuntimeState message tuple.

## User Story
As a BFF developer, I want `run_chat_turn` to accept prior conversation
messages so the LLM has multi-turn context without the BFF managing thread
state itself.

## Acceptance Criteria
- [ ] Given `conversation_prefix=((user, "hello"), (assistant, "Hi!"))` and
  `user_text="what did I just say?"`, when called with a scripted provider, then
  the thread messages include all three messages in order after the system prompt
- [ ] Given `run_chat_turn_stream()` with prefix, when called, then it yields
  `ChatStreamEvent` objects and the final assistant text uses prior context
- [ ] Given a prompt injection in the prefix, when passed through, then the
  input guardrail blocks it via `pipeline.filter_input()` on the latest user
  text before RuntimeState construction
- [ ] Given a tool call, when `tool_executor` dispatches it, then
  `pipeline.check_tool_call()` is invoked as a tool guardrail hook before
  execution proceeds
- [ ] Given a guardrail block during orchestration, when the exception
  propagates, then it is re-thrown to the BFF (not caught and suppressed)
  and the BFF returns a structured error response
- [ ] Given `AGENT_DEBUG_LLM_PAYLOAD=1`, when guardrails run, then a
  diagnostic stderr callback logs guardrail evaluation results
- [ ] Given a tool call with prefix, when `tool_executor` is provided, then the
  runtime executes the tool with the full conversation visible to the LLM
- [ ] Given empty `conversation_prefix=()`, then behavior is identical to
  pre-existing single-turn (regression)

## Verify

```bash
uv run pytest packages/c3-ai-orchestration/tests/test_turn.py -k "multi_turn or conversation_prefix" -v
```

## Technical Notes
- `conversation_prefix` is a tuple of `Message` objects (user + assistant roles only)
- System prompt is always first; prefix follows; latest user message is last
- The BFF is responsible for validating prefix roles (no system messages in prefix)
- `ChatTurnConfig` takes `config_path: str` and `environment: str`. Orchestration
  calls `load_config(config_path, environment=environment)` to get `AgentConfig`.
  Classification, permissions, and guardrail settings come from the loaded config,
  not hardcoded. BFF passes config path from `settings.AGENT_CONFIG_PATH` env var.
- `on_tool_event: Callable[[ToolEvent], Awaitable[None]] | None = None` — async
  callback, awaited by orchestration. Not sync `Callable[[ToolEvent], None]`.
- Trace dataclasses in `types.py` are **frozen**. Fields: `arguments_summary: str`
  (sorted keys digest, not raw dict), `result_summary: str` (truncated, not raw),
  `backend: Literal['mcp', 'local']`. No raw argument values in trace objects.

---

---
id: T-2
title: "BFF: Add /v1/chat/full + Wire Conversation Prefix"
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
    path: packages/c3-ai-bff/src/c3_ai_bff/app.py
    test: false
    description: "New endpoint, prefix wiring in existing stream endpoint"
  - action: MODIFY
    path: packages/c3-ai-bff/src/c3_ai_bff/executor.py
    test: false
    description: "ChatExecutor and StreamChatExecutor accept conversation_prefix"
  - action: MODIFY
    path: packages/c3-ai-bff/tests/test_routes.py
    test: true
    description: "Test /v1/chat/full, multi-message stream"
  - action: MODIFY
    path: packages/c3-ai-bff/tests/test_default_executor_parity.py
    test: true
    description: "Verify prefix forwarding"
Read-First:
  - packages/c3-ai-bff/src/c3_ai_bff/app.py
  - packages/c3-ai-bff/src/c3_ai_bff/executor.py
Exemplar-Files:
  - packages/c3-ai-bff/src/c3_ai_bff/app.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/c3-ai-bff/tests/test_routes.py -v"
---
# T-2: BFF — Add /v1/chat/full + Wire Conversation Prefix

## Scope
MODIFY `packages/c3-ai-bff/src/.../app.py` — add `POST /v1/chat/full`
endpoint (blocking JSON, accepts full messages array). Modify
`POST /v1/chat/stream` to forward messages[:-1] as conversation_prefix to
the orchestration layer.

## Acceptance Criteria
- [ ] Given `POST /v1/chat/full` with multi-message payload, then response
  references prior context
- [ ] Given `POST /v1/chat/stream` with same payload, then SSE events stream
  with context-aware response
- [ ] Given messages array with system role in prefix, then 400 error
- [ ] Given `POST /v1/chat` (single message, no prefix), then unchanged (regression)
- [ ] Given a `GuardrailBlockedError`, then HTTP 400 with structured JSON error
- [ ] Given an LLM connection failure, then HTTP 502
- [ ] Given missing `Authorization: Bearer <token>`, then 401
- [ ] Given LLM returns empty text after tool calls, then synthesized summary

## Verify

```bash
uv run pytest packages/c3-ai-bff/tests/test_routes.py -k "chat_full or multi_message" -v
```

## Technical Notes
- SSE streaming uses native FastAPI `StreamingResponse` with manual
  `data: {json}\n\n` framing. Do NOT add `sse-starlette` — Constitution #1.
- When model returns empty `assistant_text` after tool calls, BFF calls
  `assistant_text_for_user(tool_traces)` to synthesize a summary.
- Error mapping: `GuardrailBlockedError` → 400, `ChatTurnError` with LLM
  connection detection → 502, LLM timeout → 503, unknown → 500.

---

---
id: T-3
title: "React: Create Chat Page with Full Conversation History"
Stage: NEW
Type: feature
Priority: P1
Origin: phase-1
Mode: confirm
Depends-On: [T-2]
Blocks: [IG-1]
Gate: IG-1
Files:
  - action: CREATE
    path: react/src/pages/ChatPage.tsx
    test: false
    description: "Assemble chat page from packages/ui/ primitives"
  - action: CREATE
    path: react/src/shared/chatStreamClient.ts
    test: false
    description: "SSE streaming client for chat"
  - action: CREATE
    path: react/src/shared/chatStreamClient.test.ts
    test: true
    description: "Streaming client tests"
  - action: CREATE
    path: e2e/live-llm-agent-chat.spec.ts
    test: true
    description: "Multi-turn Playwright test"
Read-First:
  - packages/ui/src/components/
  - packages/ui/src/index.ts
Exemplar-Files:
  - packages/ui/showcase/pages/
Assumptions-Validated: []
Regression-Baseline: []
---
# T-3: React — Create Chat Page with Full Conversation History

## Scope
CREATE a minimal chat page using existing `packages/ui/` component primitives.
The page sends the full conversation history on every request.

## Acceptance Criteria
- [ ] Given the chat page, when user sends message 3, then fetch body contains
  all 3 user messages + 2 assistant messages
- [ ] Given streaming mode, then assistant references prior turns
- [ ] Given blocking mode toggle via `/v1/chat/full`, then full context used
- [ ] Given `/v1/meta` returns classification, then security banner correct (regression)

## Verify

```bash
cd react && npx vitest run --reporter=verbose chatStreamClient
```

---

---
id: IG-1
title: "Integration Gate: Multi-Turn Streaming Chat Works E2E"
Stage: NEW
Type: integration-gate
Depends-On: [T-1, T-2, T-3]
Blocks: [T-4, T-5]
Validates: [T-1, T-2, T-3]
Expected-Test-Artifacts:
  - path: packages/c3-ai-bff/tests/test_routes.py
    min_tests: 8
    scope: "health, meta, chat, chat/full, chat/stream multi-message, auth 401, guardrail error, regression"
  - path: packages/c3-ai-orchestration/tests/test_turn.py
    min_tests: 6
    scope: "single-turn, multi-turn prefix, empty prefix, tool call with prefix, guardrail block, stream events"
---
# IG-1: Multi-Turn Streaming Chat Works End-to-End

## Flows Under Test
- Given BFF + LLM running, when user sends "hello" then follows up with
  "what did I just say?", then SSE stream delivers context-aware response
- Given a guardrail-blocked input in a multi-turn conversation, then the
  UI shows an error without losing prior messages

## Proof Artifacts (required)
- [ ] curl transcript: multi-message `POST /v1/chat/stream` → SSE events
- [ ] Playwright run: multi-turn conversation

## Verified by
CI job or human reviewer (not the implementing agent)

---

---
id: T-4
title: "Tool Catalog: Verify Field Names + Refine Schemas"
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
    path: packages/c3-ai-bff/src/c3_ai_bff/tools_catalog.py
    test: false
    description: "Refine schemas with verified upstream field names"
  - action: MODIFY
    path: packages/c3-ai-bff/src/c3_ai_bff/openapi_flights_catalog.py
    test: false
    description: "Adjust catalog loader if needed"
  - action: MODIFY
    path: packages/c3-ai-bff/tests/test_tools_catalog.py
    test: true
    description: "Verify field name correctness"
Read-First:
  - packages/c3-ai-bff/src/c3_ai_bff/tools_catalog.py
  - openapi/flights-api.yaml
Exemplar-Files:
  - packages/c3-ai-bff/src/c3_ai_bff/tools_catalog.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/c3-ai-bff/tests/test_tools_catalog.py -v"
---
# T-4: Tool Catalog — Verify Field Names + Refine Schemas

## Scope
MODIFY `packages/c3-ai-bff/src/.../tools_catalog.py` — verify each tool's
JSON schema against actual upstream API field names (`fromAirport`/`toAirport`/
`outboundDate`, NOT `origin`/`destination`/`departure_date`).

## Acceptance Criteria
- [ ] Given `create_search` schema, then required fields are `fromAirport`,
  `toAirport`, `outboundDate`
- [ ] Given `openapi/flights-api.yaml`, then catalog includes all non-OAuth
  operations within char limit
- [ ] Given `MCP_INVOKE_BASE_URL` set, then MCP client POSTs with correct
  headers and parses `{ ok: true, result: ... }` format

## Verify

```bash
uv run pytest packages/c3-ai-bff/tests/test_tools_catalog.py -v
```

---

---
id: T-4a
title: "Tool Gateway: Add Flight Tool Definitions + OAuth"
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
    path: packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/app.py
    test: false
    description: "Add flight tool routes"
  - action: MODIFY
    path: packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/flight_tools.py
    test: false
    description: "Flight tool definitions + OAuth client"
  - action: MODIFY
    path: packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/settings.py
    test: false
    description: "Add OAuth/Flight API config fields"
  - action: MODIFY
    path: packages/c3-ai-mcp-bff/tests/test_flight_tools.py
    test: true
    description: "Flight tool tests"
Read-First:
  - packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/app.py
  - packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/settings.py
  - packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/flight_tools.py
Exemplar-Files:
  - packages/c3-ai-mcp-bff/src/c3_ai_mcp_bff/app.py
  - packages/c3-ai-bff/src/c3_ai_bff/settings.py
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/c3-ai-mcp-bff/tests/ -v"
---
# T-4a: Tool Gateway — Add Flight Tool Definitions + OAuth

## Scope
MODIFY `packages/c3-ai-mcp-bff/` — add flight-specific tool definitions,
OAuth token flow for the Flight API, and C3 HTTP client for upstream calls.

## Acceptance Criteria
- [ ] Given `POST /v1/mcp/invoke` with `tool="list_searches"`, then gateway
  authenticates via OAuth and returns `{ ok: true, result: [...] }`
- [ ] Given Flight API field names, then gateway passes `fromAirport`/
  `toAirport`/`outboundDate` exactly
- [ ] Given OAuth token expires, then gateway refreshes before retrying
- [ ] Given Flight API unreachable, then `{ ok: false, error: "upstream unreachable" }`

---

---
id: T-5
title: "Core: Tool Lifecycle Stream Events"
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
    path: packages/core/src/agent_core/types.py
    test: false
    description: "Extend StreamEvent type literal"
  - action: MODIFY
    path: packages/core/src/agent_core/runtime/executor.py
    test: false
    description: "Emit tool lifecycle events during streaming"
  - action: CREATE
    path: packages/core/src/agent_core/tool_call_wire.py
    test: false
    description: "Synthetic tool-call parser for JSON-in-text fallback (A-1)"
  - action: MODIFY
    path: packages/core/tests/test_runtime/test_executor.py
    test: true
    description: "Test new events"
  - action: MODIFY
    path: packages/c3-ai-orchestration/src/c3_ai_orchestration/turn.py
    test: false
    description: "Map new event types to ChatStreamEvent tool_start/tool_end"
Assumptions-Validated: [A-1]
Regression-Baseline:
  - "uv run pytest packages/core/tests/test_runtime/test_executor.py -v"
---
# T-5: Core — Tool Lifecycle Stream Events

## Scope
MODIFY `packages/core/src/.../types.py` — add `tool_exec_start` and
`tool_exec_result` to `StreamEvent.type` literal. CREATE
`tool_call_wire.py` for synthetic tool-call parsing (Qwen/Ollama fallback).

## Acceptance Criteria
- [ ] Given streaming with tools, then `tool_exec_start` event yielded
- [ ] Given tool execution completes, then `tool_exec_result` event yielded
- [ ] Given tool execution fails, then `tool_exec_error` included
- [ ] Given no tool calls, then no tool lifecycle events (regression)
- [ ] **[Validates A-1]** Given local LLM, when prompted with tool definition,
  then model emits parseable tool_calls (or JSON-in-text fallback handles it)

## Verify

```bash
uv run pytest packages/core/tests/test_runtime/test_executor.py -k "tool_exec" -v && \
  uv run pytest packages/c3-ai-orchestration/tests/test_turn.py -k "tool_stream" -v
```

---

---
id: IG-2
title: "Integration Gate: Tool Calling Works E2E with Multi-Turn"
Stage: NEW
Type: integration-gate
Depends-On: [T-4, T-4a, T-5]
Blocks: [T-6, T-7]
Validates: [T-4, T-4a, T-5]
Expected-Test-Artifacts:
  - path: packages/c3-ai-bff/tests/test_tools_catalog.py
    min_tests: 4
    scope: "field names, catalog loading, char limit, MCP client parsing"
  - path: packages/core/tests/test_runtime/test_executor.py
    min_tests: 4
    scope: "tool_exec_start, tool_exec_result, tool error, no-tool regression"
---
# IG-2: Tool Calling Works End-to-End with Multi-Turn

## Flows Under Test
- Given all processes running, when user asks "list my flight searches" in
  multi-turn, then LLM calls tool, gateway returns data, assistant responds
- Given SSE mode, then `tool_start` and `tool_end` events observed

## Proof Artifacts (required)
- [ ] curl transcript: multi-turn chat → tool_start → tool_end → text → done
- [ ] Server log showing MCP invoke with redacted args digest

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
    description: "Update process list if needed"
  - action: MODIFY
    path: docs/local-dev.md
    test: false
    description: "Add multi-turn testing instructions"
  - action: MODIFY
    path: docs/secrets-and-env.md
    test: false
    description: "Document any new env vars"
Assumptions-Validated: []
Regression-Baseline: []
---
# T-6: Start-All Script + Local Dev Runbook

## Scope
MODIFY `scripts/start-local-stack.sh` and `docs/local-dev.md`.

## Acceptance Criteria
- [ ] Given `.env` with required vars, then `start-local-stack.sh` starts all processes
- [ ] Given `docs/local-dev.md`, then new developer can chat within 10 minutes
- [ ] Given Ctrl+C, then all child processes cleaned up

## Verify

```bash
bash scripts/start-local-stack.sh &
sleep 5 && curl -sf http://localhost:8000/health | jq -e '.status == "ok"'
kill %1 2>/dev/null; wait 2>/dev/null
```

---

---
id: T-7
title: "Debug Logging"
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
    path: packages/c3-ai-orchestration/src/c3_ai_orchestration/debug_http.py
    test: false
    description: "Add LLM payload debug, refine truncation"
  - action: MODIFY
    path: packages/c3-ai-orchestration/src/c3_ai_orchestration/log_redaction.py
    test: false
    description: "Add tool_arguments_digest()"
Assumptions-Validated: []
Regression-Baseline:
  - "uv run pytest packages/c3-ai-orchestration/tests/ -k 'debug_http or log_redaction' -v"
---
# T-7: Debug Logging

## Scope
MODIFY `packages/c3-ai-orchestration/src/.../debug_http.py` — refine
`APP_DEBUG_HTTP` middleware. Add `AGENT_DEBUG_LLM_PAYLOAD` for payload dumping.
Tool argument redaction (sorted keys + SHA-256 digest).

## Acceptance Criteria
- [ ] Given `APP_DEBUG_HTTP=1`, then request/response logged to stderr
- [ ] Given default, then only truncated user message in INFO logs
- [ ] Given a tool call, then sorted keys + SHA-256 digest in logs (not raw values)

## Verify

```bash
uv run pytest packages/c3-ai-orchestration/tests/ -k "debug_http or log_redaction" -v
```

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
- Given `start-local-stack.sh`, then all processes start and `/health` returns 200
- Given full stack, then Playwright multi-turn chat + tool call completes
- Given `APP_DEBUG_HTTP=1`, then debug output on stderr without secrets

## Proof Artifacts (required)
- [ ] Playwright run output (multi-turn chat + tool call)
- [ ] stderr log snippet showing debug output with redacted tool args

## Verified by
CI job or human reviewer
