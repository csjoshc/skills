# Project-Level Agent Symlink Map

This table defines the recommended project-level symlink targets for each supported IDE/CLI agent. Project-level symlinks are optional but recommended for agent discovery and onboarding.

| Agent / IDE              | Project Path         | Symlink Target | Purpose                                                                     | Required?      |
| :----------------------- | :------------------- | :------------- | :-------------------------------------------------------------------------- | :------------- |
| **Gemini / Antigravity** | `./.gemini/skills`   | `~/.skills`    | Native project discovery; Gemini looks here automatically                   | ✅ Yes         |
| **Cursor**               | `./.cursor/skills`   | `~/.skills`    | Custom organization; not natively discovered but useful for project context | ⚠️ Optional    |
| **Cursor (Rules)**       | `./.cursor/rules`    | `~/.skills`    | Legacy `.mdc` organization; aids in project-scoped rule discovery           | ⚠️ Optional    |
| **Claude Code**          | `./.claude/skills`   | `~/.skills`    | Shim for project discovery; Claude reads `CLAUDE.md` from root by default   | ⚠️ Optional    |
| **OpenCode**             | `./.opencode/skills` | `~/.skills`    | Custom shim; OpenCode reads `AGENTS.md` from root by default                | ⚠️ Optional    |
| **Qwen Code**            | `./.qwen/skills`     | `~/.skills`    | Not natively discovered; useful as a documentation hook                     | ⚠️ Optional    |
| **VS Code**              | `./.vscode/skills`   | `~/.skills`    | Recommended; Copilot searches here for workspace-specific customizations    | ✅ Recommended |
| **ChatGPT / Codex**      | N/A                  | N/A            | No project-local pattern; relies on web UI uploads                          | N/A            |

## Setup by Project Type

### Minimal (Global Only)

```bash
# Skip project-level setup; rely on global symlinks
# This works for all agents
```

### Standard (Gemini + VS Code)

```bash
#!/bin/bash
# Set up project-level symlinks for Gemini and VS Code

mkdir -p .gemini .vscode
ln -sf ~/.skills .gemini/skills
ln -sf ~/.skills .vscode/skills
```

### Full (All Agents)

```bash
#!/bin/bash
# Set up complete project-level symlinks for all agents

mkdir -p .cursor .gemini .claude .opencode .qwen .vscode
ln -sf ~/.skills .cursor/skills
ln -sf ~/.skills .cursor/rules
ln -sf ~/.skills .gemini/skills
ln -sf ~/.skills .claude/skills
ln -sf ~/.skills .opencode/skills
ln -sf ~/.skills .qwen/skills
ln -sf ~/.skills .vscode/skills
```

## Exception: Project-Specific Skills

In rare cases, a project may want **local-only** skills that don't sync to the master store:

```bash
# Instead of symlinking, create a physical directory
mkdir -p .vscode/skills

# Add project-specific SKILL.md files
cat > .vscode/skills/project-local.md << 'EOF'
# Project-Specific Skill
This skill is local to this project and not synced to ~/.skills
EOF

# Configure VS Code to search this location first
# .vscode/settings.json
{
  "github.copilot.advanced": {
    "instructionsPath": ".vscode/skills"
  }
}
```

## Verification

```bash
# Check which project-level symlinks exist
echo "=== Project Symlinks ==="
for path in .gemini/skills .cursor/skills .cursor/rules .claude/skills .opencode/skills .qwen/skills .vscode/skills; do
  if [ -L "$path" ]; then
    echo "✓ $path → $(readlink -f $path)"
  elif [ -d "$path" ]; then
    echo "⚠ $path (physical directory)"
  else
    echo "✗ $path (missing)"
  fi
done
```
