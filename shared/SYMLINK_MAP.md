# Symlink Map

Authoritative symlink mapping for all AI coding agents. Used by `project-onboarding` and `skill-sync`.

## Global Symlinks

All paths symlink to the master store at `~/.skills`.

| Tool / Platform | Global Path | Target |
| :--- | :--- | :--- |
| **Master Store** | `~/.skills` | (Authoritative) |
| **Codex** | `~/.codex/skills` | `~/.skills` |
| **Cursor (Skills)** | `~/.cursor/skills` | `~/.skills` |
| **Cursor (Rules)** | `~/.cursor/rules/master` | `~/.skills` |
| **Claude Code** | `~/.claude/skills` | `~/.skills` |
| **Antigravity** | `~/.gemini/antigravity/skills` | `~/.skills` |
| **Gemini CLI** | `~/.gemini/skills` | `~/.skills` |
| **OpenCode** | `~/.config/opencode/skills` | `~/.skills` |
| **Qwen Code** | `~/.qwen/skills` | `~/.skills` |
| **ChatGPT** | `~/Documents/ChatGPT/CustomInstructions` | `~/.skills` (manual sync) |

**Note:** If a path does not exist, create parent directories before symlinking.

## Project-Level Symlinks

| Tool / Platform | Project Path | Target | Method | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Universal Shim** | `.skills/` | Granular links to `~/.skills/` | Symlink | General discovery (primary onboarding output) |
| **Claude Code** | `.claude/skills` | `~/.skills` | **Copy** (`cp -r`) | Claude Code resolves relative to project root |
| **Gemini CLI** | `.gemini/skills` | `~/.skills` | Symlink | Native discovery |
| **Cursor** | `.cursor/rules/master` | `~/.skills` | Symlink | .mdc indexing |
| **VS Code / Copilot** | `.vscode/skills` | `~/.skills` | Symlink | Copilot workspace settings |
| **Aider** | `.aider.conf.yml` | (Refers to AGENTS.md) | Config | Config-based |
| **Windsurf** | `.windsurfrules` | (Refers to AGENTS.md) | Shim file | Shim file |
| **Cline** | `.clinerules` | (Refers to AGENTS.md) | Shim file | Shim file |

**Note:** All project-level skill folders (`.skills/`, `.gemini/skills/`, `.claude/skills/`, etc.) MUST be added to the project's `.gitignore` and `.cursorignore`. Claude Code uses `cp -r` at the project level because Claude Desktop is sandboxed and cannot follow symlinks outside the workspace — re-copy when master store changes. The global symlink (`~/.claude/skills → ~/.skills`) is unaffected.

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
