# Orchestra — Canonical Defaults

This shared file contains the authoritative definitions for the **Orchestra** ticket runner's runtime configuration.

## Profiles, Models, and Chains

See `~/Projects/orchestra/profiles.yaml` for the canonical runtime config.
Run `orch config list` to see currently loaded values.

Available profiles: `work`, `mixed`, `private` (default), `cost_saver`, `qwen_chain`, `qwen_only`, `opencode_stepfun`.

---

## State Machine Stages

Every ticket markdown file must contain a `Stage:` header.

| Stage | Meaning | Transition From |
|-------|---------|-----------------|
| **`NEW`** | Initial state, ready for execution | N/A |
| **`SPEC`** | Planning/Decomposition phase | `NEW` / `REVISION_ROUTER` |
| **`BUILD`** | Implementation phase (Coding) | `SPEC` / `NEW` (Single Mode) |
| **`REVIEW`** | Audit/QA phase | `BUILD` |
| **`COMPLETE`** | Terminal state (Merged) | `REVIEW` / `BUILD` (Single Mode) |
| **`BLOCKED`** | Halted due to dependency/logic | Any non-terminal stage |
| **`FAILED`** | Technical execution failure | Any non-terminal stage |

**Routing Patterns:**
- **Single Mode:** `entry → build → complete`
- **Sequential Mode:** `entry → spec → build → review → complete`

---

## Directory Convention

Orchestra respects the following structure in the **target project**:
- `.tickets/` — Ticket markdown files
- `.handoff/` — Handoff context (used between `SPEC` and `BUILD`)
- `.orchestra.db` — SQLite task/edge tracker
- `AGENTS.md` — Local agent behavior rules
- `STANDARDS.md` — Local project-specific code standards
