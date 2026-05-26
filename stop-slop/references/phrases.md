# Phrases to Remove

## Throat-Clearing Openers

Remove these announcement phrases. State the content directly.

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

Any "here's what/this/that" construction is throat-clearing before the point. Cut it and state the point.

## Emphasis Crutches

These add no meaning. Delete them.

- "Full stop." / "Period."
- "Let that sink in."
- "This matters because"
- "Make no mistake"
- "Here's why that matters"

## Business Jargon

Replace with plain language.

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

## Adverbs

Kill all adverbs. No -ly words. No softeners, no intensifiers, no hedges.

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

Also cut these filler phrases:

- "At its core"
- "In today's [X]"
- "It's worth noting"
- "At the end of the day"
- "When it comes to"
- "In a world where"
- "The reality is"

## Meta-Commentary

Remove self-referential asides. The essay should move, not announce its own structure.

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

Sentences that announce importance without naming the specific thing. Kill these.

- "The reasons are structural"
- "The implications are significant"
- "This is the deepest problem"
- "The stakes are high"
- "The consequences are real"

If a sentence says something is important/deep/structural without showing the specific thing, cut it or replace it with the specific thing.

## Architectural Metaphors (Lazy Abstractions)

Replace these placeholders with concrete names. They feel like
specificity but they aren't — they're the *idea* of specificity. The
test: can you point at the file, class, function, or interface the
metaphor is about? If not, the metaphor is hollow.

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

The pattern: architectural metaphors substitute for the concrete name.
If you can't name the concrete artifact, you don't yet understand the
design well enough to write about it — go find the name first.

## Vendor Specificity in Agnostic Docs

If a doc claims to describe a runtime-agnostic, vendor-agnostic, or
platform-agnostic feature, scan it for product names that contradict
the claim. Common offenders:

| Token | When it's wrong | What to write instead |
|---|---|---|
| "Docker Model Runner" / "DMR" | Doc claims runtime is configurable | "Local model runtime" or "OpenAI-compatible endpoint" |
| "Ollama" | Same | Same — vendor name in a `runtime:` selector value only |
| "host.docker.internal:11434" | In a doc that's supposed to read at the abstraction level | "the host-side runtime URL (see `LLM_BASE_URL`)" |
| "nginx" (in a load-balancer-agnostic doc) | When the reverse proxy is swappable | "reverse proxy" |
| "Postgres" / "Redis" (in storage-agnostic docs) | When the storage layer is configurable | "persistent store" / "cache" |
| Hard-pinned source refs (`hf.co/unsloth/...`) | In a runtime-agnostic test or doc | the *alias* from your catalog file |

Allowed: vendor names appear in (a) runtime / vendor adapter modules,
(b) `runtime:` / `provider:` selector values, (c) per-runtime sections
of a doc clearly labeled as such. Anywhere else they assert a coupling
the doc denies.
