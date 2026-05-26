# Deploy-time AC conventions (container / helm / k8s tickets)

Source-file ACs (`helm lint`, `helm template --validate`, `grep` for a key)
are necessary but **not sufficient** for any ticket whose artifact is loaded
into a running container or cluster. The `ui-ghcr-publish` cycle shipped a
chart that passed `helm lint` but CrashLooped on deploy (busybox `cp` over
existing file, nginx :80 bind under non-root + drop ALL, NetworkPolicy
`namespaceSelector` keyed on an unset label, ROFS vs script write paths).
The pattern: **ACs verified source, never verified the running pod.**

When generating a ticket, scan the `Files:` list and the rendered templates.
If any of the three triggers below fires, emit the matching AC verbatim.
Cross-references the `ticket-critic` patterns 11/12/13 (auto-escalated to
BLOCKER at pre-build audit).

## Convention 1 — Helm subchart / chart tickets require a `helm install --wait` deploy-smoke AC

**Trigger:** the ticket creates or modifies any file under `helm/**/Chart.yaml`,
`helm/**/templates/*.yaml`, or `helm/**/values.yaml`.

**Required AC (append after the last render/lint AC):**

```bash
helm install <release> <chart-path> -n <ns> --create-namespace \
  --wait --timeout=2m \
  --set image.tag=<provided-tag> \
  [--set ...other-required-pins]
# AND
kubectl wait deployment/<workload-name> --for=condition=Available --timeout=60s -n <ns>
# Both return exit 0.
```

Needs a real cluster (kind, k3d, minikube, or shared test cluster). If the
operator's local environment does not have one, the ticket **must** mark the
AC `(deferred to cycle's terminal MTP gate ticket)` and the terminal gate
ticket inherits the AC. Do not drop it — `helm lint` PASS is not deploy
proof.

## Convention 2 — Init / entrypoint scripts require a Read-First on the base image's existing files

**Trigger:** the ticket's `Files:` list contains an entry matching
`start-*.sh`, `entrypoint*.sh`, `docker-entrypoint*`, or `*-entry.sh`, AND
the script writes to a path **outside** `/tmp`, `/var/run`, or `/var/cache`
(those are conventionally writable or already covered by emptyDir mounts).

**Required Read-First entry (one per write path):**

```
docker run --rm --entrypoint /bin/sh <base_image> -c 'ls -la <write-path>'
```

The agent then knows whether the base image ships a pre-existing file at
that path. If it does, the script must use `-f` / `rm` first / a different
target path / or accept an emptyDir mount that shadows it. The
`ui-ghcr-publish` T-730 cookiecutter shipped a `cp $tls_conf /etc/nginx/conf.d/default.conf`
that busybox-`cp`-errored because `nginx:1.27-alpine` already ships
`/etc/nginx/conf.d/default.conf` — caught only at deploy time.

## Convention 3 — NetworkPolicy ACs: cross-pod connectivity + namespace-label setup

**Trigger A (always, for any ticket adding/modifying a NetworkPolicy template):**

Append an AC of the form:

```bash
# From a test pod in the source namespace selector:
kubectl run np-probe --rm -i --restart=Never -n <src-ns> \
  --image=busybox:1.36 -- \
  wget --timeout=3 -qO- http://<target-service>.<target-ns>.svc.cluster.local:<port>/<healthpath>
# Returns 200 body within 3s; exit 0.
```

**Trigger B (conditional):** scan the rendered template for
`namespaceSelector: matchLabels`. If the key is anything other than
`kubernetes.io/metadata.name` (which Kubernetes auto-applies), the ticket
**must** include a setup AC that applies the label to the namespace via one
of: `kubectl label ns <ns> <key>=<value>` in a bootstrap script, an
init-container, a helm pre-install hook, or an explicit operator-runbook
step in the ticket body. Without this, the selector matches zero pods and
cross-pod traffic silently 504s — the T-732 failure mode.

Recommended detection during spec generation:

```bash
grep -oE 'namespaceSelector:\s*$\s*matchLabels:\s*$\s*[a-zA-Z0-9_./-]+:' \
  <rendered-template> | grep -v 'kubernetes.io/metadata.name'
# If any output: emit the labeling-AC automatically.
```

## Concrete shape — pulled from T-732 (`.tickets/T-732-helm-c3-ui-subchart.md`)

T-732's AC list had `helm lint helm/chat-stack` (AC10) and the
`helm template` render set (AC5–AC9). Under these conventions it would also
have carried:

**Added under Convention 1:**

```
13. helm install + Available smoke (deferred to IG-7G3a terminal gate).
    Verify (on terminal gate ticket):
      helm install chat-stack helm/chat-stack -n chat-stack --create-namespace \
        --wait --timeout=2m \
        --set c3-flight-mcp.image.tag=v0.0.0-rc1 \
        --set c3-chat.image.tag=v0.0.0-rc1 \
        --set c3-ui.image.tag=v0.0.0-rc1
      kubectl wait deployment/c3-ui --for=condition=Available --timeout=60s -n chat-stack
```

**Added under Convention 3 — Trigger A:**

```
14. Cross-pod reachability from c3-chat → c3-ui.
    Verify:
      kubectl run np-probe --rm -i --restart=Never -n chat-stack \
        --image=busybox:1.36 -- \
        wget --timeout=3 -qO- http://c3-ui.chat-stack.svc.cluster.local:80/
      # Exit 0; body contains '<!doctype html>'.
```

**Added under Convention 3 — Trigger B** (the template renders
`namespaceSelector: matchLabels: name: chat-stack` — not the auto-applied
`kubernetes.io/metadata.name`):

```
15. Namespace label setup precondition.
    Verify (run before AC13):
      kubectl label ns chat-stack name=chat-stack --overwrite
      kubectl get ns chat-stack -o jsonpath='{.metadata.labels.name}' | grep -q '^chat-stack$'
    OR: refactor the template's namespaceSelector to use the auto-applied
    `kubernetes.io/metadata.name: chat-stack` key (preferred — no operator
    runbook step needed).
```

**Note on T-730** (which would also be hit by Convention 2 — its
`Files:` list included `react/start-nginx.sh`):

```
Read-First:
  - "react/start-nginx.sh"
  - "docker run --rm --entrypoint /bin/sh nginx:1.27-alpine -c 'ls -la /etc/nginx/conf.d/'"
  # Outputs: default.conf already present → script must `rm -f` or use a
  # different target path before `cp`.
```
