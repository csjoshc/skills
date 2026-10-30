# Handoff file

Write this to `<workspace>/.agent-local/handoff/<slug>.md`. Drop empty sections. Add Verification only when a named check is needed.

```markdown
# <short title>

## Goal
<What done looks like>

## Current state
<What exists now, and what is left>

## Next action
1. <imperative step>
2. ...

## Constraints
- <only rules that change this work>

## Pointers
- `<absolute path, URL or commit sha>` - <why it matters>

## Verification
<test, command or acceptance check>
```

Address the next session: "Read...", "Implement...", "Keep...".

## Writing rules

- Distill decisions and facts. Leave the conversation out.
- Use absolute paths for local files.
- Point at specs, ADRs, tickets and commits. Do not copy their bodies.
- Name the env var or secrets file, never the value.
- Skip Verification when the next action already names the check.

## Before sending

- [ ] One file at `.agent-local/handoff/<slug>.md`
- [ ] Chat reply is that file's absolute path plus a few sentences on what to do next
- [ ] No paste-ready prompt block and no second plan file
- [ ] Goal, current state and next action are explicit
- [ ] Pointers use full paths
- [ ] Secrets are redacted
- [ ] Call the Skill tool with `stop-slop` on the file and the chat reply
