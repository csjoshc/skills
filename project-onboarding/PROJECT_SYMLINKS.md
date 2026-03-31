# Project-Level Agent Symlink Map

This table defines the shims and symlinks required at the project level to ensure all agents find the master skill store.

| Tool / Platform | Project Path | Target | Purpose |
| :--- | :--- | :--- | :--- |
| **Universal Shim** | `.skills/` | Granular links to `~/.skills/` | General discovery (Primary onboarding output) |
| **Gemini CLI** | `.gemini/skills` | `~/.skills` | Native discovery |
| **Cursor** | `.cursor/rules/master` | `~/.skills` | .mdc indexing |
| **VS Code / Copilot**| `.vscode/skills` | `~/.skills` | Copilot workspace settings |
| **Aider** | `.aider.conf.yml` | (Refers to AGENTS.md) | Config-based |
| **Windsurf** | `.windsurfrules` | (Refers to AGENTS.md) | Shim file |
| **Cline** | `.clinerules` | (Refers to AGENTS.md) | Shim file |

**Note:** All project-level symlink folders (`.skills/`, `.gemini/skills/`, etc.) MUST be added to the project's `.gitignore` and `.cursorignore`.

## Setup: Local `.skills` Granular Loop

When onboarding a new project, you must set up the `Universal Shim` by creating a `.skills` folder in the project root and creating a symlink for *every* skill found in the master store.

### macOS / Linux

```bash
#!/bin/bash
# Create granular project-level symlinks

MASTER_SKILLS="$HOME/.skills"
mkdir -p .skills

# Iterate over master store and link each
for skill in "$MASTER_SKILLS"/*; do
  if [ -d "$skill" ]; then
    skill_name=$(basename "$skill")
    ln -sf "$skill" ".skills/$skill_name"
  fi
done
```

### Windows (CMD)

```cmd
:: Create granular project-level symlinks on Windows
:: Must be run via cmd //c if inside Git Bash

set MASTER_SKILLS=%USERPROFILE%\.skills
mkdir ".skills"

for /D %i in ("%MASTER_SKILLS%\*") do (
  mklink /D ".skills\%%~nxi" "%%i"
)
```