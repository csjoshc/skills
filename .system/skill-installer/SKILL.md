---
name: skill-installer
description: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
metadata:
  short-description: Install curated skills from openai/skills or other repos
---

# Skill Installer

## TL;DR (Quick Start)

Installs Codex skills from the `openai/skills` curated list or any GitHub repo path. Normalize paths to `$CODEX_HOME/skills/`.

**When to use:** "install a skill", "list available skills", "download from github".

**Invocation:**
```bash
python scripts/install-skill-from-github.py --repo <owner>/<repo>
```

## Decision Tree

1. **Which source?**
   - Curated list → Default (openai/skills/.curated).
   - Experimental → Use `--path skills/.experimental`.
   - External repo → Use `--repo <owner>/<repo>`.

2. **Installation path exists?**
   - NO → Proceed with install.
   - YES → **BLOCK**; prompt user to overwrite or use different name.

3. **Does the skill exist in `.system/`?**
   - YES → Skip install; they are preinstalled.
   - NO → Proceed.

## Quick start

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Install skills with the helper scripts.

## Communication

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, list from `.experimental` instead of `.curated` and label the source accordingly:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Restart Codex to pick up new skills."

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --format json`
- Example (experimental list): `scripts/list-skills.py --path skills/.experimental`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into `$CODEX_HOME/skills/<skill-name>` (defaults to `~/.codex/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from `$CODEX_HOME/skills`.

## Assumptions & Escalation

- **Tier 1 (reversible):** Repo branch missing — default to `main` and notify user.
- **Tier 2 (conflict):** Git sparse checkout fails — **STOP**, attempt direct download mode.
- **Tier 3 (security):** Private repo requested without token — **STOP**, ask user to set `GH_TOKEN`.

## Examples (Few-Shot)

**Example 1: Installing curated skill**
Input: "Install the google-docs skill"
Output: `install-skill-from-github.py --repo openai/skills --path skills/.curated/google-docs`.

**Example 2: Listing experimental skills**
Input: "What experimental skills do you have?"
Output: `list-skills.py --path skills/.experimental`.
