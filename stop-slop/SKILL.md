---
name: stop-slop
description: "Edits prose to remove formulaic AI patterns while preserving the writer's meaning and voice, or audits prose without rewriting. Use when asked to de-slop text or explain technical work in plain language."
---

# Stop Slop

Edit prose to remove formulaic habits while keeping its meaning and the writer's voice.

## Modes

**Edit (default).** Read the whole passage, then make the smallest set of useful changes. Keep strong sentences, deliberate style, uncertainty, humor, and bluntness. Fix unclear or unsupported claims only when the source lets you do so; otherwise flag the gap or ask for the missing detail. Treat a pattern as evidence to inspect, not an automatic edit.

**Detect.** When asked to audit without rewriting, quote each passage that shows a pattern, name the pattern, and give a short suggested fix. Do not infer whether AI wrote it. Stop after the findings.

## Editing process

1. **Read for meaning and voice.** Note the audience, purpose, claims, and any writing sample. A sample sets the voice and can justify patterns that would otherwise look formulaic.
2. **Mark patterns by strength.** Edit a strong tell on one clear instance. Edit a weak tell when it repeats or appears alongside other signs. See [references/phrases.md](references/phrases.md) and [references/structures.md](references/structures.md).
3. **Rewrite at the right scale.** Remove filler directly. For larger patterns, rewrite the sentence or paragraph around its point instead of patching isolated words. Preserve meaningful contrasts, lists, emphasis, and formatting.
4. **Check meaning and voice.** Compare the rewrite with the source. Keep every supported claim unless a redundant line adds nothing; add no facts, names, numbers, dates, quotes, or citations. Restore intentional language the edit flattened.
5. **Return the requested form.** For pasted text, provide the rewrite and, when useful, a brief note on major edits. For file edits, change prose only and summarize the changes. For embedded use in a PR, commit message, or document, return only the final text.

The edit is complete when each change removes an identifiable problem, the source's claims remain intact, and the result still fits the writer and audience.

## Core guidance

1. **Remove empty words and stock phrasing.** Cut throat-clearing, emphasis crutches, puffery, and adverbs that add no meaning. Keep words that carry scope, timing, degree, or voice.
2. **Replace formula with the point.** Watch for staged openers, false contrasts, negative run-ups, forced triads, dramatic fragments, repeated closers, and ornamental formatting. Keep a construction when both sides add information or the writer uses it deliberately.
3. **Name actors when it helps.** Prefer active voice when it makes responsibility or action clearer. Keep passive voice when the actor is unknown, irrelevant, or less important than the result. Give human agency to people, not abstractions.
4. **Be concrete.** Replace vague claims with a source-backed fact, example, mechanism, consequence, or judgment. Avoid lazy extremes and architectural metaphors when they hide the actual class, function, file, or interface. Check vendor or runtime names when a document claims to be agnostic.
5. **Check portability.** If a sentence could move unchanged to another subject, see whether it contributes a useful general principle. Cut generic filler; ground useful advice in this subject.
6. **Respect the reader.** State the point without a narrator hovering over the text. Use "you" when it puts the reader in the actual situation, not as a blanket replacement for "people."
7. **Follow the writer's rhythm.** Vary sentence shape where the prose feels mechanical. Do not ban punctuation, sentence lengths, or list sizes; check whether the pattern earns its place.
8. **End when the point is complete.** Remove recap endings and quotable kickers that repeat the argument. Keep a final sentence that adds a consequence or next step.
9. **Keep artifacts self-contained.** In committed prose, explain what a thing does instead of relying on private ticket IDs, gate names, or team-local codenames. Commit messages may retain IDs for traceability.
10. **Keep code comments close and short.** Put a comment beside the line it explains and state the non-obvious reason. Move longer design rationale to a design document or commit message; leave a brief pointer when needed. See [Atwood](https://blog.codinghorror.com/when-good-comments-go-bad/) and [comment length discussion](https://www.quora.com/What-is-the-ideal-length-for-code-documentation-comments).

## Final review

Check the rewrite against these questions. Treat them as prompts, not a scorecard.

- Did any change remove a real qualification, contrast, joke, or point of view?
- Did the rewrite add, drop, or alter a claim, name, number, date, quote, citation, or causal relationship?
- Does an opener announce a point instead of making it?
- Do repeated structures, triads, fragments, dashes, or bold labels sound automatic here?
- Does each vague or inflated sentence name what happened and who or what did it?
- Does the ending add information, or repeat what the reader already knows?
- Does the result still sound like this writer addressing this reader?

## References

See [examples](references/examples.md) for transformations. For technical explainers, follow [plain vernacular guidance](references/plain-vernacular-explainers.md). For prose the user will present as their own, also follow [user voice](references/user-voice.md).

## License

MIT
