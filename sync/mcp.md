
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
GitHub has no MCP server here: agents use `gh` and `gh api`.
That keeps one auth path per account (`GH_CONFIG_DIR`), skips a ~25k-token tool schema and keeps merges as visible shell commands (2026-10-30).

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

There is no bulk MCP writer.
Native bindings are reconciled individually; `sync.py` manages shared skills, not MCP configuration.

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

These paths and schema differences inform reconciliation of the installed consumer.

### Claude Code (`~/.claude.json`)
- Key: root `.mcpServers`
- Schema: official — `type` + (`command`/`args`/`env` for stdio | `url`/`headers` for http/sse)
- Strip: `enabled`, `allowedTools`
- Also: ensure `~/.claude/settings.json` has NO `mcpServers` key (schema violation).

- File-backed stdio credentials enter through the scoped startup helper, not the parent Claude process.
- Preserve the server's reviewed tool allowlist, such as `--enabled-tools a,b,c` for `mcp-atlassian`.

### Codex (`~/.codex/config.toml`)
- **Personal only.** Reconcile only explicitly approved personal bindings; work servers and work credential references stay out.
  A definition's `"personal": true` flag is not evidence of the actual account or credential owner.
  File-backed personal credentials use the same scoped startup boundary with an explicitly personal store.
- The Codex app, CLI and IDE extension share this file. Servers are `[mcp_servers.<name>]` tables, with `[mcp_servers.<name>.env]` for env.
- Preserve `model`, project trust, native authentication, comments and unrelated server tables.
  Review an entry-level diff and rollback copy; parse the candidate TOML before replacing the live file.
- Codex has no `type` field, and a url server's headers are `http_headers`.
- Preserve per-server keys such as `startup_timeout_sec`, `tool_timeout_sec`, `enabled_tools` and `tools.*`.
  Definition metadata such as `allowedTools` is not a native field; use the installed consumer's permission mechanism.
- Refresh the affected Codex consumer with approval and verify a native tool result.
  Keep new files and rollback copies private, and preserve existing restrictive modes.

### Claude Desktop, Cursor and VS Code
- GUI apps launched from the Dock do not inherit shell exports.
  Use the scoped startup helper with explicit owning-store and variable references, not a wrapper that sources the whole store.
- Where a remote server needs a stdio bridge, retain the reviewed installed bridge and literal header references.
  Replacing a bridge or runtime path needs its own verification before removing the old dependency.
- Files: `~/Library/Application Support/Claude/claude_desktop_config.json` (no `type`) and `~/.cursor/mcp.json` (`type: stdio`). Root key `mcpServers`.
- VS Code (`~/Library/Application Support/Code/User/mcp.json`) uses root key `servers`, with `type` on every entry.
  Its settings-sync copies under `agentPlugins/*/.mcp.json` are generated by VS Code, so sync leaves them alone.
- A launcher using `--user-data-dir` has a separate `<user-data-dir>/User/mcp.json`; reconcile and verify that native profile independently.
  A Claude config root or the Claude Code extension does not prove native Agent Chat wiring.
  Reconcile only MCP runtime definitions, preserving that profile's model, account and permission settings.
- Refresh the affected native connection with approval; a saved config does not prove the running app loaded it.

### Per-target server names
- A tool may already keep a server under another name. Set `"names": {"<target>": "<name>"}` on the master entry, for example `"names": {"vscode": "Docs-Server"}`.
- Use the mapped name when reconciling that consumer's existing entry rather than creating a duplicate.
- The master and the other targets keep the master name, since Claude Code permissions and tool prefixes depend on it.
- Apply disabled intent through the consumer's native toggle or entry removal, under its mapped name.
  Leave unrelated consumer-only servers alone.
- `names` is definition metadata and is never written to a tool.

### Cline, Roo
- Root key `mcpServers`; check the installed schema before reconciliation.

### Oh My Pi (OMP)
- User config: `~/.omp/agent/mcp.json`, root key `mcpServers`.
- Reconcile the effective OMP agent directory, including a wrapper-selected `PI_CODING_AGENT_DIR`, without replacing local model/authentication settings.
- OMP uses typed `stdio`, `http` and `sse` entries with `command`/`args`/`env` or `url`/`headers`.
- File-backed stdio credentials enter through the scoped startup helper; native OAuth remains with OMP.
- Existing OMP-only servers and OMP fields such as `enabled`, `timeout`, `auth`, `oauth`, `instructions` and `requestIdFormat` are preserved when a shared entry is updated.
- Keep new files private and preserve existing restrictive modes.
  Refresh OMP with approval after reconciliation; a written file alone does not prove activation.

### Zed
- Root key `context_servers` (different!).

### OpenCode
- Legacy format: root key `mcp`, with `"type": "local"` + `"command": ["..."]` (array, not string), `environment` for env, and `{env:VAR}` references.
  Check the installed native schema and effective config before adding options: newer versions can normalize legacy entries into `mcp.servers` while discarding unsupported fields.
- It has its own `enabled` flag: an existing entry keeps it, and a master-disabled server is switched off in place instead of removed.
- Preserve intentional context-saving tool disables; a connected server need not expose its tools to the model.
  Code Mode uses a discovery/dispatch interface rather than direct tool names, so missing flattened names alone do not prove broken credentials.
  Any test-only tool or mode changes require owner approval and exact restoration afterward.
  Record the tested mode explicitly: direct MCP results do not certify Code Mode execution.

## Verification

After reconciliation, verify the changed consumer; file-write success is not proof.
For Claude Code:

1. `claude mcp list` — every enabled server must show "✓ Connected". "Failed to connect" means the entry is valid but the runtime isn't working (docker daemon, network, VPN, token, etc.).
2. `claude mcp get <name>` — verifies Claude Code parsed the entry.
3. **Subprocess E2E test** — actually invoke a tool:
   ```bash
   claude -p "Use <server> tool <toolname> to ..." \
     --allowedTools "mcp__<server>__<toolname>" \
     --output-format json
   ```
   Verify the actual requested native tool result and expected identity, tied to the intended consumer/profile and final binding.
   A successful CLI exit, `"subtype":"success"` or non-empty assistant `result` is insufficient.
4. For other tools: refresh the intended consumer/profile with approval and verify the same native tool-result evidence.
   Discovery/connectivity checks and UI / MCP-panel registration do not prove native success.

## Common failure modes and fixes

| Symptom | Root cause | Fix |
| --- | --- | --- |
| `claude mcp list` shows only claude.ai-hosted connectors | `mcpServers` in `~/.claude/settings.json` causing schema-validation failure | Delete `.mcpServers` from `settings.json`; MCP belongs in `~/.claude.json` |
| URL server fails to connect | Missing `"type"` field | Add `"type": "http"` (or `"sse"`) |
| `docker` stdio server fails to connect | Docker daemon off, image unavailable, or missing child credential | Verify the runtime and use scoped startup to supply only the named `-e VAR` credentials |
| Entry exists in master but doesn't appear | Disabled intent or native binding not reconciled | Review `enabled` and reconcile that consumer |
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
Native reconciliation is the only deployment path.

### Definition hygiene

- The master holds `${VAR}` placeholders only.
  Values live in the declared work or personal store (dir 700, file 600), outside every repo.
- Work-specific variable-name templates belong to the private pack's bootstrap overlays.
  Reconcile consumers after the owner fills the value in the declared store; do not add employer inventory to public templates.
- To rotate, see [Rotating a token](#rotating-a-token).
- Reject literal credentials during reconciliation; there is no generator validating definitions for you.
  Evidence and diagnostics name the consumer and field, never a value.

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
| Codex | yes | yes, explicitly approved personal bindings only; no work credentials |
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
