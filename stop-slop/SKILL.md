---
name: stop-slop
description: "Edits prose to remove formulaic AI patterns while preserving the writer's meaning and voice, or audits prose without rewriting. Use when asked to de-slop text or explain technical work in plain language."
---

# Stop Slop

Edit prose to remove formulaic habits while keeping its meaning and the writer's voice.
Hollow prose fails before style does, so fix missing substance before surface patterns.

## Modes

**Edit (default).** Read the whole passage, then make the smallest set of useful changes. Keep strong sentences, deliberate style, uncertainty, humor, and bluntness. Treat a pattern as evidence to inspect, not an automatic edit.

**Detect.** When asked to audit without rewriting, start with the piece-level diagnosis, then quote each passage that shows a pattern, name the pattern, and give a short suggested fix. Separate a material error from a likely improvement and from taste. Do not infer whether AI wrote it, and do not produce a replacement draft. Stop after the findings.

## Safeguards

These apply in both modes.

1. **Preserve truth and attribution.** Add no facts, names, numbers, dates, quotes, citations, causal claims, or first-person experience. Don't strengthen a claim: `may` stays `may`, and `the study found`, `the vendor says`, and `I think` stay attached to their claims.
2. **Mark gaps with `[TK: question]`.** When the point depends on a fact only the writer has, ask for it or leave the marker. Cut a sentence that only gestures at a point instead of marking it. When the user wants only the final text, leave no markers. A plain true sentence beats a vivid invented one.
3. **Make the least invasive change that solves the request.** A polish doesn't authorize a new argument, and shortening doesn't authorize dropping conditions.

## Match the register

Before editing, name the reader, what they should know or do afterward, and the register. The register sets what the prose owes:

| Register | Owes | Protect |
|---|---|---|
| Argument (essay, design proposal) | A position and its strongest real limitation | Voice, honest uncertainty |
| Explanation | An accurate mechanism at the reader's level | Terms of art, examples |
| Guide, docs | Correct steps, prerequisites, conditions, failure states | Headings, numbered steps, code, warnings |
| Reference, API | Accurate, consistent, scannable entries | Repeated entry structure, tables, normative words |
| Message (PR, commit, Slack, email) | The request, decision or update, owner, next action | Expected politeness, useful bullets |

Only an argument owes a disputable claim. In docs and reference pages, predictable structure is a feature; don't vary it to look less templated. Explicit user requirements and house style outrank this table.

## Editing process

1. **Read for meaning and voice.** Inventory the claims, examples, terms, links, conditions, and any writing sample. A sample sets the voice and can justify patterns that would otherwise look formulaic.
2. **Diagnose the largest problem first,** in this order: missing substance, wrong register, weak development, then surface patterns. Weak development means paragraphs that could swap places or relations the text implies but never states. If the draft is hollow, with no source, mechanism, example, or judgment behind it, say so in two or three sentences and ask up to three questions that would fill it. If the user still wants the rewrite, deliver it and say what editing couldn't repair.
3. **Mark patterns by strength.** Edit a strong tell on one clear instance. Edit a weak tell when it repeats or appears alongside other signs. See [references/patterns.md](references/patterns.md).
4. **Rewrite at the right scale.** Remove filler directly. For larger patterns, rewrite the sentence or paragraph around its point instead of patching isolated words. Preserve meaningful contrasts, lists, emphasis, and formatting.
5. **Check once, repair once.** Compare the rewrite with the source against the final review below. Fix the weakest issue, then stop; repeated passes flatten the prose into one register.
6. **Return the requested form.** For pasted text, provide the rewrite, a brief note on major edits when useful, and any `[TK]` questions. For file edits, change prose only, keep code, frontmatter, and link targets, and summarize the changes. For embedded use in a PR, commit message, or document, return only the final text.

The edit is complete when each change removes an identifiable problem, the source's claims remain intact, and the result still fits the writer and audience.

## Core guidance

1. **Remove empty words and stock phrasing.** Cut throat-clearing, emphasis crutches, puffery, and adverbs that add no meaning. Keep words that carry scope, timing, degree, or voice.
2. **Replace formula with the point.** Watch for staged openers, false contrasts, negative run-ups, forced triads, dramatic fragments, repeated closers, and ornamental formatting. State the claim without the cadence; if nothing specific remains, the formula was hiding a missing point. Keep a construction when both sides add information or the writer uses it deliberately.
3. **Say the relation.** When two sentences sit side by side as if one causes the other, supply the connector (`because`, `although`, `so`). If that would invent the relation, it was never there.
4. **Name actors when it helps.** Prefer active voice when it makes responsibility or action clearer. Keep passive voice when the actor is unknown, irrelevant, or less important than the result. Give human agency to people, not abstractions.
5. **Be concrete.** Replace vague claims with a source-backed fact, example, mechanism, consequence, or judgment. Avoid lazy extremes and architectural metaphors when they hide the actual class, function, file, or interface. Check vendor or runtime names when a document claims to be agnostic.
6. **Check portability.** If a paragraph could move unchanged into someone else's piece on the same subject, see whether it contributes a useful general principle. Cut generic filler; ground useful advice in this subject.
7. **Respect the reader.** State the point without a narrator hovering over the text. Use "you" when it puts the reader in the actual situation, not as a blanket replacement for "people."
8. **Follow the writer's rhythm.** Vary sentence shape where the prose feels mechanical. Do not ban punctuation, sentence lengths, or list sizes, and do not add roughness to look human.
9. **End when the point is complete.** Remove recap endings and quotable kickers that repeat the argument. Keep a final sentence that adds a consequence or next step.
10. **Keep artifacts self-contained.** In committed prose and code comments, replace private ticket IDs, gate names, or team-local codenames with what the code or change does. Commit messages may retain IDs for traceability.
11. **Keep code comments close and short.** Put a comment beside the line it explains and state the non-obvious reason. Move longer design rationale to a design document or commit message; leave a brief pointer when needed. See [Atwood](https://blog.codinghorror.com/when-good-comments-go-bad/) and [comment length discussion](https://www.quora.com/What-is-the-ideal-length-for-code-documentation-comments).

## Final review

Check the rewrite against these questions. Treat them as prompts, not a scorecard.

- Did any change remove a real qualification, contrast, joke, or point of view?
- Did the rewrite add, drop, strengthen, or alter a claim, name, number, date, quote, citation, condition, link, or causal relationship?
- Is each gap marked with `[TK]` or a question instead of filled in?
- Does the medium still work: procedures scan, warnings stay visible, messages state the ask?
- Does the rewrite reproduce a pattern it removed, under different punctuation?
- Does an opener announce a point instead of making it?
- Does each vague or inflated sentence name what happened and who or what did it?
- Does the ending add information, or repeat what the reader already knows?
- Does the result still sound like this writer addressing this reader?

## References

See [examples](references/examples.md) for transformations. For technical explainers, follow [plain vernacular guidance](references/plain-vernacular-explainers.md). For prose the user will present as their own, also follow [user voice](references/user-voice.md).

Safeguards, register table, and diagnosis order adapted from https://github.com/addyosmani/clarity @ e27ceef (MIT).

## License

MIT
