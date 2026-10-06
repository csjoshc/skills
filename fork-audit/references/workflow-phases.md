# Workflow phase detail

## Contents

- Phase 1 — Diff forensics
- Phase 2 — Inventory + style anchor
- Phase 2.5 — Fan out subagents for large diffs
- Scope
- Classification
- Key findings (3–7 bullets)
- Novel patterns (if any)
- Risks (if any)
- Reusable references
- What this DIDN'T cover
- Phase 3 — Analytical framework
- Phase 4 — Silent repo init (optional)
- Phase 5 — Fan out intermediates (`.docs/`)
- Phase 6 — Q&A hardening loop
- Phase 7 — Synthesize the final Confluence page
- Phase 8 — Verify

## Phase 1 — Diff forensics

Identify the divergent commits and their shape **before** writing anything.

1. **Resolve refs**
   - Base ref (upstream main) HEAD sha
   - Head ref (fork main) HEAD sha
   - Merge-base / divergence point
2. **List divergent commits** — get sha, date, author, message-title for each commit on head that isn't on base
3. **Per-commit metadata** — for each PR in the head, pull title, body, additions, deletions, changed_files
4. **File groupings** — counts by top-level dir (`apps/`, `packages/`, `containers/`, `helm/`, `.github/workflows/`, `docs/`, `scripts/`, root) to find where mass concentrates

**Gotcha — cross-fork compare API**: `gh api repos/<base>/compare/main...<head-owner>:<head-repo>:main` can return `status: identical` with `total_commits: 0` even when the branches clearly differ (because GitHub compares branches that are not direct ancestors as "identical" if they share no merge-base on the API path used). When this happens, fall back to listing the head branch's recent commits via `gh api repos/<owner>/<repo>/commits?per_page=N&sha=main` and compute divergence by walking back to the first commit whose sha exists on the base branch's history.

## Phase 2 — Inventory + style anchor

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

## Phase 2.5 — Fan out subagents for large diffs

Before starting deep analysis, decide whether the diff fits in a single context window or needs to be partitioned across subagents. Reading a 348-file PR sequentially is wasteful and risks context blow-up; reading it in parallel from 4 agents takes the same wall-clock as reading one.

### Triggers (fan out if any are true)

- More than ~100 files changed across the divergent commits
- More than 3 top-level dirs touched (`apps/`, `packages/`, `helm/`, `.github/`, etc.)
- More than 3 divergent commits, each with its own narrative
- Total diff size > ~10,000 LOC
- A single squash carries clearly distinct concerns (app + platform + CI)

### Partition strategies (pick one or combine)

| Pattern | Use when | How to partition |
|---|---|---|
| **By commit** | N divergent commits, each one a coherent unit | One subagent per commit; each owns its own PR body + file list |
| **By domain** | One large commit spans many top-level dirs | One subagent per dir: `apps/`, `packages/`, `containers/`, `helm/`, `.github/`, root configs |
| **By concern** | Squash mixes app + platform ride-along | App subagent, platform subagent, CI subagent — even though they share a sha |
| **By file-class** | Config-heavy diffs (yml, json, Dockerfile, helm chart, migrations) | One subagent per file class |

For very large fork-audits, **combine**: e.g. by-commit for PRs #1/#2 (small focused PRs) but by-domain for the bootstrap PR (mixed concerns).

### Subagent choice

- **`Explore`** (read-only, fast, no Edit/Write) — default for inventory: "list all files matching X", "where is symbol Y defined", "which files import Z". Cheap, no synthesis.
- **`general-purpose`** (full toolset) — use when the subagent must produce a structured summary that feeds the layered docs. Synthesizes, not just searches.
- **`Plan`** — use only if subagent must decide section structure for a topic breakout before reading code.

Dispatch in parallel by sending one message with multiple `Agent` tool calls.

### Coordination — every subagent returns this envelope

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

### Re-merge (parent's responsibility)

1. Read all subagent envelopes side-by-side.
2. Cross-reference findings to spot duplicates and contradictions; pick one canonical statement per fact.
3. Build the **L1 source material** by stitching the subagent findings into the structure the architect-audience reframe expects (component boundaries, novel pattern, reuse map, NFRs, risks, migration). Hand that bundle to `/reframe architect` in a single call.
4. Build **L2 per-commit / per-domain sections** by pulling each subagent's slice into its template position.
5. **Topic breakouts** get one page each, drafted by whichever subagent flagged the novel pattern strongest; the parent edits for cross-references.
6. Keep the subagent envelopes around (in `.docs/.scratch/` or memory) until the layered docs are written and verified — they're the audit trail.

### When NOT to fan out

- Fewer than ~50 files changed and one or two commits — sequential reads are simpler and avoid coordination overhead.
- Diff is mostly lockfiles, generated code, or other ignorable artifacts — filter before deciding.
- The user is using a fast model and explicitly wants to stay in-process — fan-out adds latency from per-agent setup.

## Phase 3 — Analytical framework

Answer these questions before writing — every output doc should be traceable to one of these answers:

| Question | Why it matters | Where the answer goes |
|---|---|---|
| What is the **identity** of head vs base? | Frame the relationship | L0 first paragraph |
| What are the **divergent commits** and how do they decompose? | Logical units for L2 | L2 per-PR sections |
| For each commit: which changes are **app-specific** vs **platform rode-along**? | A squash often carries both — readers need that split | L2 sub-sections per commit |
| What is the **novel architectural pattern**? (Not just config delta — what's structurally new) | The thing worth a topic breakout | One `topics/` page |
| What's **reused as-is** vs **replaced** vs **added** at the package level? | Maps the dependency surface | L1 Base Template Reuse Map |
| What are the **trust / operational boundaries**? (rate limits, secrets, audit, classification) | NFR posture | L1 NFR slide |
| What are the **future-merge conflict surfaces**? | Migration risk | L1 Migration slide |
| What does the user / consumer of head actually do that base doesn't? | UX delta | L0 + topics |

### Decomposition heuristics

- **Read the PR body first** — many squash-merged PRs self-describe their inner logical commits ("three commits inside this squash: feat / fix / style"). Trust that decomposition; don't reinvent.
- **Look for ride-along platform work** — if a single squash touches both `apps/<new>/` and `packages/core/`, treat the platform changes as a separate logical unit even though they share the merge sha. Call this out explicitly.
- **The novel pattern is rarely the biggest file group** — it's the thing that's structurally different, not the thing with the most LOC. The biggest file group is usually scaffolding.

## Phase 4 — Silent repo init (optional)

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

## Phase 5 — Fan out intermediates (`.docs/`)

Create the layered intermediate set. Default folder: `.docs/` at repo root, added to `.gitignore` first. These files are **not the deliverable** — they are the fan-out that grounds the final Confluence page. Each one earns its place by contributing a distinct slice to the synthesis.

```
.docs/
├── README.md                       # index — see templates/README.md
├── L0-executive-summary.md         # ~1 page, exec/product — see templates/L0-executive-summary.md
├── L1-technical-overview.md        # ~5 pages, architect — VIA /reframe architect, see templates/L1-technical-overview.md
├── L2-deep-dive.md                 # file-by-file walkthrough, engineer — see templates/L2-deep-dive.md
├── questions.md                    # Q&A loop input — see Phase 6
├── answers.md                      # Q&A loop output — code-cited answers + design gaps
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

## Phase 6 — Q&A hardening loop

The layered docs describe what the fork *is*; the Q&A loop surfaces what it *doesn't do*. This phase produced the strongest material in practice — the design-gaps section of the final page comes almost entirely from here.

1. **Collect questions** into `questions.md`. Sources, in priority order:
   - The user's own questions (they know their use case; capture them verbatim, typos and all)
   - Questions the layered docs raised but didn't answer (scaling, ops posture, eval coverage, cost)
   - Adversarial questions you generate: "what breaks at 10× scale?", "who reviews the AI output?", "what happens when the upstream API changes shape?"
2. **Answer every question in `answers.md`, citing code.** Each answer names the file:line that backs it. Where the code doesn't address the question, the answer is **"design gap — not implemented"** and gets flagged explicitly. Never paper over a gap with plausible-sounding prose.
3. **Promote cross-cutting gaps** into a numbered list at the end of `answers.md`. For each gap note whether it's *active* (biting today) or *latent* (fires on a trigger), and give the one-line check that would confirm its magnitude (a SQL query, a grep, a log inspection).
4. **Iterate.** New questions that come up while answering go back into `questions.md` (or a `questions2.md`). Stop when a round produces no new gaps.

This loop can run across sessions — the files persist, and later question rounds deepen earlier answers.

## Phase 7 — Synthesize the final Confluence page

This is the deliverable. One page, written fresh from the intermediates — **not** a concatenation of them.

1. **Confirm the target.** Page ID/URL from the user, or create under the space/parent they name. Fetch the existing page first (`confluence_get_page`) to check whether you're filling an empty page or updating live content.
2. **Draft from the fan-out.** Pull each section from its owning intermediate:

   | Final-page section | Sourced from |
   |---|---|
   | Identity paragraph + one-sentence framing | L0 |
   | "The fork in one screen" (PR table) | L0 / README diff table |
   | Primary request flow, stated as numbered steps | L2 + request-flow topic/diagram |
   | Novel-pattern section (pipeline, state machine, whatever it is) | `topics/<novel-pattern>.md` |
   | Mechanics with surprises ("the index you'd expect isn't there") | `answers.md` deep-technical answers |
   | Numbers-to-remember table (timings, costs, scale walls) | `answers.md` + topic operational notes |
   | Known gaps, numbered, with the scale at which each becomes a blocker | `answers.md` cross-cutting gaps |
   | "Where the deeper docs live" pointer table | README |

3. **Write in the Q&A voice, then run `/stop-slop`.** Direct verdicts ("There is no re-ranking. The cosine score is used directly."), concrete values, gaps stated as gaps. Tables over prose where the content is tabular. No em dashes, no filler, no hedging.
4. **Keep it one page.** Target the length of a 10-minute read. Anything that wants more depth gets a one-line pointer to the in-repo canonical doc (DEVGUIDE, design specs), not inlined. The `.docs/` intermediates are local-only and gitignored — reference them by name for the audit trail, but don't link them as if readers can click through.
5. **Publish** via `confluence_update_page` (markdown format; `table_layout: wide` reads better for the numbers tables). Offer as follow-ups: uploading the diagram SVGs via `/confluence-diagrams`, and linking the PRs if the repo is shareable.

Template: [templates/confluence-design-page.md](../templates/confluence-design-page.md).

## Phase 8 — Verify

- `git status` — output folder is not tracked (it's gitignored)
- `git check-ignore -v <output>/README.md` — confirms ignore rule fires
- All .mmd files have corresponding .svg
- README's reading table lists every file actually produced
- The Confluence page exists at the expected URL, renders its tables, and its version comment names this audit
- Every gap on the final page traces back to a flagged answer in `answers.md`
