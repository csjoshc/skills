# Global MCP Configuration Map

**Summary:** Native config locations for [named-consumer reconciliation](../mcp.md#1-named-consumer-reconciliation), not a bulk-write target list.
Definitions live in `~/.secrets/mcp.json` and private-pack `~/.secrets/mcp.d/*.json` drop-ins.
Start a new master from [mcp.example.json](mcp.example.json).
Inspect the effective config root before editing; wrapper profiles can use a different root from the base CLI.

## Target table

| Tool / Platform | Config Path | Root Key | Transports Supported | Toggle Approach |
| :--- | :--- | :--- | :--- | :--- |
| **Master store** | `~/.secrets/mcp.json` | `mcpServers` | any | Change intent, then reconcile each affected consumer |
| **Devin** | `~/.config/devin/mcp_config.json`; project `.devin/mcp_config.json` | `mcpServers` | stdio, http | Preserve native permissions and inspect project overrides |
| **Claude Code (CLI)** — user scope | `~/.claude.json` | root `mcpServers` | stdio, http, sse | Remove entry (no `enabled` field support) |
| **Claude Code (CLI)** — local scope | `~/.claude.json` | `projects["<abs-path>"].mcpServers` | stdio, http, sse | Remove entry |
| **Claude Code (CLI)** — project scope | `<repo>/.mcp.json` | `mcpServers` | stdio, http, sse | Remove entry; commit to VCS |
| **Claude Code — settings file** | `~/.claude/settings.json` | **NEVER `mcpServers`** | N/A | Prune this key defensively — schema violation |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | `mcpServers` | stdio only (http via `mcp-remote`) | Remove entry |
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` | stdio, http, sse | Remove entry or set `"enabled": false` |
| **VS Code** | `~/Library/Application Support/Code/User/mcp.json` | `servers` | stdio, http | Reconcile the selected user-data directory |
| **OMP** | `~/.omp/agent/mcp.json`, or the selected `PI_CODING_AGENT_DIR` | `mcpServers` | stdio, http | Reconcile base and wrapper profiles separately |
| **Cline (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | `mcpServers` | stdio, http, sse | `"enabled": false` supported |
| **Roo Code (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` | `mcpServers` | stdio, http, sse | `"enabled": false` supported |
| **Zed Editor** | `~/.config/zed/settings.json` | `context_servers` | stdio | Remove entry |
| **Codex** (app, CLI, IDE), personal only | `~/.codex/config.toml` | `mcp_servers` (TOML tables) | stdio, http | Preserve personal bindings; exclude work MCPs and work credential references |
| **OpenCode** | `~/.config/opencode/opencode.json` | `mcp` | stdio, http | `"enabled": false` supported; `command` is an **array** |

## Secret references per target

Definitions contain references and explicit `credentialSource: work|personal` ownership.
For file-backed credentials, use [scoped startup](../mcp.md#scoped-startup-for-an-individually-reconciled-consumer) so only named variables reach the child process.
Keep values in the owning private store, not native config, parent shell exports or a whole-file sourcing wrapper.
Preserve native OAuth and account stores rather than translating them into file-backed credentials.
Codex receives no work credentials.

## Transport whitelist per tool

- **Claude Desktop**: these local entries use stdio; use the reviewed installed bridge for remote servers.
- **Zed**: stdio only; skip URL servers.
- **Other consumers**: verify transport support against the installed native schema.

## Native schema

Use the installed consumer's schema, not one shared entry shape.
For example, OpenCode local entries use a command array; Claude-style stdio entries use `command` and `args`.
Keep definition metadata, including credential ownership, out of native entries.
See [target-specific formats](../mcp.md#target-specific-formats).

## Claude Code specifics

- Version 2.1+ supports `-t/--transport http|sse|stdio`. HTTP is the modern streamable transport (returns SSE-framed single response); SSE is legacy and deprecated.
- `~/.claude.json` is a multi-purpose state file (project history, OAuth, caches). Sync must be **surgical**: read → mutate only `.mcpServers` or `.projects["<abs-path>"].mcpServers` → write. Never overwrite the whole file.
- `~/.claude/settings.json` is for hooks, model, permissions — not MCP. Placing `mcpServers` there causes schema validation to fail and silently breaks user-scope MCP loading.
- Approval flags in settings (valid there):
  - `enableAllProjectMcpServers: true` — auto-approve all `.mcp.json` servers
  - `enabledMcpjsonServers: ["memory", "github"]` — allowlist specific project servers
  - `disabledMcpjsonServers: ["filesystem"]` — blocklist specific project servers

## Verification

`claude mcp list` checks discovery/connectivity; `claude mcp get <name>` checks the selected definition.
Neither proves an authenticated native tool call.
A successful CLI exit or non-empty assistant summary is also insufficient: verify the actual requested tool result, expected identity and final binding.
Follow the [reconciliation workflow](../mcp.md#1-named-consumer-reconciliation) for entry-level rollback, missing-credential checks, native activation and retirement gates.
