
# MCP sync & toggle

**Version:** 3.0.0

## Contents

- Master store schema
- Critical rules
- Claude Code scope model
- Standard workflows (full sync, toggle, project onboarding)
- Target-specific transforms
- Verification
- Common failure modes
- Secret hygiene
- Rotating a token
- Harness coverage
- Verification checklist

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
      "enabled": true | false,    // agent-sync MCP extension — NOT synced to targets
      "allowedTools": [ ... ]     // agent-sync MCP extension — NOT synced to targets
    }
  }
}
```

`enabled` and `allowedTools` are **agent-sync MCP extensions**. They must be stripped before writing to any target config — most tools' JSON schemas reject unknown fields or load a schema-invalid file as empty.

## Critical rules (learned the hard way)

1. **Claude Code user-scope MCPs live in `~/.claude.json` at the root `mcpServers` key — NOT in `~/.claude/settings.json`.** Putting `mcpServers` into `settings.json` is a documented schema violation (per [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)) and will cause the entire settings file to fail validation, which in turn prevents any user-scope MCPs from loading. Symptom: `claude mcp list` shows only claude.ai-hosted connectors; `claude mcp get <name>` returns "No MCP server found". Fix: delete the `mcpServers` key from `settings.json`.

2. **Always include an explicit `type` field on target entries.** `stdio`/`http`/`sse`. Newer Claude Code versions require it; older ones tolerate its absence for stdio but not for URL transports.

3. **Strip agent-sync MCP extensions (`enabled`, `allowedTools`) when writing to any target.** These are not part of the standard MCP server schema. Keep them only in the master store.

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

1. `python3 ~/.skills/agent-sync/mcp_sync.py --dry-run` and read the key paths it lists.
2. Run it again without `--dry-run`. Use `--targets claude,opencode,...` to limit it and `--strict` to fail on any literal secret.
3. Run the verification commands (§Verification).

The script reads the master, drops `enabled: false` servers, strips `enabled` and `allowedTools`, sets an explicit `type`, and merges into each target.
It keeps tool-only servers and unrelated keys, writes through a temp file and atomic rename, keeps the file's mode, and saves `<file>.bak.<ts>` (mode 600) before changing anything.
It also removes a stray `mcpServers` from `~/.claude/settings.json`.
Cursor, VS Code and Claude Desktop are skipped with a message while the app is running, because the app rewrites its own file on exit (`--ignore-running` overrides).
Tests: `python3 -I ~/.skills/agent-sync/test_mcp_sync.py`.
Mutation check: `python3 -I ~/.skills/agent-sync/mutants_mcp_sync.py`.

### 2. Toggle a server

- **Global disable:** set `enabled: false` in `~/.secrets/mcp.json`, then re-run full sync. Sync removes the entry from all targets.
- **Global enable:** set `enabled: true` (or remove the field), re-run sync.
- **Project-only override:** add/remove the entry in the project's `.mcp.json` (or `projects["<abs-path>"].mcpServers` for a personal local-scope override). Do not modify the master.

### 3. Project onboarding

- If the repo needs a committed MCP config, create `.mcp.json` at the project root (user must approve once per project via Claude Code's trust dialog).
- If it needs a personal-only MCP for this repo, add under `~/.claude.json → projects["<abs-path>"].mcpServers`.
- For non-Claude tools (OpenCode, Cursor), see target-specific paths in [GLOBAL_MCP.md](references/GLOBAL_MCP.md).
- Add project-local personal configs (`.claude/settings.local.json`) to `.gitignore`.

## Target-specific transforms

### Claude Code (`~/.claude.json`)
- Key: root `.mcpServers`
- Schema: official — `type` + (`command`/`args`/`env` for stdio | `url`/`headers` for http/sse)
- Strip: `enabled`, `allowedTools`
- Also: ensure `~/.claude/settings.json` has NO `mcpServers` key (schema violation).

- Entries keep `${VAR}` references as they are; Claude Code expands them from the shell env at start.
- `mcp-atlassian` gets its `allowedTools` as `--enabled-tools a,b,c` in `args` (Claude Code only).

### Claude Desktop, Cursor and VS Code
- GUI apps launched from the Dock do not inherit the shell env, so a server that uses a `${VAR}` becomes a wrapper: `command: /bin/zsh`, `args: ["-c", "set -a; . \"$HOME/.config/secrets/work.env\"; exec <command and args, shell-quoted>"]`.
- A secret env entry whose name equals the variable is dropped from `env` because the sourced file exports it.
  A renamed one is assigned inside the script.
- Desktop is stdio-only: a `url` server runs as `npx -y mcp-remote <url> --header "Name:$VAR"`, with the node bin dir put on `PATH`.
  Cursor does the same only when the header needs a variable.
  The npx path is taken from the master (`--npx` overrides).
- Files: `~/Library/Application Support/Claude/claude_desktop_config.json` (no `type`) and `~/.cursor/mcp.json` (`type: stdio`). Root key `mcpServers`.
- VS Code (`~/Library/Application Support/Code/User/mcp.json`) uses the same wrappers under the root key `servers`, with `type` on every entry.
  Its settings-sync copies under `agentPlugins/*/.mcp.json` are generated by VS Code, so sync leaves them alone.
- Quit and reopen the app after a sync.

### Per-target server names
- A target can use a different name for a master server: `Target(alias={master name: target name})`.
  Today only VS Code has one, `VSCODE_ALIAS = {"remote": "Aliased-Name"}`, because the user already keeps the remote server there under that name.
- Sync writes master `remote` as `Aliased-Name` and finds an existing `Aliased-Name` entry, so it is updated in place, never duplicated, and not listed as tool-only.
- The master and the other tools keep `remote`, since Claude Code permissions and tool prefixes depend on it.
- A disabled master server (`enabled: false`) is removed from VS Code like in the other targets, under its alias if it has one.
  Servers that exist only in VS Code are left alone.

### Cline, Roo
- Root key `mcpServers`. Not synced by `mcp_sync.py`; check tool docs per major-version change.

### pi (`pi_agent_rust`)
- Files: `~/.pi/agent/mcp.json` and `~/.gateway-pi/mcp.json` (the gateway-pi wrapper sets `PI_CODING_AGENT_DIR`). Root key `mcpServers`.
- Run `python3 ~/.skills/agent-sync/mcp_sync.py --targets pi,pi-gateway` (`--dry-run` first).
  `mcp_pi.py` is a thin entry point that does the same.
  Tests: `test_mcp_sync.py` and `test_mcp_pi.py`.
- Merge only: servers named in the master are added, updated or (when disabled) removed.
  Other servers, such as the pi-only `claude` one, and other keys stay.
  Writes are mode 600 with a timestamped `.bak.<ts>` copy when something changed.
- pi rejects `http` with `args`/`env`, `stdio` with `headers`, `command` with `url`, and `type` `local`/`remote`. The script emits only the fields each type allows.
- Secrets: pi expands a whole value `$ENV:NAME`, so a master `${NAME}` becomes `$ENV:NAME`.
  A `${NAME}` inside a longer value is dropped with a warning, and a literal in a secret-named field is refused.
  Build any prefixed value once in `work.env` (such as `REMOTE_MCP_AUTH`) and keep the master value a bare `${NAME}`.
  The variable must be exported in the shell that starts pi.
- Trust: pi runs a server only after `/mcp trust <name>`, per file and per definition. Any change to a server re-pends it. `$ENV:` refs keep a token rotation from re-pending.

### Zed
- Root key `context_servers` (different!).

### OpenCode
- Root key `mcp`. Uses `"type": "local"` + `"command": ["..."]` (array, not string), `environment` for env, and `{env:VAR}` references.
- It has its own `enabled` flag: an existing entry keeps it, and a master-disabled server is switched off in place instead of removed.

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

- The master holds `${VAR}` placeholders only.
  Values live in `~/.config/secrets/work.env` (dir 700, file 600), outside every repo.
- To add a secret: add `NAME=` to the repo template `secrets/work.env.example` in `~/bootstrap`, set it in `work.env`, put `${NAME}` in the master, then run `mcp_sync.py`.
- To rotate, see [Rotating a token](#rotating-a-token).
- A literal in a secret-named env/header field is refused by every target.
  Use `--strict` to make that a failure.
- The script never prints values; its warnings name the server and field only.

## Rotating a token

Rotation touches one file.
Every target holds a reference to the variable, never the value, so no config needs editing and `mcp_sync.py` does not need to run.

1. Issue the new token in the provider (GitHub, Atlassian, remote) and revoke the old one.
2. Edit the value in `~/.config/secrets/work.env`. Keep the file at mode 600.
   `REMOTE_MCP_AUTH` is derived from `REMOTE_MCP_TOKEN`, so only the token line changes.
3. Restart each tool so it re-reads the value, starting it from a shell that sourced `work.env`.

| Tool | How it gets the value | What to do after rotating |
|---|---|---|
| Claude Code | `${VAR}` expanded from its own environment at startup | Exit and relaunch from a fresh shell. |
| opencode | `{env:VAR}` expanded by the shared service | Run `opencode service restart` from a fresh shell. |
| pi, gateway-pi | `$ENV:VAR` expanded when the server starts | Quit and relaunch pi. The trust record is unchanged, because it fingerprints the reference, not the value. |
| Cursor, Claude Desktop, VS Code | A `/bin/zsh -c` wrapper sources `work.env` when the server spawns | Reload the MCP server or restart the app. No shell is needed. |

Check afterwards with `python3 -I mcp_sync.py --dry-run`: every target should report `unchanged`.
A new variable is a different job: follow "To add a secret" above.

## Harness coverage

Skills and MCP servers sync to different sets of tools, because each tool reads them from different places.

| Tool | Skills (`sync.py`) | MCP servers (`mcp_sync.py`) |
|---|---|---|
| Claude Code | yes | yes |
| opencode | yes | yes |
| Cursor | yes | yes |
| pi, gateway-pi | yes | yes |
| VS Code | no | yes (the `vscode` target) |
| Claude Desktop | no | yes (the `desktop` target) |
| Codex | yes | no: its `[mcp_servers.*]` entries in `~/.codex/config.toml` are its own and hold no master secrets |
| Antigravity | yes | no: `~/.gemini/antigravity/mcp_config.json` exists but is empty and unmanaged |
| Copilot | yes | no |

If a tool in the "no" column needs a master server, add a target in `mcp_sync.py` rather than copying values by hand.

## Verification checklist

- [ ] `~/.secrets/mcp.json` is valid JSON and follows the master schema.
- [ ] `~/.claude/settings.json` does NOT contain an `mcpServers` key.
- [ ] `mcp_sync.py --dry-run` lists no key-path changes.
- [ ] No target file contains a literal secret value (grep each `work.env` value, expect 0 hits).
- [ ] `claude mcp list` shows each enabled server as "✓ Connected".
- [ ] Subprocess E2E test on at least one server returns a real tool result.
