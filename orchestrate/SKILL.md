---
name: orchestrate
description: >-
  Defines the state machine, stage transitions, and routing rules for the headless 
  agent orchestration framework. Use this skill to understand how to read, update, 
  and transition ticket files through the pipeline.
---

## TL;DR (Quick Start)

Headless, file-driven agent orchestration. Agents communicate via `Stage:` fields in ticket markdown files. **Zero chat history dependency.**

**When to use:** Transitioning statuses, understanding the state machine, explaining how agents cooperate.

**Invocation:**
- **Status Change:** Edit the `Stage:` field in the ticket YAML header.
- **Rules:** Never leave a ticket in the same stage unless interrupted.

## Decision Tree

1. **What is the current state?**
   - No `.handoff/plan-*.md`? → Move to `Stage: SPEC`.
   - Implementation done? → Move to `Stage: REVIEW`.
   - Implementation + Audit done? → Move to `Stage: COMPLETE`.

2. **Is the ticket too large (>250 lines or >5 files)?**
   - YES → **MANDATORY** Move to `Stage: SPEC_SPLIT` and create child tickets using `01a-` pattern.
   - NO → Proceed with standard transition.

3. **Is work blocked?**
   - YES → Move to `Stage: BLOCKED`; detail reasons in the ticket body.
   - NO → Continue.

## Workflow

## The State Machine

Every ticket markdown file must contain a header with a `Stage:` field. The allowed stages and their flow are strictly defined as:

1. **`Stage: NEW`** → Initial state. Ready for the Spec/Planner agent.
2. **`Stage: SPEC`** → The Planner is currently breaking the ticket into a handoff plan. (`Stage: PLAN` is a legacy alias, normalized to `SPEC`.)
3. **`Stage: SPEC_SPLIT`** → Ticket is oversized (>250 lines body). The Planner is splitting it into sub-tickets.
4. **`Stage: BUILD`** → A `.handoff/plan-<slug>.md` exists. Ready for the Execution/Builder agent.
5. **`Stage: REVIEW`** → Implementation is complete. Ready for the QA/Reviewer agent to audit.
6. **`Stage: REVISION_ROUTER`** → Routes to affected facets for PRD-style revision when stage demands it.
7. **`Stage: COMPLETE`** → Fully implemented, tested, and audited. Terminal state.

**Exception States:**

- **`Stage: BLOCKED`** → Work cannot proceed (missing dependencies, failing tests, ambiguous specs). Requires the Architect agent to unblock.
- **`Stage: FAILED`** → The Architect cannot unblock the ticket. Requires human intervention. Terminal state.

> **Note:** The PRD expansion subsystem (`orchestra/expansion/`) is a separate pipeline. Use the **`write-prd`** skill to generate PRDs from raw intent. The ticket graph may hand off to `REVISION_ROUTER` for expansion-style revision flows.

## How to Transition State

When you finish your assigned task, you **MUST** update the state.
Use your file editing tools to modify the top of the ticket file.

**Correct:**

```yaml
Title: Implement user login
Stage: REVIEW
```

**Rule:** Never leave a ticket in the stage you found it in unless your execution timed out or was interrupted.

## Ticket Splitting (Blast Radius Control)

Every ticket created must represent a distinct 1:1 mapping of implementable work. **Do not create tickets that merely act as wrappers or epics for other tickets.**

If an existing ticket requires modifying more than 5 files or contains 2+ distinct architectural concerns, it is too large for a single isolated context window.

**If you are the Planner Agent, you must split it:**

1. Create new, strictly bounded sub-tickets in the same directory (e.g., `01a-ticket-name.md`, `01b-ticket-name.md`).
2. Give each sub-ticket the header `Stage: NEW`.
3. Ensure each new ticket defines actionable work, not just a container for others.
4. Update the original parent ticket to `Stage: COMPLETE` or `Stage: BLOCKED` so it no longer executes.
5. Do not write a handoff plan for the original parent ticket.
6. The graph routes oversized tickets (body >250 lines) automatically to `Stage: SPEC_SPLIT`.

## Inter-Agent Communication

- **Do NOT** leave messages for other agents in the ticket body unless documenting a bug/blocker.
- **Do NOT** wrap your file outputs in triple backticks (```). You are writing raw files to disk, not printing code blocks to a UI.
- All technical context, ordered steps, and absolute file paths must be written to `.handoff/plan-<slug>.md` using the `handoff` skill.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing status update — proceed, but add Task N to update the ticket before finishing.
- **Tier 2 (logic):** Ticket stage transition is illegal (e.g., NEW -> COMPLETE) — **STOP**, clarify via spec-writer.
- **Tier 3 (security):** Ticket implementation attempts to bypass stage-gate security — **STOP**, block and alert immediately.
