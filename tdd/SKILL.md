---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", or wants test-first development. Language-agnostic.
---

# TDD

## TL;DR (Quick Start)

Write ONE failing test → write minimal code to pass → refactor. Repeat for each behavior. Tests verify public interfaces, not implementation details.

**When to use:** Building new features, fixing bugs, refactoring with safety net. NOT for exploratory spikes or one-off scripts.

**Invocation:** Plan behaviors → RED (test fails) → GREEN (minimal code) → REFACTOR.

## Assumptions & Escalation

**[ASSUMPTION: Test framework available]** — If no test framework exists, add Task 0 to install pytest/vitest/jest per STANDARDS.md.

**[ASSUMPTION: User can identify behaviors to test]** — If user unsure what to test, prompt: "What should the public interface do?" Focus on user-facing behaviors.

**Escalation thresholds:**
- Tier 1 (reversible): Test naming, file location → proceed, flag for post-review
- Tier 2 (architecture): Test framework choice, mocking strategy → check STANDARDS.md
- Tier 3 (security): Testing auth/encryption flows → always block for human confirmation

## Decision Tree

Use this skill when you need to:

1. **Is this a new feature or bug fix?**
   - YES → Use TDD workflow (RED→GREEN→REFACTOR)
   - NO (exploratory spike, one-off script) → Skip TDD, document manually

2. **What type of test is needed?**
   - Unit test (single function/class) → Test public methods, edge cases
   - Integration test (multiple components) → Test through public API
   - E2E test (full user flow) → Use Playwright/cypress per STANDARDS.md

3. **Is mocking appropriate?**
   - External services (API, DB) → Use mocks/stubs
   - Internal collaborators → Prefer real objects (integration-style)
   - Pure functions → No mocks needed, test directly

4. **When to stop adding tests?**
   - All critical paths covered → Stop
   - Diminishing returns (testing trivial getters) → Stop
   - User confirms priority behaviors tested → Stop

## Examples (Few-Shot)

**Example 1: New feature — user login**

Input: "Add user login functionality with email and password"

Output (TDD workflow):
```
RED: Write test for successful login
  def test_login_valid_credentials():
      user = create_user(email="test@example.com", password="secure123")
      result = login(email="test@example.com", password="secure123")
      assert result.success == True
      assert result.user_id == user.id

GREEN: Implement minimal login function
  def login(email, password):
      user = db.get_user_by_email(email)
      if user and verify_password(password, user.password_hash):
          return LoginResult(success=True, user_id=user.id)
      return LoginResult(success=False)

REFACTOR: Extract password verification, add rate limiting

RED: Write test for failed login (wrong password)
RED: Write test for failed login (user not found)
RED: Write test for rate limiting (5 failed attempts)
```

**Example 2: Bug fix — null pointer in cart total**

Input: "Cart total crashes when cart is empty"

Output (TDD workflow):
```
RED: Write test that reproduces the crash
  def test_cart_total_empty_cart():
      cart = Cart()  # empty cart
      total = cart.get_total()  # currently crashes
      assert total == 0  # expected behavior

GREEN: Fix the bug
  def get_total(self):
      if not self.items:
          return 0
      return sum(item.price for item in self.items)

REFACTOR: No refactor needed — fix is already clean
```

**Example 3: Refactor with safety net**

Input: "Refactor authentication to use JWT instead of sessions"

Output (TDD workflow):
```
RED: Write characterization tests for current behavior
  def test_auth_valid_token():
      # Tests current session-based auth
      session = create_session(user_id=123)
      assert authenticate(session).user_id == 123

GREEN: Implement JWT-based auth (tests still pass)
  def authenticate(token):
      payload = jwt.decode(token, SECRET_KEY)
      return AuthResult(user_id=payload['user_id'])

REFACTOR: Remove old session code, clean up imports

RED: Add tests for JWT-specific behavior (expiry, refresh)
```

## Related Skills

| Skill | When to use instead |
|-------|---------------------|
| `spec-writer` | When you need to plan the feature before implementing |
| `ticket-critic` | When working from a ticket — audit before Task 1 |
| `test-ui` | For frontend E2E testing (Playwright) |
| `cleanup` | For code quality audits (not behavior testing) |

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means (like querying a database directly instead of using the interface). The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [TESTS.md](./TESTS.md) for examples and [MOCKING.md](./MOCKING.md) for mocking guidelines.

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

### 1. Planning

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Identify opportunities for deep modules (small interface, deep implementation)
- [ ] Design interfaces for testability
- [ ] List the behaviors to test (not implementation steps)
- [ ] Identify async/await requirements (pytest-asyncio, httpx for streaming)
- [ ] Get user approval on the plan

Ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Confirm with the user exactly which behaviors matter most. Focus testing effort on critical paths and complex logic, not every possible edge case.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:

- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

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
