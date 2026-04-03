# Macro Architecture Patterns

System-level patterns that define how the entire system is physically or logically divided.

## Microservices

**Description:** Decomposes an application into a collection of small, independent services that communicate over a network.

**Characteristics:**
- Independent deployment and scaling
- Own database/schema (no shared tables)
- Inter-service communication via HTTP, gRPC, or messaging
- Each service owns its domain logic

**When to Use:**
- Team autonomy is critical
- Different services have different scaling needs
- Polyglot persistence required
- Fault isolation is high priority

**Warning Signs of Drift:**
- Shared databases between services
- Distributed transactions without saga pattern
- Tight coupling via shared libraries without versioning
- Services that can't be deployed independently

**Verification:**
- Each service has independent deployment pipeline
- Database schemas are isolated
- API contracts are versioned
- Services communicate via well-defined interfaces

---

## Modular Monolith

**Description:** A single-unit application (deployed as one) that is internally divided into independent, well-defined modules.

**Characteristics:**
- Single deployment unit
- In-process module boundaries (clear package structure)
- Modules communicate via well-defined interfaces
- Shared database (but clear schema ownership per module)

**When to Use:**
- Team size doesn't justify microservices overhead
- Network latency is unacceptable
- Simpler deployment/shipping desired
- Future migration path to microservices needed

**Warning Signs of Drift:**
- Cyclic dependencies between modules
- God modules consuming half the codebase
- Shared mutable state
- No clear module boundaries

**Verification:**
- Package structure reflects module boundaries
- Modules have narrow, well-defined public APIs
- No import cycles between modules
- Clear ownership per module (owned by same team)

---

## Service Communication Patterns

### Synchronous (Request-Response)
- REST APIs
- gRPC

### Asynchronous (Event-Driven)
- Message queues (RabbitMQ, Kafka)
- Event sourcing

### Choosing Between Them

| Factor | Sync | Async |
|--------|------|-------|
| Latency tolerance | Low | High |
| Coupling tolerance | Tight | Loose |
| Consistency requirement | Strong | Eventual OK |
| Complexity tolerance | Low | High |

---

## Pattern Selection Guidance

**Start with Modular Monolith** — Migrate to microservices only when:
- Team size exceeds 5-8 people per service
- Different scaling requirements emerge
- Polyglot needs arise
- Fault isolation becomes critical

**Avoid premature decomposition** — Most projects don't need microservices until they hit significant scale.
