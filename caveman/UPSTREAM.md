# Upstream Sync Guide

Upstream repo: https://github.com/JuliusBrussee/caveman
Last synced: 2026-04-27

---

## Architectural divergence

Upstream performs compression by calling the Anthropic API from
`compress.py`. The local skill delegates compression to the resident
Claude agent that invokes the skill — no API roundtrip, no `anthropic`
SDK dependency, no `ANTHROPIC_API_KEY` required.

Several upstream files have **no local equivalent**:

| Upstream path | Local status |
|---|---|
| `caveman-compress/scripts/compress.py` | **REMOVED** — agent performs compression |
| `caveman-compress/scripts/cli.py` | **REMOVED** — entry point is `/caveman compress` skill subcommand |
| `caveman-compress/scripts/__main__.py` | **REMOVED** — no standalone CLI |

Do not re-introduce these files when syncing. Upstream changes to them
are not relevant to this fork.

---

## File map

| Upstream path | Local path | Sync method |
|---|---|---|
| `skills/caveman/SKILL.md` | `SKILL.md` §§ Intensity Levels, Activation/Deactivation | **MERGE** — do not replace |
| `caveman-compress/scripts/__init__.py` | `scripts/__init__.py` | **DIVERGED** — local omits removed modules |
| `caveman-compress/scripts/detect.py` | `scripts/detect.py` | Direct copy + re-apply `__main__` patch |
| `caveman-compress/scripts/validate.py` | `scripts/validate.py` | Direct copy |

---

## Local-only content — never overwrite

**In `SKILL.md`:**
- Intro paragraph (RTK pairing, TOKEN_BUDGET.md reference)
- `## Contents` header
- `## Subcommands` (defines `/caveman compress` and `/caveman uncompress`)
- `## When to use` / `## When NOT to use`
- `## Lithic rules (summary)` — more detailed than upstream
- `## Workflow` (Segment → Transform → Validate → Emit)
- `## Auto-activation via hook`
- `## Hard rules`
- `## Output contract`
- `## Upstream Sync`

**Local-only files:**
- `scripts/safety.py` — size + sensitive-content checks (extracted from
  upstream `compress.py` before its removal)
- `UPSTREAM.md` — this file

---

## Local patches applied to upstream scripts

`scripts/detect.py` — local addition:

A trailing `if __name__ == "__main__":` block that prints the detected
file type and exits 0 if compressible, 1 otherwise. Used by the
`/caveman compress` workflow's gating step. Re-apply when copying a new
upstream version.

---

## How to upgrade

### Fetch upstream sources

```bash
curl -s https://raw.githubusercontent.com/JuliusBrussee/caveman/main/skills/caveman/SKILL.md
curl -s https://raw.githubusercontent.com/JuliusBrussee/caveman/main/caveman-compress/scripts/detect.py
curl -s https://raw.githubusercontent.com/JuliusBrussee/caveman/main/caveman-compress/scripts/validate.py
```

Files NOT to fetch (architecturally diverged): `compress.py`, `cli.py`,
`__main__.py`.

### Merge SKILL.md

1. Read upstream `skills/caveman/SKILL.md`
2. Compare against local `## Intensity Levels` and `## Activation / Deactivation`
3. Merge any new intensity levels, trigger phrases, or safety guardrails
4. Leave all local-only sections untouched

### Update detect.py / validate.py

For each: copy new upstream content, then re-apply local patches.
For `detect.py`: re-add the `__main__` block.

### Verify

```bash
python3 ~/.skills/caveman/scripts/detect.py ~/.skills/caveman/SKILL.md
python3 ~/.skills/caveman/scripts/safety.py ~/.skills/caveman/SKILL.md
python3 ~/.skills/caveman/scripts/validate.py ~/.skills/caveman/SKILL.md ~/.skills/caveman/SKILL.md
```

Then run `/skillsmith` audit on `SKILL.md`.
