# Notes

## Layer cake (dependencies flow downward only)

1. services — business logic and orchestration
2. infra — I/O, HTTP clients, DB drivers
3. util — stateless helpers, no I/O

Exclusions: none.
