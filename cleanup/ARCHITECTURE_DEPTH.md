# Architecture Depth Lens

## Contents

- Purpose
- Vocabulary
- Deletion test
- Key principles
- How to apply

---

## Purpose

Optional Phase 1 lens for cleanup. Load when the scope includes multi-module
design or architectural structure questions. Adds an "architectural depth"
perspective not covered by the standard four lenses (Layer & Dependency,
Redundancy & Modularity, Error Handling & State, Data & Security).

Source: [improve-codebase-architecture](https://github.com/mattpocock/skills)
by Matt Pocock.

---

## Vocabulary

Use these terms precisely. Do not substitute "component," "service," "API,"
or "boundary."

| Term | Definition |
|------|-----------|
| **Module** | Anything with an interface and an implementation (function, class, package, slice) |
| **Interface** | Everything a caller must know: types, invariants, error modes, ordering, config — not just the type signature |
| **Implementation** | The code inside |
| **Depth** | Leverage at the interface: a lot of behavior behind a small interface. Deep = high leverage. Shallow = interface nearly as complex as the implementation |
| **Seam** | Where an interface lives; a place behavior can be altered without editing in place |
| **Adapter** | A concrete thing satisfying an interface at a seam |
| **Leverage** | What callers get from depth |
| **Locality** | What maintainers get from depth: change, bugs, knowledge concentrated in one place |

---

## Deletion test

The primary diagnostic for shallow modules:

> "Imagine deleting this module entirely. Does complexity vanish (the module
> was earning its keep), or does it reappear scattered across N callers
> (it was a pass-through)?"

- Complexity vanishes → module is **deep**, keep it
- Complexity reappears in callers → module is **shallow**, candidate for
  merging or deepening

---

## Key principles

- **The interface is the test surface.** If the interface can't be tested
  directly, the seam is in the wrong place.
- **One adapter = hypothetical seam. Two adapters = real seam.** Don't
  invest in the abstraction until there are two genuine implementations.
- Shallow modules: interface is nearly as complex as the implementation.
  They add indirection without reducing callers' cognitive load.
- Pure functions extracted only for testability (with the real bugs hiding
  in calling code) fail the locality test.

---

## How to apply

When running this lens during Phase 1 of cleanup, look for:

1. Modules where understanding one concept requires bouncing between many
   small files → deletion test candidates
2. Modules where the interface is nearly as complex as the implementation
   → shallow
3. Tightly-coupled modules that leak across their seams
4. Pure functions extracted only for testability, where real bugs hide in
   how they're called
5. Modules that are hard to test through their current interface → seam
   is in the wrong place

For each candidate, report (using vocabulary above):

- **Files** — which modules are involved
- **Problem** — why the current structure causes friction
- **Opportunity** — what deepening would look like (plain English, no code)
- **Test improvement** — what test is currently impossible that would
  become possible after deepening
