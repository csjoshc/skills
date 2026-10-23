#!/usr/bin/env python3
"""Codex PreToolUse adapter: pipe the hook payload to ../../merge-gate.py, translate the answer.

Codex runs the tool anyway when a hook crashes, times out or prints nothing usable, so every
failure here answers deny instead of staying silent. All policy lives in the gate; this file
only converts its exit status into Codex's deny JSON. Codex sends the same
{tool_name, tool_input, cwd} shape as Claude, so the payload needs no translation.
"""

import json
import subprocess
import sys
from pathlib import Path

TIMEOUT = 5  # seconds, matching the registration's timeout
GATE = Path(__file__).resolve().parents[2] / "merge-gate.py"


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


def main() -> int:
    payload = sys.stdin.buffer.read()  # opaque: the gate parses it
    try:
        run = subprocess.run([sys.executable, str(GATE)], input=payload,
                             capture_output=True, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return deny("BLOCKED [merge-gate]: the gate did not answer in time.")
    except OSError as exc:
        return deny(f"BLOCKED [merge-gate]: the gate could not run ({exc.strerror}).")
    if run.returncode == 0:
        return 0
    detail = run.stderr.decode(errors="replace").strip()
    if run.returncode == 2 and detail:
        return deny(detail)
    return deny(detail or f"BLOCKED [merge-gate]: the gate exited {run.returncode}.")


if __name__ == "__main__":
    sys.exit(main())
