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

**Test file location — write to the permanent path immediately.** Never use `tests/tickets/`
(deprecated gitignored staging area). The path is known before BUILD starts — the ticket's
AC→Test Traceability table names it. Write the file there from the first keystroke.

| Test type | Permanent committed path |
|---|---|
| Dockerfile / Helm / nginx / CI workflow regression | `tests/infra/test_<artifact>.py` |
| Documentation consistency | `tests/docs/test_<topic>.py` |
| Package unit/integration | `packages/<pkg>/tests/test_<module>.py` |
| E2E | `tests/template_agent_e2e/` |

Include a `test_coverage_anchor` function with `import agent_guardrails` so the orch
coverage gate passes for YAML/Dockerfile-only diffs (no `conftest.py` shim needed).

Companion files to load at specific phases:
- [SCOPING.md](./SCOPING.md) — **required Phase 0**. Produces the ranked Test Obligation Queue (`.tickets/tdd/toq-<ticket-id>.yaml`) from diff, dependency graph, risk registry, and churn. Every downstream phase reads from this queue; nothing is invented from prose.
- [MOCK_CONTRACT.md](./MOCK_CONTRACT.md) — required when the red-step test introduces a boundary mock (HTTP, DB, FS, time, SDK). Enforces that every mock references a real contract artifact and rejects conditional-branch mocks.
- [MUTATION.md](./MUTATION.md) — auto-fires at green-step completion for any TOQ entry with `mutation_candidate: true` (T1 + score > 60). Optional otherwise.

---

## FIRST Principles

Unit tests should be:

- **Fast** — run in milliseconds; slow tests get skipped or run less often, defeating their purpose
- **Independent** — any test T1 followed by T2 must produce the same result as T2 then T1; tests must not share mutable global state
- **Repeatable** — same result every run; non-determinism (flaky tests) wastes time on false failures
- **Self-checking** — pass/fail without manual inspection of output files or logs
- **Timely** — written before or alongside the code, not deferred to end-of-sprint

### Flaky Tests

A test is flaky when it passes sometimes and fails other times without code changes. Common causes: thread races, `sleep`-based waits, real clocks, shared state between tests.

**Fix pattern**: if async behavior causes flakiness, extract the synchronous core into a separate function and test that instead.

```python
# FLAKY: sleeps waiting for async result
def test_pi_flaky():
    result = TaskResult()
    math.async_pi(10, result)
    time.sleep(1)  # may not be enough
    assert result.get() == 3.1415926535

# FIXED: test the sync core directly
def test_pi():
    assert math.sync_pi(10) == 3.1415926535
```

---

## Test Smells

Patterns that make tests harder to maintain — treat as warnings, not absolute rules:

- **Obscure test** — long, complex test that checks multiple things; a test should ideally verify one behavior
- **Conditional logic** — `if`/`else` or loops in test code; test logic should be linear
- **Code duplication** — repeated setup blocks across test methods; extract to `@BeforeEach` / fixtures

Like production code, tests should be refactored regularly.

---

## Asserts per Test

Prefer one assert per test — when a test fails, you know exactly why. But don't be dogmatic:

- **One behavior, one assert**: split `testEmptyStack` and `testNotEmptyStack` into separate tests
- **Object field checks**: asserting all fields of a returned object in one test is fine
- **Table-driven repetition**: multiple asserts of the same operation with different inputs is fine

---

## Test Coverage

Coverage = statements executed by tests / total statements. Useful as a floor, not a ceiling.

| Coverage | Signal |
|---|---|
| > 90% | Typical when using TDD |
| ~70–85% | Healthy for most production systems |
| < 50% | Raises concerns |
| 100% | Usually not the goal — getters/setters and UI code are hard to test |

**Branch coverage (C1)** is stricter than statement coverage (C0): an `if` with only one path tested gives 100% C0 but 50% C1. Use branch coverage when the code has meaningful conditional logic.

Don't set a rigid coverage target. Instead, monitor the trend over time and audit uncovered statements to confirm they're trivially untestable (not just forgotten).

---

## Testability

Testability is a design property: code that is easy to test tends to be well-structured. The same principles that produce good design (high cohesion, low coupling, single responsibility, dependency inversion) produce testable code.

**Common fix patterns:**

1. **Extract domain logic** — if a class depends on hard-to-instantiate types (HTTP request/response, servlet context), pull the pure logic into a separate class that takes only primitives. Test the inner class.

2. **Extract sync core from async** — if a function spawns a thread, extract the computation into a synchronous helper. Test the helper; leave the async wrapper untested or integration-tested.

```python
# Hard to test — depends on HTTP context
class BMIServlet:
    def do_get(self, req, res):
        w = req.get_param("weight")
        h = req.get_param("height")
        res.write(f"BMI: {float(w) / float(h)**2}")

# Easy to test — pure logic extracted
class BMIModel:
    def calculate(self, weight: str, height: str) -> float:
        return float(weight) / float(height) ** 2
```

---

## Mocks

Mocks replace real dependencies (external APIs, databases, file systems, clocks) so unit tests stay fast and isolated.

### Test Double Taxonomy

| Type | What it does |
|---|---|
| **Dummy** | Passed as argument but never used; satisfies type system |
| **Fake** | Simplified real implementation (e.g., in-memory database) |
| **Stub** | Returns canned responses; verifies state |
| **Mock** | Returns canned responses AND verifies interactions (e.g., "was `send()` called?") |

In practice these terms are used loosely. Most frameworks (Mockito, pytest-mock, unittest.mock) call everything a "mock."

### Mock Drawbacks

Mocks increase coupling between the test and the implementation:

- Tests can break when internals change even if observable behavior hasn't
- Mocks verify what you program them to verify — if the contract assumption is wrong, the test passes but the real integration fails

See [MOCK_CONTRACT.md](./MOCK_CONTRACT.md) for rules on when mocks require a real contract artifact.

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

> **Slicing reference:** when breaking a feature into TDD-able increments, see `references/slicing.md` for vertical-slice patterns, risk-first ordering, and the "noticed but not touching" scope-discipline callout.

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

### Prove-It Pattern (6 steps)

<!-- merged from addyosmani/agent-skills test-driven-development -->

Do not start by trying to fix the bug. Start by proving it.

1. Read the bug report; restate the expected vs observed behavior in one line.
2. Write a test that exercises the failing scenario through the public interface.
3. Run it — it MUST fail. A passing reproduction test is not a reproduction.
4. Implement the minimal fix.
5. Re-run the test — it passes.
6. Run the full relevant suite to confirm no regressions; commit test + fix together.

If step 3 doesn't fail, the test isn't testing the bug — fix the test first.

---

## DAMP over DRY in tests

Production code prefers DRY. Tests prefer **DAMP** (Descriptive And Meaningful Phrases). Each test should read like a self-contained spec — the reader shouldn't have to chase shared helpers to understand what's being verified.

```python
# DAMP — each test stands alone
def test_rejects_empty_titles():
    with pytest.raises(ValueError, match="Title is required"):
        create_task(title="", assignee="user-1")

def test_trims_whitespace_from_titles():
    task = create_task(title="  Buy groceries  ", assignee="user-1")
    assert task.title == "Buy groceries"
```

Duplication in tests is fine when it makes each test independently legible. Extract shared setup only when the duplication actively obscures intent.

---

## Integration Tests

Integration tests verify a complete feature or service involving multiple classes and real external dependencies (databases, message queues, APIs). Unlike unit tests, they do **not** use mocks for infrastructure.

Key patterns:
- Reset state before each test (`@BeforeEach` truncates DB tables, clears queues)
- Clean up connections after each test (`@AfterEach`)
- Slower than unit tests — run less frequently, but at minimum in CI

```python
class ForumIntegrationTest:
    def setup_method(self):
        self.connection = DB.truncate_tables()
        self.forum = Forum(self.connection)

    def teardown_method(self):
        self.connection.close()

    def test_empty_database(self):
        assert self.forum.list_questions() == []

    def test_add_three_questions(self):
        self.forum.add_question("1 + 1 = ?")
        self.forum.add_question("2 + 2 = ?")
        questions = self.forum.list_questions()
        assert len(questions) == 2
        assert questions[0].text == "1 + 1 = ?"
```

---

## End-to-End Tests

E2E tests simulate real user interactions from the outside — browser sessions (Selenium, Playwright), CLI invocations, or full API call chains. They sit at the top of the test pyramid: fewest in number, most expensive to write and maintain.

Trade-offs:
- Most realistic — exercises all layers
- Most brittle — a UI label change can break multiple tests
- Hardest to diagnose — a failure in an e2e test doesn't point to a specific function

Run e2e tests last, after unit and integration tests pass. Use them to verify critical happy paths, not edge cases.

---

## Test Design Techniques (Black-box)

When selecting test inputs without looking at internal code:

**Equivalence classes** — partition the input domain into groups that should behave the same way. Test one value per group. Example: for a tax function with four salary brackets, test one salary in each bracket.

**Boundary value analysis** — bugs concentrate at edges. For each boundary, test: `boundary - 1`, `boundary`, `boundary + 1`.

```
Salary range: $1,903.99 – $2,826.65 at 7.5%
Test inputs: $1,903.98, $1,903.99, $2,826.65, $2,826.66
```

These complement coverage metrics: a test suite can have 100% statement coverage but miss boundary bugs.

---

<!-- pattern: common-rationalizations -->
## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll add the test after the code works" | You won't. And tests written after the fact test implementation, not behavior. |
| "This change is too small to test" | Small changes accumulate. The test documents the expected behavior. |
| "Manual testing covered it" | Manual coverage doesn't persist. Tomorrow's change might break it silently. |
| "Mocking the DB is enough" | Mocked tests pass while real migrations fail. Integration > confidence. |

---

## Test Pyramid Summary

| Level | Scope | Mocks? | Speed | Quantity |
|---|---|---|---|---|
| Unit | Single class / function | Yes (for dependencies) | Milliseconds | ~70% of suite |
| Integration | Feature / service + real DB | No | Seconds | ~20% |
| End-to-end | Full system, real UI/API | No | Minutes | ~10% |
