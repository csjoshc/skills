# Phase 0 Mechanical Checks

Every Phase 0 finding is non-negotiable; a later subjective judgment cannot dismiss it.
Schema for the emitted block: [`~/.skills/reviews/schemas.md`](../reviews/schemas.md).

| Check                      | Python                                 | TypeScript/JS                               |
| -------------------------- | -------------------------------------- | ------------------------------------------- |
| Unused imports/vars        | `ruff check --select F401,F841`        | `npx eslint --rule 'no-unused-vars: error'` |
| Unused exports             | `vulture --min-confidence 80`          | `npx ts-prune`, `npx knip`                  |
| File size                  | `wc -l` vs 300/500 thresholds          | same                                        |
| Cyclomatic complexity      | `radon cc -n C` (>10 = refactor)       | `npx complexity-report`                     |
| Duplication                | `jscpd .` (>5% = consolidate)          | same                                        |
| Import cycles              | `pycycle` / `importlinter`             | `npx madge --circular`                      |
| **Layer boundaries**       | delegate to `layer-boundary-critic.md` | same                                        |
| **Dead code / redundancy** | delegate to `redundancy-watcher.md`    | same                                        |
| Dead branches              | `# pragma: no cover` without reason    | `istanbul ignore` without reason            |
| Commented-out blocks       | `grep -En '^\s*(#\|//)[^!]'`           | same                                        |
| **Scope-leak vocabulary**  | `git grep -nE '(ADR-[A-Z0-9-]+\|T-[0-9]{3,}\|FR-[0-9]+\|NFR-[0-9]+\|RISK-[0-9]+\|IG-[0-9]+G[0-9]*\|[0-9]+G[0-9]+\|Slice [0-9]+\|Constitution P[0-9]+\|AP-[0-9]+)' -- '*.py'` (extend to docstrings) | `git grep -nE '<same>' -- '*.ts' '*.tsx' '*.js' '*.mjs' '*.sh'` |
| **Cycle-coupled paths**    | `git grep -nE '"[^"]*(proof\|evidence)/[^"]*[0-9]G[0-9]+' -- '*.py'` | `git grep -nE '"[^"]*(proof\|evidence)/[^"]*[0-9]G[0-9]+' -- '*.ts' '*.tsx' '*.sh'` |
| **Runtime-coupled names**  | filename grep: `find . -name '*-vendora.*' -o -name '*-vendorb.*' -o -name '*-openai.*'` (exclude `tests/` and explicit runtime-tagged fixtures) | same |
| **Tracked-but-ignored**    | `git ls-files -ci --exclude-standard` plus `git ls-files .plan .tickets .handoff`; every path either prints is HIGH, ignore rule or not | same |
| **Inline lookup tables**   | `grep -cE '^\s*(case\|match)\b\|=> *["'\'']' <file> | awk '$1>3{...}'` — branches > 3 should externalize per `DA-003` | same |
