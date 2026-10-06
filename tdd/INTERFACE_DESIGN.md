# Interface Design for Testability

Good interfaces make testing natural:

## 1. Accept Dependencies, Don't Create Them

```typescript
// Testable
function processOrder(order, paymentGateway) {}

// Hard to test
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

## 2. Return Results, Don't Produce Side Effects

```typescript
// Testable
function calculateDiscount(cart): Discount {}

// Hard to test
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

## 3. Small Surface Area

- Fewer methods = fewer tests needed
- Fewer params = simpler test setup

## 4. Deep Modules

A deep module has:
- Simple, small public interface
- Complex implementation hidden behind it

```
Shallow:  many methods, simple logic → lots of tests needed
Deep:     few methods, complex logic  → fewer tests, more coverage
```

## 5. Explicit is Better Than Implicit

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

## 6. Interaction Spec (behavioral contract)

Before implementation, capture **how** the unit collaborates — not just type shapes.
Keep it declarative (markdown or a lightweight `*.interaction.spec` / comment block next to the interface). Include:

- Expected call patterns (who calls this, with what)
- Required dependency interactions (input → output per call)
- Side effects (if any)
- Failure modes and conditions
- Ordering / temporal constraints (if any)

Do **not** re-test type shape or guard correctness in behavioral tests — those belong in contract/guard tests. Behavioral tests assert against this interaction contract + requirements.

## 7. Explicit function surface (optional TS/DI convention)

When a module is exported for consumption elsewhere and must stay DI-testable, prefer an explicit split over ad-hoc bags of args:

- **Deps** — injected collaborators (always mockable)
- **Params** — caller-controlled configuration
- **Payload** — the data being transformed
- **Return** — success | error union (do not silently omit the error arm for "this can't fail")

Internal helpers are exempt. Existing code need not be rewritten to this shape unless the ticket asks for it.

## 8. Fractal module companions

When a package uses co-located support files, keep the support set with the source unit:

| Companion | Role |
|---|---|
| interface / types | Owned contracts for this unit |
| guards (+ guard tests) | Runtime boundary enforcement |
| mocks / factories | Canonical test doubles for consumers |
| unit tests | Behavior vs interaction spec |
| provides / index | Public export surface |
| integration tests | Real chain at approved boundaries |

Prefer **component-owned types** at the boundary you control; avoid drive-by shared type packages that couple unrelated modules. See `./MOCKING.md` for canonical mocks.
