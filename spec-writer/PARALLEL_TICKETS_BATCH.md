# Parallel / batched markdown tickets (Orchestra & similar runners)

Companion to **spec-writer** (`SKILL.md` in this directory). Load when the user asks for **parallel tickets**, **batch tickets for `-j` / `--concurrency`**, or **one session that emits many ordered tickets** for a runner that schedules from explicit edges only.

## When `-j` / `--concurrency` > 1 is appropriate

- A **single** long-context session produced **all** tickets in the batch (one model, one coherent plan).
- Work is scoped to be **mutually independent** where possible: disjoint modules, no hidden shared refactors.
- **`Depends-On:`** (or your runner's equivalent) encodes **every** ordering constraint. Schedulers that only honor explicit edges will **not** infer order from prose or file mentions.

## When to keep default concurrency 1

- Tickets come from **different** LLM sessions, models, or days — dependency information is unreliable.
- Any doubt about overlap or sequencing: serialize. Wrong order causes rework or merge pain.

## Authoring checklist (batch mode)

1. **DAG:** dependency field lists ticket **stems** (filename without `.md` if that is your convention); no cycles; upstream work is foundational.
2. **Stems match filenames** after renames; missing upstreams are usually skipped silently at sync time.
3. **Blast radius:** prefer tickets that name **disjoint** paths so parallel workers collide less often if the graph is imperfect.
4. **Parent/epic:** if you use `Parent:` (or equivalent), keep it consistent; children should depend on the **narrowest** real prerequisite, not only the epic.

## Orchestra-specific conventions

When the target is **Orchestra** (this repo or another project using the same ticket format), align YAML front matter and graph rules with the project skill:

- Path (orchestra repo): `.cursor/skills/orchestra-decomposed-tickets/SKILL.md`  
  (If that skill is not in the workspace, use the same content from the Orchestra repo you are driving.)

That skill covers **`Depends-On:`**, **`Parent:`**, decomposition, and blast radius for `.tickets/` markdown — without duplicating runner internals here.

---

## Creating Parallelizable Tickets

### The Core Principle

**Parallelizable tasks have clean interfaces defined BEFORE implementation.** If you can write the contract (API, data schema, function signature) before any code exists, the task is parallelizable. If the interface emerges during implementation, it's sequential.

### Test: The "Contract Test"

Ask: *"Can a worker complete this task without knowing what other workers decided?"*

- **Yes** → Parallel (e.g., "Add validation to the email field" — the contract is clear)
- **No** → Sequential (e.g., "Design the error handling strategy" — this affects everything)

### Pattern 1: Interface-First Decomposition

**Sequential (bad):**
```yaml
Title: Build user authentication
# Requires: DB schema → API → frontend → tests (each depends on prior)
```

**Parallelizable (good):**
```yaml
Title: Implement auth system — DB models
Depends-On: []
# Contract: User model {id, email, password_hash, created_at}
# Touches: models/user.py, migrations/001_users.py

---
Title: Implement auth system — API endpoint
Depends-On: []
# Contract: POST /auth/login {email, password} → {token, user_id}
# Touches: routes/auth.py, dto/auth.py

---
Title: Implement auth system — frontend form
Depends-On: []
# Contract: Consumes POST /auth/login, renders login UI
# Touches: components/LoginForm.tsx

---
Title: Implement auth system — tests
Depends-On: [auth-db-models, auth-api-endpoint, auth-frontend-form]
# Touches: tests/test_auth.py
```

### Pattern 2: File-Level Disjointness

Parallel tickets must have **zero file overlap** in their primary edit targets:

| Parallelizable | Sequential |
|---|---|
| Different modules (`auth/` vs `billing/`) | Same module (`api/users.py` for 3 features) |
| Different layers (backend vs frontend) | Same layer (3 API endpoints sharing middleware) |
| Orthogonal concerns (feature + tests + docs) | Interleaved concerns (feature A needs feature B's types) |

### Pattern 3: The Dependency Graph Rule

Build explicit DAGs where:
- **Root tickets** (no `Depends-On:`) can run in parallel
- **Leaf tickets** depend on all upstream work
- **No shared intermediate files** between parallel branches

```
Ticket A (no deps) ──┐
                      ├──→ Ticket D (depends on A, B, C)
Ticket B (no deps) ──┤
                      │
Ticket C (no deps) ──┘
```

### Pattern 4: Reasoning Chain Continuity

**Do NOT decompose** when:
- Step C requires "scratchpad thoughts" from Step A
- Subtasks share implicit assumptions that aren't documented
- Workers would need to re-derive prior reasoning
- The task requires architectural design decisions that affect everything

**DO decompose** when:
- Subtasks are truly independent (different domains, different files)
- Interfaces are explicit and documented in ticket specs
- Each worker has full context for its subtask
- Global constraints are listed in every ticket's front-matter

### Anti-Patterns to Avoid

1. **Hidden dependencies:** Ticket says "add feature X" but implicitly requires changes from ticket Y
2. **Shared refactors:** Two tickets both need to modify the same utility module
3. **Emergent interfaces:** "Figure out the API as you go" — define it first
4. **Cross-cutting concerns:** "Update all error handling across the codebase" — this touches everything
5. **Architectural decisions:** "Choose the database strategy" — this affects all downstream work

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
- **Maximum:** 4 workers (hard cap in Orchestra's concurrent runner)
- **Beyond 4:** Coordination overhead exceeds benefits — split into sequential batches

---

## Canonical copy of this file

Master store: `~/.skills/spec-writer/PARALLEL_TICKETS_BATCH.md`.  
**Skill sync:** `~/.cursor/skills` should symlink to `~/.skills` (see skill-sync). Repos may add `project/.cursor/skills/spec-writer` → `../../../../.skills/spec-writer` so agents in the repo resolve the same companion as the global skill.
