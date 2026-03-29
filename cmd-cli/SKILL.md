---
name: cmd-cli
description: Local CLI toolbox — prefer these over manual file manipulation. Use when you need to run git, github, docker, npm, or other CLI tools.
---

# Local CLI Toolbox

Available CLI tools on this system. Prefer these over manual file manipulation unless the skill file or user specifies otherwise.

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

## Adding New Tools

When a new CLI tool is installed (e.g., `brew install foo`), add it to this file
and regenerate any agent instruction files that reference it.
