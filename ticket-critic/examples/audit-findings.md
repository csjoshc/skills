# Audit Finding Examples

---

## Example 0A: Ralph flag — PASS (eligible ticket, correct schema)

**Ticket excerpt:**
```yaml
---
Stage: BUILD
Ralph: true
Ralph-Reason: "7 additive ACs: new parser module + tests, each grep/pytest-checkable, no bootstrap"
---
```
AC→Tests table has 7 rows, each with a `grep -nE` or `pytest -k` command. Failure Protocol says "revert new files" (not "revert all callers"). No bootstrap language.

**Audit finding:**
```
### Ralph Flag Audit — ✅ PASS

Ralph: true — Verified:
- AC count: 7 ✓ (≥6)
- Scope: additive (new module, new tests) ✓
- All ACs machine-checkable (grep/pytest) ✓
- No bootstrap or "after BUILD" ACs ✓
- Failure Protocol: revert new files only (not all) ✓
- Ralph-Reason: present and specific ✓
```

---

## Example 0B: Ralph flag — BLOCKED (flag contradicts scope)

**Ticket excerpt:**
```yaml
---
Stage: BUILD
Ralph: true
Ralph-Reason: "6 ACs, each checkable"
---
```
Scope section says: "Replace all callers of `run_attempt()` with the new `run_attempt_v2()` signature across the codebase."

**Audit finding:**
```
### Ralph Flag Audit — ❌ BLOCKER

Ralph: true — INVALID. Disqualifier detected:
- Scope is a cross-cutting refactor ("Replace all callers") — per-box commits leave
  callers broken between iterations. Half-done state is worse than not-done.
- This ticket must use Ralph: false.

Required action:
- [ ] Change Ralph: true → Ralph: false
- [ ] Update Ralph-Reason: "Refactor: cross-cutting caller rename, half-done state invalid"
```

---

## Example 0C: Ralph flag — BLOCKED (AC not machine-checkable)

**Ticket excerpt:**
```yaml
Ralph: true
Ralph-Reason: "8 ACs, all checkable"
```
AC→Tests table row: `AC-5 | Verify visually that the progress bar updates smoothly | manual | -`

**Audit finding:**
```
### Ralph Flag Audit — ❌ BLOCKER

Ralph: true — INVALID for AC-5.
- AC-5 uses manual verification. Under Ralph mode, ACs are load-bearing:
  the loop checks the box only when a command exits 0.
- A manual AC breaks the loop — the agent cannot verify it mechanically.

Required action:
- [ ] Replace AC-5 with a machine-checkable command, OR
- [ ] Change Ralph: false with Ralph-Reason explaining the manual AC
```

---

## Example 1: Unimplemented Dependency

**Ticket excerpt:**
> "Frontend calls `POST /api/workflow/load` to import workflow JSON"

**Audit finding:**
```
### Pattern 1: Unimplemented Dependencies — ❌ BLOCKER

Issue: Ticket assumes `POST /api/workflow/load` endpoint exists

Verification:
- Checked `src/server.py`: endpoint not found
- Checked open PRs: no PR for this endpoint
- Ticket dependencies: lists `fixes/implement/11-workflow-load-endpoint.md` (status: in progress)

Required before Task 1:
- [ ] Backend endpoint merged and deployed, OR
- [ ] API contract defined in Architecture Decisions, OR
- [ ] Task 0 added: "Verify backend endpoint exists"

Evidence: Section 2 "API contracts" assumes endpoint exists
```

## Example 2: Auto-Resolved via Architecture Decisions

**Ticket excerpt:**
> "Open question: Should API use REST or GraphQL?"

**Audit finding:**
```
### Pattern 6: Missing Decision Points — ⚠️ AUTO-RESOLVED

Issue: API pattern undecided

Resolution: Architecture Decisions section "API Pattern" says:
> "Default: REST with JSON responses"

Action: Applied REST pattern, updated ticket assumptions

Evidence: Architecture Decisions "API Pattern" section
```

## Example 3: Security Vulnerability

**Ticket excerpt:**
> "Endpoint accepts file path from user, serves file directly"

**Audit finding:**
```
### Pattern 5: Security Vulnerabilities — ❌ BLOCKER

Issue: User-provided file path served without validation

Risk: Path traversal attack (e.g., `../../../etc/passwd`)

Touchpoints needing security review:
- User input: file path parameter
- File access: direct file serving
- Missing: path validation, allowlist directories

Required before Task 1:
- [ ] Path validation strategy (sanitize, allowlist)
- [ ] Directory allowlist defined
- [ ] Architecture Decisions security checklist applied

Evidence: Section 2 "API contracts" lacks validation spec
```

---

## Example 11: Container image without "image actually starts" smoke AC

**Ticket excerpt** (anonymized from a Dockerfile-replacement ticket):
> Action: REPLACE `<app>/Dockerfile` with a multi-stage build…
> COPY `--chmod=755 <app>/start-nginx.sh /usr/local/bin/start-nginx.sh`
> ENTRYPOINT `["/usr/local/bin/start-nginx.sh"]`
>
> AC-1: `docker build … -t test-ui …` exits 0 AND
> `docker image inspect test-ui --format '{{.Size}}'` returns < 105 MB
> AND `docker run --rm test-ui sh -c 'ls /usr/share/nginx/html/index.html'`
> exits 0.
>
> AC-2: `docker run --rm -d -p 8080:80 --name probe test-ui && sleep 2
> && curl -fsS http://localhost:8080/` returns HTTP 200.

**Audit finding:**
```
### Pattern 11 — ❌ BLOCKER

Issue: Ticket REPLACES Dockerfile and ships a custom entrypoint
(`/usr/local/bin/start-nginx.sh`) but no AC executes the entrypoint
under the new base image's userland.

- AC-1 inspects metadata + filesystem; does not run the entrypoint.
- AC-2 attempts a probe but only checks an HTTP response — does not
  separate "entrypoint exited cleanly" from "nginx-default config
  happened to answer because the entrypoint silently fell through".

Risk: busybox `cp` (alpine) errors when the target exists without
`-f`; this is invisible to grep-against-Dockerfile-text ACs and
will CrashLoop only at deploy time.

Required before Task 1:
- [ ] Add an AC that runs:
      docker run --rm -d --name probe test-ui
      sleep 5
      [ "$(docker inspect -f '{{.State.Running}}' probe)" = "true" ]
      docker rm -f probe
- [ ] The smoke must invoke the entrypoint script (not just nginx -t
      or a file check).
- [ ] Run with production --build-arg shape.

Evidence: AC-1 / AC-2 at Acceptance Criteria §1–§2; no `State.Running`
or equivalent post-boot liveness check anywhere in ACs.
```

---

## Example 12: ROFS without entrypoint write-path audit

**Ticket excerpt** (anonymized from a helm subchart ticket):
> values.yaml: `securityContext.readOnlyRootFilesystem: true`,
> `runAsUser: 101`, `capabilities.drop: [ALL]`.
> Container `command:` resolves to image `ENTRYPOINT
> ["/usr/local/bin/start-nginx.sh"]`.
>
> CRITICAL (A-3): `nginxWritableMounts.enabled: true` — emptyDir
> volumes at `/var/cache/nginx` and `/var/run` required when
> `readOnlyRootFilesystem: true`.
>
> AC-7: Deployment includes emptyDir volumes at `/var/cache/nginx`
> and `/var/run`. Verify: `yq … | grep -q '^nginx-cache,nginx-run,$'`.

**Audit finding:**
```
### Pattern 12 — ❌ BLOCKER

Issue: Pod has `readOnlyRootFilesystem: true` plus a custom
entrypoint (`start-nginx.sh`). AC-7 verifies only the canonical
nginx pair (/var/cache/nginx + /var/run). The entrypoint script
also writes to /etc/nginx/conf.d/default.conf (via `cp` of the
selected template) — this path is NOT covered by either emptyDir.

Required before Task 1:
- [ ] Run, against the entrypoint script:
      grep -nE '(>|>>|cp|mv|mkdir|touch|tee|sed -i|envsubst)
      \s+/[^ ]+' <app>/start-nginx.sh
- [ ] For each write target, confirm a corresponding emptyDir /
      configMap / secret / projected mount.
- [ ] Add an AC that re-runs this audit at chart-template time
      (helm template … | yq cross-reference).

Evidence: securityContext.readOnlyRootFilesystem at values.yaml
[section]; entrypoint at <app>/start-nginx.sh; AC-7 covers
canonical pair only.
```

---

## Example 13: NetworkPolicy selector keyed on non-auto-applied label

**Ticket excerpt** (anonymized from a helm NetworkPolicy template):
> networkpolicy.yaml: ingress wired from
> `.Values.networkPolicy.ingress` which renders as
> `from: [{ namespaceSelector: { matchLabels: { name: chat-stack } } }]`.
>
> AC-9: NetworkPolicy is rendered when `networkPolicy.enabled: true`.
> AC-10: `helm template …` exits 0 AND
> `grep -c '^kind: NetworkPolicy'` returns 3.

**Audit finding:**
```
### Pattern 13 — ❌ BLOCKER

Issue: namespaceSelector.matchLabels uses `name: chat-stack`.
Kubernetes only auto-applies `kubernetes.io/metadata.name` to
namespaces; `name=chat-stack` requires an explicit
`kubectl label namespace` step that no AC enforces. Result: the
policy renders cleanly, applies cleanly, and silently matches no
source pods — cross-pod traffic in the namespace is dropped at
runtime (504 / connection refused).

AC-9 / AC-10 verify that the policy renders. Rendering does not
exercise selector semantics.

Required before Task 1, one of:
- [ ] Rewrite selector to
      `namespaceSelector.matchLabels.kubernetes.io/metadata.name:
      chat-stack`.
- [ ] Add bootstrap AC: `kubectl label namespace chat-stack
      name=chat-stack --overwrite`.
- [ ] Add helm pre-install hook that applies the label.
- [ ] Add operator-runbook AC documenting the labeling step.

Evidence: networkpolicy.yaml ingress block [section]; AC §9–§10
verify rendering only.
```

---

## Example 14: Non-root + drop ALL + privileged port

**Ticket excerpt** (anonymized from a helm subchart ticket):
> values.yaml:
>   securityContext:
>     runAsNonRoot: true
>     runAsUser: 101
>     readOnlyRootFilesystem: true
>     capabilities: { drop: [ALL] }
>   service: { type: ClusterIP, port: 80 }
>   deployment.containerPort: 80
>   livenessProbe.httpGet.port: http   # http → 80
>
> AC-5: `containerPort: 80`. Verify: `grep -E "containerPort:\s*80$"
> deployment.yaml`.

**Audit finding:**
```
### Pattern 14 — ❌ BLOCKER

Issue: All three signals present:
- runAsNonRoot: true / runAsUser: 101
- capabilities.drop: [ALL] (no NET_BIND_SERVICE add)
- containerPort: 80 (<1024)

This combination CrashLoops with `bind() to 0.0.0.0:80 failed
(13: Permission denied)` on the chosen base image. Adding
`capabilities.add: [NET_BIND_SERVICE]` is not a reliable fix
without per-image verification — alpine-nginx's file
capabilities and ambient-capability inheritance from the
entrypoint vary by tag.

Required before Task 1, one of (preferred → fallback):
- [ ] Rebind container to port 8080. Update deployment.yaml
      containerPort: 8080, service.yaml targetPort: 8080
      (service.port stays 80). Update livenessProbe /
      readinessProbe port refs.
- [ ] Keep port 80 + add capabilities.add: [NET_BIND_SERVICE]
      PLUS a Read-First AC running `getcap` on the nginx
      binary in the exact base-image tag PLUS a smoke AC that
      runs the container and asserts the listen succeeds.

Evidence: securityContext.runAsUser=101 at values.yaml
[section]; capabilities.drop=[ALL] at values.yaml [section];
containerPort: 80 at deployment.yaml [section]; no rebind
AC; no getcap AC.
```
