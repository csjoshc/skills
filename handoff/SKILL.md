---
name: handoff
description: "Creates one concise `.agent-local/handoff/<slug>.md` for a follow-up session, then returns its absolute path and a brief next-action summary. Use when asked for a handoff or to continue in a new chat, harness, directory or teammate."
---

# Session handoff

Write one handoff file so the next session can continue without this conversation.

## Workflow

1. Take the workspace root from the user's requested location, or from the current working directory. Read the files and artifacts the next session will need. Record unknowns as unknown. Treat work as done only when a file or command shows it.
   Done when you can state the follow-up task and point to the sources it needs.
2. Fill in [TEMPLATE.md](TEMPLATE.md). Keep goal, current state, next action, constraints and authoritative pointers. Add verification only when a named check is needed. Use absolute paths for local files.
   Done when the draft has those sections, no copied spec bodies, and no empty headings.
3. Write exactly one file at `<workspace>/.agent-local/handoff/<slug>.md`, creating `.agent-local/handoff/` if needed. Use a short kebab-case slug. Leave other files in `.agent-local/handoff/` as they are. The chat reply is that path plus a short next-action summary.
   Done when the single file exists at its absolute path.
4. Call the Skill tool with `stop-slop` on the handoff file and the chat reply. Return the file's absolute path and a few sentences on what the next session should do.
   Done when the chat reply has the path, a short next-action summary, and no copy of the file.

## Content rules

- Point at specs, tickets, ADRs, diffs or URLs by absolute path, with one line on why each matters.
- State the next action as numbered imperative steps. Keep only constraints that change that work.
- Add verification only when a specific test, command or acceptance check will keep the next session honest.
- Name a secret by its environment variable or file path. Omit the value and any personal data.
- Skip skill lists, empty sections and extra plan files.
