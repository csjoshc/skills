# Test Antipatterns

## Contents

- Test Structure Antipatterns
- Test Naming Antipatterns
- Test Logic Antipatterns
- Fixture Antipatterns
- Integration vs Unit Confusion
- Decision Checklist
- Quick Reference


A catalog of common testing antipatterns to avoid. See also: [SKILL.md](./SKILL.md), [TESTS.md](./TESTS.md).

---

## Test Structure Antipatterns

### God Test File
**Definition:** A single test file with 500+ lines testing unrelated functionality.

**Impact:** Hard to navigate, long CI runs, merge conflicts.

**Refactor:** Split by feature/domain.

---

### Duplicate Test Suites
**Definition:** Same tests exist in multiple directories (e.g., `tests/` and `project_export/tests/`).

**Impact:** Confusion, maintenance burden, inconsistent results.

**Refactor:** Single source of truth, consolidate to one location.

---

### Test Without Assertions
**Definition:** Test runs code but has no meaningful assertions.

```python
# BAD
def test_something():
    process_data()  # No assertions!

# GOOD
def test_something():
    result = process_data()
    assert result.status == "completed"
```

---

### Over-Mocked Tests
**Definition:** Mocking internal collaborators instead of testing through public interfaces.

```python
# BAD - mocks internals
def test_checkout():
    mock_payment = Mock()
    order = Order()
    checkout(order, mock_payment)
    mock_payment.charge.assert_called_once()

# GOOD - tests behavior
def test_checkout():
    order = Order()
    result = checkout(order, valid_payment)
    assert result.status == "confirmed"
```

---

## Test Naming Antipatterns

### Test Name Describes HOW
**Definition:** Test name tells you how the code works, not what it does.

| Bad | Good |
|-----|------|
| `test_checkout_calls_payment_gateway` | `test_checkout_succeeds_with_valid_card` |
| `test_user_validation_regex` | `test_rejects_invalid_email_format` |

---

### Generic Test Names
**Definition:** Names that don't describe specific behavior.

```python
# BAD
def test_1(): ...
def test_process(): ...
def test_error_case(): ...

# GOOD
def test_rejects_negative_quantity(): ...
def test_calculates_tax_correctly(): ...
```

---

## Test Logic Antipatterns

### Test Logic Duplication
**Definition:** Same setup/assertion repeated across multiple tests.

**Refactor:** Extract to fixtures or helper functions.

---

### Conditional Test Logic
**Definition:** Tests with `if` statements that change behavior.

```python
# BAD
def test_something():
    if env == "prod":
        # different assertions!
```

---

### Dry-Run Dependency

**Definition:** Using dry-run mode as the primary verification method for feature completion when a real backend is available.

```python
# BAD - Always using dry-run for feature tests
def test_generation():
    init_pipeline(backend="dry_run")
    result = generate_image(params)
    assert result is not None  # Doesn't verify real generation

# GOOD - Use real backend for feature verification
def test_generation():
    init_pipeline(backend="comfyui")  # or default
    result = generate_image(params)
    assert result is not None
    assert result.size == expected_size
```

**Impact:** Tests pass but feature doesn't work in production; false confidence.

**Fix:** Default to real backend; use dry-run only for:
- Orchestration logic tests
- CI pipelines without GPU
- Error handling without external dependencies

---

### Testing Multiple Things
**Definition:** One test that verifies multiple unrelated behaviors.

```python
# BAD - too much!
def test_order_processing():
    # Creates order
    # Validates inventory
    # Charges payment
    # Sends email
    # Updates inventory
    # Updates user points

# GOOD - one thing per test
def test_order_creation_returns_order_id(): ...
def test_order_charges_payment(): ...
def test_order_sends_confirmation_email(): ...
```

---

## Fixture Antipatterns

### Fat Fixtures
**Definition:** Fixtures that do too much, creating unnecessary objects.

**Refactor:** Create focused fixtures, only what's needed.

---

### Fixture Smell
**Definition:** Tests depend on shared fixture state that mutates.

**Refactor:** Use fresh fixtures per test, or reset state explicitly.

---

## Integration vs Unit Confusion

### Fake Unit Tests
**Definition:** "Unit tests" that actually test multiple integrated components.

**Impact:** Slow, brittle, don't pinpoint failures.

**Fix:** Either:
- Make them true integration tests (explicit)
- Or isolate units properly

---

## Decision Checklist

| Question | Threshold | Action |
|----------|-----------|--------|
| Test file > 300 lines? | Split by feature |
| Same test in 2+ places? | Consolidate |
| Test has no assertions? | Add or delete |
| Mocking internal classes? | Test via public API |
| Test name has "how"? | Rename to "what" |
| One test > 50 lines? | Split |
| Test setup > 20 lines? | Extract fixture |
| Tests share mutable state? | Use fresh fixtures |
| Test always uses dry-run? | No GPU/CI constraint | Use real backend |

---

## Quick Reference

| Antipattern | Trigger | Solution |
|-------------|---------|----------|
| God Test File | > 500 lines | Split by feature |
| Duplicate Suites | Same tests in 2 dirs | Consolidate |
| No Assertions | assert missing | Add meaningful assertions |
| Over-Mocking | Mocking internal classes | Test through public API |
| Generic Names | "test_1", "test_func" | Name describe behavior |
| Multi-Behavior | > 3 assertions | Split into separate tests |
| Fat Fixtures | Excessive setup | Create focused fixtures |
| Conditional Logic | if/else in tests | Split into separate tests |
| Dry-Run Dependency | Always backend="dry_run" | Use real backend for feature tests |
