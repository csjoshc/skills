---
name: pr-review
description: "Reviews a pull request or an unpushed local branch with specialist lenses (bugs, standards, errors, tests, scope), applies auto-fixable findings to the working tree, and leaves comments only for open questions. Use when reviewing a PR, posting review comments, or reviewing local changes before pushing."
---

# pr-review

Reviews pull requests, or local changes before they are pushed, with
specialist review lenses and criteria-based checklists. Every reported issue
must pass an explicit binary checklist.

PR mode posts GitHub review comments. Local mode reviews the branch diff plus
uncommitted work and reports in chat; nothing leaves the machine. For codebase
audits not tied to a change, use `cleanup`.

## Contents

- When to use
- Invocation
- Workflow summary
- Output contracts
- Mandatory companions
- Fix-first disposition
- Scope boundary
- Output rules

---

## When to Use

- Reviewing an open pull request
- Reviewing your own branch or working tree before pushing (local mode)
- Preparing code review feedback before posting
- Auditing a PR diff for bugs, standards, tests, error handling, or scope drift
- Posting inline PR comments and a summary review

Do not use for:

- Full codebase audits unrelated to a PR → use `cleanup`
- Editing ticket/spec markdown → use `ticket-review`

---

## Invocation

```bash
/pr-review <owner/repo> <pr-number>
```

If already on the PR branch, detect repo and PR automatically via `gh pr view`.

```bash
/pr-review --local [<base>]
```

Local mode: no PR, no posting. Use it when the user asks to review before
pushing, or when the current branch has no PR. Base defaults to the merge-base
with the remote default branch. Context commands are in
`reference/review-operations.md` → Local mode.

### Side-by-side diff

Review in the current session by default.
Open a diff pane only when the user explicitly requests one:

```bash
~/.skills/shared/scripts/side-diff.sh <base>...<head>
```

For a PR that isn't checked out, run `git fetch origin <base> pull/<N>/head` and pass `origin/<base>...FETCH_HEAD`.
It picks WezTerm, tmux or iTerm2 from the environment, falls back to a new Terminal.app window on macOS, and uses difftastic when installed.
Done when it prints `side-pane: <where>`; on exit 1, give the user the printed command.

---

## Workflow Summary

1. Run pre-flight checks and fetch the PR context (local mode: the git diff).
2. Gather standards from `reference/review-standards.md` and repo-local policy files.
3. Run deterministic checks before LLM critique when available.
4. Launch specialist review lenses from `reference/review-lenses.md`.
5. Validate, deduplicate, and sort findings into `REVIEW-FINDINGS` blocks.
6. Independent re-check: a harness subagent with a different chat model (at
   minimum fresh context with no view of this transcript) re-derives each
   verdict and verifies proof targets; `OVERRULE` findings drop to
   `DISMISSED` with the reason, a skipped re-check caps confidence at MEDIUM
   (workflow in `reference/review-operations.md`).
7. Emit `REVIEW-LEDGER` and `REVIEW-GATE: report → post` (local mode: stop
   at `phase-1 → report`).
8. Run `python3 ~/.skills/reviews/validate.py --transcript <draft> --repo <root>`
   (add `--local` in local mode); exit 0 required before posting or reporting.
   The transcript file carries the fenced blocks; local-mode chat stays lean.
9. Disposition (see Fix-first disposition): apply auto-fixable findings to
   the working tree; carry only open questions forward as comments.
10. PR mode: post the remaining open-question comments and a summary using
   `reference/review-operations.md`. Local mode: print open questions in chat
   as `file:line` with the suggested fix, and post nothing.

Do not expand the full lens definitions or posting templates here. Load the
companions below.

---

## Output Contracts

Every `/pr-review` session emits, in order:

1. One or more `REVIEW-FINDINGS` fenced blocks (schema in
   [`~/.skills/reviews/schemas.md`](../reviews/schemas.md)).
2. `REVIEW-GATE: phase-1 → report. Criteria: [...]. Proceeding: yes.`
3. `REVIEW-LEDGER` YAML summarizing counts and confidence.
4. `REVIEW-GATE: report → post. Criteria: [validator exit 0: met]. Proceeding: yes.`
   Local mode omits this gate.

These blocks are the machine contract: they belong in the validated transcript
file, not in chat prose. In local mode the chat report stays lean - findings
with evidence, disposition, and the validator boolean; the transcript
(`.agent-local/reviews/<slug>.md`) carries the blocks. The blocks reappear
readable only when something posts.

Validate before reporting: run `python3 ~/.skills/reviews/validate.py --transcript <draft>`
(add `--local` in local mode); exit 0 required before posting or reporting.

Transcript-carrying rules (unchanged): every finding carries `source`
(`tool-flagged` for pre-flight results) and `checklist_score: N/M`; structural
findings require a `proof:` field - a path in the reviewed repo, a failing
test, or a CI link, verified for on-disk existence by the validator when
`--repo` is passed. The proof rule fires on `severity: CRITICAL` (any
category), `category: Architectural Drift`, or `category: Layer` at
`HIGH`/`CRITICAL`. `category` is exactly one of Bug | Error Handling |
Standards | Test Gap | Scope | Layer | Redundancy | Modularity |
Architectural Drift. `line` is the new-file line number, not the diff-text
position.

Fixed phase sequence is documented in
[`~/.skills/reviews/runbook.md`](../reviews/runbook.md).

---

## Review Lenses (supplemental)

Use alongside the specialist lenses in `reference/review-lenses.md`. Apply only when relevant to the diff.

Operate as `Mode: Reviewer`: hunt **EO&D** (errors, omissions, discrepancies) from the diff and on-disk artifacts — not from author narrative or checkbox status. Same vocabulary as `shared/EVIDENCE_REVIEWER.md`.

<!-- pattern: common-rationalizations -->
### Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The diff is small, low risk" | Small diffs hide load-bearing assumptions. Read what surrounds the change. |
| "Author said it was tested" | Verify the test exists and exercises the new path. Trust but check. |
| "Style is fine, ship it" | Convention drift compounds. Flag it now or refactor later. |
| "Performance is premature optimization" | If the diff adds an N+1 or sync I/O on a hot path, flag it. |

<!-- pattern: trusted-untrusted-boundary -->
### Trusted vs untrusted boundaries (security lens)

When reviewing diffs that handle external input (HTTP body, query strings, file uploads, third-party API responses, log lines), check that the code marks the trust boundary explicitly. Suspect any code that:

- Concatenates untrusted strings into SQL, shell, or path operations
- Logs untrusted data without escaping (log injection)
- Reflects untrusted data into HTML/templates without contextual escaping
- Trusts a field's "type" without runtime validation

Flag the boundary in the review with a fence marker:

```
┌─ UNTRUSTED INPUT — sanitize before use ─┐
req.body.user_id  →  used in `WHERE id = ${user_id}`
└─────────────────────────────────────────┘
```

---

## Mandatory Companions

| File                                                       | Role                                                                    | Load when        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------- |
| [`reference/review-lenses.md`](reference/review-lenses.md)         | Specialist agents, checklists, validation, output format                | Every invocation |
| [`reference/review-standards.md`](reference/review-standards.md)   | Standards cited by the standards compliance lens                        | Every invocation |
| [`reference/review-operations.md`](reference/review-operations.md) | Pre-flight, commands, posting flow, platform-context handling, traceability execution | Every invocation |
| [`../reviews/schemas.md`](../reviews/schemas.md)                   | Fenced-block schemas + source-tag rules                                 | Every invocation |
| [`../reviews/runbook.md`](../reviews/runbook.md)                   | Fixed phase sequence shared with cleanup                                | Every invocation |
| [`../reviews/validate.py`](../reviews/validate.py)                 | Pre-post validator (stdlib-only)                                        | Before posting   |
| [`../reviews/arch-violations/`](../reviews/arch-violations/)       | Architectural-violation catalog (11 files; index in README.md)          | Lens 6 runs      |
| [`~/.skills/shared/QUALITY_RUBRIC.md`](../shared/QUALITY_RUBRIC.md) | Supplementary rubric (M1–M12, Tiers A–I, anti-patterns)                 | Supplementary    |
| [`~/.skills/shared/TEST_ANTIPATTERNS.md`](../shared/TEST_ANTIPATTERNS.md) | Supplementary test anti-pattern catalog                            | Supplementary    |
| [`~/.skills/shared/SKILL_NOISE_TERMS.md`](../shared/SKILL_NOISE_TERMS.md) | Skill-internal terms that must not appear in committed artifacts — flag as `scope-leak` | When reviewing comments, CI YAML, Makefile, PR body |

---

## Fix-first disposition

The reviewer commits fixes; it does not just leave comments. A pull request
full of comments is more human work; a reviewed artifact with the fixes
already applied is less. Comments are for genuine open questions, not for
work the reviewer could do itself.

After the ledger, give every VALIDATED finding a disposition:

- **FIX (default):** mechanical or unambiguous changes with a localized blast
  radius: the lens's suggested edit is clearly correct and behavior-preserving
  (banned API, import shape, null guard, dead code, naming, obvious bug with a
  single correct fix). Apply it to the working tree using `pr-fix`'s safety
  rules (one at a time, minimal diff, verify after each). Collect these in a
  `REVIEW-FIXED` block: `file:line`, the finding, and the commit/diff.
- **COMMENT:** open questions only: a behavior change, an ambiguous intent, a
  design trade-off, a one-way-door or high-blast-radius change, or anything
  where more than one fix is defensible. These are posted (PR mode) or reported
  (local mode).

Mode rules:

- **Branch checked out locally (local mode, or a PR branch in a worktree):**
  apply FIX findings and commit locally. Never push; the user reviews and
  pushes. Report the `REVIEW-FIXED` block plus any COMMENT findings in chat.
- **PR branch not checked out or not writable by you:** every finding becomes
  a COMMENT; note in the summary which ones would otherwise have been fixed.

When unsure whether a finding is FIX or COMMENT, treat it as COMMENT. The
validator gate still runs on whatever is posted.

## Scope Boundary

| In scope                           | Out of scope                             |
| ---------------------------------- | ---------------------------------------- |
| PR diff review                     | Full repo health audit                   |
| GitHub inline comments             | Ticket editing                           |
| Code-review findings with evidence | Generic “LGTM” approval without evidence |

---

## Output Rules

- Every finding must cite concrete evidence from changed code.
- Every finding must pass its lens checklist threshold.
- Findings are ordered by severity/category after deduplication.
- Posted comments carry no agent or model signature.

## Close the loop

After the ledger, if any finding was mechanical (a fixed pattern, banned
API, import shape, or file location a check could catch) or repeats a
standard review keeps enforcing by hand, add one line: `Suggest /retro to
turn these into a check or standard so they are not reviewed by hand
again.` The goal is to never write the same comment twice. Never run
`/retro` yourself.
