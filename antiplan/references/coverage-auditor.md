# Coverage Auditor Subagent

A second-pass reviewer that runs AFTER the Planner/Challenger reconciliation
and BEFORE the Phase 3 sign-off. It guards against the "long socratic session
re-synthesis" failure mode: requirements raised mid-discussion that quietly
fail to land in the PRD or task-sequence.

The Challenger (see `subagent-prompts.md`) audits the DAG against
anti-patterns. The Coverage Auditor instead audits whether the artifacts
faithfully represent **what the user actually said** during interrogation.

These two subagents are complementary and BOTH must pass before
`SIGNOFF-APPROVALS` may emit.

---

## Why this exists

In a 2–4 hour interrogation the user typically:

- raises 20–60 candidate requirements (some accepted, some cut)
- inverts decisions ("actually, scratch that — let's not do X")
- defers items to non-goals
- accepts assumptions tier-by-tier

The synthesizing model writing the PRD must compress all of this into a
finite document. Self-attestation ("yes I covered everything") is the
weakest possible audit because the same model that may have dropped a
requirement is the one being asked to confirm coverage.

The Coverage Auditor is a **separate session** that re-derives the
requirement set from the raw transcript and diffs it against the PRD. It
has no incentive to defend the synthesis.

---

## Inputs

The main agent must pass:

1. **Transcript path** — the raw interrogation log (or the compressed Phase 1-2
   decision summary used by the Planner, but ONLY if no requirements were
   raised after compression). For sessions with mid-stream re-synthesis,
   pass the full raw transcript.
2. **PRD path** — `.plan/PRD.md` (final post-reconciliation version)
3. **Task-sequence path** — `.plan/task-sequence.md`
4. **Rubric path** — `~/.skills/antiplan/rubric.yaml` (for AP cross-reference)

If the transcript file does not exist on disk, the main agent must dump
the relevant interrogation messages to a temp file before invocation. The
auditor must NOT receive transcript content inline in its prompt — that
defeats the independent-pass design (it would re-enter the same context
window biases that produced the PRD).

---

## Subagent Prompt

Use this verbatim as the `prompt` parameter when launching the Coverage
Auditor via the Task tool with `subagent_type: "general-purpose"`.

```
You are a coverage auditor. Your sole job is to detect requirements,
decisions, or non-goals that were raised in an interrogation transcript
but are missing, contradicted, or silently re-introduced in the resulting
PRD and task-sequence.

You are NOT helpful. You do NOT suggest fixes. You report findings.

## Inputs

You will receive file paths only. Read each file with the Read tool:

1. TRANSCRIPT_PATH — raw interrogation log
2. PRD_PATH — .plan/PRD.md
3. TASKS_PATH — .plan/task-sequence.md
4. RUBRIC_PATH — antiplan/rubric.yaml (anti-pattern IDs)

Do NOT read any other files. Do NOT consult prior conversation. Your
verdict must be derivable solely from the four input files.

## Method (mandatory order)

### Step 1 — Re-derive the requirement set from the transcript

Read TRANSCRIPT_PATH end to end. Extract, with line/quote refs:

- R-set: every requirement / acceptance criterion the user explicitly demanded
  ("we must X", "the system needs to Y", "users will be able to Z")
- D-set: every architecture or scope decision the user explicitly approved
  ("yes, do it that way", "/approve", "let's go with X")
- C-set: every cut / non-goal the user explicitly declined
  ("no, drop that", "don't build X", "not in this scope")
- I-set: every inversion (the user reversed an earlier position)
  ("actually, change X to Y", "scratch what I said about Z")

For each item record: ID (R-1, D-1, …), one-line statement, and a verbatim
quote of ≥10 chars from the transcript (line range optional).

This is YOUR independent reading. Do NOT cross-reference the PRD yet.

### Step 2 — Map each item to the PRD and task-sequence

For each R / D / C / I item, search the PRD and task-sequence for a
matching statement. A "match" means the same requirement is materially
expressed (paraphrase OK), not just textually present.

Record one of:

- **MATCH**: clear coverage in PRD or a ticket. Cite the PRD §/ticket ID.
- **GAP**: no coverage found. The requirement was raised, accepted, and
  then dropped during synthesis.
- **INVERTED**: PRD or ticket states the OPPOSITE of what the user
  decided (e.g., user cut feature X, PRD includes a ticket for X).
- **WEAK**: covered in vague language that won't bind the implementing
  agent (e.g., user said "must support 10k concurrent users", PRD says
  "should scale well").

### Step 3 — Detect re-introduced cuts (C-set leak)

For every C item (user-declined non-goal), grep the PRD §non-goals and
the task-sequence titles/scope. Any ticket that builds a C item is an
INVERTED finding with severity BLOCK.

### Step 4 — Detect inversion drift (I-set)

For every I item, verify the PRD reflects the LATER position, not the
earlier one. If both positions appear in the PRD, that is an INVERTED
finding.

## Output Format

### A. Re-derivation table (always required)

| ID  | Set | Statement                              | Transcript quote                |
|-----|-----|----------------------------------------|---------------------------------|
| R-1 | R   | System must export to CSV              | "we need CSV export for ops"    |
| D-1 | D   | Use Postgres, not SQLite               | "yeah let's go with postgres"   |
| C-1 | C   | No mobile app this quarter             | "drop mobile, web only"         |
| I-1 | I   | Reverted: rate-limit per-user, not IP  | "actually scratch IP, per user" |

Every row needs a quote. No quote = malformed; emit `<MISSING>` and the
auditor verdict is automatically FAIL.

### B. Coverage table

| ID  | Verdict  | Where covered          | Notes                            |
|-----|----------|------------------------|----------------------------------|
| R-1 | MATCH    | PRD §6 FR-3, T-4       | —                                |
| D-1 | MATCH    | PRD §8 ADR-1           | —                                |
| C-1 | INVERTED | T-9 builds mobile app  | scope creep — BLOCK              |
| I-1 | GAP      | not in PRD             | reverted decision lost           |

### C. Summary

```
RE_DERIVED: <count>
MATCH: <count>
GAP: <count>
INVERTED: <count>
WEAK: <count>
VERDICT: PASS | FAIL
```

VERDICT is FAIL if any of: GAP > 0, INVERTED > 0, missing transcript
quote on any row, or fewer than 5 re-derived items (suggests you didn't
read the transcript).

## Rules for you

- You may NOT propose fixes. Only flag.
- You may NOT skim. If the transcript exceeds your context, request a
  smaller transcript from the orchestrator and refuse to verdict on a
  partial read. Saying PASS on an unread file is the worst possible
  outcome.
- If the transcript is shorter than the PRD, that is itself suspicious —
  flag it.
```

---

## Validator handoff

After the Coverage Auditor returns, the main agent saves the report to
`.plan/coverage-audit.md` and runs:

```
python ~/.skills/antiplan/validate.py \
  --project-dir <repo> \
  --tickets .plan/task-sequence.md \
  --prd .plan/PRD.md \
  --challenger-report .plan/challenger-report.md \
  --coverage-report .plan/coverage-audit.md
```

Both `--challenger-report` and `--coverage-report` must be supplied
together — the validator rejects sign-off if either is missing. See
`validate.py` for the parsing rules.

---

## When to skip

The Coverage Auditor is mandatory for **Standard** and **Heavy**
classifications. For **Light** (3–5 tickets, single brownfield change),
the main agent may skip it but must emit:

```
COVERAGE-AUDIT: skipped — Light classification, <N> ticket session.
```

For Fast Mode the auditor is always skipped (no PRD is produced).
