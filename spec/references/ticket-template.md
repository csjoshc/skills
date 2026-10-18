# Ticket template: SPEC, PLAN, TASKS sections

Read this when drafting or revising a ticket body. The Stage header contract stays in SKILL.md.

## Contents

- SECTION 1: SPEC (incl. success-criteria reframing)
- SECTION 2: PLAN (AC table, test paths, failure paths)
- SECTION 3: TASKS (task format, vertical slices, expand-contract, sizing)

### SECTION 1: SPEC

**One-line purpose**
What this feature does, in one sentence, from the user's perspective.

**Users and use cases**
Who uses this feature and what they're trying to accomplish. List each use case as: `As a [user type], I want to [action] so that [outcome].`

**Requirements**
What must be true for this feature to work. Numbered list. Functional only — no implementation details.

**Scope boundary (recommended)**  
Short **IN scope** / **OUT of scope** lists so agents do not gold-plate or miss boundaries (METHOD Phase 1).

**Edge cases**
What can go wrong or behave unexpectedly. For each: describe the situation and the expected behavior.

**Acceptance criteria**
Use Given/When/Then format. One criterion per scenario. Cover the happy path first, then edge cases.

#### Reframe instructions as success criteria

<!-- merged from addyosmani/agent-skills spec-driven-development -->

Vague verbs ("faster", "better", "more responsive") are not testable. Translate every directive into a measurable target before writing ACs. Loop the human on the target, not the wording.

| Vague instruction | Reframed success criterion |
|---|---|
| Make the dashboard faster | LCP < 2.5s on 4G; initial data < 500ms; CLS < 0.1 |
| Improve search | p95 query < 200ms; relevance > baseline by X on the eval set |
| Better error handling | All boundaries return structured errors; no swallowed exceptions; user sees actionable message |

If you can't measure it, don't ship it as an AC.

```
Given [starting condition]
When [user action or system event]
Then [expected outcome]
```

Mark every assumption with `[ASSUMPTION: ...]` inline. Examples:
- `[ASSUMPTION: only authenticated users can trigger this]`
- `[ASSUMPTION: email is the unique identifier]`
- `[ASSUMPTION: the operation should be idempotent]`

---

### SECTION 2: PLAN

**Stack and architecture**
State what you know about the user's stack from context. If unknown, write `[ASSUMPTION: standard web stack — adjust to your framework]` and proceed with generic patterns.

**Data model changes**
What needs to be created, modified, or deleted in the data layer. Be specific about fields and types.

**API contracts**
Endpoints or functions needed. For each: method, path or name, inputs, outputs, error states.

**Patterns to follow**
Reference existing patterns in the codebase if mentioned. If not mentioned, flag: `[ASSUMPTION: following standard CRUD pattern — point me to your auth/data layer if you want me to match your conventions]`

**Acceptance Criteria → Tests** (required)

The table format, the check rules and the ticket sections are defined once in [`../../shared/TICKET_CONTRACT.md`](../../shared/TICKET_CONTRACT.md): `| AC | Check | Tier |`, one test id or one shell command per row, at least one `(failure path)` row.
`/tdd` Phase 0 reads the Tier column and derives the test pattern and mutation flag itself, so the table carries nothing else.

**Test path convention:** a test id in the Check column must be the **permanent, committed path** — the file is created there directly during BUILD, never in `tests/tickets/` (deprecated gitignored staging area).

| Test type | Permanent path |
|---|---|
| Dockerfile / Helm / nginx / CI workflow regression | `tests/infra/test_<artifact>.py` |
| Documentation consistency | `tests/docs/test_<topic>.py` |
| Package unit/integration | `packages/<pkg>/tests/test_<module>.py` |

For PDCA-T / METHOD.md workflows: add a short line beneath the table calling out **test-first** ordering and any **quality targets** (e.g. coverage floor) the user or repo mandates. Don't re-list per-AC categories (happy/error/edge) as prose; the AC rows carry them.

**Security and performance constraints**
Authentication requirements, authorization rules, rate limits, response time targets. Mark each unknown as `[ASSUMPTION: ...]`.

**Failure paths (conditional — include when ticket carries `[FALLIBLE_IO]` tags)**
For each external boundary the ticket touches (API, LLM, database, stream,
third-party service): state what happens when it fails. Errors must propagate
(re-throw or structured error response), never be silently caught and
swallowed. Format:
- **Boundary:** [name] — **On failure:** [what the user sees + what gets logged]

**Architecture decisions (optional)**
Add an **ADR-NN** entry only for a decision that is hard to reverse, surprising without context, and a real trade-off (test in `../PDCA_T.md`). Everything else stays prose.

**Design alternatives (if upstream analysis exists)**
If challenge or prior design discussion surfaced alternatives or rejected options, include a short subsection explaining why the recommended approach was chosen and what tradeoffs were considered. Reference upstream analysis to avoid re-debating settled decisions.

---

### SECTION 3: TASKS

Break the plan into **ordered atomic micro-instructions**: numbered tasks where each one is a **single** concrete action an agent can execute without inventing missing steps.

Each task must:
- Be completable in a single agent session
- Produce a verifiable, testable change
- Contain all context needed — no assumptions, no "see previous task"
- Have its own mini acceptance criteria
- Stay **one action per task** where possible; if a task must bundle steps, use numbered sub-steps, each still verifiable (**Do** + **Check** + **Test** at micro scale)
- When aligning with [METHOD.md](https://github.com/exchanet/method_pdca-t_coding/blob/main/METHOD.md) Phase 4: aim for **≤ ~50 lines** of production change per task (excluding tests/docstrings); split otherwise
- Prefer **one primary source file per task** (plus that file's support set: types, guards, mocks, tests). Do not cram a second unrelated source file into the same task "for a small tweak."
- Attach interface/type/guard edits to the **first consuming source-file task** — never orphan them as standalone type-only tasks.
- Order tasks producers-before-consumers; keep the tree buildable after each task.
- Author the verification steps yourself (grep/check/validate in the task text). Do not push "determine whether X exists" onto the implementer.
- Prefer path/symbol identifiers over brittle renumbering when tasks may be inserted mid-list.

Format each task as:

```
## Task N: [Title]

**What to build:** [specific description]
**Primary source file:** [exactly one implementation file, or "n/a" for pure docs/config]
**Support files:** [types/guards/mocks/tests belonging to that source file]
**Files likely affected:** [list — should match primary + support]
**Acceptance criteria:** [1-3 specific, verifiable outcomes]
**Dependencies:** [Task N if blocked, or "none"]
**Docs to update:** [bullet list of every doc/diagram/runbook that mentions the surface being changed, with relative paths — or "None — internal change" if truly none]
```

The **Docs to update** line is mandatory. Author it from the `Docs to
Update` ticket-level inventory (see *Docs to Update — mandatory ticket
section* above). A ticket-level entry can map to multiple tasks, but
every task that mutates documented behavior carries the subset that
applies to it.

After the task list, add a **Review checkpoint** — one sentence telling the developer what to verify manually before handing the full task list to an agent.

#### Vertical slices + task sizing

<!-- vertical-slice rules adapted from mattpocock/skills to-tickets (MIT) -->

Slice the work into **tracer bullets**: each slice is a narrow but complete path through every layer it needs (schema, API, UI, tests).

- A finished slice is demoable or verifiable on its own and leaves the system working.
- Each slice fits in one fresh context window.
- Prefactoring comes first: make the change easy, then make the easy change.
- Order slices by real blocking edges only; a slice with no blockers can start immediately.

Example: registration slice (schema + API + UI + test), then login slice, then the next slice.
Inside a slice, order tasks producers-before-consumers (`schema -> models/types -> endpoints -> client -> UI`).

**Wide refactors use expand-contract.**
A wide refactor is one mechanical change (rename a column, retype a shared symbol) whose blast radius breaks many call sites at once, so no vertical slice can land green.
Sequence it in three steps.
Expand: add the new form beside the old so nothing breaks.
Migrate: move call sites in batches sized by blast radius (per package or directory), each batch its own ticket blocked by the expand, with CI green between batches because the old form still exists.
Contract: delete the old form in a ticket blocked by every migrate batch.
When even the batches cannot stay green alone, let them share an integration branch that blocks a final integrate-and-verify ticket; green is promised only there.

**Sizing**

| Size | Files | Use |
|---|---|---|
| XS | 1 | Single function or config tweak |
| S | 1-2 | One endpoint or component |
| M | 3-5 | One vertical slice |
| L | 5-8 | Multi-component — prefer to split |
| XL | 8+ | Too large; break it down |

Split when: >2h of agent work, can't write 3 ACs, touches 2+ unrelated subsystems, or the title contains "and". Insert a **Checkpoint** every 2-3 tasks (tests pass, build clean, end-to-end flow works).
