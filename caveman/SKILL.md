---
name: caveman
description: >-
  Token-compression skill with two modes. Inline: apply "lithic"
  compression to long agent prose responses. File: `/caveman compress
  <path>` shrinks AI-facing markdown at rest with `.original.md` backup.
  Compression performed by the resident agent (no API roundtrip). Code,
  paths, commands, identifiers preserved byte-for-byte. Use when compressing
  review summaries, multi-agent reports >1,000 words, or permanently
  shrinking heavy SKILL.md / reference docs. Skip for specs, ACs, tickets,
  user-facing prose.
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

## Contents

- Activation / Deactivation
- Subcommands
- Intensity Levels
- When to use / When NOT to use
- Lithic rules (summary)
- Workflow
- Auto-activation via hook
- Upstream Sync
- Hard rules
- Output contract

## Activation / Deactivation

**Trigger phrases** (any of these activate caveman mode):
"caveman mode", "talk like caveman", "use caveman", "less tokens",
"be brief", `/caveman`

**Persistence:** Once activated, applies to all subsequent responses
until explicitly deactivated.

**Deactivation:** "stop caveman" or "normal mode"

**Auto-suspend** (full prose for that response only, mode stays active):
- Security warnings or destructive operation confirmations
- Complex multi-step sequences where abbreviation risks misunderstanding

## Subcommands

Beyond mode toggling, the skill exposes one-shot subcommands.

### `/caveman compress <path>`

Compress a markdown file in place. Targets AI-facing docs loaded as
context repeatedly — heavy SKILL.md files, long reference docs, plans.
Compressing once pays back continuously across sessions.

**Workflow** (the agent follows this when invoked):

1. `python3 ~/.skills/caveman/scripts/detect.py <path>` — confirm
   natural-language file (exits 0 if compressible, 1 if not)
2. `python3 ~/.skills/caveman/scripts/safety.py <path>` — size limit
   (<500KB) and sensitive-content scan (credentials, secrets, tokens,
   private keys). Exits 0 if safe.
3. Read the file
4. Apply lithic rules per the Workflow section below (Segment →
   Transform → Validate → Emit). The agent — not an external API —
   performs the transform.
5. Write compressed content back to `<path>`. Save original as
   `<path stem>.original.md`.
6. `python3 ~/.skills/caveman/scripts/validate.py <original> <compressed>` —
   deterministic preservation check (headings, code blocks, URLs, paths)
7. If validate exits non-zero: read errors, fix inline, re-validate.
   Max 2 retries.
8. Emit metadata line: `[caveman: in=N tokens → out=K tokens (X% compression)]`

**Do not run on:** specs, ACs, tickets, READMEs, customer-facing prose,
files containing secrets.

### `/caveman uncompress <path>`

Restore from `.original.md` backup. Backup overwrites the compressed
file; backup is then removed.

```bash
mv <path>.original.md <path>
```

If no backup exists, abort with an error.

## Intensity Levels

| Level | Style |
|---|---|
| **lite** | Removes filler/hedging; preserves articles and full sentences |
| **full** (default) | Drops articles, uses fragments and short synonyms |
| **ultra** | Abbreviates terms (DB, auth, config); uses symbolic reasoning (X → Y) |

Activate a specific level: "caveman lite", "caveman ultra".
Default when no level is specified: **full**.

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

Respond in telegraphic style. Cut all filler, keep technical substance.
- Drop articles (a, an, the), filler (just, really, basically, actually).
- Drop pleasantries (sure, certainly, happy to).
- No hedging. Fragments fine. Short synonyms.
- Technical terms stay exact. Code blocks unchanged.
- Pattern: [thing] [action] [reason]. [next step].

## Workflow

### Segment classification (used by `/caveman compress`)

| Segment | Treatment |
|---|---|
| Fenced code, inline code | byte-for-byte |
| Paths, URLs, identifiers | byte-for-byte |
| Prose, headings, table cells | apply lithic rules |

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

## Upstream Sync

See [`UPSTREAM.md`](UPSTREAM.md) for the full upgrade guide: file map,
local patches, what not to overwrite, and step-by-step instructions.

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
