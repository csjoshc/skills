---
name: handoff
description: "Writes a copy-pasteable cold-start prompt for a new session, linking artifacts by path, with optional plan files under .handoff/. Use when asked for a handoff or to continue in a new chat."
---

# Session handoff

When the user wants to **hand off** work (new chat, new harness, new directory, a teammate, or async continuation), produce **one block of text they can paste as the sole first message** to the next agent.
Assume the recipient has **zero** conversation history and knows only what the prompt tells it.
If the user said what the next session is for, tailor the prompt to that focus.

Artifact and redaction rules adapted from Matt Pocock's `handoff` skill (MIT).

## Output contract

1. **Handoff prompt** (always): one markdown section holding the full paste-ready text, wrapped in a `markdown` code block so it copies in one click.
   It is **sufficient and necessary**: everything a competent agent needs to continue without guessing, and nothing it can read for itself.
2. **Plan file** (conditional): when the remaining work is non-trivial (see below), also write `.handoff/plan-<slug>.md` and reference it by absolute path in the prompt.

Build the prompt from [TEMPLATE.md](TEMPLATE.md).

## What to summarize

From the conversation and any open or referenced files, state clearly:

| Area | Include |
|------|---------|
| **Goal** | What "done" looks like; user constraints (stack, style, deadlines). |
| **Current state** | What exists now (branches, key files, deployed vs local). |
| **Task for the next agent** | Imperative, ordered list of what to do next, not a recap of the past. |
| **Repo / workspace** | Root path if known (e.g. `/Users/.../project`). |
| **Relevant paths** | Every file or directory the next agent must read or edit, as **full absolute paths**. |
| **Suggested skills** | Which skills the next agent should invoke, and for which step. |

### Point at artifacts instead of copying them

Specs, plans, ADRs, tickets, issues, commits and diffs already hold their content.
Reference each by absolute path, URL or commit sha with one line on why it matters, and let the next agent read it.
Treat standards, trackers and config the next agent must respect the same way (testing standards, `.plan/`, `.tickets/`, `.env.example`, `docker-compose.yml`).
If nothing beyond normal source files applies, say so in one line and name the README or AGENTS.md to follow.

### Redact

Leave out API keys, tokens, passwords and personal data.
Name where a secret lives (env var, secrets file path) instead of its value.

## Plan file (conditional)

### When to write `.handoff/plan-<slug>.md`

Write a plan file when **any** of these hold:

- The change is more than a quick local edit: roughly **more than ~10 lines of substantive code in one file**, or it touches **multiple** files or modules.
- There are **non-obvious ordering constraints** (migrations before code, API before UI).
- Steps should be **incrementally verifiable** (tests, manual checks, build targets).

For a trivial one-off edit with obvious verification, the prompt alone is enough.

### Where to put it

- Path: **`<workspace-root>/.handoff/plan-<slug>.md`**, creating `.handoff/` in the workspace root if missing.
- `<slug>`: short kebab-case topic, e.g. `plan-auth-refactor.md`. Parallel tracks get distinct slugs or a numeric suffix (`plan-02.md`).

### Plan file content

- **Narrowly scoped**: one coherent deliverable or milestone per file; split if huge.
- **Stepwise**: ordered steps, each with **how to verify** it (test command, expected outcome, or manual check).
- **Stable**: file paths, API names and decisions stated explicitly, so a cold agent never depends on chat tone.

In the prompt, add a line such as `Follow the incremental plan at: /absolute/path/.handoff/plan-<slug>.md` and tell the next agent to read it first.
Keep the step list in the plan file and only summarize it in the prompt.

## Companion files

Read only when the situation matches:

- [TEMPLATE.md](TEMPLATE.md): writing the handoff prompt block, suggested skills, and the pre-send checklist
