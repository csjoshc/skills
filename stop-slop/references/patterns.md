# Patterns to Inspect

<!-- diagnoses adapted from addyosmani/clarity references/edit.md @ e27ceef (MIT) -->

Read the passage before classifying a pattern.
A strong tell can justify an edit on one clear instance; a weak one needs repetition or another tell.
Treat every list here as a search aid, not a ban.
Keep quoted text, proper names, terms of art, and an ordinary word used accurately.
Don't swap one watched word for a synonym; rewrite the claim or leave it alone.

## Contents

- Substance and claims: importance without mechanism, specific-looking vagueness, vague attribution, lazy extremes, architectural metaphors, vendor names in agnostic docs
- Formula and structure: formula carrying the argument, decorative tails, abstract actors, narrator from a distance, structural regularity, endings
- Surface residue: words, openers and meta, empty adverbs, jargon, fake-strong verbs, synonym cycling, rhythm, formatting
- Preserve human material
- Put craft back

## Substance and claims

### Importance without mechanism

The sentence claims magnitude instead of showing what happens.

```txt
Watch: pivotal, crucial, transformative, stands as a testament, marks a pivotal moment,
       plays a vital role, underscores the importance, the stakes are high,
       the implications are significant, the reasons are structural, this is genuinely hard,
       this is what X actually looks like
Test:  remove the emphasis. Does the rest name an actor, mechanism, result, or limit?
Fix:   state the supported mechanism or fact and let the reader judge its importance.
```

"Marks a pivotal moment" becomes "The launch is the company's first paid product."
Keep an evaluative word when the same passage supplies the evidence that earns it.
`Robust` belongs in a sentence that names the failure handling, not in "a robust approach."

### Specific-looking vagueness

An anecdote can have the grammar of an example and the content of an abstraction: "a package once caused a security problem."
Ask which package, what happened, and how it was caught.
If the source doesn't say, use `[TK: question]` or cut the anecdote; never fill the gap yourself.

### Vague attribution and false precision

```txt
Watch: experts agree, studies show, many argue, widely regarded as, industry reports suggest
Fix:   name the supplied source, keep its uncertainty, ask for it, or cut the claim.
```

Don't turn association into causation, `may` into `will`, `some` into `most`, or a vendor's claim into narrator fact.
A more confident sentence isn't automatically a clearer one.

### Lazy extremes

`every`, `always`, `never`, `everyone`, `nobody` claim authority the source rarely has.
Use the actual scope when the source gives it; keep the word when it's literally true.

### Architectural metaphors

These sound specific while hiding the mechanism.
Name the file, class, function, or interface when the prose needs it and the source provides it.
Keep a metaphor when it communicates more clearly than the implementation name.

| Avoid | Replace with |
|---|---|
| "The centralized seam" | The class or function: "the `apply_llm_env_overrides` function" |
| "Single source of truth" | The authority: "the values in `config/llm-defaults.env`" |
| "First-class" | The property: "errors are returned, not raised" |
| "Load-bearing" | What depends on it: "the `localhost` token in `server_name` matches the default block's Host" |
| "Non-trivial" | The complexity: "three nested `if` branches handling stream/blocking/error" |
| "Out-of-the-box" | The default: "the `LLM_RUNTIME=ollama` default ships with..." |
| "By design" | The spec: "Per `docs/ADR-CHAT-1.md`, this is intentional because..." |
| "Battle-tested" | The usage: "X has run in prod since YYYY-MM-DD across N services" |
| "Cleanly" / "elegantly" | Cut, or name the property worth naming |
| "Modular" / "extensible" | The extension point: "new providers register via `create_provider(name, ProviderClass)`" |

### Vendor names in agnostic docs

If a doc claims a runtime-, vendor-, or platform-agnostic feature, scan it for product names that contradict the claim.

| Token | Write instead |
|---|---|
| "Ollama", "Vendor A runtime" | "Local model runtime" or "OpenAI-compatible endpoint" |
| "<host>:<port>" in an abstraction-level doc | "the host-side runtime URL (see `LLM_BASE_URL`)" |
| "nginx" when the proxy is swappable | "reverse proxy" |
| "Postgres" / "Redis" when storage is configurable | "persistent store" / "cache" |
| Pinned source refs (`hf.co/unsloth/...`) | The alias from the catalog file |

Vendor names belong in adapter modules, `runtime:` / `provider:` selector values, and per-runtime sections labeled as such.
Anywhere else they assert a coupling the doc denies.

## Formula and structure

### Formula carrying the argument

Common forms:

| Pattern | Example |
|---|---|
| Binary contrast | "Not because X. Because Y." / "The answer isn't X. It's Y." / "not just X but also Y" |
| Negative listing | "It wasn't X. It wasn't Y. It was Z." |
| Faux-insight setup | "What most people get wrong:" / "Here's what nobody tells you" |
| Colon reveal | "The detail that makes it work: a separate agent grades it." |
| Rhetorical setup | "What if [reframe]?" / "Think about it:" / "And that's okay." |
| Dramatic fragments | "[Noun]. That's it. That's the [thing]." / "X. And Y. And Z." |
| Forced triad | Three items where the third adds nothing |
| Question answered at once | "Why does this matter? Because..." |
| Narrative template | "By the time X, I was Y." |

Run two tests:

1. **Flatten test:** state the claim without the cadence. If nothing specific remains, the formula was doing the missing reasoning's work.
2. **Relation test:** restate the implied link with `because`, `although`, `when`, `if`, or `so`. "The benchmark is saturated. The model still fails in production." becomes "Although the benchmark is saturated, the model still fails in production, so the benchmark no longer measures what ships." If you'd have to invent the relation, the original only suggested one.

"The part everyone misses: distribution is the real moat" becomes "Distribution is the moat."
Keep an earned contrast, a concrete three-item list, a deliberate fragment, or a memorable line.
Change repeated or unsupported use, not the device itself.

### Decorative tails

Trailing `-ing` clauses that gesture at meaning: "highlighting," "underscoring," "reflecting," "showcasing," "fostering."
"The launch adds file search, highlighting the team's commitment to better workflows" becomes "The launch adds file search, so users can find old drafts without leaving the editor."

### Abstract actors

Complaints don't become fixes, decisions don't emerge, and data doesn't speak; someone fixes, decides, or reads.
Name the person, team, system, or documented process when that makes responsibility clearer.
Keep ordinary shorthand like "the market grew," and keep passive voice when the actor is unknown, irrelevant, protected, or less important than the result.

### Narrator from a distance

"Nobody designed this," "This is why...," and "People tend to..." float above the scene.
Ground the claim in the reader's situation when that helps; use "you" only when it fits the audience.

### Structural regularity

Inspect the piece's dominant shape, not isolated words:

- sections with identical length and internal order;
- paragraphs that could trade places without changing the argument;
- headings doing all the organizing;
- every example interpreted for the reader;
- every paragraph ending on a line built to be quoted.

Fix only the dominant problem: merge or move material, let one section carry more weight, or name the relation at a weak join.
Don't add a tangent, a loose thread, or sentence-length wobble just to look irregular.
In docs and reference pages, repeated entry structure is a feature.

### Endings

Inspect "In conclusion," "Ultimately," "Overall," "Looking ahead," and final paragraphs that restate the piece.
Cut a closing aphorism or mic-drop that only repeats the point.
End on the last concrete point, consequence, or next action.

## Surface residue

### Words to inspect

delve, foster, leverage, utilize, facilitate, empower, streamline, robust, seamless, cutting-edge, groundbreaking, unlock, paradigm shift, game changer, tapestry, realm, landscape, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness, ever-evolving, "this is huge," "this changes everything."

Replace one when a plainer, more exact word keeps the meaning.
Keep it when it names a real property or fits the writer's voice.

### Openers, emphasis, and meta

| Kind | Examples |
|---|---|
| Throat-clearing | "Here's the thing:", "Here's why X", "The truth is,", "It turns out", "Let me be clear", "Can we talk about" |
| Emphasis crutches | "Full stop.", "Let that sink in.", "Make no mistake", "Here's why that matters", "It's worth noting", "At its core" |
| Meta narration | "In this section, we'll...", "Let me walk you through...", "As we'll see...", "But that's another post" |
| Chat residue | "Great question", "Certainly", "I hope this helps", "Let me know if", a knowledge-limit disclaimer followed by a guess |
| Performed sincerity | "I promise", "creeps in" |

Cut the wrapper when the sentence works without it.
"Here's what" can stay when it introduces a real example or turn.
A heading restated by its first sentence: delete the sentence or make it add information.

### Empty adverbs and stacked qualifiers

really, just, literally, genuinely, honestly, simply, actually, deeply, truly, fundamentally, inherently, inevitably, interestingly, importantly, crucially; "In today's [X]," "When it comes to," "At the end of the day," "In a world where."

Cut them when they add emphasis but no meaning.
Keep words that carry scope, timing, degree, real uncertainty, or voice.
Strip a qualifier that hides a claim; keep one that honestly reports doubt.

### Business jargon

| Avoid | Use instead |
|-------|-------------|
| Navigate (challenges) | Handle, address |
| Unpack | Explain, examine |
| Lean into / double down | Accept / commit, increase |
| Deep dive | Analysis |
| Moving forward / circle back | Next / return to |
| On the same page | Agreed |

### Fake-strong verbs

"serves as," "acts as," "functions as," "represents" often hide "is" or a real verb.
"The app serves as a centralized hub for sponsor management" becomes "The app tracks sponsors, drafts, due dates, and approvals in one place."

### Synonym cycling

If several terms name the same thing, repeat the clearest one.
"The agent reviews the draft. The assistant scores the piece. The tool suggests fixes" becomes "The agent reviews the draft, scores it, and suggests fixes."
Keep distinct terms for distinct roles.

### Sentence starters and rhythm

- Several sentences opening with the same word, "So," "Look," or a Wh- clause ("What makes this hard is..." becomes "The constraint is...").
- Repeated punchy paragraph endings.
- Dashes as the default connector.
- Hedging dressed as reassurance: "Not always. Not perfectly."
- Hyphenated modifiers after the noun: "the report is high quality."

Vary these only when the repetition sounds automatic; don't ban punctuation or sentence lengths.

### Formatting

Bold sprinkled mid-sentence, bold-label bullet lists, emoji in headings, headings over two-sentence sections, and bullets where two sentences read better.
Keep formatting that helps scanning, accessibility, or the requested medium.

## Preserve human material

Protect what the writer could defend:

- an unusual, checkable detail;
- a real aside, self-correction, mixed feeling, or unresolved doubt;
- deliberate repetition of the right ordinary word;
- trade language, dated references, or a slightly surprising phrase that fits the writer;
- sentence-length variation the thought produced;
- an earned joke, contrast, rhythmic series, or closing beat.

Don't insert these as "human signals." Existing texture can stay; invented texture is performance.

## Put craft back

After cutting, ask:

- Where the piece most needs weight, can the reader see or check anything?
- Does evaluative writing show what the writer wants, prefers, or doubts?
- Does the syntax express how the thoughts relate?
- Did the edit remove warmth, humor, or a line the surrounding prose earned?

Add only what the source supports.
For a hollow passage, a precise `[TK: question]` beats model-written color.
