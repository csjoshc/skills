# G5 Live-Fire Gate Rules

## Contents

- Fresh artifact rule
- Tearing down the old stack (authorization gate)
- Reusing the existing data volume

**G5 must run against a freshly rebuilt artifact — never a stale one.** If the
> live-fire harness uses containers, rebuild images from the working tree
> (`docker compose up -d --build`) and **stop any pre-existing/duplicate-project
> containers first** — a health check that passes against a 4-day-old container
> built from the *un-pruned* code is a **false green** that proves nothing. Verify
> the thing serving the port is the rebuilt artifact (check the compose project
> name and image build time; the dir-derived project name differs between a
> worktree and the main checkout, so both stacks can exist at once and collide on
> ports). Same rule for a dev server, a reinstalled venv, or a cached build:
> restart it from the pruned tree before trusting the result. Note that a
> container DB volume is per-project — a freshly rebuilt stack starts with an
> **empty** corpus, so the data-dependent gates (pipeline row-counts, corpus
> search) need a re-ingest or a baseline run on the un-pruned stack for comparison.

**Tearing down the old stack is a required G5 step — not optional.** Full e2e
validation is only real against the rebuilt artifact, so a pre-existing/long-running
stack holding the ports **must be stopped** and the pruned stack brought up in its
place (then migrate + seed/ingest so the data-dependent gates can run). This
disrupts a running environment (and the operator may be watching it), so it is an
**authorization gate: raise an HITL question before stopping a stack you did not
start** — state what you'll stop, that its data volume is preserved (`docker
compose stop`/`stop <containers>`, not `down -v`, so it is restartable), and that
the rebuilt stack starts with an empty DB. Proceed once authorized; never skip the
teardown just to avoid the disruption — an unvalidated prune is not done. Record
the authorization and the e2e result in the plan.

**Reuse the existing data volume — don't re-ingest into an empty one.** The
data-dependent gates (row-counts, corpus search, provenance) are far cheaper to
validate against the corpus you already have. Run the rebuilt stack so it attaches
the *existing* DB volume rather than a fresh empty one: easiest is to bring it up
under the **same compose project name** (project name defaults to the directory
basename, so a git **worktree** gets a *different* name and a *different* volume —
that is the usual reason a rebuilt stack comes up empty; override with `-p
<old-project>` or `COMPOSE_PROJECT_NAME`). Alternatives: an `external: true` shared
volume, or point `DATABASE_URL` at the running DB. **Postgres is single-writer** —
only one server per data volume at a time, so stop the old app/server first; the
two stacks can't both be live on one volume. After attaching, **confirm the app
reports the real provider/embedding model, not the mock** (a rebuilt-for-boot
stack often defaults to a mock provider, which makes corpus-search scores
meaningless — the query vector won't match a corpus embedded by the real model).
For provenance, embed a probe query with the real model yourself and compare your
pgvector similarity to the app's score; matching to ~3 dp proves the same path.
