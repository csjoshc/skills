# Global Agent Symlink Map

This table defines the authoritative global symlink targets for each supported IDE/CLI agent. All paths should point to `~/.skills` (the master store).

| Agent / IDE              | Global Path                    | Symlink Target | Notes                                                                                    |
| :----------------------- | :----------------------------- | :------------- | :--------------------------------------------------------------------------------------- |
| **Cursor**               | `~/.cursor/skills`             | `~/.skills`    | Primary symlink for rule files; see `~/.cursor/rules` for `.mdc` manifests               |
| **Cursor (Rules)**       | `~/.cursor/rules`              | `~/.skills`    | Legacy rules path; modern `.mdc` files are stored here                                   |
| **Gemini / Antigravity** | `~/.gemini/antigravity/skills` | `~/.skills`    | Native support for global + project-local skills                                         |
| **Claude Code**          | `~/.claude/skills`             | `~/.skills`    | Reads `CLAUDE.md` from project root by default; skills folder is a shim for organization |
| **OpenCode**             | `~/.config/opencode/skills`    | `~/.skills`    | Reads `AGENTS.md` from project root; skills folder provides extra context                |
| **Qwen Code**            | `~/.qwen/skills`               | `~/.skills`    | Global-only; no native project-local discovery                                           |
| **VS Code**              | `~/.vscode/skills`             | `~/.skills`    | Global skills accessible to all workspaces via Copilot extensions                        |
| **ChatGPT / Codex**      | N/A                            | N/A            | Uses custom instructions (web UI) or file uploads; no local symlink directory            |

## Setup Script

```bash
#!/bin/bash
# Create all global symlinks

MASTER="$HOME/.skills"

mkdir -p ~/.cursor ~/.gemini/antigravity ~/.claude ~/.config/opencode ~/.qwen ~/.vscode

# Link each platform to master store
ln -sf $MASTER ~/.cursor/skills
ln -sf $MASTER ~/.cursor/rules
ln -sf $MASTER ~/.gemini/antigravity/skills
ln -sf $MASTER ~/.claude/skills
ln -sf $MASTER ~/.config/opencode/skills
ln -sf $MASTER ~/.qwen/skills
ln -sf $MASTER ~/.vscode/skills

echo "✅ Global symlinks created"
```

## Verification

```bash
# Verify all symlinks point to master store
for path in ~/.cursor/skills ~/.cursor/rules ~/.gemini/antigravity/skills ~/.claude/skills ~/.config/opencode/skills ~/.qwen/skills ~/.vscode/skills; do
  echo "$(readlink -f $path) == $HOME/.skills"
done
```
