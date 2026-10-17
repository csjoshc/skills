# Phrases to Inspect

## Contents

- Words to Inspect
- Throat-Clearing Openers
- Emphasis Crutches
- Business Jargon
- Empty Emphasis and Stacked Qualifiers
- Meta-Commentary
- Faux-Insight Setups
- Importance Puffery
- Weasel Attribution
- Fake-Strong Verbs
- Performative Emphasis
- Telling Instead of Showing
- Vague Declaratives
- Architectural Metaphors (Lazy Abstractions)
- Vendor Specificity in Agnostic Docs


## Words to inspect

These words can add puffery or hide a simple action. Replace them when a plainer, more exact word preserves the meaning. Keep them when they name a real property or fit the writer's voice.

delve, foster, leverage, utilize, facilitate, empower, streamline, robust, cutting-edge, paradigm shift, game changer, this is huge, this changes everything, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness, ever-evolving.

## Throat-Clearing Openers

Check whether these phrases delay the point. Cut the opener when the sentence works without it.

- "Here's the thing:"
- "Here's what [X]"
- "Here's this [X]"
- "Here's that [X]"
- "Here's why [X]"
- "The uncomfortable truth is"
- "It turns out"
- "The real [X] is"
- "Let me be clear"
- "The truth is,"
- "I'll say it again:"
- "I'm going to be honest"
- "Can we talk about"
- "Here's what I find interesting"
- "Here's the problem though"

"Here's what/this/that" often announces content the sentence could state directly. Keep it when it introduces a real example or turn in the conversation.

## Emphasis Crutches

These often add emphasis without information. Remove them when the surrounding sentence already carries the point.

- "Full stop." / "Period."
- "Let that sink in."
- "This matters because"
- "Make no mistake"
- "Here's why that matters"

## Business Jargon

Prefer plain language when it keeps the same meaning.

| Avoid | Use instead |
|-------|-------------|
| Navigate (challenges) | Handle, address |
| Unpack (analysis) | Explain, examine |
| Lean into | Accept, embrace |
| Landscape (context) | Situation, field |
| Game-changer | Significant, important |
| Double down | Commit, increase |
| Deep dive | Analysis, examination |
| Take a step back | Reconsider |
| Moving forward | Next, from now |
| Circle back | Return to, revisit |
| On the same page | Aligned, agreed |

## Empty emphasis and stacked qualifiers

Remove adverbs and hedges when they only add emphasis or make a claim sound vague. Keep them when they carry real scope, timing, degree, uncertainty, or voice. Several qualifiers stacked on one claim usually need trimming.

Specific offenders:

- "really"
- "just"
- "literally"
- "genuinely"
- "honestly"
- "simply"
- "actually"
- "deeply"
- "truly"
- "fundamentally"
- "inherently"
- "inevitably"
- "interestingly"
- "importantly"
- "crucially"

Common filler phrases to inspect:

- "At its core"
- "In today's [X]"
- "It's worth noting"
- "At the end of the day"
- "When it comes to"
- "In a world where"
- "The reality is"

## Meta-Commentary

Check whether a self-referential aside helps the reader. Cut it when it only announces the text's structure.

- "Hint:"
- "Plot twist:" / "Spoiler:"
- "You already know this, but"
- "But that's another post"
- "X is a feature, not a bug"
- "Dressed up as"
- "The rest of this essay explains..."
- "Let me walk you through..."
- "In this section, we'll..."
- "As we'll see..."
- "I want to explore..."

## Faux-Insight Setups

These can cast the writer as the lone expert. Cut the setup when the claim stands on its own.

- "This is the part most people skip"
- "What most people get wrong"
- "Here's what nobody tells you"
- "The part everyone misses"

"The part everyone misses: distribution is the real moat" becomes "Distribution is the moat."

## Importance Puffery

State the fact. Let the reader judge whether it matters.

| Avoid | Instead |
|-------|---------|
| "stands as a testament" | State the fact it supposedly testifies to |
| "marks a pivotal moment" | "The launch is the company's first paid product" |
| "plays a vital role" | Name what it does |
| "solidifies its position" | Name the position, cite the evidence |
| "underscores its significance" | Cut |

## Weasel Attribution

Name the source or cut the claim. If there is no source, ask instead of inventing one.

- "Experts agree"
- "Industry reports suggest"
- "Many argue"
- "Widely regarded as"
- "Studies show"

## Fake-Strong Verbs

Prefer "is" and "has" when clearer. "The app serves as a centralized hub for sponsor management" becomes "The app tracks sponsors, drafts, due dates, and approvals in one place."

- "serves as"
- "acts as"
- "functions as"
- "represents" (when "is" works)

## Performative Emphasis

False intimacy or manufactured sincerity:

- "creeps in"
- "I promise"
- "They exist, I promise"

## Telling Instead of Showing

Announcing difficulty or significance rather than demonstrating it:

- "This is genuinely hard"
- "This is what leadership actually looks like"
- "This is what X actually looks like"
- "actually matters"

## Vague Declaratives

Sentences that announce importance without naming the specific thing. Replace the announcement when the source supports a concrete fact or consequence.

- "The reasons are structural"
- "The implications are significant"
- "This is the deepest problem"
- "The stakes are high"
- "The consequences are real"

If a sentence says something is important/deep/structural without showing the specific thing, cut it or replace it with the specific thing.

## Architectural Metaphors (Lazy Abstractions)

These phrases can sound specific while hiding the mechanism. Name the
file, class, function, or interface when the prose needs that detail
and the source provides it. Keep a metaphor when it communicates more
clearly than the implementation name.

| Avoid | Replace with |
|---|---|
| "The centralized seam" | Name the class / function / module: e.g. "the `apply_llm_env_overrides` function" |
| "Single source of truth" | Name the authority: e.g. "the values in `config/llm-defaults.env`" |
| "First-class" | Cut. If you need to convey importance, state the property directly: "errors are returned, not raised" |
| "Load-bearing" | Cut, or state what depends on it: "the `localhost` token in `server_name` matches the IronBank default block's Host" |
| "Non-trivial" | Cut, or name the complexity: "three nested `if` branches handling stream/blocking/error" |
| "Out-of-the-box" | Name the default: "the `LLM_RUNTIME=ollama` default ships with…" |
| "By design" | Cut, or cite the spec: "Per `docs/ADR-CHAT-1.md`, this is intentional because…" |
| "Battle-tested" | Cite usage: "X has run in prod since YYYY-MM-DD across N services" |
| "Cleanly" / "elegantly" | Cut; if the design has a property worth naming, name the property |
| "Modular" / "extensible" | Show the extension point: "new providers register via `create_provider(name, ProviderClass)`" |

Use a concrete name when it helps the reader locate or understand the design. If the source does not identify the artifact, keep the wording general or ask for the missing detail.

## Vendor Specificity in Agnostic Docs

If a doc claims to describe a runtime-agnostic, vendor-agnostic, or
platform-agnostic feature, scan it for product names that contradict
the claim. Common offenders:

| Token | When it's wrong | What to write instead |
|---|---|---|
| "Vendor A runtime" | Doc claims runtime is configurable | "Local model runtime" or "OpenAI-compatible endpoint" |
| "Ollama" | Same | Same; keep the vendor name only in a `runtime:` selector value |
| "<host>:<port>" | In a doc that's supposed to read at the abstraction level | "the host-side runtime URL (see `LLM_BASE_URL`)" |
| "nginx" (in a load-balancer-agnostic doc) | When the reverse proxy is swappable | "reverse proxy" |
| "Postgres" / "Redis" (in storage-agnostic docs) | When the storage layer is configurable | "persistent store" / "cache" |
| Hard-pinned source refs (`hf.co/unsloth/...`) | In a runtime-agnostic test or doc | the *alias* from your catalog file |

Allowed: vendor names appear in (a) runtime / vendor adapter modules,
(b) `runtime:` / `provider:` selector values, (c) per-runtime sections
of a doc clearly labeled as such. Anywhere else they assert a coupling
the doc denies.
