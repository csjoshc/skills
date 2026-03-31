# Parallel / batched markdown tickets (Orchestra & similar runners)

Companion to **spec-writer** (`SKILL.md` in this directory). Load when the user asks for **parallel tickets**, **batch tickets for `-j` / `--concurrency`**, or **one session that emits many ordered tickets** for a runner that schedules from explicit edges only.

## When `-j` / `--concurrency` &gt; 1 is appropriate

- A **single** long-context session produced **all** tickets in the batch (one model, one coherent plan).
- Work is scoped to be **mutually independent** where possible: disjoint modules, no hidden shared refactors.
- **`Depends-On:`** (or your runner’s equivalent) encodes **every** ordering constraint. Schedulers that only honor explicit edges will **not** infer order from prose or file mentions.

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

## Canonical copy of this file

Master store: `~/.skills/spec-writer/PARALLEL_TICKETS_BATCH.md`.  
**Skill sync:** `~/.cursor/skills` should symlink to `~/.skills` (see skill-sync). Repos may add `project/.cursor/skills/spec-writer` → `../../../../.skills/spec-writer` so agents in the repo resolve the same companion as the global skill.
