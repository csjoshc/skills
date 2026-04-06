# TDD Dry-Run Usage

Tests should default to running in **NON dry-run mode** to ensure real-world connectivity and generation parity.

## When to use dry-run

- Rapid iteration on orchestration logic
- CI pipelines where live backend is unavailable
- Testing error handling without external dependencies

## When NOT to use dry-run

- Feature completion verification (unless explicitly justified)
- Integration tests that verify end-to-end behavior
- Tests that validate actual output quality

Dry-run mode (`backend="dry_run"`) is valuable for isolated unit testing, but it MUST NOT be the primary verification method for feature completion.
