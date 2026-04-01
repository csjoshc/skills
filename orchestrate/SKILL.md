---
name: orchestrate
description: >-
  Runs Orchestra tickets against a target project. Prompts for runtime config (profile, mode, model, concurrency)
  then executes the CLI command. Also covers state machine rules, stage transitions, and ticket splitting.
  Use when you want to execute tickets, transition ticket states, or understand orchestration flow.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for orchestrate:**
- **Tier 1 (reversible):** Missing status update — proceed, but add Task N to update the ticket before finishing.
- **Tier 2 (conflict):** Ticket stage transition is illegal (e.g., NEW -> COMPLETE) — **STOP**, clarify via spec-writer.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert.

## TL;DR (Quick Start)

**This skill is a CLI wrapper — it does NOT make code changes directly.** Instead, it:
1. Prompts you for runtime configuration (profile, mode, model, concurrency)
2. Constructs and executes the `python main.py ...` command
3. Reports results from the Orchestra run

Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

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
   - YES → Proceed to "Running Tickets" workflow below.
   - NO → Use **spec-writer** to create tickets first.

2. **What environment are you in?**
   - See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for **Execution Profiles** (`work`, `mixed`, `private`).

3. **Are tickets narrow and well-scoped?**
   - YES → Mode: `single`, consider cheaper model via `--model`.
   - NO (architectural, ambiguous) → Mode: `sequential`, use **Frontier** model.

## Workflow

### Running Tickets

**Important:** This skill is an **interactive CLI wrapper**. You MUST:

1. **Discover tickets** — Scan `.tickets/` directory.
2. **Prompt the user** — Ask for runtime configuration (do NOT assume defaults).
3. **Execute the command** — Run `python main.py ...` with user's choices.
4. **Report outcomes** — Summarize what completed/failed/blocked.

---

**Step 2: Prompt for runtime config (REQUIRED)**

You MUST ask the user these questions:

| Question | Options | Default |
|----------|---------|---------|
| Which profile? | See `ORCHESTRA_DEFAULTS.md` | `private` |
| Which mode? | `single` or `sequential` | `single` |
| Override model?| Any model name, or "none" | Profile default |
| Concurrency? | 1-4 | 1 |
| Dry run? | `yes` (preview only), `no` | `no` |

---

### Step 3: Construct and run the command

Build the command from answers:
```bash
python main.py --project <project_dir> \
  --runtime-profile <profile> \
  --mode <mode> \
  [--model <model>] \
  [--concurrency <N>] \
  [--dry-run]
```

---

## The State Machine (Stages)

Every ticket markdown file must contain a `Stage:` field.

See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for the canonical stage list:
- **`Stage: NEW`**
- **`Stage: SPEC`**
- **`Stage: BUILD`**
- **`Stage: REVIEW`**
- **`Stage: COMPLETE`**

## How to Transition State

When you finish your assigned task, you **MUST** update the stage. Edit the YAML header:
```yaml
Stage: REVIEW
```
**Rule:** Never leave a ticket in the stage you found it in unless interrupted.

## Advanced Details & Deep Dives

See **[`../orchestra/DETAILS.md`](../orchestra/DETAILS.md)** for progressive disclosure on:
- **Inter-Agent Communication Rules** (Mandatory isolation)
- **Detailed Mode Comparisons** (Single vs Sequential)
- **Common Execution Patterns**

## Ticket Splitting (Blast Radius Control)

If a ticket requires modifying **>5 production files** or has 2+ distinct concerns, split it:
1. Create sub-tickets: `01a-slug.md`, `01b-slug.md` (`Stage: NEW`).
2. Update parent to `Stage: COMPLETE` or `BLOCKED`.
3. Tickets >250 lines auto-route to `SPEC_SPLIT`.

## Project Setup

Ensure these are in `.gitignore`:
```
.orchestra.db
.orchestra/
```
