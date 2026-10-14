#!/usr/bin/env python3
"""Project ~/.secrets/mcp.json into pi's mcp.json files (pi_agent_rust).

Thin entry point over mcp_sync.py, kept so the old command and --target PATH still work.
Usage: mcp_pi.py [--dry-run] [--master PATH] [--target PATH ...]
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcp_sync


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--master", type=Path, default=mcp_sync.MASTER)
    ap.add_argument("--target", type=Path, action="append")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.target:
        targets = [mcp_sync.Target("pi", p, "mcpServers", mcp_sync.to_pi, mode=0o600)
                   for p in args.target]
    else:
        targets = [t for t in mcp_sync.default_targets() if t.name.startswith("pi")]
    return mcp_sync.sync(json.loads(args.master.read_text()), targets, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
