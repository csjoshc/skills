---
name: sync
description: "Syncs and audits skills, MCP configs and guard hooks across agent harnesses."
disable-model-invocation: true
---

# sync

For a named mode, read its file below.

| Task | Read | Master store |
|---|---|---|
| Sync, audit or ingest skills; fix broken or stale links | [skills.md](skills.md) (run `sync.py`) | `~/.skills` |
| Sync, toggle or onboard MCP servers (Claude, Codex, OpenCode, Cursor, OMP and more) | [mcp.md](mcp.md) | `~/.secrets/mcp.json` and `~/.secrets/mcp.d/` |
| Rotate or add a token or API key | [mcp.md#rotating-a-token](mcp.md#rotating-a-token) | `~/.config/secrets/work.env` |
| Sync or audit guard hooks (`/sync hooks`) | [../shared/HOOK_PRINCIPLES.md#guard-sync](../shared/HOOK_PRINCIPLES.md#guard-sync) | `~/.skills/hooks/` and bootstrap's `BOM.md` |

With no mode specified, include the guard audit alongside skill-link discovery.
Hook reconciliation is agent-assisted; `sync.py` and `mcp_sync.py` do not install hooks.
An audit writes nothing; repair preserves unrelated settings and asks before replacing conflicting configuration.
Report registration separately from live enforcement, and leave unverified harnesses explicit.
Sync does not authorize commits, pushes, merges, service restarts or removal of old history.

Shared path table: [../shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
Pinned upstream skills: [skill-sources.json](skill-sources.json); `sync.py` installs these before harness link repair.
Keep hook implementations in `~/.skills/hooks/`; reconcile registrations rather than copying scripts into each harness.
