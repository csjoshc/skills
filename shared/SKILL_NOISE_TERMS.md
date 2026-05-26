# SKILL_NOISE_TERMS.md

Terms that are **skill-internal scaffolding** — they must not appear in any committed artifact
that a downstream reader (or external contributor) will encounter. Specifically:

- **Source code** — inline comments, docstrings (`"""..."""`, `/** ... */`, `//` line comments),
  log strings, error messages, and string literals used as file paths or directory names.
- **Configuration** — committed YAML / TOML / JSON / `.env` / Makefile values; filenames of
  committed config files.
- **Documentation** — `*.md`, `*.mmd` (Mermaid), `*.rst`; titles, section anchors, link text.
- **CI/CD** — workflow filenames, job names, step names, summary output.
- **Test artifact paths** — `proof/<gate-slug>/`, `evidence/<cycle>/`, hardcoded fixture dirs.
- **PR titles / bodies** — visible to anyone with repo access.

Presence of any of these in a committed diff is a `scope-leak` finding. They belong in
`.tickets/`, `.plan/`, planning artifacts, commit messages, or PR-thread comments — never in
the long-lived tree.

> **Used by**: `pr-review`, `cleanup`, `pr-create` (pre-flight grep), `project-onboarding` (fork audit), `ticket-critic` (build-stage scan)
> **Severity when found**: LOW (one-off comment) · MEDIUM (CI YAML, Makefile, docs, config filename) · HIGH (docstring on a public surface, path literal, identifier name)

---

## 1. "Constitution" system (cross-skill policy labels)

| Term / Pattern | Explanation |
|---|---|
| `Constitution` (capitalized) | Skill-internal policy document name |
| `Constitution P\d+`, `P\d+\b` (in code/docs) | Constitution principle codes — keep in commit messages, not committed prose |
| `P1` … `P23` (standalone or prefixed) | Constitution principle codes |
| `P1-auth'd`, `P5-retired` etc. | Annotated Constitution references |
| `MTP` | "Multi-Tier Proof" — skill delivery-cycle jargon |
| `IG-*` (e.g. `IG-7G4`) | Integration Gate ID pattern |
| `\d+G\d+\b` (e.g. `7G4`, `4G1`, `6G1`) | Bare gate ID pattern (without `IG-` prefix) — leaks as path slugs and script names |
| `<n>G-<slug>-cycle` (e.g. `4G-ui-cycle`, `3G-rerun-screenshots`) | Cycle-slug pattern used in `proof/`, `evidence/`, and test-artifact paths |
| `Slice \d+` | Spec-writer decomposition index (kept in `.tickets/`, not in code/docs) |
| `cycle:` as a prose label | Skill sprint-cycle reference |
| `cycle-close` in commit/PR titles | Skill sprint-closure marker |

---

## 2. spec-writer / ticket lifecycle

| Term / Pattern | Explanation |
|---|---|
| `FR-NN`, `NFR-NN`, `RISK-NN` | Functional / non-functional / risk requirement codes |
| `ADR-NN`, `DEBT-NN` | Decision record / tech-debt ticket codes |
| `T-NNN` (e.g. `T-762`, `T-767`) | Internal ticket ID pattern |
| `Stage: NEW\|SPEC\|PLAN\|BUILD\|REVIEW\|COMPLETE\|FAILED` | Orchestra stage enum |
| `Ralph:` / `Ralph-Reason:` / `Ralph-eligible` | Automated-review metadata fields |
| `[FALLIBLE_IO]` | Spec annotation tag |
| `ASSUMPTION:` | Spec assumption annotation |
| `PDCA-T` | Skill methodology label |
| `micro-task cycle` | Spec-writer process phrase |
| `vertical slice` | Spec-writer decomposition term |
| `Tier 1/2/3 assumptions`, `T1\|T2\|T3` | Risk tier codes |
| `RALPH_DECISION_RULE` | Shared-file reference |

---

## 3. antiplan

| Term / Pattern | Explanation |
|---|---|
| `AP-1` … `AP-25` | Antiplan anti-pattern codes |
| `Phase 0\|1\|2\|3\|3.5` (antiplan context) | Antiplan phase labels |
| `BROWNFIELD-CONTEXT`, `GREENFIELD-CONTEXT` | Antiplan section headers |
| `PROBLEM-STATEMENT`, `TICKET-DAG`, `INTEGRATION-GATES` | Antiplan PRD section names |
| `PHASE-GATE: Phase N → N+1` | Antiplan gate notation |
| `confidence: HIGH\|MEDIUM\|LOW` | Antiplan ledger field |
| `RECLASSIFY:` | Antiplan ledger marker |
| `Light\|Standard\|Heavy` (as scale) | Antiplan scope-scale labels |
| `interrogation` (as process noun) | Antiplan persona jargon |
| `brownfield scan`, `artifact ingestion` | Antiplan workflow phrases |
| `Fail Fast and Learn Faster` | Antiplan motto |
| `PRD §1` … `§17` | Antiplan PRD section references |
| `§8b`, `§8c` etc. | Antiplan section sub-codes |
| `validate.py` (antiplan context) | Antiplan convergence-check artifact |
| `coverage-auditor`, `challenger`, `champion` | Antiplan persona names |

---

## 4. ticket-critic

| Term / Pattern | Explanation |
|---|---|
| `Pattern 1–15` | Ticket-critic issue-pattern codes |
| `AC→Test traceability` | Ticket-critic review phrase |
| `machine-executable verification` | Ticket-critic AC quality label |
| `MRA` (Minimal Reproducible Artifact) | Ticket-critic jargon |
| `tautological tests` | Ticket-critic finding label |
| `constitutional leakage` | Ticket-critic finding category |
| `E2E validation gap` | Ticket-critic gap label |
| `Stage gate` (as a noun phrase) | Ticket-critic gate reference |
| `RALPH_DECISION_RULE.md`, `QUALITY_RUBRIC.md` | Shared-file names in prose |
| `Ralph-binding` | Ticket-critic binding-decision label |

---

## 5. pr-review / cleanup

| Term / Pattern | Explanation |
|---|---|
| `REVIEW-FINDINGS`, `REVIEW-GATE`, `REVIEW-LEDGER` | Skill-internal report section headers |
| `REVIEW-PHASE-0` | Cleanup phase label |
| `M1–M12` | QUALITY_RUBRIC dimension codes |
| `Tier A–I` (rubric tiers) | QUALITY_RUBRIC tier codes |
| `RESOLVED\|OVERRIDDEN\|OPEN` (as rubric status) | Cleanup ledger statuses |
| `specialist lenses` | pr-review process phrase |
| `Five-Axis rubric` | pr-review scoring label |
| `criteria-based checklist` | pr-review process phrase |
| `Multi-model review pattern` | pr-review architecture label |
| `scope drift` (as a code finding) | pr-review finding category |
| `N-of-M pattern` | cleanup threshold notation |
| `redundancy-watcher`, `layer-boundary-critic` | Cleanup sub-agent names |
| `coverage-auditor` | Review sub-agent name |
| `architecture depth lens` | Cleanup lens name |

---

## How to apply

### Default grep set

The patterns the noise terms above compile to:

```
ADR-[A-Z0-9-]+        # ADR labels in code/docs
T-[0-9]{3,}           # ticket IDs
FR-[0-9]+|NFR-[0-9]+|RISK-[0-9]+|DEBT-[0-9]+   # spec-writer codes
IG-[0-9]+G[0-9]*      # integration gate IDs
[0-9]+G[0-9]+         # bare gate IDs (proof slugs)
Slice [0-9]+
Constitution P[0-9]+|^P[0-9]+\b|[^A-Z]P[0-9]+\b
AP-[0-9]+
Pattern [0-9]+        # ticket-critic codes
M[0-9]+\b             # rubric dimension codes (in code context only)
```

### Where to grep — by skill

| Skill | Targets | Cmd hint |
|---|---|---|
| `pr-review` | diff hunks, including docstrings + path literals | `git diff main...HEAD -- '*.py' '*.ts' '*.tsx' '*.sh' '*.md' '*.yaml' '*.mmd'` |
| `cleanup` | changed files in the working tree | same as above on staged + unstaged |
| `pr-create` (Phase 3C) | full tree if deleting a package/module; otherwise diff | `git grep -nE '<pattern>' -- '*.md' '*.mmd' '.github/workflows/' 'helm/'` |
| `project-onboarding` | full repo on first audit | `git grep -nE '<pattern>'` |
| `ticket-critic` | build-stage tickets' AC verify commands | inspect AC `verify:` block in the ticket |

### Severity mapping

For each hit, record a `scope-leak` finding:

- **HIGH** — appears in a docstring on a public surface, an identifier (function/file/dir name), a string literal used as a path, an enum value, an API response field, or a config filename in a committed location.
- **MEDIUM** — CI YAML, Makefile target name, doc page title/anchor, image filename, Mermaid node label.
- **LOW** — one-off inline comment, log message at DEBUG, scratch fixture inside `tests/`.

Finding text: `"<term>" is skill-internal scaffolding vocabulary — strip from committed artifacts; keep in .tickets/, commit message, or PR-thread comments.`

### Why this matters

Docstrings and path literals are the **highest-impact** surfaces because they outlive the cycle that named them. An ADR label in a docstring confuses every future reader who doesn't have the ADR open; a gate slug in a path (`proof/4G-ui-cycle/`) makes the path stale the moment the gate is renamed. Code comments rot but get re-read rarely; docstrings get rendered into hover-help, autocomplete, generated docs sites, and onboarding wikis.
