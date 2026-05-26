# Artifact naming hygiene + Docs to Update

Companion to `spec-writer/SKILL.md`. Loaded when authoring or
critiquing a spec that introduces named files, paths, identifiers,
or docstrings.

---

## Artifact naming hygiene

Specs are read by humans and executed by agents. Both audiences need
names that survive the cycle that birthed them. The rules below block
the most common naming failures the review process catches at PR time
— get them right in the spec and they never reach the diff.

### Rule 1 — No ticket / gate / cycle / slice IDs in committed paths or filenames

A spec must never instruct the author to commit any of:

- `scripts/verify-T-732.sh`, `scripts/verify-6g1.sh` — verify-script names tied to a ticket
- `proof/4G-ui-cycle/`, `evidence/Slice-3/` — artifact directories named after a gate
- `tests/tickets/<ticket-id>.py` — test files named after the ticket
- `docs/PRD-<cycle>.md` referenced as a long-lived doc — these belong in `.plan/`

These names rot the moment the ticket closes or the gate is renamed.
Use names that describe the *test scope* or *feature*:
`scripts/verify-llm-config.sh`, `proof/chat-stack-smoke/`,
`tests/infra/test_compose_helm_parity.py`.

If a per-cycle artifact directory is genuinely needed, make the path
env-overridable: the test reads `os.environ.get("PROOF_DIR", default)`,
with the default being the feature-scoped name.

### Rule 2 — No runtime / vendor names in supposedly-agnostic identifiers

If the design is meant to support multiple runtimes / vendors / backends
in the future (or even just the foreseeable lifetime of the feature),
the names must reflect the *abstraction*, not today's instantiation.

Bad → Good:

- `agent.local-dmr.yaml` → `agent.local.yaml` (runtime selected by an env var, not the filename)
- `DockerModelRunnerClient` → `OpenAICompatibleClient` (DMR is one of many endpoints)
- `EMBEDDING_PULL_TAG = "hf.co/unsloth/..."` → catalog file keyed by alias, source ref per runtime
- `/api/v1/agent/docker-model-runner/status` → `/api/v1/agent/runtime/status`
- `function processOllamaResponse(...)` → `function processModelResponse(...)`

Allowed exceptions: runtime-specific code paths that *only* run for
that runtime (e.g. `provision_dmr()` inside a bootstrap script that
branches on `LLM_RUNTIME`); their names earn the vendor token because
they literally implement that vendor's protocol.

### Rule 3 — No internal-label drops in committed prose

A spec must not instruct the author to add ADR / Constitution / RISK /
ticket labels to:

- Source-code docstrings or comments
- Doc-page titles or section anchors
- Filenames of committed config files
- API response fields, enum values, or error codes

The label is a planning artifact; the code is the long-lived artifact.
If the rationale is load-bearing, the spec should require *prose* that
explains the *why*, accompanied by a stable link (path to an ADR file
under `docs/`, RFC URL, or spec filename) when one exists.

### Application

When a task in Section 3 mandates writing a file, naming a function,
or adding a docstring, scan it against rules 1–3 before listing the
file in `Files likely affected:`. If a name is borderline, name it
after the *feature* (`chat-stack-smoke`) rather than the *cycle*
(`4G-ui-cycle`).

---

## Docs to Update — mandatory ticket section

Every ticket must list every doc, diagram, README, runbook, env
example, and generated-reference file that mentions the surface being
changed. The author's job in the BUILD phase is to keep that checklist
in lockstep with the code change; reviewers reject the PR if the
checklist isn't complete or has unchecked boxes.

Format inside the ticket file:

```markdown
## Docs to Update
- [ ] `docs/architecture-overview.md` — replace `c3-agent` references with `agent_core`
- [ ] `docs/c3/diagrams/c4-L2-container.mmd` — same
- [ ] `README.md` — endpoint list (drop `/v1/chat/stream`, document the single-SSE shape)
- [ ] `packages/c3-chat/README.md` — runtime table; align with `config/llm-defaults.env`
- [ ] `.env.example` — add LLM_MODEL_EMBED row
- [ ] `tests/docs/test_local_dev_c3_ai_stack_runbook.py` — assertions for the new shape
```

How to populate the list when authoring the ticket:

```bash
# Substitute <surface> with the name of the changed thing — endpoint
# string, package name, config filename, env var, public function.
git grep -nE "\\b<surface>\\b" -- '*.md' '*.mmd' '*.rst' '.env*' 'docs/' 'README*'
```

Every hit becomes a checkbox. Tickets that delete a package or rename
a public symbol almost always have 5–10 boxes; tickets that change
behind a stable interface may have zero (record
`- [ ] None — internal change` for traceability).

This checklist is the spec-writer's contribution to closing the
"reference rot" gap; without it, parallel docs go stale and reviewers
have to discover the drift one comment at a time.
