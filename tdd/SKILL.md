---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", or wants test-first development. Language-agnostic.
---

# Test-Driven Development (TDD)

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means (like querying a database directly instead of using the interface). The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [TESTS.md](./TESTS.md) for examples and [MOCKING.md](./MOCKING.md) for mocking guidelines.

Companion files to load at specific phases:
- [SCOPING.md](./SCOPING.md) — **required Phase 0**. Produces the ranked Test Obligation Queue (`.tickets/tdd/toq-<ticket-id>.yaml`) from diff, dependency graph, risk registry, and churn. Every downstream phase reads from this queue; nothing is invented from prose.
- [MOCK_CONTRACT.md](./MOCK_CONTRACT.md) — required when the red-step test introduces a boundary mock (HTTP, DB, FS, time, SDK). Enforces that every mock references a real contract artifact and rejects conditional-branch mocks.
- [MUTATION.md](./MUTATION.md) — auto-fires at green-step completion for any TOQ entry with `mutation_candidate: true` (T1 + score > 60). Optional otherwise.

---

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" - treating RED as "write all tests" and GREEN as "write all code."

This produces **crap tests**:

- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things (data structures, function signatures) rather than user-facing behavior
- Tests become insensitive to real changes - they pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

**Correct approach**: Vertical slices via tracer bullets. One test → one implementation → repeat. Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
  ...
```

---

## Dry-Run Usage (IMPORTANT)

Tests should default to running in **NON dry-run mode** to ensure real-world connectivity and generation parity.

**When to use dry-run:**
- Rapid iteration on orchestration logic
- CI pipelines where live backend is unavailable
- Testing error handling without external dependencies

**When NOT to use dry-run:**
- Feature completion verification (unless explicitly justified)
- Integration tests that verify end-to-end behavior
- Tests that validate actual output quality

Dry-run mode (`backend="dry_run"`) is valuable for isolated unit testing, but it MUST NOT be the primary verification method for feature completion.

---

## Commit Discipline

After each feature (or small set of tasks):

1. **Run the relevant tests** from your test suite
2. **Update progress documentation** with status and notes
3. **Stage all related files**, including new files (`git add ...`)
4. **Verify `git status` is clean** before commit
5. **Create a small, descriptive git commit** so rollback is clean

```bash
# Example commit workflow
pytest tests/path/to/test.py -v           # Run tests
git add src/path/file.py tests/path/test.py
git status                                 # Verify clean
git commit -m "feat: add specific feature"
```

**Deprecation Cleanup:**
When a file/module is confirmed unused or explicitly deprecated:
1. Remove the file in the same feature branch
2. Verify no references remain (`rg -n "OldSymbol|old/path"`)
3. Include the deletion in the same commit as the replacement work

---

## Workflow

### 0. Scoping (deterministic) — REQUIRED

Run **before** Planning. Loads [SCOPING.md](./SCOPING.md) and produces the
ranked Test Obligation Queue at `.tickets/tdd/toq-<ticket-id>.yaml`.

Inputs are pulled from the orchestrate envelope (ticket path, diff base, registry
path) or discovered from the working tree. Signal collection (diff, blast radius,
MCP dependency graph, churn, failure history, existing tests, risk tier) is
deterministic — no LLM inference. The model only **ranks and shapes** candidates
via the pattern catalog in SCOPING.md.

If the TOQ already exists and is fresh (mtime ≥ ticket mtime AND diff_base
unchanged), reuse it. Otherwise regenerate.

### 1. Planning

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

### 2. Tracer Bullet

Pull the **top non-deferred entry** from the TOQ. Write ONE test for its
`done_when` condition:

```
RED:   Write test for TOQ[0].done_when → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

### 3. Incremental Loop

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

### 4. Refactor

After all tests pass, look for refactor candidates:

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

---

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```

---

## Applying to Bug Fixes

When fixing a bug, TDD still applies:

1. **Write a failing test first** that reproduces the bug
2. **Fix the bug** to make the test pass
3. **Refactor** if needed

This ensures:
- The bug is actually reproduced (not just symptoms)
- The fix actually works
- The bug doesn't regress

```
RED:   Write test that fails due to bug → test fails
GREEN: Fix bug → test passes
REFACTOR: Clean up if needed
```
