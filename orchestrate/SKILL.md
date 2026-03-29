---
name: orchestrate
description: >-
  Defines the state machine, stage transitions, and routing rules for the headless 
  agent orchestration framework. Use this skill to understand how to read, update, 
  and transition ticket files through the pipeline.
---

# Agent Orchestration Protocol

This project uses a headless, file-driven agent orchestration framework. Agents do not pass context through chat history; they communicate entirely through file state on disk.

As an agent in this system, your primary administrative duty is to transition tickets between stages based on the outcome of your work.

## The State Machine

Every ticket markdown file must contain a header with a `Stage:` field. The allowed stages and their flow are strictly defined as:

1. **`Stage: NEW`** → Initial state. Ready for the Planner agent.
2. **`Stage: PLAN`** → The Planner is currently breaking the ticket into a handoff plan.
3. **`Stage: BUILD`** → A `.handoff/plan-<slug>.md` exists. Ready for the Execution/Builder agent.
4. **`Stage: REVIEW`** → Implementation is complete. Ready for the QA/Reviewer agent to audit.
5. **`Stage: COMPLETE`** → Fully implemented, tested, and audited. Terminal state.

**Exception States:**

- **`Stage: BLOCKED`** → Work cannot proceed (missing dependencies, failing tests, ambiguous specs). Requires the Architect agent to unblock.
- **`Stage: FAILED`** → The Architect cannot unblock the ticket. Requires human intervention. Terminal state.

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

If a ticket requires modifying more than 5 files or contains 2+ distinct architectural concerns, it is too large for a single isolated context window.

**If you are the Planner Agent, you must split it:**

1. Create new sub-tickets in the same directory (e.g., `01a-ticket-name.md`, `01b-ticket-name.md`).
2. Give each sub-ticket the header `Stage: NEW`.
3. Update the original parent ticket to `Stage: COMPLETE` (it now acts as an epic/tracker).
4. Do not write a handoff plan for the parent ticket.

## Inter-Agent Communication

- **Do NOT** leave messages for other agents in the ticket body unless documenting a bug/blocker.
- **Do NOT** wrap your file outputs in triple backticks (```). You are writing raw files to disk, not printing code blocks to a UI.
- All technical context, ordered steps, and absolute file paths must be written to `.handoff/plan-<slug>.md` using the `handoff` skill.
