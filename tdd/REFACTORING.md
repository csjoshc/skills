# Refactor Candidates

After TDD cycle, look for:

## Code Smells

Twelve Fowler smells (_Refactoring_, ch. 3), each as what it is -> how to fix.
This is the single copy; pr-review links here.
A documented repo standard overrides any smell, and a smell is a judgement call, never a hard violation.

- **Mysterious Name:** a function, variable or type whose name hides what it does or holds -> rename it; if no honest name comes, the design is murky.
- **Duplicated Code:** the same logic shape in more than one place -> extract the shared shape and call it from both.
- **Feature Envy:** a method that reaches into another object's data more than its own -> move it onto the data it envies.
- **Data Clumps:** the same few fields or params keep travelling together -> bundle them into one type and pass that.
- **Primitive Obsession:** a primitive or string standing in for a domain concept -> give the concept its own small type.
- **Repeated Switches:** the same `switch` or `if` cascade on the same type in several places -> replace with polymorphism, or one map both sites share.
- **Shotgun Surgery:** one logical change forces scattered edits across many files -> gather what changes together into one module.
- **Divergent Change:** one module is edited for several unrelated reasons -> split it so each module changes for one reason.
- **Speculative Generality:** abstractions, params or hooks for needs nobody has -> delete them and inline until a real need shows.
- **Message Chains:** long `a.b().c().d()` navigation the caller depends on -> hide the walk behind one method on the first object.
- **Middle Man:** a class or function that mostly delegates onward -> cut it and call the real target directly.
- **Refused Bequest:** a subclass or implementer that ignores or overrides most of what it inherits -> drop the inheritance and use composition.

Smell list adapted from mattpocock/skills `code-review` (MIT).

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
