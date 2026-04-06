# C3 Platform Context

## When to Use

If the PR modifies any C3 backend code — `.c3typ` files, Type definitions, `fetch()` / `evalMetric()` calls, server-side JavaScript actions, logger initialization (`PerLogger`), test setup (`Jasmine`, `TestApi`), or C3 platform patterns — query the **C3AI-MCP** server for platform-specific context before launching review agents.

## What Qualifies as C3 Backend Code

- `.c3typ` / `.c3doc` type definition files
- Server-side `.js` files using C3 APIs (`Type.fetch()`, `.merge()`, `.upsert()`, `Obj.make()`, `HttpRequest`, `ContentValue`, etc.)
- Test files using C3's `Jasmine` / `TestApi` harness
- `PerLogger` or `Log` logging calls
- `seed/` data files or `canonicalize` scripts
- C3 package metadata (`package.json` with `c3` dependencies)

## How to Use C3AI-MCP

- Query the MCP for documentation on any C3 API or Type referenced in the diff
- Use MCP-provided context to validate whether C3 API usage is correct (e.g., correct `fetch()` filter syntax, proper `spec` parameter conventions, valid Type method signatures)
- Pass relevant C3 platform context to the review agents alongside the standards

**Do NOT skip this step for backend changes** — C3 is a proprietary platform and general-purpose knowledge will not cover its APIs, Type system semantics, or runtime behavior.
