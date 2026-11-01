# review-operations

Operational workflow for the `pr-review` skill: pre-flight gates, deterministic
checks, standards gathering, traceability execution, and GitHub posting.

## Contents

- Pre-flight checks
- Local mode
- Diff sizing gate
- Plan-present pre-flight
- Standards gathering
- Deterministic checks
- Platform context
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

Tracked-but-ignored check (`source: tool-flagged`, severity HIGH for any hit).
Planning dirs (`.agent-local/plan/`, `.agent-local/tickets/`, `.agent-local/handoff/`) and gitignored paths
must never appear in a PR diff:

```bash
gh pr view <PR> --json files -q '.files[].path' \
  | rg '^\.(plan|tickets|handoff)/'
gh pr view <PR> --json files -q '.files[].path' \
  | git check-ignore --no-index --stdin
```

For a local diff, feed the changed paths (`git diff --name-only <base>...`)
into the same two commands.

---

## Local Mode

Reviews committed and uncommitted work on the current branch before it is pushed.
No `gh` calls, no posting.

```bash
git fetch -q origin
base=${BASE:-$(git merge-base HEAD "origin/$(git remote show origin | sed -n 's/.*HEAD branch: //p')")}
git log --oneline "$base"..HEAD   # intent, in place of a PR body
git diff "$base"                  # committed + staged + unstaged
git ls-files --others --exclude-standard   # untracked files are part of the change
```

- Commit messages stand in for the PR body. If they don't explain intent, ask before reviewing.
- The PR skip rules (closed, draft, already commented) don't apply.
- Run the tracked-but-ignored check on `git diff --name-only "$base"` plus the untracked list.
- Plan lookup uses only the local plan step.

Quiet reporting: write the assembled transcript (findings, gates, ledger) to
`.agent-local/reviews/<slug>.md`, validate it there
(`python3 ~/.skills/reviews/validate.py --transcript <file> --skill pr-review --local --repo <root>`),
and keep chat lean: the findings with evidence, the FIX/COMMENT disposition,
test or gate results, and the one-line validator boolean. Chat never reprints
the fenced blocks; the transcript is the artifact, and it is what a later
posting step would validate again.

Independent re-check before disposition: when the harness can spawn a
subagent with a different chat model (or at minimum a fresh context and no
access to this transcript), hand it only the diff and the `REVIEW-FINDINGS`
blocks and ask it to re-derive each lens checklist verdict and verify every
proof target itself. It returns one line per finding: `CONFIRM` or
`OVERRULE <one-line reason>`. An `OVERRULE` finding drops to `DISMISSED`
with the reason recorded, unless new evidence is produced for it. What the
subagent gets must not include this session's conclusions; its job is to be
the unanchored second opinion that `validate.py` cannot be - the validator
checks shape, the re-check checks substance. Skip it only when the harness
has no subagent mechanism, and record `recheck: skipped` per finding; a
skipped re-check caps ledger confidence at MEDIUM.
- Validate with `--local`, end at `REVIEW-GATE: phase-1 → report`, and print findings in chat.
- If the user then opens a PR, rerun in PR mode rather than posting the local transcript.

---

## Diff Sizing Gate

Apply the review-budget and diff-coverage guidance in the [change-quality pass](../../shared/QUALITY_RUBRIC.md#change-quality-pass) before deep review.
This also applies to standalone local reviews; reuse a current preflight from `pr-create` instead of repeating it.

---

## Plan-Present Pre-Flight

Before launching lenses, determine whether a linked plan/PRD artifact
exists. This drives the ledger's `plan_present` field and the
Architectural-Drift lens's behavior.

Look in this order; stop on first match:

1. **PR body** — any link matching `*/PRD.md`, `*.agent-local/tickets/*`, `*PLAN.md`,
   or text containing `ARCHITECTURE-DECISIONS` / `challenge`.
2. **Linked tickets** — any linked issue whose body contains an
   `ARCHITECTURE-DECISIONS` fenced block.
3. **Local plan** — `.agent-local/tickets/PRD.md`, `.agent-local/plan/**/PRD.md` or
   `.agent-local/plan/**/task-sequence.md` in the reviewer's local checkout. Planning
   dirs are never committed, so do not look for them on the PR branch; a
   planning file in the PR diff is itself a finding (see pre-flight).

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

## Platform Context

If the PR touches platform-specific code (custom type systems,
platform-specific server APIs, in-house test harnesses), load the matching
platform-context skill or MCP server if one is installed (e.g. a
`<platform>-pr-context` skill) before review. Use it to validate API
semantics, type signatures, and platform conventions. Do not rely on generic
knowledge for platform behavior.

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

Before any `gh api` call, run the independent re-check (Local Mode section)
on the findings that survived validation, then assemble the review output
(findings, ledger, gate lines) into a single draft file and run:

```bash
python3 ~/.skills/reviews/validate.py --transcript <draft>.md --skill pr-review --repo <repo-root>
```

Local mode adds `--local`, which drops the `report → post` gate requirement.

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

For each validated issue, post an inline PR comment, with no agent or model signature.

Inline comment example:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
  --method POST \
  -f body="[issue description + checklist]" \
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

Checked for bugs, standards compliance, error handling, tests, and scope integrity."
```

---

## Attribution Rule

Posted comments and summaries carry no agent or model signature or footer.
