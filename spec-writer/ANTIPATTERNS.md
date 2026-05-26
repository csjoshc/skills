# Code Antipatterns

## Contents

- File/Module Antipatterns
- API/Endpoint Antipatterns
- Testing Antipatterns
- General Anti-patterns
- Decision Checklist
- Quick Reference


A catalog of common antipatterns to avoid when writing specs and plans. Use this as a checklist during spec review.

---

## File/Module Antipatterns

### God Class / God File
**Definition:** A single file with 500+ lines containing multiple unrelated responsibilities.

**Examples:**
- `api_types.py` with 50+ unrelated Pydantic DTOs
- `server.py` with all API routes + middleware + lifecycle + helpers

**Impact:** Hard to navigate, test in isolation, review, and merge.

**Refactor pattern:** Split by domain — DTOs go to `api/dto/batches.py`, routes go to `api/routes/batches.py`.

---

### Mixed Concerns (SRP Violation)
**Definition:** A module handles unrelated responsibilities that should belong to different layers.

**Examples:**
- `config.py` mixing hardware detection, model presets, and session config loading
- Route handlers containing business logic + HTTP response building

**Impact:** Unclear ownership, cascade changes when one concern evolves.

**Refactor pattern:** Separate into layers — `config/hardware.py`, `config/presets.py`, `services/batch_service.py`.

---

### Flat Architecture
**Definition:** All modules in a single flat directory with no layer separation.

**Impact:** Tight coupling, difficult to isolate changes, no clear import contracts.

**Refactor pattern:**
```
src/
├── api/           # HTTP layer (routes, DTOs)
├── services/      # Business logic
├── domain/        # Domain models, entities
└── infrastructure/# External clients, persistence
```

---

### Duplicate Code
**Definition:** Identical or near-identical code appears in multiple places.

**Examples:**
- Same test suite in `tests/` and `project_export/tests/`
- Repeated validation logic in multiple endpoints

**Impact:** Wasted maintenance, inconsistent behavior.

**Refactor pattern:** Extract to shared module, use test fixtures.

---

### Hidden Constants
**Definition:** Hardcoded values scattered across modules instead of centralized configuration.

**Examples:**
- API endpoint paths duplicated in route files
- Default values repeated in multiple services

**Impact:** Fragile, difficult to configure, easy to introduce inconsistencies.

**Refactor pattern:** Centralize in `config/` or `constants.py`.

---

### Blob Data Classes
**Definition:** Dataclasses with 25+ fields doing multiple things.

**Impact:** Hard to reason about, test in isolation, extend.

**Refactor pattern:** Split into focused value objects — `GenerationConfig`, `BatchConfig`, `SessionConfig`.

---

## API/Endpoint Antipatterns

### Route Monolith
**Definition:** Single file containing all API route handlers (500+ lines).

**Impact:** Impossible to review, constant merge conflicts, no isolation for testing.

**Refactor pattern:** Extract routes to `api/routes/{resource}.py`, import into main app.

---

### DTO Explosion in Single File
**Definition:** 40+ Pydantic models in one `api_types.py` file.

**Impact:** Hard to navigate, understand relationships, find relevant DTOs.

**Refactor pattern:** Split by domain:
```
api/dto/
├── wildcards.py   # WildcardGraphDTO, WildcardOptionDTO, etc.
├── batches.py    # BatchSummaryDTO, BatchDetailDTO, etc.
└── generation.py  # GenerateRequestDTO, ProgressDTO, etc.
```

---

### Service Logic in Route Handlers
**Definition:** Business logic embedded directly in route functions.

**Impact:** Hard to test, impossible to reuse, route files bloat.

**Refactor pattern:** Call service functions — route does HTTP, service does logic.

---

## Testing Antipatterns

### Duplicate Test Suites
**Definition:** Same tests replicated in multiple test directories.

**Impact:** Confusion, wasted maintenance, inconsistent results.

**Refactor pattern:** Single `tests/` directory with proper structure.

---

### Fat Integration Tests
**Definition:** Integration tests that do too much, spanning multiple subsystems.

**Impact:** Brittle, slow, hard to diagnose failures.

**Refactor pattern:** Unit tests for logic, lean integration tests for wiring.

---

## Deploy-time Antipatterns (container / helm / k8s tickets)

### Source-only Verification on a Running-Container Artifact
**Definition:** Ticket ACs verify only source files (`grep`, `helm lint`, `helm template --validate`) for an artifact whose runtime is a container or pod. Deploy-time bugs (CrashLoopBackOff, port-bind denied under non-root, NetworkPolicy zero-match) ship to the cluster because `helm lint` PASS was treated as deploy proof.

**Examples (from `ui-ghcr-publish`):**
- `helm lint` PASS but pod CrashLoops on `cp` over an existing base-image file
- `helm template` renders a NetworkPolicy that matches zero pods because `namespaceSelector` keys on an unset label
- `readOnlyRootFilesystem: true` + script writing outside emptyDir mounts

**Impact:** Deploy-time outages caught after merge; cycle gate stopwatches overflow; rollback required.

**Fix pattern:** Apply the three Deploy-time AC conventions in `SKILL.md` — `helm install --wait` deploy-smoke AC, base-image Read-First on entrypoint write paths, NetworkPolicy cross-pod reachability + namespace-label setup. Cross-referenced with `ticket-critic` patterns 11/12/13.

---

## General Anti-patterns

### Circular Dependencies
**Definition:** Module A imports B, which imports C, which imports A.

**Impact:** Import errors, hard to test in isolation, fragile refactoring.

**Refactor pattern:** Dependency injection, clear layer contracts.

---

### Feature Envy
**Definition:** A function/method more interested in another class's data than its own.

**Impact:** Tight coupling, hard to reuse, violates encapsulation.

**Refactor pattern:** Move function to the class it envies.

---

## Decision Checklist

When reviewing a spec, ask:

| Question | Threshold |
|----------|-----------|
| Any file will exceed 300 lines after this change? | Trigger refactoring |
| Multiple unrelated DTOs in one file? | Split by domain |
| Route handler > 100 lines? | Extract to service |
| Test file duplicated elsewhere? | Consolidate |
| Hardcoded values repeated 3+ times? | Centralize |
| Dataclass has 20+ fields? | Consider splitting |

---

## Quick Reference

| Antipattern | Trigger Size | Solution |
|-------------|-------------|----------|
| God File | > 500 lines | Split by domain |
| Route Monolith | > 1000 lines | Extract routes |
| DTO File | > 30 models | Split by resource |
| Service Module | > 300 lines | Split by operation |
| Test File | > 500 lines | Split by feature |
| Dataclass | > 20 fields | Split into value objects |

---

*This file is a companion to SKILL.md. Update it as new antipatterns are discovered in your codebase.*
