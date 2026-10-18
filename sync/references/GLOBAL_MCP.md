# Global MCP Configuration Map

Authoritative target list for sync. Master store: `~/.secrets/mcp.json` (never edited by downstream tools), plus any `~/.secrets/mcp.d/*.json` drop-ins.
Start a new master from [mcp.example.json](mcp.example.json).

## Target table

| Tool / Platform | Config Path | Root Key | Transports Supported | Toggle Approach |
| :--- | :--- | :--- | :--- | :--- |
| **Master store** | `~/.secrets/mcp.json` | `mcpServers` | any | Set `enabled: true/false`; re-run sync |
| **Claude Code (CLI)** — user scope | `~/.claude.json` | root `mcpServers` | stdio, http, sse | Remove entry (no `enabled` field support) |
| **Claude Code (CLI)** — local scope | `~/.claude.json` | `projects["<abs-path>"].mcpServers` | stdio, http, sse | Remove entry |
| **Claude Code (CLI)** — project scope | `<repo>/.mcp.json` | `mcpServers` | stdio, http, sse | Remove entry; commit to VCS |
| **Claude Code — settings file** | `~/.claude/settings.json` | **NEVER `mcpServers`** | N/A | Prune this key defensively — schema violation |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | `mcpServers` | stdio only (http via `mcp-remote`) | Remove entry |
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` | stdio, http, sse | Remove entry or set `"enabled": false` |
| **Cline (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | `mcpServers` | stdio, http, sse | `"enabled": false` supported |
| **Roo Code (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` | `mcpServers` | stdio, http, sse | `"enabled": false` supported |
| **Zed Editor** | `~/.config/zed/settings.json` | `context_servers` | stdio | Remove entry |
| **Codex** (app, CLI, IDE), personal only | `~/.codex/config.toml` | `mcp_servers` (TOML tables) | stdio, http | Only servers marked `"personal": true` and with no `${VAR}`; no `type`, headers are `http_headers` |
| **OpenCode** | `~/.config/opencode/opencode.json` | `mcp` | stdio, http | `"enabled": false` supported; `command` is an **array** |
| **pi** (`pi_agent_rust`) | `~/.pi/agent/mcp.json` and `~/.gateway-pi/mcp.json` | `mcpServers` | stdio, http, sse | Remove entry; run `mcp_sync.py` (see mcp.md) |

## Secret references per target

The master holds `${VAR}` placeholders only. `mcp_sync.py` writes each target's own reference form.
The values live in `~/.config/secrets/work.env` (mode 600), never in a tool config.

| Target | Form written | Where the value comes from |
| :--- | :--- | :--- |
| Claude Code | `${VAR}` | Shell env of the process that starts `claude` |
| OpenCode | `{env:VAR}` | Shell env of the opencode process or service |
| pi | `$ENV:VAR` (whole value only) | Shell env of the process that starts pi |
| Cursor, Claude Desktop | `/bin/zsh -c 'set -a; . "$HOME/.config/secrets/work.env"; exec ...'` | The wrapper sources `work.env`, because Dock-launched apps do not inherit shell env |

Codex is not in this table: it never receives a secret reference.

A header that needs a prefix, such as `Bearer <token>`, is built once in `work.env` (for example `REMOTE_MCP_AUTH`) so every target can use a whole-value reference.
A literal in a secret-named field is refused, never written.

## Transport whitelist per tool

- **Claude Desktop**: stdio only, so a `url` server is proxied through `npx mcp-remote`.
- **Zed**: stdio only; skip URL servers.
- **All others**: full stdio + http + sse.

## Required canonical schema for each target entry

Always emit `type` explicitly; newer tools require it.

```jsonc
// stdio
{ "type": "stdio", "command": "<bin>", "args": ["..."], "env": { "K": "v" } }

// http (preferred over sse)
{ "type": "http", "url": "https://...", "headers": { "Authorization": "Bearer ..." } }

// sse (legacy — deprecated in Claude Code)
{ "type": "sse", "url": "https://...", "headers": { "..." : "..." } }
```

Do NOT emit: `enabled`, `allowedTools`, or any other field not in the tool's public schema. These are sync MCP extensions and live only in the master store.

## Claude Code specifics

- Version 2.1+ supports `-t/--transport http|sse|stdio`. HTTP is the modern streamable transport (returns SSE-framed single response); SSE is legacy and deprecated.
- `~/.claude.json` is a multi-purpose state file (project history, OAuth, caches). Sync must be **surgical**: read → mutate only `.mcpServers` or `.projects["<abs-path>"].mcpServers` → write. Never overwrite the whole file.
- `~/.claude/settings.json` is for hooks, model, permissions — not MCP. Placing `mcpServers` there causes schema validation to fail and silently breaks user-scope MCP loading.
- Approval flags in settings (valid there):
  - `enableAllProjectMcpServers: true` — auto-approve all `.mcp.json` servers
  - `enabledMcpjsonServers: ["memory", "github"]` — allowlist specific project servers
  - `disabledMcpjsonServers: ["filesystem"]` — blocklist specific project servers

## Verification commands

```bash
# Health check (Claude Code)
claude mcp list

# Per-server parse check
claude mcp get <name>

# End-to-end subprocess test — proves tool invocation works
claude -p "Use <server> MCP to run <toolname> with ..." \
  --allowedTools "mcp__<server>__<toolname>" \
  --output-format json
```

Successful output has `"subtype":"success"` and a non-empty `"result"`.

## Safety checklist before every sync

1. Dry run: `python3 ~/.skills/sync/mcp_sync.py --dry-run` (lists key paths, no values). Real runs write a `.bak.<ts>` copy first.
2. Validate master: `jq empty ~/.secrets/mcp.json`.
3. Confirm no `mcpServers` key will leak into `~/.claude/settings.json`.
4. After sync: `claude mcp list` and at least one subprocess E2E test.
