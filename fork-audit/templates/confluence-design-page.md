# <Page title, usually "Design">

<!--
The FINAL artifact of a fork-audit. One page, 10-minute read, synthesized fresh
from the .docs/ intermediates — never a concatenation of them.

Voice: Q&A vernacular + /stop-slop. Direct verdicts, concrete values, gaps stated
as gaps. Tables where the content is tabular. No em dashes, no filler.

Publish with confluence_update_page, content_format: markdown, table_layout: wide.
-->

This page is the working mental model for `<org>/<fork-repo>`, the <fork name>. It is a fork of [<upstream name>](<upstream Confluence page or repo URL>) (`<upstream-repo>`). The upstream is the platform: <what the platform provides>. This repo ships <what the fork adds>. Everything below cites the code; where the code doesn't do something, the line says so.

**One sentence:** <the whole system as a plain-vernacular sentence, e.g. "an ETL + vector database + RAG app: X comes in from Y, gets enriched by Z, and a chat UI answers over that corpus.">

## The fork in one screen

<!-- Source: L0 / README diff table -->

| PR | What it does | Size |
|---|---|---|
| #N | <one line> | <n> files |

<One short paragraph on what the fork reuses vs replaces from the platform, and the one structural difference worth knowing up front.>

## How <the primary use case> works

<!-- Source: L2 + request-flow diagram/topic. Numbered steps, one round trip. -->

1. <User action>
2. <System step, naming the function/file that does it. State what does NOT happen too: "No query rewriting. No re-ranking.">
3. ...

<Closing facts the reader will misassume otherwise: memory windows, session-length assumptions, thresholds.>

## <The novel pattern> 

<!-- Source: topics/<novel-pattern>.md. The structurally new thing, not the biggest file group. -->

| Stage | Table/component | What happens |
|---|---|---|

<Ops posture in plain terms: how it runs today (CLI? scheduled?), what's acknowledged as the next step.>

## <Mechanics section(s)>

<!-- Source: answers.md deep-technical answers. Lead with the surprise if there is one:
     "the index you'd expect isn't there", "the primary path is the slow one". -->

## Numbers to remember

<!-- Source: answers.md + topic operational notes -->

| Operation | Figure |
|---|---|

## Known gaps

<!-- Source: answers.md cross-cutting gaps, verbatim in substance. Each was flagged
     "design gap — not implemented" during the Q&A loop. Note the scale/trigger at
     which each becomes a blocker. -->

Each of these is a defensible scope cut for <current scale>. They become blockers if <scaling condition>.

1. **<Gap>.** <One-line consequence.>

<Pointer to the second-tier audit findings: name the local analysis file (do not hyperlink gitignored files), note it carries the confirm-check for each item.>

## Where the deeper docs live

| To understand | Read |
|---|---|
| <topic> | <in-repo canonical doc / Confluence page / spec path> |
