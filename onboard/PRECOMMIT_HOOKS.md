# Static Analysis via Pre-Commit Hooks

The repo should have **static analysis / linting checks** that run as a **git commit hook** and **block commits** when they fail (type errors, invalid returns/inputs, unreachable code, obvious null/None hazards, etc.).

## Contents

- Where to encode the policy
- Mechanical check or standards rule
- Hook mechanism defaults
- Smoke test
- Run-everything documentation

### Where to encode the policy

1. **`./STANDARDS.md` (authoritative)**: Add a short section like:
   - Commits must be blocked by pre-commit hooks that run static analysis appropriate to the stack.
   - The “run everything” command(s) must be documented (see below).

2. **`AGENTS.md` (operational)**: Add a brief bullet reminding agents to ensure hooks exist and are kept passing.

### Mechanical check or standards rule

Sort each rule before encoding it.
A **mechanical** rule (a banned API, an import shape, a file-location rule, any fixed pattern) gets a deterministic check: a lint rule, a hook or a CI job, whichever the stack makes cheapest.
A **judgement call** (cross-file consistency, matching surrounding style) goes in `./STANDARDS.md`, where review reads it.
Prefer building the check over writing the rule.

### Hook mechanism defaults (use these unless the repo already has something else)

If the repo already uses a hook framework (e.g. `pre-commit`, `husky`, `lefthook`, `lint-staged`, `simple-git-hooks`), **extend the existing one**; do not introduce a second framework without a strong reason.

If the repo does not have hooks yet:

- **Python present** → use **`pre-commit`** with (at minimum):
  - `ruff` (format + lint) and
  - `mypy` (type checking).

- **npm/Node present** → use **`husky`** with (at minimum):
  - `eslint` (lint) and
  - `tsc -p <tsconfig>` (type checking) when TypeScript is present.
  - If no TypeScript config exists, run `eslint` only (do not invent `tsconfig.json`).

- **npm + Python present**:
  - Enforce both. Prefer one runner that calls both toolchains (commonly `lefthook`) if low-risk; otherwise extend the existing mechanism.

### Smoke test

After adding or changing hooks, commit the hook setup itself so the commit runs through the new hook.
A commit that passes the hook, or fails it for a real reason, proves the hook is wired.
If the commit goes through without the checks running, the hook is not installed (check the framework's install step, such as `pre-commit install` or the `prepare` script).

### “Run everything” documentation (required)

Ensure the repo has a documented way to run the same checks outside git hooks, ideally in one place (choose the natural home for the stack):

- **Python**: `make check`, `uv run pre-commit run -a`, `python -m ruff check . && python -m mypy ...`, etc.
- **Node**: `npm run lint`, `npm run typecheck`, or a combined `npm run check`.

Use what the repo already has; do not guess tooling beyond npm/Python detection. **Hooks enforce**; developers can run the same checks directly.
