# Hook & Skill Principles

Canonical reference for when to invoke each enforcement skill and when
to promote it to a hook. Referenced by `onboard`,
and any agent that asks "should this be a hook?"

## Why hooks backfire

A hook becomes counter-productive when it does any of these:

1. Fires on every save → agent learns to dismiss output → signal dies.
2. Adds > 500ms per invocation on a hot event → session slows measurably.
3. Dumps verbose output into the context window → poisons later turns.
4. Cascades into its own tool calls (especially `PreToolUse: Bash` → Bash).
5. Can be silently bypassed → bypass becomes the norm.
6. Enforces a stale rule nobody owns.
7. Over-enforces on spikes, prototypes, research code.

## Hook criteria (all five required)

Promote a skill to a hook only if:

- [ ] Check runs in < 500ms on a warm system
- [ ] Event is rare (PR creation, commit, session open — not every edit)
- [ ] Signal is high (low false-positive rate in practice)
- [ ] Cost of the miss is high (shipped bug, false claim, policy breach)
- [ ] Bypass is explicit (user action, not agent reasoning)

If any criterion fails, keep it as a skill invoked on demand.

## Skill trigger matrix

| Skill / companion | Best trigger | Avoid when | Hook? |
|---|---|---|---|
| `verify` | Before PR, before commit of a fix | Mid-TDD loop | **Yes — halt** on PR/commit |
| `caveman` | Context > 50%, bulk reports | First reply, specs, errors | No - the agent cannot measure its own context; invoke on demand |
| `cleanup/WRITE_TIME_GUARD.md` | New file or new export in mature repo | Tests, generated, prototypes | No — call from workflow |
| `cleanup/LAYER_ENFORCEMENT.md` | Import added AND layer map exists | No layer map | **Advisory** PostToolUse |
| `tdd/MOCK_CONTRACT.md` | New boundary mock in prod test | Pure-fn tests, spikes | **Advisory** on test file writes |
| `tdd/MUTATION.md` | End of TDD cycle, pre-PR audit | Every save (too slow) | No — on demand |
| `onboard/WORKFLOW_GATES.md` | First turn of a session | Every prompt | No - link it from the project AGENTS.md, which every harness loads |
| Self code review | Before `gh pr create` | Draft PRs | No - `pr-create` Phase 0 runs it |
| `ticket-review` AC→Test table | User asks for a pre-build ticket audit | Default `/todo` drive | No - optional specialist |
| `pr-fix` staleness | After each review-comment fix | No PR open | No — internal |
| `cleanup` Phase 0 | On-demand audit, pre-PR self-review | After every edit | No |

## The decision rule

> Hook if the cost of the miss is high AND the check is cheap AND the
> event is rare. Skill otherwise.

Examples applied:

- `verify` on `git commit` → HIGH cost (false done), CHEAP check
  (scan recent claims), RARE event → **hook**.
- `mutation-critic` on every save → HIGH cost (tautological test), but
  EXPENSIVE check (seconds) and FREQUENT event → **skill**.
- `redundancy-watcher` on every `Write` → moderate cost, cheap-ish
  check but FREQUENT event → **skill**, invoked from `workflow-guard`.

## Mechanical rule or judgement call

Sort a recurring mistake before choosing where its fix lives.
A mechanical violation (fixed pattern, banned API, import shape, file location) gets a deterministic check: a lint rule, a commit hook or a CI job.
A judgement call (consistency, fit with surrounding code) goes in the project's standards file, which review reads.
The decision rule above then says whether that check also runs as an agent hook.

Prove each new hook fires: trigger its event once (for a commit hook, make a commit through it) and see it run.

## Advisory vs. blocking

Reserve `halt` for unambiguous, user-visible harms:

- Secrets in staged files
- `CLAIM_UNVERIFIED.md` present at PR/commit time
- Upward layer imports with a provided fix suggestion

Everything else is `advisory` — the hook posts a report; the agent or
user decides. Advisory hooks degrade gracefully; blocking hooks must
earn their block with a concrete, cheap alternative.

## Hook catalogue

Add a hook only when a real failure mode points to it.

| Hook | Event | Mode | Timeout |
|---|---|---|---|
| `verify-gate` | `PreToolUse: Bash` running `git commit` or `gh pr create` | halt | 5s |
| `merge-gate` | `PreToolUse`: shell and MCP merge, approval, protected-branch push and local merge attempts | halt | 5s |

`verify-gate` only catches an agent that ran verify, recorded a failure, and
tried to ship anyway. It cannot catch an agent that never ran the check;
that rule lives in AGENTS.md and `pr-create` Phase 0.

Removed hooks and where their intent lives now:

- PR self-review reminder → `pr-create` Phase 0.
- Ticket BUILD reminder → `/todo` state detection.
- Workflow-gates notice → a link from the project AGENTS.md.
- Caveman context reminder → on demand; no hook can see context usage.

Advisory hooks that only print and exit 0 are not shown to the model on
some harnesses. Don't add one; make it block, or make it a skill step.

Anti-examples (do NOT add these):

- Any hook on `PreToolUse: Write` or `Edit` that greps the codebase
- Any hook that runs the full test suite
- Any hook that invokes `mutation-critic` or `pr-review` on every save
- Any hook blocking with no override path
- Any hook reporting subjective judgments (opinion-as-policy)

## Override protocol

`verify-gate` accepts two bypasses:

1. Resolve the cause (for `verify-gate`: produce the evidence, or
   the user says `override: <reason>` and the agent deletes the marker
   and records the reason in the PR body).
2. `.hooks-disabled` (or `.claude/hooks-disabled`) at repo root - hooks
   skip silently until removed. Used for spikes and prototypes.

Agents MUST NOT override hooks on their own reasoning. "I think this
is fine" is not an override.

`merge-gate` does not accept marker-file bypasses or infer authorization from prompts.
The owner performs merges and approvals in their own terminal or GitHub UI.
The clean `~/.skills` main-push exception is the only automatic protected-branch exception.
Blocked ways to land unreviewed work on `main`, `master` or `dev`:
- `gh pr merge`, REST `/merges`, `/pulls/N/merge`, `/git/refs/heads/<protected>`, `/contents` writes to a protected branch, GraphQL merge mutations.
- GitHub MCP `merge_pull_request`, `enable_auto_merge`, and `push_files`, `create_or_update_file`, `delete_file` aimed at a protected branch.
- `git push` to a protected branch, including a bare `git push` or `HEAD` while on one, `--all`, `--mirror`, glob refspecs and deletes.
- On a protected branch: `git merge`, `cherry-pick`, `rebase`, `am`, `revert` and a `git pull` that can merge; `--abort`, `--quit`, `--continue` and `--skip` stay allowed.
- Moving a protected ref from elsewhere: `git branch -f|-M|-C`, `checkout -B`, `switch -C`, `update-ref`, `fetch|pull <remote> x:main`.
- The same commands inside `sh -c`, `eval` or `xargs` text, and via a full path such as `/usr/bin/git`; a chained `git checkout main &&` counts as being on main.
- Text handed to a shell is matched unblanked, so quoting a blocked command inside `sh -c` also blocks; that is accepted.
`git pull --ff-only` and `git pull --rebase` stay allowed, so syncing main from origin works.
When blocked, the agent tells the owner the exact command to run themselves (`! gh pr merge <n> --squash`) or to merge on GitHub, and does not retry or work around the gate.
Land work by pushing a branch, opening a PR and letting the owner merge it.
Out of scope: scripts or other programs that call git or the API on their own, `git reset --hard <ref>` and plain `git commit` on main.
Each git probe inside the gate has a 1s cap, well inside the 5s hook timeout; a probe timeout fails closed (blocks).

## Guard sync

**Summary:** `/sync hooks` reconciles shared Git guards and native hook registrations for every installed harness.
This is an agent procedure, not another installer or a new skill.
The skill count is unchanged.
Bootstrap owns the executable Git guards and machine setup facts; `~/.skills/hooks/merge-gate.py` owns the native agent gate.
Retire the older bootstrap repo-crawling installation path in favor of BOM reconciliation; do not reintroduce it under `/sync`.

### Reconcile

1. Discover the bootstrap checkout, then read its `AGENTS.md`, `BOM.md` Git guards section and settings-migration procedure.
   Use the approved checkout, not an unmerged branch or a copied wrapper in the skills repo.
2. Inventory installed harnesses from `shared/SYMLINK_MAP.md`, plus other harnesses the owner uses, including OMP and VS Code/Copilot.
   Record the active profile, config source and shell PATH for each; skill discovery does not establish hook support.
3. Audit the shared wrapper, Git template and effective repository pre-push hooks against bootstrap's BOM.
   Cover the current repo and owner-selected existing repositories, not a recursive crawl of the home directory.
   Check `core.hooksPath` before choosing a hook destination.
   Preserve other hooks and template content; an existing `exec` must not make the guard unreachable.
4. Read the installed harness version's hook documentation before adding a registration or adapter.
   Register the canonical script by absolute path with a five-second timeout, after verifying its input and blocking-output contracts.
   Keep unrelated hooks and settings; a missing hook is added, a conflicting one needs approval.
   Follow bootstrap's backup, format-preservation and concurrent-edit checks.
5. When duplicate registrations exist, identify their effective source, including compatibility imports.
   Propose one native registration and remove only approved duplicate entries for this same gate in the same change.
   Preserve all unrelated imported hooks; do not disable compatibility imports globally.
6. Report each installed harness even when it has no verified blocking-hook adapter.
   Shared CLI guards are partial coverage, not protection of direct MCP calls or arbitrary API clients.
   Do not mark a harness protected merely because its skills directory is linked.

### Native registrations

| Harness | Registration | Contract |
|---|---|---|
| Claude Code | `hooks.PreToolUse` in the active profile's `settings.json` | Matcher `^(Bash|mcp__.*)$`; command receives `tool_name` and `tool_input`; exit 2 blocks |
| Devin CLI | `hooks.PreToolUse` in `~/.config/devin/config.json` | Matcher `^(exec|mcp_call_tool|mcp__.*)$`; same command payload and exit 2 |
| Codex, Cursor, OpenCode, pi, OMP, Antigravity, VS Code/Copilot, other installed harnesses | Resolve from the installed version's documentation | Until an adapter is implemented and demonstrated, report `native gate unverified` rather than copying Claude's schema |

Both supported registrations invoke `python3` with the absolute path to `~/.skills/hooks/merge-gate.py`.
Quote the path for the harness's command shell.
Devin may also import Claude hooks; inspect effective registrations before adding a second copy.
Gateway/profile-specific Claude installations need their active settings file, not an assumed default.
For another hook-capable harness, adapt only the event payload and deny response; reuse the existing gate rather than maintaining another policy parser.
If no blocking hook is supported, record that limitation and retain shared CLI coverage.
Windows-native shells need a separately verified wrapper integration; the macOS bootstrap links are not Windows coverage.

### Evidence and limits

Report columns: harness/profile, CLI wrapper resolution, repository pre-push hook, native registration source, live blocking evidence and remaining gap.
Use `missing`, `registered / unverified`, `verified`, or `unsupported` only when backed by the installed version's docs.
If testing is deferred, leave live evidence `deferred`; do not run a repair implicitly.
When verification is authorized, use local throwaway repositories and a stub `gh`, then a fresh-session harmless blocked command.
Do not send a real merge, approval or push as a probe.
Repeat the audit to confirm the approved repair proposes no further edits.

A terminal is not proof of a human: agents can allocate PTYs.
These guards prevent common accidents, not a same-user process deliberately bypassing local files, absolute binaries or APIs.
Server-side authorization is separate and changes only with explicit owner approval.
For the previous accidental PR merge, this workflow would have surfaced the missing live-blocking evidence before work resumed.

## Escalation for new hooks

Before adding another hook, write down:

1. What failure mode does this catch that existing hooks miss?
2. How often will it fire (per session, per week)?
3. What's the false-positive rate on a typical week's work?
4. What's the blast radius of the miss it prevents?
5. Can it be an advisory skill instead?

If answers 1 or 4 are weak, or answer 3 is high, keep it as a skill.
