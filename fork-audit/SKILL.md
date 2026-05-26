---
name: fork-audit
description: Audits and documents a forked or divergent codebase at layered depth (exec / architect / engineer) plus topic breakouts. Use when documenting a downloaded fork zip, understanding what changed vs upstream, decomposing squashed PRs into logical commits, identifying the novel architectural pattern, and producing reusable documentation under a gitignored .docs/ folder with Mermaid diagrams. Not for forward-looking design (use spec-writer/make-prd), not for PR-time review (use pr-review), not for general repo onboarding (use brief-docs).
---

# fork-audit

Apply this skill when the user says any of: "document this fork", "what changed vs main/upstream", "we downloaded a zip of repo X, audit it", "compare main…feature-branch and write it up", "understand and document this divergent branch".

The output is a **layered docs set** under a gitignored folder (default `.docs/`), structured so exec / architect / engineer can each enter at their own depth without rewriting.

## When to use vs not

| Use this skill | Use a different skill |
|---|---|
| Documenting a downloaded fork zip | New design from scratch → `make-prd` or `spec-writer` |
| Auditing a divergent branch (main…feature) | Per-PR review comments → `pr-review` |
| Producing layered exec/architect/engineer docs | Short single-page onboarding → `brief-docs` |
| Mermaid for system context, data flow, sequence | Just rendering one diagram → `make-mmd` |
| Confluence embeds → call `confluence-diagrams` after |

## Decision tree

```
1. Inputs you have?
   ├─ Local working dir of fork + upstream remote → use git diff directly
   ├─ Local zip + upstream GitHub URL → init silent repo, use gh API
   ├─ Two GitHub refs → use gh API only
   └─ Conversation context only → ask for refs

2. Style anchor provided?
   ├─ Yes (PDF / Confluence page / existing docs) → ingest first to extract narrative pattern
   └─ No → use the default layered template (this skill's `templates/`)

3. Should the repo be a "silent" local git repo?
   ├─ User said "don't appear as a fork" / "silent repo" → git init, no remotes
   ├─ User wants to push later → leave it to them
   └─ Already a working repo → don't re-init

4. Output folder?
   ├─ Default → .docs/ at repo root, gitignored
   └─ User-specified path
```

## Workflow

### Phase 1 — Diff forensics

Identify the divergent commits and their shape **before** writing anything.

1. **Resolve refs**
   - Base ref (upstream main) HEAD sha
   - Head ref (fork main) HEAD sha
   - Merge-base / divergence point
2. **List divergent commits** — get sha, date, author, message-title for each commit on head that isn't on base
3. **Per-commit metadata** — for each PR in the head, pull title, body, additions, deletions, changed_files
4. **File groupings** — counts by top-level dir (`apps/`, `packages/`, `containers/`, `helm/`, `.github/workflows/`, `docs/`, `scripts/`, root) to find where mass concentrates

**Gotcha — cross-fork compare API**: `gh api repos/<base>/compare/main...<head-owner>:<head-repo>:main` can return `status: identical` with `total_commits: 0` even when the branches clearly differ (because GitHub compares branches that are not direct ancestors as "identical" if they share no merge-base on the API path used). When this happens, fall back to listing the head branch's recent commits via `gh api repos/<owner>/<repo>/commits?per_page=N&sha=main` and compute divergence by walking back to the first commit whose sha exists on the base branch's history.

### Phase 2 — Inventory + style anchor

1. **Codebase inventory** — top-level structure of both base and head: `apps/`, `packages/`, `containers/`, `helm/`, `.github/workflows/`, `templates/`, `scripts/`, `docs/`
2. **Diff classification** — for each changed group, classify as one of:
   - **Added** (new directory or file)
   - **Removed** (deleted in head)
   - **Modified** (changed in head)
   - **Unchanged**
3. **Style anchor (optional)** — if a canonical reference is provided (PDF, Confluence URL, existing docs folder), read it and extract:
   - Section pattern (problem/constraint/solution, layered C4, etc.)
   - Table density vs prose density
   - Diagram density and style
   - Vocabulary used for the architecture

### Phase 2.5 — Fan out subagents for large diffs

Before starting deep analysis, decide whether the diff fits in a single context window or needs to be partitioned across subagents. Reading a 348-file PR sequentially is wasteful and risks context blow-up; reading it in parallel from 4 agents takes the same wall-clock as reading one.

#### Triggers (fan out if any are true)

- More than ~100 files changed across the divergent commits
- More than 3 top-level dirs touched (`apps/`, `packages/`, `helm/`, `.github/`, etc.)
- More than 3 divergent commits, each with its own narrative
- Total diff size > ~10,000 LOC
- A single squash carries clearly distinct concerns (app + platform + CI)

#### Partition strategies (pick one or combine)

| Pattern | Use when | How to partition |
|---|---|---|
| **By commit** | N divergent commits, each one a coherent unit | One subagent per commit; each owns its own PR body + file list |
| **By domain** | One large commit spans many top-level dirs | One subagent per dir: `apps/`, `packages/`, `containers/`, `helm/`, `.github/`, root configs |
| **By concern** | Squash mixes app + platform ride-along | App subagent, platform subagent, CI subagent — even though they share a sha |
| **By file-class** | Config-heavy diffs (yml, json, Dockerfile, helm chart, migrations) | One subagent per file class |

For very large fork-audits, **combine**: e.g. by-commit for PRs #1/#2 (small focused PRs) but by-domain for the bootstrap PR (mixed concerns).

#### Subagent choice

- **`Explore`** (read-only, fast, no Edit/Write) — default for inventory: "list all files matching X", "where is symbol Y defined", "which files import Z". Cheap, no synthesis.
- **`general-purpose`** (full toolset) — use when the subagent must produce a structured summary that feeds the layered docs. Synthesizes, not just searches.
- **`Plan`** — use only if subagent must decide section structure for a topic breakout before reading code.

Dispatch in parallel by sending one message with multiple `Agent` tool calls.

#### Coordination — every subagent returns this envelope

```
## Scope
<paths the agent covered>

## Classification
<app-specific / platform ride-along / CI / docs / config>

## Key findings (3–7 bullets)
<observations grounded in specific file:line references>

## Novel patterns (if any)
<structurally new shapes, not just config delta>

## Risks (if any)
<rate limits, classification leaks, migration surfaces>

## Reusable references
<symbol → file:line that other subagents or the parent will need>

## What this DIDN'T cover
<gaps the parent should dispatch to another agent>
```

The "what this didn't cover" field is the most important — it lets the parent decide if a second round of fan-out is needed without re-reading everything.

#### Re-merge (parent's responsibility)

1. Read all subagent envelopes side-by-side.
2. Cross-reference findings to spot duplicates and contradictions; pick one canonical statement per fact.
3. Build the **L1 source material** by stitching the subagent findings into the structure the architect-audience reframe expects (component boundaries, novel pattern, reuse map, NFRs, risks, migration). Hand that bundle to `/reframe architect` in a single call.
4. Build **L2 per-commit / per-domain sections** by pulling each subagent's slice into its template position.
5. **Topic breakouts** get one page each, drafted by whichever subagent flagged the novel pattern strongest; the parent edits for cross-references.
6. Keep the subagent envelopes around (in `.docs/.scratch/` or memory) until the layered docs are written and verified — they're the audit trail.

#### When NOT to fan out

- Fewer than ~50 files changed and one or two commits — sequential reads are simpler and avoid coordination overhead.
- Diff is mostly lockfiles, generated code, or other ignorable artifacts — filter before deciding.
- The user is using a fast model and explicitly wants to stay in-process — fan-out adds latency from per-agent setup.

### Phase 3 — Analytical framework

Answer these questions before writing — every output doc should be traceable to one of these answers:

| Question | Why it matters | Where the answer goes |
|---|---|---|
| What is the **identity** of head vs base? | Frame the relationship | L0 first paragraph |
| What are the **divergent commits** and how do they decompose? | Logical units for L2 | L2 per-PR sections |
| For each commit: which changes are **app-specific** vs **platform rode-along**? | A squash often carries both — readers need that split | L2 sub-sections per commit |
| What is the **novel architectural pattern**? (Not just config delta — what's structurally new) | The thing worth a topic breakout | One `topics/` page |
| What's **reused as-is** vs **replaced** vs **added** at the package level? | Maps the dependency surface | L1 Toolkit Reuse Map |
| What are the **trust / operational boundaries**? (rate limits, secrets, audit, classification) | NFR posture | L1 NFR slide |
| What are the **future-merge conflict surfaces**? | Migration risk | L1 Migration slide |
| What does the user / consumer of head actually do that base doesn't? | UX delta | L0 + topics |

### Decomposition heuristics

- **Read the PR body first** — many squash-merged PRs self-describe their inner logical commits ("three commits inside this squash: feat / fix / style"). Trust that decomposition; don't reinvent.
- **Look for ride-along platform work** — if a single squash touches both `apps/<new>/` and `packages/core/`, treat the platform changes as a separate logical unit even though they share the merge sha. Call this out explicitly.
- **The novel pattern is rarely the biggest file group** — it's the thing that's structurally different, not the thing with the most LOC. The biggest file group is usually scaffolding.

### Phase 4 — Silent repo init (optional)

If user wants a "silent" local repo (downloaded zip → standalone git repo, no remote linkage):

```bash
cd <repo>
git init -b main
# Append .docs/ to .gitignore (or whatever output folder)
git -c user.name="local" -c user.email="local@example.com" add -A
git -c user.name="local" -c user.email="local@example.com" commit -m "Import <repo>@<sha> (zip snapshot)"
git remote -v  # confirm empty
```

The local repo will not show as a fork on any platform unless a remote is later added. The upstream repo on GitHub may still be platform-labelled as a fork — that's a property of the GitHub repo, not changeable from local.

### Phase 5 — Output generation

Create the layered output set. Default folder: `.docs/` at repo root, added to `.gitignore` first.

```
.docs/
├── README.md                       # index — see templates/README.md
├── L0-executive-summary.md         # ~1 page, exec/product — see templates/L0-executive-summary.md
├── L1-technical-overview.md        # ~5 pages, architect — VIA /reframe architect, see templates/L1-technical-overview.md
├── L2-deep-dive.md                 # file-by-file walkthrough, engineer — see templates/L2-deep-dive.md
├── topics/
│   ├── <novel-pattern>.md          # the structural innovation
│   ├── <distinctive-feature>.md    # major feature deep-dive
│   └── <package-diff>.md           # what changed in shared packages
└── diagrams/
    ├── l1-system-context.{mmd,svg}    # system / component boundaries
    ├── l1-data-flow.{mmd,svg}         # the novel pipeline / flow
    └── l1-request-flow.{mmd,svg}      # sequence diagram of the primary use case
```

**Generation order:**
1. Write L0 directly (exec voice, problem/constraint/solution table, 1-paragraph identity, "what changed" table, "where to go from here" navigation)
2. Compose source material for L1 → invoke `/reframe architect <source>` → save its output as `L1-technical-overview.md`
3. Generate the three Mermaid diagrams (see Diagram conventions below); render each with `mmdc -i X.mmd -o X.svg -b transparent`
4. Write L2 (per-PR sections; for each, sub-sections for app-specific vs platform-ride-along; tables of files with `additions/deletions` from the PR metadata)
5. Write topic breakouts (one per `topics/`)
6. Write README.md last (index with reading-by-audience table; one-screen diff summary; what was written; what was intentionally not written)

### Phase 6 — Verify

- `git status` — output folder is not tracked (it's gitignored)
- `git check-ignore -v <output>/README.md` — confirms ignore rule fires
- All .mmd files have corresponding .svg
- README's reading table lists every file actually produced

## Output contract

Each file follows a defined shape. Templates in `templates/`:

| File | Stub | Voice | Key elements |
|---|---|---|---|
| `README.md` | [templates/README.md](templates/README.md) | Neutral | Reading-by-audience table; one-screen diff summary; "What was written / not written" |
| `L0-executive-summary.md` | [templates/L0-executive-summary.md](templates/L0-executive-summary.md) | Exec | Identity paragraph; Problem · Constraints · Solution table; "What changed vs upstream" 3-column table (PR / files / what it does); "Where to go from here" |
| `L1-technical-overview.md` | [templates/L1-technical-overview.md](templates/L1-technical-overview.md) | Architect (via `/reframe`) | YAML frontmatter + `## Slide:` sections per reframe contract; thesis; core-tension table; component-boundaries diagram; reuse map; NFRs; migration considerations; parking lot |
| `L2-deep-dive.md` | [templates/L2-deep-dive.md](templates/L2-deep-dive.md) | Engineer | Per-PR section with sub-section per logical commit; file table with additions/deletions; key code snippets where the design choice isn't obvious from the diff |
| `topics/<name>.md` | [templates/topic.md](templates/topic.md) | Engineer | Single-purpose; lead with "where it lives" + "why it exists"; diagram link if applicable; "see also" tail |

## Diagram conventions

Three Mermaid diagrams target the architect layer (L1):

1. **System context / component boundaries** (flowchart LR) — boxes for consumers, services, libraries, state, external systems; classDef colors per role; subgraphs for trust boundaries
2. **Novel-pattern data flow** (flowchart TB) — stages in the data pipeline / orchestration / state machine
3. **Primary request flow** (sequenceDiagram) — one canonical user→system→external→system→user round trip

**classDef color convention** (consistent with `/make-mmd` and `confluence-diagrams`):

```
classDef consumer fill:#bfbfbf,stroke:#444,color:#000;
classDef service  fill:#a8c5ff,stroke:#2855a8,color:#000;
classDef library  fill:#c9e3ff,stroke:#3970b8,color:#000;
classDef state    fill:#d6c4f0,stroke:#6a4ea8,color:#000;
classDef external fill:#d3d3d3,stroke:#666,color:#000;
classDef compute  fill:#a8c5ff,stroke:#2855a8,color:#000;
classDef output   fill:#c4eac4,stroke:#3a7a3a,color:#000;
classDef removed  fill:#f8d6d6,stroke:#a83838,color:#000,stroke-dasharray: 5 5;
```

Render each `.mmd` to `.svg` with `mmdc -i X.mmd -o X.svg -b transparent`.

## Hard constraints

- **Output folder is gitignored by default.** Prepend the output folder (e.g. `.docs/`) to the repo's `.gitignore` *before* the initial commit if doing a silent-repo init, so it never gets tracked.
- **Don't invent commit metadata.** If a PR body says "three commits inside this squash", honor it. Don't synthesize a decomposition the maintainer didn't endorse.
- **Distinguish app-specific from platform ride-along.** Single squash commits frequently carry both. Failing to split them produces an L2 that misleads readers about what's actually patent-search-specific (or whatever the app is).
- **L1 goes through `/reframe`.** Don't write the architect-audience layer from scratch — that's what `/reframe architect` exists for. Hand it the assembled source material in one call.
- **No silent information loss.** Anything cut from a doc for audience reasons goes in that doc's parking-lot (mirrors the `/reframe` contract).
- **Don't trust `gh api compare` cross-fork.** It can return `status: identical` for branches that differ. Always verify with the head's own commit history.

## Companion files

| File | Use when |
|---|---|
| [templates/README.md](templates/README.md) | Writing the index page |
| [templates/L0-executive-summary.md](templates/L0-executive-summary.md) | Writing the exec layer |
| [templates/L1-technical-overview.md](templates/L1-technical-overview.md) | Feeding into `/reframe architect` |
| [templates/L2-deep-dive.md](templates/L2-deep-dive.md) | Writing the engineer file-by-file layer |
| [templates/topic.md](templates/topic.md) | Each topic breakout |

## Quality checklist

Before reporting done:

- [ ] Output folder is gitignored and `git status` is clean
- [ ] L0 fits on one screen and leads with the identity paragraph
- [ ] L1 has YAML frontmatter, `## Slide:` sections, a parking-lot appendix, and at least one diagram
- [ ] L2 has one section per divergent commit, with app-specific vs platform ride-along sub-sections where applicable
- [ ] At least one topic breakout exists for the novel architectural pattern (the structurally new thing, not just the biggest file group)
- [ ] Each diagram has a `.mmd` source and a rendered `.svg`
- [ ] README lists every file actually produced
- [ ] Cross-references between L0/L1/L2/topics are real (clickable, resolve to existing files)
- [ ] The "where to go from here" / reading-by-audience table is in README and L0
- [ ] If `/stop-slop` is available, the prose has been run through it

## Composition with other skills

| Step | Skill |
|---|---|
| Architect-layer reframing | `/reframe architect <assembled-source>` (produces L1) |
| Diagram authoring | `/make-mmd` for fresh diagrams; this skill embeds the conventions inline |
| Confluence embed (post-hoc) | `/confluence-diagrams` |
| Final prose polish | `/stop-slop` per-file |
| Handoff to next session | `/handoff` — point the new agent at `.docs/README.md` |
