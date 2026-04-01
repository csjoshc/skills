# Orchestra — Canonical Defaults

This shared file contains the authoritative definitions for the **Orchestra** ticket runner's runtime configuration.

## Execution Profiles

Select a profile via `--profile` or `ORCHESTRA_PROFILE` env var.

| Profile | Target Environment | Runtimes used | Primary Model |
|---------|-------------------|--------------|---------------|
| **work** | Corporate laptop, proprietary code | Cursor only | Sonnet 4.6 (Frontier) |
| **mixed** | Hybrid work/side projects | Cursor + opencode | Sonnet 4.6 + big-pickle |
| **private** | Personal computer (Default) | opencode + qwen | big-pickle + qwen3.5-plus |
| **cost_saver** | Heavily used for simple tasks | qwen → opencode | qwen3.5-plus |
| **qwen_only** | Single-model isolation | qwen only | qwen3.5-plus |

## Model Tiers

Use the appropriate tier based on ticket complexity.

| Tier | Recommended Models | Use Case |
|------|--------------------|----------|
| **Frontier** | Sonnet 4.6, Opus 4.6, opencode/big-pickle | Architecture, complex logic, ambiguous scope |
| **Standard** | Composer 2 Fast, qwen3.5-plus, gemini-3-flash | Narrow bugfixes, well-defined features, cost-sensitive |

**Rule of thumb:** If a ticket touches >3 files or requires a `Task 0: Design` phase, use **Frontier**.

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
