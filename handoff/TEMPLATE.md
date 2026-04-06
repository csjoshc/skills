# Handoff — Prompt Template and Anti-patterns

## Handoff prompt template

Use this structure inside the **Handoff prompt** block (adapt sections; omit empty ones).

**⚠️ Important**: Wrap your entire output in a markdown code block so it can be copied with one click:

````markdown
```markdown
## Context
- Workspace: `<absolute path>`
- Stack / runtime (if known): …

## Goal
<What success means>

## Current state
<What is already done vs not done>

## Constraints
<Non-negotiables: compatibility, no new deps, style, etc.>

## Key files (read these)
- `<absolute path>` — <role>
- …

## Related standards / trackers (if any)
- `<absolute path>` — <purpose>

## Your task
1. …
2. …

## Plan (if applicable)
Execute the steps in: `<absolute path>/.handoff/plan-<slug>.md`

## Verification
<How to confirm completion: tests, commands, acceptance criteria>

## Open questions / risks (if any)
- …
```
```
````

Tone: **direct instructions** to the receiving agent ("Implement…", "Read…", "Do not…").

---

## Anti-patterns

- **Chat transcript** — Do not paste long back-and-forth. Distill to decisions and facts.
- **Vague paths** — Never "the tests folder"; always absolute paths when known.
- **Missing verification** — Always say how the next agent proves correctness.
- **Plan in chat only** — For complex work, put the step list in `.handoff/plan-*.md` and only **summarize** in the prompt.

---

## Skill Clusters (Reference)

When handing off, optionally include which skill cluster the recipient should draw from.

| Task Type | Skills to consider |
|----------|-------------------|
| **Frontend UI** | `make-ui`, `c3-ui`, `test-ui`, `chrome-devtools` |
| **Backend Tests** | `c3-backend-tests`, `tdd` |
| **Git/PR Work** | `create-pr`, `pr-review`, `pr-fix` |
| **Infrastructure** | `skill-sync`, `mcp-sync`, `confluence-diagrams` |
| **Planning/Specs** | `spec-writer`, `ticket-critic`, `tdd` |
| **CLI/Tooling** | `cmd-cli` |
| **Onboarding** | `project-onboarding` |

### In handoff prompt

Add an optional line under "Constraints" or "Context":

```markdown
## Recommended skills
- Cluster: <task type from table above>
- Specifically: make-ui, c3-ui (example)
```

---

## Quick checklist before sending

- [ ] Paste-ready block is wrapped in a markdown code block for one-click copying
- [ ] Paste-ready block is self-contained for a **new** agent.
- [ ] Task, goal, and **next actions** are explicit.
- [ ] All critical files use **full paths**.
- [ ] Standards/trackers/specs mentioned with paths if relevant.
- [ ] Complex work has `.handoff/plan-<slug>.md` and that path is in the prompt.
- [ ] Verification / acceptance criteria included.
- [ ] Skill cluster guidance included if applicable (see "Skill Clusters" section)
