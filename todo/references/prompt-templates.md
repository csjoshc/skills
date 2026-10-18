# Prompt Templates

Full template bodies extracted from `SKILL.md` for the 500-line budget.
Fill bracketed slots from detected state; each prompt is stand-alone.

## Contents

- Template: challenge-start (manual path for a new, risky or large feature)
- Template: challenge-resume (Phase 0 or 1 incomplete)
- Template: challenge-audit-resume (dag-done-no-audits)
- Template: audit-fix-resume (challenger-BLOCK or coverage-GAP/INVERTED)
- Template: spec-next (dag-done)
- Template: ticket-review-next (tickets-written-uncriticized)
- Template: spec-fix (critic-failed)
- Template: build-ticket-manual (ready-for-build / partial-build)
- Template: build-ticket-resume (mid-build-resume)
- Template: slice-gate-review (slice-gate-pending)
- Template: handoff (generic cold-start prompt for current stage)

When emitting a prompt for the user to paste into the next session, use
these templates. Fill in the bracketed slots from detected state. Each
prompt is stand-alone — the next session loads it cold with no memory of
this one.

### Template: challenge-start (Manual mode, new Full pipeline)

```
Invoke the /challenge skill for this feature:

**Feature:** <feature description from user>
**Working directory:** <pwd>
**Artifact output dir:** .plan/

Let challenge pick its mode (Fast Mode by default). If it escalates to a
phased mode, write brownfield-context.md, PRD.md and task-sequence.md into
.plan/ and stop after Phase 3. Do not emit fleshed ticket bodies; those are
downstream (spec).
```

### Template: spec-direct (Manual mode, new Lite pipeline)

```
Invoke the spec skill for this defined feature (no challenge PRD):

**Feature:** <feature description from user>
**Working directory:** <pwd>

Write one fleshed ticket per independently testable slice to
.tickets/NNN-slug.md (next free numeric prefix). Each ticket needs YAML
frontmatter with `Stage: NEW`, Scope, >=3 grep-verifiable ACs including
>=1 failure-path AC, an AC->Test table, and a Verify command. Note any
dependency on another ticket in a `Dependencies:` line. Do not write .plan/.
Return ticket paths, unresolved assumptions, and lint result; do not repeat
full ticket contents in chat.
```

### Template: challenge-resume (Phase 0 or 1 incomplete)

```
Resume /challenge. The following artifacts exist and should be treated as
already-approved inputs — do not re-derive them:

- <list of existing files under .plan/ with absolute paths>

Continue from <detected phase>. Do not rewrite approved artifacts unless
the user explicitly asks.
```

### Template: challenge-audit-resume (dag-done-no-audits)

```
Resume /challenge to run the Phase 3 / Phase 3.5 final-pass audits. The
DAG is already written; do NOT regenerate it.

**Existing artifacts (treat as approved input):**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md (if present)

**Task — run only the missing audits:**

1. If .plan/challenger-report.md is missing OR older than task-sequence.md:
   Run the Challenger per references/subagent-prompts.md (subagent suggested).
   Pass it ~/.skills/challenge/rubric.yaml as the AP source of truth.
   Save its full output (per-AP audit table + per-finding entries +
   summary with VERDICT line) to .plan/challenger-report.md.

2. If classification is Standard or Heavy AND .plan/coverage-audit.md is
   missing OR older than PRD.md / task-sequence.md:
   Run the Coverage Auditor per references/coverage-auditor.md (subagent suggested).
   It re-derives R/D/C/I sets from the interrogation transcript and diffs
   them against PRD.md + task-sequence.md. Save its output to
   .plan/coverage-audit.md.
   For Light classification, instead emit a single line at the top of
   coverage-audit.md: `COVERAGE-AUDIT: skipped — Light classification.`

3. Run validate.py against both reports and confirm exit 0 before halt:
   ```
   python3 ~/.skills/challenge/validate.py \
     --project-dir . \
     --tickets .plan/task-sequence.md \
     --prd .plan/PRD.md \
     --challenger-report .plan/challenger-report.md \
     --coverage-report .plan/coverage-audit.md
   ```

4. After both reports exist AND validate.py exits 0, do not proceed to
   spec in this session. Stop and confirm exit status to user.
   If validate.py exits non-zero, surface the specific failure and halt
   without proceeding to spec — the user must direct resolution
   (which becomes a `audit-fix-resume` invocation).
```

### Template: audit-fix-resume (challenger-BLOCK or coverage-GAP/INVERTED)

```
Resume /challenge to address Phase 3 / Phase 3.5 audit failures. The DAG
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

<!-- For each BLOCK in challenger-report.md, the Auto driver
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
   python3 ~/.skills/challenge/validate.py \
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
   the receiving agent attempted. Do not proceed to spec in
   this session.
```

**Template usage notes (for Auto mode):**
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

### Template: spec-next (dag-done)

```
Invoke the /spec skill.

**Inputs:**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md (if exists; brownfield-only)

**Task:** For every stub in task-sequence.md §2, write one fleshed ticket
file to .tickets/NNN-slug.md following ~/.skills/shared/TICKET_CONTRACT.md.
Before finishing, run `python3 ~/.skills/spec/scripts/tickets_lint.py .tickets --dry-red --runner "<project pytest command>"`
and fix every ERROR.

Numbering: use the next-available numeric prefix in .tickets/ (inspect
existing files to find gaps). Slug format: NNN-kebab-case-title.md.

Do not produce a monolithic ticket-pack.md. One file per ticket.
Return created ticket paths, unresolved assumptions, and lint result; do not
repeat the approved PRD or task-sequence in chat.
```

### Template: ticket-review-next (tickets-written-uncriticized)

```
Invoke the /ticket-review skill.

**Inputs:**
- .tickets/*.md (excluding .plan/)
- Contract: ~/.skills/shared/TICKET_CONTRACT.md (the lint enforces the mechanical part)

**Task:** Run the lint, then review design and risk. Emit a report
at .plan/critic-report.md with one line per ticket: `PASS <id>` or
`FAIL <id>: <reasons>`. Do not change ticket files or stages. On any FAIL,
stop the build handoff and route failing tickets to spec for repair.
```

### Template: spec-fix (critic-failed)

```
Invoke /spec in fix mode.

**Inputs:**
- .plan/critic-report.md (list of FAIL tickets and reasons)
- ~/.skills/shared/TICKET_CONTRACT.md
- .plan/PRD.md
- The failing ticket files listed in critic-report.md

**Task:** Rewrite each failing ticket in place to satisfy the contract.
Do not rewrite passing tickets. Do not renumber.
Re-run the lint on the rewritten tickets before finishing.
Return changed ticket paths and lint result; do not repeat ticket contents.
```

### Template: build-ticket-manual (ready-for-build / partial-build)

Per-ticket flow. Single session per ticket using
`/tdd` for red-green-refactor and `/verify` as the evidence gate
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
