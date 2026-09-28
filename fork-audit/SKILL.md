---
name: fork-audit
description: Audits and documents a forked or divergent codebase, fanning out intermediate layered docs (exec / architect / engineer), topic breakouts, and a code-grounded Q&A loop under a gitignored .docs/ folder, then synthesizing them into one final Confluence design page. Use when documenting a downloaded fork zip, understanding what changed vs upstream, decomposing squashed PRs into logical commits, identifying the novel architectural pattern, or publishing a fork's mental model to Confluence. Not for forward-looking design (use spec-writer/make-prd), not for PR-time review (use pr-review), not for general repo onboarding (use brief-docs).
---

# fork-audit

Apply this skill when the user says any of: "document this fork", "what changed vs main/upstream", "we downloaded a zip of repo X, audit it", "compare main…feature-branch and write it up", "understand and document this divergent branch", "publish the fork's design to Confluence".

The **final artifact is a single Confluence design page**. Everything else — the layered docs, topic breakouts, diagrams, and Q&A files under a gitignored folder (default `.docs/`) — is **intermediate fan-out material** that exists to drive the final page. The intermediates stay on disk as the audit trail and drill-down reference; the Confluence page is what the team reads.

```
Phase 1–2: diff forensics + inventory
        │
Phase 2.5: subagent fan-out over the diff
        │
Phase 5: fan out intermediates (.docs/)
   ├── L0 exec summary        ─┐
   ├── L1 architect overview   │
   ├── L2 per-commit deep dive │──► Phase 7: synthesize ──► Confluence design page
   ├── topics/<breakouts>      │        (the deliverable)
   ├── diagrams/*.svg          │
   └── Q&A loop (questions.md ─┘
        → answers.md)
```

## When to use vs not

| Use this skill | Use a different skill |
|---|---|
| Documenting a downloaded fork zip | New design from scratch → `make-prd` or `spec-writer` |
| Auditing a divergent branch (main…feature) | Per-PR review comments → `pr-review` |
| Publishing a fork's design page to Confluence, backed by layered exec/architect/engineer intermediates | Short single-page onboarding → `brief-docs` |
| Mermaid for system context, data flow, sequence | Just rendering one diagram → `make-mmd` |
| | Confluence diagram embeds → call `confluence-diagrams` after |

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

5. Confluence target?
   ├─ User gave a page URL/ID → publish the final page there (update in place)
   ├─ User gave a space/parent → create a child page titled "Design" (or user's title)
   └─ No Confluence access / user declines → the synthesis still happens; save it as
      .docs/FINAL-design.md and tell the user it's ready to paste
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

### Phase 5 — Fan out intermediates (`.docs/`)

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

### Phase 6 — Q&A hardening loop

The layered docs describe what the fork *is*; the Q&A loop surfaces what it *doesn't do*. This phase produced the strongest material in practice — the design-gaps section of the final page comes almost entirely from here.

1. **Collect questions** into `questions.md`. Sources, in priority order:
   - The user's own questions (they know their use case; capture them verbatim, typos and all)
   - Questions the layered docs raised but didn't answer (scaling, ops posture, eval coverage, cost)
   - Adversarial questions you generate: "what breaks at 10× scale?", "who reviews the AI output?", "what happens when the upstream API changes shape?"
2. **Answer every question in `answers.md`, citing code.** Each answer names the file:line that backs it. Where the code doesn't address the question, the answer is **"design gap — not implemented"** and gets flagged explicitly. Never paper over a gap with plausible-sounding prose.
3. **Promote cross-cutting gaps** into a numbered list at the end of `answers.md`. For each gap note whether it's *active* (biting today) or *latent* (fires on a trigger), and give the one-line check that would confirm its magnitude (a SQL query, a grep, a log inspection).
4. **Iterate.** New questions that come up while answering go back into `questions.md` (or a `questions2.md`). Stop when a round produces no new gaps.

This loop can run across sessions — the files persist, and later question rounds deepen earlier answers.

### Phase 7 — Synthesize the final Confluence page

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

Template: [templates/confluence-design-page.md](templates/confluence-design-page.md).

### Phase 8 — Verify

- `git status` — output folder is not tracked (it's gitignored)
- `git check-ignore -v <output>/README.md` — confirms ignore rule fires
- All .mmd files have corresponding .svg
- README's reading table lists every file actually produced
- The Confluence page exists at the expected URL, renders its tables, and its version comment names this audit
- Every gap on the final page traces back to a flagged answer in `answers.md`

## Output contract

The Confluence page is the deliverable; each intermediate follows a defined shape. Templates in `templates/`:

| File | Stub | Voice | Key elements |
|---|---|---|---|
| **Confluence design page** (final) | [templates/confluence-design-page.md](templates/confluence-design-page.md) | Q&A vernacular, `/stop-slop`ed | Identity + one-sentence framing; fork-in-one-screen table; request flow; novel pattern; mechanics with surprises; numbers table; numbered gaps; pointer table |
| `README.md` | [templates/README.md](templates/README.md) | Neutral | Reading-by-audience table; one-screen diff summary; "What was written / not written" |
| `L0-executive-summary.md` | [templates/L0-executive-summary.md](templates/L0-executive-summary.md) | Exec | Identity paragraph; Problem · Constraints · Solution table; "What changed vs upstream" 3-column table (PR / files / what it does); "Where to go from here" |
| `L1-technical-overview.md` | [templates/L1-technical-overview.md](templates/L1-technical-overview.md) | Architect (via `/reframe`) | YAML frontmatter + `## Slide:` sections per reframe contract; thesis; core-tension table; component-boundaries diagram; reuse map; NFRs; migration considerations; parking lot |
| `L2-deep-dive.md` | [templates/L2-deep-dive.md](templates/L2-deep-dive.md) | Engineer | Per-PR section with sub-section per logical commit; file table with additions/deletions; key code snippets where the design choice isn't obvious from the diff |
| `topics/<name>.md` | [templates/topic.md](templates/topic.md) | Engineer | Single-purpose; lead with "where it lives" + "why it exists"; diagram link if applicable; "see also" tail |
| `questions.md` / `answers.md` | none (freeform) | Interrogative / verdict | Questions verbatim; answers cite file:line; gaps flagged "design gap — not implemented"; cross-cutting gaps numbered with active/latent status + confirm check |

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
- **The Confluence page is a synthesis, not a concatenation.** Never paste an intermediate onto the page wholesale. Every section is rewritten for the one-page read, and every claim on it traces to an intermediate.
- **Gaps come from the Q&A loop.** Don't write the known-gaps section from intuition; write it from the flagged "design gap — not implemented" answers in `answers.md`. If the loop hasn't run, run it first.
- **Never link gitignored intermediates from the Confluence page as if they resolve.** Name them ("the local `.docs/answers.md` analysis") so readers know the audit trail exists, but only hyperlink things a reader can open: in-repo docs, other Confluence pages, PRs.

## Companion files

| File | Use when |
|---|---|
| [templates/confluence-design-page.md](templates/confluence-design-page.md) | Synthesizing the final Confluence page (Phase 7) |
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
- [ ] `questions.md` + `answers.md` exist; every answer cites code or is flagged as a design gap
- [ ] The Q&A loop ran until a round produced no new gaps
- [ ] The Confluence page is published (or `.docs/FINAL-design.md` exists if no Confluence access), synthesized fresh, and every gap on it traces to `answers.md`
- [ ] If `/stop-slop` is available, the final page and intermediates have been run through it

## Composition with other skills

| Step | Skill |
|---|---|
| Architect-layer reframing | `/reframe architect <assembled-source>` (produces L1) |
| Diagram authoring | `/make-mmd` for fresh diagrams; this skill embeds the conventions inline |
| Diagram embeds on the final page | `/confluence-diagrams` after publishing |
| Final prose polish | `/stop-slop` — mandatory on the Confluence page, per-file on intermediates |
| Handoff to next session | `/handoff` — point the new agent at `.docs/README.md` and the Confluence page URL |
