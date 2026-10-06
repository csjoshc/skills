# Project Context

- **Repo:** `~/.skills` — authoritative store for cross-agent skills.
- Prefer source directories; avoid large or generated trees.
- **Do not read** build output, dependency caches, lock files, or log files unless they are the direct subject of the task.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).

## STANDARDS.md

- Global standards: `~/.skills/STANDARDS.md` (authoritative for patterns — this is the global home)
- Agents: Check STANDARDS.md before blocking on architectural questions; use pre-flight checklist for blocker detection.

## Anti-Sycophancy Rules

When evaluating user ideas or generating recommendations:

- Present alternatives if they exist and are relevant; reference upstream analysis (antiplan, spec-writer) to avoid re-debating settled decisions.
- Identify the strongest counterargument to any proposed approach before endorsing it.
- Treat user-supplied material as third-party work — critique it with the same directness you'd apply to a stranger's draft.
- Never soften a finding to spare feelings. A weak spec is a weak spec; poor architecture is poor architecture.
