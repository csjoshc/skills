# Global Agent Symlink Map

This table defines the authoritative global symlink targets for each supported IDE/CLI agent. All paths should point to `~/.skills` (the master store).

| Agent / IDE              | macOS/Linux Path               | Windows Path                                 | Target        | Notes                                                              |
| :----------------------- | :----------------------------- | :------------------------------------------- | :------------ | :----------------------------------------------------------------- |
| **Gemini / Antigravity** | `~/.gemini/antigravity/skills` | `%USERPROFILE%\.gemini\antigravity\skills\`  | `~/.skills`   | Native support for global + project-local skills                   |
| **ChatGPT / Codex**      | `~/.codex/skills`              | `%USERPROFILE%\.codex\skills\`               | `~/.skills`   | Primary symlink for codex system-skills and user skills            |
| **Cursor**               | `~/.cursor/skills`             | `%USERPROFILE%\.cursor\skills\`              | `~/.skills`   | Primary symlink for rule files; see `.cursor/rules` for `.mdc`     |
| **Cursor (Rules)**       | `~/.cursor/rules`              | `%USERPROFILE%\.cursor\rules\`               | `~/.skills`   | Legacy rules path; modern `.mdc` files are stored here             |
| **VS Code / Copilot**    | `~/.vscode/skills`             | `%USERPROFILE%\.copilot\skills\`             | `~/.skills`   | Global skills accessible via Copilot extensions                    |
| **Qwen Code**            | `~/.qwen/skills`               | `%USERPROFILE%\.qwen\skills\`                 | `~/.skills`   | Global-only; no native project-local discovery                     |
| **OpenCode**             | `~/.config/opencode/skills`    | `%USERPROFILE%\.config\opencode\skills\`     | `~/.skills`   | Reads `AGENTS.md` from project root; provides extra context        |
| **Claude Code**          | `~/.claude/skills`             | `%USERPROFILE%\.claude\skills\`               | `~/.skills`   | Reads `CLAUDE.md` from project root; skills folder is organizational|

## Setup Scripts

### macOS / Linux
```bash
#!/bin/bash
# Create all global symlinks on macOS/Linux

MASTER="$HOME/.skills"

mkdir -p ~/.cursor ~/.gemini/antigravity ~/.claude ~/.config/opencode ~/.qwen ~/.vscode ~/.codex

# Link each platform to master store
ln -sf $MASTER ~/.gemini/antigravity/skills
ln -sf $MASTER ~/.codex/skills
ln -sf $MASTER ~/.cursor/skills
ln -sf $MASTER ~/.cursor/rules
ln -sf $MASTER ~/.vscode/skills
ln -sf $MASTER ~/.qwen/skills
ln -sf $MASTER ~/.config/opencode/skills
ln -sf $MASTER ~/.claude/skills

echo "✅ macOS/Linux Global symlinks created"
```

### Windows (Git Bash / CMD)
*Note: Due to Windows filesystem restrictions, it is highly recommended to use `mklink /D` executed via `cmd //c` when in Git Bash, or run a native batch script as an administrator or with Developer Mode enabled.*

```cmd
:: Create all global symlinks on Windows
:: Run this in Command Prompt (CMD)

set MASTER=%USERPROFILE%\.skills

mkdir "%USERPROFILE%\.gemini\antigravity" "%USERPROFILE%\.codex" "%USERPROFILE%\.cursor" "%USERPROFILE%\.copilot" "%USERPROFILE%\.qwen" "%USERPROFILE%\.config\opencode" "%USERPROFILE%\.claude"

mklink /D "%USERPROFILE%\.gemini\antigravity\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.codex\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.cursor\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.cursor\rules" "%MASTER%"
mklink /D "%USERPROFILE%\.copilot\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.qwen\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.config\opencode\skills" "%MASTER%"
mklink /D "%USERPROFILE%\.claude\skills" "%MASTER%"

echo "✅ Windows Global symlinks created"
```

## Verification Instructions

When querying or verifying these paths using an LLM agent, ensure you use the OS-appropriate command:

- **macOS/Linux:** Use `readlink -f [path]` or `[ -L [path] ]` 
- **Windows (Git Bash):** Use `ls -la [path]` and check for the `lrwxrwxrwx ... ->` pattern to confirm it resolves back to `%USERPROFILE%\.skills`.
