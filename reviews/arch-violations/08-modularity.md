# Modularity, cohesion, and reuse

Smells at the granularity boundary — how responsibilities are divided
across modules, how similar concerns get deduplicated (or don't), and
whether abstractions earn their cost. The compounding damage is usually
merge friction, shadow divergence, and eroded ownership.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (4)

### Premature abstraction

**Shape (language-agnostic):** An interface, base type, or strategy
seam exists with exactly one implementation, justified as "for future
flexibility." The seam creates two places to change for every change
without providing substitutability that callers actually use.

**Decidable at:** `diff` — visible only once the one-implementation
reality is in the tree.

**Why it compounds:** Each call site now depends on the abstract type.
Adding a second implementation later is no cheaper than refactoring a
concrete one would have been — but the indirection tax is paid on every
read of the code until then.

**Category mapping:** `category: Modularity` / severity `LOW` / `rule_code: ARCH-MOD-PREMATURE`

---

### Duplicate implementations of a cross-cutting concern

**Shape (language-agnostic):** Two or more independent implementations
of the same concern coexist — two logger configurations, two retry
policies, two date formatters, two HTTP clients with different
timeouts. No single source of truth; drift is inevitable.

**Decidable at:** `diff`

**Why it compounds:** Bug fixes applied to one copy are silently missing
from the other. Observability is fractured (two log formats, two metric
namespaces). A new engineer picks whichever one they find first,
entrenching the duplication.

**Category mapping:** `category: Redundancy` / severity `MEDIUM` / `rule_code: ARCH-MOD-DUP`

---

### God module / god type

**Shape (language-agnostic):** A single file, class, or module owns
responsibilities that are unrelated by domain or lifecycle. Changes to
unrelated features touch the same file, tests cannot isolate behavior,
and ownership becomes ambiguous because no team fully owns the file.

**Decidable at:** `diff`

**Why it compounds:** Merge conflicts multiply with team size. Test
setup grows unbounded as unrelated dependencies accumulate. Refactoring
becomes risky because the file holds too many invariants at once.

**Category mapping:** `category: Modularity` / severity `MEDIUM` / `rule_code: ARCH-MOD-GOD`

---

### Feature-flag / config sprawl with no retirement path

**Shape (language-agnostic):** Flags, environment variables, or config
toggles accumulate without an owner, a default, or a sunset date. The
code simultaneously encodes all historical versions of itself; every
new contributor must reason about the full power set of flag
combinations.

**Decidable at:** `both` — /antiplan should require retirement criteria
when a flag is introduced.

**Why it compounds:** The test matrix grows as the product of all
flags. Behavior becomes unreproducible without the exact flag set that
triggered a bug. Removing any one flag requires archaeology.

**Category mapping:** `category: Modularity` / severity `MEDIUM` / `rule_code: ARCH-MOD-FLAG-SPRAWL`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Premature abstraction | `rg -n "class .*Interface\|abstract class\|Protocol\|interface " <dir>/` cross-referenced with `rg -nl "implements <Iface>\|extends <Base>"` — count of implementations. One = smell. |
| Duplicate cross-cutting concern | `jscpd --min-lines 20 <dir>/` or two independent `rg` matches for the concern (e.g., `rg "logging\.getLogger\|log = .*Logger"` returning multiple config sites). |
| God module / god type | `wc -l <file>` > project threshold AND `rg -c "^(def \|function \|class )" <file>` > ~15 distinct top-level declarations; `git log --oneline <file>` showing unrelated feature areas in commit messages. |
| Flag sprawl | `rg -n "feature_flag\|is_enabled\|FLAG_" <dir>/` counting unique flag names; `git log -G"FLAG_" --since=1.year` showing additions without removals. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Redundancy
  lens: redundancy-watcher
  file: src/clients/retry.py
  line: 1
  rule_code: ARCH-MOD-DUP
  severity: MEDIUM
  source: tool-flagged
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    Two independent retry implementations: src/clients/retry.py
    (exponential, max 3) and src/integrations/vendor_client.py:40-88
    (linear, max 5). Both wrap outbound HTTP calls; neither references
    the other.
  proof: |
    $ jscpd --min-lines 15 --format python src/
    → duplicate block src/clients/retry.py:12-48 ≡
      src/integrations/vendor_client.py:40-76
    $ rg -nl "def .*retry|Retry\(" src/ | wc -l
    → 2 retry call sites with divergent backoff strategies.
  suggested_fix: |
    Consolidate into src/clients/retry.py. Have vendor_client import it.
    Document the default policy in AGENTS.md so the next integration
    reuses the same module.
```
````

---

## Few-shot: good dismissal

A reviewer sees two functions in the repository named `format_date` —
one in `reports/` and one in `exports/` — and flags duplicate
cross-cutting concern. It is **not** a duplication smell when the two
functions implement deliberately different contracts: `reports/` formats
dates in the user's locale for a UI, `exports/` formats dates in RFC
3339 for downstream ingestion. The names collide; the concerns don't.
Similarly, an interface with one implementation is not premature
abstraction if the codebase has an explicit plan to add a second
implementation in the next ticket (and the plan is linked). The
question is not "is there one implementation?" but "does the plan name
a second one?"

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Premature abstraction | ❌ — emerges from code | ✅ | ✅ |
| Duplicate cross-cutting concern | partial — can mandate a canonical module | ✅ | ✅ |
| God module / god type | ❌ — grows over time | ✅ | ✅ |
| Flag sprawl | partial — should require retirement criteria | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot detect instances.
When `plan_present: true` and the plan named a canonical module or
retirement criteria, emit as `category: Architectural Drift` with
`decidable_at: design`.
