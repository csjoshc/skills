---
name: agent-sync
description: "Sync and audit skill symlinks and MCP configs across agent harnesses."
disable-model-invocation: true
---

# agent-sync

Pick the mode, then read only that file.

| Task | Read | Master store |
|---|---|---|
| Sync, audit or ingest skills; fix broken or stale links | [skills.md](skills.md) (run `sync.py`) | `~/.skills` |
| Sync, toggle or onboard MCP servers | [mcp.md](mcp.md) | `~/.secrets/mcp.json` |
| Rotate or add a token or API key | [mcp.md#rotating-a-token](mcp.md#rotating-a-token) | `~/.config/secrets/work.env` |

Shared path table: [../shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
Hooks are not synced. Edit them in place; see [../shared/HOOK_PRINCIPLES.md](../shared/HOOK_PRINCIPLES.md) before adding one.
