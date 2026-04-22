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
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DESC_MIN_CHARS = 60


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
        # Fallback parser — handles simple key: value and YAML folded/literal block scalars (>- >, |- |).
        lines = block.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if ":" not in line or line.lstrip().startswith("#"):
                i += 1
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value in {">", ">-", "|", "|-"}:
                folded = value.startswith(">")
                parts: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or lines[i] == ""):
                    parts.append(lines[i].strip())
                    i += 1
                data[key] = (" " if folded else "\n").join(p for p in parts if p)
                continue
            data[key] = value.strip('"').strip("'")
            i += 1

    fm_line_count = block.count("\n") + 3
    return data, fm_line_count


def is_local_md_link(link: str) -> bool:
    if link.startswith(("http://", "https://", "#", "~", "/")):
        return False
    return link.lower().endswith(".md")


def resolve_link(skill_path: Path, link: str) -> Path:
    link = link.split("#", 1)[0].split("?", 1)[0]
    return (skill_path.parent / link).resolve()


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
            if len(description) < DESC_MIN_CHARS:
                issues.append(
                    Issue(
                        "WARN",
                        skill_path,
                        "description-min-length",
                        f"`description` is {len(description)} chars; aim for >= {DESC_MIN_CHARS} for discoverability.",
                    )
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

        # name must match parent directory (skill is invoked by dir name)
        if name and skill_path.parent.name != name:
            issues.append(
                Issue(
                    "FAIL",
                    skill_path,
                    "name-matches-dir",
                    f"Frontmatter `name` ({name!r}) must match skill directory ({skill_path.parent.name!r}).",
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

    # Broken local .md references — prevents dead traversal paths
    for link in LINK_RE.findall(text):
        if not is_local_md_link(link):
            continue
        target = resolve_link(skill_path, link)
        if not target.exists():
            issues.append(
                Issue(
                    "FAIL",
                    skill_path,
                    "broken-ref",
                    f"Local reference does not exist: {link}",
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
