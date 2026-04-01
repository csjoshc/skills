---
name: orchestra
description: >-
  CLI ticket runner that executes .tickets/*.md through a LangGraph state machine.
  Covers execution modes (single vs sequential), concurrent batching, runtime failover,
  and how to feed tickets from spec-writer/write-prd into the runner.
  Use when running tickets, configuring modes, or debugging execution.

## Assumptions & Escalation

- **Tier 1 (reversible):** Wrong mode choice — re-run with different `--mode`, no data loss.
- **Tier 2 (conflict):** Ticket dependencies form a cycle — **STOP**, fix `Depends-On:` edges.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert immediately.

## TL;DR (Quick Start)

Headless, file-driven agent orchestration. Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

**When to use:** Running tickets, choosing execution mode, configuring concurrency, debugging failures.

**Invocation:**
```bash
# Run all pending tickets (single mode, default)
python main.py --project ~/Projects/myapp

# Sequential mode for less capable providers
python main.py --project ~/Projects/myapp --mode sequential

# Parallel batch execution
python main.py --project ~/Projects/myapp --concurrency 4
```

## Decision Tree

1. **What model/provider are you using?**
   - Capable (Sonnet, Opus, etc.) → `--mode single` (default)
   - Less capable (smaller providers) → `--mode sequential`

2. **Are tickets independent (no Depends-On edges between them)?**
   - YES → `--concurrency N` (up to 4) for parallel execution
   - NO → `--concurrency 1` (default) — scheduler respects dependency order

3. **Do tickets exist yet?**
   - NO → Use **spec-writer** to create them, or **write-prd** for complex features
   - YES → Run **ticket-critic** to audit, then Orchestra to execute

## Workflow

---

## System Overview

Orchestra is a **headless, file-driven agent orchestrator** that drives CLI LLM agents through a LangGraph state machine. Two independent subsystems:

1. **Ticket Orchestrator** — executes `.tickets/*.md` through a state machine
2. **PRD Expansion Pipeline** — turns raw issues into structured PRDs and implementation tickets (`orchestra/expansion/`)

### Core Principle

Agents communicate exclusively via `Stage:` fields in ticket markdown files — **zero chat history dependency**. Each session is fully isolated:

```
agent call → writes Stage: BUILD → graph reads file → routes to build_node
```

---

## Execution Modes

### Single Mode (`--mode single`, default)

```
entry → build → complete
```

One agent does everything: planning (in scratchpad), implementation, and self-verification.

**When to use:**
- Capable models (Sonnet, Opus, etc.)
- Most tickets (research shows 80% of tasks work best single-agent)
- Faster execution (fewer LLM calls, no handoff latency)

**What happens:**
- NEW/SPEC/PLAN tickets route directly to `build` node
- Agent plans in scratchpad before coding
- Post-edit validation (syntax/lint checks + LLM verification)
- No dedicated spec or review nodes

### Sequential Mode (`--mode sequential`)

```
entry → spec → build → review → complete
```

Structured pipeline with dedicated agents for each phase.

**When to use:**
- Less capable providers that need structured decomposition
- Complex tickets requiring planning before implementation
- When you want a QA audit step

**What happens:**
- `spec` node: Planner writes handoff plan at `.handoff/<stem>.md`, updates stage to BUILD
- `build` node: Implementer reads handoff, writes code, updates to REVIEW
- `review` node: QA auditor checks code, updates to COMPLETE/BUILD/SPEC/BLOCKED
- Retry loops at every stage (max 3 attempts)

### Mode Comparison

| Aspect | Single | Sequential |
|--------|--------|------------|
| Graph | entry → build → complete | entry → spec → build → review → complete |
| Planning | Agent scratchpad | Dedicated spec node + handoff file |
| Review | Self-verification only | Dedicated review node |
| Speed | Faster | Slower (3+ LLM calls) |
| Quality gates | Post-edit validation | Spec + build + review verification |

---

## How to Feed Tickets Into Orchestra

### Path A: Direct via spec-writer (most common)

```bash
# 1. Create tickets from a feature request
/spec-writer Add retry mechanism for failed API calls

# 2. Audit tickets before running
/ticket-critic .tickets/141-retry-mechanism.md

# 3. Run Orchestra
python main.py --project ~/Projects/myapp
```

The **spec-writer** skill creates `.tickets/*.md` files with proper YAML front-matter (`Stage: BUILD`, `Depends-On:`, etc.). For parallel batches, it reads `PARALLEL_TICKETS_BATCH.md` for interface-first decomposition patterns.

### Path B: PRD Pipeline for Complex Features

```bash
# 1. Generate PRD from raw intent
python write_prd_langgraph.py --text "Build a notification system with email, SMS, and push"

# 2. PRD pipeline produces tickets in .tickets/
#    (intake → classification → facets → HITL → PRD → tickets)

# 3. Run Orchestra
python main.py --project ~/Projects/myapp
```

### Path C: Manual Ticket Creation

Write `.tickets/<number>-<slug>.md` files directly:

```yaml
---
Stage: BUILD
Type: feature
Depends-On: []
---

# 141 — Add retry mechanism

## Goal
...

## Acceptance criteria
Given... When... Then...
```

**Required fields:** `Stage:` (must be valid enum). See **orchestrate** skill for canonical stage definitions.

---

## Running Orchestra

### Basic Usage

```bash
# Run all pending tickets
python main.py --project ~/Projects/myapp

# Run a single ticket
python main.py --project ~/Projects/myapp --ticket ~/Projects/myapp/.tickets/42-batch.md

# Preview without executing
python main.py --project ~/Projects/myapp --dry-run
```

### Concurrency

```bash
# Run up to 4 tickets in parallel (respects Depends-On edges)
python main.py --project ~/Projects/myapp --concurrency 4
```

- Thread pool capped at **4 workers** (research shows saturation at 4 agents)
- Only tickets with **all upstream dependencies COMPLETE** run in parallel
- Each thread builds its own graph instance (fully isolated)

### Runtime Configuration

### Profiles

Three built-in profiles for different environments. Select with `--profile <name>` or `ORCHESTRA_PROFILE` env var (default: `private`).

| Profile | Where | Runtimes | Models |
|---------|-------|----------|--------|
| **work** | Work laptop, proprietary code | Cursor only | Bedrock: Opus 4.6, Sonnet 4.6, Composer 2 Fast |
| **mixed** | Work laptop, side projects | Cursor + opencode | Cursor models + opencode default |
| **private** | Home computer | opencode + qwen | opencode/big-pickle, qwen3.5-plus |

### Common Execution Patterns

**Pattern A: Narrow Tasks → Standard Model (Most Common)**

Opus/Sonnet creates narrowly-scoped tickets → delegate to cheaper model:

```bash
# Opus created 10 tickets, run them with Composer 2 (overkill to use Opus)
python main.py --project ~/Projects/myapp --profile work --model claude-composer-2-fast --concurrency 2
```

**Pattern B: Sequential Mode → Cost-Saving Model**

Qwen creates tasks → run sequentially with cheaper model:

```bash
# Qwen created tasks, run sequentially
python main.py --project ~/Projects/myapp --profile private --mode sequential --model qwen3.5-plus
```

### Model Tiers

| Tier | Models | When to Use |
|------|--------|-------------|
| **Frontier** | Opus 4.6, Sonnet 4.6, opencode/big-pickle | Complex tickets, architecture, unclear scope |
| **Standard** | Composer 2 Fast, qwen3.5-plus | Narrow tickets, well-defined scope, cost-sensitive |

**Rule of thumb:** If the ticket is <50 lines and has clear acceptance criteria → Standard. If it's architectural or ambiguous → Frontier.

### CLI Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `--profile` | Select runtime profile | `private` (or `ORCHESTRA_PROFILE` env var) |
| `--mode` | `single` or `sequential` | `single` |
| `--model` | Override model for this run | Profile default |
| `--concurrency` | Parallel workers (1-4) | `1` |
| `--runtime-config` | Path to custom config file | None |

### Custom Config

For custom profiles, create a YAML/JSON config:

```yaml
profiles:
  myprofile:
    primary_runtime: cursor
    runtime_chain: [cursor, opencode]
    providers:
      cursor: {model: "claude-composer-2-fast"}
      opencode: {model: "opencode/big-pickle"}
    max_runtime_switches: 1
```

```bash
python main.py --project ~/Projects/myapp --runtime-config runtime-policy.yaml --profile myprofile
```

---

## State Machine

Stages and transitions are defined in the **orchestrate** skill. Key points:

- **Canonical stages:** `NEW` → `SPEC` → `SPEC_SPLIT` → `BUILD` → `REVIEW` → `REVISION_ROUTER` → `COMPLETE`
- **Exception states:** `BLOCKED`, `FAILED`
- **Legacy:** `PLAN` is normalized to `SPEC`
- **Oversize routing:** Tickets with body >250 lines auto-route to `SPEC_SPLIT`

See **orchestrate** skill for the full state machine diagram and transition rules.

---

## Directory Convention

```
~/Projects/
├── orchestra/          ← this repo (the orchestrator)
└── <projname>/
    ├── .tickets/       ← ticket .md files (Stage: header required)
    │   └── archive/    ← completed tickets
    ├── .handoff/       ← handoff context files between stages
    ├── .orchestra.db   ← SQLite task/edge/run tracking
    ├── .orchestra/     ← runtime artifacts (PID, logs)
    ├── AGENTS.md       ← agent behavior rules
    ├── STANDARDS.md    ← code style / quality standards
    └── PROGRESS.md     ← append-only log of completed tickets
```

---

## Ticket Format

Every ticket must have a `Stage:` field in its YAML header:

```yaml
---
Stage: BUILD
Type: feature
Depends-On: [ticket-001]
Parent: epic-001
---

# 42 — Add batch counter

## Goal
...
```

**Required:** `Stage:` (valid enum). See **orchestrate** skill.
**For parallel execution:** `Depends-On:` must be accurate — scheduler uses this for DAG ordering.
**For blast radius control:** If implementation touches >5 files, split into child tickets (`01a-`, `01b-` pattern). See **orchestrate** skill.

---

## Skill Integration

Skills are referenced in prompts and live in the **target project's** `.skills/` directory:

| Skill | Used In | Purpose |
|-------|---------|---------|
| **ticket-critic** | Before running tickets | Pre-flight audit: 10 blocking patterns |
| **spec-writer** | Creating tickets | Turns feature requests into `.tickets/*.md` |
| **orchestrate** | All stage prompts | State transition rules |
| **handoff** | spec/retry/unblock prompts | Formatting handoff files |
| **tdd** | build prompts | Red-green-refactor discipline |
| **cleanup** | review prompts | Quality rubric, code audits |
| **write-prd** | PRD pipeline | Multi-round PRD generation |

---

## Testing

```bash
python -m pytest tests/ -q
```

---

## Adding a New Project

1. Create `~/Projects/<projname>/.tickets/` and `~/Projects/<projname>/.handoff/`
2. Add `AGENTS.md` and `STANDARDS.md` to `~/Projects/<projname>/`
3. Write ticket files with `Stage: NEW` headers (or use **spec-writer**)
4. Run: `python main.py --project ~/Projects/<projname>`

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ticket skipped | Upstream dependency not COMPLETE | Check `Depends-On:` edges, run upstream tickets first |
| Agent exits without updating stage | Prompt too vague, model confused | Add clearer acceptance criteria, run **ticket-critic** |
| All tickets route to build | Running in single mode (default) | Use `--mode sequential` if you want spec → build → review |
| Concurrency not helping | Tickets have Depends-On edges | Only independent tickets run in parallel; check DAG |
| Runtime failover not working | Chain misconfigured | Check `--runtime-config` or env `ORCHESTRA_RUNTIME_CHAIN` |
