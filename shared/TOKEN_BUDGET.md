# Token Budget Strategy

Two compression layers work the token budget from opposite ends:

- **RTK (Rust Token Killer)** — input side. Shell-proxy binary that
  filters and compresses CLI command output before it ever enters the
  agent's context. 60-90% reduction on common commands (cargo test,
  git status, pytest, npm run build). Zero-config after install;
  Claude Code runs `git status` as normal and RTK rewrites the output
  transparently. Single Rust binary, no dependencies. See
  [rtk-ai/rtk](https://github.com/rtk-ai/rtk).

- **Caveman** — output side. Skill that compresses the *agent's* prose
  before it reaches the user. Code, paths, commands, identifiers pass
  through byte-for-byte; only prose is compressed. 65-75% reduction on
  long reports. See `.claude/skills/caveman/SKILL.md`.

These are complementary. Use both.

## Where in the pipeline they apply

```
  user prompt
      │
      ▼
  ┌─────────────────────┐
  │ agent reasoning     │
  └──┬──────────────────┘
     │ Bash("git status")
     ▼
  ┌─────────────────────┐
  │ RTK shell proxy     │ ← INPUT compression
  │ (filters, dedupes,  │
  │  strips ANSI,       │
  │  drops progress)    │
  └──┬──────────────────┘
     │ compressed output
     ▼
  ┌─────────────────────┐
  │ agent context       │
  │ (budget preserved)  │
  └──┬──────────────────┘
     │ agent generates reply
     ▼
  ┌─────────────────────┐
  │ caveman skill       │ ← OUTPUT compression
  │ (prose → telegraph, │
  │  code untouched)    │
  └──┬──────────────────┘
     │ compressed reply
     ▼
  user
```

## When each earns its keep

| Scenario | RTK helps | Caveman helps |
|---|---|---|
| Long test suite output (`pytest -vv`) | Yes (huge) | No (already compressed by RTK) |
| CI log scraping | Yes | No |
| `cleanup` Phase 0 tool output (ruff, knip, vulture, jscpd) | Yes | Rarely |
| `pr-review` 5-agent reports | Modest | Yes — reports are verbose |
| `reframe` architect or engineer mode outputs | No | Yes |
| `pr-fix` comment summaries | No | Yes if > 1k words |
| User-facing spec / AC text | No (never compress input) | **No** — keep full prose |
| Error messages / tracebacks | No — RTK preserves errors | **No** — keep for debugging |
| First reply in a new session | No | **No** — tone matters |

## Install RTK (one-time, per machine)

```bash
# Install the binary (macOS/Linux)
cargo install rtk-ai

# Or prebuilt
curl -sSL https://rtk-ai.app/install.sh | sh

# Wire into Claude Code (and Cursor, Codex, Gemini CLI, Windsurf, Cline, OpenCode)
rtk init

# Verify
rtk status
```

RTK installs a shell hook that rewrites command output transparently.
No per-command prefix required. It's agent-agnostic — one install
covers every tool that shells out.

## When to bypass RTK

A few cases want the raw output:

- Debugging a flaky test where the exact stack trace matters — use
  `rtk bypass cargo test -- some::test`
- Capturing evidence for a PR body (use the unfiltered log for the
  ephemeral-commit attachment).
- Any command where the trimmed output removed the bit you cared about.

Claude Code's `Bash` tool can take a `rtk bypass` prefix in these cases.

## When to bypass caveman

Caveman auto-activates via the `caveman-budget-auto` hook at > 50%
context usage. Turn it off explicitly when:

- User asks for full prose ("don't compress")
- Output is a PR body, ticket, spec, or anything posted publicly
- Response is an error explanation

Disable for a turn with `/uncaveman` or session-wide by removing the
`caveman-budget-auto` entry from `~/.hooks/`.

## Stacking: when do they hurt each other?

Rarely. One failure mode to watch: if RTK strips a warning that
caveman then paraphrases, the original meaning can drift. Mitigation:

- RTK preserves ERROR, WARNING, and FAIL lines by default. Keep this
  setting on.
- Caveman never compresses fenced code, so command output inside code
  fences is safe.
- If combining both on a deeply-nested review chain, have each chain
  report its raw lines with `rtk bypass` once, then let downstream
  summarizers compress.

## Skills that benefit most from RTK

Strongly recommended before running these (the token savings are
largest):

- `cleanup` Phase 0 — runs many linters and dup detectors
- `pr-review` — 5 sub-agents each read the full diff
- `pr-fix` — compiler and test re-runs
- `tdd/MUTATION.md` — multiple test runs per mutant
- `verify-claim` — test output capture
- `project-onboarding` — stack-detection shell scripts

Skills where RTK matters less:

- `reframe` — reads markdown, not CLI output
- `spec-writer`, `ticket-critic` — text-only
- `skill-sync`, `mcp-sync`, `hook-sync` — small JSON/YAML writes

## Budget calibration

Rough numbers from field reports on a large TypeScript monorepo:

| Layer | Before | After |
|---|---|---|
| Raw CLI output per session | ~50k tokens | ~8k tokens (RTK, 84% off) |
| Agent response prose per session | ~40k tokens | ~12k tokens (caveman, 70% off) |
| Total session budget | ~120k tokens | ~35k tokens |

Your mileage varies with stack, test verbosity, and how many sub-agents
the review chain spawns. Measure with `/context` before deciding
whether you need both layers or just one.

## References

- [rtk-ai/rtk](https://github.com/rtk-ai/rtk) — source, install, docs
- [rtk-ai.app](https://www.rtk-ai.app/) — landing page
- [Esteban Estrada's write-up](https://codestz.dev/experiments/rtk-rust-token-killer) — 70% reduction field report
- [Kilo Code discussion](https://github.com/Kilo-Org/kilocode/discussions/5848) — 89% reduction, 10M tokens saved
- `.claude/skills/caveman/SKILL.md` — output-side counterpart
