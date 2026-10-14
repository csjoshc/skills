# Parallel / batched markdown tickets (for ticket runners)

## Contents

- When `-j` / `--concurrency` > 1 is appropriate
- When to keep default concurrency 1
- Authoring checklist (batch mode)
- Ticket format conventions
- Creating Parallelizable Tickets
- Canonical copy of this file


Companion to **spec-writer** (`SKILL.md` in this directory). Load when the user asks for **parallel tickets**, **batch tickets for `-j` / `--concurrency`**, or **one session that emits many ordered tickets** for a runner that schedules from explicit edges only.

## When `-j` / `--concurrency` > 1 is appropriate

- A **single** long-context session produced **all** tickets in the batch (one model, one coherent plan).
- Work is scoped to be **mutually independent** where possible: disjoint modules, no hidden shared refactors.
- **`Depends-On:`** (or your runner's equivalent) encodes **every** ordering constraint. Schedulers that only honor explicit edges will **not** infer order from prose or file mentions.

## When to keep default concurrency 1

- Tickets come from **different** LLM sessions, models, or days: dependency information is unreliable.
- Any doubt about overlap or sequencing: serialize. Wrong order causes rework or merge pain.

## Authoring checklist (batch mode)

1. **DAG:** dependency field lists ticket **stems** (filename without `.md` if that is your convention); no cycles; upstream work is foundational.
2. **Stems match filenames** after renames; missing upstreams are usually skipped silently at sync time.
3. **Blast radius:** prefer tickets that name **disjoint** paths so parallel workers collide less often if the graph is imperfect.
4. **Parent/epic:** if you use `Parent:` (or equivalent), keep it consistent; children should depend on the **narrowest** real prerequisite, not only the epic.

## Ticket format conventions

Align YAML front matter and graph rules (**`Depends-On:`**, **`Parent:`**, decomposition, blast radius) with whatever ticket format your runner expects. If the project ships its own decomposed-tickets skill, load it alongside this one.

---

## Creating Parallelizable Tickets

### The Core Principle

**Each ticket is a vertical slice: a narrow but complete path through every layer it needs, demoable or verifiable on its own.**
Parallelism comes from slices that touch disjoint files, not from splitting one feature by layer.
A slice whose interface depends on another slice's choices waits for it through a `Depends-On:` edge.

<!-- vertical-slice rules adapted from mattpocock/skills to-tickets (MIT) -->

### Test: The "Contract Test"

Ask: *"Can a worker complete this slice without knowing what other workers decided?"*

- **Yes** → Parallel (e.g., "Add validation to the email field": the contract is clear)
- **No** → Sequential (e.g., "Design the error handling strategy": this affects everything)

### Pattern 1: Vertical Slices With Explicit Edges

Each slice ships schema, logic, UI and its own tests together, sized for one fresh context window.
Prefactoring lands first so later slices start from easy-to-change code.

```yaml
Title: Auth - prefactor session helper out of routes/base.py
Depends-On: []
Files: [auth/session.py, routes/base.py, tests/test_session.py]

---
Title: Auth - email + password login, end to end
Depends-On: [auth-prefactor-session]
Files: [models/user.py, migrations/001_users.py, routes/auth.py, components/LoginForm.tsx, tests/test_login.py]
# Demo: a seeded user logs in through the form and lands on the dashboard

---
Title: Billing - show current plan on account page
Depends-On: []
Files: [billing/plan.py, components/PlanCard.tsx, tests/test_plan_card.py]
# Runs in parallel with the auth chain: no shared files

---
Title: Auth - password reset, end to end
Depends-On: [auth-login]
Files: [routes/reset.py, components/ResetForm.tsx, tests/test_reset.py]
```

Wide refactors (rename a column, retype a shared symbol) cannot land as one green slice.
Sequence them as expand, migrate batches, contract; see `references/ticket-template.md` → *Vertical slices + task sizing*.

### Pattern 2: File-Level Disjointness

Parallel tickets must have **zero file overlap** in their primary edit targets:

| Parallelizable | Sequential |
|---|---|
| Different modules (`auth/` vs `billing/`) | Same module (`api/users.py` for 3 features) |
| Slices touching disjoint files end to end | Slices that share a file (3 endpoints in one router) |
| Independent features, each with its own tests | Interleaved features (feature A needs feature B's types) |

### Pattern 3: The Dependency Graph Rule

Build explicit DAGs where:
- **Root tickets** (no `Depends-On:`) can run in parallel
- **Each ticket** lists only the tickets that genuinely gate it, so the frontier stays wide
- **No shared intermediate files** between parallel branches

```
Slice A (no deps) ──→ Slice B (depends on A)
Slice C (no deps) ──→ Slice D (depends on C)
                       Slice E (depends on B, D)
```

### Pattern 4: Reasoning Chain Continuity

Keep work in one ticket when:
- Step C requires "scratchpad thoughts" from Step A
- Subtasks share implicit assumptions that aren't documented
- Workers would need to re-derive prior reasoning
- The task requires architectural design decisions that affect everything

Split into parallel tickets when:
- Slices are truly independent (different domains, different files)
- Interfaces are explicit and documented in ticket specs
- Each worker has full context for its slice
- Global constraints are listed in every ticket's front-matter

### Anti-Patterns to Avoid

1. **Hidden dependencies:** Ticket says "add feature X" but implicitly requires changes from ticket Y. Add the `Depends-On:` edge.
2. **Shared refactors:** Two tickets both need to modify the same utility module. Prefactor it in its own upstream ticket.
3. **Emergent interfaces:** "Figure out the API as you go". Settle it in the first slice that needs it, and make later slices depend on that one.
4. **Cross-cutting concerns:** "Update all error handling across the codebase". Sequence it as expand-contract.
5. **Architectural decisions:** "Choose the database strategy". Decide it in the PLAN (ADR) before any slice starts.
6. **Horizontal splits:** separate DB, API, UI and test tickets for one feature. None is demoable alone, and the test ticket finds the integration bugs last.

### Global Constraints in Parallel Tickets

Every parallel ticket must include the same `Global-Constraints:` to prevent premise shifts:

```yaml
---
Stage: BUILD
Type: feature
Global-Constraints:
  - All endpoints must return JSON with {error, details} format
  - Use PostgreSQL with SQLAlchemy ORM
  - Auth via JWT Bearer tokens
  - No shell subprocess execution
---
```

### Batch Size Guidelines

- **Optimal:** 3-4 parallel workers (research shows saturation at 4 agents)
- **Maximum:** 4 workers (typical cap for concurrent runners)
- **Beyond 4:** Coordination overhead exceeds benefits: split into sequential batches

---

## Canonical copy of this file

Master store: `~/.skills/spec-writer/PARALLEL_TICKETS_BATCH.md`.  
**Skill sync:** `~/.cursor/skills` should symlink to `~/.skills` (see agent-sync). Repos may add `project/.cursor/skills/spec-writer` → `../../../../.skills/spec-writer` so agents in the repo resolve the same companion as the global skill.
