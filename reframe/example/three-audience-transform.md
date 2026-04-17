# Three-Audience Transform Example

## Contents

- [Source Material](#source-material)
- [Exec Reframe](#exec-reframe)
- [Architect Reframe](#architect-reframe)
- [Engineer Reframe](#engineer-reframe)

---

## Source Material

Raw technical and business facts about a fictional migration project:

> **Project: Order Platform Migration**
>
> We are migrating from a monolithic Ruby on Rails API to an event-driven
> microservices architecture on Kubernetes. The current system handles 10K
> req/s with p99 latency of 200ms. Target: 50K req/s with p99 of 50ms.
>
> Key services: Order Service, Inventory Service, Payment Service, Notification
> Service. Communication via Kafka event bus with Schema Registry for contract
> enforcement. PostgreSQL per service (database-per-service pattern). Redis for
> caching and distributed locks.
>
> Risk: data consistency during migration — dual-write period where both old and
> new systems process orders. Mitigation: change data capture (CDC) via Debezium
> with idempotent consumers. Rollback: feature flags per service allow instant
> revert to monolith path.
>
> Timeline: 6 months. Phase 1 (months 1-2): extract Order Service. Phase 2
> (months 3-4): extract Inventory and Payment. Phase 3 (months 5-6): extract
> Notification, decommission monolith. Budget: $500K (infra + contractor support).
>
> Current pain points: deploy cycle is 4 hours (full monolith redeploy), scaling
> requires scaling everything, a single service failure takes down the entire
> platform, team velocity has dropped 40% in the last year due to merge conflicts
> and coupling.

---

## Exec Reframe

**Audience:** VP Engineering / CFO
**Arc:** Punchline-first
**Slide count:** 6

### Slide 1: Title
**Order Platform Modernization** — Faster releases, lower cost, higher reliability

### Slide 2: Recommendation
We recommend migrating our order platform from a single application to
independent services over 6 months for $500K.

**Why now:** Team velocity has dropped 40% in the past year. Every deployment
takes 4 hours. A single failure takes down the entire platform.

### Slide 3: Value / Impact
- **5x throughput capacity** — supports projected growth without proportional infra cost
- **4h → 15min deploy cycles** — faster feature delivery to customers
- **40% team velocity recovery** — fewer merge conflicts, independent team ownership
- **Fault isolation** — one service failure no longer takes down the platform

### Slide 4: Risk

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Data inconsistency during transition | High | Automated sync with instant rollback | In progress |
| Timeline overrun | Medium | Phased approach — value delivered each phase | Mitigated |
| Team ramp-up on new stack | Low | Contractor support included in budget | Mitigated |

### Slide 5: Timeline
- **Months 1-2:** First service extracted. Deploy time drops to 1 hour.
- **Months 3-4:** Core services migrated. Independent scaling enabled.
- **Months 5-6:** Migration complete. Old system decommissioned.

### Slide 6: The Ask
**Approve $500K budget and dedicated team allocation for 6 months.**
Next step: Kickoff meeting by end of month. Decision needed by April 30.

### Parking Lot
*Cut for this audience:* Kafka, CDC, Debezium, Schema Registry, database-per-service
pattern, Redis caching, Kubernetes details, idempotent consumers, feature flag
implementation. Available in architect and engineer versions.

---

## Architect Reframe

**Audience:** Solution Architect / Staff Engineer
**Arc:** Tradeoff-first
**Slide count:** 9

### Slide 1: Title
**Order Platform — Monolith to Event-Driven Services** — Architecture Review

### Slide 2: Context & Constraints
- **Driver:** 40% velocity drop, 4h deploy cycles, no fault isolation
- **Constraints:** Zero-downtime migration, maintain data consistency, 6-month timeline
- **Key quality attributes:** Latency (p99 < 50ms), throughput (50K req/s), availability (99.95%)

### Slide 3: Options / Tradeoff Matrix

| Criterion | Strangler Fig + Events | Big Bang Rewrite | Modular Monolith |
|-----------|----------------------|-----------------|-----------------|
| Migration risk | Low (incremental) | High (all-or-nothing) | Low |
| Target throughput | 50K req/s | 50K req/s | 20K req/s |
| Team independence | Full | Full | Partial |
| Operational complexity | High (distributed) | High (distributed) | Low |
| Timeline | 6 months | 9-12 months | 3 months |
| Rollback capability | Per-service | None | N/A |

**Recommended: Strangler Fig + Events** — incremental risk, per-service rollback,
meets all NFR targets.

### Slide 4: Target Architecture
*(Embed component diagram — see diagram-patterns.md for Mermaid template)*

Four bounded contexts: Order, Inventory, Payment, Notification. Kafka event bus
for async communication. Schema Registry for contract enforcement.
Database-per-service (PostgreSQL). Redis for caching and distributed locks.
API Gateway fronting all services.

### Slide 5: System Boundaries
- **Ours:** Order, Inventory, Payment, Notification services + Kafka cluster
- **External:** Payment gateway (Stripe), notification providers (email/SMS)
- **Trust boundary:** API Gateway handles auth; inter-service communication is trusted network
- **Data ownership:** Each service owns its PostgreSQL instance. No shared databases.

### Slide 6: Integration Points
- **Sync:** REST between API Gateway and services (p99 < 20ms internal)
- **Async:** Kafka topics per domain event (OrderPlaced, InventoryReserved, PaymentProcessed)
- **Contracts:** Avro schemas in Schema Registry, backward-compatible evolution
- **Legacy bridge:** CDC via Debezium during dual-write period

### Slide 7: Migration Strategy
- **Phase 1:** Extract Order Service via strangler fig. Monolith proxies to new service.
  CDC syncs order data bidirectionally. Feature flag controls routing.
- **Phase 2:** Extract Inventory + Payment. Event-driven choreography replaces
  synchronous monolith calls.
- **Phase 3:** Extract Notification. Decommission monolith. Remove CDC bridge.
- **Rollback:** Feature flags per service allow instant revert to monolith path.

### Slide 8: Risks & Open Questions
- **Dual-write consistency:** CDC + idempotent consumers mitigate, but edge cases
  during high-load periods need load testing
- **Kafka operational maturity:** Team has no production Kafka experience — contractor
  support planned for months 1-3
- **Schema evolution:** Backward-compatible only? Or allow breaking changes with versioned topics?
- **Observability:** Distributed tracing strategy not yet defined

### Parking Lot
*Cut for this audience:* Budget details, ROI calculations, team velocity metrics
(exec concerns). Implementation-level details like consumer group configs, Redis
lock TTLs, specific API payloads (engineer concerns).

---

## Engineer Reframe

**Audience:** Backend engineers implementing the migration
**Arc:** Mechanism-first
**Slide count:** 10

### Slide 1: Title
**Order Platform Migration — Implementation Guide**

### Slide 2: What It Does
- Extracts 4 services from the Rails monolith: Order, Inventory, Payment, Notification
- Introduces Kafka event bus for inter-service communication
- Database-per-service with PostgreSQL; Redis for caching and distributed locks
- CDC via Debezium for dual-write consistency during migration

### Slide 3: How It Works
*(Embed sequence diagram — see diagram-patterns.md for Mermaid template)*

Order creation flow (post-migration):
1. Client → API Gateway: `POST /v1/orders {items, userId, paymentMethod}`
2. API Gateway → Order Service: forward with auth context
3. Order Service → PostgreSQL: `INSERT INTO orders` (status: PENDING)
4. Order Service → Kafka: publish `OrderPlaced {orderId, items, userId}`
5. Inventory Service consumes `OrderPlaced` → reserve stock → publish `InventoryReserved`
6. Payment Service consumes `InventoryReserved` → charge → publish `PaymentProcessed`
7. Order Service consumes `PaymentProcessed` → update status to CONFIRMED
8. Notification Service consumes `PaymentProcessed` → send confirmation email

### Slide 4: Components

| Component | Responsibility | Tech Stack | Repo Path |
|-----------|---------------|-----------|-----------|
| Order Service | Order lifecycle, saga orchestration | Kotlin + Spring Boot | `services/order/` |
| Inventory Service | Stock management, reservation | Kotlin + Spring Boot | `services/inventory/` |
| Payment Service | Payment processing, refunds | Kotlin + Spring Boot | `services/payment/` |
| Notification Service | Email, SMS, push | Python + FastAPI | `services/notification/` |
| API Gateway | Routing, auth, rate limiting | Kong | `infra/kong/` |
| CDC Bridge | Dual-write sync during migration | Debezium + Kafka Connect | `infra/debezium/` |

### Slide 5: Interfaces / Contracts
**REST (API Gateway → Services):**
```
POST /v1/orders         → Order Service
GET  /v1/orders/:id     → Order Service
POST /v1/inventory/reserve → Inventory Service
POST /v1/payments/charge   → Payment Service
```

**Kafka Topics & Schemas (Avro):**
- `order.placed` — `{orderId: string, items: Item[], userId: string, timestamp: long}`
- `inventory.reserved` — `{orderId: string, reservationId: string, status: enum}`
- `payment.processed` — `{orderId: string, transactionId: string, amount: decimal}`

Schema evolution: backward-compatible only. New fields must have defaults.

### Slide 6: Data Flow
*(Embed data flow diagram)*

Order data lifecycle: API request → validated order → persisted to PostgreSQL →
event published to Kafka → consumed by downstream services → saga state updated
→ final status written back → cached in Redis (TTL: 5min) for read path.

### Slide 7: Failure Modes

| Failure | Detection | Recovery | Blast Radius |
|---------|-----------|----------|-------------|
| Kafka unavailable | Health check + consumer lag alert | Retry with exponential backoff, DLQ after 3 attempts | Orders stuck in PENDING |
| Inventory reservation timeout | 30s timeout + circuit breaker | Release reservation after TTL, compensating event | Single order |
| Payment failure | Stripe webhook + polling | Publish `PaymentFailed`, trigger inventory release | Single order |
| CDC lag during dual-write | Debezium lag metric > 5s | Alert, pause new migrations, let CDC catch up | Data inconsistency window |
| Database failover | PgBouncer health check | Automatic failover to replica, ~30s downtime | Single service |

All consumers must be **idempotent** — deduplicate by `eventId` in a processed-events table.

### Slide 8: Operational Concerns
- **Monitoring:** Prometheus + Grafana. Key metrics: consumer lag, p99 latency per service,
  error rate, saga completion rate
- **Distributed tracing:** OpenTelemetry with Jaeger. Trace ID propagated via Kafka headers
- **Scaling:** HPA on CPU/memory. Kafka partitions = 2x expected consumer instances
- **Deployment:** ArgoCD GitOps. Canary deploys with 5% → 25% → 100% traffic shift
- **Feature flags:** LaunchDarkly. Per-service routing: `order.use_new_service: boolean`

### Slide 9: Implementation Notes
- **Consumer group IDs:** `{service-name}-{environment}` (e.g., `inventory-prod`)
- **Redis lock TTL:** 30s for inventory reservations, 60s for payment idempotency
- **Schema Registry URL:** `schema-registry.internal:8081`
- **Gotcha:** Debezium requires `wal_level=logical` on PostgreSQL — coordinate with DBA
- **Gotcha:** Kafka consumer rebalance during deploy — use cooperative-sticky assignor
- **Testing:** Contract tests via Pact for all Kafka schemas. Integration tests against
  Testcontainers (Kafka + PostgreSQL)

### Slide 10: Getting Started
```bash
# Clone and set up local environment
git clone git@github.com:org/order-platform.git
cd order-platform
make setup          # starts Kafka, PostgreSQL, Redis via docker-compose
make migrate        # runs all database migrations
make test           # runs unit + integration tests
make run-order      # starts Order Service on :8080
```

### Parking Lot
*Cut for this audience:* Business justification, ROI, budget details (exec concerns).
Architecture option comparison, NFR targets, governance (architect concerns).
