# Skill Playbook

Which skill to reach for.
Skills also trigger from their `description:`; this is the human-readable map.
Skills marked *(typed)* are user-invoked: they fire only when you type their name, and no other skill can call them.
Each skill's SKILL.md is authoritative; this file only routes.
Before stating what a skill does or advising that a step be skipped, read that skill's SKILL.md; the notes here are for orientation only.

| You're about to... | Use | Notes |
|---|---|---|
| Make a small, scoped change | implement directly, `tdd` if you want test-first | No pipeline needed. |
| Fix a bug | `tdd` (Prove-It path) | Reproduce with a failing test first. |
| Build a defined feature (a few tickets) | `/todo` or `/todo spec <feature>` *(typed)* | Bare `/todo` drives spec then subagent builds. |
| Build something risky, contested or large | `/todo start <feature>` *(typed)* | challenge runs Fast Mode first and escalates only if needed. |
| Explore a fuzzy idea | `/prd` *(typed)* | Collaborative, not adversarial. |
| Resume or hand off mid-pipeline | `/todo`, `/todo handoff` *(typed)* | Reads state from `.agent-local/plan/` and `.agent-local/tickets/`. Bare `/todo` drives. |
| Move work to a new harness, directory or colleague | `handoff` | Writes `.agent-local/handoff/<slug>.md`; replies with the path. |
| Claim "done" | `verify` | Inside a red-green loop the failing test is the evidence; use it at the end. |
| Open a PR | `pr-create` | |
| Self-check your branch | the harness's built-in code review | Cheaper than pr-review. |
| Review someone else's PR | `pr-review` | Posts evidence-backed inline comments. |
| Address review comments | `pr-fix` | One comment at a time. |
| Audit a repo, package or directory | `cleanup` | For whole trees; branch diffs go to code review. |
| Strip unused template packages | `prune` | Run before `cleanup`. |
| Document a fork | `/fork-audit` *(typed)* | |
| Sync skills or MCP servers across tools | `/sync` *(typed)* | |
| Look back after a pass or a session that went sideways | `/retro` *(typed)* | Turns mistakes into hooks, lint or standards. Run it before clearing. |

## Phase boundaries

### Authoring and review workflow map

The [shared change-quality contract](shared/QUALITY_RUBRIC.md#change-quality-pass) owns the rubric.
This map owns navigation; skills own execution and evals check behavior.
Carry the same claims forward in the existing ticket, chat brief, or PR body, not a new document per stage.

| Stage | Entry | Application of the contract |
|---|---|---|
| Establish | `spec` / `/todo`, or a brief for a small edit | State intent, structure, planned evidence, and delivery boundary before delegation |
| Implement | `tdd` / `ui` | Produce the evidence and check scope at the first working slice |
| Prepare handoff | `verify` | Match the account to the final diff and evidence |
| Request review | `pr-create` | Apply aggregate review budget and present the concise account |
| Challenge | `pr-review`, or the chosen human/built-in reviewer | Independently assess the same contract |
| Examine cumulative debt | `cleanup` | Propose separately scoped work rather than expanding the active PR |

Read a cross-skill policy change in this order: shared contract, corrected contradictions, caller wiring, then evals.
Change obligations in the contract; change when/how they apply in the owning skill.

### Session transitions

A phase is a chunk of work inside a session (grilling, implementing, QA).
Decide at the boundary between phases; mid-phase, continue or split the rest into subagents.
Ask in order; the first yes wins:

1. **Continue**: the next phase needs this one as a primary source, or there is room left in the window. Free and lossless.
2. **`/clear`**: nothing here matters to what comes next. Clearing relevant context loses the why for good.
3. **`handoff`**: the work is moving to a new harness, a new directory, a colleague, or a side task forked mid-phase.
4. **Subagent**: the task is scoped tightly enough to run unattended (review, research) and report back.
5. **`/compact`**: the default when nothing above fits. Pass an instruction so the summary keeps what the next phase needs.

Adapted from Matt Pocock's `ask-matt` phase boundaries (MIT).

## Hooks

Gate hooks live in `hooks/` and parse input from any harness via `hooks/lib/hook-input.sh`.
Disable per project with `.hooks-disabled` (or `.claude/hooks-disabled`) at the repo root.
Read `shared/HOOK_PRINCIPLES.md` before adding a hook.

## Use skills sparingly

- Invoke a skill when its trigger actually fits; a precise trigger keeps people trusting them.
- Run `pr-review` when a branch is ready for review; use the built-in code review for WIP checks.
- Run `tdd/MUTATION.md` at the end of a cycle.
