# Symlink Map

Authoritative symlink mapping for all AI coding agents. Used by `project-onboarding` and `skill-sync`.

## Global Symlinks

All paths symlink to the master store at `~/.skills`.

| Tool / Platform | Global Path | Target |
| :--- | :--- | :--- |
| **Master Store** | `~/.skills` | (Authoritative) |
| **Cursor (Skills)** | `~/.cursor/skills` | `~/.skills` |
| **Cursor (Rules)** | `~/.cursor/rules/master` | `~/.skills` |
| **Claude Code** | `~/.claude/skills` | `~/.skills` |
| **Gemini CLI** | `~/.gemini/antigravity/skills` | `~/.skills` |
| **OpenCode** | `~/.config/opencode/skills` | `~/.skills` |
| **Qwen Code** | `~/.qwen/skills` | `~/.skills` |
| **ChatGPT** | `~/Documents/ChatGPT/CustomInstructions` | `~/.skills` (manual sync) |

**Note:** If a path does not exist, create parent directories before symlinking.

## Project-Level Symlinks

| Tool / Platform | Project Path | Target | Purpose |
| :--- | :--- | :--- | :--- |
| **Universal Shim** | `.skills/` | Granular links to `~/.skills/` | General discovery (primary onboarding output) |
| **Gemini CLI** | `.gemini/skills` | `~/.skills` | Native discovery |
| **Cursor** | `.cursor/rules/master` | `~/.skills` | .mdc indexing |
| **VS Code / Copilot** | `.vscode/skills` | `~/.skills` | Copilot workspace settings |
| **Aider** | `.aider.conf.yml` | (Refers to AGENTS.md) | Config-based |
| **Windsurf** | `.windsurfrules` | (Refers to AGENTS.md) | Shim file |
| **Cline** | `.clinerules` | (Refers to AGENTS.md) | Shim file |

**Note:** All project-level symlink folders (`.skills/`, `.gemini/skills/`, etc.) MUST be added to the project's `.gitignore` and `.cursorignore`.

## Setup: Local `.skills` Granular Loop

When onboarding a new project, create a `.skills` folder in the project root and symlink every skill from the master store.

### macOS / Linux

```bash
#!/bin/bash
MASTER_SKILLS="$HOME/.skills"
mkdir -p .skills
for skill in "$MASTER_SKILLS"/*; do
  if [ -d "$skill" ]; then
    skill_name=$(basename "$skill")
    ln -sf "$skill" ".skills/$skill_name"
  fi
done
```

### Windows (CMD)

```cmd
set MASTER_SKILLS=%USERPROFILE%\.skills
mkdir ".skills"
for /D %i in ("%MASTER_SKILLS%\*") do (
  mklink /D ".skills\%%~nxi" "%%i"
)
```
