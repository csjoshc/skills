# Project-Level Agent Symlink Map

This table defines the recommended project-level symlink targets for each supported IDE/CLI agent. Project-level symlinks are optional but recommended for agent discovery and onboarding.

| Agent / IDE              | macOS/Linux Project Path | Windows Project Path       | Symlink Target    | Purpose                            | Required?      |
| :----------------------- | :----------------------- | :------------------------- | :---------------- | :--------------------------------- | :------------- |
| **Gemini / Antigravity** | `./.gemini/skills`       | `.\.gemini\skills`         | `~/.skills` (OS path) | Native discovery; Gemini looks here | ✅ Yes         |
| **Project-Wide Skills**  | `./.skills`              | `.\.skills`                | `~/.skills` (OS path) | Universal project shortcut         | ✅ Yes         |
| **Cursor**               | `./.cursor/skills`       | `.\.cursor\skills`         | `~/.skills` (OS path) | Custom organization                 | ⚠️ Optional    |
| **Cursor (Rules)**       | `./.cursor/rules`        | `.\.cursor\rules`          | `~/.skills` (OS path) | Legacy / project-scoped rules       | ⚠️ Optional    |
| **Claude Code**          | `./.claude/skills`       | `.\.claude\skills`         | `~/.skills` (OS path) | Shim for project discovery          | ⚠️ Optional    |
| **OpenCode**             | `./.opencode/skills`     | `.\.opencode\skills`       | `~/.skills` (OS path) | Custom shim                         | ⚠️ Optional    |
| **Qwen Code**            | `./.qwen/skills`         | `.\.qwen\skills`           | `~/.skills` (OS path) | Not natively discovered             | ⚠️ Optional    |
| **VS Code / Copilot**    | `./.vscode/skills`       | `.\.copilot\skills`        | `~/.skills` (OS path) | Copilot searches workspace settings | ✅ Recommended |
| **ChatGPT / Codex**      | N/A                      | N/A                        | N/A               | Relies on global or web UI uploads  | N/A            |

## Setup by Project Type

### Standard (Gemini + VS Code)

#### macOS / Linux
```bash
#!/bin/bash
# Set up project-level symlinks for Gemini and VS Code

mkdir -p .gemini .vscode
ln -sf ~/.skills .gemini/skills
ln -sf ~/.skills .vscode/skills
```

#### Windows (Git Bash / CMD)
```cmd
:: Set up project-level symlinks for Gemini, Copilot and Project-Wide Skills
 
mkdir ".gemini" ".copilot"
mklink /D ".skills" "%USERPROFILE%\.skills"
mklink /D ".gemini\skills" "%USERPROFILE%\.skills"
mklink /D ".copilot\skills" "%USERPROFILE%\.skills"
```

## Exception: Project-Specific Skills

In rare cases, a project may want **local-only** skills that don't sync to the master store:

### macOS / Linux
```bash
# Instead of symlinking, create a physical directory
mkdir -p .vscode/skills

# Add project-specific SKILL.md files
cat > .vscode/skills/project-local.md << 'EOF'
# Project-Specific Skill
This skill is local to this project and not synced to ~/.skills
EOF
```

### Windows (CMD)
```cmd
mkdir ".copilot\skills"
echo # Project-Specific Skill > .copilot\skills\project-local.md
echo This skill is local to this project and not synced to %%USERPROFILE%%\.skills >> .copilot\skills\project-local.md
```

## Configuration for VS Code
Once the directory (symlinked or local) is set, prioritize it in `.vscode/settings.json`:
```json
{
  "github.copilot.advanced": {
    "instructionsPath": ".vscode/skills" // Adjust to .copilot/skills on Windows if applicable based on the extension usage
  }
}
```

## Verification
To verify project symlinks, check standard link creation:

- **macOS/Linux:** `ls -la .gemini/skills`
- **Windows (Git Bash):** `ls -la .gemini/skills` or use native `dir` command.
