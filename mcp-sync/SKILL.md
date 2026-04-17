---
name: mcp-sync
description: >-
  Synchronizes and audits Model Context Protocol (MCP) configurations across multiple
  IDEs, CLI agents, and desktop apps. Uses ~/.secrets/mcp.json as the master store.
  Supports global syncing, project-specific MCP enabling, and toggling specific
  MCP servers across all platforms. Use when standardizing MCP configs, enabling
  or disabling MCP servers, or onboarding MCP settings in new projects.
---

# MCP Sync & Toggle

**Version:** 2.0.0

## Context
MCP configurations are fragmented across different tools. This skill unifies them using `~/.secrets/mcp.json` as the authoritative source, then projects entries into each tool's native format — **not a blind copy**. Tool-specific schemas, file locations, and validation rules must be respected or the tool will silently reject the whole config.

## Master store schema (`~/.secrets/mcp.json`)

```json
{
  "mcpServers": {
    "<name>": {
      "type": "http" | "sse" | "stdio",
      "url": "...",               // http/sse only
      "headers": { ... },         // http/sse only
      "command": "...",           // stdio only
      "args": [ ... ],            // stdio only
      "env": { ... },             // stdio only
      "enabled": true | false,    // mcp-sync extension — NOT synced to targets
      "allowedTools": [ ... ]     // mcp-sync extension — NOT synced to targets
    }
  }
}
```

`enabled` and `allowedTools` are **mcp-sync extensions**. They must be stripped before writing to any target config — most tools' JSON schemas reject unknown fields or load a schema-invalid file as empty.

## Critical rules (learned the hard way)

1. **Claude Code user-scope MCPs live in `~/.claude.json` at the root `mcpServers` key — NOT in `~/.claude/settings.json`.** Putting `mcpServers` into `settings.json` is a documented schema violation (per [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)) and will cause the entire settings file to fail validation, which in turn prevents any user-scope MCPs from loading. Symptom: `claude mcp list` shows only claude.ai-hosted connectors; `claude mcp get <name>` returns "No MCP server found". Fix: delete the `mcpServers` key from `settings.json`.

2. **Always include an explicit `type` field on target entries.** `stdio`/`http`/`sse`. Newer Claude Code versions require it; older ones tolerate its absence for stdio but not for URL transports.

3. **Strip mcp-sync extensions (`enabled`, `allowedTools`) when writing to any target.** These are not part of the standard MCP server schema. Keep them only in the master store.

4. **A disabled server (`enabled: false` in master) means "omit from target entirely."** Do not emit `{"enabled": false}` into a target's config.

5. **Surgical writes only for multi-purpose files.** `~/.claude.json` and `~/.claude/settings.json` hold far more than MCP config (project history, OAuth, hooks, model prefs). Read → mutate only the MCP-relevant key → write. Never overwrite the whole file.

6. **Never put `mcpServers` in `~/.claude/settings.json`.** Explicitly prune it during every sync as a safety net, even if the skill didn't put it there.

## Claude Code scope model (authoritative)

| Scope | File | Key path | Use for |
| --- | --- | --- | --- |
| Managed | `/Library/Application Support/ClaudeCode/managed-mcp.json` (macOS) | `mcpServers` | IT-deployed org policy |
| User | `~/.claude.json` | root `mcpServers` | Personal, across all projects |
| Project | `<repo>/.mcp.json` | `mcpServers` | Shared with team via VCS |
| Local | `~/.claude.json` | `projects["<abs-path>"].mcpServers` | Personal, single project |
| Plugin | plugin's `.mcp.json` or inline in `plugin.json` | `mcpServers` | Bundled with a plugin |

Precedence when the same name appears in multiple scopes: **Local → Project → User → Plugin → claude.ai connectors**.

## Standard workflows

### 1. Full sync (master → all targets)

1. Read `~/.secrets/mcp.json`.
2. Filter: keep only entries where `enabled != false`.
3. For each entry, produce a clean copy without `enabled` / `allowedTools`, and ensure `type` is explicit.
4. For each target in [GLOBAL_MCP.md](references/GLOBAL_MCP.md):
   - Read current target JSON (preserve unrelated keys).
   - Apply target-specific transform (root key, transport whitelist, etc.).
   - Write back surgically using `jq` or equivalent — never overwrite the whole file.
5. Run verification commands (§Verification).

### 2. Toggle a server

- **Global disable:** set `enabled: false` in `~/.secrets/mcp.json`, then re-run full sync. Sync removes the entry from all targets.
- **Global enable:** set `enabled: true` (or remove the field), re-run sync.
- **Project-only override:** add/remove the entry in the project's `.mcp.json` (or `projects["<abs-path>"].mcpServers` for a personal local-scope override). Do not modify the master.

### 3. Project onboarding

- If the repo needs a committed MCP config, create `.mcp.json` at the project root (user must approve once per project via Claude Code's trust dialog).
- If it needs a personal-only MCP for this repo, add under `~/.claude.json → projects["<abs-path>"].mcpServers`.
- For non-Claude tools (Gemini CLI, OpenCode), see target-specific paths in [GLOBAL_MCP.md](references/GLOBAL_MCP.md).
- Add project-local personal configs (`.claude/settings.local.json`, `.gemini/mcp_config.json`) to `.gitignore`.

## Target-specific transforms

### Claude Code (`~/.claude.json`)
- Key: root `.mcpServers`
- Schema: official — `type` + (`command`/`args`/`env` for stdio | `url`/`headers` for http/sse)
- Strip: `enabled`, `allowedTools`
- Also: ensure `~/.claude/settings.json` has NO `mcpServers` key (schema violation).

Example jq sync snippet (safe pattern):

```bash
jq '
  .mcpServers as $m |
  [ $m | to_entries[] | select(.value.enabled != false) |
    { key: .key,
      value: (.value
        | del(.enabled, .allowedTools)
        | if has("url") then
            (if has("type") then . else . + {"type":"http"} end)
          elif has("command") then
            (if has("type") then . else . + {"type":"stdio"} end)
          else . end) }
  ] | from_entries
' ~/.secrets/mcp.json > /tmp/clean_mcp.json

jq --slurpfile clean /tmp/clean_mcp.json \
  '.mcpServers = $clean[0]' ~/.claude.json > ~/.claude.json.tmp \
  && mv ~/.claude.json.tmp ~/.claude.json

# Belt-and-braces: ensure settings.json never holds mcpServers
jq 'del(.mcpServers)' ~/.claude/settings.json > ~/.claude/settings.json.tmp \
  && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

### Claude Desktop
- Stdio-only. Skip any server with `url` (http/sse not supported).
- File: `~/Library/Application Support/Claude/claude_desktop_config.json`, root key `mcpServers`.

### Cursor, Cline, Roo, Gemini CLI
- Root key `mcpServers`. Stdio + URL generally supported; check tool docs per major-version change.

### Zed
- Root key `context_servers` (different!).

### OpenCode
- Root key `mcp`. Uses `"type": "local"` + `"command": ["..."]` (array, not string).

## Verification

Run ALL of the following after a sync — pure file-write success is not proof.

1. `claude mcp list` — every enabled server must show "✓ Connected". "Failed to connect" means the entry is valid but the runtime isn't working (docker daemon, network, VPN, token, etc.).
2. `claude mcp get <name>` — verifies Claude Code parsed the entry.
3. **Subprocess E2E test** — actually invoke a tool:
   ```bash
   claude -p "Use <server> tool <toolname> to ..." \
     --allowedTools "mcp__<server>__<toolname>" \
     --output-format json
   ```
   A successful `"subtype":"success"` with a non-empty `result` field proves end-to-end: config parsed, server reachable, tool invoked, result returned.
4. For other tools: restart the tool and confirm the server appears in its UI / MCP panel.

## Common failure modes and fixes

| Symptom | Root cause | Fix |
| --- | --- | --- |
| `claude mcp list` shows only claude.ai-hosted connectors | `mcpServers` in `~/.claude/settings.json` causing schema-validation failure | Delete `.mcpServers` from `settings.json`; MCP belongs in `~/.claude.json` |
| URL server fails to connect | Missing `"type"` field | Add `"type": "http"` (or `"sse"`) |
| `docker` stdio server fails to connect | Docker daemon off, image not pulled, or env var (`-e VAR`) not in parent env | Start Docker; `docker pull <image>`; set env in entry's `env` block |
| Entry exists in master but doesn't appear | `enabled: false` in master | Set `enabled: true` and re-sync |
| Tool returns stale config after edit | MCP servers only load at session startup | Restart Claude Code (exit + relaunch) |

## Secret hygiene

- Never inline secrets into the skill or committed files.
- `~/.secrets/mcp.json` is the only place tokens live. It must be outside any repo (`~/.secrets/` is user-only).
- Do not echo full tokens in logs; redact in any diagnostic output.

## Verification checklist

- [ ] `~/.secrets/mcp.json` is valid JSON and follows the master schema.
- [ ] `~/.claude/settings.json` does NOT contain an `mcpServers` key.
- [ ] `~/.claude.json → mcpServers` matches `~/.secrets/mcp.json` filtered by `enabled != false`, stripped of custom keys, with `type` set.
- [ ] `claude mcp list` shows each enabled server as "✓ Connected".
- [ ] Subprocess E2E test on at least one server returns a real tool result.
