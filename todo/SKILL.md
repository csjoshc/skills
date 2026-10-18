---
name: todo
description: "Route the planning-to-build pipeline in manual or auto mode."
disable-model-invocation: true
---

# /todo

`/todo` is the single entry point for work that needs planning, tickets, and
implementation. It detects the current pipeline state, then offers two modes:

- **Manual:** report the next skill and emit its copy-pasteable prompt. The user
  runs that stage, then invokes `/todo manual` again.
- **Auto:** run each required stage in order. Pause for human input only at the
  escalation points in [references/auto-driver.md](references/auto-driver.md).

Use `/todo auto` or `/todo manual` to choose directly. Bare `/todo` detects the
state, shows the next stage, and asks: **Auto** to drive through stages and pause
for critical decisions, or **Manual** to receive the next skill prompt. If the
pipeline is fresh and no feature was described, ask for its description with
the mode choice. If the pipeline is complete, report completion without asking.
`/todo status` prints state without choosing a mode. `/todo handoff` emits a
cold-start resume prompt.

For a small, already-scoped change that fits one session, skip `/todo` and use
the relevant skill directly.

## Pipeline

```text
Full: antiplan → validate → spec-writer → ticket-critic → build
Lite: spec-writer → optional ticket-critic → build
Build: /tdd + /verify-claim, then Stage NEW → BUILD → COMPLETE
```

Artifacts on disk carry state between stages: planning artifacts go in
`.plan/`, and fleshed tickets go in `.tickets/`. See
[references/state-detection.md](references/state-detection.md) for the artifact
map, state inference, dependencies, and staleness rules.

## Mode behavior

### Manual

Read paths, ticket frontmatter, and artifact mtimes to detect the current state.
Read only what the next stage needs. Do not inline full PRDs, task sequences, or
tickets into the prompt. Emit the matching template from
[references/prompt-templates.md](references/prompt-templates.md) or
[references/execution-templates.md](references/execution-templates.md). Preserve
any approval or escalation needed by that specialist stage.

### Auto

Follow the state machine in [references/auto-driver.md](references/auto-driver.md).
Invoke the specialist skill for each stage, re-detect state after it returns,
and continue without asking the user to copy prompts between stages. Preserve
the specialist skill's own instructions and approval gates.

## Escalation

Pause and ask the user when a required decision cannot be inferred safely, a
specialist skill requests approval, a Tier 2 or Tier 3 assumption is unresolved,
validation or review still fails after one repair, a slice gate fails, or a
commit cannot be completed safely. State the blocker, evidence, and one clear
question or next action. After the user responds, continue the same mode from
the current artifacts.

Auto mode may create ticket-scoped source checkpoints after evidence review.
Never commit `.plan/` or `.tickets/` artifacts and never push. Require a clean
working tree before the first source change; if it is dirty, ask the user to
commit, stash, or choose a separate worktree.

## Status output

For `/todo status`, list the detected state, present artifacts, ticket stages,
staleness warnings, and the recommended next skill. Do not execute that skill.

For Manual mode, emit only a short state summary and the next-stage prompt. For
Auto mode, report progress at stage boundaries and finish with either pipeline
completion or the escalation details.

## Companion files

- [references/state-detection.md](references/state-detection.md): state map and
  routing facts
- [references/prompt-templates.md](references/prompt-templates.md): manual
  planning and review prompts
- [references/execution-templates.md](references/execution-templates.md):
  manual build, resume, and slice-gate prompts
- [references/auto-driver.md](references/auto-driver.md): end-to-end Auto mode
- [../shared/EVIDENCE_REVIEWER.md](../shared/EVIDENCE_REVIEWER.md): evidence
  review checklist for Auto mode
