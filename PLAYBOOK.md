# Skill Playbook

Quick reference for which skill to invoke at each phase. Most skills
auto-trigger from their `description:` field when you mention the right
verbs; listed below in order of the flow.

## Scenario matrix

| You're about to... | Invoke in order | Why |
|---|---|---|
| Open a new repo for the first time | `project-onboarding` | Writes AGENTS.md, installs pre-commit hooks, sets up STANDARDS.md, wires RTK/caveman. Loads `WORKFLOW_GATES.md` for session orchestration. |
| Start a session in an existing repo | (nothing explicit — `workflow-gates-session` hook dumps AGENTS.md + STANDARDS.md as the SessionStart digest) | Grounds the agent in your rules. |
| Turn a vague idea into a ticket | `spec-writer`, then `ticket-critic` | Produces Given/When/Then ACs and the mandatory AC→Test table. Blocks `Stage: BUILD` until each AC names its test. |
| Stress-test a plan before building | `antiplan` | Adversarial interrogation; 14 anti-patterns including "never reinvent" and "YAGNI is law". |
| Add a new file / module / utility | `cleanup` with its `WRITE_TIME_GUARD.md` companion | Blocks duplication and "just in case" code before the file exists. |
| Change imports in a layered codebase | `cleanup` with `LAYER_ENFORCEMENT.md` | Rejects upward imports; suggests dependency inversion. |
| Write a test | `tdd` (red → green → refactor); if mocking a boundary, also load `MOCK_CONTRACT.md` | Enforces real-contract references for boundary mocks; rejects internal-collaborator mocks. |
| Finish a TDD cycle | `tdd/MUTATION.md` (3-mutant pass on the changed function) | Catches tautological tests that pass whether the code runs or not. |
| Claim you're "done" | `verify-claim` | Requires passing test output + (screenshot for UI / curl for API / regression test for fix). Writes `CLAIM_UNVERIFIED.md` if evidence missing. |
| Open a PR | `pr-create` — Phase 0 runs `verify-claim` + `pr-review` self-check + `tdd/MUTATION.md` + `tdd/MOCK_CONTRACT.md` before any git work | Catches false completions, scope creep, tautological tests, and uncontracted mocks before anyone else sees the PR. |
| Review someone else's PR | `pr-review` | 5 parallel sub-agents (Bug Hunter, Standards, Error Handling, Test Analyzer, Spec-Traceability). Every finding binds to a binary checklist — no vibe scores. |
| Address review comments on your PR | `pr-fix` | One comment at a time, 3-attempt retry cap, staleness check via `tdd/MUTATION.md` after each fix. |
| Audit existing code (not a PR) | `cleanup` — Phase 0 mechanical pass first, then subjective rubric | Prevents the LLM from rationalizing away mechanical issues. |
| Present findings to execs / engineers | `reframe exec` or `reframe architect` or `reframe engineer` | Audience-appropriate restructuring, no fabrication. |
| Produce a deck from the reframe | pipe into `ppt-make` | Consumes the YAML frontmatter + `## Slide:` contract. |
| Sync skills across tools | `skill-sync` | Propagates `~/.skills` → Claude Code, Cursor, Codex, Gemini, etc. |
| Sync MCPs | `mcp-sync` | `~/.secrets/mcp.json` → target-specific settings files. |
| Sync hooks | `hook-sync` | `~/.hooks/*.json` → Claude Code settings.json + Cursor + Codex + Gemini. |
| Hit a long session | caveman auto-activates above 50% context (via hook) | Compresses agent prose; code/paths untouched. |
| Notice CLI noise eating budget | verify RTK is installed: `rtk status` | Compresses shell output before it enters context. |
| Try to do the same thing again next month | re-read `shared/HOOK_PRINCIPLES.md` before adding hooks | Decision rule + minimal safe catalogue. |

## The three canonical flows

### Flow A — New feature, ticket to PR

```
1. spec-writer              →  .tickets/FEAT-042.md with ACs
2. ticket-critic            →  enforces AC→Test table; moves to Stage: BUILD
3. antiplan                 →  adversarial check on the plan
4. (implement)              →  cleanup + WRITE_TIME_GUARD blocks duplication
                               cleanup + LAYER_ENFORCEMENT blocks upward imports
5. tdd (red → green)        →  MOCK_CONTRACT validates boundary mocks
6. tdd/MUTATION             →  prove the tests aren't tautological
7. verify-claim             →  evidence gate
8. pr-create                →  Phase 0 gates + push + PR
```

Typical time to insight if something's wrong: step 2 (AC-test binding
forces intent-first thinking) or step 6 (mutation survivors reveal
circular tests).

### Flow B — Reviewing an incoming PR

```
1. pr-review <owner/repo> <pr>
   → 5 sub-agents run in parallel
   → each finding passes its binary checklist
   → 5th agent (Spec-Traceability Auditor) maps every hunk to an AC
2. If comments require changes, the author runs:
   pr-fix                   →  one-at-a-time fixes with staleness check
```

### Flow C — Audit / cleanup pass on existing code

```
1. cleanup Phase 0          →  ruff, eslint, knip, ts-prune, vulture, jscpd,
                               madge --circular, LAYER_ENFORCEMENT
   → non-empty Phase 0 output must be resolved or explicitly ack'd
2. cleanup Phase 1-5        →  subjective rubric mapping (M1-M12, Tier A-C)
3. For any dead code found, route through antiplan AP-4 (YAGNI) before
   deleting — confirm nobody depends on it.
```

## What NOT to do

- Do not invoke `pr-review` on your own WIP branch every hour — it's
  for PR gating, not mid-stream development. Use `cleanup` for mid-stream.
- Do not invoke `tdd/MUTATION.md` on every save — it's slow. End of
  cycle only.
- Do not add new hooks without reading `shared/HOOK_PRINCIPLES.md` and
  checking the 5 criteria.
- Do not run `verify-claim` inside a TDD red-green loop — the red
  test failing IS the evidence. Run it at phase boundaries.
- Do not bypass RTK just because output "looks weird" — test with
  `rtk bypass <cmd>` once to confirm, then trust the proxy.
- Do not invoke all skills "just in case." Each one has a trigger;
  miss-triggering trains you and the agent to ignore them.

## Context hygiene

For rules-file authoring, context-packing strategies, and confusion-management patterns across any session, see `~/.skills/shared/CONTEXT_HYGIENE.md`.

## Discovering skills (and avoiding fabrication)

Every skill has a `description:` field in its frontmatter. Claude Code
surfaces them in a list when invoking. Use the description to decide —
if the description doesn't clearly match what you're doing, don't
invoke it.

Companion files (`MOCKING.md`, `MOCK_CONTRACT.md`, `MUTATION.md`,
`LAYER_ENFORCEMENT.md`, `WRITE_TIME_GUARD.md`, `WORKFLOW_GATES.md`,
`HOOK_PRINCIPLES.md`, `TOKEN_BUDGET.md`) are loaded by their parent
skill at the appropriate phase — you don't invoke them directly.

## One-liners for Claude Code

```
# Starting a ticket
"Use spec-writer to turn this into a ticket: <paste user story>"
"Run ticket-critic on .tickets/FEAT-042.md"

# Implementing
"Write a test for AC-1 using tdd"
"Check layer boundaries on the changes I just made"

# Before PR
"Run verify-claim on my recent changes"
"Open a PR for this branch"  ← triggers pr-create Phase 0 gates

# Reviewing
"Review PR c3-e/c3fed-usmc#2856"
"Fix the review comments on PR 2856"

# Auditing
"Run cleanup Phase 0 on src/auth/"
"Reframe these docs for an exec audience"
```
