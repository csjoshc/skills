# Symlink Map

Authoritative symlink mapping for all AI coding agents. Used by `project-onboarding`, `skill-sync`, `mcp-sync`, and `hook-sync`.

## Global Symlinks

All paths symlink to the master store at `~/.skills`.

| Tool / Platform | Global Path | Target |
| :--- | :--- | :--- |
| **Master Store** | `~/.skills` | (Authoritative) |
| **Codex** | `~/.codex/skills/<name>` | `~/.skills/<name>` (per-skill, see note) |
| **Cursor (Skills)** | `~/.cursor/skills` | `~/.skills` |
| **Cursor (Rules)** | `~/.cursor/rules/master` | `~/.skills` |
| **Claude Code** | `~/.claude/skills` | `~/.skills` |
| **Antigravity** | `~/.gemini/antigravity/skills` | `~/.skills` |
| **Gemini CLI** | `~/.gemini/skills` | `~/.skills` |
| **OpenCode** | `~/.config/opencode/skills` | `~/.skills` |
| **Qwen Code** | `~/.qwen/skills` | `~/.skills` |
| **ChatGPT** | `~/Documents/ChatGPT/CustomInstructions` | `~/.skills` (manual sync) |

**Note:** If a path does not exist, create parent directories before symlinking.

### Codex exception: per-skill symlinks

Codex installs system-managed skills (`imagegen`, `openai-docs`, `plugin-creator`, `skill-creator`, `skill-installer`, `slides`, `spreadsheets`) directly into `~/.codex/skills/`, marked by `~/.codex/skills/.system/.codex-system-skills.marker`. These are not portable to other agents.

To preserve codex-only content while still syncing master skills, `~/.codex/skills/` is a real directory containing **per-skill symlinks** to `~/.skills/<name>/`. Codex-managed skills coexist as plain directories.

**Sync workflow for codex:**

```bash
# Detect master skills missing from codex
cd /Users/joshc/.skills && for d in */; do
  name="${d%/}"
  [ -f "$d/SKILL.md" ] && [ ! -e "$HOME/.codex/skills/$name" ] && echo "$name"
done

# Add missing per-skill symlinks
cd ~/.codex/skills && for s in <missing-skills>; do
  ln -s "$HOME/.skills/$s" "$s"
done

# Detect stale codex symlinks (master skill deleted)
find ~/.codex/skills -maxdepth 1 -type l ! -exec test -e {} \; -print
```

This is forward-compatible: as new master skills are added, run the discovery loop to add symlinks. Codex-only skills are untouched.

## Global Hook Paths

All paths are managed by `hook-sync` using `~/.hooks/` as the master store of hook definitions. Hooks are JSON files per definition; some targets embed hooks in a settings file (surgical write required), others accept a directory (symlink-compatible).

| Tool / Platform | Hook Path | Method |
| :--- | :--- | :--- |
| **Master Store** | `~/.hooks/` | (Authoritative, JSON files) |
| **Claude Code (user)** | `~/.claude/settings.json` → `hooks` | Surgical `jq` merge |
| **Claude Code (project)** | `.claude/settings.json` → `hooks` | Surgical `jq` merge |
| **Cursor** | `~/.cursor/hooks/` | Symlink to `~/.hooks/` |
| **Codex CLI** | `~/.codex/hooks.yaml` | Transform (`yq` write) |
| **Gemini CLI** | `~/.gemini/hooks.json` | JSON rewrite |
| **Antigravity** | `~/.gemini/antigravity/hooks.json` | JSON rewrite |

**Note:** Embedded-hook targets (Claude Code) must NEVER be fully overwritten — other user settings share the file. `hook-sync` merges by hook `name` only.

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
