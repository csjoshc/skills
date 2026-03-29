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
