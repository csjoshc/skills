# Security at the architectural level

Not CVE-spotting — structural shapes that guarantee the system will
leak, over-authorize, or over-trust over time. The compounding damage
is silent: a missing check in one place becomes the template for the
next ten endpoints.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (5)

### Authorization logic scattered across handlers

**Shape (language-agnostic):** Each endpoint or handler re-implements
"is this actor allowed to do this?" inline, rather than delegating to a
single policy layer. Similar checks drift over time and at least one
handler is eventually missing a clause.

**Decidable at:** `both` — /antiplan should mandate a policy module;
diff review catches scattered re-implementations.

**Why it compounds:** Divergence is statistically guaranteed at scale.
Adding a new permission requires touching every handler and reviewing
each for subtle variance. Audit is expensive; a future bypass is
inevitable.

**Category mapping:** `category: Architectural Drift` (when plan
mandated a policy layer) else `Standards` / severity `HIGH` /
`rule_code: ARCH-SEC-AUTHZ-SCATTERED`

---

### Trust-boundary confusion

**Shape (language-agnostic):** User-controlled data (request body,
URL parameters, authenticated-user fields beyond identity) flows
directly into a template, shell command, SQL query, filesystem path,
or deserializer without being marked untrusted or passed through a
sanitizer. The "authenticated" status is conflated with "trusted."

**Decidable at:** `diff`

**Why it compounds:** Each new sink that accepts user input inherits
the missing-sanitizer shape. The first successful injection is usually
at a sink added long after the original trust decision.

**Category mapping:** `category: Bug` / severity `CRITICAL` / `rule_code: ARCH-SEC-TRUST`

---

### Secrets committed to the repository

**Shape (language-agnostic):** Hardcoded passwords, API keys, signing
keys, or cloud credentials live in tracked files (source, config,
fixtures). Rotation becomes a coordinated cross-repo and deploy event.

**Decidable at:** `diff`

**Why it compounds:** Git history preserves secrets forever; rewriting
history is disruptive and often incomplete. A single leaked token
compromises every environment that shares it.

**Category mapping:** `category: Bug` / severity `CRITICAL` / `rule_code: ARCH-SEC-SECRET`

---

### Missing auth check on a new endpoint

**Shape (language-agnostic):** A new route or handler is added to a
codebase where every other endpoint is decorated/wrapped with an auth
guard, but this one is not. The pattern "every endpoint has X" has a
gap.

**Decidable at:** `both` — /antiplan should mandate a default-deny
registration pattern; diff catches gaps.

**Why it compounds:** The same gap will recur every time someone adds
an endpoint with the minimum-path template. A default-deny framework
forecloses the class; a default-allow framework guarantees repeats.

**Category mapping:** `category: Bug` / severity `CRITICAL` / `rule_code: ARCH-SEC-AUTH-GAP`

---

### Privilege escalation via object reference

**Shape (language-agnostic):** An endpoint accepts an identifier from
the client and fetches the referenced resource without verifying that
the authenticated actor is authorized to see or modify it. Any
authenticated user can access any resource by guessing IDs.

**Decidable at:** `diff`

**Why it compounds:** As more resources become addressable by ID,
every new endpoint inherits the shape. One missing owner-check
compromises the full set of records the endpoint can reach.

**Category mapping:** `category: Bug` / severity `CRITICAL` / `rule_code: ARCH-SEC-IDOR`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Authz scattered | `rg -n "user\.role\|is_admin\|has_permission\|check_perm" <handlers>/` counting inline checks; cross-reference with presence/absence of a single policy module (e.g., `policies/`, `authz/`). |
| Trust-boundary confusion | `bandit -r src/` (B608 SQL injection, B602 shell), `semgrep --config auto`; OR `rg -n "subprocess.*shell=True\|render_template_string\|exec\(\|eval\(" <dir>/` showing user input on the path. |
| Committed secrets | `gitleaks detect`, `trufflehog filesystem .`, GitHub secret scanning; OR `rg -n "AKIA[0-9A-Z]{16}\|sk_live_\|-----BEGIN" <repo>/`. |
| Missing auth check | `rg -n "@app\.(get\|post\|route)\|app\.(get\|post)\(" <routes>/` cross-referenced with `rg -nL "@require_auth\|requires_auth\|app\.use\(auth" <same-files>/` showing routes without the guard. |
| IDOR | `rg -n "\.get\(id\)\|findById\(\s*req\.params" <dir>/` cross-referenced with absence of `owner_id = current_user\|\.where.*user_id` in the same handler; OR a pentest-style test fetching another user's resource. |

Prose alone never satisfies proof. CRITICAL findings must cite a
concrete reproduction.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: security-architecture
  file: src/api/documents.py
  line: 73
  rule_code: ARCH-SEC-IDOR
  severity: CRITICAL
  source: lens-derived
  decidable_at: diff
  checklist_score: 5/5
  status: VALIDATED
  evidence: |
    GET /documents/{id} at line 73 fetches the Document by primary key
    and returns the full body without any owner or tenant check. Other
    handlers in the same file (e.g., /folders/{id}, line 41) call
    `require_owner(request.user, folder)` before returning. This route
    omits the check.
  proof: |
    $ curl -H "Authorization: Bearer <user-A-token>" \
           https://local/documents/$(doc-id-owned-by-user-B)
    → 200 OK, returns user B's private document contents. Expected 403.
    Regression test: tests/api/test_documents.py::test_cross_tenant_read_denied
    — currently failing.
  suggested_fix: |
    Replace the naked `Document.get(id)` with a helper that takes
    (request.user, id) and filters by owner_id/tenant_id at the query
    level, raising 403 on miss. Apply the same pattern to every
    handler in this file. AGENTS.md already documents the pattern for
    /folders/.
```
````

---

## Few-shot: good dismissal

A reviewer sees `GET /public/status/{id}` fetching a status object by
ID without an auth check and flags IDOR. It is **not** an IDOR when
the resource is intentionally public, the response contains only
non-sensitive status metadata that any unauthenticated client may
read, and the route is registered in a dedicated `public_router` that
documents the design. The smell is about private resources exposed by
missing checks; unconditionally public endpoints are not the shape.
Similarly, a configuration constant `DEBUG_KEY = "development"` is not
a committed-secrets violation if the value is a non-sensitive marker
used for local-only feature gating — the check should be "does this
grant access to anything?" not "does the variable name contain 'key'?"

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Authz scattered | partial — should mandate policy module | ✅ | ✅ |
| Trust-boundary confusion | ❌ — emerges in code | ✅ | ✅ |
| Committed secrets | ❌ | ✅ | ✅ |
| Missing auth check | partial — should mandate default-deny registration | ✅ | ✅ |
| IDOR | partial — should mandate owner-scoped fetch helper | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see code.
When `plan_present: true` and the plan addressed the policy layer,
pr-review/cleanup may emit `category: Architectural Drift` with
`decidable_at: design`.
