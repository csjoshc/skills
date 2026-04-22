---
name: caveman
description: >-
  Token-compression wrapper for long agent outputs. Applies "lithic"
  compression to prose while leaving code, paths, commands, filenames,
  and identifiers untouched. Cuts output tokens by ~65-75% with no loss
  of technical fidelity. Use when compressing long review summaries, reframe output,
  multi-agent reports, or any response over ~1,000 words. Skip for
  specs, ACs, tickets, and user-facing prose.
---

# caveman

Wraps [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman),
a token-compression skill. Caveman's "lithic compression" style
rewrites prose in a terse telegraphic register — articles dropped,
sentences shortened, redundancy removed — while code blocks, paths,
commands, URLs, and identifiers pass through byte-for-byte. Technical
fidelity stays; budget shrinks.

**Pairs with RTK (Rust Token Killer)** on the input side. RTK compresses
CLI command output before it enters the agent's context; caveman
compresses the agent's prose before it leaves. See
`shared/TOKEN_BUDGET.md` for the joint strategy and measurement data.

## When to use

Invoke on outputs where the *user* doesn't need flowing prose:

- `pr-review` multi-agent summary
- `cleanup` mechanical + subjective findings
- `reframe` engineer or architect mode outputs
- `pr-fix` summary table
- `consolidate-memory` index rebuild
- Any agent-internal thought trace before a final answer
- Any response above ~1,000 words of prose

## When NOT to use

Keep full prose for:

- `spec-writer` output — the user reads ACs in full
- `ticket-critic` verdicts — stakeholders read these
- Customer / reviewer replies on PRs or tickets
- Error messages and failure explanations (clarity > token savings)
- Anything shown directly to non-technical stakeholders
- First response to a new user (tone matters)

## Lithic rules (summary)

Caveman's transforms, in order of priority:

1. Code, paths, shell, URLs, identifiers: **no change**.
2. Remove articles (a, an, the) and mild hedges (perhaps, likely, may).
3. Collapse polite framing ("I'd recommend" → "recommend").
4. Drop transitional filler ("In addition", "That said", "To be clear").
5. Use lists and tables over prose for enumerations.
6. Keep numbers, proper nouns, negatives, modal verbs (must/should/never).
7. Preserve sequence markers (first, then, finally) only when order is load-bearing.

Target ratio: 0.3-0.4 output tokens per input token of prose. Code is
counted separately and does not contribute to the ratio.

## Workflow

### Phase 1: Segment

Split the intended output into segments:

| Segment | Classification | Treatment |
|---|---|---|
| Fenced code (``` or indented) | keep | byte-for-byte |
| Inline code (backticks) | keep | byte-for-byte |
| Paths, URLs, identifiers | keep | byte-for-byte |
| Prose | transform | lithic rules |
| Headings | transform-light | drop articles only |
| Table cells with prose | transform | lithic |
| Table cells with code | keep | byte-for-byte |

### Phase 2: Transform prose

Apply the lithic rules. Retain negations, modal verbs, quantifiers.
Output must remain grammatical enough for a technical reader.

### Phase 3: Validate

Re-read the compressed output and check:

- No identifier renamed
- No path altered
- No numeric value changed
- No "never" dropped or flipped
- No imperative inverted

If any check fails: roll back to the original segment.

### Phase 4: Emit

Deliver the compressed text. If the user asks for the long form, emit
the pre-compression version on request.

## Auto-activation via hook

When `hook-sync` is installed, register a `SessionStart` hook that turns
caveman on when either is true:

- Estimated session budget > 50% consumed
- User toggles `caveman on` explicitly

Hook file at `~/.hooks/caveman-compression.json`:

```json
{
  "name": "caveman-compression",
  "events": [
    { "event": "SessionStart" },
    { "event": "PreToolUse", "tool": "Stop" }
  ],
  "action": { "type": "skill", "skill": "caveman" },
  "trigger_on": "context_usage > 0.5",
  "platforms": ["claude-code", "cursor", "codex", "gemini"]
}
```

## Upstream sync

Caveman is maintained upstream. To refresh:

```bash
# Assuming the upstream repo is cloned into ~/src/caveman
cd ~/src/caveman && git pull

# Copy the upstream SKILL-equivalent files into this bundle,
# preserving our wrapper SKILL.md above it.
cp -r ~/src/caveman/prompts ./prompts
cp ~/src/caveman/README.md ./UPSTREAM_README.md
```

Then run `skill-sync` so every platform picks up the refresh.

## Hard rules

- Never compress anything the user explicitly asked for in full.
- Never compress error messages or tracebacks.
- Never compress user-facing copy (PR descriptions, review comments
  posted to GitHub, messages to stakeholders).
- Never rename an identifier, path, or flag under compression.
- If unsure whether a segment is prose or code, treat it as code.

## Output contract

Emit compressed text directly. At the end, single-line metadata:

```
[caveman: in=NNN tokens → out=KKK tokens (compression X%)]
```

If the user wants to see the original:

```
/uncaveman   →   returns the pre-compression version
```
