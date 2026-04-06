# Layer Ownership

## Domain Layer
- **Purpose:** Pure business logic, business rules
- **Dependencies:** Standard library only
- **No:** Database calls, HTTP requests, file I/O, external APIs
- **Examples:** `TaskRecord`, `TaskState`, validation logic, business calculations

## Service Layer
- **Purpose:** Orchestration, business workflows
- **Dependencies:** Domain layer + infrastructure (DB, HTTP, files)
- **Responsibilities:** Transaction management, error handling, logging
- **Examples:** `generation_service.py`, `batch_service.py`

## Application Layer (if used)
- **Purpose:** Adapters for external interfaces
- **Dependencies:** Service layer + frameworks
- **Responsibilities:** HTTP handlers, CLI commands, message queue consumers
- **Examples:** FastAPI route handlers, CLI commands

## Infrastructure Layer
- **Purpose:** External system adapters
- **Dependencies:** Frameworks, drivers, SDKs
- **Responsibilities:** Database access, HTTP clients, file operations
- **Examples:** Database repositories, ComfyUI client, S3 client
