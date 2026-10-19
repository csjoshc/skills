# Symlink Map

Authoritative symlink mapping for all AI coding agents. Used by `onboard` and `sync`.

## Global Symlinks

All paths symlink to the master store at `~/.skills`.

| Tool / Platform | Global Path | Target |
| :--- | :--- | :--- |
| **Master Store** | `~/.skills` | (Authoritative) |
| **Codex** | `~/.codex/skills/<name>` | `~/.skills/<name>` (per-skill, see note) |
| **Cursor (Skills)** | `~/.cursor/skills` | `~/.skills` |
| **Claude Code** | `~/.claude/skills` | `~/.skills` |
| **Antigravity** | `~/.gemini/antigravity/skills` | `~/.skills` |
| **OpenCode** | `~/.config/opencode/skills` | `~/.skills` |
| **pi** (`pi_agent_rust`) | `~/.pi/agent/skills/<name>` | `~/.skills/<name>` (per-skill, see pi note) |
| **pi, gateway profile** | `~/.gateway-pi/skills/<name>` | `~/.skills/<name>` (per-skill, see pi note) |
| **ChatGPT** | `~/Documents/ChatGPT/CustomInstructions` | `~/.skills` (manual sync) |

**Note:** If a path does not exist, create parent directories before symlinking.

**pi note:** pi treats every markdown file in its skills folder as a skill, so a single symlink to `~/.skills` made it warn about the root `.md` files (`AGENTS.md`, `GEMINI.md`, `PLAYBOOK.md`, `STANDARDS.md`). pi's skills path is therefore a real directory of per-skill symlinks, kept by `sync/sync.py` the same way as Codex's. The global memory file needs no link, because pi already reads `~/AGENTS.md` as an ancestor of any directory under `$HOME`.

### Codex exception: per-skill symlinks

Codex installs system-managed skills (`imagegen`, `openai-docs`, `plugin-creator`, `skill-creator`, `skill-installer`, `slides`, `spreadsheets`) directly into `~/.codex/skills/`, marked by `~/.codex/skills/.system/.codex-system-skills.marker`. These are not portable to other agents.

To preserve codex-only content while still syncing master skills, `~/.codex/skills/` is a real directory containing **per-skill symlinks** to `~/.skills/<name>/`. Codex-managed skills coexist as plain directories.

**Sync workflow for codex:**

```bash
# Detect master skills missing from codex
cd ~/.skills && for d in */; do
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

## Global Memory File

`~/AGENTS.md` is the single source. Every harness reads it through a symlink or import.

| Tool / Platform | Path | Method |
| :--- | :--- | :--- |
| **Master** | `~/AGENTS.md` | (Authoritative, real file) |
| **Claude Code** | `~/.claude/CLAUDE.md` | `@/Users/joshc/AGENTS.md` import (Claude Code reads only a project-level AGENTS.md, and only when no CLAUDE.md or CLAUDE.local.md is in that folder or above) |
| **Codex** | `~/.codex/AGENTS.md` | Symlink |
| **OpenCode** | `~/.config/opencode/AGENTS.md` | Symlink |
| **Antigravity** | `~/.gemini/antigravity/AGENTS.md` | Symlink |
| **Cursor / Copilot** | (none) | No global file; use project `AGENTS.md` |

Projects inherit `~/AGENTS.md` from the home directory; keep project-specific rules in the repo root `AGENTS.md` without a symlink to the global file.

## Project-Level Symlinks

| Tool / Platform | Project Path | Target | Method | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Universal Shim** | `.skills/` | Granular links to `~/.skills/` | Symlink | General discovery (primary onboarding output) |
| **Claude Code** | `.claude/skills` | `~/.skills` | **Filtered copy** (see sync/skills.md) | Materializes upstream skill links for sandboxed projects |
| **Cursor** | `.cursor/rules/master` | `~/.skills` | Symlink | .mdc indexing |
| **VS Code / Copilot** | `.vscode/skills` | `~/.skills` | Symlink | Copilot workspace settings |
| **Aider** | `.aider.conf.yml` | (Refers to AGENTS.md) | Config | Config-based |
| **Windsurf** | `.windsurfrules` | (Refers to AGENTS.md) | Shim file | Shim file |
| **Cline** | `.clinerules` | (Refers to AGENTS.md) | Shim file | Shim file |

**Note:** All project-level skill folders (`.skills/`, `.claude/skills/`, etc.) MUST be added to the project's `.gitignore` and `.cursorignore`.
Claude Desktop is sandboxed and cannot follow symlinks outside the workspace; use the filtered `rsync -aL` command in [sync/skills.md](../sync/skills.md) and re-copy when the master store changes.
The global symlink (`~/.claude/skills → ~/.skills`) is unaffected.

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
