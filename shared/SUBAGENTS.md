# Subagents: suggested, never required

Skills may suggest a subagent (an agent in a separate context).
No skill requires one.
The output contract and any validator are the same either way.

## When a subagent earns its cost

- **Independence.** Reviewing output this same context produced (a plan, a diff, a ticket claim). Self-review in one context shares its blind spots.
- **Context pressure.** The work would push the main context past roughly half full (many tickets, a large diff).
- **Parallel work.** Independent pieces that can run at once and merge by a fixed format.

If none apply, run the role inline.

## Running a role inline

1. Load the role's prompt from the skill and follow it as written.
2. Produce the same artifact or block, in the same format.
3. Put `run: inline` in the artifact header so readers know there was no independent pass.
4. For an independence role (Challenger, Coverage Auditor, evidence reviewer, gate review), say once that a subagent or a fresh session would be more independent, then proceed.

## Harnesses without subagents

Run inline, or hand the role to a fresh session with a copy-pasteable prompt.
