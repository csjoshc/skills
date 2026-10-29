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
| Reconcile, toggle or onboard one native MCP consumer | [mcp.md](mcp.md) | `~/.secrets/mcp.json` and private-pack `~/.secrets/mcp.d/` definitions |
| Rotate or add a token or API key | [mcp.md#rotating-a-token](mcp.md#rotating-a-token) | The binding's declared work or personal credential store |
| Sync or audit guard hooks (`/sync hooks`) | [../shared/HOOK_PRINCIPLES.md#guard-sync](../shared/HOOK_PRINCIPLES.md#guard-sync) | `~/.skills/hooks/` and bootstrap's `BOM.md` |

With no mode specified, include the guard audit alongside skill-link discovery.
Hook reconciliation is agent-assisted; `sync.py` does not install hooks.
Per-repo git hooks belong to `/onboard` (step 0g); sync installs them only in `~/.skills` and `~/bootstrap`.
An audit writes nothing; repair preserves unrelated settings and asks before replacing conflicting configuration.
Report registration separately from live enforcement, and leave unverified harnesses explicit.
Sync does not authorize commits, pushes, merges, service restarts or removal of old history.
MCP changes use the named-consumer reconciliation workflow, not bulk generation.
Track wrapper profiles separately from their base agents and retain old dependencies until every reader has moved.

Shared path table: [../shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md).
Pinned upstream skills: [skill-sources.json](skill-sources.json); `sync.py` installs these before harness link repair.
Keep hook implementations in `~/.skills/hooks/`; reconcile registrations rather than copying scripts into each harness.
