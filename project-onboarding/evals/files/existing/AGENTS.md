# Project Context

npm project (demo-widgets). Build: `npm run build`. Test: `npm test`.

## Git workflow

- Never push directly to a protected/default branch (`main`, `master`, `trunk`), even for trivial or corrective changes, even if the push would technically succeed (branch protection may not be configured to block it). Always create a branch and open a PR.
- This applies to agents and subagents equally — a "quick fix" is not an exception.

## Code comments

Plain English, no AI-slop. 1–2 lines (≤100 chars), next to the code. Say why, not what. Only real footguns earn more. History behind odd code earns a comment too, with an issue or file pointer.

# Engineering principles

Before writing code, in order:
1. Reuse: use what the repo, stdlib and platform already provide.
2. YAGNI: build only what was asked. Add an abstraction once it has a second real use.
3. DRY: dedupe repeated *knowledge* at the 2nd-3rd real use, not look-alike code.
4. SOLID: reshape only when a second real consumer or change pressure exists.
YAGNI wins over DRY/SOLID until then. Prefer the shortest solution that is still correct.

Keep validation, error handling and auth checks at trust boundaries, even when they cost lines.
Touch only what the task needs; match existing style.
If requirements are ambiguous or conflict, state your assumption and ask before choosing.
