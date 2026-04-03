# Domain-Driven Design Patterns

## Strategic DDD: Bounded Contexts

**Description:** Defines high-level boundaries that separate different subdomain responsibilities.

**Key Concepts:**
- **Bounded Context:** Explicit boundary where a particular domain model applies
- **Context Map:** Visual representation of bounded contexts and their relationships
- **Subdomain:** Business capability area (can be core, supporting, or generic)

**Relationships Between Contexts:**
- **Partnership:** Teams work together, synchronized development
- **Customer-Supplier:** Upstream provides, downstream consumes
- **Conformist:** Downstream conforms to upstream's model
- **Anti-Corruption Layer:** Adapter that translates between contexts
- **Open Host Service:** Published language for integration
- **Published Language:** Shared abstraction for communication

**When to Use:**
- Large codebase with distinct domain areas
- Multiple teams working on different parts
- Integrating with external systems
- Planning microservices decomposition

**Verification:**
- Each bounded context has clear ownership
- Models don't leak across boundaries
- Integration points are explicit
- Context map exists and is current

---

## Tactical DDD: Building Blocks

### Entities

**Description:** Objects with identity that persists beyond individual attribute values.

**Characteristics:**
- Unique identifier
- Mutable state
- Lifecycle continuity

**Example:**
```python
class Order:
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id
        self._items = []
        self._status = OrderStatus.DRAFT
    
    @property
    def id(self) -> OrderId:
        return self._id
```

**When to Use:** Objects that need identity tracking, lifecycle management

### Value Objects

**Description:** Immutable objects defined by their attributes, no identity.

**Characteristics:**
- Immutable
- No identifier
- Self-validating
- Equivalence by attribute values

**Example:**
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount must be non-negative")
```

**When to Use:** Measurements, coordinates, dates, any descriptive concept without identity

### Aggregates

**Description:** Cluster of related entities and value objects with a single root (Aggregate Root).

**Characteristics:**
- Single entry point (Aggregate Root)
- Invariants enforced within aggregate boundary
- Changes only via Aggregate Root
- Version/ETag for concurrency

**Example:**
```python
class OrderAggregate:
    def __init__(self, order_id: OrderId):
        self._root = Order(order_id)
        self._items = []
    
    def add_item(self, product_id: ProductId, quantity: int):
        # Invariant: max 10 items
        if len(self._items) >= 10:
            raise MaxItemsExceeded()
        self._items.append(OrderItem(product_id, quantity))
```

**When to Use:** Enforcing invariants across multiple entities

### Domain Events

**Description:** Something significant that happened in the domain.

**Characteristics:**
- Immutable
- Timestamped
- Contains relevant domain data
- Past tense naming

**Example:**
```python
@dataclass(frozen=True)
class OrderPlaced:
    order_id: OrderId
    customer_id: CustomerId
    total: Money
    timestamp: datetime
```

**When to Use:** Event-driven architectures, eventual consistency, audit trails

### Domain Services

**Description:** Operation that doesn't naturally fit within an entity or value object.

**Characteristics:**
- Stateless
- Complex operations spanning multiple aggregates
- No identity
- Named with verb

**Example:**
```python
class OrderPricingService:
    def calculate_total(self, items: list[OrderItem], discount: Discount) -> Money:
        subtotal = sum(item.price for item in items)
        return discount.apply(subtotal)
```

**When to Use:** Operations that don't belong to a single entity

### Repositories

**Description:** Collection-like interface for accessing aggregates.

**Characteristics:**
- Collection semantics (add, remove, get)
- Abstracts persistence
- Returns aggregates, not raw data
- Domain model, not infrastructure

**Example:**
```python
class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> OrderAggregate: ...
    def save(self, order: OrderAggregate) -> None: ...
    def delete(self, order_id: OrderId) -> None: ...
```

**When to Use:** Persistence needs for aggregates

### Factories

**Description:** Encapsulates complex object creation logic.

**Characteristics:**
- Handles complex construction
- May use builders
- Can be static or instance method

**When to Use:** Complex object creation, especially with invariants

---

## Applying DDD in Practice

### Project Structure (Hexagonal + DDD)

```
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── aggregates/
│   ├── events/
│   └── services/
├── application/
│   ├── commands/     # Write operations
│   ├── queries/     # Read operations
│   └── services/     # Application services
├── ports/
│   ├── inbound/
│   └── outbound/
└── adapters/
    ├── inbound/
    └── outbound/
```

### Common Pitfalls

1. **Anemic Domain Model** — Entities with no behavior (just getters/setters)
2. **False Aggregates** — Objects grouped without enforcing invariants
3. **Leaky Boundaries** — Domain model leaks across bounded contexts
4. **Anarchy** — No bounded context definitions
5. **Over-Engineering** — DDD patterns for simple CRUD

### When DDD Is Worth It

- Complex business rules
- Evolving domain (frequent changes)
- Large team with distinct domain areas
- Long-lived system (10+ years)
