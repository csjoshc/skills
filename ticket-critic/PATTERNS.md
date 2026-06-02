# Ticket-Critic Pattern Library

## Contents

- Pattern scoring rubric
- Pattern 1: Unimplemented dependencies
- Pattern 2: Architecture contradictions
- Pattern 3: Scope gaps
- Pattern 4: Unverified assumptions
- Pattern 5: Security vulnerabilities
- Pattern 6: Missing decision points
- Pattern 7: Unclear success criteria
- Pattern 8: Missing tests and verification
- Pattern 9: Layer and architecture confusion
- Pattern 10: Resource and performance blind spots
- Pattern 11: Container image without "image actually starts" smoke AC
- Pattern 12: `readOnlyRootFilesystem: true` without entrypoint-write-path audit
- Pattern 13: NetworkPolicy `namespaceSelector` keyed on a non-auto-applied label
- Pattern 14: Non-root + `drop: ALL` + privileged port (<1024) antipattern

## Pattern Scoring Rubric

For each pattern, assign one of:

- `PASS`: No blocker found.
- `AUTO-RESOLVED`: Question was answered by `~/.skills/STANDARDS.md` or local `./STANDARDS.md`.
- `BLOCKER`: Must be resolved before `Stage: BUILD` execution starts.

Every `BLOCKER` finding must include evidence.

## Pattern 1: Unimplemented Dependencies

**Check:** Ticket assumes services/endpoints/jobs/features that are missing or unstable.

**Red flags:**
- "Already implemented" with no commit/PR reference
- API dependency with no contract
- Dependency ticket still in progress

**Verification:**
1. List explicit dependencies in the ticket.
2. Verify each dependency in codebase or merged PRs.
3. If missing, require merge, contract, or explicit Task 0.

**Block template:**
```markdown
❌ BLOCKED: Unimplemented Dependency

Issue: Ticket assumes [X] exists, but [X] is not merged/stable.

Required before Task 1:
- [ ] Merge dependency, OR
- [ ] Define stable API contract, OR
- [ ] Add Task 0 to implement/verify dependency

Evidence: [ticket line/section + verification result]
```

## Pattern 2: Architecture Contradictions

**Check:** Ticket conflicts with approved architecture decisions or related tickets.

**Red flags:**
- Conflicting implementation directions for same subsystem
- Contradiction with STANDARDS architecture sections
- Multiple tickets changing same layer with incompatible strategy

**Verification:**
1. Identify overlapping tickets and target files.
2. Check `STANDARDS.md` architecture decisions.
3. Require a single authoritative direction when conflict exists.

## Pattern 3: Scope Gaps

**Check:** Required functionality for end-to-end flow is marked out of scope.

**Red flags:**
- Critical backend work marked out of scope for frontend feature
- Required UI/API contract steps omitted
- Security considerations excluded for untrusted input paths

**Verification:**
1. Trace full user flow from trigger to result.
2. Mark each step in-scope or out-of-scope.
3. Block if any mandatory step is missing from scope.

## Pattern 4: Unverified Assumptions

**Check:** Ticket assumes current system behavior without evidence.

**Red flags:**
- "Field already exists" with no schema reference
- "MSW already configured" with no config evidence
- "Pattern already used" with no file link

**Verification:**
1. Extract assumptions from ticket text.
2. Attach file/test evidence for each assumption.
3. Require Task 0 verification for critical assumptions.

## Pattern 5: Security Vulnerabilities

**Check:** Design introduces security risk without mitigation.

**Red flags:**
- User input reaches privileged operations without validation
- Path traversal or arbitrary file access risk
- Missing authz/authn constraints for protected operations
- Missing abuse/rate limiting for exposed endpoints

**Verification:**
1. Identify untrusted input touchpoints.
2. Identify validation, authorization, and containment controls.
3. Block if controls are absent or unspecified.

## Pattern 6: Missing Decision Points

**Check:** Ticket contains unresolved "TBD" or open questions that block implementation.

**Red flags:**
- Open architecture choice with no owner/decision date
- Undefined third-party integration behavior
- Undecided schema or API contract

**Verification:**
1. Collect open questions.
2. Check if resolved in STANDARDS.
3. If unresolved and non-trivial, block for decision.

## Pattern 7: Unclear Success Criteria

**Check:** Acceptance criteria are non-binary or non-testable.

**Red flags:**
- "Works correctly" style criteria
- Missing observable verification conditions
- Missing unhappy-path requirements
- Ticket carries `[FALLIBLE_IO]` tag but no AC specifies failure behavior →
  auto-escalate to BLOCKER

**Verification:**
1. Convert AC to explicit pass/fail behavior.
2. Require measurable outputs and edge cases.
3. Block if criteria remain subjective.

## Pattern 8: Missing Tests and Verification

**Check:** Ticket changes behavior but omits validation strategy.

**Red flags:**
- No test plan for public API changes
- No regression checks for refactor-heavy ticket
- No command-level verification evidence

**Verification:**
1. Require minimum test strategy by layer impacted.
2. Require verification commands and expected results.
3. Block if verification is absent.

## Pattern 9: Layer and Architecture Confusion

**Check:** Responsibilities are mixed across layers.

**Red flags:**
- Domain logic in infrastructure boundary files
- API/controller logic mixed into persistence modules
- Missing ownership boundaries in tasks

**Verification:**
1. Map each task to architecture layers.
2. Compare against architecture decisions.
3. Block if ownership boundaries are ambiguous.

## Pattern 10: Resource and Performance Blind Spots

**Check:** Ticket ignores scalability, latency, memory, or throughput risks.

**Red flags:**
- Unbounded queries or loops
- No pagination or limits for list endpoints
- No timeout/retry/backoff rules for network boundaries
- Ticket carries `[FALLIBLE_IO]` tag but spec has no `## Failure Paths`
  section → auto-escalate to BLOCKER

**Verification:**
1. Identify potential unbounded operations.
2. Require limits, constraints, and failure handling.
3. Block if high-risk performance paths are unaddressed.

## Pattern 11: Container image without "image actually starts" smoke AC

**Check:** Ticket creates or replaces a container image but no AC actually
runs the built image and verifies it stays up. Greps against Dockerfile
*contents* are not a substitute for executing the resulting artifact —
busybox vs GNU coreutils differences, ENTRYPOINT typos, permission
mismatches under non-root, and missing runtime files all surface only at
`docker run` time.

**Pattern signal:**
- Ticket has `action: REPLACE`/`CREATE` on a `Dockerfile`, OR
- Ticket scope contains a `FROM ` directive being authored/modified, AND
- ACs verify Dockerfile *text* (grep, syntax) but no AC executes the
  resulting image and asserts it does not exit immediately.

**Red flags:**
- Every AC is a `grep -E ... Dockerfile` shape; no `docker run` step.
- AC builds the image but only inspects `--format` metadata or
  `ls`-into-the-fs — no probe of the entrypoint actually running.
- Entrypoint is a custom shell script (`start-*.sh`, `entrypoint.sh`)
  and the ticket trusts that "it's the same script from before" without
  re-executing under the new base image's userland (alpine busybox vs
  debian GNU is the classic failure mode: `cp` without `-f`, `sed -i`,
  `mktemp`, `readlink -f`).
- A `docker run -p ...:... && curl /` AC exists but uses a different
  port than the container's privileged listen port — masks
  `bind: Permission denied` failures behind a host-port mapping that
  never gets reached.

**Verification:**
1. List every container-image artifact the ticket creates/replaces.
2. For each, require at least one AC of the form:
   `docker run --rm -d --name probe <image>; sleep 5;
    [ "$(docker inspect -f '{{.State.Running}}' probe)" = "true" ];
    docker rm -f probe`
   — or equivalent (`docker run --rm <image> --version`,
   `docker run --rm <image> /entrypoint --check`).
3. If the entrypoint is a custom shell script, require the smoke AC
   to run the *script*, not just `nginx -t` / `node --version`.
4. If `--build-arg` / `ENV` shape varies by deployment, require the
   smoke to run with the *production* arg shape, not a minimal one.

**Block conditions:**
- No AC executes the image → **BLOCKED**.
- The only "run" AC inspects metadata (`docker image inspect`) or
  static files (`ls /usr/share/...`) without running the entrypoint →
  **BLOCKED** (this is a filesystem audit, not a smoke).
- Custom entrypoint script in scope but no AC runs it under the new
  base image → **BLOCKED**.

**Block template:**
```markdown
❌ BLOCKED: Pattern 11 — No "image actually starts" smoke AC

Issue: Ticket [REPLACES/CREATES] [Dockerfile path]. ACs verify
Dockerfile contents (FR-NN grep) but no AC runs the built image
and confirms the entrypoint stays up.

Risk: Image publishes green; pod CrashLoops at deploy time
(busybox/coreutils drift, ENTRYPOINT shape, permission failure
under non-root).

Required before Task 1:
- [ ] Add AC: `docker build` then `docker run --rm -d --name probe
      <image> && sleep 5 && docker inspect -f '{{.State.Running}}'
      probe | grep -q true && docker rm -f probe`
- [ ] If entrypoint is a custom script, the smoke must invoke
      it (not just `nginx -t` or `node --version`)
- [ ] Smoke must use the production build-arg / env shape

Evidence: AC §[N] — only Dockerfile text is verified;
no entrypoint execution
```

## Pattern 12: `readOnlyRootFilesystem: true` without entrypoint-write-path audit

**Check:** Ticket sets `securityContext.readOnlyRootFilesystem: true` on
a container that uses a custom entrypoint script, but no AC enumerates
every write path that script touches and confirms each is covered by an
`emptyDir`, `configMap`, `secret`, or PVC mount.

The canonical nginx-alpine pair (`/var/cache/nginx` + `/var/run`) covers
nginx itself. It does *not* cover writes the entrypoint script performs
before `exec nginx` — most commonly templating into `/etc/nginx/conf.d/`,
copying TLS certs, or generating runtime config.

**Pattern signal:**
- Helm chart / pod spec has `readOnlyRootFilesystem: true`, AND
- Container `command:` / `args:` / image `ENTRYPOINT` points to a
  shell script (look for `start-*.sh`, `entrypoint.sh`,
  `docker-entrypoint*`, or any `*.sh` in `/usr/local/bin/`).

**Red flags:**
- AC enumerates emptyDir mounts but stops at the canonical nginx pair
  (`/var/cache/nginx` + `/var/run`).
- Entrypoint script is described in scope but the AC list does not
  reference auditing its write operations.
- Risk register mentions `readOnlyRootFilesystem` only in the abstract
  ("RISK: ROFS misconfig") without naming specific write paths.

**Verification:**
1. Open the entrypoint script.
2. Enumerate every write operation:
   `grep -nE '(\s|>|>>|cp|mv|mkdir|touch|tee|sed -i|envsubst)\s+/[^ ]+' entrypoint.sh`
3. For each write target, confirm one of:
   - The target sits under an `emptyDir` mountPath in the pod spec.
   - The target is under a `configMap`/`secret` projected path.
   - The target is under `/tmp` AND `/tmp` is an explicit emptyDir.
4. Require an AC that performs the cross-reference (the audit
   command itself can be the AC), not just an AC that the
   canonical pair is present.

**Block conditions:**
- ROFS:true + custom entrypoint + no write-path-audit AC → **BLOCKED**.
- AC enumerates emptyDirs without naming the entrypoint script
  paths they cover → **BLOCKED** (this is a values-file audit, not a
  write-path audit).
- Entrypoint script writes to `/etc/...` paths and no mount covers
  them → **BLOCKED** (the `/etc` overlay almost never happens via
  emptyDir; usually requires a separate writable config directory).

**Block template:**
```markdown
❌ BLOCKED: Pattern 12 — ROFS without entrypoint write-path audit

Issue: Pod has `readOnlyRootFilesystem: true` and `command:
[/usr/local/bin/<script>.sh]`, but ACs cover only the canonical
nginx pair (`/var/cache/nginx` + `/var/run`). The script writes
to additional paths that the AC list does not enumerate.

Required before Task 1:
- [ ] Run `grep -nE '(>|>>|cp|mv|mkdir|touch|tee|sed -i|envsubst)
      \s+/[^ ]+' <script>.sh` and list every write target
- [ ] For each target, confirm a corresponding mount exists in
      the chart (emptyDir / configMap / secret / projected)
- [ ] Add an AC that re-runs this audit at template time
      (e.g. `helm template ... | yq` cross-reference)

Evidence: securityContext.readOnlyRootFilesystem: true at
[file:line]; entrypoint script at [path]; AC list at [section]
covers only the canonical pair.
```

## Pattern 13: NetworkPolicy `namespaceSelector` keyed on a non-auto-applied label

**Check:** Ticket adds or modifies a `NetworkPolicy` template whose
`namespaceSelector: matchLabels` is keyed on anything other than
`kubernetes.io/metadata.name`. Kubernetes only auto-applies that one
label to every namespace; any other key requires an explicit
`kubectl label namespace ...` step. Without it, the selector matches
no namespaces silently, and ingress/egress traffic is dropped without
an obvious error.

Failures of this shape are invisible at `helm template` time and at
`kubectl apply` time — they manifest only when a cross-pod request
times out (504 / connection refused).

**Pattern signal:**
- Ticket adds/modifies a NetworkPolicy with
  `namespaceSelector: matchLabels:`, AND
- The label key is not `kubernetes.io/metadata.name` (e.g. `name:`,
  `app:`, `tier:`, `chart:`).

**Red flags:**
- `namespaceSelector: matchLabels: name: <release-name>` (the
  classic shape — looks correct, isn't auto-applied).
- Selector key matches the helm release/namespace name and the
  ticket treats that as "obviously already there".
- Risk register mentions "NetworkPolicy enforcement is implicit OOS
  (kindnet ignores it silently)" but does *not* mention the label
  prerequisite, leaving the failure mode hidden in non-kindnet
  clusters where the policy IS enforced.

**Verification:**
1. List every `namespaceSelector: matchLabels` in the ticket's
   templates.
2. For any key that is not `kubernetes.io/metadata.name`, require
   one of:
   - A bootstrap AC that runs
     `kubectl label namespace <ns> <key>=<value> --overwrite`.
   - A helm pre-install hook (`helm.sh/hook: pre-install`) that
     applies the label.
   - An operator-runbook AC documenting the manual labeling step.
   - A rewrite to use `kubernetes.io/metadata.name`.
3. Block if none of the above is present.

**Block conditions:**
- `namespaceSelector: matchLabels` with non-auto label + no pairing
  AC → **BLOCKED**.
- AC says "verify NetworkPolicy renders" but does not verify the
  policy actually *matches* anything → **BLOCKED** (template
  rendering does not exercise selector semantics).

**Block template:**
```markdown
❌ BLOCKED: Pattern 13 — NetworkPolicy selector with no label-bootstrap AC

Issue: networkpolicy.yaml uses `namespaceSelector: matchLabels:
{<key>: <value>}` where `<key>` is not `kubernetes.io/metadata.name`.
Kubernetes does not auto-apply this label; without an explicit
`kubectl label namespace` step the selector matches no namespaces
and all in-policy traffic is silently dropped.

Required before Task 1, one of:
- [ ] Rewrite selector to use `kubernetes.io/metadata.name`
- [ ] Add bootstrap AC: `kubectl label namespace <ns>
      <key>=<value> --overwrite`
- [ ] Add helm pre-install hook that applies the label
- [ ] Add operator-runbook AC documenting the labeling step

Evidence: networkpolicy.yaml [section]; AC list [section]
contains no paired labeling step.
```

## Pattern 14: Non-root + `drop: ALL` + privileged port (<1024) antipattern

**Check:** Ticket configures a container with all three of:
1. Non-root execution (`runAsUser != 0` or `runAsNonRoot: true`).
2. Linux capabilities `drop: [ALL]` (no add of `NET_BIND_SERVICE`,
   or add but on a base image where ambient capabilities don't
   activate the way you expect).
3. A `containerPort` < 1024.

This combination is fragile. Adding `NET_BIND_SERVICE` back to
`capabilities.add` is the textbook fix but does not always work —
some base images (notably alpine-nginx) need either file capabilities
on the binary (`setcap cap_net_bind_service=+ep`) or PID-1
ambient-capability inheritance that the entrypoint does not preserve.
The robust fix is to rebind to a port ≥ 1024 and let the Kubernetes
Service do the privileged port mapping.

**Pattern signal:**
- securityContext: `runAsNonRoot: true` OR `runAsUser: <non-zero>`, AND
- securityContext: `capabilities.drop: [ALL]` (no `NET_BIND_SERVICE` in
  add, OR add present but no AC proves it activates), AND
- A `containerPort: <1024>` (`80`, `443`, `53`, etc.) anywhere in the
  pod spec or values.

**Red flags:**
- nginx-alpine + UID 101 + port 80 + drop ALL (the canonical
  failure shape).
- `capabilities.add: [NET_BIND_SERVICE]` *with* drop ALL, but no AC
  runs `getcap` on the binary or verifies the container can actually
  bind.
- Comment in values says "needs NET_BIND_SERVICE" but no smoke AC
  exercises the bind.
- Probe `httpGet.port: http` where `http` is a named port mapped to
  80, with no test that the listen actually happens.

**Verification:**
1. Check securityContext for the three-way combination.
2. If present, require one of:
   - **Preferred:** rebind container to a port ≥ 1024
     (`containerPort: 8080`), Service maps `port: 80 → targetPort: 8080`.
     Verify with `grep -E "containerPort:\s*8080" deployment.yaml`
     and `grep -E "targetPort:\s*8080" service.yaml`.
   - **Acceptable but require evidence:** keep port 80 with
     `capabilities.add: [NET_BIND_SERVICE]` AND an AC that runs
     `getcap` on the exact server binary in the exact base-image
     tag, AND a smoke AC that boots the container and asserts the
     listen succeeds (`docker run -d ... && curl -fsS .../ ` ).

**Block conditions:**
- All three signals present + no port rebind + no `getcap` AC →
  **BLOCKED**.
- `capabilities.add: [NET_BIND_SERVICE]` claimed as the fix without
  a smoke AC proving it works on the chosen base image → **BLOCKED**.
- Hidden port-mapping AC (e.g. host-side `docker run -p 8080:80`)
  that bypasses the in-container bind — these mask the failure →
  **BLOCKED**.

**Block template:**
```markdown
❌ BLOCKED: Pattern 14 — non-root + drop ALL + privileged port

Issue: Container runs as UID <N> with `capabilities.drop: [ALL]`
and listens on port <P> (<1024). This combination commonly fails
with `bind: Permission denied` on alpine and minimal base images,
and `capabilities.add: [NET_BIND_SERVICE]` is not a reliable fix
without per-image verification.

Required before Task 1, one of (preferred → fallback):
- [ ] Rebind container to a port ≥1024 (e.g. 8080); have
      Service map `port: 80 → targetPort: 8080`. Update probes.
- [ ] Keep port <P> and add `capabilities.add: [NET_BIND_SERVICE]`
      PLUS a Read-First AC running `getcap` on the server binary
      in the exact base-image tag PLUS a smoke AC that boots the
      container and confirms the listen succeeds.

Evidence: securityContext at [file:line]; containerPort: <P>
at [file:line]; no rebind AC; no getcap AC.
```

---

## Pattern 15: Source-prose hygiene — naming, identifiers, and leaked planning metadata

**Check:** Scan the ticket for any of these author-time directives that
would put planning artifacts into the long-lived tree:

1. **Cycle / gate / ticket / slice IDs in committed paths or filenames**
   — proof directories named `proof/<N>G<n>-*` or `proof/[Ss]lice-*/`,
   verify scripts named after the ticket (`scripts/verify-T-732.sh`),
   test files under `tests/tickets/`, doc filenames in `docs/`
   carrying a cycle slug.
2. **Vendor / runtime tokens in supposedly-agnostic identifiers** —
   config filenames like `agent.local-dmr.yaml`, env vars like
   `OLLAMA_BASE_URL` when the project surface is the agnostic
   `LLM_BASE_URL`, class names like `DockerModelRunnerClient` in a
   module whose other branches handle multiple providers, doc-page
   titles "Local dev with DMR" for a runtime-agnostic doc.
3. **Internal labels in committed prose** — docstrings, code comments,
   doc bodies, API response fields, enum values, or error codes that
   carry `ADR-NN`, `Constitution P\d+`, `T-\d+`, `RISK-NN`, `AC-\d+`,
   `Slice \d+`, `\d+G\d+`, `IG-\d+G\d+`, `Pattern \d+`, `AP-\d+`,
   `F-\d+`, `M\d+`, or similar. These labels point nowhere from a
   public branch and rot the moment the cycle closes.

These three sub-patterns share a common cause: the author imports the
ticket / spec / review system's organizing principle into the code or
docs without thinking about the audience that will read them after the
cycle closes.

**Pattern signal:**
- A task's `Files:` or `What to build:` lists a path containing a
  gate / cycle / ticket slug
- A task instructs the author to commit a `verify-<ticket-id>.sh`,
  `test-<gate>-*.py`, or similar one-off script
- A task names a file with a runtime / vendor suffix that contradicts
  the SPEC's "runtime-agnostic" framing
- An acceptance criterion references "ADR-NN documents the design",
  but the AC's `Verify:` doesn't include prose review of the
  docstring/comment that mentions the ADR
- A task's docstring template includes an `ADR-NN:` prefix or
  references `Constitution P\d+`, `Slice \d+`, ticket numbers, or
  review-time finding codes (`F-NNN`, `RISK-NN`)

**Red flags:**
- `proof/4G-ui-cycle/` or similar gate-slug paths in playwright /
  pytest / artifact configs the ticket mandates committing
- `tests/tickets/test_T732_*.py` — tests should live under
  `tests/<type>/`, not `tests/tickets/`
- `scripts/verify-6g1.sh` — verify scripts named after their birthing
  ticket get committed and never deleted
- A config filename `agent.local-dmr.yaml` whose spec elsewhere says
  `LLM_RUNTIME` is configurable
- Task instructions like *"add a docstring `\"\"\"ADR-CHAT-1: single SSE
  endpoint\"\"\"`"* — the AC name-drops the label without requiring
  prose that explains the why
- A `## Docs to Update` section missing on a ticket that changes a
  documented surface (endpoint shape, env var, config filename,
  public API)

**Verification:**
1. For each path in `Files:` or any mandated artifact path, check
   that the basename does **not** match cycle / gate / ticket
   patterns (`\d+G\d+`, `T-\d+`, `IG-\d+G\d+`, `Slice \d+`). Test
   fixture directories under `tests/` are exempt only when the path
   *is* the test scope.
2. For any new committed config filename, check that it does not
   contain a runtime / vendor token (`dmr`, `ollama`, `bedrock`,
   `s3`, ...) unless the file is by design vendor-specific (e.g.
   `provision_dmr.sh`, `terraform/aws/*.tf`).
3. For docstring templates the ticket includes verbatim, run the
   `SKILL_NOISE_TERMS` grep set; any hit must be paired with a
   prose explanation of *why*, not just the label.
4. Require a `## Docs to Update` section in the ticket body whenever
   the ticket changes a surface mentioned outside `.tickets/` (run
   the locator grep from spec-writer's *Docs to Update* section to
   confirm there are no untracked references).

**Block conditions:**
- Committed path matches `^(proof|evidence)/\d+G\d+` or
  `(scripts|tools)/(verify|test)-T-\d+` or similar →
  **BLOCKED** (rename to feature-scoped + env-overridable).
- Config filename contains a runtime/vendor token in a ticket whose
  SPEC asserts the runtime/vendor is configurable → **BLOCKED**
  (rename; see AP-25).
- Docstring template contains an internal label without prose
  rationale → **BLOCKED** (rewrite the docstring template).
- Surface-changing ticket missing `## Docs to Update` checklist →
  **BLOCKED** (author the checklist before BUILD).

**Block template:**

````markdown
❌ BLOCKED: Pattern 15 — source-prose hygiene

Issue: Ticket mandates committing <path|filename|identifier|docstring>
that <embeds cycle ID | bakes in vendor token | drops internal label
without rationale | omits Docs to Update section>.

Required before Task 1:
- [ ] Rename <artifact> to a feature/scope-based name (suggestion:
      `<new-name>`); make any per-cycle artifact directory
      env-overridable via `<ENV_VAR>` with a stable default.
- [ ] Rewrite docstring template so prose explains *why*; remove
      bare label drops, or pair the label with a stable
      `docs/ADR-*.md` pointer and a one-sentence summary.
- [ ] Author `## Docs to Update` checklist from the
      `git grep -nE "\\b<changed-surface>\\b"` output (see
      spec-writer's mandatory-section guidance).

Evidence: <path/filename> at [file:line]; SPEC asserts <agnosticism>
at [file:line]; no `## Docs to Update` section.
````



## Pattern 16: AC shell commands must be runnable in the target environment

**Why this matters.** ACs that prescribe shell commands as their
verifier are only valid if the command itself can execute. If the
chosen base image lacks the binary, the path math (`../../`) is off
by one level, the env-var is unset, or the CLI flag requires a newer
version than the runner has, the AC will silently never execute and
the ticket will pass review while shipping a broken verification
path. This is the single most common reason that "all ACs PASS" reports
don't predict working operator behavior.

**Detection signals:**

- AC verifier references a CLI binary (`curl`, `wget`, `jq`, `nc`,
  `actionlint`, `make`) but the ticket doesn't verify the binary
  is present in the runtime environment (container base image,
  CI runner default packages, dev host expectations)
- Shell scripts include path math (`$SCRIPT_DIR/../../`,
  `cd ../..`) — the number of `../` doesn't match the actual
  depth of the script from the implied target directory
- AC verifier invokes a Makefile target — the ticket doesn't
  show or reference the target body to confirm it works (the
  target itself may be broken in ways that aren't visible in
  the AC line)
- CLI tool used with a `--flag` whose support depends on version
  (`docker compose ps --format json` requires Compose v2.4+;
  `find -path` is GNU; `sed -i.bak` is BSD-vs-GNU divergent)
- Command references `localhost` (vs `127.0.0.1`) in a context
  where IPv4/IPv6 resolution may differ across base images
  (`nginx:alpine` resolves `localhost` to `::1` first; nginx
  listens only on IPv4 → "connection refused" from healthcheck)
- AC verifier depends on env-vars (`$GOOGLE_API_KEY`,
  `$DATABASE_URL`) but the ticket doesn't enumerate which env
  the verifier expects to be set

**BLOCK conditions:**

- Container ticket prescribes `curl` healthcheck on an image
  whose base is known to lack it (`python:slim`, `alpine`-based
  without explicit `apk add curl`) → **BLOCKED**
- Bash script uses `$SCRIPT_DIR/../../../..` without an explicit
  comment showing the absolute path that resolves to →
  **BLOCKED** (require the comment OR an `assert`-style
  check)
- AC verifier expects an env-var that isn't named in the ticket's
  Verify-commands preamble → **BLOCKED**

**WARN conditions:**

- Command uses a tool that *probably* exists (`make`, `python3`)
  but isn't explicitly verified — issue **WARN** with a
  one-line suggestion to add a sanity-check step.
- `localhost` is used where `127.0.0.1` is safer → **WARN**.

**Block template:**

````markdown
❌ BLOCKED: Pattern 16 — AC shell command not verified runnable

Issue: AC <N> at [file:line] prescribes <command>. The runtime
environment (<container base image | CI runner | dev host>) is
not verified to contain <binary | flag-support | env-var>.

Required before Task 1:
- [ ] Add a verifier step ahead of the AC command that confirms
      the binary is present (`command -v <bin>`) or replace with
      a stdlib alternative (e.g., `python -c "import
      urllib.request; …"` instead of `curl`).
- [ ] If path math is involved, add a comment showing the
      absolute path the `../../` resolves to AND an assertion
      (`[ "$(basename $(pwd))" = "expected-dir" ] || exit 1`)
      that fails fast on mis-rooting.
- [ ] Name every env-var the verifier reads in the ticket's
      Verify-commands preamble.

Evidence: <command at file:line>; base image <name>; ticket does
not list <binary>.
````


## Pattern 17: Operator entry point requires end-to-end smoke gate

**Why this matters.** When a ticket introduces a user-facing command
(make target, wrapper script, docker compose target), every prior
AC may pass while the command still fails because nothing exercised
the literal operator invocation. Bugs that survive in this gap are
usually compose semantics (services without profile auto-up under
`--profile X`), env-file paths, env-var injection, binary
availability in the chosen base image, or shell-script path math.

This is the ticket-critic gatekeeper for AP-26 (Operator Entry
Point Not Smoke-Tested).

**Detection signals:**

- Ticket creates or modifies a Makefile target, wrapper script, or
  docker compose wrapper intended for operator use
- No AC in the ticket OR in any named integration gate invokes the
  operator command literally from a fresh-clone state and asserts
  exit 0
- Per-ticket ACs use explicit-service docker compose forms
  (`docker compose up svc1 svc2`) but the operator target uses
  `up` without a service list — the explicit form sidesteps the
  ticket's actual bug surface
- The downstream integration gate that should exercise this is
  itself skip-prone (gated on Docker / Ollama / DB availability)
  — if it skips, the operator command is never end-to-end
  validated
- The ticket's own subagent verification used an explicit /
  sidestep invocation; the wrapper target was not re-tested after
  the build
- For profile-scoped wrappers, no AC asserts that
  non-profile-tagged or other-profile services are *not* started

**BLOCK action:** require an explicit AC in either this ticket or a
named gate that:

1. Starts from a clean state (no caches assumed;
   `make down && rm -rf <state-dir>` first)
2. Runs the literal operator command (`make compose-patent`, etc.)
3. Asserts exit 0 AND that only the intended side-effects occurred
   (intended services up, no unintended services started)
4. Captures stdout/stderr as an artifact under
   `tests/integration/artifacts/`

For profile-scoped wrappers, require a negative AC pair: positive
AC = "intended services healthy", negative AC = "other-profile
or no-profile services NOT running after the wrapper completes".

**WARN action:** if a gate exists but is skip-prone, require the
skip path to be loud (logged at WARNING level, mentioned in final
report) AND a hermetic alternative that exercises as much of the
wrapper as the test environment allows.

**Block template:**

````markdown
❌ BLOCKED: Pattern 17 — operator entry point not smoke-tested

Issue: Ticket introduces <wrapper-command> but no AC executes the
literal invocation from a fresh-clone state. Subagent verification
used <sidestep-command>, which masks bugs in the wrapper.

Required before Task 1:
- [ ] Add an AC: "Given a fresh-clone state, when `<wrapper-command>`
      runs from the project root, then exit 0 AND only the intended
      services / files / env-vars exist."
- [ ] For profile-scoped wrappers, add a negative AC: "Services
      outside the targeted profile do NOT run after the wrapper
      completes."
- [ ] If the AC is deferred to a downstream gate, link the gate
      ticket explicitly and verify the gate's own ACs are NOT
      skip-prone for the wrapper exercise.

Evidence: <wrapper-command at file:line>; <sidestep-command at
file:line>; no AC ties them together.
````


## Pattern 18: Subagent claims require adversarial evidence review

**Why this matters.** A BUILD subagent's "AC passed" report describes
what the agent *intended* to do, not necessarily what's true on disk.
The agent saw its own tool outputs, decided ACs were satisfied,
flipped Stage to COMPLETE, and the next ticket starts — without anyone
independently verifying the files exist, the tests actually ran (not
just `--collect-only`), or the commands actually exited 0.

Observed failure modes in subagent reports:
- ACs that depend on env (DB, Ollama, network) get marked
  PASS-via-skip without external verification of the skip path
- Subagents use sidestep invocations during their own verification
  (explicit service list when the ticket's actual invocation is
  broader) — Pattern 17 lives here too
- Subagents patch files outside the ticket's declared Files: list;
  the deviation is noted in the final report but not flagged for
  human review before the next ticket starts
- Subagent reports cite artifact files at expected paths but the
  files don't exist on disk OR have suspiciously small size (0
  bytes, < expected)
- "All N tests pass" is reported when the test invocation was
  `pytest --collect-only` (collection succeeded; nothing executed)

**Detection signals:**

- Subagent final report contains words like "SKIPPED" / "marked as"
  / "documented as" without explicit external evidence that the
  skipped path is genuinely the right choice
- Stage flipped to COMPLETE but `git diff` against the prior
  checkpoint shows files outside the ticket's declared Files: list
- AC commands the agent claimed to run aren't reproducible from
  the operator's environment (path differs, binary missing, env
  unset)
- Subagent report cites artifact files but they don't exist on
  disk or have suspiciously small size
- Cross-ticket dependencies: the ticket's "downstream gate will
  cover this" claim is unverified — the downstream gate hasn't
  run yet, or has its own skip-prone path

**BLOCK action (gate before next ticket starts):** spawn an
adversarial reviewer subagent with read-only access to:

- `git diff` against the prior checkpoint commit
- the just-completed subagent's final report
- the artifact files under `tests/integration/artifacts/` (or
  equivalent)
- the ticket's ACs (the source of truth — not the subagent's
  interpretation of them)
- relevant `docker logs`, `pytest -v` output, server logs if the
  ticket touched runtime surfaces

The reviewer must produce one of:

- **VERIFIED** — every AC has disk-evidence backing it (file
  exists, test output shows execution, command exit 0 captured)
- **DRIFT-DETECTED** — files were patched outside the declared
  scope, an AC was skipped without justification, or the
  subagent's claim doesn't match what's on disk
- **EVIDENCE-INSUFFICIENT** — the artifacts the AC requires don't
  exist; re-run the AC verification before proceeding

Only **VERIFIED** unblocks the next ticket. Drift and insufficient
evidence return to the BUILD subagent (or the operator) for
remediation.

**WARN action:** if running the full reviewer for every ticket is
too heavy, sample-audit one in three subagent completions; require
full review on:
- integration-gate tickets
- tickets touching infrastructure (compose, Dockerfile, CI workflows)
- tickets whose subagent report contains the word "deviation",
  "adapted", "alternative", or "skipped"

**Reviewer protocol:** see
[`~/.skills/evidence-reviewer/SKILL.md`](~/.skills/evidence-reviewer/SKILL.md)
for the full evidence-reviewer skill, which is the canonical
implementation of this pattern.

**Block template:**

````markdown
❌ BLOCKED: Pattern 18 — subagent claim requires adversarial evidence review

Issue: Ticket <ID> flipped to Stage: COMPLETE by its build subagent,
but the claim has not been independently verified. The subagent's
final report contains <signal: "SKIPPED N ACs" | "deviated from
spec at X" | "files modified outside scope" | etc.>.

Required before next ticket starts:
- [ ] Invoke `/evidence-reviewer` on ticket <ID>, providing:
      git diff vs prior checkpoint, the subagent's final report,
      artifact file paths, ticket ACs.
- [ ] Reviewer must return VERIFIED. If DRIFT-DETECTED or
      EVIDENCE-INSUFFICIENT, the build subagent (or operator)
      remediates and the next ticket waits.

Evidence: <subagent report snippet quoting the deviation>; <git diff
showing out-of-scope files>; <missing artifact path>.
````
