# Performance Budgets

## Default Targets (adjust per project)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API response time (simple) | <200ms | >500ms |
| API response time (complex) | <1s | >2s |
| Frontend initial load | <3s | >5s |
| Frontend interaction | <100ms | >200ms |
| File upload (<10MB) | <10s | >20s |
| Queue processing | <60s/job | >90s (timeout) |
| Memory per process | <500MB | >400MB |

## Cleanup Strategies

| Resource | Strategy |
|----------|----------|
| In-memory caches | LRU eviction, max 100 entries, 1-hour TTL |
| Temp files | Clean on startup, 24-hour TTL |
| Run history | Keep last 10 entries, archive older |
