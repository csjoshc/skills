# Skill Playbook

Which skill to reach for.
Skills also trigger from their `description:`; this is the human-readable map.
Each skill's SKILL.md is authoritative; this file only routes.

| You're about to... | Use | Notes |
|---|---|---|
| Make a small, scoped change | implement directly, `tdd` if you want test-first | No pipeline needed. |
| Fix a bug | `tdd` (Prove-It path) | Reproduce with a failing test first. |
| Build a defined feature (a few tickets) | `/todo spec <feature>` | Lite pipeline: spec-writer, optional ticket-critic, `/todo build`. |
| Build something risky, contested or large | `/todo start <feature>` | antiplan runs Fast Mode first and escalates only if needed. |
| Explore a fuzzy idea | `make-prd` | Collaborative, not adversarial. |
| Resume or hand off mid-pipeline | `/todo`, `/todo handoff` | Reads state from `.plan/` and `.tickets/`. |
| Claim "done" | `verify-claim` | Not inside a red-green loop; the failing test is the evidence there. |
| Open a PR | `pr-create` | |
| Self-check your branch | the harness's built-in code review | Cheaper than pr-review. |
| Review someone else's PR | `pr-review` | Posts evidence-backed inline comments. |
| Address review comments | `pr-fix` | One comment at a time. |
| Audit a repo, package or directory | `cleanup` | Not for branch diffs. |
| Strip unused template packages | `prune` | Run before `cleanup`. |
| Sync skills or MCP servers across tools | `agent-sync` | |

## Hooks

Gate hooks live in `hooks/` and parse input from any harness via `hooks/lib/hook-input.sh`.
Disable per project with `.hooks-disabled` (or `.claude/hooks-disabled`) at the repo root.
Read `shared/HOOK_PRINCIPLES.md` before adding a hook.

## Don't

- Don't run every skill just in case; mis-triggering trains everyone to ignore them.
- Don't run `pr-review` on your WIP every hour.
- Don't run `tdd/MUTATION.md` on every save; end of cycle only.
