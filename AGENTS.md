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

## Notes
<!-- memory:start -->
- `tdd/scripts/red_first.py` is the local test-quality gate; extend it or the skill text only when
  real use shows a need, and leave the archived 16-ticket gate plan (`.trash/gate-plan-2026-10-15/`)
  archived - it shipped nothing in a day (2026-10-15).
- Skill scripts never import anthropic; the invoking agent does the LLM step and Python only gates
  or verifies - a second model call adds latency, needs an API key and breaks offline (2026-04-27).
- Plans for this repo state the net skill count and what gets deprecated, show the workflow change
  on a real past project, and prefer editing existing files or `shared/` over new skills - a
  four-new-skill plan was rejected because it didn't map to real use (2026-10-14).
<!-- memory:end -->
