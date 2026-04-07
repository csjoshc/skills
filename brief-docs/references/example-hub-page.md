# Example — hub and satellite shape

Illustrates the **brief-docs** pattern with a **fictional** doc tree. Replace names with your product's.

## Fictional hub (`docs/acme-api/README.md`)

```markdown
# Acme API (`docs/acme-api/`)

**Summary:** The dashboard calls only the **public API**; auth and billing secrets stay on server workers. Real-time updates use **SSE** on the chat endpoint.

**Run locally:** `docker compose up`, copy `.env.example` → `.env`.

**Code / entrypoints:** [`services/api/`](../services/api), [`apps/dashboard/`](../apps/dashboard).

**More detail:** [Architecture](architecture.md) · [Network](network.md) · [Ports](ports.md) · [Env](env.md)
```

What this shows:

- **`Summary:`** — Trust boundaries and main protocol in one paragraph.
- **`Run locally:`** — Commands and env file names only; no secret values.
- **Entrypoints** — Short list of repository paths (adjust depth to your layout).
- **`More detail:`** — One line of links to satellites.

## Fictional satellite (`docs/acme-api/network.md`)

- Opens with **Summary** (who calls whom, primary URLs).
- **Follow-up** links into source (handlers, clients) and notes edge cases.
- **At most one** small diagram if it clarifies topology.
- **See also** back to the hub.

## Takeaways

- **Hub** = orientation + links; avoid deep mechanics.
- **Satellite** = one concern + link back to hub.
- **Canonical** ports, env names, and URLs live on dedicated lookup pages; the hub does not duplicate full tables.

After behavior changes, update the relevant **Summary** first; put implementation detail in **Follow-up** and run through [accuracy-and-drift.md](accuracy-and-drift.md) before merge.
