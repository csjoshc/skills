# CI/CD and Test Execution

## Contents

- Running Tests
- Coverage Targets
- Test Markers
- CI Configuration
- Test Fixtures Reference


Reference for running tests locally and in CI pipelines.

---

## Running Tests

### Backend (pytest)

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# Specific file
pytest tests/test_generation_jobs.py -v

# Skip slow/integration tests
pytest -m "not slow and not integration"

# Run only fast unit tests
pytest -m "not integration"
```

### Frontend (Vitest)

```bash
# All tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific file
npm test -- src/api/__tests__/bootstrap.test.ts
```

---

## Coverage Targets

| Module | Target |
|--------|--------|
| `server.py` | ≥80% |
| `api_types.py` | ≥80% |
| `generation_tasks.py` | ≥80% |
| `sse_buffer.py` | ≥80% |
| `api/` (frontend) | ≥70% |
| `components/` (frontend) | ≥70% |

### Backend Coverage Enforcement

```bash
# Generate HTML report
pytest --cov=src --cov-report=html tests/

# Open in browser
open htmlcov/index.html

# Fail CI if below threshold
pytest --cov=src --cov-fail-under=80 tests/
```

### Frontend Coverage Configuration

```typescript
// vite.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70
      }
    }
  }
});
```

---

## Test Markers

### pytest.ini Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
markers = [
    "integration: marks tests as integration tests (requiring ComfyUI)",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

### Marking Tests

```python
# Skip integration tests by default
@pytest.mark.integration
def test_with_comfyui():
    """Requires running ComfyUI instance."""
    pass

# Skip slow tests
@pytest.mark.slow
def test_full_pipeline():
    """Full generation pipeline test."""
    pass
```

---

## CI Configuration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run backend tests
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-fail-under=80 \
            -m "not integration and not slow"
      
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install frontend dependencies
        run: npm ci
      
      - name: Run frontend tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Fixtures Reference

### Backend Fixtures

| Fixture | Purpose | Location |
|---------|---------|----------|
| `tmp_path` | Isolated temp directory | Built-in pytest |
| `monkeypatch` | Patch module-level values | Built-in pytest |
| `hw_config` | HardwareConfig for testing | `tests/test_pipeline.py` |
| `params` | GenerationParams for testing | `tests/test_pipeline.py` |
| `temp_wildcards` | Temporary wildcard files | `tests/test_session_runner.py` |
| `batch_setup` | Batch directory setup | `tests/test_batch_service.py` |

### Frontend Fixtures

| Fixture | Purpose | Location |
|---------|---------|----------|
| `server` (MSW) | HTTP request interception | `src/api/__tests__/mocks/server.ts` |
| `handlers` | API response handlers | `src/api/__tests__/mocks/handlers.ts` |
| `Wrapper` | QueryClient wrapper | Per-test-file |
| `mockEventSource` | SSE mock | Per-test-file |
