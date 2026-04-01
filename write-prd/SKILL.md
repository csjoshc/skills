---
name: write-prd
description: >-
  Generates Product Requirements Documents from raw intent using the PRD expansion pipeline.
  Handles multi-round human-in-the-loop (HITL) clarification and routes output to `.prd/drafts/`
  or `.tickets/`. Use when turning vague requests into structured PRDs, not for one-shot ticket
  creation (use spec-writer for that).
---

## TL;DR (Quick Start)

Generates structured Product Requirements Documents (PRDs) from raw intent using a multi-round LangGraph pipeline with human-in-the-loop (HITL) clarification.

**When to use:** "write a PRD for...", "turn this idea into a spec".

**Invocation:**
```bash
write-prd "new feature summary"
```

## Decision Tree

1. **Is the score of ambiguity > 0.3?**
   - YES → **HITL Pause**; present Question DAG to user.
   - NO → Proceed to PRD composition.

2. **Is this a one-shot ticket request?**
   - YES → Use **spec-writer** instead.
   - NO → Proceed with `write-prd`.

3. **Are there architectural questions?**
   - YES → Categorize as HIGH impact and surface first in HITL.
   - NO → Proceed with standard questions.

## Workflow

## Role Distinction

| Skill | Input | Output |
|-------|-------|--------|
| **`write-prd`** | Raw request / issue | PRD document (Goals, Non-goals, Criteria) — **what/why to build** |
| **`spec-writer`** | Vague feature idea | Implementation plan / tickets — **how to build** |

## When to Use

- User says "write a PRD for...", "create a spec for...", "draft requirements for..."
- User wants to turn a vague request into a structured PRD
- User says `write-prd` directly
- **NOT** for one-shot ticket creation (use `spec-writer`)
- **NOT** for continuing existing tickets (use `orchestrate`)

## Invocation

```
write-prd                           # Interactive (prompts for description)
write-prd "add file upload..."      # Inline text
write-prd --input .prd/intake/xyz   # From intake file
write-prd --dry-run "..."           # Preview only
write-prd --output-dir /path ...    # Target specific project
write-prd --approve "..."           # Skip HITL (CI/scripted)
```

## How It Works

**Invocation:** The skill is invoked via the agent system (`/write-prd`), which runs the PRD expansion pipeline.

**Execution pattern:**
```bash
# Via agent skill (recommended)
/write-prd "feature description"

# Or with intake file (reads from project root)
/write-prd --input .prd/intake/my-issue.md

# The agent runs the pipeline targeting the current project directory
# Output: .prd/drafts/{slug}.md (same project root as intake)
```

### Pipeline Stages

```
Intake → Classification → Facet Analysis (product + codebase + alternatives)
                                                     ↓
                               Question DAG (if ambiguity > 0.3)
                                                     ↓
                               HITL Clarification (up to 2 rounds)
                                                     ↓
                               PRD Composition → Tickets
```

### Output Routing

| Pipeline status | Output location |
|-----------------|-----------------|
| `completed` | PRD → `.prd/drafts/{slug}.md`, Tickets → `.tickets/` (Stage: NEW) |
| `needs_human_feedback` | Manifest → `.prd/{slug}.manifest.json` (pipeline pauses) |
| `blocked` / `error` | Report errors and stop |

## HITL Flow (Interactive)

When ambiguity score > 0.3, the pipeline generates a Question DAG and pauses.

### When HITL Triggers

Questions are classified by type:
- `independent` — can be answered in any order
- `dependent` — requires parent question answered first
- `eliminating` — certain answers eliminate entire sub-trees

### Present Questions

Use the structured format from [templates/hitl-questions.md](templates/hitl-questions.md). Categorize questions by architectural impact:
- **Storage / Infrastructure** (HIGH)
- **Authentication / Security** (HIGH)
- **Integration / APIs** (HIGH)
- **UX / Interaction** (MEDIUM)
- **Performance / Scale** (LOW)
- **Compliance / Policy** (HIGH)

Show high-impact questions first.

### Collect Answers

Users can answer:
1. Inline key-value pairs: `q_storage_01: S3, q_auth_01: OAuth2`
2. Direct JSON: `--answers '{"q_storage_01": "S3", "q_auth_01": "OAuth2'}'`
3. Skip all: `--approve`

### Round 2

Pipeline prunes the Q-DAG based on Round 1 answers. Present any remaining follow-up questions. After answers are provided, pipeline proceeds to PRD composition.

## CLI Reference

```bash
# Via agent skill (recommended)
/write-prd "add file upload to dashboard"
/write-prd --input .prd/intake/my-issue.md

# Pipeline supports multi-round HITL clarification
# Answers provided via --answers flag for resume
```

| Flag | Purpose |
|------|---------|
| `--input`, `-i` | Input file from `.prd/intake/` |
| `--text`, `-t` | Raw text (alternative to `--input`) |
| `--dry-run` | Preview artifacts without writing |
| `--approve` | Skip all HITL rounds |
| `--answers`, `-a` | JSON of question_id → answer_text for HITL resume |

## Manifest Format

When HITL pauses, a manifest is written to `.prd/{slug}.manifest.json`:

```json
{
  "slug": "file-upload-to-dashboard",
  "status": "needs_human_feedback",
  "round": 1,
  "human_questions": [
    {"id": "q_abc123", "text": "What storage backend?"}
  ],
  "prior_answers": [],
  "artifacts": []
}
```

The skill reads this manifest on subsequent calls to merge answers across rounds.

## Common Mistakes

- **Using `spec-writer` for PRD** — spec-writer outputs tickets, not PRD documents
- **Forgetting `--approve`** in CI/scripted contexts — pipeline will pause for HITL
- **Answering without `--answers`** — answers must be passed via `--answers` flag for the pipeline to resume correctly
- **Skipping the manifest** — always let the skill write the manifest so multi-round HITL works
- Not categorizing questions by impact — high-impact architectural questions should be surfaced first

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for write-prd:**
- **Tier 1 (reversible):** Low ambiguity (score < 0.2) — proceed without HITL.
- **Tier 2 (conflict):** PRD draft contradicts existing project requirements — **STOP**, clarify with user.
- **Tier 3 (security):** PRD request involves PII or security-sensitive infrastructure — **STOP**, block and alert immediately.

## Examples

See `examples/interactive-session.md` for a full interactive HITL session transcript and `examples/non-interactive.md` for a simple --approve flow.
