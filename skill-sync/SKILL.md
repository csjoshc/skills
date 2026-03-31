---
name: skill-sync
description: Synchronizes and audits AI skills across multiple IDEs and CLI agents across macOS, Linux, and Windows.
---

# Skill Sync

## TL;DR (Quick Start)

Synchronize and audit AI skills from a master store (`~/.skills`) to platform-specific directories (Cursor, Gemini, VS Code) using symlinks. Ensures consistency across all AI agents and IDEs.

**When to use:** Setting up a new IDE, troubleshooting missing skills, or after manual updates to the master skill store.

**Invocation:**
```bash
python3 ~/.skills/skill-sync/sync.py
```

## When to Use
- Syncing new skills from `~/.skills` to all platforms.
- Auditing existing symlinks for health and correct targets.
- Repairing broken links after an OS update or file move.
- **NOT for:** Editing skills directly (always edit in `~/.skills/`).

## Decision Tree

1. **Are you on Windows?**
   - YES → Use `mklink /D` via CMD/Git Bash. Refer to `GLOBAL_SYMLINKS.md` Windows columns.
   - NO (macOS/Linux) → Use `ln -sf`. Refer to POSIX columns.

2. **Is a platform directory missing its skills link?**
   - YES → Create symlink pointing to the master store.
   - NO → Audit existing link integrity.

3. **Did a skill get deleted from the master store?**
   - YES → The sync audit will identify the stale link; confirm and remove.

## Workflow

### 1. Environment Check
Check if you are running on Windows vs macOS/Linux. Refer to [GLOBAL_SYMLINKS.md](./GLOBAL_SYMLINKS.md) for correct paths.

### 2. Platform Audit
Iterate through platforms (Cursor, Gemini, VS Code/Copilot). Verify each skills directory is a symlink pointing to `~/.skills`.

### 3. Verification & Repair
- Report status: "Synced", "Out of Sync", or "Broken".
- Re-create broken or missing links using OS-appropriate commands.

### 4. Project-Level Setup
Optionally link project-specific `.skills/` directories to the master store for local agent access.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing symlink — proceed with re-creation.
- **Tier 2 (conflict):** Physical directory exists where symlink should be — **STOP**, backup content to master store before replacing.
- **Tier 3 (permission):** Permission denied on `mklink` (Windows) — block and request Developer Mode or Admin rights.

## Examples (Few-Shot)

**Example 1: Basic Audit**
Input: "Audit my skill symlinks"
Output: Status table showing all platforms are synced to `~/.skills`.

**Example 2: Repairing Broken Link**
Input: "Fix broken skills in Cursor"
Output: Command execution of `mklink /D` (Windows) or `ln -sf` (POSIX) to restore the link.

## Related Skills
| Skill | When to use instead |
|-------|---------------------|
| project-onboarding | When first setting up a new project |
| mcp-sync | For syncing Model Context Protocol settings |
