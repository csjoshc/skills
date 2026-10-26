---
name: retro
description: Retrospective on a coding session that proposes fixes to the agent's environment.
disable-model-invocation: true
---

# Retro

Find what in the environment (files, checks, steering, tools) made the session slower or wrong, and propose where each fix lives.
Adapted from Matt Pocock's `retro` skill (MIT).

## Source

Use the session the user names: the current session by default, or a log path they give.
Assume no log location for any harness; if the named log can't be read, ask for the path.
Before proposing a check, read the repo's own check command (lint, typecheck, test scripts, CI workflow, hook config).

## Categories

- **Navigation:** the agent took long to find a file or fact, or tripped on a hidden dependency. Fix: a pointer in AGENTS.md or a doc.
- **Automated checks:** a mistake a lint rule, type check, test or hook could have caught. An existing check that is unwired or broken is the finding. A repo with no hook and no CI running its checks is a finding too.
- **Coding standards:** review missed a mistake, or a rule is unclear or stale.
- **AGENTS.md bloat:** steering in the repo or global AGENTS.md that belongs in a standards file or a check.
- **Tool economy:** expensive or repeated tool calls, or a CLI or MCP tool that wastes tokens.
- **No-ops:** steering lines that change no behaviour. Cut them.
- **Information access:** a fact the agent needed but could not reach, such as dev server logs or read-only access to a service.

## Where each fix goes

Classify every finding first:
- **Mechanical** (a fixed pattern, banned API, import shape, file location): a deterministic check. In a project, a lint rule, a commit hook or a CI job, whichever its stack makes cheapest. In `~/.skills`, `hooks/` or `skillsmith/scripts/skill_audit.py`. Prefer building the check over writing a rule.
- **Judgement call** (consistency, fit with surrounding code): the project's standards file (`./STANDARDS.md`), or `~/.skills/standards/` for global ones.

Keep AGENTS.md to navigation pointers and rules every session needs.
Standards are read at review time, so they carry the rules review enforces.
Before adding a hook, apply `~/.skills/shared/HOOK_PRINCIPLES.md`.

## Mechanical gate

Never write the same comment twice. A mechanical finding is not resolved by
fixing the one instance — it is resolved only when a deterministic check will
catch the next instance. For each mechanical finding, the outcome must be one
of, in order of preference:

1. **Checked** — a lint rule, commit hook, CI job, or audit-script assertion
   now fails on the pattern. Prove it: run the check and show it flag a seeded
   instance (red), then pass once fixed (green).
2. **Deferred** — the user explicitly accepts no check, with a one-line reason
   recorded in the finding (e.g. "too rare to be worth a rule").

"Noted" and "fixed by hand" are not valid outcomes for a mechanical finding.
Judgement-call findings are exempt: they go to a standards file and are
enforced at review time, not by a check.

## Output

List findings by severity, highest first.
For each: what happened (with a session quote or step), the category, the fix, and its destination file or check.
Apply only the fixes the user approves.
