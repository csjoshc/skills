// OMP (oh-my-pi) adapter for hooks/merge-gate.py: the reference for other harnesses.
// All policy lives in the Python gate. This file only translates OMP's tool_call event into
// the gate's payload and the gate's exit code back into a block. Link it, do not copy:
//   ln -s ~/.skills/hooks/adapters/omp/merge-gate.ts ~/.omp/agent/extensions/merge-gate.ts
// Contract (OMP 18.12.2): event {toolName, toolCallId, input}, ctx.cwd; return {block, reason};
// a throw or a timeout also blocks the call, so every failure below fails closed.
import { spawnSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

const TIMEOUT_MS = 5000; // the gate's own budget in every harness
const GATE = join(dirname(realpathSync(fileURLToPath(import.meta.url))), "..", "..", "merge-gate.py");
const PYTHON = process.platform === "win32" ? ["py", "-3"] : ["python3"];

/** Block reason from the gate, or null to allow. */
function verdict(payload: object): string | null {
  const [cmd, ...args] = PYTHON;
  const run = spawnSync(cmd, [...args, GATE], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    timeout: TIMEOUT_MS,
  });
  if (run.error) return `merge-gate could not run: ${run.error.message}`;
  if (run.status === 0) return null;
  return run.stderr.trim() || `merge-gate exited ${run.status}`;
}

export default function mergeGate(pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    const shell = event.toolName === "bash";
    if (!shell && !event.toolName.startsWith("mcp__")) return; // MCP tools are mcp__<server>_<tool>
    const reason = verdict({
      tool_name: shell ? "Bash" : event.toolName,
      tool_input: event.input,
      cwd: ctx.cwd,
    });
    if (reason) return { block: true, reason };
  });
}
