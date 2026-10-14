# Handoff: Prompt Template and Checklist

## Handoff prompt template

Use this structure inside the **Handoff prompt** block; adapt sections and omit empty ones.
Wrap the whole prompt in a `markdown` code block so it copies in one click:

````markdown
```markdown
## Context
- Workspace: `<absolute path>`
- Stack / runtime (if known): ...

## Goal
<What success means>

## Current state
<What is already done vs not done>

## Constraints
<Non-negotiables: compatibility, no new deps, style, etc.>

## Key files (read these)
- `<absolute path>` - <role>
- ...

## Related artifacts (authoritative, read these)
- `<absolute path, URL or commit sha>` - <spec, ADR, ticket, tracker, standards file: why it matters>

## Your task
1. ...
2. ...

## Plan (if applicable)
Execute the steps in: `<absolute path>/.handoff/plan-<slug>.md`

## Suggested skills
- `<skill>` - <which step it serves>

## Verification
<How to confirm completion: tests, commands, acceptance criteria>

## Open questions / risks (if any)
- ...
```
````

Tone: **direct instructions** to the receiving agent ("Implement...", "Read...", "Keep...").

---

## Write it like this

- **Decisions and facts**: distill the conversation to what was decided and why; leave the back-and-forth behind.
- **Absolute paths**: name `/abs/path/to/tests/`, never "the tests folder".
- **Pointers over copies**: link specs, ADRs, tickets and commits by path, URL or sha.
- **Verification stated**: always say how the next agent proves it is done.
- **Steps in the plan file**: for complex work, the step list lives in `.handoff/plan-*.md` and the prompt only summarizes it.
- **Secrets by location**: name the env var or secrets file, never the value; leave out personal data.

---

## Suggested skills

Name the skills the next agent should invoke, tied to the step each one serves.
Pick from this map, or from `~/.skills/PLAYBOOK.md`; read a skill's SKILL.md before recommending it.

| Task type | Skills to consider |
|----------|-------------------|
| **Frontend UI** | `make-ui`, `test-ui`, `chrome-devtools` |
| **Tests / bug fix** | `tdd` |
| **Git / PR work** | `pr-create`, `pr-review`, `pr-fix`, `verify-claim` |
| **Planning / specs** | `todo`, `antiplan`, `spec-writer`, `ticket-critic` |
| **Infrastructure** | `agent-sync`, `confluence-diagrams` |
| **CLI / tooling** | `cmd-cli` |
| **Onboarding** | `project-onboarding` |

---

## Quick checklist before sending

- [ ] Paste-ready block is wrapped in a markdown code block for one-click copying.
- [ ] Paste-ready block is self-contained for a **new** agent.
- [ ] Task, goal, and **next actions** are explicit.
- [ ] All critical files use **full paths**.
- [ ] Specs, ADRs, tickets and commits are referenced by path, URL or sha, not pasted.
- [ ] Secrets and personal data are redacted.
- [ ] Complex work has `.handoff/plan-<slug>.md` and that path is in the prompt.
- [ ] Verification / acceptance criteria included.
- [ ] Suggested skills section names a skill per step where one applies.
- [ ] Handoff prompt prose passes `/stop-slop` to remove AI writing patterns.
