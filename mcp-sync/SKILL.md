---
name: mcp-sync
description: Synchronizes and audits Model Context Protocol (MCP) configs across all ides and agents.
---

# MCP Sync & Toggle

## TL;DR (Quick Start)

Unifies Model Context Protocol (MCP) server configurations across IDEs (Cursor, VS Code) and agents (Claude, Gemini). Uses `~/.secrets/mcp.json` as the master store.

**When to use:** Adding a new MCP server, global sync across all tools, or toggling (enable/disable) specific servers.

**Invocation:**
```bash
mcp-sync sync-all
# Or via script
python3 ~/.skills/mcp-sync/sync.py
```

## When to Use
- Adding or modifying a global MCP server configuration.
- Syncing changes from the master store to all tools.
- Enabling or disabling a specific server by name.
- **NOT for:** Per-project local tool configuration (handled by the project agent).

## Decision Tree

1. **Global or Local update?**
   - GLOBAL → Update `~/.secrets/mcp.json` and sync all platforms.
   - LOCAL → Update project-specific `.mcp_config.json`.

2. **Is the target a specific tool?**
   - Claude Desktop → Merge into `mcpServers` key.
   - Gemini/Antigravity → Merge into `context_servers` key.

3. **Are secrets involved?**
   - YES → **MANDATORY** Store in `~/.secrets/mcp.json`; never in the skill repo.
   - NO → Proceed with standard config.

## Workflow

### 1. Initialize/Audit
Read `~/.secrets/mcp.json`. Verify the existence of target config files for all platforms.

### 2. Update Master
Add the new server config to the master store using the standard `{ "mcpServers": { ... } }` format.

### 3. Propagate (Sync)
Merge the master configuration into each tool's local configuration file, preserving tool-specific keys.

### 4. Toggle
When a server is marked as `enabled: false` in the master store, remove it from all synced targets.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing tool config — proceed with re-creation of target file.
- **Tier 2 (conflict):** Different commands for the same server name — block and confirm priority.
- **Tier 3 (security):** Secrets found in public skill documentation — **STOP**, scrub history, block and alert.

## Examples (Few-Shot)

**Example 1: Adding a new server**
Input: "Sync the new postgres mcp server"
Output: `~/.secrets/mcp.json` updated with `postgres` server; and all platform configs synced.

**Example 2: Disabling a server**
Input: "Disable the figma mcp server globally"
Output: `figma` server removed from `mcpServers` and all tools synced.

## Related Skills
| Skill | When to use instead |
|-------|---------------------|
| skill-sync | For syncing behavior/documentation (`.skills/`) |
| mcp-cli | For local command-line exploration of MCP tools |

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.
