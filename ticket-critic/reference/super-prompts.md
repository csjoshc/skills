# Super-Prompts

## Harden Tickets Under `.tickets/`

Use when the user wants markdown tickets upgraded in place:

```
Read AGENTS.md and STANDARDS.md first.

Use ticket-critic (this skill) for Stage gate and 10 patterns.
Read spec-writer and tdd skills for structure and test-first discipline.
Read ~/.cursor/rules/cleanup/QUALITY_RUBRIC.md for checkable AC tied to mechanical (M1–M12) and subjective tiers—do not run the cleanup codebase-audit workflow unless also asked to review code.

For each ticket in .tickets/ (or paths named):
1. Stage header valid; dependencies and STANDARDS alignment.
2. If BUILD implied: explicit TDD, Verification commands, Self-review checklist.
3. >5 production files → split 01a/01b…; parent epic per orchestrate.
4. No vague AC; assumptions in STANDARDS or [ASSUMPTION] + BLOCKED.
5. You MAY edit ticket markdown to satisfy the above.

Frontend: Playwright (or project E2E) if UI exists; else state N/A.
Backend: pytest (or project standard) for contracts and unhappy paths.
```

## Kickoff Prompt: Generate New Cleanup-Oriented Tickets

When the user wants **new** tickets from an audit report (adapt repo root):

```
Create actionable tasks in .tickets/ using orchestrate ticket shape, spec-writer and ticket-critic discipline.

Each ticket: explicit target file list (≤5 files), AGENTS.md/STANDARDS.md alignment, checkable AC, Verification commands, TDD where implementation is implied.

Prioritize work that maps to QUALITY_RUBRIC.md (layering, contracts, tests, mechanical M-patterns).

Mechanical improvements should be verifiable with project pytest/linters/security tools; avoid promising numeric score deltas.
```
