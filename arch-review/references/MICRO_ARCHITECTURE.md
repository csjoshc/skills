# Micro Architecture Patterns

Code-level patterns that define how code is organized within a single service or module.

## Hexagonal Architecture (Ports and Adapters)

**Description:** Separates core business logic from external technologies using interfaces (ports) and implementations (adapters).

**Key Concepts:**
- **Domain/Core:** Pure business logic, no dependencies on external frameworks
- **Ports:** Interfaces that define how the domain interacts with the outside world
- **Adapters:** Implementations that connect to external concerns (DB, HTTP, UI)

**Structure:**
```
src/
├── domain/           # Pure business logic
│   ├── entities/
│   ├── value_objects/
│   └── services/
├── ports/            # Interfaces
│   ├── inbound/      # Use case interfaces
│   └── outbound/     # Repository, external service interfaces
└── adapters/         # Implementations
    ├── inbound/      # HTTP controllers, CLI
    └── outbound/     # Database, external APIs
```

**When to Use:**
- Testability is critical
- Need to swap external dependencies (e.g., DB)
- Complex business logic that should be framework-agnostic
- Long-lived system with evolving external dependencies

**Warning Signs of Drift:**
- Business logic imports external frameworks
- Controllers contain business logic
- Direct database calls in domain services
- No clear separation of inbound/outbound concerns

**Verification:**
- Domain layer has zero external dependencies
- All I/O goes through ports
- Adapters implement port interfaces
- Can test domain logic without any infrastructure

---

## Vertical Slices

**Description:** A feature-centric approach where code is organized by functionality rather than technical layers.

**Structure:**
```
features/
├── create_order/
│   ├── create_order.py      # Feature logic (all layers)
│   ├── create_order_test.py
│   └── schemas.py           # Feature-specific types
├── cancel_order/
│   ├── cancel_order.py
│   ├── cancel_order_test.py
│   └── schemas.py
└── shared/
    └── ...                  # Shared utilities
```

**When to Use:**
- Feature teams work independently
- Minimize cross-feature coordination
- Faster development cycles per feature
- Simpler navigation (all code for feature in one place)

**Warning Signs of Drift:**
- Technical layering (controllers/, services/, repos/) mixed with features
- Feature code scattered across layers
- Changes require touching multiple directories
- Duplicated logic between feature slices

**Verification:**
- Each feature directory contains all needed code
- No cross-feature import chains
- Feature-specific types co-located
- Tests mirror feature structure

---

## Layered Architecture

**Description:** Traditional separation into UI, Business Logic, and Data Access layers.

**Structure:**
```
src/
├── ui/           # Controllers, views, presenters
├── application/  # Use cases, orchestration
├── domain/       # Entities, business rules
└── infrastructure/  # DB, external services
```

**When to Use:**
- Simple CRUD applications
- Team familiarity
- Well-understood domain

**Warning Signs of Drift:**
- Business logic in controllers
- Domain layer depends on infrastructure
- No clear responsibility boundaries
- God classes spanning layers

---

## Pattern Comparison

| Aspect | Hexagonal | Vertical Slices | Layered |
|--------|-----------|-----------------|---------|
| Change impact | Feature needs adapter updates | Feature in one place | Cross-layer changes |
| Testability | Excellent (pure domain) | Good (feature-contained) | Moderate |
| Learning curve | Higher | Medium | Lower |
| Best for | Complex domains | Feature teams | Simple CRUD |

## Choosing Between Patterns

**Hexagonal:** Complex business logic, testability priority, framework independence needed

**Vertical Slices:** Feature teams, rapid development, clear feature ownership

**Layered:** Simple applications, team familiarity, CRUD-heavy

**Recommendation:** Default to Vertical Slices for most new projects. Use Hexagonal when domain complexity justifies it.
