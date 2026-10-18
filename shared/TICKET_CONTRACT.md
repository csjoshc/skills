# Ticket contract

The one definition of a `.tickets/NNN-slug.md` file.
spec-writer writes it, `spec-writer/scripts/tickets_lint.py` checks it mechanically, ticket-critic reviews its design, `/tdd` and `/todo` read it.
No other file restates this schema; link here instead.

## Contents

- Frontmatter
- Body
- Checks
- Defaults
- Integration gates
- Lint

## Frontmatter

```yaml
---
id: T-3
title: "Red-first on added or changed tests"
Stage: BUILD
Depends-On: [T-2]
Blocks: [IG-1]
Files:
  - action: CREATE
    path: gate/scripts/red_first.py
    test: false
  - action: MODIFY
    path: gate/scripts/test_scope.py
    test: true
Read-First:
  - gate/scripts/gate.py
---
```

Required: `id`, `title`, `Stage`, `Depends-On` (may be `[]`), `Files` (at least one entry).
`Stage` is one of `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.
`NEW` means queued and not yet started; `BUILD` means implementation is in progress.
`/todo` changes `NEW` to `BUILD` when a build session starts.
`Files[].action` is `CREATE | MODIFY | VERIFY | DELETE`; add a `description` only when the path doesn't say enough.
At most 5 non-test files per ticket; split above that.

Optional: `Blocks`, `Type` (`integration-gate` for gates), `Gate` (the gate that validates this ticket; trackboard reads it), `Validates` (on a gate: the tickets it proves), `Read-First`, `Assumptions-Validated` (PRD assumption ids), `Regression-Baseline` (commands that must stay green).
A `BLOCKED` ticket also needs `Blocked-By` (what it waits for) and `Unblock-Check` (one command that exits 0 once unblocked).

Paths are repo-relative, or absolute for other repos.
A `MODIFY`, `VERIFY` or `Read-First` path must exist now or be created by a ticket this one depends on, directly or transitively.

## Body

Required sections, in this order:

1. `## Scope`: what changes, naming the files.
2. `## Acceptance Criteria → Tests`: the table below.
3. `## Verify`: one bash block that exits non-zero when any AC fails.
4. `## Notes`: implementation anchors (APIs, existing functions, decisions with a one-line reason).

Optional, only when they have content: `## Not Doing`, `## Docs to Update`, `## Assumptions`, `## Failure Protocol` (only to override the default).

### The AC table

```markdown
## Acceptance Criteria → Tests

| AC | Check | Tier |
|---|---|---|
| AC-1 Given two added tests and one edited, when changed tests are listed, then exactly those three ids return | `gate/scripts/test_scope.py::test_changed_tests_python` | T1 |
| AC-2 (failure path) Given a feature slice with no changed test, then red-first fails "no new or changed test" | `gate/scripts/test_red_first.py::test_feature_without_tests_fails` | T2 |
| AC-3 Given the settings file after the change, then its first two hook entries are unchanged | `jq -c '.hooks.PreToolUse[0:2]' ~/.claude/settings.json \| diff - "$TMPDIR/before.json"` | T1 |
```

- **AC**: Given/When/Then, one behaviour, binary. The Then clause states the expected result; that is the assertion.
- **Check**: either one test id (`path::test_name`, run with the project's runner) or one shell command. One test per row; never `-k "a or b"`, which passes when any one name exists. Escape a literal `|` as `\|`.
- **Tier**: `T1 | T2 | T3`, from the PRD risk surface; use the highest tier of the paths the AC touches.
- At least 3 rows, and at least one row marked `(failure path)` that asserts behaviour a user or an integration test can observe.
- Non-code work (config, scripts, prose skills, docs) uses a shell command as its check. Each such check is run once before the change and must fail; a grep on prose only proves the text exists, so prose wiring also needs a behavioural check later (a real session or an integration gate).

## Checks

A check is load-bearing only if it can fail.

- Run it before the change: it must fail for the expected reason (test not found, file missing, string absent), not because a tool is missing.
  The exception is a preservation check (something must stay unchanged), which passes before and after.
- Never let missing input pass: assert globs match files before reading them, use `jq -e`/`jq -er`, make `awk` fail when its line is absent, guard `${TMPDIR:?}`.
- Under `set -e`, a bare `! cmd` line never fails the script; write `if cmd; then exit 1; fi`.
- Match transcripts and logs structurally (jq on tool calls), not with a grep that also matches the prompt or loaded skill text.

## Defaults

These apply to every ticket unless its body overrides them.

- **Test evidence**: the red run of the ticket's new tests is saved before implementation, the green run after, both to `$TMPDIR/gate-proof/<id>/` (`red.txt`, `green.txt`).
- **Mutation**: T1 rows on source code get a mutation check at green (the gate's mutation check, or `tdd/MUTATION.md` as fallback); non-code rows have nothing to mutate.
- **Test pattern**: `/tdd` Phase 0 picks it from the tier and the AC (`tdd/SCOPING.md`).
- **Failure protocol**: at most 2 retries per failing AC; then revert only this ticket's files, set `Stage: FAILED`, and report the failing output to the user.
- **Style**: plain English, one sentence per line in prose, no em dashes, no plan labels (ticket or decision ids) in committed code, comments or test names.

## Integration gates

A ticket with `Type: integration-gate` changes no code and proves the tickets it depends on work together on real inputs.
Extra required sections:

- `## Silent Failure Detection`: at least one check that would catch a regression unit tests miss (a cached result that shouldn't exist, a tool that "passed" without running, a real repo that changed).
- `## Proof`: the local inner-loop evidence, as file paths the Verify block checks exist and are non-empty: red-then-green runs, every test type the repo has or the plan adds (unit, integration, property, e2e, mutation), replay or session transcripts. CI run URLs belong to the PR, not to a local gate.

A gate reaches `Stage: COMPLETE` only when a session other than the implementing one runs its Verify block and records its session id, model and date under `## Proof`, or the user marks it complete.

## Lint

`python3 spec-writer/scripts/tickets_lint.py .tickets` checks everything mechanical in this file: frontmatter, sections, the AC table, paths against the DAG, `bash -n` on Verify, and known traps (`-k` or-chains, bare `!`, em dashes).
`--runner "<pytest command>" --dry-red` also runs every test-id check and every read-only shell check (grep, test, jq) now, before build, fails when one breaks for an environmental reason (tool or module missing), and warns when one passes already (fine for a preservation check, a bug otherwise).
spec-writer runs it before handing off; ticket-critic runs it first and reviews only design, risk and scope after it passes.
