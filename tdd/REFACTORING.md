# Refactor Candidates

After TDD cycle, look for:

## Code Smells

| Smell | Refactor To |
|-------|-------------|
| **Duplication** | Extract function/class |
| **Long methods** | Break into private helpers (keep tests on public interface) |
| **Shallow modules** | Combine or deepen |
| **Feature envy** | Move logic to where data lives |
| **Primitive obsession** | Introduce value objects |
| **God class** | Split by responsibility |
| **Shotgun surgery** | Consolidate related changes |

## When to Refactor

1. **After GREEN** - Never refactor while tests are failing
2. **When tests reveal issues** - New code often exposes problems in existing code
3. **Before adding new behavior** - Clean first, then extend

## Refactoring Safety

- Tests should pass before and after refactor
- If tests break during refactor, you changed behavior, not just structure
- Small, incremental changes with test runs between each

## What to Look For

After each TDD cycle, ask:

- Is there duplication between tests? → Extract fixture
- Is test setup complex? → Extract helper functions
- Are tests coupled to implementation? → Rewrite to test behavior
- Does existing code look worse after new code? → Refactor existing code too
