
# MCP sync & toggle

**Version:** 3.0.0

**Summary:** Reconcile one native MCP consumer at a time from local definitions and private-pack drop-ins.
Keep credentials in the declared owning store, preserve native authentication and permissions, and verify the final binding through that consumer before retiring its old dependencies.
Bootstrap prepares definitions and skill links; it does not deploy native MCP bindings.

## Contents

- Master store schema
- New machine: the template and drop-ins
- Critical rules
- Claude Code scope model
- Standard workflows (native reconciliation, toggle, project onboarding)
- Target-specific transforms
- Verification
- Common failure modes
- Secret hygiene
- Rotating a token
- Harness coverage
- Verification checklist

## Context
`~/.secrets/mcp.json` and private-pack drop-ins declare server intent.
Each native binding adds the consumer's approved account, permissions and launch shape.
Reconcile those together; copying another harness's whole config can overwrite authentication or local settings.

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
      "enabled": true | false,    // sync MCP extension — NOT synced to targets
      "allowedTools": [ ... ],    // sync MCP extension — NOT synced to targets
      "personal": true,           // sync MCP extension: opts the server in to Codex (personal only)
      "credentialSource": "work",
      "names": { "<target>": "<name>" }  // sync MCP extension: name this tool already uses for the server
    }
  }
}
```

`enabled`, `allowedTools`, `personal`, `credentialSource` and `names` are definition metadata, not native MCP fields.
`credentialSource` selects work or personal ownership; it never selects an inherited environment fallback.
Omit it only for credential-free or native-authentication bindings.

## New machine: the template and drop-ins

`~/.secrets/mcp.json` is local only, because it holds work URLs and an email address.
The repo tracks a clean copy, [references/mcp.example.json](references/mcp.example.json), with only `${VAR}` placeholders.

1. `mkdir -p ~/.secrets && chmod 700 ~/.secrets`, then `cp ~/.skills/sync/references/mcp.example.json ~/.secrets/mcp.json && chmod 600 ~/.secrets/mcp.json`.
2. Keep the servers you use, set `enabled`, and replace the example URL.
3. Declare credential ownership explicitly.
   A private pack registers its variable-name templates through bootstrap's existing overlay convention; values stay outside repositories.
   `./bootstrap.sh --secrets` preserves values while preparing the owning work/personal stores.
4. Reconcile one approved consumer using the workflow below and bootstrap's `docs/operations.md#secrets`.

Servers that belong to another repo do not go in the master.
Put them in `~/.secrets/mcp.d/*.json`, which has the same schema and is read after the master in file-name order.
A server with the same name as one in the master replaces it.
For example, `ln -s ~/path/to/private-repo/mcp.work.json ~/.secrets/mcp.d/work.json` adds a private repo's server file without copying it.
Drop-ins contain references, not values.
Validate the merged definitions before editing a consumer; an invalid definition is a blocker, not permission to use stale or inherited credentials.

## Critical rules (learned the hard way)

1. **Claude Code user-scope MCPs live in `~/.claude.json` at the root `mcpServers` key — NOT in `~/.claude/settings.json`.** Putting `mcpServers` into `settings.json` is a documented schema violation (per [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)) and will cause the entire settings file to fail validation, which in turn prevents any user-scope MCPs from loading. Symptom: `claude mcp list` shows only claude.ai-hosted connectors; `claude mcp get <name>` returns "No MCP server found". Fix: delete the `mcpServers` key from `settings.json`.

2. **Always include an explicit `type` field on target entries.** `stdio`/`http`/`sse`. Newer Claude Code versions require it; older ones tolerate its absence for stdio but not for URL transports.

3. **Strip sync MCP extensions (`enabled`, `allowedTools`) when writing to any target.** These are not part of the standard MCP server schema. Keep them only in the master store.

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

### 1. Named-consumer reconciliation

1. Identify the actual launcher, effective config/import roots, account, owning credential store and approved read-only operation.
   Wrapper profiles are separate rows; do not infer their roots from the base CLI.
2. Review an entry-level diff and rollback path, preserving unrelated fields, permissions, native authentication and private modes.
   Keep secret values out of arguments, configuration and evidence.
3. Test the exact launch definition, then refresh the affected native consumer with approval and capture an actual tool result.
   Discovery, transport success and native activation are separate evidence.
4. Exercise missing credentials in an isolated synthetic candidate, and reconcile again to prove a no-op.
   Check that bootstrap, private-pack setup and sync will not overwrite the final binding.
5. Record final binding identity, attempt, outcome and remaining blocker in the private BOM or one current local handoff.
   Before approved retirement, audit every known reader of the old helper, credential store and transport.

The legacy `mcp_sync.py` refuses a batch containing declared credential ownership or existing `credential_exec.py` readers before writing any target.
Its format tests remain available through `python3 -I ~/.skills/sync/test_mcp_sync.py`; they are not permission to regenerate migrated consumers.

### 2. Toggle a server

- **Global intent:** change `enabled` in the owning definition, then reconcile each affected consumer individually.
- **Consumer-only change:** use that consumer's native enable/disable mechanism without changing other profiles.
- **Project-only override:** add/remove the entry in the project's `.mcp.json` (or `projects["<abs-path>"].mcpServers` for a personal local-scope override). Do not modify the master.

### 3. Project onboarding

- If the repo needs a committed MCP config, create `.mcp.json` at the project root (user must approve once per project via Claude Code's trust dialog).
- If it needs a personal-only MCP for this repo, add under `~/.claude.json → projects["<abs-path>"].mcpServers`.
- For non-Claude tools (OpenCode, Cursor), see target-specific paths in [GLOBAL_MCP.md](references/GLOBAL_MCP.md).
- Add project-local personal configs (`.claude/settings.local.json`) to `.gitignore`.

## Target-specific formats

These paths and schema differences inform reconciliation; legacy projection behavior is not a deployment recipe for scoped readers.

### Claude Code (`~/.claude.json`)
- Key: root `.mcpServers`
- Schema: official — `type` + (`command`/`args`/`env` for stdio | `url`/`headers` for http/sse)
- Strip: `enabled`, `allowedTools`
- Also: ensure `~/.claude/settings.json` has NO `mcpServers` key (schema violation).

- Entries keep `${VAR}` references as they are; Claude Code expands them from the shell env at start.
- `mcp-atlassian` gets its `allowedTools` as `--enabled-tools a,b,c` in `args` (Claude Code only).

### Codex (`~/.codex/config.toml`)
- **Personal only.** Codex gets a server only when the master marks it `"personal": true`. The default is that nothing reaches it, so a new work server can never leak in by being added to the master.
- A server that needs `work.env` (any `${VAR}` in its command, args, url, env or headers) is never written to Codex, even if it is marked personal. The run says so and skips it.
  A server in the master that is not marked personal but already sits in Codex's file is left alone and flagged in the output, so you can remove it by hand.
- Mark only servers with no secret, such as a browser-automation server. Work servers stay out.
- The Codex app, CLI and IDE extension share this file. Servers are `[mcp_servers.<name>]` tables, with `[mcp_servers.<name>.env]` for env.
- The file also holds `model`, project trust and servers Codex manages itself, so sync edits only the tables of servers whose projected value changed.
  Everything else stays byte for byte, including comments and hand formatting.
  A changed server is rewritten where its first table was, and a new one goes at the end.
- Before writing, the result is parsed back and must equal the planned config exactly. If it does not, nothing is written, for any target, and the run exits 1.
  An unreadable `config.toml` stops the run the same way.
  With no personal server to write, no file is created.
- Codex has no `type` field, and a url server's headers are `http_headers`.
- Per-server Codex keys such as `startup_timeout_sec`, `tool_timeout_sec`, `enabled_tools` and `tools.*` are kept when the server is updated.
- `allowedTools` is not written to Codex, as for every target. Codex can enforce a list with `enabled_tools` if you want it later.
- Codex is not skipped while running, because its app does not rewrite this file on exit. Restart Codex after a sync.
- Fresh files are created with mode 600, and an existing file keeps its mode. A `.bak.<ts>` copy is saved before any change.

### Claude Desktop, Cursor and VS Code
- GUI apps launched from the Dock do not inherit shell exports.
  Use the scoped startup helper with explicit owning-store and variable references, not a wrapper that sources the whole store.
- Where a remote server needs a stdio bridge, retain the reviewed installed bridge and literal header references.
  Replacing a bridge or runtime path needs its own verification before removing the old dependency.
- Files: `~/Library/Application Support/Claude/claude_desktop_config.json` (no `type`) and `~/.cursor/mcp.json` (`type: stdio`). Root key `mcpServers`.
- VS Code (`~/Library/Application Support/Code/User/mcp.json`) uses root key `servers`, with `type` on every entry.
  Its settings-sync copies under `agentPlugins/*/.mcp.json` are generated by VS Code, so sync leaves them alone.
- Refresh the affected native connection with approval; a saved config does not prove the running app loaded it.

### Per-target server names
- A tool may already keep a server under another name. Set `"names": {"<target>": "<name>"}` on the master entry, for example `"names": {"vscode": "Docs-Server"}`.
- Sync writes that server under the mapped name in that target only, and finds an existing entry with that name, so it is updated in place, never duplicated, and not listed as tool-only.
- The master and the other targets keep the master name, since Claude Code permissions and tool prefixes depend on it.
- A disabled master server (`enabled: false`) is removed from the target like in the other targets, under its mapped name if it has one.
  Servers that exist only in that tool are left alone.
- `names` is an sync extension and is never written to a tool.

### Cline, Roo
- Root key `mcpServers`. Not synced by `mcp_sync.py`; check tool docs per major-version change.

### Oh My Pi (OMP)
- User config: `~/.omp/agent/mcp.json`, root key `mcpServers`.
- Reconcile the effective OMP agent directory, including a wrapper-selected `PI_CODING_AGENT_DIR`, without replacing local model/authentication settings.
- OMP uses typed `stdio`, `http` and `sse` entries with `command`/`args`/`env` or `url`/`headers`.
- `${VAR}` references stay as references in `env` and `headers`; keep credential values in the environment and out of the master file.
- Existing OMP-only servers and OMP fields such as `enabled`, `timeout`, `auth`, `oauth`, `instructions` and `requestIdFormat` are preserved when a shared entry is updated.
- A new target file is mode `0600`; an existing file keeps its mode. OMP reads its MCP config on startup, so restart it after a sync.

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

### Scoped startup for an individually reconciled consumer

`shared/credential_exec.py` loads named credentials into one consumer, not the parent harness or global shell.
For a native MCP entry, use `python3` as its command and the following tokens as its argument array, with reviewed absolute paths:

```text
-I /absolute/skills/shared/credential_exec.py --file /absolute/private/work.env --var EXAMPLE_TOKEN -- /absolute/bin/consumer
```

Repeat `--var` for required names; reserve `--set NAME=value` for non-secret runtime settings.
Arguments after `--` remain literal; never put secret values in them or in the native config.
The helper permits a fixed runtime environment and rejects missing/empty credentials, unsafe file ownership/modes and symlinked credential files.
It sources a trusted shell-compatible file in a clean Bash subprocess: this is not a sandbox for untrusted files or encryption at rest.
Use private files outside repositories on macOS or the Linux side of WSL; WSL execution is not yet verified.
Descriptor mode is retained for existing bridge bindings, not required for new direct command bindings.
Tests: `python3 -I shared/test_credential_exec.py` runs synthetic child processes without live credentials.

No harness is automatically migrated by installing this helper.
Reconcile one native entry, preserve account/tool permissions and unrelated configuration, then verify a real read-only operation with approval.
The legacy generator refuses scoped readers; native reconciliation is their only deployment path.

### Legacy generator

- The master holds `${VAR}` placeholders only.
  Values live in `~/.config/secrets/work.env` (dir 700, file 600), outside every repo.
- Work-specific variable-name templates belong to the private pack's bootstrap overlays.
  Reconcile consumers after the owner fills the value in the declared store; do not add employer inventory to public templates.
- To rotate, see [Rotating a token](#rotating-a-token).
- A literal in a secret-named env/header field is refused by every target.
  Use `--strict` to make that a failure.
- The script never prints values; its warnings name the server and field only.

## Rotating a token

Update the binding's owning store, not a canary copy or inherited shell export.
Keep private-file modes at 600 and the directory at 700.
With approval, relaunch only affected consumers and verify their actual identity and read-only operation.
Obtain approval to revoke the old credential only after every affected reader passes.
Native OAuth and model-account authentication stay with their native owner; do not copy their stores between profiles.
No generator run is needed for a value rotation.

## Harness coverage

Skills and MCP servers sync to different sets of tools, because each tool reads them from different places.

| Tool | Skills (`sync.py`) | Native MCP reconciliation |
|---|---|---|
| Claude Code | yes | yes |
| opencode | yes | yes |
| Cursor | yes | yes |
| VS Code | no | yes (the `vscode` target) |
| Claude Desktop | no | yes (the `desktop` target) |
| Codex | yes | yes, personal only (servers marked `"personal": true`, no secrets; edits `~/.codex/config.toml` in place) |
| Antigravity | yes | no: `~/.gemini/antigravity/mcp_config.json` exists but is empty and unmanaged |
| Copilot | yes | no |

Devin uses its dedicated MCP config files; inspect project overrides as well as the user config.
Gateway wrappers select their roots through private-pack launchers and require their own verification rows.
For another installed consumer, use its documented native format rather than adding a bulk generator target or copying secret values.

## Verification checklist

- [ ] `~/.secrets/mcp.json` is valid JSON and follows the master schema.
- [ ] `~/.claude/settings.json` does NOT contain an `mcpServers` key.
- [ ] Reconciliation of the final native entry is a no-op; approved account, permissions and unrelated fields are preserved.
- [ ] `~/.codex/config.toml` still parses (`python3 -c 'import tomllib,sys;tomllib.load(open(sys.argv[1],"rb"))' ~/.codex/config.toml`).
- [ ] Credential fields contain references only; never put secret values in search commands or output.
- [ ] `claude mcp list` shows each enabled server as "✓ Connected".
- [ ] Every changed consumer has a fresh native read-only result tied to its final binding; transport-only and blocked rows remain explicit.
- [ ] All known readers have moved before any old helper, canary store, bridge or evidence is retired with approval.
