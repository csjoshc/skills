---
name: stop-slop
description: >-
  Remove AI writing patterns from prose. Use when drafting, editing, or reviewing
  text to eliminate predictable AI tells; detect mode audits without rewriting;
  also when explaining scoped technical work in plain vernacular
  (what/why/evidence, tests vs live proof) for readers unfamiliar with the codebase.
metadata:
  trigger: >-
    Writing prose, editing drafts, reviewing content for AI patterns;
    plain-vernacular technical explainers, remediation writeups, evidence tables
  author: Hardik Pandya (https://hvpandya.com)
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## Modes

**Edit (default).** Apply the rules below with the minimum effective edit. Fix slop, errors, and unclear passages; leave strong human sentences alone. Preserve the writer's meaning, vocabulary, cadence, and edge (blunt language, humor, honest admissions). A rough draft with a real voice should sound like the same person after editing. Strictness rules below (adverbs, em dashes) still apply.

**Detect.** When asked to audit, scan, or flag a draft without rewriting: name each pattern found, quote the offending line, give the fix in a few words. Do not rewrite or guess whether AI wrote it. Named patterns are evidence the reader can check; offer to edit afterward.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, and all adverbs. See [references/phrases.md](references/phrases.md).

2. **Break formulaic structures.** Avoid binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency. See [references/structures.md](references/structures.md).

3. **Use active voice.** Every sentence needs a human subject doing something. No passive constructions. No inanimate objects performing human actions ("the complaint becomes a fix").

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work. No architectural metaphors ("seam," "layer," "pipeline," "single source of truth," "first-class," "load-bearing," "non-trivial") that substitute for a concrete name — name the class, function, file, or interface. If a doc claims to be runtime- or vendor-agnostic, scan it for product names ("Vendor A runtime," "Ollama") that contradict the claim.

5. **Apply the portability test.** If a sentence could move unchanged to another person, company, country, or product, it is filler. Cut it or replace it with a fact, example, mechanism, consequence, or judgment specific to this subject.

6. **Put the reader in the room.** No narrator-from-a-distance voice. "You" beats "People." Specifics beat abstractions.

7. **Vary rhythm.** Mix sentence lengths. Two items beat three. End paragraphs differently. No em dashes.

8. **Trust readers.** State facts directly. Skip softening, justification, hand-holding. No summary-recap endings; end on the last concrete point or next action.

9. **Cut quotables.** If it sounds like a pull-quote or a mic-drop kicker, delete it and end on the clearest concrete sentence already in the draft.

## Quick Checks

Before delivering prose:

- Any adverbs? Kill them.
- Any passive voice? Find the actor, make them the subject.
- Inanimate thing doing a human verb ("the decision emerges")? Name the person.
- Sentence starts with a Wh- word? Restructure it.
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Any "not X, it's Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Banned word (delve, leverage, robust, tapestry, transformative...)? Replace. See references/phrases.md.
- Faux-insight setup ("what nobody tells you")? Cut the setup, keep the claim.
- Colon reveal ("The best part: it learns")? Rewrite as a plain sentence.
- Trailing "-ing" analysis ("..., highlighting the team's commitment")? Replace with the actual consequence.
- Puffery ("marks a pivotal moment") or weasel attribution ("experts agree")? State the fact; name the source or cut.
- Synonym cycling (agent/assistant/tool for the same thing)? Repeat the clear word.
- Ends with "In conclusion" or a recap? Cut; end on the last concrete point.
- Sentence portable to any company/product unchanged? Filler; cut or make it specific.
- Narrator-from-a-distance ("Nobody designed this")? Put the reader in the scene.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.

## Scoring

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |
| Voice | Would the writer recognize it as their own? |

Below 42/60: revise.

## Examples

See [references/examples.md](references/examples.md) for before/after transformations.

## Plain vernacular technical explainers

When explaining scoped technical work to readers unfamiliar with the codebase (relevance, design choices, implications, evidence), follow [references/plain-vernacular-explainers.md](references/plain-vernacular-explainers.md). Voice still follows Core Rules above; that reference adds audience, what/why/evidence structure, and evidence honesty (tests vs live PR).

## License

MIT
