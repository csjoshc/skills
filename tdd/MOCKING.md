# When to Mock

## Contents

- Designing for Mockability
- Concrete Mocking Patterns


Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

---

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

### 1. Use Dependency Injection

Pass external dependencies in rather than creating them internally:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeGateway();
  return client.charge(order.total);
}
```

### 2. Prefer SDK-Style Interfaces

Create specific functions for each external operation instead of one generic function with conditional logic:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint

### 3. Accept Interfaces, Return Concrete

```typescript
// Testable: accepts interface
function calculateDiscount(cart, pricingService): Discount {
  return pricingService.getRate(cart);
}

// Hard to test: creates dependency internally
function calculateDiscount(cart): Discount {
  const pricingService = new PricingService();
  return pricingService.getRate(cart);
}
```

---

## Concrete Mocking Patterns

### Backend (pytest)

#### File System Isolation with `tmp_path`

```python
import pytest
from PIL import Image
from src import batch_service

class TestBatchService:
    @pytest.fixture
    def batch_setup(self, tmp_path, monkeypatch):
        """Set up isolated batch directory."""
        monkeypatch.setattr(batch_service, "OUTPUT_DIR", tmp_path)
        
        batch_id = batch_service.generate_batch_id()
        batch_dir = tmp_path / batch_id
        batch_dir.mkdir(parents=True)
        (batch_dir / "images").mkdir()
        return batch_id, batch_dir

    def test_saves_image_file(self, batch_setup):
        batch_id, _ = batch_setup
        img = Image.new("RGB", (1024, 1024), color="red")
        
        saved_path = batch_service.save_image_with_metadata(
            batch_id=batch_id,
            image_num=1,
            image=img,
            seed=42,
            resolved_prompt="test prompt",
            minibatch_name="test_batch",
            position_in_minibatch=1,
            generation_params={"test": "params"},
            timing={"elapsed_seconds": 1.5},
        )
        
        assert saved_path.exists()
        assert saved_path.name == "001.png"
```

#### Monkeypatch for Module-Level Dependencies

```python
def test_missing_nodes_raise_runtime_error(monkeypatch, tmp_path):
    """Should surface RuntimeError when nodes are missing."""
    ref_path = tmp_path / "face.png"
    ref_path.write_bytes(b"fake")
    
    def raise_nodes():
        raise RuntimeError("Flux KV reference nodes not available.")
    
    monkeypatch.setattr("src.pipeline._load_flux_kv_nodes", raise_nodes)
    
    with pytest.raises(RuntimeError, match="Flux KV reference nodes not available"):
        _build_flux_kv_reference(str(ref_path), "pos", "neg", "vae")
```

#### Dependency Injection for Generation Functions

```python
from PIL import Image
from src.generation_jobs import run_batch_job_sync
from src.config import load_hardware_config

def test_run_batch_job_sync_with_stub():
    hw = load_hardware_config()
    request = GenerationRequest(
        minibatches=[MinibatchRequest(
            name="test",
            count=1,
            prompt_template="test prompt",
        )]
    )
    
    def fake_gen_fn(params, hw):
        return [Image.new("RGB", (64, 64), "blue")], None
    
    preview, gallery, batch_id = run_batch_job_sync(
        request, hw,
        gen_fn_override=fake_gen_fn
    )
    assert preview is not None
    assert gallery
    assert batch_id
```

#### Capturing Parameters for Verification

```python
def test_passes_correct_params(monkeypatch):
    captured = {}
    
    def fake_gen_fn(params, hw):
        captured["face_mode"] = params.face_mode
        captured["face_ref_path"] = params.face_ref_path
        return [Image.new("RGB", (64, 64), "blue")], None
    
    monkeypatch.setattr(generation_jobs, "generate_assets_for_batch", lambda **kwargs: None)
    monkeypatch.setattr(generation_jobs, "get_batch_assets", lambda batch_id: {"generated_assets": {}})
    
    run_batch_job_sync(request, hw, gen_fn_override=fake_gen_fn)
    
    assert captured["face_ref_path"] == "C:\\\\fake\\\\face.png"
    assert captured["face_mode"] == "reference"
```

### Frontend (Vitest + MSW)

#### MSW API Mocking Setup

```typescript
// src/api/__tests__/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/bootstrap', () => {
    return HttpResponse.json({
      hwInfo: {
        gpu_name: 'RTX 4090',
        vram_gb: 24,
        ram_gb: 64,
        platform: 'linux'
      },
      comfyUrl: 'http://localhost:8188',
      comfyui_available: true,
      presets: ['default', 'portrait', 'landscape'],
    });
  }),
  
  http.get('/api/generate/status/:batchId', ({ params }) => {
    return HttpResponse.json({
      batchId: params.batchId,
      status: 'complete',
      progress: 100,
      imagesGenerated: 5
    });
  })
];

// src/api/__tests__/mocks/browser.ts
import { setupWorker } from 'msw/browser';

export const worker = setupWorker(...handlers);
```

#### Using MSW in Tests

```typescript
// src/api/__tests__/bootstrap.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useBootstrap } from '../useBootstrap';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

function Wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

test('useBootstrap returns hardware info', async () => {
  const { result } = renderHook(() => useBootstrap(), { wrapper: Wrapper });
  
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  
  expect(result.current.data?.hwInfo.gpu_name).toBe('RTX 4090');
  expect(result.current.data?.comfyui_available).toBe(true);
});
```

#### TanStack Query Hook Mocking

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useGenerationStatus } from '../useGenerationStatus';

global.fetch = jest.fn().mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({
    batchId: 'test-batch-123',
    status: 'complete',
    progress: 100
  })
}) as jest.Mock;

test('returns generation status', async () => {
  const { result } = renderHook(() => useGenerationStatus('test-batch-123'));
  
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  
  expect(result.current.data?.status).toBe('complete');
});
```
