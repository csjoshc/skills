---
name: orchestrate
description: >-
  State machine rules for Orchestra ticket stage transitions, ticket splitting, and inter-agent communication.
  Used by prompts.py to guide downstream LLM agents through the orchestration pipeline.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for orchestrate:**
- **Tier 1 (reversible):** Missing status update — proceed, but add Task N to update the ticket before finishing.
- **Tier 2 (conflict):** Ticket stage transition is illegal (e.g., NEW -> COMPLETE) — **STOP**, clarify via spec-writer.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert.

## TL;DR

This skill defines **state machine rules** for agents executing Orchestra tickets — stage transitions, ticket splitting, and inter-agent communication. It does NOT wrap or invoke any CLI. For running tickets, see **`run-ticket`**.

Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

## Decision Tree

1. **Is the stage transition legal?**
   - Check the State Machine table below. Illegal transitions (e.g., `NEW → COMPLETE`) must be blocked.
   - When in doubt → **STOP**, escalate via spec-writer.

2. **Should this ticket be split?**
   - Modifies >5 production files OR has 2+ distinct concerns → YES, split.
   - >250 lines → auto-route to `SPEC_SPLIT`.

3. **Should this ticket be blocked?**
   - Upstream `Depends-On:` not `COMPLETE` → mark `BLOCKED`.
   - Ambiguous scope or missing acceptance criteria → mark `BLOCKED`, escalate.

## The State Machine (Stages)

Every ticket markdown file must contain a `Stage:` field.

See [`~/.skills/shared/ORCHESTRA_DEFAULTS.md`](~/.skills/shared/ORCHESTRA_DEFAULTS.md) for the canonical stage list:

| Stage | Meaning | Transition From |
|-------|---------|-----------------|
| **`NEW`** | Initial state, ready for execution | N/A |
| **`SPEC`** | Planning/Decomposition phase | `NEW` / `REVISION_ROUTER` |
| **`BUILD`** | Implementation phase (Coding) | `SPEC` / `NEW` (Single Mode) |
| **`REVIEW`** | Audit/QA phase | `BUILD` |
| **`COMPLETE`** | Terminal state (Merged) | `REVIEW` / `BUILD` (Single Mode) |
| **`BLOCKED`** | Halted due to dependency/logic | Any non-terminal stage |
| **`FAILED`** | Technical execution failure | Any non-terminal stage |

**Routing Patterns:**
- **Single Mode:** `entry → build → complete`
- **Sequential Mode:** `entry → spec → build → review → complete`

## How to Transition State

When you finish your assigned task, you **MUST** update the stage. Edit the YAML header:
```yaml
Stage: REVIEW
```
**Rule:** Never leave a ticket in the stage you found it in unless interrupted.

## Ticket Splitting (Blast Radius Control)

If a ticket requires modifying **>5 production files** or has 2+ distinct concerns, split it:
1. Create sub-tickets: `01a-slug.md`, `01b-slug.md` (`Stage: NEW`).
2. Update parent to `Stage: COMPLETE` or `BLOCKED`.
3. Tickets >250 lines auto-route to `SPEC_SPLIT`.

## Inter-Agent Communication Rules

- **Strict Isolation:** Each agent session is fresh. Communication is only via `Stage:` and `.handoff/` files.
- **No Messages in Body:** Do NOT leave notes/questions for other agents in the ticket body. Use the `handoff` skill or mark the ticket `BLOCKED`.
- **Raw File Output:** Do NOT wrap file outputs in triple backticks in implementation steps — write directly to the filesystem.

## Project Setup

Ensure these are in `.gitignore`:
```
.orchestra.db
.orchestra/
```

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.
