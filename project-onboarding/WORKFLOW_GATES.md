---
name: workflow-guard
description: >-
  Session-level orchestrator that routes tasks through the correct skill
  pipeline at each phase. Ensures spec-writer runs before implementation,
  tdd runs before tests, verify-claim runs before "done", pr-review runs
  before PR. Prevents enforcement from being purely opt-in. Use at session
  start and at every phase transition.
---

# workflow-guard

Enforcement only works if it fires at the right moment. This skill is the
conductor — it watches phase transitions in a session and invokes the
correct downstream skill so the user doesn't have to remember to do so.

## When to invoke

- Automatically on `SessionStart` (via hook if hook-sync is installed)
- At the start of any new task, before any tool use
- At every detected phase transition (see Phase map below)

## Phase map

| Phase trigger (user or agent intent) | Required skill(s) | Gate |
|---|---|---|
| "Create ticket / spec / plan for X" | `spec-writer`, `ticket-critic` | AC→test table present |
| "Implement / write / add X" | `redundancy-watcher` (pre-write), `layer-boundary-critic` (on import add) | No BLOCK unresolved |
| "Write tests for X" | `tdd`, `mock-contract` (if boundary mock) | Tests fail red then green |
| "I'm done / complete / fixed X" | `verify-claim` | `CLAIM_UNVERIFIED.md` absent |
| "Open / create PR" | `pr-review` self-pass, `create-pr` | No BLOCK from 5 agents |
| "Fix review comments" | `pr-fix` | Staleness check green |
| "Clean up / refactor X" | `cleanup` Phase 0 first | Mechanical findings addressed |

## Workflow

### SessionStart digest

```bash
# Read project context
test -f AGENTS.md && head -100 AGENTS.md
test -f STANDARDS.md && head -100 STANDARDS.md
test -f CLAUDE.md && head -60 CLAUDE.md

# Summarize in one paragraph at session start
echo "Project: <name>. Layer cake: <list>. Standards source: STANDARDS.md. Key rules: <top 3>."
```

Persist to `.claude/cache/session-context.md` for later phases.

### Intent classification

Parse the user's message for phase triggers. Classify via keyword match
plus LLM short-prompt on ambiguous cases. When multiple phases apply,
route through each sequentially.

### Gate enforcement

For each phase, invoke the listed skills in order. If any skill emits a
BLOCK or writes `CLAIM_UNVERIFIED.md`, halt and relay the block to the
user before proceeding.

### Loop

After each phase completes, re-classify the next user message. Never
assume the user is in the same phase across turns.

## Interaction with hooks

When `hook-sync` is present, workflow-guard registers itself as a
`SessionStart` hook and a `PreToolUse` hook on `Write`/`Edit` so phase
transitions fire deterministically rather than relying on the agent to
remember.

## Hard rules

- Never skip a gate. "The user is in a hurry" is not a reason.
- Never substitute a different skill for the one the phase map names.
- Never claim a phase complete without the gate's green signal.
- If a skill is missing from the library, report it and stop — do not
  improvise an equivalent.

## Output contract

One line per phase transition:

```
[phase] → invoked <skill>,<skill>,<skill> → <GREEN|BLOCK>
```
