# TDD Workflow Details

## Contents

- 0. Scoping (deterministic, ticket builds only)
- 1. Planning, one source file per cycle, discovery halt
- 2. Tracer Bullet
- 3. Incremental Loop
- 4. Refactor
- Applying to Bug Fixes (Prove-It pattern)

Slicing patterns and risk-first ordering: [references/slicing.md](references/slicing.md).

## 0. Scoping (deterministic) - ticket builds only

Skip for bug fixes and ad-hoc work with no ticket (see SKILL.md). Otherwise run **before** Planning. Loads [SCOPING.md](./SCOPING.md) and produces the
ranked Test Obligation Queue at `.tickets/tdd/toq-<ticket-id>.yaml`.

Inputs are pulled from the ticket runner envelope (ticket path, diff base, registry
path) or discovered from the working tree. Signal collection (diff, blast radius,
MCP dependency graph, churn, failure history, existing tests, risk tier) is
deterministic — no LLM inference. The model only **ranks and shapes** candidates
via the pattern catalog in SCOPING.md.

If the TOQ already exists and is fresh (mtime ≥ ticket mtime AND diff_base
unchanged), reuse it. Otherwise regenerate.

## 1. Planning

Present the TOQ to the user. Ask:

> "Here is the ranked Test Obligation Queue derived from diff + risk-registry +
> dependency graph. Confirm, reprioritize, or reject entries before we start the
> RED loop."

- [ ] User confirms the top-N queue
- [ ] User may promote deferred entries or demote top entries (record reason)
- [ ] Identify opportunities for deep modules (small interface, deep implementation)
- [ ] Design interfaces for testability for the confirmed TOQ targets
- [ ] Identify async/await requirements (pytest-asyncio, httpx for streaming) for confirmed targets

**You can't test everything.** The TOQ caps (top 5 unit / 3 integration / 1
e2e per ticket) enforce this. Anything outside the caps is deferred, not
discarded — it stays in the YAML for future reconsideration.

### One source file per cycle (support set included)

Treat each TDD cycle as **one source file** plus its support set — not a second unrelated source file "for a small tweak."

Dependency order inside the cycle (skip steps the node does not need):

1. Contract / types (interface)
2. Type-guard tests → guards (when used)
3. Interaction expectations (see `./INTERFACE_DESIGN.md` — interaction spec)
4. Canonical mocks / factories for this unit
5. RED behavioral tests
6. Implementation
7. Public surface (`provides` / exports) if the module uses an explicit barrel
8. Integration test only when a producer → subject → consumer boundary is reached

Rules:

- Types/interfaces/guards are **not** their own cycles — attach them to the first source file that consumes the change.
- Do not orphan an interface edit in a separate task from its consumer.
- Build producers before consumers; keep the tree buildable after each cycle.
- Prefer relational identifiers (path + symbol) over numbered steps that break on insert/reorder.

### Discovery halt (multi-file scope)

If completing the current cycle requires editing a **second source file** (or an undeclared support file outside this cycle):

1. Stop editing.
2. Report discovery: dependent files, why, minimal next cycles.
3. Propose the added cycles (one source file each).
4. Wait for explicit approval — do not improvise the multi-file change.

## 2. Tracer Bullet

Pull the **top non-deferred entry** from the TOQ. Write ONE test for its
`done_when` condition:

```
RED:   Write test for TOQ[0].done_when → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

## 3. Incremental Loop

For each remaining TOQ entry (in score order):

```
RED:   Write test for TOQ[i].done_when → fails
GREEN: Minimal code to pass → passes
```

Rules:

- One TOQ entry at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on the entry's `done_when` (observable behavior)
- **Test-run scope**: when you run tests during the cycle, restrict the runner
  to `TOQ[i].target` + its `existing_tests` mapping. Do not run the full suite.
  This is what prevents unrelated tests from firing and polluting context.
  Run the full suite only at end-of-ticket, before marking Stage COMPLETE.

## 4. Refactor

After all tests pass, look for refactor candidates:

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

## Applying to Bug Fixes (Prove-It pattern)

<!-- merged from addyosmani/agent-skills test-driven-development -->

Do not start by trying to fix the bug. Start by proving it.

1. Read the bug report; restate the expected vs observed behavior in one line.
2. Write a test that exercises the failing scenario through the public interface.
3. Run it; it must fail. A passing reproduction test is not a reproduction.
   - Check the test sits at the correct seam: it exercises the real bug pattern as it happens at the call site. A seam too shallow to replay the triggering chain (one caller when the bug needs several) gives false confidence. If no correct seam exists, report that as the finding.
   - If you forced the red by mutating code or a fixture, `diff` against a pristine copy to prove the mutation landed before you trust the failure.
4. Implement the minimal fix.
5. Re-run the test; it passes.
6. Run the full relevant suite to confirm no regressions; commit test + fix together.

If step 3 doesn't fail, the test isn't testing the bug; fix the test first.

Seam and pristine-copy checks adapted from mattpocock/skills `diagnosing-bugs` (MIT).
