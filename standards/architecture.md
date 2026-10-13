# Architecture Decisions

## API Pattern
- **Default:** REST with JSON responses
- **Endpoint structure:** `/api/{domain}/{action}` or `/api/{resource}/{id}`
- **Error format:** `{error: string, details?: object}`
- **Status codes:** 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation error), 500 (server error)

## Authentication & Authorization
- **Auth mechanism:** JWT via `Authorization: Bearer <token>` header
- **Session storage:** Stateless JWT (no server-side sessions)
- **Role-based access:** `is_admin` role for admin endpoints
- **Rate limiting:** 100 requests/minute per user (adjust per project)

## Data Layer
- **Database:** PostgreSQL (default), SQLAlchemy ORM
- **Migrations:** Alembic (Python) or Prisma (Node)
- **Connection pooling:** Use framework defaults unless performance requires tuning

## Testing Strategy
- **Backend:** pytest (Python) / Vitest (Node)
- **Frontend:** Vitest + React Testing Library
- **E2E:** Playwright (preferred) or Cypress
- **Coverage targets:** 80% line coverage for new code, 70% for refactors
- **Test structure:** Co-develop tests with implementation (TDD where specified)

## Code Organization

**Backend structure:**
```
src/
├── api/
│   ├── routes/      # HTTP endpoint handlers
│   ├── dto/         # Data transfer objects (Pydantic models)
│   └── helpers.py   # Shared helper functions
├── domain/          # Pure business logic (no external deps)
├── services/        # Orchestration, calls domain + infrastructure
├── config/          # Configuration loading
└── models/          # Database models
```

**Frontend structure:**
```
react-app/src/
├── components/  # Reusable UI components
├── pages/       # Route-level components
├── hooks/       # Custom React hooks
├── stores/      # State management (Zustand, Redux, etc.)
├── api/         # API client functions
└── types/       # TypeScript types
```

## File Size Limits
- **Soft limit:** 300 lines (proactively suggest refactoring)
- **Hard limit:** 500 lines (must refactor before merging)
- **Exceptions:** DTO files, generated code, test fixtures

## Fractal module layout (optional, library-style units)

When a unit is meant to be independently testable (or extractable), co-locate its support set rather than scattering types/mocks across shared buckets:

```
component/
├── interface.*     # owned types + contracts
├── guard.*         # runtime guards (+ guard tests)
├── mocks.*         # canonical factories / doubles for consumers
├── *.test.*        # unit behavior
├── component.*     # implementation
├── provides.*      # public exports (optional barrel)
└── *.integration.* # producer→subject→consumer when at a boundary
```

Prefer this when DI and consumer mocks matter; keep the simpler tree above for thin app code. Details: `tdd/INTERFACE_DESIGN.md`, `tdd/MOCKING.md`.

## Module support set (when co-locating)
For library-style or heavily DI'd units, keep interface/guards/canonical mocks/tests with the source file (see Fractal module layout above and `tdd/INTERFACE_DESIGN.md`). Do not orphan type-only tickets — attach type/guard edits to the first consuming source-file task.

## Error handling (pass-through)
- Prefer explicitly typed errors at boundaries.
- Do not swallow, store-and-forget, or rewrite errors into unrelated types to "keep going."
- Surface the original failure (or a typed wrap that **preserves** cause/context) so it can be fixed.
- One error value ≈ one specific failure mode.

## Optional exported-function shape (TypeScript / strict DI)
For new **exported** functions that must stay testable: split Deps / Params / Payload and return `Success | Error`. Internal helpers exempt; do not mass-convert existing code without a ticket.
