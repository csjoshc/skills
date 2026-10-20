# Prompt Templates

Fill slots from detected state. Used when starting challenge or spec,
or when a halt needs a follow-up prompt. BUILD briefs live in
execution-templates.md.

## Contents

- challenge-start
- spec-direct
- challenge-resume
- spec-next
- handoff

### challenge-start (`/todo start <feature>`)

```
Invoke challenge for this feature:

**Feature:** <feature description>
**Working directory:** <pwd>
**Artifact dir:** .plan/

Let challenge pick its mode (Fast Mode by default). If it escalates, write
brownfield-context.md, PRD.md and task-sequence.md into .plan/ and stop
after Phase 3. Do not emit fleshed ticket bodies.
```

### spec-direct (`/todo spec <feature>`, Lite)

```
Invoke spec for this defined feature (no challenge PRD):

**Feature:** <feature description>
**Working directory:** <pwd>

Write one ticket per independently testable slice to .tickets/NNN-slug.md.
Each ticket follows ~/.skills/shared/TICKET_CONTRACT.md with Stage: NEW.
Do not write .plan/.
```

### challenge-resume

```
Resume challenge. Treat these as approved inputs; do not re-derive them:

- <existing .plan/ files with absolute paths>

Continue from <detected phase>.
```

### spec-next (dag-done)

```
Invoke spec.

**Inputs:**
- .plan/PRD.md
- .plan/task-sequence.md
- .plan/brownfield-context.md (if present)

For every stub in task-sequence.md, write one .tickets/NNN-slug.md following
~/.skills/shared/TICKET_CONTRACT.md. Stage: NEW. One file per ticket.
```

### handoff

Write `.handoff/<slug>.md` via the handoff skill. Reply with its absolute
path and 2-4 sentences. Do not paste the file.
