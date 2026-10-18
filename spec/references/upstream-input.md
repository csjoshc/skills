# Upstream Input and Naming Hygiene (AP-25)

Read when `.plan/PRD.md` or `.plan/task-sequence.md` exists, or before fleshing any ticket stub.

**Preferred input (from upstream `challenge` or `prd`):**
- `.plan/PRD.md` — narrative, scope, decisions
- `.plan/task-sequence.md` — ordered placeholders to expand

When both files exist, read them first and expand each placeholder in `task-sequence.md` into a fully-fleshed `.tickets/NN-<slug>.md`. Do not re-debate decisions already settled in the PRD. If only a free-text feature request is provided, generate without the upstream contract.

**Naming hygiene exception (AP-25):** Naming hygiene is not a requirements debate. Before fleshing any stub, apply the AP-25 substitution test to every identifier the stub introduces or names: *if the plan declares a concept as multi-valued (a set, enum, list of equivalents, or configurable abstraction), does this identifier still make sense if a different member of that set is substituted?* If the answer is no — the name only makes sense for one specific member — it fails the test. Annotate the ticket draft with `[NAMING: AP-25 — '<ident>' couples to a single instantiation of '<abstraction>'; the name should describe the role, not the member]`. This annotation is not a hard block, but a failing name must never go unannotated; a ticket where every name passes needs no naming note. Do not copy a self-contradicting name from the PRD into a ticket AC without surfacing it here.
