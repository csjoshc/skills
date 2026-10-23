// The OpenCode adapter maps execute.before to the gate payload and blocks by throwing.
// Run with the runtime OpenCode itself uses: BUN_BE_BUN=1 opencode test hooks/adapters/opencode
import { afterEach, describe, expect, test } from "bun:test"
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { pathToFileURL } from "node:url"

const ADAPTER = join(import.meta.dir, "merge-gate.ts")
const originalPath = process.env.PATH
const roots: string[] = []

afterEach(() => {
  process.env.PATH = originalPath
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

/** Loads a copy of the adapter whose ../../merge-gate.py is `gate`, and returns its hook. */
async function load(gate: string) {
  const root = mkdtempSync(join(tmpdir(), "merge-gate-"))
  roots.push(root)
  const holder = join(root, "hooks", "adapters", "opencode")
  mkdirSync(holder, { recursive: true })
  copyFileSync(ADAPTER, join(holder, "merge-gate.ts"))
  const script = join(root, "hooks", "merge-gate.py")
  writeFileSync(script, gate)
  chmodSync(script, 0o755)
  const plugin = (await import(pathToFileURL(join(holder, "merge-gate.ts")).href)).default
  let hook: (event: unknown) => void = () => {}
  await plugin.setup({
    location: { directory: root },
    tool: { hook: (_name: string, fn: (event: unknown) => void) => { hook = fn } },
  })
  return { hook, root }
}

const ALLOW = "import sys\nsys.stdin.read()\n"
const DENY = "import sys\nsys.stdin.read()\nprint('BLOCKED [merge-gate]: gh pr merge.', file=sys.stderr)\nsys.exit(2)\n"

function recorder() {
  const dir = mkdtempSync(join(tmpdir(), "merge-gate-payload-"))
  roots.push(dir)
  const path = join(dir, "payload.json")
  process.env.MERGE_GATE_RECORD = path
  return path
}

const RECORD = "import os, sys\nopen(os.environ['MERGE_GATE_RECORD'], 'w').write(sys.stdin.read())\n"

const shell = (command: string) => ({ tool: "shell", input: { command } })
const call = (hook: (event: unknown) => void, event: unknown) => () => hook(event)

describe("merge gate", () => {
  test("allows a read-only command", async () => {
    const { hook } = await load(ALLOW)
    expect(call(hook, shell("gh pr view 1"))).not.toThrow()
  })

  test("blocks a merge with the gate's reason", async () => {
    const { hook } = await load(DENY)
    expect(call(hook, shell("gh pr merge 1"))).toThrow("BLOCKED [merge-gate]: gh pr merge.")
  })

  test("sends the shell command as Bash with the session directory", async () => {
    const path = recorder()
    const { hook, root } = await load(RECORD)
    hook(shell("git push origin main"))
    const payload = JSON.parse(readFileSync(path, "utf8"))
    expect(payload).toEqual({
      tool_name: "Bash",
      tool_input: { command: "git push origin main" },
      cwd: root,
    })
  })

  test("prefixes an MCP tool the way the gate expects", async () => {
    const path = recorder()
    const { hook } = await load(RECORD)
    hook({ tool: "github_merge_pull_request", input: {} })
    expect(JSON.parse(readFileSync(path, "utf8")).tool_name).toBe("mcp__github_merge_pull_request")
  })

  test("does not mistake an ordinary tool for a shell", async () => {
    const path = recorder()
    const { hook } = await load(RECORD)
    hook({ tool: "read", input: { filePath: "README.md" } })
    expect(JSON.parse(readFileSync(path, "utf8")).tool_name).toBe("mcp__read")
  })

  test("blocks when the interpreter cannot start", async () => {
    const { hook } = await load(ALLOW)
    process.env.PATH = "/nonexistent"
    expect(call(hook, shell("gh pr view 1"))).toThrow("could not run")
  })

  test("blocks on an unexpected gate exit", async () => {
    const { hook } = await load("import sys\nsys.stdin.read()\nprint('boom', file=sys.stderr)\nsys.exit(3)\n")
    expect(call(hook, shell("gh pr view 1"))).toThrow("boom")
  })

  test("blocks a silent unexpected exit", async () => {
    const { hook } = await load("import sys\nsys.exit(7)\n")
    expect(call(hook, shell("gh pr view 1"))).toThrow("exited 7")
  })
})
