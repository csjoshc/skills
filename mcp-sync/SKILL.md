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

**Version:** 1.0.0

## Context
MCP configurations are fragmented across different tools. This skill unifies them using `~/.secrets/mcp.json` as the authoritative source.

## Objectives
1. **Global Sync:** Propagate servers from `~/.secrets/mcp.json` to all platform-specific config files.
2. **Project Setup:** Create project-local MCP shims if needed (e.g., `.gemini/mcp_config.json`).
3. **Toggle (Enable/Disable):** Globally or locally enable/disable a specific MCP server by name.
4. **Secret Protection:** Ensure no actual secrets are in the skill; always reference `~/.secrets/mcp.json`.

## Core Commands & Workflows

### 1. Sync All Platforms
- Read `~/.secrets/mcp.json`.
- Audit [GLOBAL_MCP.md](references/GLOBAL_MCP.md) for target paths.
- For each path, merge the master JSON into the target.
- **Handling Wrappers:** If the target is Claude Desktop, ensure servers are under the `"mcpServers"` key.

### 2. Project Onboarding (MCP)
- Check for `.gemini/mcp_config.json` or `.mcp.json`.
- Reference [PROJECT_MCP.json](references/PROJECT_MCP.json) for project-specific overrides.
- Add these local configs to `.gitignore`.

### 3. MCP Toggle (`mcp-toggle`)
When the user asks to "enable/disable [server]":
- **Global Toggle:** Modify `~/.secrets/mcp.json` (comment out or set an `enabled: false` flag if supported by the tool, or remove/add the entry).
- **Multi-Tool Propagation:** Immediately run the Sync workflow to update all IDEs and CLIs so the change is reflected everywhere.
- **Project-Specific Toggle:** Enable/Disable only for the current project by modifying the local `.mcp.json` or `.gemini/mcp_config.json`.

## Step-by-Step Implementation

### 1. Initialize Master Store
- If `~/.secrets/mcp.json` does not exist:
  - Create the `~/.secrets` directory.
  - Seed it from `~/.config/mcp/mcp_servers.json` or create a new JSON with `{ "mcpServers": {} }`.

### 2. Update Master Store
- Add or modify the desired MCP server configuration in `~/.secrets/mcp.json`.
- Ensure the configuration follows the standard `{ "mcpServers": { "serverName": { "command": "...", "args": [...] } } }` format.

### 3. Propagate to Targets (Sync)
- For each target defined in `GLOBAL_MCP.md`:
  - Read the existing target configuration.
  - Merge the `mcpServers` object from the master store into the target's relevant key (e.g., `mcpServers`, `context_servers`, or `mcp`).
  - Write the updated configuration back to the target path.
  - Create parent directories if they are missing.

### 4. Verification
- Use `mcp-cli` to verify the server is recognized by the CLI.
- Check IDE settings to confirm the server appears.

## Verification
- [ ] `~/.secrets/mcp.json` exists and is valid JSON.
- [ ] Target config files are updated with the correct format (standard vs. wrapped).
- [ ] Toggled servers are successfully removed or added across all audited paths.
