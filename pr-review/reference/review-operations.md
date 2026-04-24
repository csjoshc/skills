# review-operations

Operational workflow for the `pr-review` skill: pre-flight gates, deterministic
checks, standards gathering, traceability execution, and GitHub posting.

## Contents

- Pre-flight checks
- Diff sizing gate
- Plan-present pre-flight
- Standards gathering
- Deterministic checks
- C3 platform context
- PR summary
- Traceability execution
- Pre-post validation
- Posting review comments
- No-issue path
- Attribution rule

---

## Pre-Flight Checks

Gather PR context first:

```bash
gh pr view <PR> --json title,body,state,isDraft,author,baseRefName,headRefName,comments
gh pr diff <PR>
```

Skip review if:

- PR is closed or merged
- PR is a draft
- PR is trivial (dependency bump, generated update, single typo)
- This skill already commented on the PR

If the PR description is too weak to explain intent, edge cases, and
integration points, request clarification before continuing.

---

## Diff Sizing Gate

If the diff exceeds roughly 400 changed lines, emit a batch-size warning and
recommend splitting the PR before deep review. Large diffs reduce review
quality and increase false negatives.

Use this as a warning gate, not an automatic hard failure unless your org
requires it.

---

## Plan-Present Pre-Flight

Before launching lenses, determine whether a linked plan/PRD artifact
exists. This drives the ledger's `plan_present` field and the
Architectural-Drift lens's behavior.

Look in this order; stop on first match:

1. **PR body** — any link matching `*/PRD.md`, `*.tickets/*`, `*PLAN.md`,
   or text containing `ARCHITECTURE-DECISIONS` / `antiplan`.
2. **Linked tickets** — any linked issue whose body contains an
   `ARCHITECTURE-DECISIONS` fenced block.
3. **Branch artifacts** — `.tickets/PRD.md`, `plans/*.md`, `specs/*.md`
   on the PR's head branch.

```bash
gh pr view <PR> --json body,closingIssues
gh pr view <PR> --json files | jq -r '.files[].path' | rg -i 'prd|plan|ticket'
```

If a plan is found:

- Fetch its `ARCHITECTURE-DECISIONS` block (if present).
- Provide it as context to all lenses — Architectural-Drift lens
  especially.
- Set `plan_present: true` in the ledger.

If no plan is found:

- Set `plan_present: false` in the ledger.
- Cap ledger `confidence` at MEDIUM. The validator rejects `HIGH` with
  `plan_present: false`.
- Add a one-line note to the final summary: *"No plan artifact was
  linked. Architectural-drift findings omitted; rerun with a linked PRD
  for a full architectural review."*
- Architectural-Drift lens emits findings only when it can cite code
  evidence that no plan is needed (e.g., an obviously broken layer
  import); otherwise it skips and logs a dismissal.

---

## Standards Gathering

1. Load `review-standards.md`.
2. Load repo-local standards files at root and under directories containing
   modified files:
   - `CLAUDE.md`
   - `.cursorrules`
   - `AGENTS.md`
   - `copilot-instructions.md`
3. Merge them into one standards context for the standards lens.

Repo-local standards override generic skill guidance.

---

## Deterministic Checks

Run deterministic checks before LLM critique when available:

- Build or typecheck if the repo supports it
- Relevant unit tests for touched areas
- Lint/static checks already present in project scripts
- `layer-boundary-critic` if imports changed
- Any claim-verification artifact if the repo uses one

Do not invent commands the repo does not use. Prefer project-native commands.

---

## C3 Platform Context

If the PR touches C3 backend code, query C3-specific context before review.

Examples:

- `.c3typ` or `.c3doc`
- C3 server-side JavaScript
- `fetch()` or `evalMetric()` calls
- `PerLogger` setup
- `Jasmine` / `TestApi` harness
- Seed or canonicalize scripts
- C3 package metadata

Use C3 context to validate API semantics, filter syntax, type signatures, and
platform-specific conventions. Do not rely on generic knowledge for proprietary
C3 behavior.

---

## PR Summary

Before launching lenses, produce a compact summary:

- What changed and why
- Files modified with add/modify/delete status
- Risk areas: auth, data layer, API surface, UI, config
- Linked tickets or acceptance criteria if available

---

## Traceability Execution

The spec-traceability lens should build a matrix like:

| AC   | Hunk(s)                  | Evidence              | Status      |
| ---- | ------------------------ | --------------------- | ----------- |
| AC-1 | `src/ui/Toast.tsx:42-58` | Screenshot in PR body | MAPPED      |
| AC-2 | —                        | none                  | MISSING     |
| —    | `src/utils/dateFmt.ts`   | no AC reference       | SCOPE CREEP |

Check for:

- Hunks with no AC
- ACs with no hunk
- Layer BLOCK findings
- Unverified claims
- Out-of-scope file edits

---

## Pre-Post Validation

Before any `gh api` call, assemble the review output (findings, ledger,
gate lines) into a single draft file and run:

```bash
python3 ~/.skills/reviews/validate.py --transcript <draft>.md --skill pr-review
```

Exit code `0` is required. If the validator fails:

- `required_blocks_present` — add the missing `REVIEW-FINDINGS` or
  `REVIEW-LEDGER` block.
- `gate_lines_present` — emit the missing `REVIEW-GATE` line.
- `structural_findings_have_proof` — add a `proof:` field (reproducible
  command, failing test, or CI link) or downgrade severity. Triggered
  by any of: `severity: CRITICAL` (any category), `category: Layer`
  with `severity: HIGH` or `CRITICAL`. (`category: Architectural Drift`
  has its own stricter rule in `architectural_drift_has_plan_reference`.)
- `findings_shape` / `ledger_shape` — fix the malformed field.
- `ledger_counts_match_findings` — recompute the ledger counts mechanically
  from the findings block(s).

Only after the validator prints `All checks passed` may the posting step
proceed. Emit:

```
REVIEW-GATE: report → post. Criteria: [validator exit 0: met]. Proceeding: yes.
```

---

## Posting Review Comments

For each validated issue, post an inline PR comment. Every comment ends with:

```markdown
---

_Generated by Claude_
```

Inline comment example:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
  --method POST \
  -f body="[issue description + checklist]

***
*Generated by Claude*" \
  -f commit_id="$(gh pr view <PR> --json headRefOid -q .headRefOid)" \
  -f path="file.py" \
  -F line=42 \
  -f side="RIGHT"
```

Use GitHub suggestion blocks only for small, self-contained fixes. For larger
fixes, describe the remediation without a suggestion block.

After inline comments, post one summary comment.

---

## No-Issue Path

If no validated issues remain, post:

```bash
gh pr comment <PR> --body "## Code Review — No Issues Found

Checked for bugs, standards compliance, error handling, tests, and scope integrity.

***
*Generated by Claude*"
```

---

## Attribution Rule

Every posted comment and summary must end with:

```markdown
---

_Generated by Claude_
```
