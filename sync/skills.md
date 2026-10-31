
# Skills sync

**Version:** 1.1.0

## Contents

- Windows and Mac use the same entry point
- Context
- Objectives
- Companion Files
- Execution Steps (discovery, master sync, symlink verification, project-level setup)
- Output Format
- Quick Reference

## Windows and Mac use the same entry point

The master stays `~/.skills` on every OS. Python and Git are the only sync prerequisites; no harness CLI or account is needed. Use Windows Python 3.12+ for junction detection (bootstrap installs 3.13); Mac/Linux support Python 3.10+.

| Action | Windows PowerShell | Mac/Linux shell |
|---|---|---|
| Audit | `python "$HOME/.skills/sync/sync.py" --audit` | `python3 ~/.skills/sync/sync.py --audit` |
| Repair | `python "$HOME/.skills/sync/sync.py"` | `python3 ~/.skills/sync/sync.py` |

The audit writes no log or configuration, performs no downloads, and exits nonzero for unresolved source, link or installed-harness permission problems. Repair installs pinned sources, repairs links, then verifies them. Missing harness parent directories are skipped; start/install a harness before syncing it. The `PLATFORMS` table in `sync.py` owns the harness paths.

Windows first tries directory symlinks, then local-volume junctions when symlink privileges are unavailable. Both refer to the same files, so edits are immediately visible through every linked harness. Every native skill root uses individual skill links, preserving physical overrides and private links. A foreign whole-store link requires deliberate reconciliation. Only stale links into the shared store are removed. Codex's existing `.system` remains reachable during migration from a legacy whole-store link.

Windows and WSL have separate homes. Run sync with the interpreter for the consuming OS; Windows clients receive Windows paths. Git checkout updates are separate from link repair. Sync provides discovery; sandbox access and each skill's runtime still depend on the consuming harness and machine. Native MCP projection is a separate Windows gap; running the current Mac MCP sync against Windows configs is not part of this skill-link flow.

Bootstrap's current main uses agent-led setup. Its BOM lists the native prerequisites and the same sync commands; no Windows installer or wrapper is required.

## Context

The user maintains a "Universal Skills" directory at `~/.skills`. This is the authoritative source for all AI behavior, tool definitions, and SOPs.

## Objectives

1. **Identify New Skills:** Scan the current working directory and common skill locations for any `.md` files that are NOT yet present in `~/.skills`.
2. **Ingest:** If a new skill is found, copy it to `~/.skills` after confirming with the user.
3. **Audit Symlinks:** Verify per-skill links to public definitions in `~/.skills`, preserving native private entries.
4. **Propagate Removals (Audit Stale):** 
   - Identify broken symlinks in platform paths (pointing to deleted master skills).
   - Identify files in "Local-only" platforms that have been deleted from the master `~/.skills` store.
   - Propose removal to keep all tools in sync with the authoritative state.

## Companion Files

Before running the sync audit, review these companion files for authoritative symlink mappings:

- **[shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md)** — Table of global and project-level symlinks for each agent/IDE. Use this to set up or verify syncing.

## Execution Steps

### Step 0: Pinned upstream skills

The shared store contains public definitions, including pinned packages under its own `.vendor/`.
Private pack skills stay in the pack and are linked only into approved native consumer roots.
Before any sync or project-link action, `sync.py` refuses external skill imports still present in the shared store.
Reconcile their permitted native readers, verify those readers, then obtain approval to remove the old shared imports and any disallowed consumer links.
Keep Codex personal-only and preserve native private links outside the shared store.

Run `python3 ~/.skills/sync/sync.py` to install missing pinned sources before repairing harness links.
Run it with `--audit` for a read-only check that performs no clone, fetch or checkout.
Both commands fail with a nonzero exit when a source cannot be verified; platform repair stops until that source is resolved.

[`skill-sources.json`](skill-sources.json) records each upstream repository, full commit SHA and package path.
The installer clones into ignored `~/.skills/.vendor/<name>/`, checks out the pin detached, and creates an ignored `~/.skills/<name>` symlink to the package inside that clone.
For Archify, the package path is `archify`, so the skill link resolves to `.vendor/archify/archify/`.
Keep the manifest and installer tracked; keep upstream checkouts and their root skill links ignored.
This manifest replaces the former Archify bundle; the upstream Archify source replaces the vendored bundle.

An ordinary run uses the recorded pin, never upstream's latest branch.
To update, explicitly choose a new upstream commit, change the manifest through a PR, run sync and verify the skill.
The installer refuses dirty checkouts, conflicting directories, unexpected origins, and attached branches when a pin change would move them.
Resolve local work before retrying; do not reset or delete it to make sync pass.
Removing a source requires removing its manifest entry, root skill link and corresponding per-skill harness links together.
Retain its ignored checkout until any local work is saved, then run sync to audit the remaining skills.

Tests: `python3 -I ~/.skills/sync/test_skill_sources.py` uses real local Git repositories to exercise fresh installs, pin changes, read-only audits and protection of local work.

### Step 1: Discovery & Audit

- List all files in the current agent's local skill repository.
- Compare filenames and checksums against `~/.skills`.
- Report any "untracked" (new) skills OR "stale" (removed from master but still local) skills.

### Step 2: The "Master Sync"

- **New Skills:** Offer to copy a missing public skill to `~/.skills`; private definitions remain in their owning pack or native consumer root.
- **Stale Skills:** If a skill is missing from `~/.skills` but still exists in a local-only or non-symlinked folder, offer to `rm` it.
- **Broken Links:** If a symlink exists but its target in `~/.skills` is gone, offer to remove the broken link.

### Step 3: Symlink Verification (The Bridge)

For global symlinks, refer to [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md) for the complete list of paths to audit.

For each path:
1. Check whether it is a **symlink** (and where it points) or a **regular directory/file**
2. Expect a real native directory containing per-skill links; a whole-store symlink needs migration.
3. Reconcile public definitions with `~/.skills`; preserve private definitions in approved native roots rather than moving them into the shared store.

**Codex exception (per-skill symlinks):** `~/.codex/skills/` is a real directory containing per-skill symlinks because Codex installs system-managed skills under `.system/` (`imagegen`, `openai-docs`, `slides`, `spreadsheets`, etc.). Do NOT replace it with a single symlink to `~/.skills` — that shadows `.system` and `sync.py` must never `rmtree` it.

`sync/sync.py` uses per-skill links for every supported consumer.
Repair converts a whole-store link only when it points to `~/.skills`, then adds or fixes public skill links while preserving native entries and Codex's `.system/`.
A foreign root is a reconciliation blocker, not permission to replace it.

OMP reads skills from `~/.omp/agent/skills`. Shared skills are linked individually from `~/.skills`; OMP-local skills remain in place. Run `python3 ~/.skills/sync/sync.py --audit` to inspect the path and `python3 ~/.skills/sync/sync.py` to repair it.

Use the canonical sync command for Codex so the shared-store ownership check runs before linking:

```bash
python3 ~/.skills/sync/sync.py
```

If `.system/` is missing, open Codex Desktop or run the Codex CLI once — it reinstalls embedded system skills automatically.

### Step 4: Project-Level Symlink Setup

Refer to [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md) to determine:
- Whether the current project requires project-level symlinks
- Which symlinks to create (VS Code is recommended; others are optional)
- How to handle project-specific (non-synced) skills vs. master-synced skills

**Claude Code (project-level) — copy, not symlink:** Claude Desktop is sandboxed and cannot follow symlinks outside the workspace. Use the filtered copy below instead of a symlink (about 2 MB; a plain `cp -r` drags in `.git`, eval runs and mirrors, over 30 MB).

```bash
python3 ~/.skills/sync/sync.py --audit &&
  rsync -aL --exclude='.git' --exclude='.vendor' --exclude='.backup' --exclude='synced' --exclude='.trash' --exclude='__pycache__' --exclude='evals/runs' --exclude='*.log' --exclude='/master' ~/.skills/ .claude/skills/
```

Run it from the project root.
During sync, compare the managed public copies against `~/.skills`; remove stale public copies only with approval, preserving project-private content.
Global `~/.claude/skills` remains a separate directory of per-skill links.
`-L` materializes upstream skill links inside the sandboxed project copy; excluding `.vendor` keeps the upstream repository and Git metadata out.

For VS Code workspaces specifically:
- Global Copilot skills are available via native `~/.copilot/skills`; `~/.vscode/skills` is not a native personal discovery root.
- Project-level `.vscode/skills` can provide local overrides or discovery
- Use `.vscode/settings.json` to prioritize: `"github.copilot.advanced": { "instructionsPath": ".vscode/skills" }`

## Output Format

Always provide a **Sync Status Report** table with the following structure:

| Agent / Platform | Global Status | Project Status | Notes |
| :--- | :--- | :--- | :--- |
| Cursor | Synced / Out of Sync / Missing | Setup / Missing / N/A | Refer to shared/SYMLINK_MAP.md |
| Claude Code | Synced / Out of Sync / Missing | Setup / Stale / Missing / N/A | Project-level uses `cp -r` (not symlink) |
| Codex | Synced / Out of Sync / Missing | N/A | Global `~/.codex/skills` symlink required |
| VS Code | Synced / Out of Sync / Missing | Setup / Missing / N/A | Project-level discovery recommended |
| *[Others]* | Synced / Out of Sync / Missing | Setup / Missing / N/A | See shared/SYMLINK_MAP.md |

Add a **Stale/Broken Links** section below if any removals are required to propagate state from the master store.

## Permissions column

The audit's Permissions column says whether a tool can read `~/.skills` without asking.

| Value | Meaning |
|---|---|
| OK | Nothing to configure (workspace trust), or the allow rule is present. |
| Missing | opencode only: no allow rule for `~/.skills`. A repair run adds one. |
| Unmanaged | Codex: no managed config exists. Nothing is written, and it is not a failure. |

opencode v2 takes a `permissions` rule array in `~/.config/opencode/opencode.json`.
The repair adds two rules and leaves every other key and the file mode alone:

```json
{ "action": "external_directory", "resource": "~/.skills/*", "effect": "allow" }
{ "action": "read", "resource": "~/.skills/*", "effect": "allow" }
```

`*` also matches `/`, so one rule covers the whole tree.
The older `permission.external_directory` object is still recognised by the audit.
Without the rules, an `ask` default rejects the read in a non-interactive `opencode run`, which was seen in a test.
`test_sync_permissions.py` covers the audit and repair.

## Quick Reference

For detailed setup instructions and platform-specific paths:
- **Setting up symlinks** → See [shared/SYMLINK_MAP.md](../shared/SYMLINK_MAP.md)
