---
name: orchestra
description: >-
  CLI ticket runner that executes .tickets/*.md through a LangGraph state machine.
  Covers execution modes (single vs sequential), concurrent batching, runtime failover,
  and how to feed tickets from spec-writer/write-prd into the runner.
  Use when running tickets, configuring modes, or debugging execution.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for orchestra:**
- **Tier 1 (reversible):** Wrong mode choice — re-run with different `--mode`.
- **Tier 2 (conflict):** Ticket dependencies form a cycle — **STOP**, fix `Depends-On:` edges.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert.

## TL;DR (Quick Start)

Headless, file-driven agent orchestration. Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

**When to use:** Running tickets, choosing execution mode, configuring concurrency, debugging failures.

**Invocation:**
```bash
orch run                            # interactive, prompts for config
orch run --profile private          # non-interactive
orch run --mode sequential          # sequential pipeline
```

## Decision Tree

1. **What model/provider are you using?**
   - Capable (Sonnet, Opus, etc.) → `--mode single` (default)
   - Less capable (smaller providers) → `--mode sequential`

2. **Are tickets independent (no Depends-On edges between them)?**
   - YES → `--concurrency N` (up to 4) for parallel execution
   - NO → `--concurrency 1` (default) — scheduler respects dependency ordering.

3. **Do tickets exist yet?**
   - NO → Use **spec-writer** to create them, or **write-prd** for complex features
   - YES → Run **ticket-critic** to audit, then Orchestra to execute

## Workflow

---

## System Overview

Orchestra is a **headless, file-driven agent orchestrator** that drives CLI LLM agents through a LangGraph state machine.

### Core Principle

Agents communicate exclusively via `Stage:` fields in ticket markdown files — **zero chat history dependency**. See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for stage definitions.

```
agent call → writes Stage: BUILD → graph reads file → routes to build_node
```

---

## Execution Modes

### Single Mode (`--mode single`, default)
One agent does planning, implementation, and self-verification.
- **Node chain:** `entry → build → complete`

### Sequential Mode (`--mode sequential`)
Structured pipeline with dedicated agents for each phase.
- **Node chain:** `entry → spec → build → review → complete`

---

## Canonical Defaults (Profiles, Tiers, Stages)

See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for:
- [ ] **Execution Profiles** (`work`, `mixed`, `private`)
- [ ] **Model Tiers** (Frontier vs Standard)
- [ ] **State Machine stages** (`NEW`, `SPEC`, `BUILD`, `REVIEW`, `COMPLETE`)

---

## How to Feed Tickets Into Orchestra

### Path A: Direct via spec-writer (most common)
The **spec-writer** skill creates `.tickets/*.md` files with proper YAML front-matter.

### Path B: PRD Pipeline for Complex Features
The **write-prd** skill produces tickets through the PRD expansion pipeline.

### Path C: Manual Ticket Creation
Write `.tickets/<number>-<slug>.md` files directly. Required field: `Stage:` (must be valid enum).

---

## Running Orchestra

Run `orch run --help` for the full flag reference, or `orch config list` for available profiles.

---

## Directory Convention

See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for the standard directory structure (`.tickets/`, `.handoff/`, etc.).

---

## Skill Integration

| Skill | Purpose |
|-------|---------|
| **ticket-critic** | Pre-flight audit: 10 blocking patterns |
| **spec-writer** | Turns feature requests into `.tickets/*.md` |
| **orchestrate** | State transition rules |
| **handoff** | Formatting handoff files |
| **tdd** | Red-green-refactor discipline |
| **cleanup** | Quality rubric, code audits |

---

## Advanced Usage & Deep Dives

See [`DETAILS.md`](~/.skills/orchestra/DETAILS.md) for progressive disclosure on:
- **Mode Comparisons** (Single vs Sequential deep-dives)
- **Common Execution Patterns** (Standard delegate, Sequential fallback)
- **Detailed Troubleshooting** (Symptoms and fixes)
- **Inter-Agent Communication Rules**

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ticket skipped | Upstream dependency not COMPLETE | Check `Depends-On:` edges |
| Agent exits without updating stage | Prompt too vague, model confused | Run **ticket-critic** |
| All tickets route to build | Running in single mode (default) | Use `--mode sequential` |

For more symptoms and fixes, see **[`DETAILS.md`](~/.skills/orchestra/DETAILS.md)**.
