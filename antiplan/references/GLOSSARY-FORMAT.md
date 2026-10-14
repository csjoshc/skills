# GLOSSARY.md Format

Adapted from Matt Pocock's `domain-modeling` skill (MIT).
Loaded from [domain-model.md](domain-model.md).

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
A confirmed Customer request for one or more Items.
_Avoid_: Purchase, cart, basket

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Be opinionated.** When several words exist for one concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences. Define what it is, not what it does.
- **Project-specific terms only.** General programming concepts (timeouts, error types, utility patterns) stay out even if the project uses them heavily. Before adding a term, ask: is this unique to this context, or general programming? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. A flat list is fine for one cohesive area.

## Single vs multi-context repos

**Single context (most repos):** one `GLOSSARY.md` at the repo root.

**Multiple contexts:** a `GLOSSARY-MAP.md` at the repo root lists the contexts, where they live, and how they relate:

```md
# Glossary Map

## Contexts

- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders
- [Billing](./src/billing/GLOSSARY.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/GLOSSARY.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: shared types for `CustomerId` and `Money`
```

Infer which structure applies:

- If `GLOSSARY-MAP.md` exists, read it to find the contexts.
- If only a root `GLOSSARY.md` exists, it's a single context.
- If neither exists, create a root `GLOSSARY.md` lazily when the first term is resolved.

With multiple contexts, infer which one the current topic belongs to.
If that's unclear, add it to the next question round.
