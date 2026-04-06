#!/usr/bin/env python3
"""Audit skill compliance for ~/.skills style repositories."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED_RE = re.compile(r"(anthropic|claude)", re.IGNORECASE)
FIRST_SECOND_PERSON_RE = re.compile(
    r"\b(i|i'm|i've|i'd|we|we're|we've|our|ours|you|you're|you've|your|yours)\b",
    re.IGNORECASE,
)
WHEN_RE = re.compile(r"\buse when\b|\bwhen the user\b|\bwhen users\b", re.IGNORECASE)
CONTENTS_RE = re.compile(r"^##\s+(contents|table of contents)\b", re.IGNORECASE | re.MULTILINE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass
class Issue:
    severity: str  # FAIL or WARN
    file: Path
    rule: str
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Return (frontmatter dict, line_count_including_delimiters)."""
    if not text.startswith("---\n"):
        return {}, 0

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, 0

    block = text[4:end]
    data: dict[str, str] = {}
    try:
        if yaml is not None:
            loaded = yaml.safe_load(block) or {}
            if isinstance(loaded, dict):
                for key, value in loaded.items():
                    if value is None:
                        data[str(key)] = ""
                    else:
                        data[str(key)] = str(value).strip()
        else:
            raise ValueError("yaml parser unavailable")
    except Exception:
        # Fallback parser for malformed blocks.
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")

    fm_line_count = block.count("\n") + 3
    return data, fm_line_count


def is_local_md_link(link: str) -> bool:
    if link.startswith(("http://", "https://", "#", "~", "/")):
        return False
    return link.lower().endswith(".md")


def one_level_deep(link: str) -> bool:
    link = link.split("#", 1)[0].split("?", 1)[0]
    parts = [p for p in link.split("/") if p not in ("", ".")]
    return len(parts) <= 2


def audit_skill(skill_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = skill_path.read_text(encoding="utf-8")
    frontmatter, fm_lines = parse_frontmatter(text)

    if not frontmatter:
        issues.append(Issue("FAIL", skill_path, "frontmatter", "Missing or invalid YAML frontmatter."))
        body_lines = len(text.splitlines())
    else:
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")

        if not name:
            issues.append(Issue("FAIL", skill_path, "name", "Frontmatter missing `name`."))
        else:
            if not NAME_RE.match(name):
                issues.append(
                    Issue(
                        "FAIL",
                        skill_path,
                        "name-format",
                        "`name` must match ^[a-z0-9-]{1,64}$.",
                    )
                )
            if RESERVED_RE.search(name):
                issues.append(
                    Issue(
                        "FAIL",
                        skill_path,
                        "name-reserved",
                        "`name` must not include reserved words like anthropic/claude.",
                    )
                )

        if not description:
            issues.append(Issue("FAIL", skill_path, "description", "Frontmatter missing `description`."))
        else:
            if len(description) > 1024:
                issues.append(
                    Issue("FAIL", skill_path, "description-length", "`description` exceeds 1024 characters.")
                )
            if FIRST_SECOND_PERSON_RE.search(description):
                issues.append(
                    Issue(
                        "FAIL",
                        skill_path,
                        "description-voice",
                        "`description` should be third-person (avoid I/you/we).",
                    )
                )
            if not WHEN_RE.search(description):
                issues.append(
                    Issue(
                        "FAIL",
                        skill_path,
                        "description-when",
                        "`description` should include when to use the skill (for discovery).",
                    )
                )

        body_lines = max(0, len(text.splitlines()) - fm_lines)

    if body_lines > 500:
        issues.append(
            Issue(
                "FAIL",
                skill_path,
                "line-budget",
                f"SKILL.md body is {body_lines} lines; must be <= 500.",
            )
        )

    for link in LINK_RE.findall(text):
        if not is_local_md_link(link):
            continue
        if not one_level_deep(link):
            issues.append(
                Issue(
                    "FAIL",
                    skill_path,
                    "reference-depth",
                    f"Reference is deeper than one level: {link}",
                )
            )

    # Companion file TOC warnings (>100 lines)
    skill_dir = skill_path.parent
    for companion in sorted(skill_dir.rglob("*.md")):
        if companion.name == "SKILL.md":
            continue
        content = companion.read_text(encoding="utf-8")
        if len(content.splitlines()) <= 100:
            continue
        top = "\n".join(content.splitlines()[:40])
        if not CONTENTS_RE.search(top):
            issues.append(
                Issue(
                    "WARN",
                    companion,
                    "companion-contents",
                    "Companion file over 100 lines should include `## Contents` near the top.",
                )
            )

    return issues


def discover_skills(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*/SKILL.md") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit skill compliance.")
    parser.add_argument("root", nargs="?", default=".", help="Skill root path (default: current directory)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"ERROR: Root path does not exist: {root}", file=sys.stderr)
        return 2

    skills = discover_skills(root)
    if not skills:
        print(f"No SKILL.md files found under {root}")
        return 0

    all_issues: list[Issue] = []
    for skill in skills:
        all_issues.extend(audit_skill(skill))

    fails = [i for i in all_issues if i.severity == "FAIL"]
    warns = [i for i in all_issues if i.severity == "WARN"]

    print(f"Audited {len(skills)} skills in {root}")
    print(f"FAIL: {len(fails)}  WARN: {len(warns)}")

    for issue in sorted(all_issues, key=lambda x: (x.severity != "FAIL", str(x.file), x.rule)):
        rel = issue.file.relative_to(root)
        print(f"[{issue.severity}] {rel} :: {issue.rule} :: {issue.message}")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
