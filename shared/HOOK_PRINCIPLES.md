# Hook & Skill Principles

Canonical reference for when to invoke each enforcement skill and when
to promote it to a hook. Referenced by `project-onboarding`,
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
| `caveman` | Context > 50%, bulk reports | First reply, specs, errors | No - the agent cannot measure its own context; invoke on demand |
| `cleanup/WRITE_TIME_GUARD.md` | New file or new export in mature repo | Tests, generated, prototypes | No — call from workflow |
| `cleanup/LAYER_ENFORCEMENT.md` | Import added AND layer map exists | No layer map | **Advisory** PostToolUse |
| `tdd/MOCK_CONTRACT.md` | New boundary mock in prod test | Pure-fn tests, spikes | **Advisory** on test file writes |
| `tdd/MUTATION.md` | End of TDD cycle, pre-PR audit | Every save (too slow) | No — on demand |
| `project-onboarding/WORKFLOW_GATES.md` | First turn of a session | Every prompt | No - link it from the project AGENTS.md, which every harness loads |
| Self code review | Before `gh pr create` | Draft PRs | No - `pr-create` Phase 0 runs it |
| `ticket-critic` AC→Test table | Ticket promoting to `Stage: BUILD` | NEW/SPEC tickets | No - `/todo` state detection routes to it |
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

## Hook catalogue

One hook. Add another only when a real failure mode points to it.

| Hook | Event | Mode | Timeout |
|---|---|---|---|
| `verify-claim-gate` | `PreToolUse: Bash` running `git commit` or `gh pr create` | halt | 5s |

It only catches an agent that ran verify-claim, recorded a failure, and
tried to ship anyway. It cannot catch an agent that never ran the check;
that rule lives in AGENTS.md and `pr-create` Phase 0.

Removed hooks and where their intent lives now:

- PR self-review reminder → `pr-create` Phase 0.
- Ticket BUILD reminder → `/todo` state detection.
- Workflow-gates notice → a link from the project AGENTS.md.
- Caveman context reminder → on demand; no hook can see context usage.

Advisory hooks that only print and exit 0 are not shown to the model on
some harnesses. Don't add one; make it block, or make it a skill step.

Anti-examples (do NOT add these):

- Any hook on `PreToolUse: Write` or `Edit` that greps the codebase
- Any hook that runs the full test suite
- Any hook that invokes `mutation-critic` or `pr-review` on every save
- Any hook blocking with no override path
- Any hook reporting subjective judgments (opinion-as-policy)

## Override protocol

Hooks accept two bypasses:

1. Resolve the cause (for `verify-claim-gate`: produce the evidence, or
   the user says `override: <reason>` and the agent deletes the marker
   and records the reason in the PR body).
2. `.hooks-disabled` (or `.claude/hooks-disabled`) at repo root - hooks
   skip silently until removed. Used for spikes and prototypes.

Agents MUST NOT override hooks on their own reasoning. "I think this
is fine" is not an override.

## Escalation for new hooks

Before adding another hook, write down:

1. What failure mode does this catch that existing hooks miss?
2. How often will it fire (per session, per week)?
3. What's the false-positive rate on a typical week's work?
4. What's the blast radius of the miss it prevents?
5. Can it be an advisory skill instead?

If answers 1 or 4 are weak, or answer 3 is high, keep it as a skill.
