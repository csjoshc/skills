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
