# Integration

## With `/todo`

Full mode: challenge → spec → ticket-review → build.
Ticket Critic reviews existing `.tickets/*.md` after spec and writes
`.plan/critic-report.md`.

Lite mode: spec creates tickets directly. Ticket Critic is optional;
`/todo` may route directly to build.

On `FAIL`, `/todo` routes only failing tickets to spec for repair, then
runs Ticket Critic again. On all `PASS`, `/todo` routes to build.

Ticket Critic does not change ticket stages. New tickets start at `Stage: NEW`;
`/todo build` changes a ticket to `Stage: BUILD` when implementation starts.

## With other skills

- `/tdd` may be used directly without Ticket Critic when no ticket workflow is
  needed.
- `onboard` may provide repository standards. Ticket Critic uses
  those standards when resolving findings.
- `cleanup` reviews existing code. Ticket Critic reviews ticket readiness;
  use the [shared quality rubric](../../shared/QUALITY_RUBRIC.md) only when a
  ticket explicitly needs quality-dimension acceptance criteria.
