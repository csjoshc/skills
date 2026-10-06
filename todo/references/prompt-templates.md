# Prompt Templates

Full template bodies extracted from `SKILL.md` for the 500-line budget.
Fill bracketed slots from detected state; each prompt is stand-alone.

When emitting a prompt for the user to paste into the next session, use
these templates. Fill in the bracketed slots from detected state. Each
prompt is stand-alone — the next session loads it cold with no memory of
this one.

### Template: antiplan-start (for `/todo start <feature>`)

```
Invoke the /antiplan skill for this feature:

**Feature:** <feature description from user>
**Working directory:** <pwd>
**Artifact output dir:** .plan/

Follow antiplan's phases end to end. Write brownfield-context.md, PRD.md,
and task-sequence.md into .plan/. Do not emit fleshed ticket bodies —
those are downstream (spec-writer). Stop at the end of antiplan's Phase 3
after writing task-sequence.md.
```

### Template: antiplan-resume (Phase 0 or 1 incomplete)

```
Resume /antiplan. The following artifacts exist and should be treated as
already-approved inputs — do not re-derive them:

- <list of existing files under .plan/ with absolute paths>

Continue from <detected phase>. Do not rewrite approved artifacts unless
the user explicitly asks.
```

### Template: antiplan-audit-resume (dag-done-no-audits)

```
Resume /antiplan to run the Phase 3 / Phase 3.5 final-pass audits. The
DAG is already written; do NOT regenerate it.

**Existing artifacts (treat as approved input):**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md (if present)

**Task — run only the missing audits:**

1. If .plan/challenger-report.md is missing OR older than task-sequence.md:
   Launch the Challenger subagent per references/subagent-prompts.md.
   Pass it ~/.skills/antiplan/rubric.yaml as the AP source of truth.
   Save its full output (per-AP audit table + per-finding entries +
   summary with VERDICT line) to .plan/challenger-report.md.

2. If classification is Standard or Heavy AND .plan/coverage-audit.md is
   missing OR older than PRD.md / task-sequence.md:
   Launch the Coverage Auditor subagent per references/coverage-auditor.md.
   It re-derives R/D/C/I sets from the interrogation transcript and diffs
   them against PRD.md + task-sequence.md. Save its output to
   .plan/coverage-audit.md.
   For Light classification, instead emit a single line at the top of
   coverage-audit.md: `COVERAGE-AUDIT: skipped — Light classification.`

3. Run validate.py against both reports and confirm exit 0 before halt:
   ```
   python ~/.skills/antiplan/validate.py \
     --project-dir . \
     --tickets .plan/task-sequence.md \
     --prd .plan/PRD.md \
     --challenger-report .plan/challenger-report.md \
     --coverage-report .plan/coverage-audit.md
   ```

4. After both reports exist AND validate.py exits 0, do not proceed to
   spec-writer in this session. Stop and confirm exit status to user.
   If validate.py exits non-zero, surface the specific failure and halt
   without proceeding to spec-writer — the user must direct resolution
   (which becomes a `audit-fix-resume` invocation).
```

### Template: audit-fix-resume (challenger-BLOCK or coverage-GAP/INVERTED)

```
Resume /antiplan to address Phase 3 / Phase 3.5 audit failures. The DAG
is the starting point — modify it only to resolve the findings below.

**Existing artifacts (approved input — do not rewrite unless resolving
a finding):**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md
- .plan/challenger-report.md
- .plan/coverage-audit.md

**Findings to resolve** (each section quotes the upstream report
verbatim — do NOT re-derive; the receiving agent must address the named
finding, not its own re-interpretation):

<!-- For each BLOCK in challenger-report.md, the parent /todo run
auto-driver pastes a section here using this template: -->

### Challenger BLOCK <AP-ID> (<ticket-IDs>): <one-line summary>

**Quoted finding** (verbatim from challenger-report.md):
> <quoted finding text — at least the rubric's detection-signal line
> and the per-finding entry block>

**Quoted upstream context** (PRD / task-sequence excerpts the receiving
agent needs to read; inline so no re-fetch is required):
- PRD §<N>: > <quoted text>
- task-sequence T<N>: > <quoted text>

**Required resolution — pick exactly one and apply it. Weak options
intentionally absent:**
- (a) <Behavioral fix that changes runtime evidence — preferred>
- (b) <Alternative behavioral fix>

**NOT acceptable as a fix:**
- Adding a comment / note / docstring that asserts the invariant
  without changing runtime behavior (the build driver reads exit
  codes, not prose)
- Justifying that an existing gate is "sufficient" if the Challenger
  already flagged it as skip-prone — that loops the AP-N signal back
  in
- Deferring the fix to a downstream gate that is itself skip-prone

**For AP-26 specifically (Operator Entry Point Not Smoke-Tested),
every resolution must include at least one mandatory-not-skippable
live call in the gate.** A skip-guarded chat assertion + SQL + health
is NOT sufficient if exit 0 is reachable when the live call skips.

---

<!-- For each Coverage finding (INVERTED / GAP), the parent pastes
a section using this template: -->

### Coverage <VERDICT>-<N> (<requirement-id>): <one-line summary>

**Quoted finding** (verbatim from coverage-audit.md):
> <quoted finding text including the re-derived requirement, the
> PRD's claim, and the verdict line>

**Quoted upstream context** (constitution / PRD section quoted so
receiving agent doesn't re-fetch):
- Constitution §<N>: > <quoted text>
- PRD §<N>: > <quoted text>
- transcript: > <quoted decision text>

**Required resolution:**
- For INVERTED: PRD section <N> must <add | remove | rephrase> the
  named requirement to match transcript intent. The receiving agent
  commits to ONE side (in scope OR not in scope) — opposite options
  are not offered because the live DAG already chose a side.
- For GAP: add an AC to T<N> requiring <observable behavioral
  assertion>. **The AC must be machine-verifiable** — no "looks
  yellow", no "visually inspect", no "screenshot shows X". Examples
  of acceptable AC shapes:
  - `grep -q '<expected-string>' <output-file>`
  - `curl -fsS http://localhost:<port>/<route> | jq -e '<predicate>'`
  - HTML DOM contains role + text: `grep -oE 'role="status"[^>]*>[^<]*Local:[^<]*' index.html`
  - `pytest tests/test_<name>.py::test_<func>` exits 0 with N >= 1 test
    actually executed (not collected)

---

**After applying all resolutions:**

1. Re-run the Challenger subagent against the updated DAG; overwrite
   .plan/challenger-report.md with the new output.
2. Re-run the Coverage Auditor subagent against the updated PRD +
   task-sequence; overwrite .plan/coverage-audit.md.
3. Run staleness re-check: if PRD.md mtime > task-sequence.md mtime,
   the task-sequence may need a revision pass. Surface this; do NOT
   silently proceed.
4. Run validate.py against the new reports:
   ```
   python ~/.skills/antiplan/validate.py \
     --project-dir . \
     --tickets .plan/task-sequence.md \
     --prd .plan/PRD.md \
     --challenger-report .plan/challenger-report.md \
     --coverage-report .plan/coverage-audit.md
   ```
5. **Halt condition (mandatory all-of):**
   - validate.py exit 0
   - challenger-report VERDICT: PASS (or all BLOCKs that remain are
     explicitly justified WARNs)
   - coverage-audit verdict shows 0 GAP, 0 INVERTED
   - staleness re-check clean (or surfaced and the user has accepted)

   Only when all four conditions hold may the receiving agent stop
   with "audit-fix complete." If any condition fails, halt with a
   structured report naming exactly which condition failed and what
   the receiving agent attempted. Do not proceed to spec-writer in
   this session.
```

**Template usage notes (for `/todo run` driver):**
- The auto-driver pastes one `### Challenger BLOCK …` section per BLOCK
  found in challenger-report.md, and one `### Coverage <V>-<N> …`
  section per INVERTED/GAP in coverage-audit.md.
- The driver inlines the verbatim quotes from the report — never
  paraphrases. If a quote is missing, the driver halts and asks the
  user to provide the source text rather than make it up.
- The driver computes "Required resolution" options from the
  rubric.yaml detection signals + the AP's anti-patterns.md prose
  prevention section — not from imagination.
- Weak options ("accept and justify", "note in the spec", "defer to
  downstream gate") are filtered out before paste. If only weak
  options exist, the driver halts and asks the user whether to accept
  partial resolution.

### Template: spec-writer-next (dag-done)

```
Invoke the /spec-writer skill.

**Inputs:**
- .plan/PRD.md
- .plan/task-sequence.md (the Ticket Contract is in §3)
- .plan/brownfield-context.md (if exists; brownfield-only)

**Task:** For every stub in task-sequence.md §2, write one fleshed ticket
file to .tickets/NNN-slug.md. Each file must satisfy the Ticket Contract
(task-sequence.md §3) — YAML frontmatter with the required fields, Scope,
User Story, ≥3 grep-verifiable ACs including ≥1 failure-path AC, Verify
command, Technical Notes, Failure Protocol. Integration gates additionally
include Silent Failure Detection, Dev Agent Record, Proof Artifacts.

Numbering: use the next-available numeric prefix in .tickets/ (inspect
existing files to find gaps). Slug format: NNN-kebab-case-title.md.

Do not produce a monolithic ticket-pack.md. One file per ticket.
```

### Template: ticket-critic-next (tickets-written-uncriticized)

```
Invoke the /ticket-critic skill.

**Inputs:**
- .tickets/*.md (excluding .plan/)
- Ticket Contract: .plan/task-sequence.md §3

**Task:** Validate every ticket against the Ticket Contract. Emit a report
at .plan/critic-report.md with one line per ticket: `PASS <id>` or
`FAIL <id>: <reasons>`. Block Stage: BUILD on any FAIL until remediated.
```

### Template: spec-writer-fix (critic-failed)

```
Invoke /spec-writer in fix mode.

**Inputs:**
- .plan/critic-report.md (list of FAIL tickets and reasons)
- .plan/task-sequence.md §3 (Ticket Contract)
- .plan/PRD.md
- The failing ticket files listed in critic-report.md

**Task:** Rewrite each failing ticket in place to satisfy the contract.
Do not rewrite passing tickets. Do not renumber.
```

### Template: build-ticket-manual (ready-for-build / partial-build)

Per-ticket flow. Single session per ticket using
`/tdd` for red-green-refactor and `/verify-claim` as the evidence gate
before commit. Subagents are reserved for slice gates, not per-ticket.

Full template body: see `references/execution-templates.md` §
build-ticket-manual. When emitting the prompt to the user, inline the
full body from that file with the slot fields filled in.

### Template: build-ticket-resume (mid-build-resume)

Resumes a ticket whose `Stage: BUILD` was set in a prior session that
ended without reaching COMPLETE.

Full template body: see `references/execution-templates.md` §
build-ticket-resume.

### Template: slice-gate-review (slice-gate-pending)

Closes a slice when every non-gate ticket is COMPLETE and the gate
ticket is NEW. Three-pass flow: artifact collection → independent
subagent review → disposition.

Full template body: see `references/execution-templates.md` §
slice-gate-review.

### Template: handoff (generic cold-start prompt for current stage)

```
I am resuming a pipeline-based planning/implementation effort. The
artifacts on disk are the source of truth; do not ask me what was decided.

**Working directory:** <pwd>
**Current stage:** <detected stage>
**Key artifacts:**
- <bullet list of existing artifacts with absolute paths>

**Immediate next step:** <one-sentence description>

The next-step prompt to run is:

<paste the matching next-stage template from above, pre-filled>

Do not continue prior chat conversations. Start from those artifacts.
```
