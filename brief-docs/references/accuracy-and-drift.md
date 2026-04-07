# Accuracy and drift prevention

Use this checklist when authoring or reviewing brief docs so they stay aligned with the product.

## Tie claims to source

- **APIs:** Field names and routes match **OpenAPI**, route handlers, or client types—not memory.
- **Events / wire format:** SSE or WebSocket **event type** strings match serializers, shared DTOs, or client parsers (grep the codebase for the literal type names).
- **Env vars:** Names match **settings modules**, `env.example`, or deployment manifests.
- **Ports:** Match **start scripts**, `docker-compose`, or server bind config.

## Remove obsolete product behavior

- Delete paths to **removed** services, packages, or flags (grep the codebase; if symbol is gone, doc must not reference it).
- Replace “optional alternate stack” prose with **either** current default **or** a single “legacy” footnote if migration is in flight.

## Naming consistency

- Prefer the same **canonical term** as the public API or wire format in examples—not an internal-only field name unless documenting internals.
- When code and UI differ, document **wire/API** first; note UI label in Follow-up if needed.

## Duplication = drift risk

- If two pages define the same table, **one** is wrong within weeks. Pick **one canonical** page; elsewhere use **one line + link**.

## Secrets and compliance

- Document **variable names** and **where** to set them; never example **real** tokens, keys, or PII.
- Call out **dev-only** debug flags and that they must not run in production with sensitive data.

## Review cadence

- After a **large PR** touching APIs, services, or client protocol: grep the doc tree for stale **service names**, **ports**, **routes**, and **event or message types** changed in the PR.
