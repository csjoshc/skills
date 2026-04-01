# Test Design & Refactoring

## Interface Design for Testability

Good interfaces make testing natural.

### 1. Accept Dependencies, Don't Create Them

```typescript
// Testable
function processOrder(order, paymentGateway) {}

// Hard to test
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

### 2. Return Results, Don't Produce Side Effects

```typescript
// Testable
function calculateDiscount(cart): Discount {}

// Hard to test
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

### 3. Small Surface Area

- Fewer methods = fewer tests needed
- Fewer params = simpler test setup

### 4. Deep Modules

A deep module has:
- Simple, small public interface
- Complex implementation hidden behind it

```
Shallow:  many methods, simple logic → lots of tests needed
Deep:     few methods, complex logic  → fewer tests, more coverage
```

### 5. Explicit is Better Than Implicit

```typescript
// Good: Explicit inputs/outputs
function validateEmail(email: string): ValidationResult {}

// Bad: Implicit side effects
function validateEmail(email: string): void {
  // modifies global state?
  // throws on error?
  // returns nothing for ambiguity
}
```

---

## Refactoring After TDD

### Code Smells

| Smell | Refactor To |
|-------|-------------|
| **Duplication** | Extract function/class |
| **Long methods** | Break into private helpers (keep tests on public interface) |
| **Shallow modules** | Combine or deepen |
| **Feature envy** | Move logic to where data lives |
| **Primitive obsession** | Introduce value objects |
| **God class** | Split by responsibility |
| **Shotgun surgery** | Consolidate related changes |

### When to Refactor

1. **After GREEN** — Never refactor while tests are failing
2. **When tests reveal issues** — New code often exposes problems in existing code
3. **Before adding new behavior** — Clean first, then extend

### Refactoring Safety

- Tests should pass before and after refactor
- If tests break during refactor, you changed behavior, not just structure
- Small, incremental changes with test runs between each

### What to Look For

After each TDD cycle, ask:

- Is there duplication between tests? → Extract fixture
- Is test setup complex? → Extract helper functions
- Are tests coupled to implementation? → Rewrite to test behavior
- Does existing code look worse after new code? → Refactor existing code too
