# Subagents: suggested, never required

Skills may suggest a subagent (an agent in a separate context).
No skill requires one.
The output contract and any validator are the same either way.

## When a subagent earns its cost

- **Independence.** Reviewing output this same context produced (a plan, a diff, a ticket claim). Self-review in one context shares its blind spots.
- **Context pressure.** The work would push the main context past roughly half full (many tickets, a large diff).
- **Parallel work.** Independent pieces that can run at once and merge by a fixed format.

If none apply, run the role inline.

## Depth and briefs

- Only the top-level session spawns subagents. A skill running inside a subagent runs its roles inline and marks `run: inline`.
- Brief subagents with pointers (paths to spec, tickets, notes), not pasted content.

## Running a role inline

1. Load the role's prompt from the skill and follow it as written.
2. Produce the same artifact or block, in the same format.
3. Put `run: inline` in the artifact header so readers know there was no independent pass.
4. For an independence role (Challenger, Coverage Auditor, evidence reviewer, gate review), say once that a subagent or a fresh session would be more independent, then proceed.

## Waiting on remote CI

A subagent that waits on a GitHub Actions run polls in a loop with short sleeps; it never uses Monitor (that tracks local processes) or one long `gh run watch`, which trips the 600s stall watchdog.
```
until [ "$(gh run view <id> -R <owner>/<repo> --json status -q .status)" = completed ]; do sleep 20; done
gh run view <id> -R <owner>/<repo> --json conclusion,url
```
Resume a stalled one with SendMessage, not a new agent; its run and PR are untouched.

## Harnesses without subagents

Run inline, or hand the role to a fresh session with a copy-pasteable prompt.
