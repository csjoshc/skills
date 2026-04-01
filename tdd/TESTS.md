# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```typescript
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Characteristics:
- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```typescript
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Red flags:
- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```typescript
// BAD: Bypasses interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: Verifies through interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

## Test Naming

Good test names describe behavior:

| Bad (HOW) | Good (WHAT) |
|-----------|-------------|
| `test_checkout_calls_payment` | `test_checkout_succeeds_with_valid_card` |
| `test_user_controller_validates_email` | `test_rejects_invalid_email_format` |
| `test_order_service_calculates_total` | `test_total_includes_tax_and_shipping` |

---

## Test Antipatterns

### Structure Antipatterns

| Antipattern | Trigger | Solution |
|-------------|---------|----------|
| God Test File | > 500 lines | Split by feature |
| Duplicate Suites | Same tests in 2 dirs | Consolidate to one location |
| No Assertions | `assert` missing | Add meaningful assertions |
| Over-Mocking | Mocking internal classes | Test through public API |
| Multi-Behavior | > 3 assertions per test | Split into separate tests |
| Fat Fixtures | Excessive setup (> 20 lines) | Create focused fixtures |
| Conditional Logic | `if`/`else` in tests | Split into separate tests |
| Dry-Run Dependency | Always `backend="dry_run"` | Use real backend for feature tests |

### Naming Antipatterns

| Bad | Good |
|-----|------|
| `test_checkout_calls_payment_gateway` | `test_checkout_succeeds_with_valid_card` |
| `test_user_validation_regex` | `test_rejects_invalid_email_format` |
| `test_1()`, `test_process()` | `test_rejects_negative_quantity()` |

### Logic Antipatterns

**Test without assertions:**
```python
# BAD
def test_something():
    process_data()  # No assertions!

# GOOD
def test_something():
    result = process_data()
    assert result.status == "completed"
```

**Testing multiple things:**
```python
# BAD - too much!
def test_order_processing():
    # Creates order, validates inventory, charges payment, sends email

# GOOD - one thing per test
def test_order_creation_returns_order_id(): ...
def test_order_charges_payment(): ...
def test_order_sends_confirmation_email(): ...
```

**Dry-run dependency:**
```python
# BAD - Always using dry-run for feature tests
def test_generation():
    init_pipeline(backend="dry_run")
    result = generate_image(params)
    assert result is not None  # Doesn't verify real generation

# GOOD - Use real backend for feature verification
def test_generation():
    init_pipeline(backend="comfyui")
    result = generate_image(params)
    assert result is not None
    assert result.size == expected_size
```

---

## Frontend Component Testing

### Testing Library Patterns

```typescript
// src/components/__tests__/GenerationForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GenerationForm } from '../GenerationForm';

jest.mock('../PersonPanel', () => ({
  PersonPanel: ({ onChange }: any) => (
    <button onClick={() => onChange({ mode: 'reference' })}>Set Person</button>
  )
}));

test('submits generation request', async () => {
  const onSubmit = jest.fn();
  render(<GenerationForm onSubmit={onSubmit} />);
  
  await userEvent.click(screen.getByText('Set Person'));
  await userEvent.click(screen.getByLabelText(/submit/i));
  
  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      person_mode: 'reference'
    }));
  });
});

test('shows validation errors', async () => {
  render(<GenerationForm onSubmit={jest.fn()} />);
  
  await userEvent.click(screen.getByRole('button', { name: /submit/i }));
  
  expect(screen.getByText(/person mode is required/i)).toBeInTheDocument();
});
```

### SSE/EventSource Testing

```typescript
// src/api/__tests__/useSSEStream.test.ts
import { renderHook, act } from '@testing-library/react';
import { useEffect } from 'react';

function createMockEventSource() {
  return {
    onmessage: null, onerror: null, onopen: null,
    close: jest.fn(), readyState: 1 // OPEN
  };
}

beforeEach(() => {
  global.EventSource = jest.fn().mockImplementation(createMockEventSource);
});

test('connects to SSE endpoint', () => {
  const { result } = renderHook(() => useSSEStream('test-batch-123'));
  expect(EventSource).toHaveBeenCalledWith(
    '/api/generate/stream?batchId=test-batch-123'
  );
});
```

---

## Backend Async/Streaming Tests

### SSE Streaming with httpx

```python
import httpx
import pytest
import json

@pytest.mark.asyncio
async def test_sse_stream_opens():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://testserver/api/generate/stream?batchId=test123") as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"

@pytest.mark.asyncio
async def test_sse_preview_events():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://testserver/api/generate/stream?batchId=test123") as response:
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    events.append(json.loads(line[5:]))
            assert any(e.get("event") == "preview" for e in events)
```

### Event Buffer Testing

```python
import pytest
from src.sse_buffer import EventBuffer

class TestEventBuffer:
    def test_add_and_get_events(self):
        buffer = EventBuffer(max_events=50, ttl_seconds=3600)
        buffer.add_event("batch1", {"type": "preview", "data": "test"})
        buffer.add_event("batch1", {"type": "status", "data": "progress"})
        events = buffer.get_events_since("batch1", after_index=0)
        assert len(events) == 2
    
    def test_max_events_eviction(self):
        buffer = EventBuffer(max_events=3, ttl_seconds=3600)
        for i in range(5):
            buffer.add_event("batch1", {"index": i})
        events = buffer.get_events_since("batch1", after_index=-1)
        assert len(events) == 3
        assert events[-1]["index"] == 4
```
