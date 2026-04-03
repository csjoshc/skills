---
name: run-ticket
description: >-
  Run orchestra tickets against a target project using the `orch` CLI.
  The CLI handles interactive prompts, config discovery, and execution.
---

## TL;DR

Run `orch run` from the project directory. The CLI prompts for configuration interactively when flags are omitted.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `orch run` | Interactive run (prompts for profile/mode) |
| `orch run --profile private` | Non-interactive with specific profile |
| `orch run --ticket 001-feature.md` | Run a single ticket |
| `orch list` | Show pending tickets and stages |
| `orch status` | Show recent run results |
| `orch config list` | Show available profiles/models/chains |
| `orch config show private` | Show one profile's full config |
| `orch init` | Scaffold .tickets/, .gitignore entries |
| `orch run --dry-run` | Preview without executing |
| `orch kill` | Kill running process |

## Orchestrator Location

The orchestrator lives at `~/Projects/orchestra`. Either:
- Add it to PATH, or
- Run: `cd ~/Projects/orchestra && orch run --project /path/to/app`

## When to Use

- "run the tickets", "execute ticket X", "start orchestra"
- NOT for generating PRDs (use `write-prd`)
- NOT for writing specs (use `spec-writer`)

## Configuration

`orch` discovers config automatically:
1. CLI flags (highest priority)
2. Environment variables (`ORCHESTRA_PROJECT_DIR`, `ORCHESTRA_PROFILE`)
3. `.orchestra.yaml` in project directory (walk-up from cwd)
4. `~/.config/orchestra/config.yaml` (user global)
5. Built-in `profiles.yaml` (lowest priority)

Run `orch config list` to see loaded profiles, models, and chains.

## Assumptions & Escalation

- **Tier 1 (reversible):** Model timeout — proceed with fallback chain.
- **Tier 2 (logic):** Ambiguous error — check `.orchestra.db`, block if unclear.
- **Tier 3 (security):** Unauthorized access attempt — **STOP**, block and alert.

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.
