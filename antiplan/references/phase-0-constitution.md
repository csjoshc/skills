# Phase 0: Constitution & Context

Loaded when entering Phase 0. Establishes non-negotiable principles and the
existing-code baseline before any feature discussion begins.

---

## Purpose

Phase 0 is the only phase that runs on every antiplan invocation regardless of
scale classification. It produces the two artifacts every later phase depends
on: the project constitution (user-declared principles) and the brownfield
research artifact (verified existing-code inventory).

---

## Phase 0 Steps

### 1. Constitution

Ask the user to declare 3–5 immutable project principles. Examples:
"no new runtime dependencies", "TDD strictly", "offline-capable", "single
binary deploy". These become project-specific challenge criteria used by the
Constitution Gate in Phase 2.

If the user declines to declare principles, record `constitution: none
declared` explicitly — silence is not a valid answer.

### 2. Brownfield Scan

If an existing codebase is detected, scan it automatically. Tag discovered
patterns, conventions, and architecture as `Observed` in the Assumption
Register. In Phase 2, the burden of proof **inverts** — the user must justify
deviations from existing architecture, not justify the architecture itself.

### 3. Research Artifact (brownfield only)

Write the brownfield scan to a structured `research.md` file (or a
brownfield-context section of the PRD). This is NOT optional — verbal
summaries disappear on context compaction.

Required contents:
- Existing package inventory (see hard rule below)
- Naming conventions
- Key function signatures at boundaries the feature touches
- Pre-existing behaviors that must not break
- The agent's interpretation of the architecture

The user then annotates disagreements or corrections before Phase 1 begins.
This catches AP-9 (Greenfield Hallucination) at the earliest possible moment —
if the agent misunderstands the existing codebase, better to discover it here
than in a failed integration gate.

**Hard rule — ls-verified paths:** Every directory path in the package
inventory MUST be the verbatim output of `ls` (or equivalent filesystem
listing), not a conceptual or abbreviated name. Use the template:

```
| Package | Directory (exact, ls-verified) | Import name (exact) | Key modules |
```

The research artifact is not ready for user review if any path is inferred
rather than observed from the filesystem.

**Hard rule — runtime contracts per surface (AP-27 mitigation):** Every
surface in the brownfield table must record the runtime invariants
that downstream tickets will need to honor. A path-only entry is
incomplete. For each surface, capture as a "Runtime contract" column
(or as a per-row sub-bullet):

- **Schemas / Pydantic models / Literals:** field count, field
  names + types, validator constraints (`min_length`, `max_length`,
  `regex`, `ge`, `le`, custom validators). Don't say "`PatentEnrichment`";
  say "`PatentEnrichment` — 9 fields: `summary: str`,
  `commercial_use_cases: list[str]`, …".
- **Enums / Literal value-sets:** the actual values. Don't say
  "`enrichment_status` enum"; say "`enrichment_status: Literal['pending',
  'complete', 'failed']` (will add `'enriched_placeholder'`)".
- **Compose services:** profile membership AND its implication. Don't
  say "`mcp-data-server`, no profile"; say "`mcp-data-server` — no
  profile → auto-up under any `--profile X up`; downstream wrappers
  must use explicit service list".
- **Container base images:** which CLI binaries the image ships with
  by default. Don't say "`nginx:alpine`"; say "`nginx:alpine` — has
  `wget`, no `curl`; healthcheck commands prescribed downstream must
  not assume curl".
- **Settings / env-var surfaces:** which variables are
  required-vs-optional at startup, and what happens if absent.
  Don't say "`Settings` class"; say "`Settings.GOOGLE_API_KEY:
  str | None = None` (optional; absence is fine post-T04 patch)".
- **Workspace / monorepo manifests:** which build-context root the
  Dockerfile expects, which workspace selector pnpm/uv/cargo
  filters require, what the package's actual `name` is in its
  manifest.

For every captured fact, ALSO record the *implication* — what
downstream tickets must do (or avoid) because of it. A fact without
an implication is half a contract.

If you don't know the contract, run the verifier (`grep`, `Read`,
`docker run --rm <image> which <bin>`) before writing the entry.
The brownfield doc is not ready for review if any surface row is
prose-only ("seems to be…", "probably…") rather than verified.

### 4. Implementation Topology Mapping (brownfield only)

For each feature area the user mentions, identify the existing file(s) that
would change. Produce a preliminary MODIFY/CREATE inventory. If the user
proposes creating a new package and an existing package has overlapping
responsibility, challenge immediately with AP-9. This mapping becomes PRD §8b.

### 5. Scale Classification

Determine Light / Standard / Heavy using the Decision Tree in SKILL.md. For
Light projects, compress the remaining phases per the classification rules.

---

## Phase 0 Output Contract

The Phase 0 exit response must contain a fenced `BROWNFIELD-CONTEXT:` block
(or `GREENFIELD-CONTEXT:` for greenfield work). See
`~/.skills/shared/PRD_TEMPLATES.md` → Phase-Block Contracts for the exact shape.

---

## Phase 0 Hard Gates

- Constitution is declared (or `none declared` recorded explicitly)
- For brownfield: research artifact is written and reviewed by the user
  before Phase 1
- Any user corrections to the agent's understanding of existing architecture
  are tagged `User-stated` in the Assumption Register
- The `BROWNFIELD-CONTEXT:` / `GREENFIELD-CONTEXT:` block is present in the
  Phase 0 exit response
- **Runtime contracts captured (AP-27):** every surface in the
  brownfield table has the runtime-invariants column populated from
  *verifier output* (grep, Read, ls, docker run), not from prose.
  Any surface that will be constructed, patched, or invoked by a
  downstream ticket must have its schema / enum / profile /
  base-image-binaries enumerated.

## Phase-Gate Audit Line

Before advancing to Phase 1, emit:

```
PHASE-GATE: Phase 0 → 1. Criteria: [constitution declared: <met|not met>; research artifact written: <met|not met|n/a greenfield>; ls-verified paths: <met|not met>; runtime contracts captured: <met|not met>]. Proceeding: <yes|no>.
```

If `Proceeding: no`, surface the specific blocker and stay in Phase 0.
