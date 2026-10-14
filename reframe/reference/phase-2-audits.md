# Phase 2 Audits

Run these during Phase 2 (Reframe) when the trigger applies.

## Contents

- Runtime-agnostic naming pass: source covers multiple runtimes or vendors
- Multi-mode comparison tables: source covers more than one run mode
- Doc fan-out audit: several pages cover the same feature
- Hub-shedding audit: one page carries too much
- Confluence comment-anchor preservation: editing a Confluence page with inline comments

## Runtime-agnostic naming pass

When the source material covers multiple runtime modes or vendor
choices (e.g. process / Docker Compose / kind+helm; local runtime /
self-hosted server / cloud API), apply this pass before structure selection:

1. **Identify the abstraction name** — the role-based noun the
   feature plays: "model runtime", "chat stack", "inference
   endpoint", "OpenAI-compatible provider". Use it in the
   primary narrative.
2. **Demote vendor / runtime tokens** — `Vendor A runtime`,
   `Ollama`, `<host>:<port>` go in a feature table
   row labeled by mode, never in the prose backbone.
3. **Mermaid node labels follow the same rule.** A node labeled
   "Vendor A runtime" in an architecture diagram for a
   runtime-agnostic stack is a self-contradiction; relabel to the
   role ("LLM runtime — OpenAI-compatible endpoint") with the
   binding env var as the secondary label.
4. **Mode-specific subsections are explicit.** When you genuinely
   need runtime-specific content, put it under a subsection whose
   heading names the mode ("Mode: Vendor A runtime",
   "Runtime: Ollama"). The reader can scope-read; the abstract
   narrative stays clean.

The reframe output that ships with a vendor token in the title or a
runtime-specific Mermaid node in the primary diagram fails this skill.

## Multi-mode comparison tables

If the source covers more than one run mode but does not include a
side-by-side comparison table, generate one during Phase 2. The
table rows are at minimum:

| Aspect | Mode A | Mode B | Mode C |
|---|---|---|---|
| Startup command | … | … | … |
| Base URL the consumer sees | … | … | … |
| Ports exposed on host | … | … | … |
| Key env vars | … | … | … |
| External-dep plumbing (LLM, MCP, DB) | … | … | … |
| Teardown / cleanup | … | … | … |

If a cell is unknown, mark it `[TO BE DOCUMENTED]` — surface the
gap rather than guessing. The comparison table is what makes
multi-mode docs scannable; without it, the reader has to
reconstruct the comparison from mode-specific subsections.

## Doc fan-out audit

Before finalizing, check whether the source directory has more
than one standalone page covering the same feature (e.g.
`local-dev.md` *and* `docker-compose.md` *and* `runtime-modes.md`
all describing the same chat stack). If so, the reframe output
either:

- Picks the canonical hub and folds the rest into mode-specific
  subsections of that hub, or
- Explicitly labels the others as satellites with prominent
  links back to the hub.

A reframe that adds a fourth parallel page increases the doc-rot
surface; it doesn't help the audience.

## Hub-shedding audit (the inverse fan-out)

The fan-out audit above catches too many pages. This one catches
one page carrying too much. When a single hub has absorbed the job
of its own children (one section runs past ~70% of the body, the
page needs scrolling to reach the decision or the open questions),
reframe pushes the heavy blocks down, not sideways:

1. **Measure before cutting.** Count words per section. A block
   that dominates the page and answers a question the reader came
   to a *different* page for is the move candidate. Apply the test:
   did the reader open the hub to learn *this*, or to find out
   *where* to learn it? A 7-by-4 comparison matrix fails that test
   on a hub and passes it on the comparison page.
2. **Push into existing children first.** Fold the block into the
   child that already owns that job (the source-only core into the
   build-out page, the orchestrator matrix into the architectures
   page). Create a new child only when no child owns the topic.
3. **Reshape on arrival, don't dump.** Moving a wall of text to
   another page relocates the overwhelm. Regroup the block to the
   destination's structure (six flat bullets become three grouped
   ones; a prose list of options becomes a table).
4. **Leave a gist plus a link.** The hub keeps a two or three line
   summary and a link to the child, so a hub reader still gets the
   answer's shape without the full block.

The target is a hub that reads as orientation: what this is, what
is decided versus open, where to go for depth.

## Confluence comment-anchor preservation

Restructuring a Confluence page orphans any inline comment anchored
to text you move or delete. The anchor is a marker wrapped around a
specific phrase in the storage XML, not a position, so rewording or
relocating that phrase breaks it silently. Before editing a page
that has inline comments:

1. **Read the storage format first.** Fetch the page with
   `convert_to_markdown=false` and find the
   `ac:inline-comment-marker` elements. The phrase each one wraps is
   the live anchor. Do not assume an anchor sits where the rendered
   text suggests; a comment can be pinned to a heading or a mid-list
   sentence that your edit is about to move.
2. **Keep anchored phrases on the page verbatim** when the section
   they live in survives. A section-scoped edit that rewrites the
   anchored sentence orphans the comment even if the section stays.
3. **Re-anchor deliberately when the text has to move.** Add a fresh
   inline comment carrying the original question and author
   attribution, anchored to surviving text (an Open-items entry that
   states the same question works well), and note in the body that a
   restructure moved the original anchor. This mirrors the
   tombstone-comment pattern teams already use.
4. **Verify after.** Re-fetch the comments and confirm the live copy
   attaches to real page text; expect the orphaned originals to
   remain as resolvable tombstones.

Section-scoped update tools help here: they replace one section's
body and leave other sections, macros, and their anchors intact,
which a full-page download-edit-reupload round trip does not.
