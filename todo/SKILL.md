---
name: todo
description: "Drive the planning-to-build pipeline. Default is to run it."
disable-model-invocation: true
---

# /todo

`/todo` is the single entry point for work that needs planning, tickets, and
implementation. Bare `/todo` drives. `/todo auto` is an alias. `/todo manual`
emits the next-stage prompt without driving.

- **Drive (default):** detect state, create missing artifacts from the request
  and the repo, then run each required stage. Pause only for load-bearing
  decisions in [references/auto-driver.md](references/auto-driver.md).
- **Manual:** report the next skill and emit its prompt. The user runs that
  stage, then invokes `/todo manual` again.

`/todo status` prints state without driving. `/todo handoff` writes
`.handoff/<slug>.md` via the handoff skill and replies with its path plus a
few sentences.

For a small, already-scoped change that fits one session, skip `/todo` and use
the relevant skill directly. For frontend UI work, that entry is `/ui`.

## Pipeline

```text
Full: challenge → spec → build
Lite: spec → build
Build: subagent per ticket; /tdd + /verify; Stage NEW → BUILD → COMPLETE
```

The DAG and tickets on disk are the guardrails against drift.
`.plan/` owns order; `.tickets/` owns scope, ACs and Stage.
ticket-review is optional and never a build gate.
See [references/state-detection.md](references/state-detection.md).

## Drive

Follow [references/auto-driver.md](references/auto-driver.md).

1. Detect state from paths and ticket frontmatter. Do not ingest every ticket body.
2. If fresh and the user named work: write a thin DAG + compact tickets, or skip
   tickets for a small change. Proceed on Tier 1 assumptions.
3. Spawn one BUILD subagent per implementation ticket. Parallel only when
   `Depends-On` is satisfied, `Files:` are disjoint, and risk is low.
   Serialize overlapping files, mutation hubs, integration gates, and
   medium-or-higher risk.
4. Check returned evidence against ACs
   (`../shared/EVIDENCE_REVIEWER.md`). Drift or missing evidence → halt.
5. Loop until complete or a load-bearing halt.

For a ticket whose scope changes frontend UI, the BUILD subagent calls the
Skill tool with `ui` while preserving ticket ACs, `/tdd`, and `/verify`.

Never commit `.plan/` or `.tickets/` and never push. Require a clean working
tree before the first source change; if it is dirty, ask the user to commit,
stash, or choose a separate worktree.

## Manual

Read paths, ticket frontmatter, and artifact mtimes. Emit the matching template
from [references/prompt-templates.md](references/prompt-templates.md) or
[references/execution-templates.md](references/execution-templates.md).

## Escalation

Halt and ask only for auth, public API, data-model, security, conflicting
tickets, undefined success, a failed evidence review, or a specialist skill's
own sign-off. Record reversible assumptions on the ticket.
See `~/.skills/shared/ASSUMPTION_TIERS.md`.

## Status output

For `/todo status`, list the detected state, present artifacts, ticket stages,
staleness warnings, and the recommended next skill. Do not execute that skill.

When tickets exist, show a Markdown table with `Stage` and `Tickets` columns,
counting implementation tickets by their current `Stage:` values.
Keep each source stage distinct, including FAILED, and flag missing or unknown stages.
Follow it with `N/M implementation tickets complete`, the in-flight ticket IDs,
blockers, and the next action.
Count only `Stage: COMPLETE` as complete.
Report integration gates separately; exclude them from the implementation total.

Derive progress from `.tickets/` and `.plan/` on each run.
No progress files, history, percentages, graphical bars, or generated diagrams.

Driving: short status, then either the next halt question or "pipeline done".
`/todo handoff` returns the file path plus 2-4 sentences; no paste block.

## Companion files

- [references/state-detection.md](references/state-detection.md): state map
- [references/prompt-templates.md](references/prompt-templates.md): challenge / spec start prompts
- [references/execution-templates.md](references/execution-templates.md): BUILD / resume / gate briefs
- [references/auto-driver.md](references/auto-driver.md): drive loop
- [../shared/EVIDENCE_REVIEWER.md](../shared/EVIDENCE_REVIEWER.md): BUILD evidence review
