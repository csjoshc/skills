---
name: run-ticket
description: >-
  Run orchestra tickets against a target project. Prompts for runtime config
  (models, profiles, fallback chains) with cursor as default. Supports
  targeting the current working directory or a specific project directory.
---

## TL;DR (Quick Start)

Executes Orchestra tickets against a target project root using a selectable model runtime (Cursor, OpenCode, Gemini). Handles fallback chains and execution monitoring.

**Orchestrator code lives outside the target repo:** resolve the Python entry under **`~/Projects/orchestrate`** (see [Orchestrator resolution](#orchestrator-resolution)). Do **not** assume `main.py` exists in the app project’s cwd.

**When to use:** "run tickets", "execute ticket 001", "start orchestra".

**Invocation:**
```bash
run-ticket
```

## Decision Tree

1. **Which project are you targeting?**
   - Current directory → Use default path.
   - Specific repo → Provide `--project /path/to/repo`.

2. **Which model should lead?**
   - Cursor (macOS) → Best for complex reasoning.
   - OpenCode/Qwen → Best for high-volume free tier.

3. **Is the task mission-critical?**
   - YES → **MANDATORY** Enable fallback chain (`cursor_opencode` or `free`).
   - NO → Use `only_cursor` or single model.

4. **Do you need to monitor details?**
   - YES → Use **live** mode (blocks CLI).
   - NO → Use **background** mode.

## Workflow

## Orchestrator resolution

The ticket runner is **not** bundled inside arbitrary product repos. Before any execution step:

1. **Canonical checkout:** `ORCHESTRA_HOME` = **`~/Projects/orchestrate`** (expand `~` to the user’s home directory, e.g. `/Users/<user>/Projects/orchestrate` on macOS).
2. **Verify it exists:** `test -d "$HOME/Projects/orchestrate"` (or list that path). If missing, tell the user the orchestrator repo is absent or not cloned to that path—do **not** silently fall back to inventing a different command without stating this.
3. **Resolve the Python entrypoint** inside `ORCHESTRA_HOME`:
   - Prefer **`main.py`** at the root of that repo if present.
   - If there is no `main.py`, inspect the repo for the real entry (e.g. `pyproject.toml` `[project.scripts]`, `python -m <package>`, or a `cli/` script) and use **that** path—still under `ORCHESTRA_HOME`.
4. **Run from `ORCHESTRA_HOME`:** Either `cd ~/Projects/orchestrate && python main.py ...` or `python ~/Projects/orchestrate/main.py ...` so the working directory and imports match how the orchestrator is meant to run.
5. **Target project stays separate:** `--project` (or equivalent) must still point at the **customer repo** root (the one containing `.tickets/`), not `ORCHESTRA_HOME`.

**Failure mode:** If `~/Projects/orchestrate` is missing or has no runnable entrypoint, **stop** and report that explicitly. Optionally offer to **implement ticket work manually** in the target repo (same as when no orchestrator is installed)—but never claim “no CLI” without checking **`~/Projects/orchestrate` first**.

## When to Use

- User says "run the tickets", "execute ticket X", "run orchestra"
- User wants to process pending tickets against a project
- User says "run-ticket" directly
- NOT for generating PRDs (use `write-prd`)
- NOT for writing specs (use `spec-writer`)

## Invocation

### Interactive (default)
```
run-ticket
```

### Target specific project directory
```
run-ticket --project /path/to/project
```

### Run a single ticket
```
run-ticket --project /path/to/project --ticket 001-feature-name.md
```

### Dry run (preview only)
```
run-ticket --project /path/to/project --dry-run
```

### Non-interactive (use profile directly)
```
run-ticket --project /path/to/project --profile only_cursor
```

## Directory Routing

| Scenario | Target |
|----------|--------|
| No directory specified | Current working directory (reads `.tickets/` and `.orchestra.db` at cwd) |
| `--project` specified | Target project root (reads `.tickets/` and creates `.orchestra.db` there) |

## Runtime Configuration Prompt

When invoked interactively (no `--profile` flag), the skill prompts the user through 5 steps:

### Step 1: Select Project Directory

If user didn't specify `--project`, ask:

```
Which project directory should I run tickets against?
  1. Current directory: /path/to/cwd
  2. Specify custom path

[Default: 1 (current directory)]
```

### Step 2: Select Ticket Scope

```
How many tickets should I process?
  1. All pending tickets (default — processes runnable tickets in order)
  2. Single ticket (prompts for ticket number/name)
  3. Specific tickets (enter comma-separated list, e.g., "001, 003, 005")

[Default: 1 (all pending)]
```

### Step 3: Select Primary Runtime

Present the user with available runtimes:

```
=== Runtime Configuration ===

Select primary runtime:
  1. cursor        (Composer 2 — default, macOS only)
  2. opencode      (opencode/qwen3.6-plus-free)
  3. gemini        (gemini-3-flash-preview)
  4. qwen          (qwen3.5-plus)
  5. ollama        (local, requires ollama serve)

[Default: 1 (cursor)]
```

### Step 4: Configure Fallback Chain

```
Enable fallback chain if primary runtime fails?
  1. Yes — use default chain for selected runtime
  2. Yes — customize fallback order
  3. No — single runtime only (fail if primary fails)

[Default: 1 (yes, default chain)]
```

**If user selects "Yes — customize fallback order":**
Present an interactive multi-select prompt showing all available runtimes (excluding the primary):

```
Select fallback order (select in priority order, highest first):
  [ ] opencode    (opencode/qwen3.6-plus-free)
  [ ] gemini      (gemini-3-flash-preview)
  [ ] qwen        (qwen3.5-plus)
  [ ] cursor      (Composer 2, macOS only)
  [ ] ollama      (local ollama)

Tip: Select multiple options. Order matters — first selected = first fallback.
```

Construct the chain as: `[primary] + [selected fallbacks in order]`

Example: If primary=qwen and user selects [gemini, opencode, cursor], chain becomes:
`qwen → gemini → opencode → cursor`

### Step 5: Execution Mode (Background vs Live)

```
Execution output mode:
  1. live          (stream output to this CLI session — blocks until complete)
  2. background    (run in background, you can continue using the CLI)

[Default: 1 (live)]
```

### Optional: Advanced Settings

After the 5 main steps, offer:

```
Advanced options (press Enter to skip)?
  - Attempt timeout: [900s]
  - Run timeout: [3600s]
  - Max runtime switches: [2]
  - Context window (ollama): [131072]
  - Debug mode: [off]
```

## Execution

After the 5-step configuration, the skill constructs and runs the command using the **resolved orchestrator** under `~/Projects/orchestrate` (see [Orchestrator resolution](#orchestrator-resolution)). Replace `main.py` with the actual entry file if different.

### Live Mode (default)
Runs in foreground, streaming output to the current CLI session:
```bash
cd ~/Projects/orchestrate && python main.py \
  --project /path/to/project \
  --runtime-profile <profile_name> \
  [--ticket <ticket_file>] \
  [--dry-run] \
  [--debug] \
  [--ctx <context_size>]
```

### Background Mode
Runs in background with output redirected, provides PID for monitoring:
```bash
cd ~/Projects/orchestrate && python main.py \
  --project /path/to/project \
  --runtime-profile <profile_name> \
  [--ticket <ticket_file>] \
  [--dry-run] \
  [--debug] \
  [--ctx <context_size>] &
```

### Profile Matching

If the user's selections match a pre-built profile in `runtime-policy.yaml`, use that profile name:

| Selection | Matching Profile |
|-----------|-----------------|
| cursor, single | `only_cursor` |
| cursor, chain [cursor, opencode] | `cursor_opencode` |
| opencode, chain [opencode, qwen, gemini, cursor] | `opencode_chain` |
| cursor, tiered | `cursor` (tier preset) |
| opencode/gemini/qwen, tiered | `free` (tier preset) |

If no matching pre-built profile exists, write a temporary runtime config:
```bash
cd ~/Projects/orchestrate && python main.py \
  --project /path/to/project \
  --runtime-config /tmp/orchestra-runtime-<timestamp>.yaml \
  --runtime-profile default
```

## Available Runtimes

| Runtime | Default Model | Requires |
|---------|--------------|----------|
| `cursor` | Auto (Composer 2) | Cursor installed and licensed |
| `opencode` | opencode/qwen3.6-plus-free | opencode installed |
| `gemini` | gemini-3-flash-preview | Google API key |
| `qwen` | qwen3.5-plus | API access |
| `ollama` | varies (user-configured) | Ollama running locally |

## Pre-built Profiles (from runtime-policy.yaml)

| Profile | Primary | Chain | Mode | Description |
|---------|---------|-------|------|-------------|
| `default` | cursor | [cursor] | single | Cursor-only, no fallback |
| `only_cursor` | cursor | [cursor] | single | Same as default, explicit |
| `cursor_opencode` | cursor | [cursor, opencode] | chain | Cursor with opencode fallback |
| `opencode_chain` | opencode | [opencode, qwen, gemini, cursor] | chain | Full fallback chain |
| `free` | varies | tiered | tiered | Free-model tier presets |
| `cursor` | varies | tiered | tiered | Claude/Cursor tier presets |

## Monitoring Output

During execution, the skill reports:

```
[timestamp] Found N ticket(s): X feature, Y bugfix, Z refactor
┌─────────────────────────────────────┐
│ Starting                            │
│ Project : /path/to/project          │
│ Runtime : cursor                    │
│ Model   : Auto                      │
│ Policy  : only_cursor               │
│ Runnable: 3 (of 5 pending)          │
└─────────────────────────────────────┘

── [Type: feature] 001-add-auth.md ──
COMPLETE

── [Type: bugfix] 002-fix-login.md ──
FAILED

┌─────────────────────────────────────┐
│ Summary                             │
│ Completed : 1                       │
│ Incomplete: 002-fix-login.md        │
└─────────────────────────────────────┘
```

## Common Mistakes

- **`python main.py` in the product repo** — the orchestrator is under **`~/Projects/orchestrate`**, not the app monorepo; running `which`/glob in the wrong tree yields “not found” and wasted turns. Always resolve the entrypoint there first.
- **Skipping existence checks** — if `~/Projects/orchestrate` is missing, say so and either clone/install per user docs or switch to manual ticket execution—do not pretend the generic skill invocation exists.
- **Running without `--project` in wrong directory** — skill should detect missing `.tickets/` and prompt for project path
- **Using `free` profile without API keys** — tiered profiles require valid credentials for all listed models
- **Forgetting `ollama serve`** — ollama runtime requires the daemon running locally
- **Running `--dry-run` thinking it executes** — dry-run only shows pending tickets, does not run the graph

## CLI Reference

All examples assume the orchestrator repo at **`~/Projects/orchestrate`** and entry **`main.py`**—adjust if that repo uses a different module/script name.

```bash
cd ~/Projects/orchestrate && python main.py --project /path/to/project
cd ~/Projects/orchestrate && python main.py --project /path/to/project --ticket 001-feature.md
cd ~/Projects/orchestrate && python main.py --project /path/to/project --dry-run
cd ~/Projects/orchestrate && python main.py --project /path/to/project --debug
cd ~/Projects/orchestrate && python main.py --project /path/to/project --runtime-profile only_cursor
cd ~/Projects/orchestrate && python main.py --project /path/to/project --runtime-config custom.yaml
cd ~/Projects/orchestrate && python main.py --project /path/to/project --ctx 65536
```

### Key CLI Options

| Flag | Purpose |
|------|---------|
| `--project` | Absolute path to the target project directory |
| `--ticket` | Run a single specific ticket file |
| `--runtime-config` | Custom runtime policy (.json/.yml/.yaml) |
| `--runtime-profile` | Profile name from runtime-policy.yaml (default: default) |
| `--dry-run` | Show pending tickets without executing |
| `--debug` | Enable debug logging |
| `--ctx` | Ollama context window size (default: 131072) |

## Assumptions & Escalation

- **Tier 1 (reversible):** Model timeout/quota exceeded — proceed with fallback chain automatically.
- **Tier 2 (logic):** Ticket fails with ambiguous error — check project `.orchestra.db`, block if logs are unclear.
- **Tier 3 (security):** Ticket implementation attempts unauthorized external network access — **STOP**, block and alert immediately.

## Examples (Few-Shot)

**Example 1: Initializing execution**
Input: "Run the pending tickets in this repo"
Output: Interactive prompt suite (Project → Scope → Runtime → Fallback → Mode).

**Example 2: Single-ticket targeted run**
Input: "Execute ticket 005 with opencode"
Output: Non-interactive execution of ticket 005 using the `only_opencode` profile.
