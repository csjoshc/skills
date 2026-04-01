---
name: orchestrate
description: >-
  Runs Orchestra tickets against a target project. Prompts for runtime config (profile, mode, model, concurrency)
  then executes the CLI command. Also covers state machine rules, stage transitions, and ticket splitting.
  Use when you want to execute tickets, transition ticket states, or understand orchestration flow.

## TL;DR (Quick Start)

**This skill is a CLI wrapper — it does NOT make code changes directly.** Instead, it:
1. Prompts you for runtime configuration (profile, mode, model, concurrency)
2. Constructs and executes the `python main.py ...` command
3. Reports results from the Orchestra run

Headless, file-driven agent orchestration. Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

**When to use:** "run the tickets", "execute orchestra", "run tickets with profile X".

**Invocation:**
- **Run tickets:** This skill will prompt you for config, then execute `python main.py ...`
- **Transition state:** Edit the `Stage:` field in the ticket YAML header.

## Important: This Skill Does NOT

- ❌ Make code changes to tickets or implementation files
- ❌ Implement ticket requirements directly
- ❌ Act as the agent that writes code

**The chat agent invoking this skill is the ORCHESTRATOR, not the IMPLEMENTER.** Orchestra spawns external CLI agents (opencode, cursor, gemini, etc.) that do the actual coding work.

## Decision Tree

1. **Do tickets exist and are ready to run?**
   - YES → Go to "Running Tickets" workflow below
   - NO → Use spec-writer to create tickets first

2. **What environment are you in?**
   - Work laptop, proprietary code → Profile: `work` (Cursor only)
   - Work laptop, side projects → Profile: `mixed` (Cursor + opencode)
   - Home computer → Profile: `private` (opencode + qwen, default)

3. **Are tickets narrow and well-scoped?**
   - YES → Mode: `single`, consider cheaper model via `--model`
   - NO (architectural, ambiguous) → Mode: `sequential`, use frontier model

## Workflow

### Running Tickets

**Important:** This skill is an **interactive CLI wrapper**. When invoked, you must:

1. **Discover tickets** — Scan `.tickets/` directory
2. **Prompt the user** — Ask for runtime configuration (do NOT assume defaults)
3. **Execute the command** — Run `python main.py ...` with user's choices
4. **Report outcomes** — Summarize what completed/failed/blocked

---

**Step 1: Discover tickets**

Determine the target project directory:
- Use the **current working directory** (where the skill was invoked)
- Append OS-specific path separator + `.tickets/`:
  - Windows: `<cwd>\.tickets\`
  - macOS/Linux: `<cwd>/.tickets/`

Check for pending tickets:
```bash
ls .tickets/*.md
```

Report how many tickets exist and their current stages.

**Step 2: Prompt for runtime config (REQUIRED)**

**Do not skip this step.** You MUST ask the user these questions before running:

| Question | Options | Default |
|----------|---------|---------|
| Which profile? | `work`, `mixed`, `private`, `cost_saver`, `qwen_chain`, `qwen_only`, `opencode_stepfun` | `private` |
| Which mode? | `single` (one agent), `sequential` (spec→build→review) | `single` |
| Override model? | Any model name, or "none" | Profile default |
| Concurrency? | 1-4 | 1 (or number of independent tickets) |
| Dry run? | `yes` (preview only), `no` (execute) | `no` |

Use `ask_user_question` or equivalent to get explicit user input for each question.

**Note on custom profiles:** If the user wants a profile not in the standard list (e.g., `qwen_chain`), they must provide a custom runtime config file via `--runtime-config`.

**Step 3: Construct and run the command**

Build the command from answers:
```bash
python main.py --project <project_dir> \
  --runtime-profile <profile> \
  --mode <mode> \
  [--runtime-config <path>] \
  [--model <model>] \
  [--concurrency <N>] \
  [--dry-run]
```

**CLI Arguments Reference:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--project <path>` | ✅ | Absolute path to target project |
| `--runtime-profile <name>` | ❌ | Profile name: `work`, `mixed`, `private`, `cost_saver`, `qwen_chain`, `qwen_only`, `opencode_stepfun` (default: `private`) |
| `--runtime-config <path>` | ❌ | Optional custom runtime config YAML/JSON (rarely needed) |
| `--mode <mode>` | ❌ | `single` or `sequential` (default: `single`) |
| `--model <name>` | ❌ | Override model (e.g., `qwen3.5-plus`, `opencode/big-pickle`) |
| `--concurrency <N>` | ❌ | Parallel tickets 1-4 (default: 1) |
| `--dry-run` | ❌ | Preview tickets and routing without executing |
| `--debug` | ❌ | Enable debug logging |

Execute it and report results.

**Step 4: Report outcome**

After execution, report:
- How many tickets completed
- Any failures or blocks
- Which stages tickets ended up in

### Profile Reference

| Profile | Where | Runtimes | Models |
|---------|-------|----------|--------|
| **work** | Work laptop, proprietary code | Cursor only | Sonnet 4.6 (or Opus/Composer) |
| **mixed** | Work laptop, side projects | Cursor + opencode | Sonnet 4.6 + big-pickle |
| **private** | Home computer | opencode + qwen | big-pickle + qwen3.5-plus |
| **cost_saver** | Cost-optimized | qwen → opencode | qwen3.5-plus → big-pickle |
| **qwen_chain** | Qwen-first fallback chain | qwen → opencode → gemini → cursor | qwen3.5-plus → qwen3.6-plus-free → gemini-3-flash → Composer 2 |
| **qwen_only** | Qwen single runtime | qwen only | qwen3.5-plus |
| **opencode_stepfun** | Opencode with StepFun model | opencode only | openrouter/stepfun/step-3.5-flash:free |

### Model Tiers

| Tier | Models | When |
|------|--------|------|
| **Frontier** | Opus 4.6, Sonnet 4.6, opencode/big-pickle | Complex/ambiguous tickets |
| **Standard** | Composer 2 Fast, qwen3.5-plus | Narrow, well-scoped tickets |

**Rule of thumb:** If tickets are <50 lines with clear acceptance criteria → Standard. If architectural → Frontier.

---

## The State Machine

Every ticket markdown file must contain a header with a `Stage:` field.

### Stages

1. **`Stage: NEW`** → Initial state. Ready for execution.
2. **`Stage: SPEC`** → Planner breaking ticket into handoff plan.
3. **`Stage: SPEC_SPLIT`** → Ticket oversized (>250 lines), being split into sub-tickets.
4. **`Stage: BUILD`** → Ready for implementation.
5. **`Stage: REVIEW`** → Implementation complete, ready for audit.
6. **`Stage: COMPLETE`** → Done. Terminal state.

**Exception States:** `BLOCKED`, `FAILED`

### Mode-Specific Routing

**Single mode** (default):
```
entry → build → complete
```

**Sequential mode**:
```
entry → spec → build → review → complete
```

## How to Transition State

When you finish your assigned task, you **MUST** update the stage. Edit the YAML header:

```yaml
Stage: REVIEW
```

**Rule:** Never leave a ticket in the stage you found it in unless interrupted.

## Ticket Splitting (Blast Radius Control)

If a ticket requires modifying >5 files or has 2+ distinct concerns, split it:

1. Create sub-tickets: `01a-ticket-name.md`, `01b-ticket-name.md`
2. Each sub-ticket gets `Stage: NEW`
3. Update parent to `Stage: COMPLETE` or `BLOCKED`
4. Graph auto-routes oversized tickets (>250 lines) to `SPEC_SPLIT`

## Inter-Agent Communication

- **Do NOT** leave messages for other agents in ticket body (except blockers)
- **Do NOT** wrap file outputs in triple backticks — write raw files to disk
- Handoff context goes to `.handoff/plan-<slug>.md` using the `handoff` skill

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for orchestrate:**
- **Tier 1 (reversible):** Missing status update — proceed, but add Task N to update the ticket before finishing.
- **Tier 2 (logic):** Ticket stage transition is illegal (e.g., NEW -> COMPLETE) — **STOP**, clarify via spec-writer.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert immediately.

## Project Setup

When running Orchestra on a new project, ensure these are in `.gitignore`:

```
.orchestra.db
.orchestra/
```

These are runtime artifacts and should not be committed.
