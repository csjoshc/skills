# Hook & Skill Principles

Canonical reference for when to invoke each enforcement skill and when
to promote it to a hook. Referenced by `hook-sync`, `project-onboarding`,
and any agent that asks "should this be a hook?"

## Why hooks backfire

A hook becomes counter-productive when it does any of these:

1. Fires on every save → agent learns to dismiss output → signal dies.
2. Adds > 500ms per invocation on a hot event → session slows measurably.
3. Dumps verbose output into the context window → poisons later turns.
4. Cascades into its own tool calls (especially `PreToolUse: Bash` → Bash).
5. Can be silently bypassed → bypass becomes the norm.
6. Enforces a stale rule nobody owns.
7. Over-enforces on spikes, prototypes, research code.

## Hook criteria (all five required)

Promote a skill to a hook only if:

- [ ] Check runs in < 500ms on a warm system
- [ ] Event is rare (PR creation, commit, session open — not every edit)
- [ ] Signal is high (low false-positive rate in practice)
- [ ] Cost of the miss is high (shipped bug, false claim, policy breach)
- [ ] Bypass is explicit (user action, not agent reasoning)

If any criterion fails, keep it as a skill invoked on demand.

## Skill trigger matrix

| Skill / companion | Best trigger | Avoid when | Hook? |
|---|---|---|---|
| `verify-claim` | Before PR, before commit of a fix | Mid-TDD loop | **Yes — halt** on PR/commit |
| `hook-sync` | After editing `~/.hooks/*` | Every session | No — manual |
| `caveman` | Context > 50%, bulk reports | First reply, specs, errors | **Conditional** on SessionStart |
| `cleanup/WRITE_TIME_GUARD.md` | New file or new export in mature repo | Tests, generated, prototypes | No — call from workflow |
| `cleanup/LAYER_ENFORCEMENT.md` | Import added AND layer map exists | No layer map | **Advisory** PostToolUse |
| `tdd/MOCK_CONTRACT.md` | New boundary mock in prod test | Pure-fn tests, spikes | **Advisory** on test file writes |
| `tdd/MUTATION.md` | End of TDD cycle, pre-PR audit | Every save (too slow) | No — on demand |
| `project-onboarding/WORKFLOW_GATES.md` | First turn of a session | Every prompt | **Yes — halt on missing context** |
| `pr-review` (5 agents) | Before `gh pr create` | Draft PRs | **Yes — advisory** |
| `ticket-critic` AC→Test table | Ticket promoting to `Stage: BUILD` | NEW/SPEC tickets | **Advisory** on ticket edits |
| `pr-fix` staleness | After each review-comment fix | No PR open | No — internal |
| `cleanup` Phase 0 | On-demand audit, pre-PR self-review | After every edit | No |

## The decision rule

> Hook if the cost of the miss is high AND the check is cheap AND the
> event is rare. Skill otherwise.

Examples applied:

- `verify-claim` on `git commit` → HIGH cost (false done), CHEAP check
  (scan recent claims), RARE event → **hook**.
- `mutation-critic` on every save → HIGH cost (tautological test), but
  EXPENSIVE check (seconds) and FREQUENT event → **skill**.
- `redundancy-watcher` on every `Write` → moderate cost, cheap-ish
  check but FREQUENT event → **skill**, invoked from `workflow-guard`.

## Advisory vs. blocking

Reserve `halt` for unambiguous, user-visible harms:

- Secrets in staged files
- `CLAIM_UNVERIFIED.md` present at PR/commit time
- Upward layer imports with a provided fix suggestion

Everything else is `advisory` — the hook posts a report; the agent or
user decides. Advisory hooks degrade gracefully; blocking hooks must
earn their block with a concrete, cheap alternative.

## Minimal safe hook catalogue

Start with these five and nothing more. Add a sixth only when a real
failure mode points to it.

| Hook | Event | Mode | Timeout |
|---|---|---|---|
| `verify-claim-gate` | `PreToolUse: Bash(gh pr create*\|git commit*)` | halt | 5s |
| `pr-review-self-check` | `PreToolUse: Bash(gh pr create*)` | advisory | 30s |
| `workflow-gates-session` | `SessionStart` | setup-only (no block) | 1s |
| `ticket-critic-build-gate` | `PostToolUse: Edit(.tickets/*.md)` with `Stage: BUILD` in diff | advisory | 3s |
| `caveman-budget-auto` | `SessionStart` with `context_usage > 0.5` | setup-only | 500ms |

Anti-examples (do NOT add these):

- Any hook on `PreToolUse: Write` or `Edit` that greps the codebase
- Any hook that runs the full test suite
- Any hook that invokes `mutation-critic` or `pr-review` on every save
- Any hook blocking with no override path
- Any hook reporting subjective judgments (opinion-as-policy)

## Override protocol

All hooks must accept a bypass in one of two forms:

1. `override: <reason>` typed by the user — recorded to
   `.claude/hook-overrides.log` with timestamp and reason.
2. Presence of `.claude/hooks-disabled` at repo root — hooks skip
   silently until removed. Used for spikes and prototypes.

Agents MUST NOT override hooks on their own reasoning. "I think this
is fine" is not an override.

## Escalation for new hooks

Before adding a sixth hook, write down:

1. What failure mode does this catch that existing hooks miss?
2. How often will it fire (per session, per week)?
3. What's the false-positive rate on a typical week's work?
4. What's the blast radius of the miss it prevents?
5. Can it be an advisory skill instead?

If answers 1 or 4 are weak, or answer 3 is high, keep it as a skill.
