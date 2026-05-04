---
name: perf
description: >-
  Performance investigation. Use when something is slow or to hit
  a perf budget. Measure-first workflow, Core Web Vitals, N+1 detection.
  Not for browser-only profiling sessions (use chrome-devtools).
---

<!-- imported from addyosmani/agent-skills performance-optimization -->

# Performance Optimization

Measure before optimizing. Profile, identify the bottleneck, fix it, measure again.

## When to Use

| Trigger | Note |
|---|---|
| Spec defines budgets | LCP/SLA targets |
| Users / monitoring report slowness | Real signal |
| Core Web Vitals below threshold | Below "Good" |
| Suspected regression | Compare to baseline |
| Large datasets / high traffic | Built for scale |

**Don't use** without evidence of a problem. Premature optimization adds complexity that costs more than it gains.

## Core Web Vitals

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## Workflow

```
MEASURE → IDENTIFY → FIX → VERIFY → GUARD
```

### Step 1: Measure

Two complementary modes — use both.

| Mode | Tool | Best for |
|---|---|---|
| Synthetic | Lighthouse, DevTools Performance | Reproducible CI regression detection |
| RUM | web-vitals lib, CrUX | Validate fix against real users |

```typescript
import { onLCP, onINP, onCLS } from 'web-vitals';
onLCP(console.log);
onINP(console.log);
onCLS(console.log);
```

Backend:
```typescript
console.time('db-query');
const result = await db.query(...);
console.timeEnd('db-query');
```

### Where to Start by Symptom

| Symptom | First check |
|---|---|
| First page load slow | Bundle size, TTFB in network waterfall |
| TTFB high (DNS) | Add `dns-prefetch` / `preconnect` |
| TTFB high (server) | Profile backend, queries, caching |
| Render-blocking | Network waterfall for CSS/JS |
| UI freezes on click | Long tasks (>50ms) on main thread |
| Form input lag | Re-renders, controlled component overhead |
| Animation jank | Layout thrashing, forced reflows |
| Endpoint slow | DB queries, indexes |
| All endpoints slow | Connection pool, memory, CPU |
| Intermittent | Lock contention, GC, external deps |

### Step 2: Identify

**Frontend symptoms:**

| Symptom | Likely cause |
|---|---|
| Slow LCP | Large images, render-blocking, slow server |
| High CLS | Images without dims, late content, font shifts |
| Poor INP | Heavy JS on main thread, large DOM updates |
| Slow initial load | Large bundle, many requests |

**Backend symptoms:**

| Symptom | Likely cause |
|---|---|
| Slow API | N+1, missing indexes, unoptimized queries |
| Memory growth | Leaked refs, unbounded caches, large payloads |
| CPU spikes | Sync heavy compute, regex backtracking |
| High latency | Missing caching, redundant compute, network hops |

### Step 3: Fix Anti-Patterns

**N+1 (backend):**

```typescript
// BAD
const tasks = await db.tasks.findMany();
for (const task of tasks) {
  task.owner = await db.users.findUnique({ where: { id: task.ownerId } });
}

// GOOD
const tasks = await db.tasks.findMany({ include: { owner: true } });
```

**Unbounded fetch:**

```typescript
// GOOD
const tasks = await db.tasks.findMany({
  take: 20, skip: (page - 1) * 20,
  orderBy: { createdAt: 'desc' },
});
```

**Image optimization (LCP / hero):**

```html
<picture>
  <source media="(max-width: 767px)"
    srcset="/hero-mobile-400.avif 400w, /hero-mobile-800.avif 800w"
    sizes="100vw" width="800" height="1000" type="image/avif" />
  <source media="(max-width: 767px)"
    srcset="/hero-mobile-400.webp 400w, /hero-mobile-800.webp 800w"
    sizes="100vw" width="800" height="1000" type="image/webp" />
  <source srcset="/hero-800.avif 800w, /hero-1200.avif 1200w, /hero-1600.avif 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200" height="600" type="image/avif" />
  <source srcset="/hero-800.webp 800w, /hero-1200.webp 1200w, /hero-1600.webp 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200" height="600" type="image/webp" />
  <img src="/hero-desktop.jpg" width="1200" height="600"
    fetchpriority="high" alt="Hero image description" />
</picture>

<!-- Below-the-fold: lazy + async decode -->
<img src="/content.webp" width="800" height="400"
  loading="lazy" decoding="async" alt="Content image description" />
```

**Re-renders (React):**

```tsx
// BAD: new object each render
function TaskList() { return <TaskFilters options={{ sortBy: 'date', order: 'desc' }} />; }

// GOOD: stable reference
const DEFAULT_OPTIONS = { sortBy: 'date', order: 'desc' } as const;
function TaskList() { return <TaskFilters options={DEFAULT_OPTIONS} />; }

const TaskItem = React.memo(function TaskItem({ task }: Props) {
  return <div>{/* expensive render */}</div>;
});

function TaskStats({ tasks }: Props) {
  const stats = useMemo(() => calculateStats(tasks), [tasks]);
  return <div>{stats.completed} / {stats.total}</div>;
}
```

**Bundle splitting:**

```typescript
const ChartLibrary = lazy(() => import('./ChartLibrary'));
const SettingsPage = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <SettingsPage />
    </Suspense>
  );
}
```

> Modern bundlers (Vite, webpack 5+) tree-shake named imports automatically when the dep ships ESM with `sideEffects: false`. Profile before chasing import-style changes.

**Caching:**

```typescript
const CACHE_TTL = 5 * 60 * 1000;
let cachedConfig: AppConfig | null = null;
let cacheExpiry = 0;

async function getAppConfig(): Promise<AppConfig> {
  if (cachedConfig && Date.now() < cacheExpiry) return cachedConfig;
  cachedConfig = await db.config.findFirst();
  cacheExpiry = Date.now() + CACHE_TTL;
  return cachedConfig;
}

app.use('/static', express.static('public', { maxAge: '1y', immutable: true }));
res.set('Cache-Control', 'public, max-age=300');
```

## Performance Budget

| Item | Budget |
|---|---|
| JS bundle (initial) | < 200KB gzipped |
| CSS | < 50KB gzipped |
| Image (above fold) | < 200KB |
| Fonts (total) | < 100KB |
| API p95 | < 200ms |
| TTI on 4G | < 3.5s |
| Lighthouse Performance | ≥ 90 |

```bash
npx bundlesize --config bundlesize.config.json
npx lhci autorun
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll optimize later" | Perf debt compounds. Fix anti-patterns now. |
| "Fast on my machine" | Profile on representative hardware/network. |
| "This optimization is obvious" | If you didn't measure, you don't know. |
| "Users won't notice 100ms" | Research shows conversion drops. |
| "Framework handles perf" | Doesn't fix N+1 or oversized bundles. |

## Red Flags

- Optimization without profiling data
- N+1 patterns in data fetching
- List endpoints without pagination
- Images without dims, lazy, or responsive sizes
- Bundle growing unreviewed
- No production perf monitoring
- `React.memo` / `useMemo` everywhere

## Verification

- [ ] Before/after measurements (real numbers)
- [ ] Specific bottleneck addressed
- [ ] Core Web Vitals in "Good"
- [ ] Bundle size hasn't ballooned
- [ ] No N+1 in new code
- [ ] Perf budget passes in CI
- [ ] Existing tests still pass

## See Also

- `chrome-devtools` — browser-side profiling and traces
- `debug` — slowness as a regression
