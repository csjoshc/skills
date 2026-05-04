#!/usr/bin/env python3
"""
Safety checks for caveman compress — file size and sensitive content.

Exits 0 if safe to compress. Non-zero with reason on failure.
"""

import sys
from pathlib import Path


MAX_SIZE_BYTES = 500_000

SENSITIVE_PATTERNS = [
    "credentials",
    "secrets",
    "private_key",
    "password",
    "api_key",
    "token",
    ".ssh",
    ".aws",
]


def has_sensitive_content(content: str) -> bool:
    content_lower = content.lower()
    return any(pattern in content_lower for pattern in SENSITIVE_PATTERNS)


def check_file(filepath: Path) -> tuple[bool, str]:
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return (False, f"failed to read: {e}")

    if len(content) > MAX_SIZE_BYTES:
        return (False, f"file too large: {len(content)} bytes (max {MAX_SIZE_BYTES})")

    if has_sensitive_content(content):
        return (False, "file contains sensitive content (credentials/secrets)")

    return (True, "")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 safety.py <filepath>")
        sys.exit(2)

    safe, reason = check_file(Path(sys.argv[1]))
    if safe:
        print("safe")
        sys.exit(0)
    else:
        print(f"unsafe: {reason}")
        sys.exit(1)
