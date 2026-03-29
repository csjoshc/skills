---
name: skill-sync
description: >-
  Synchronizes and audits AI skills across multiple IDEs and CLI agents using ~/.skills
  as the authoritative store. Use when the user asks to sync skills, audit skill symlinks,
  ingest new skills into the master folder, or unify skills across Cursor, Claude Code,
  Gemini/Antigravity, OpenCode, VS Code (global and project-level), or ChatGPT. Handles 
  propagation of removals from master store.
---

# Skill Sync

**Version:** 1.1.0

## Context

The user maintains a "Universal Skills" directory at `~/.skills`. This is the authoritative source for all AI behavior, tool definitions, and SOPs.

## Objectives

1. **Identify New Skills:** Scan the current working directory and common skill locations for any `.md` files that are NOT yet present in `~/.skills`.
2. **Ingest:** If a new skill is found, copy it to `~/.skills` after confirming with the user.
3. **Audit Symlinks:** Verify that each platform path is a **symlink** to `~/.skills`.
4. **Propagate Removals (Audit Stale):** 
   - Identify broken symlinks in platform paths (pointing to deleted master skills).
   - Identify files in "Local-only" platforms that have been deleted from the master `~/.skills` store.
   - Propose removal to keep all tools in sync with the authoritative state.

## Companion Files

Before running the sync audit, review these companion files for authoritative symlink mappings:

- **[GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md)** — Table of global symlinks (`~/.cursor/skills`, `~/.vscode/skills`, etc.) for each agent/IDE. Use this to set up or verify global-level syncing.
- **[PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md)** — Table of project-level symlinks (`./.cursor/skills`, `./.vscode/skills`, etc.). Use this to determine which projects need local skill discovery.

## Execution Steps

### Step 1: Discovery & Audit

- List all files in the current agent's local skill repository.
- Compare filenames and checksums against `~/.skills`.
- Report any "untracked" (new) skills OR "stale" (removed from master but still local) skills.

### Step 2: The "Master Sync"

- **New Skills:** If a skill exists in the local project but not in `~/.skills`, offer to `cp` it to the master directory.
- **Stale Skills:** If a skill is missing from `~/.skills` but still exists in a local-only or non-symlinked folder, offer to `rm` it.
- **Broken Links:** If a symlink exists but its target in `~/.skills` is gone, offer to remove the broken link.

### Step 3: Symlink Verification (The Bridge)

For global symlinks, refer to [GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md) for the complete list of paths to audit.

For each path:
1. Check whether it is a **symlink** (and where it points) or a **regular directory/file**
2. If a path is a physical directory instead of a symlink, alert the user that the platform is "Out of Sync"
3. Propose a migration: Move physical files to `~/.skills` and replace with a symlink: `ln -sf ~/.skills [target_path]`

### Step 4: Project-Level Symlink Setup

Refer to [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md) to determine:
- Whether the current project requires project-level symlinks
- Which symlinks to create (Gemini and VS Code are recommended; others are optional)
- How to handle project-specific (non-synced) skills vs. master-synced skills

For VS Code workspaces specifically:
- Global skills are available via `~/.vscode/skills`
- Project-level `.vscode/skills` can provide local overrides or discovery
- Use `.vscode/settings.json` to prioritize: `"github.copilot.advanced": { "instructionsPath": ".vscode/skills" }`

## Output Format

Always provide a **Sync Status Report** table with the following structure:

| Agent / Platform | Global Status | Project Status | Notes |
| :--- | :--- | :--- | :--- |
| Cursor | Synced / Out of Sync / Missing | Setup / Missing / N/A | Refer to GLOBAL_SYMLINKS.md and PROJECT_SYMLINKS.md |
| Gemini / Antigravity | Synced / Out of Sync / Missing | Setup / Missing / N/A | Gemini natively supports project-level symlinks |
| VS Code | Synced / Out of Sync / Missing | Setup / Missing / N/A | Project-level discovery recommended |
| *[Others]* | Synced / Out of Sync / Missing | Setup / Missing / N/A | See GLOBAL_SYMLINKS.md for details |

Add a **Stale/Broken Links** section below if any removals are required to propagate state from the master store.

## Quick Reference

For detailed setup instructions and platform-specific paths:
- **Setting up global symlinks** → See [GLOBAL_SYMLINKS.md](GLOBAL_SYMLINKS.md)
- **Setting up project-level symlinks** → See [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md)
- **VS Code workspace configuration** → See [PROJECT_SYMLINKS.md](PROJECT_SYMLINKS.md#setup-by-project-type)
