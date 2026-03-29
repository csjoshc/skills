# Global Agent Symlink Map

This table defines the authoritative global symlink targets for each supported tool. All paths should point to the master store at `~/.skills`.

| Tool / Platform | Global Path | Target | Status |
| :--- | :--- | :--- | :--- |
| **Master Store** | `~/.skills` | (Authoritative) | - |
| **Cursor (Skills)** | `~/.cursor/skills` | `~/.skills` | Shared behavior |
| **Cursor (Rules)** | `~/.cursor/rules/master` | `~/.skills` | .mdc rules |
| **Claude Code** | `~/.claude/skills` | `~/.skills` | Custom instructions |
| **Gemini CLI** | `~/.gemini/antigravity/skills` | `~/.skills` | Native skills |
| **OpenCode** | `~/.config/opencode/skills` | `~/.skills` | Shared store |
| **Qwen Code** | `~/.qwen/skills` | `~/.skills` | Shared store |
| **ChatGPT** | `~/Documents/ChatGPT/CustomInstructions` | `~/.skills` | (Manual sync) |

**Note:** If a path does not exist, the onboarding skill should create the parent directories before symlinking.