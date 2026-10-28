// OpenCode (v2) adapter for hooks/merge-gate.py: the plugin equivalent of the OMP extension.
// All policy lives in the Python gate. This file only maps OpenCode's execute.before event to
// the gate's payload and the gate's exit code to a thrown error, which OpenCode reports as a
// Tool.Error and no tool call runs. Link it, do not copy:
//   ln -s ~/.skills/hooks/adapters/opencode/merge-gate.ts ~/.config/opencode/plugins/merge-gate.ts
//
// Contract (OpenCode 2.0.32): ctx.tool.hook("execute.before", ({tool, input}) => void) runs for
// every tool call, including code-mode and MCP calls; a throw blocks it. There is no fail-open
// switch here on purpose, so a missing interpreter or a broken gate also blocks.
import { spawnSync } from "node:child_process"
import { realpathSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const TIMEOUT_MS = 5000 // the gate's own budget in every harness
const GATE = join(dirname(realpathSync(fileURLToPath(import.meta.url))), "..", "..", "merge-gate.py")
const PYTHON = process.platform === "win32" ? ["py", "-3"] : ["python3"]
const SHELL = new Set(["shell", "bash"])

// The gate reads a shell command or an MCP name. OpenCode flattens MCP tools to
// <server>_<tool>, so every other tool is presented with the mcp__ prefix the gate expects;
// the gate then matches its known suffixes and ignores unrelated tools.
function gateName(tool: string): string {
  if (SHELL.has(tool)) return "Bash"
  // Code mode and MCP servers have both shown `server.tool` and `server_tool`; the gate
  // matches underscore suffixes, so flatten dots before qualifying the name.
  const flat = tool.replaceAll(".", "_")
  return flat.startsWith("mcp__") ? flat : `mcp__${flat}`
}

/** Block reason from the gate, or null to allow. */
function verdict(payload: object): string | null {
  const [cmd, ...args] = PYTHON
  const run = spawnSync(cmd, [...args, GATE], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    timeout: TIMEOUT_MS,
  })
  if (run.error) return `BLOCKED [merge-gate]: the gate could not run (${run.error.message}).`
  if (run.status === 0) return null
  return run.stderr.trim() || `BLOCKED [merge-gate]: the gate exited ${run.status}.`
}

export default {
  id: "merge-gate",
  async setup(ctx: any) {
    ctx.tool.hook("execute.before", (event: any) => {
      const reason = verdict({
        tool_name: gateName(String(event.tool ?? "")),
        tool_input: event.input ?? {},
        cwd: ctx.location?.directory,
      })
      if (reason) throw new Error(reason)
    })
  },
}
