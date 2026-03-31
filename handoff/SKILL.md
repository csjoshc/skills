---
name: handoff
description: >-
  Produces a copy-pasteable handoff prompt for a new agent with no prior context,
  summarizing the task or project, linked artifacts with full paths, and optional
  incremental plan files under .handoff/. Use when the user asks for a handoff,
  session handoff, context transfer, cold-start prompt, or to continue work in a
  new chat.
---

## TL;DR (Quick Start)

Produces a self-contained, copy-pasteable markdown prompt to transition work to a new agent or session. Summarizes goals, state, constraints, and next actions with absolute file paths.

**When to use:** "handoff", "session handoff", "context transfer", "continue in new chat".

**Invocation:**
```bash
/handoff
```

## Decision Tree

1. **How complex is the remaining work?**
   - Trivial (<10 lines, single file) → Generate prompt only.
   - Non-trivial (multiple files, migrations, multi-step) → **MANDATORY** Create `.handoff/plan-<slug>.md` and link it in the prompt.

2. **Are there non-obvious ordering constraints?**
   - YES → Detail them in the plan file; point to the specific task order in the prompt.
   - NO → List tasks directly in the prompt.

3. **Does the task involve specialized domains?**
   - YES → Reference the relevant **Skill Cluster** (e.g., Frontend UI, Backend Tests).

## Workflow

## Output contract

1. **Primary deliverable**: A single markdown section titled **Handoff prompt** (or similar) containing the full paste-ready text. The handoff must be **sufficient and necessary** to continue the task—not a dump of everything said, but everything a competent agent needs to succeed without guessing.

   **⚠️ Critical**: Wrap the entire handoff prompt in a markdown code block (triple backticks with "markdown" language tag) so the user can copy it with one click.

2. **Secondary deliverable** (conditional): If the remaining work is **complex or non-trivial** (see threshold below), also write a **plan file** and reference it by absolute path in the handoff prompt.

---

## What to summarize (always)

From the current conversation and any open or referenced files, extract and state clearly:

| Area | Include |
|------|---------|
| **Goal** | What “done” looks like; user constraints (stack, style, deadlines). |
| **Current state** | What exists now (branches, key files, deployed vs local). |
| **Task for the next agent** | Imperative, ordered list of what to do next—not a recap of the past. |
| **Repo / workspace** | Root path if known (e.g. `/Users/.../project`). |
| **Relevant paths** | Every file or directory the next agent must read or edit, with **full absolute paths**. |

### Helper and context files (mandatory when applicable)

If the work depends on standards, trackers, specs, or scripts **outside** the main code path, **name each with its full path** and one line on why it matters:

- Testing standards, skill files, team conventions  
- Progress trackers, TODO files, ADRs, specs (`METHOD.md`, `FR/NFR`, etc.)  
- Env or config the next agent must not ignore (e.g. `.env.example`, `docker-compose.yml`)

If nothing beyond normal source files applies, say so briefly (“No separate tracker or standards file; follow repo conventions in `README` at `…`”).

---

## Plan file (conditional)

### When to write `.handoff/plan-<slug>.md`

Write a plan file when **any** of these hold:

- The change is **not** a quick local edit (rule of thumb: **more than ~10 lines of substantive code in a single file**, or touch **multiple** files/modules).
- There are **non-obvious ordering constraints** (migrations before code, API before UI).
- Steps should be **incrementally verifiable** (tests, manual checks, build targets).

**Do not** write a plan file for trivial one-off edits (single small change, obvious verification).

### Where to put it

- Path: **`<workspace-root>/.handoff/plan-<slug>.md`**
- `<slug>`: short kebab-case topic, e.g. `plan-auth-refactor.md`, `plan-flight-price-api.md`. If multiple parallel tracks exist, use distinct slugs or a numeric suffix (`plan-02.md`).
- Create `.handoff/` if missing (in the **workspace root** the user is working in).

### Plan file content

Each plan must be:

- **Narrowly scoped** — one coherent deliverable or milestone per file (split if huge).
- **Stepwise** — ordered steps with **how to verify** each step (test command, expected outcome, or manual check).
- **Stable** — file paths, API names, and decisions stated explicitly so a cold agent does not depend on chat tone.

### Referencing the plan in the handoff prompt

In the paste-ready prompt, include a line such as:

- `Follow the incremental plan at: /absolute/path/to/workspace/.handoff/plan-<slug>.md`

The next agent should be instructed to **read that file first** (or immediately after the repo README if required).

---

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

Tone: **direct instructions** to the receiving agent (“Implement…”, “Read…”, “Do not…”).

---

## Anti-patterns

- **Chat transcript** — Do not paste long back-and-forth. Distill to decisions and facts.
- **Vague paths** — Never “the tests folder”; always absolute paths when known.
- **Missing verification** — Always say how the next agent proves correctness.
- **Plan in chat only** — For complex work, put the step list in `.handoff/plan-*.md` and only **summarize** in the prompt.

---

## Skill Clusters (Reference)

When handing off, optionally include which skill cluster the recipient should draw from. This is guidance — the agent picks, but you're pointing it in the right direction.

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

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing secondary file path — proceed, note the gap in "Open questions".
- **Tier 2 (conflict):** Handoff request contradicts current implementation — **STOP**, clarify with user before generating the prompt.
- **Tier 3 (security):** Handoff prompt includes secrets (API keys, tokens) — **STOP**, redact immediately, block and alert.

## Examples (Few-Shot)

**Example 1: Simple UI Polish**
Input: "Handoff the button styling to a new agent"
Output: Markdown prompt block with current CSS path and specific "Your task" to adjust hover states.

**Example 2: Complex Feature Implementation**
Input: "Handoff the user auth feature"
Output: `.handoff/plan-auth.md` created; Prompt generated referencing the plan, database schema path, and auth standards.
