---
name: fork-audit
description: Audits and documents a forked or divergent codebase: layered docs (exec / architect / engineer), topic breakouts, and a code-grounded Q&A loop under a gitignored .docs/ folder, synthesized into one Confluence design page. Use when documenting a fork, understanding what changed vs upstream, decomposing squashed PRs, or publishing a fork's mental model. Not for forward-looking design (use spec-writer/make-prd), PR review (use pr-review), or repo onboarding (use brief-docs).
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

Eight phases. Read [references/workflow-phases.md](references/workflow-phases.md) for the detail of the phase you are in (commands, tables, envelope, gotchas); it is not needed to pick a path.

| Phase | Goal / output | Gate |
|---|---|---|
| 1 Diff forensics | Resolve base/head/merge-base; list divergent commits, per-PR metadata, file-group counts | Refs verified from head's own history (never trust cross-fork `gh api compare`) |
| 2 Inventory + style anchor | Classify groups as added/removed/modified/unchanged; extract narrative pattern from any anchor doc | Inventory covers both base and head |
| 2.5 Fan-out | Partition large diffs (>~100 files, >3 top-level dirs, >3 commits, >~10k LOC) across parallel subagents returning one fixed envelope; parent re-merges. Skip for small diffs | Each envelope has "what this didn't cover" resolved |
| 3 Analytical framework | Answer the identity, decomposition, novel-pattern, reuse, NFR and merge-risk questions; split app-specific from platform ride-along | Every planned doc traces to an answer |
| 4 Silent repo init | Optional: `git init`, no remote, output folder gitignored first | Remote list empty |
| 5 Intermediates | Write `.docs/` set: L0, L1 (via `/reframe architect`), L2, topics, diagrams, README last | Generation order followed |
| 6 Q&A loop | `questions.md` to `answers.md`, code-cited, gaps flagged "design gap — not implemented" | A round yields no new gaps |
| 7 Synthesize | One fresh Confluence page from the intermediates, `/stop-slop`ed, template [templates/confluence-design-page.md](templates/confluence-design-page.md) | Not a concatenation; every gap traces to `answers.md` |
| 8 Verify | Gitignore fires, every .mmd has .svg, README complete, page renders | Checklist passes |

Read the reference file when starting Phase 1 (gotcha), Phase 2.5 (triggers, partitions, envelope, re-merge), Phase 5 (folder tree, order), Phase 6 and Phase 7 (source-to-section table).



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
| [references/workflow-phases.md](references/workflow-phases.md) | Executing any phase in detail |
| [references/diagrams-and-checklist.md](references/diagrams-and-checklist.md) | Drawing diagrams (Phase 5) and the final quality checklist (Phase 8) |

## Composition with other skills

| Step | Skill |
|---|---|
| Architect-layer reframing | `/reframe architect <assembled-source>` (produces L1) |
| Diagram authoring | `/make-mmd` for fresh diagrams; this skill embeds the conventions inline |
| Diagram embeds on the final page | `/confluence-diagrams` after publishing |
| Final prose polish | `/stop-slop` — mandatory on the Confluence page, per-file on intermediates |
| Handoff to next session | `/handoff` — point the new agent at `.docs/README.md` and the Confluence page URL |
