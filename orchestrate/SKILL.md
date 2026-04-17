---
name: orchestrate
description: >-
  Defines the state machine, stage transitions, and routing rules for the headless 
  agent orchestration framework. Use when interpreting ticket stages, applying
  transition rules, running tickets via the CLI, or updating stage metadata
  through the orchestration pipeline.
---

# Agent Orchestration Protocol

Orchestra is a headless, file-driven agent orchestration framework built on LangGraph.
Agents do not pass context through chat history; they communicate entirely through
file state on disk (ticket frontmatter, handoff files, worktrees).

As an agent in this system, your primary administrative duty is to transition tickets
between stages based on the outcome of your work.

## Directory Layout

```
<target-project>/
  .tickets/                          # Ticket markdown files
  .orchestra/
    handoff/<slug>.md                # Per-ticket handoff/build logs
    worktrees/<slug>/                # Isolated git worktrees per ticket
    logs/                            # Runtime logs
    orchestra.db                     # SQLite state database
  .reports/                          # Run reports (run-YYYY-MM-DD.md)
```

## The State Machine

Every ticket markdown file must contain a **YAML frontmatter** block. This is the
only stable interface for tracking state.

```yaml
---
Title: Implement user login
Slug: implement_user_login
Order: 01
Stage: BUILD
DependsOn: []
---
```

### Stages

Primary flow (sequential mode):

1. **`NEW`** → Initial state. Routed to spec node.
2. **`SPEC`** → Planner writes spec/plan sections. (`PLAN` is a legacy alias.)
3. **`BUILD`** → Builder agent implements the ticket in an isolated worktree.
4. **`REVIEW`** → Reviewer agent audits the implementation.
5. **`COMPLETE`** → Fully implemented, gates passed, audited. Terminal state.

Exception/internal stages:

- **`SPEC_SPLIT`** → Ticket exceeds token threshold (~2200 tokens); auto-split into child tickets.
- **`BLOCKED`** → Work cannot proceed. Requires human or architect intervention.
- **`FAILED`** → Terminal failure after exhausting retries. Requires human intervention.
- **`REVISION_ROUTER`** → Routes review feedback to affected facets for rework.

### Execution Modes

- **`single`** — entry → build → unified_gate → complete (skips spec and review)
- **`sequential`** — entry → spec → spec_gate → build → unified_gate → review → unified_gate → complete

### Deterministic Gates

Gates are pure-Python checks that run after spec and build/review, **not** LLM calls:

- **spec_gate** — file count limits, god-file detection, acceptance criteria, dependency approval, DAG cycles
- **unified_gate** — plan drift, god-file limits, secrets scan, AST violations, complexity, test pass + coverage, working tree cleanliness, commit hygiene, mutation testing, regression tests

Gate failure routes the ticket back to its source stage for rework (build → build, review → review).

### Circuit Breakers

- `MAX_ATTEMPTS = 3` per stage
- `MAX_TOTAL_ATTEMPTS = 10` across all stages
- `MAX_BLOCKED_ATTEMPTS = 2`

Exceeding any limit routes to `FAILED`.

## How to Transition State

When you finish your assigned task, update the frontmatter `Stage:` field.

**Rule:** Never leave a ticket in the stage you found it in unless your execution
timed out or was interrupted.

## Assertion-Driven Intake (optional)

If the target project has a `ticket_graph.json` at its root, the file is
**optional but strict-when-present**: schema or reference errors abort the run
with a deterministic message. Projects without the file keep baseline scheduler
behavior.

Downstream tickets may depend on a validated assertion by declaring it in
frontmatter:

```yaml
---
Stage: NEW
Type: feature
Depends-On: [02-ig1-graph-contract-tracer-bullet]
Requires-Assertions: [A2]
---
```

`unified_gate` blocks tickets whose required assertions are not `validated`.
Validator tickets use `Type: integration-gate` and prove one or more
assertions (`A1-A6` in this repo — see `.tickets/202, 206, 209, 213, 216, 218`).
Their `COMPLETE` transition flips the assertion to `validated` and releases
downstream fanout.

## Merge Queue and End-Of-Run Promotion

When `ORCHESTRA_MERGE_QUEUE=1` (default ON), completed tickets land serially on
a dedicated run branch `orch/<run-id>`; the source branch is advanced once at
end-of-run. States: `PENDING / LANDING / LANDED / PAUSED / FAILED`.

- Conflicts pause the queue and write
  `.orchestra/merge_conflicts/<run_id>/<slug>.json`. Resume with
  `orch merge-resume --project <path> --run-id <run-id>`.
- End-of-run promotion is automatic for full `orch run`; on demand use
  `orch promote-run --project <path> [--run-id <id>] [--delete-run-branch]`.
  Idempotent; aborts safely if the queue is not drained.
- See `docs/MERGE_QUEUE.md` for the troubleshooting playbook.

## Ticket Splitting

If a ticket body exceeds the token threshold (~2200 tokens) or requires modifying
many files across distinct concerns, Orchestra auto-routes to `SPEC_SPLIT`.

The spec_split agent creates child tickets (e.g., `01a-sub-task.md`, `01b-sub-task.md`)
with `Stage: NEW` and marks the parent `Stage: COMPLETE`.

## Running Orchestra (CLI)

The `orch` CLI lives in the Orchestra repo. Call the binary directly:

```bash
/Users/joshc/Projects/orchestra/.venv/bin/orch <command> [options]
```

### Kick off a single ticket build

```bash
/Users/joshc/Projects/orchestra/.venv/bin/orch run \
  --project /path/to/target-project \
  --ticket /path/to/target-project/.tickets/<slug>.md \
  --runtime-profile work \
  --mode sequential \
  --concurrency 1 \
  --model gemma4:26b
```

**Key flags:**
- `--project` — absolute path to the target project (not the orchestra repo)
- `--ticket` — absolute path to a single ticket file to run
- `--mode single` — build only (no review pass); `--mode sequential` — build then review
- `--model` — model name; common values: `gemma4:26b`, `auto`, or any model from `profiles.yaml`
- `--runtime-profile` — named profile from `profiles.yaml` (e.g. `work`, `mixed`, `cost_saver`)

### Reset a ticket for a fresh run

Before re-running a ticket, clean up all stale state:

```bash
cd /path/to/target-project

# 1. Reset the ticket stage to BUILD
sed -i '' 's/^Stage: .*/Stage: BUILD/' .tickets/<slug>.md

# 2. Remove stale handoff (carries rework context from previous attempts)
rm -f .orchestra/handoff/<slug>.md

# 3. Remove stale worktree and branch (if they exist)
git worktree remove --force .orchestra/worktrees/<slug> 2>/dev/null
git worktree prune
git branch -D ticket/<slug> 2>/dev/null
```

All three steps matter. If you skip the handoff removal, the agent gets injected with
error context from a prior failed run. If you skip the branch deletion, a foreign branch
with unrelated commits can pollute validation (Orchestra auto-detects this, but cleaning
up is faster).

### Process lifetime

Orchestra runs are long-lived (5–30+ minutes per ticket depending on model speed and
rework loops). **Wait at least 30 minutes before attempting to capture output or kill
the process.** The shell tool's background capture will kill the process prematurely —
for monitored runs, prefer checking progress via:

```bash
# Check if the process is still alive
pgrep -f "orch run"

# Check the ticket's current stage
head -6 /path/to/target-project/.tickets/<slug>.md

# Check the latest run report
cat /path/to/target-project/.reports/run-$(date +%Y-%m-%d).md
```

If you need to launch from a shell tool and monitor, use `block_until_ms` of at least
1800000 (30 minutes). Shorter timeouts will background and eventually orphan the process.

## Inter-Agent Communication

- **Do NOT** leave messages for other agents in the ticket body unless documenting a bug/blocker.
- **Do NOT** wrap your file outputs in triple backticks (```). You are writing raw files to disk, not printing code blocks to a UI.
- Handoff context lives in `.orchestra/handoff/<slug>.md` (not `.handoff/`).
- Technical context, ordered steps, and absolute file paths go in the handoff file.
