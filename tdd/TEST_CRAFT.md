# Test Craft Reference

## Contents

- FIRST principles and flaky tests
- Test smells, asserts per test
- Coverage and testability
- Mocks: test double taxonomy and drawbacks
- DAMP over DRY
- Integration and end-to-end tests
- Black-box test design techniques
- Test pyramid

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

## Test Pyramid Summary

| Level | Scope | Mocks? | Speed | Quantity |
|---|---|---|---|---|
| Unit | Single class / function | Yes (for dependencies) | Milliseconds | ~70% of suite |
| Integration | Feature / service + real DB | No | Seconds | ~20% |
| End-to-end | Full system, real UI/API | No | Minutes | ~10% |
