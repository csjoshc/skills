# Global MCP Configuration Map

This table defines the location and schema requirements for global MCP configuration files.

| Tool / Platform | Global Config Path | JSON Root Key | Toggle Approach |
| :--- | :--- | :--- | :--- |
| **Authoritative Store**| `~/.secrets/mcp.json` | `mcpServers` | Master Source (do not edit directly) |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | `mcpServers` | Set `enabled: false` or remove server entry |
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` | Set `enabled: false` or remove server entry |
| **Cline (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | `mcpServers` | Set `enabled: false` |
| **Roo Code (VS Code)** | `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` | `mcpServers` | Set `enabled: false` |
| **Zed Editor** | `~/.config/zed/settings.json` | `context_servers` | Remove server entry |
| **OpenCode** | `~/.config/opencode/opencode.json` | `mcp` | Set `enabled: false` |
| **Gemini CLI** | `~/.gemini/mcp_config.json` | `mcpServers` | Set `enabled: false` |

### How to Enable/Disable MCP Servers

**IMPORTANT:** Each IDE/vendor has its own config file with its own schema. Do NOT edit `~/.secrets/mcp.json` directly for toggling.

To disable a server:
1. Open the vendor-specific config file (e.g., `~/.cursor/mcp.json`, `~/.config/opencode/opencode.json`)
2. Find the server entry and either:
   - Set `"enabled": false` (if supported by that tool), OR
   - Remove the server entry entirely
3. Restart the IDE/tool to apply changes

### Schema Differences
- **Most tools:** Use `{"mcpServers": { "name": { "command": "...", "args": [...] } }}`
- **Zed:** Uses `{"context_servers": { "name": { "command": "...", "args": [...] } }}`
- **OpenCode:** Uses `{"mcp": { "name": { "type": "local", "command": ["..."], "enabled": true } }}` (Note: `command` is often an array in OpenCode).

**Note:** For tools like Claude Desktop, the sync tool must handle the specific nesting and ensure no other settings in the file are overwritten.
