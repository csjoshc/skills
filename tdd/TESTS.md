# Good and Bad Tests

## Contents

- Good Tests
- Bad Tests
- Test Naming
- Frontend Component Testing
- Backend Async/Streaming Tests


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
    onmessage: null,
    onerror: null,
    onopen: null,
    close: jest.fn(),
    readyState: 1 // OPEN
  };
}

beforeEach(() => {
  global.EventSource = jest.fn().mockImplementation(createMockEventSource);
});

afterEach(() => {
  jest.clearAllMocks();
});

test('connects to SSE endpoint', () => {
  const { result } = renderHook(() => useSSEStream('test-batch-123'));
  
  expect(EventSource).toHaveBeenCalledWith(
    '/api/generate/stream?batchId=test-batch-123'
  );
});

test('parses preview events', async () => {
  const previewHandler = jest.fn();
  let eventSourceInstance: ReturnType<typeof createMockEventSource>;
  
  global.EventSource = jest.fn().mockImplementation((url: string) => {
    eventSourceInstance = createMockEventSource();
    return eventSourceInstance;
  });
  
  renderHook(() => {
    const handler = useSSEStream('test-batch-123');
    useEffect(() => {
      handler.onPreview = previewHandler;
    }, []);
  });
  
  act(() => {
    eventSourceInstance!.onmessage?.({ data: JSON.stringify({
      imageBase64: 'abc123',
      imageIdx: 0,
      minibatchIdx: 0
    })});
  });
  
  expect(previewHandler).toHaveBeenCalledWith(expect.objectContaining({
    imageBase64: 'abc123',
    imageIdx: 0
  }));
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
    """Test that preview events contain expected fields."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://testserver/api/generate/stream?batchId=test123") as response:
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    events.append(json.loads(line[5:]))
            
            assert any(e.get("event") == "preview" for e in events)

@pytest.mark.asyncio
async def test_sse_done_event():
    """Test that done event is emitted on completion."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://testserver/api/generate/stream?batchId=test123") as response:
            done_events = []
            async for line in response.aiter_lines():
                if line.startswith("event: done"):
                    done_events.append(line)
            
            assert len(done_events) >= 1
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
    
    def test_reconnect_resume(self):
        buffer = EventBuffer(max_events=50, ttl_seconds=3600)
        
        for i in range(10):
            buffer.add_event("batch1", {"index": i})
        
        # Client reconnects, wants events after index 5
        events = buffer.get_events_since("batch1", after_index=5)
        assert len(events) == 4
        assert events[0]["index"] == 6
```
