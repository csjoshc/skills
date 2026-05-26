# Identifier and doc-staleness audit (onboarding 0d)

Companion to `project-onboarding/SKILL.md` section 0d. Loaded when
onboarding a fork, an inherited project, or any codebase whose
history includes prior planning cycles. Catches debris that
accumulated under previous owners and would otherwise leak into
every future PR.

## Identifier scope scan (source + docs)

The patterns from
[`~/.skills/shared/SKILL_NOISE_TERMS.md`](../shared/SKILL_NOISE_TERMS.md)
— ADR labels, ticket IDs, Constitution principles, gate / slice /
cycle slugs — belong in `.tickets/`, `.plan/`, and commit messages,
**not** in committed source, docstrings, doc bodies, config
filenames, or test artifact paths. Run:

```bash
# Exclude planning artifacts and historical proof; keep the noise.
git grep -nE '(ADR-[A-Z0-9-]+|T-[0-9]{3,}|FR-[0-9]+|NFR-[0-9]+|RISK-[0-9]+|IG-[0-9]+G[0-9]*|[0-9]+G[0-9]+|Slice [0-9]+|Constitution P[0-9]+|AP-[0-9]+|Pattern [0-9]+)' \
  -- '*.py' '*.ts' '*.tsx' '*.js' '*.mjs' '*.sh' '*.md' '*.mmd' '*.yaml' '*.yml' '*.json' '*.toml' \
  ':!.tickets' ':!.plan' ':!.handoff' ':!.orchestra' ':!proof/' ':!docs/ADR-*'
```

For every hit, classify:

- **ADR-NN labels in docstrings** → these are doc identifiers, not
  source-comment identifiers. Replace with prose that explains the
  *why*, optionally followed by `docs/ADR-XX.md` as a stable pointer.
- **T-NNN / IG-NGN / Slice N in code or docs** → ticket / gate /
  slice IDs. Strip; if the rationale is load-bearing, restate in
  prose without the planning-system token.
- **Constitution P\d+ in code** → policy labels. Strip and restate
  the *rule* itself in one sentence.
- **Cycle slugs in committed paths** (`proof/4G-ui-cycle/`,
  `scripts/verify-6g1.sh`) → rename to feature/scope-based names per
  AP-24; make per-cycle artifact directories env-overridable.
- **Vendor / runtime tokens in supposedly-agnostic identifiers**
  (`agent.local-dmr.yaml`, `OLLAMA_BASE_URL` when the project surface
  is meant to be `LLM_BASE_URL`) → rename per AP-25.

Record findings in the onboarding handoff so they become followup
tickets, not silent debt:

```markdown
## Onboarding scan — identifier / naming debt

| Path | Pattern | Suggested rename | Coupled to |
|---|---|---|---|
| `packages/c3-chat/config/agent.local-dmr.yaml` | vendor token in agnostic filename | `agent.local.yaml` | runtime |
| `proof/4G-ui-cycle/` | cycle slug in artifact path | `proof/chat-stack-smoke/` (env-overridable) | cycle |
| `react/src/.../client.ts:42` (`ADR-CHAT-1`) | label-only docstring | prose explaining single-SSE rationale | — |
```

Add a note to `STANDARDS.md` and `AGENTS.md`:

> Identifiers (`ADR-*`, `T-NNN`, `Constitution P\d+`, `Slice N`, gate
> slugs) are planning-system markers. Keep code explanations
> self-contained; reference IDs only in commit messages and PR
> threads.

## Doc-stale-ness scan (documentation tree)

After the identifier scan, audit `docs/` and the README tree for
references to deleted/renamed entities. Two passes:

```bash
# Find docs that reference a candidate-deleted package or module
git grep -lE '\b(packages/old-name|class OldClient|/api/v1/old-endpoint)\b' \
  -- '*.md' '*.mmd' '*.rst'

# Find docs explicitly marked stale by previous owners
git grep -lE '(TODO|TBD|OBSOLETE|DEPRECATED|XXX|FIXME)' \
  -- '*.md' | head -20
```

For every doc that references a missing or renamed entity:

- **Update** the reference if the replacement is unambiguous.
- **Delete** the doc if it described only the deleted thing and the
  hub no longer needs the spoke.
- **Fold** unique facts into the hub when a spoke goes orphan.

Common debris this scan catches: architecture diagrams pointing at
packages that no longer exist; README quick-starts that pull removed
binaries; runbooks with stale endpoint shapes; ADR cross-links to
renamed packages.

Both scans become part of the onboarding handoff — they don't have
to be fully cleaned during onboarding, but they must be *surfaced*
so the team can prioritize cleanup before the debt ossifies into
"that's just how this repo is".
