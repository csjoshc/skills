# Project-Level Agent Symlink Map

This table defines the shims and symlinks required at the project level to ensure all agents find the master skill store.

| Tool / Platform | Project Path | Target | Purpose |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | `.gemini/skills` | `~/.skills` | Native discovery |
| **Cursor** | `.cursor/rules/master` | `~/.skills` | .mdc indexing |
| **Universal Shim** | `.skills` | `~/.skills` | General discovery |
| **Aider** | `.aider.conf.yml` | (Refers to AGENTS.md) | Config-based |
| **Windsurf** | `.windsurfrules` | (Refers to AGENTS.md) | Shim file |
| **Cline** | `.clinerules` | (Refers to AGENTS.md) | Shim file |

**Note:** All project-level symlinks (`.skills/`, `.gemini/skills/`, etc.) MUST be added to the project's `.gitignore`.