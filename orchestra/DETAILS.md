# Orchestra — Advanced Details & Deep Dives

This is a companion document for the Orchestra suite of skills (`orchestra`, `orchestrate`, `run-ticket`). It contains detailed implementation patterns and reference data.

## Execution Modes: Single vs Sequential

| Aspect | Single Mode (`--mode single`) | Sequential Mode (`--mode sequential`) |
|--------|------------------------------|--------------------------------------|
| **Graph Path** | `entry → build → complete` | `entry → spec → build → review → complete` |
| **Planning** | Agent scratchpad (internal) | Dedicated `SPEC` node + `.handoff/` file |
| **Review** | Self-verification only | Dedicated `REVIEW` node + human/audit check |
| **Latency** | Low (Single LLM call per run) | High (Multiple handoffs/calls) |
| **Best For** | Capable models (Sonnet, Opus), non-ambiguous tasks | Smaller models, complex decomposition tasks |

### Single Mode Deep Dive
Research shows 80% of coding tasks work best with a single capable agent.
- **Node logic:** Tickets in `NEW`, `SPEC`, or `PLAN` route directly to the `build` node.
- **Verification:** Post-edit validation includes syntax/lint checks and LLM-guided verification of acceptance criteria.

### Sequential Mode Deep Dive
- **`spec` node:** Planner writes a detailed implementation plan at `.handoff/plan-<stem>.md`.
- **`build` node:** Implementer reads the handoff and implementation targets.
- **`review` node:** QA auditor checks code, updates to `COMPLETE`, `BUILD` (retry), or `BLOCKED`.

---

## Common Execution Patterns

### Pattern A: Standard Delegate (Cost-Saving)
Use a Frontier model (Opus/Sonnet) to create tickets, then delegate to a Standard model (Composer 2/Qwen) for execution.
```bash
# Frontier created 10 tickets, run them with a cheaper tier
python main.py --project ~/Projects/myapp --profile work --model claude-composer-2-fast --concurrency 2
```

### Pattern B: Sequential Fallback
Use simpler models in a structured pipeline to ensure quality via multiple "eyes".
```bash
python main.py --project ~/Projects/myapp --profile private --mode sequential --model qwen3.5-plus
```

---

## Profile Matching Logic (run-ticket)

If selections don't match a pre-built profile, the orchestrator generates a temporary config:

| Selection | Resulting Policy |
|-----------|------------------|
| cursor, single | `work` |
| cursor, chain [cursor, opencode] | `mixed` |
| opencode, chain [...] | `qwen_chain` |
| cursor, tiered | `cursor` (tier preset) |
| free models, tiered | `cost_saver` (tier preset) |

### Custom Runtime Config
For advanced users, provide a `.yaml` config:
```yaml
profiles:
  myprofile:
    primary_runtime: cursor
    runtime_chain: [cursor, opencode]
    providers:
      cursor: {model: "claude-composer-2-fast"}
      opencode: {model: "opencode/big-pickle"}
    max_runtime_switches: 1
```

---

## Inter-Agent Communication Rules

- **Strict Isolation:** Each agent session is fresh. Communication is only via `Stage:` and `.handoff/` files.
- **No Messages in Body:** Do NOT leave notes/questions for other agents in the ticket body. Use the `handoff` skill or mark the ticket `BLOCKED`.
- **Raw File Output:** Do NOT wrap file outputs in triple backticks in implementation steps — write directly to the filesystem.

---

## Troubleshooting & Common Mistakes

| Symptom | Probable Cause | Corrective Action |
|---------|----------------|-------------------|
| **Ticket skipped** | Dependency not `COMPLETE` | Verify `Depends-On:` tags in YAML header. |
| **Infinite loop** | Agent fails to update `Stage:` | Run `ticket-critic` to audit for vagueness. |
| **Path failure** | Wrong project root | Verify `--project` points to the dir with `.tickets/`. |
| **Failover error** | Rate limits or API failure | Check `runtime-policy.yaml` for fallback chain. |
| **`python main.py` not found** | Resolved in product repo | Always resolve orchestrator in `~/Projects/orchestra`. |

---

## Directory Reference

| Path | Purpose |
|------|---------|
| `.tickets/` | Source of truth for tasks. `Stage:` field required. |
| `.tickets/archive/` | Storage for terminal-state tasks. |
| `.handoff/` | Inter-stage communication (spec -> build). |
| `.orchestra/` | Runtime telemetry, PIDs, and logs. |
| `.orchestra.db` | SQLite DAG and run tracker. |
| `PROGRESS.md` | Append-only human-readable log of completion. |
