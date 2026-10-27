# Architecture Depth Lens

## Contents

- Purpose
- Vocabulary
- Principles
- Deepening by dependency category
- Replace, don't layer
- Design it twice
- How to apply

---

## Purpose

Optional Phase 1 lens for cleanup. Load when the scope includes multi-module
design or architectural structure questions. Adds an "architectural depth"
perspective not covered by the standard four lenses (Layer & Dependency,
Redundancy & Modularity, Error Handling & State, Data & Security).

Source: [codebase-design](https://github.com/mattpocock/skills) by Matt Pocock (MIT).

---

## Vocabulary

Module, interface, implementation, depth, seam, adapter, leverage and locality
are defined once in [`../standards/modularity.md`](../standards/modularity.md).
Use those terms exactly; `pr-review` cites the same file. Depth is measured as
leverage, not as a ratio of implementation lines to interface lines, which
would reward padding.

---

## Principles

- **Depth is a property of the interface, not the implementation.**
  A deep module can be built from small swappable parts, as long as they stay out of the interface.
- **The deletion test.**
  Imagine deleting the module.
  If complexity vanishes, it was a pass-through.
  If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
  Callers and tests cross the same seam.
  Wanting to test past the interface means the module is the wrong shape.
- **One adapter means a hypothetical seam, two adapters means a real one.**
  Introduce a seam only when something actually varies across it, typically production plus test.
- **Internal vs external seams.**
  A deep module can have internal seams used by its own tests.
  Keep them private rather than exposing them through the interface.

---

## Deepening by dependency category

Classify a candidate's dependencies first; the category decides how the deepened module is tested across its seam.

1. **In-process** - pure computation or in-memory state, no I/O.
   Always deepenable: merge the modules and test through the new interface directly, no adapter needed.
2. **Local-substitutable** - has a local stand-in (PGLite for Postgres, in-memory filesystem).
   Deepenable if the stand-in exists; tests run against it, and the seam stays internal.
3. **Remote but owned (ports and adapters)** - your own services across a network.
   Define a port at the seam, keep the logic in one deep module, and inject the transport: an in-memory adapter for tests, HTTP/gRPC/queue in production.
4. **True external (mock)** - third-party services you do not control (Stripe, Twilio).
   The deepened module takes the dependency as an injected port; tests supply a mock adapter.

---

## Replace, don't layer

- Once tests exist at the deepened module's interface, delete the old unit tests on the shallow modules it replaced.
- Assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors.
  A test that must change when the implementation changes is testing past the interface.

---

## Design it twice

For a chosen candidate, the first interface idea is rarely the best (Ousterhout).
Use this only when the user wants to explore alternatives; cleanup itself stays read-only.

1. Frame the problem: constraints the new interface must meet, its dependencies and their category, and a rough sketch to make the constraints concrete.
2. Produce three or more radically different interfaces, in parallel sub-agents where available, each under one constraint: minimal (1-3 entry points), maximally flexible, trivial for the most common caller, or ports and adapters.
3. For each, give the interface (including invariants and error modes), a usage example, what hides behind the seam, the dependency strategy, and trade-offs.
4. Compare on depth, locality and seam placement, then recommend one, or a hybrid.
   Be opinionated rather than offering a menu.

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

- **Files** - which modules are involved
- **Problem** - why the current structure causes friction
- **Opportunity** - what deepening would look like (plain English, no code)
- **Test improvement** - what test is currently impossible that would
  become possible after deepening
