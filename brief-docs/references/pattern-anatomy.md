# Pattern anatomy — brief docs

## Contents

- [Summary](#summary)
- [Follow-up](#follow-up)
- [Optional blocks](#optional-blocks)
- [Hub page](#hub-page)
- [Satellite page](#satellite-page)
- [Headings and scanability](#headings-and-scanability)
- [Tables vs prose](#tables-vs-prose)
- [Mermaid](#mermaid)

## Summary

- **First section** after the H1 (or first content on a wiki page).
- **One to three sentences**, or one tight paragraph—fits above the fold.
- Start with **`Summary:`** in bold (Markdown) or an equivalent panel/callout label so skimmers see the contract.
- State **what** the thing is, **who** it is for (if non-obvious), and **boundaries** (what is out of scope in this page).

## Follow-up

- Label **`Follow-up:`** in bold.
- Mechanics, sequence, file paths, edge cases, and “how it works” live here—not in Summary.
- Use **relative links** to code and sibling docs. Prefer **one primary link** per claim when pointing to implementation.

## Optional blocks

- **`Run locally:`** (or **Quick start:**) — numbered or bulleted commands only; no narrative.
- **`More detail:`** — single line of **inline links** separated by middots or bullets, for hub pages.
- **`See also:`** — cross-repo or external links.

## Hub page

- H1 = product or doc area name.
- **Summary** names the whole subsystem and trust boundaries (e.g. what talks to what).
- **Run locally** or equivalent if developers are the audience.
- **More detail** lists satellites in **reading order** or **by concern** (architecture, network, env, debug).

## Satellite page

- Same **Summary / Follow-up** pattern.
- Title answers **one concern** (e.g. “URLs and ports”, “Secrets and environment”).
- End with **See also** pointing back to hub and related satellites.

## Headings and scanability

- Use **H1 once**, then **H2** for major sections. Avoid deep nesting (H4+ rare).
- **Bold** API paths, env var names, service names, and critical negatives (“never commit values”).
- Avoid long prose paragraphs; **split** at logical breaks or use bullets.

## Tables vs prose

- Use **tables** for **lookup** content: ports, env names, artifact paths, matrix of who owns what.
- Keep tables **narrow** (few columns). If a cell needs a paragraph, the row may deserve its own satellite page.
- Do **not** duplicate the same table on hub and satellite—**link** to the canonical page.

## Mermaid

- **At most one** diagram per page for standard docs. If two diagrams differ by **audience** (e.g. deploy vs dev), split pages.
- Prefer **small** flowcharts (LR or TB) over large sequence diagrams unless sequence is the teaching goal.
- Follow project or renderer rules: no spaces in node IDs, quote edge labels with special characters.
- If your wiki stores diagrams as separate attachments, **one** embed or link from the brief page; do not duplicate full ASCII art and Mermaid for the same flow.
