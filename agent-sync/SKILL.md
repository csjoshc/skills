---
name: agent-sync
description: >-
  Keeps AI agent setups in sync from one master store. Skills mode audits and repairs symlinks
  from ~/.skills into Claude Code, Cursor, Codex, Antigravity, OpenCode and others. MCP mode projects
  ~/.secrets/mcp.json into each tool's native config (env-var references, never literal secrets)
  and toggles servers. Use when syncing or
  auditing skills, ingesting a new skill, fixing broken skill links, or enabling, disabling or
  standardizing MCP servers across tools.
---

# agent-sync

Pick the mode, then read only that file.

| Task | Read | Master store |
|---|---|---|
| Sync, audit or ingest skills; fix broken or stale links | [skills.md](skills.md) (run `sync.py`) | `~/.skills` |
| Sync, toggle or onboard MCP servers | [mcp.md](mcp.md) | `~/.secrets/mcp.json` |

Shared path table: [../shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
Hooks are not synced. Edit them in place; see [../shared/HOOK_PRINCIPLES.md](../shared/HOOK_PRINCIPLES.md) before adding one.
