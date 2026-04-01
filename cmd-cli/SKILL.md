---
name: cmd-cli
description: Local CLI toolbox — prefer these over manual file manipulation. Use when you need to run git, github, docker, npm, or other CLI tools.
---

# Local CLI Toolbox

## TL;DR (Quick Start)
Use CLI tools instead of manual file manipulation for: git operations, GitHub interactions (pr, issues), JSON processing, code search, and container management.

**When to use:** Running git commands, creating PRs, searching code, Docker operations, package management.

**Invocation:** Run commands directly in terminal. Use `--help` to discover syntax.

## Core Utilities

| Tool | Purpose | Common Commands |
|------|---------|-----------------|
| `git` | Version control | `git status`, `git diff`, `git log`, `git branch` |
| `gh` | GitHub CLI | `gh pr create`, `gh issue list`, `gh run list` |
| `jq` | JSON processing | `jq '.key'`, `jq -s` |
| `rg` (ripgrep) | Code search | `rg "pattern"`, `rg -l "pattern"` |
| `curl` | HTTP requests | `curl -s`, `curl -X POST` |

## Package Managers

| Tool | Purpose | Common Commands |
|------|---------|-----------------|
| `brew` | Homebrew (macOS) | `brew install`, `brew list`, `brew search` |
| `npm` | Node package manager | `npm install`, `npm run`, `npm list` |
| `pnpm` | Node package manager | `pnpm install`, `pnpm add` |
| `bun` | Node runtime + pkg mgr | `bun run`, `bun install` |
| `uv` | Python package manager | `uv pip install`, `uv sync` |
| `pip3` | Python package manager | `pip3 install`, `pip3 list` |

## Containers & Cloud

| Tool | Purpose | Common Commands |
|------|---------|-----------------|
| `docker` | Container runtime | `docker ps`, `docker build`, `docker run` |
| `docker-compose` | Multi-container orch | `docker-compose up`, `docker-compose logs` |
| `kubectl` | Kubernetes CLI | `kubectl get pods`, `kubectl apply` |

## Python & Rust

| Tool | Purpose | Common Commands |
|------|---------|-----------------|
| `python3` | Python runtime | `python3 -m`, `python3 script.py` |
| `cargo` | Rust package manager | `cargo build`, `cargo test`, `cargo run` |
| `rustc` | Rust compiler | `rustc main.rs` |

## IDEs & Editors

| Tool | Purpose |
|------|---------|
| `code` | VS Code CLI |
| `cursor` | Cursor IDE CLI |

## Other

| Tool | Purpose | Common Commands |
|------|---------|-----------------|
| `ollama` | Local LLM runtime | `ollama list`, `ollama run` |
| `hub-tool` | Docker registry | `hub-tool --help` |

## Workflow

1. **Discover** — If unsure of syntax, run `tool --help` or `man tool`
2. **Verify** — Check command output before assuming success
3. **Pipe** — Use pipes to refine data (`gh issue list --json | jq`)

## Examples

**Example 1: Check git status**
Input: `git status`
Output: Shows modified, staged, and untracked files.

**Example 2: Create a GitHub PR**
Input: `gh pr create --title "feat: add login" --body "$(cat <<'EOF'
## Summary
- Added user login functionality
EOF
)"`
Output: Creates PR and returns URL.

**Example 3: Search code and format JSON**
Input: `rg "function.*validate" --json | jq '.[] | .path'`
Output: List of file paths containing validate functions.

## When to Use

- **Git operations:** status, diff, log, branch management
- **GitHub work:** create PRs, list issues, check runs
- **Code search:** ripgrep for finding patterns
- **JSON processing:** jq for parsing API responses
- **Container management:** docker, kubectl
- **NOT for:** writing/editing files (use file tools)

## Decision Tree

Use this skill when you need to:

1. **Is the task a file operation (read/write/edit)?**
   - YES → Use file manipulation tools instead
   - NO → Continue

2. **Is the task a code/search operation?**
   - YES → Use `rg` (ripgrep) for pattern matching
   - NO → Continue

3. **Is the task a Git/GitHub operation?**
   - YES → Use `git` or `gh` CLI tools
   - NO → Continue

4. **Is the task a container/cluster operation?**
   - YES → Use docker, kubectl, or helm
   - NO → Consider other skills

## Assumptions & Escalation

- **Tier 1 (reversible):** Minor style issues — proceed, flag for post-review
- **Tier 2 (architecture):** Design concerns blocking — check Architecture Decisions (spec-writer skill), block if unresolved
- **Tier 3 (security):** Security vulnerabilities — always block for human confirmation
