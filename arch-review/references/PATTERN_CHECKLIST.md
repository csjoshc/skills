# Architecture Pattern Checklist

Quick reference for reviewing architecture compliance.

## Macro Architecture Check

### Microservices ✓/✗
- [ ] Services deploy independently
- [ ] Each service owns its data (no shared tables)
- [ ] API contracts are versioned
- [ ] Communication via well-defined interfaces
- [ ] No distributed transactions without saga

### Modular Monolith ✓/✗
- [ ] Package structure reflects module boundaries
- [ ] No cyclic dependencies between modules
- [ ] Modules have narrow public APIs
- [ ] Clear ownership per module

## Micro Architecture Check

### Hexagonal Architecture ✓/✗
- [ ] Domain has zero external dependencies
- [ ] All I/O through ports
- [ ] Adapters implement port interfaces
- [ ] Business logic in domain layer only

### Vertical Slices ✓/✗
- [ ] Each feature contains all needed code
- [ ] No cross-feature import chains
- [ ] Feature-specific types co-located
- [ ] Tests mirror feature structure

### Layered Architecture ✓/✗
- [ ] Clear layer responsibilities
- [ ] No business logic in UI layer
- [ ] No infrastructure imports in domain
- [ ] Dependency direction inward only

## DDD Check

### Bounded Contexts ✓/✗
- [ ] Clear context boundaries defined
- [ ] Models don't leak across contexts
- [ ] Integration points are explicit
- [ ] Context map exists

### Tactical Patterns ✓/✗
- [ ] Entities have identity + behavior
- [ ] Value objects are immutable
- [ ] Aggregates enforce invariants
- [ ] Domain events for significant changes
- [ ] Repositories abstract persistence

## Common Anti-Patterns

- [ ] God modules (500+ LOC, too many responsibilities)
- [ ] Feature envy (class that manipulates another's data)
- [ ] Cyclic dependencies
- [ ] Anemic domain model
- [ ] Premature abstraction
- [ ] Tight coupling to concrete implementations

## Review Output Template

```
## Architecture Review: [path or PR]

### Pattern in Use
- Macro: [microservices | modular monolith]
- Micro: [hexagonal | vertical slices | layered]

### Findings

#### [Issue 1]
- File: [path:line]
- Pattern: [which pattern violated]
- Evidence: [specific code evidence]
- Fix: [suggested fix]

#### [Issue 2]
...

### Summary
- Pattern compliance: [X/Y checks pass]
- Critical issues: [list]
- Recommended actions: [list]
```
