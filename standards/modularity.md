# Modularity vocabulary

Shared terms for reasoning about module depth, cited by `cleanup`
(ARCHITECTURE_DEPTH.md) and `pr-review` (Modularity lens). One definition, so
review and audit use the same words. Rooted in Ousterhout's *Philosophy of
Software Design* and Feathers' seam.

Use these terms exactly. Say module, interface, seam or adapter rather than
"component", "service", "API" or "boundary".

| Term | Definition |
|------|-----------|
| **Module** | Anything with an interface and an implementation, at any scale: function, class, package, tier-spanning slice |
| **Interface** | Everything a caller must know to use the module correctly: type signature, invariants, ordering, error modes, required config, performance |
| **Implementation** | The code inside the module. Distinct from adapter: a small adapter can have a large implementation, and the reverse |
| **Depth** | Leverage at the interface: behaviour a caller or test can exercise per unit of interface learned. Deep = lots behind a small interface. Shallow = interface nearly as complex as the implementation |
| **Seam** | Where an interface lives; a place behaviour can be altered without editing in place (Feathers) |
| **Adapter** | A concrete thing satisfying an interface at a seam. Names a role, not a substance |
| **Leverage** | What callers get from depth: one implementation pays back across N call sites and M tests |
| **Locality** | What maintainers get from depth: change, bugs, knowledge and verification concentrate in one place |

Depth is measured as leverage, not as a ratio of implementation lines to
interface lines, which would reward padding.

## Why it matters for agents

Deep modules produce fewer structure-sensitive tests: when behaviour hides
behind a small interface, tests written at that interface exercise behaviour,
not file layout, so they survive refactors. Shallow modules push detail into
the interface, and tests written there couple to structure and break on
reformatting. Locality (a change ripples a short distance) and leverage (a
caller gets a lot from a small interface) are good for codebases and good for
agents working in them.

## Core principles

- **Depth is a property of the interface, not the implementation.** A deep
  module can be built from small swappable parts, as long as they stay out of
  the interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes,
  it was a pass-through. If complexity reappears across N callers, it earned
  its keep.
- **The interface is the test surface.** Callers and tests cross the same
  seam. Wanting to test past the interface means the module is the wrong shape.
- **One adapter means a hypothetical seam, two adapters means a real one.**
  Introduce a seam only when something actually varies across it, typically
  production plus test.
