# Production-Bound PRs

## Pre-launch checklist (production-bound PRs)

<!-- merged from addyosmani/agent-skills shipping-and-launch -->

Use when the PR ships to production directly or behind a flag. Skip for purely internal changes.

| Category | Must be true |
|---|---|
| Code quality | Tests, build, lint, types pass; no `console.log`; error paths handled |
| Security | No secrets in tree; `npm audit` clean (high/critical); auth/authz checks on new routes; CORS not wildcard |
| Performance | No N+1; bundle within budget; indexes on new queries; CWV in "Good" |
| Accessibility | Keyboard reachable; AA contrast; focus management on new modals; no axe warnings |
| Infrastructure | Env vars set; migrations ready; health check live; logging + error reporting wired |
| Documentation | README / API docs / ADR / CHANGELOG updated as applicable; **removed packages/modules also removed from docs, diagrams, CI path filters, helm values, and any manifest descriptions** (see DOC_XREF_SCRUB.md) |

## Rollback plan

Every production-bound PR carries a rollback plan in the description.

```markdown
## Rollback Plan
**Trigger:** error rate > 2x baseline, p95 latency > Xms, or user reports of <issue>.
**Steps:**
1. Disable feature flag <name>  — OR  `git revert <sha> && git push`
2. Verify health check + error monitoring return to baseline
3. Notify <channel>
**Database:** migration <name> reversible via <command>; new-feature data preserved / cleaned per <plan>.
**Time-to-rollback:** flag <1m / redeploy <5m / DB rollback <15m
```
