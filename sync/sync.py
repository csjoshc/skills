#!/usr/bin/env python3
"""
Universal Skills Sync System
Cross-platform symlink audit, repair, and permission management.

Usage:
    python sync.py              # Full audit + repair (verbose)
    python sync.py --audit      # Audit only, no changes
    python sync.py --project    # Add project-level .skills symlink
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

# Standalone scripts also load through importlib in the isolated regression checks.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from directory_links import create_link, is_link, remove_link


# ─── OS Detection ───────────────────────────────────────────────────────────


class OS(Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


def detect_os() -> OS:
    system = platform.system().lower()
    if system == "windows":
        return OS.WINDOWS
    elif system == "darwin":
        return OS.MACOS
    return OS.LINUX


OS_TYPE = detect_os()
IS_WINDOWS = OS_TYPE == OS.WINDOWS


# ─── Path Resolution ────────────────────────────────────────────────────────

HOME = Path.home()
SKILLS_DIR = HOME / ".skills"
# Per-skill links preserve native private definitions and Codex's .system directory.
LOG_FILE = SKILLS_DIR / "sync.log"


def resolve_path(path_str: str) -> Path:
    """Resolve a path string with ~ expansion."""
    return Path(path_str).expanduser()


# ─── Platform Definitions ───────────────────────────────────────────────────


@dataclass
class PlatformConfig:
    name: str
    skills_symlink: Path
    permission_type: str  # "external_directory", "trust", "unmanaged"
    config_path: Optional[Path] = None
    permission_note: str = ""  # shown for "unmanaged" platforms
    platform_key: str = ""  # Set during PLATFORMS construction


PLATFORMS = {
    "opencode": PlatformConfig(
        name="OpenCode",
        skills_symlink=HOME / ".config" / "opencode" / "skills",
        permission_type="external_directory",
        config_path=HOME / ".config" / "opencode" / "opencode.json",
        platform_key="opencode",
    ),
    "codex": PlatformConfig(
        name="Codex",
        skills_symlink=HOME / ".codex" / "skills",
        permission_type="unmanaged",
        permission_note="no managed config; sandbox reads outside the workspace not confirmed",
        platform_key="codex",
    ),
    "cursor": PlatformConfig(
        name="Cursor",
        skills_symlink=HOME / ".cursor" / "skills",
        permission_type="trust",
        platform_key="cursor",
    ),
    "claude": PlatformConfig(
        name="Claude",
        skills_symlink=HOME / ".claude" / "skills",
        permission_type="trust",
        platform_key="claude",
    ),
    "omp": PlatformConfig(
        name="OMP",
        skills_symlink=HOME / ".omp" / "agent" / "skills",
        permission_type="trust",
        platform_key="omp",
    ),
    # Devin CLI reads ~/.config/devin/skills; its ".claude" import does not cover skills.
    "devin": PlatformConfig(
        name="Devin",
        skills_symlink=HOME / ".config" / "devin" / "skills",
        permission_type="trust",
        platform_key="devin",
    ),
    "copilot": PlatformConfig(
        name="Copilot",
        skills_symlink=HOME / ".copilot" / "skills",
        permission_type="trust",
        platform_key="copilot",
    ),
}


# ─── Status Types ───────────────────────────────────────────────────────────


class Status(Enum):
    SYNCED = "✅ Synced"
    BROKEN = "❌ Broken"
    MISSING = "⚠️  Missing"
    WRONG_TARGET = "❌ Wrong Target"
    NOT_INSTALLED = "➖ Not Installed"
    PERMISSION_OK = "✅ OK"
    PERMISSION_UNMANAGED = "➖ Unmanaged"
    PERMISSION_MISSING = "❌ Missing"
    PERMISSION_BROKEN = "❌ Broken"


@dataclass
class AuditResult:
    platform_key: str
    platform_name: str
    symlink_status: Status
    symlink_details: str = ""
    permission_status: Optional[Status] = None
    permission_details: str = ""
    repaired: bool = False
    errors: list = field(default_factory=list)


# ─── Logging ────────────────────────────────────────────────────────────────


class Logger:
    def __init__(self, verbose: bool = True, log_file: Optional[Path] = None):
        self.verbose = verbose
        self.log_file = log_file
        self.messages = []

    def log(self, level: str, message: str):
        entry = f"[{level}] {message}"
        self.messages.append(entry)
        if self.verbose:
            print(entry)
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")

    def info(self, message: str):
        self.log("INFO", message)

    def warn(self, message: str):
        self.log("WARN", message)

    def error(self, message: str):
        self.log("ERROR", message)

    def debug(self, message: str):
        if self.verbose:
            self.log("DEBUG", message)


if IS_WINDOWS:
    sys.stdout.reconfigure(encoding="utf-8")


# ─── Symlink Operations ─────────────────────────────────────────────────────


def is_symlink(path: Path) -> bool:
    return is_link(path)


def get_symlink_target(path: Path) -> Optional[Path]:
    if is_symlink(path):
        return path.resolve()
    return None


def create_symlink(link_path: Path, target: Path) -> bool:
    """Create a directory link while preserving real local entries."""
    try:
        create_link(link_path, target)
        return True
    except (OSError, ValueError) as exc:
        print(f"directory link failed: {exc}")
        return False


def owned_skill_link(path):
    """Only links into the shared store belong to this sync."""
    if not is_symlink(path):
        return False
    raw_target = os.readlink(path)
    if IS_WINDOWS:
        raw_target = raw_target.removeprefix("\\\\?\\")
    target = Path(raw_target)
    if not target.is_absolute():
        target = path.parent / target
    return target.resolve().is_relative_to(SKILLS_DIR.resolve())


# ─── Symlink Audit ──────────────────────────────────────────────────────────


def audit_symlink(
    platform_key: str, config: PlatformConfig, logger: Logger
) -> AuditResult:
    """Audit a single platform's skills symlink."""
    result = AuditResult(
        platform_key=platform_key,
        platform_name=config.name,
        symlink_status=Status.MISSING,
    )

    symlink_path = config.skills_symlink

    if not symlink_path.parent.exists() and not (
        platform_key == "copilot" and (HOME / ".vscode").is_dir()
    ):
        result.symlink_status = Status.NOT_INSTALLED
        result.symlink_details = (
            f"Parent directory {symlink_path.parent} does not exist"
        )
        logger.info(f"{config.name}: Not installed (parent dir missing)")
        return result

    if not symlink_path.exists() and not is_symlink(symlink_path):
        result.symlink_status = Status.MISSING
        result.symlink_details = "Symlink does not exist"
        logger.warn(f"{config.name}: Skills symlink missing")
        return result

    # Real directory of per-skill symlinks (see SYMLINK_MAP.md)
    if is_symlink(symlink_path):
        result.symlink_status = Status.WRONG_TARGET
        result.symlink_details = (
            f"{config.name} skills must be a real directory of per-skill symlinks, "
            "not a single symlink to ~/.skills"
        )
        logger.warn(f"{config.name}: Skills path is a full symlink (unsafe)")
        return result

    if not symlink_path.is_dir():
        result.symlink_status = Status.BROKEN
        result.symlink_details = f"{config.name} skills path is not a directory"
        logger.warn(f"{config.name}: Skills path is not a directory")
        return result

    issues = []
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not (skill_dir / "SKILL.md").is_file():
            continue
        link = symlink_path / skill_dir.name
        if owned_skill_link(link) and link.resolve() != skill_dir.resolve():
            issues.append(f"wrong: {skill_dir.name}")
        elif not link.exists() and not is_symlink(link):
            issues.append(f"missing: {skill_dir.name}")

    for entry in symlink_path.iterdir():
        if not entry.name.startswith(".") and owned_skill_link(entry) and not (SKILLS_DIR / entry.name / "SKILL.md").is_file():
            issues.append(f"stale: {entry.name}")

    if issues:
        result.symlink_status = Status.BROKEN
        result.symlink_details = (
            f"Per-skill link issues: {', '.join(sorted(issues)[:8])}"
            + ("…" if len(issues) > 8 else "")
        )
        logger.warn(f"{config.name}: {len(issues)} skill link issue(s)")
        return result

    result.symlink_status = Status.SYNCED
    result.symlink_details = "per-skill symlinks → ~/.skills/<name>"
    logger.info(f"{config.name}: Per-skill symlinks OK")
    return result


def repair_symlink(config: PlatformConfig, logger: Logger) -> bool:
    """Repair a broken skills symlink."""
    # Codex keeps system-managed skills under ~/.codex/skills/.system and
    # must remain a real directory of per-skill symlinks — never a single
    # symlink to ~/.skills (that shadows .system and risks rmtree of it).
    return sync_per_skill_links(config, logger)


def sync_per_skill_links(config: PlatformConfig, logger: Logger) -> bool:
    """Ensure the platform's skills path is a real dir with per-skill symlinks to master.

    Preserves platform-only entries (e.g. Codex's `.system/`, plain dirs) and only
    adds/repairs symlinks for master skills that have SKILL.md.
    """
    links_dir = config.skills_symlink
    skills_root = SKILLS_DIR.resolve()
    logger.info(f"Syncing {config.name} per-skill symlinks...")

    legacy_system = None
    if is_symlink(links_dir):
        if links_dir.resolve() != SKILLS_DIR.resolve():
            logger.error(f"{config.name}: reconcile the foreign skills root before syncing")
            return False
        if config.platform_key == "codex" and (links_dir / ".system").is_dir():
            legacy_system = (links_dir / ".system").resolve()
        logger.warn(
            f"{config.name} skills path is a symlink to the master store; "
            "converting to a real directory with per-skill links."
        )
        remove_link(links_dir)

    links_dir.mkdir(parents=True, exist_ok=True)
    if legacy_system is not None and not (links_dir / ".system").exists():
        if not create_symlink(links_dir / ".system", legacy_system):
            return False

    added = 0
    repaired = 0
    success = True
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not (skill_dir / "SKILL.md").is_file():
            continue

        link_path = links_dir / skill_dir.name
        expected = skill_dir.resolve()

        if is_symlink(link_path):
            try:
                current = link_path.resolve()
            except (OSError, RuntimeError):
                current = None
            if current != expected:
                if current is None or not current.is_relative_to(skills_root):
                    logger.debug(f"  Preserving native symlink: {link_path.name}")
                    continue
                if create_symlink(link_path, skill_dir):
                    repaired += 1
                    logger.info(f"  Repaired: {link_path.name}")
                else:
                    success = False
            continue

        if link_path.exists():
            # Real dir/file (Codex-managed or local) — leave untouched
            logger.debug(f"  Skipping non-symlink entry: {link_path.name}")
            continue

        if create_symlink(link_path, skill_dir):
            added += 1
            logger.info(f"  Linked: {link_path.name}")
        else:
            success = False

    # Drop broken symlinks that no longer exist in master
    stale = []
    for entry in links_dir.iterdir():
        if not entry.name.startswith(".") and owned_skill_link(entry) and not (SKILLS_DIR / entry.name / "SKILL.md").is_file():
            try:
                target = entry.resolve()
            except (OSError, RuntimeError):
                continue
            if target.is_relative_to(skills_root):
                stale.append(entry)
    for entry in stale:
        remove_link(entry)
        logger.info(f"  Removed broken: {entry.name}")

    if config.platform_key == "codex":
        if (links_dir / ".system").is_dir():
            logger.info("  .system/ present (Codex-managed; preserved)")
        else:
            logger.warn(
                "  .system/ missing — Codex will recreate it on next Desktop/CLI start"
            )

    logger.info(
        f"  {config.name} sync done (added={added}, repaired={repaired}, stale_removed={len(stale)})"
    )
    return success


# ─── Permission Config Audit ────────────────────────────────────────────────


# opencode v2 reads a `permissions` rule array. `*` also matches `/`, so one rule covers the tree.
OPENCODE_SKILLS_RULES = [
    {"action": "external_directory", "resource": "~/.skills/*", "effect": "allow"},
    {"action": "read", "resource": "~/.skills/*", "effect": "allow"},
]


def opencode_allows_skills(data: dict) -> bool:
    """True if the config allows ~/.skills, as a v2 rule array or the older v1 object."""
    for rule in data.get("permissions") or []:
        if (
            rule.get("action") == "external_directory"
            and rule.get("effect") == "allow"
            and ".skills" in rule.get("resource", "")
        ):
            return True
    v1 = (data.get("permission") or {}).get("external_directory")
    return isinstance(v1, dict) and any(".skills" in k and v == "allow" for k, v in v1.items())


def audit_permissions(config: PlatformConfig, logger: Logger) -> AuditResult:
    """Audit permission configuration for a platform."""
    result = AuditResult(
        platform_key="",
        platform_name=config.name,
        symlink_status=Status.SYNCED,
    )

    if config.permission_type == "trust":
        result.permission_status = Status.PERMISSION_OK
        result.permission_details = "Workspace trust (no config needed)"
        return result

    if config.permission_type == "unmanaged":
        result.permission_status = Status.PERMISSION_UNMANAGED
        result.permission_details = config.permission_note
        return result

    if not config.config_path or not config.config_path.exists():
        result.permission_status = Status.PERMISSION_MISSING
        result.permission_details = f"Config file missing: {config.config_path}"
        logger.warn(f"{config.name}: Permission config missing")
        return result

    try:
        data = json.loads(config.config_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        result.permission_status = Status.PERMISSION_BROKEN
        result.permission_details = f"Parse error: {e}"
        logger.error(f"{config.name}: Permission config parse error: {e}")
        return result

    if opencode_allows_skills(data):
        result.permission_status = Status.PERMISSION_OK
        result.permission_details = "~/.skills allowed"
    else:
        result.permission_status = Status.PERMISSION_MISSING
        result.permission_details = "No allow rule for ~/.skills"
    return result


def repair_permissions(config: PlatformConfig, logger: Logger) -> bool:
    """Add the ~/.skills allow rules to opencode's config, keeping every other key and the mode."""
    path = config.config_path
    try:
        data = json.loads(path.read_text()) if path.exists() else {}
    except (OSError, json.JSONDecodeError) as e:
        # Never overwrite a file we cannot parse.
        logger.error(f"  Not touching {path}: {e}")
        return False

    rules = list(data.get("permissions") or [])
    rules += [r for r in OPENCODE_SKILLS_RULES if r not in rules]
    data["permissions"] = rules

    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    tmp = path.with_name(path.name + ".tmp-sync")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    logger.info(f"  Added ~/.skills allow rules to {path}")
    return True


# ─── Project-Level Symlinks ─────────────────────────────────────────────────


def add_project_symlink(project_dir: Path, logger: Logger) -> bool:
    """Add a project-level .skills symlink."""
    project_skills = project_dir / ".skills"

    if is_symlink(project_skills) and get_symlink_target(project_skills) == SKILLS_DIR.resolve():
        logger.info(f"Project link already exists: {project_skills}")
        return True

    if project_skills.exists() and not is_symlink(project_skills):
        logger.error(f"Project .skills contains local files; preserved: {project_skills}")
        return False

    success = create_symlink(project_skills, SKILLS_DIR)
    if success:
        logger.info(f"Created project symlink: {project_skills} → {SKILLS_DIR}")
        gitignore = project_dir / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".skills" not in content:
                with open(gitignore, "a") as f:
                    f.write("\n# Skills symlink (managed by sync.py)\n.skills\n")
                logger.info("Added .skills to .gitignore")
        else:
            gitignore.write_text(".skills\n")
            logger.info("Created .gitignore with .skills entry")
    else:
        logger.error("Failed to create project symlink")

    return success


# ─── Main Sync Logic ────────────────────────────────────────────────────────


def full_audit(
    audit_only: bool = False, logger: Optional[Logger] = None
) -> list[AuditResult]:
    """Audit all platforms and optionally repair."""
    if logger is None:
        logger = Logger(verbose=True, log_file=None if audit_only else LOG_FILE)

    results = []

    logger.info("=" * 60)
    logger.info("Universal Skills Sync — Full Audit")
    logger.info(f"OS: {OS_TYPE.value} | Skills: {SKILLS_DIR}")
    logger.info("=" * 60)

    for platform_key, config in PLATFORMS.items():
        logger.info(f"\n--- {config.name} ---")

        symlink_result = audit_symlink(platform_key, config, logger)
        permission_result = audit_permissions(config, logger)

        combined = AuditResult(
            platform_key=platform_key,
            platform_name=config.name,
            symlink_status=symlink_result.symlink_status,
            symlink_details=symlink_result.symlink_details,
            permission_status=permission_result.permission_status,
            permission_details=permission_result.permission_details,
        )

        if not audit_only and symlink_result.symlink_status != Status.NOT_INSTALLED:
            if symlink_result.symlink_status != Status.SYNCED:
                try:
                    repaired = repair_symlink(config, logger)
                except (OSError, ValueError) as exc:
                    logger.error(f"{config.name}: {exc}")
                    repaired = False
                combined.repaired = repaired
                if repaired:
                    checked = audit_symlink(platform_key, config, logger)
                    combined.symlink_status = checked.symlink_status
                    combined.symlink_details = checked.symlink_details

            if permission_result.permission_status in (
                Status.PERMISSION_MISSING,
                Status.PERMISSION_BROKEN,
            ):
                if config.permission_type == "external_directory":
                    repaired = repair_permissions(config, logger)
                    if repaired:
                        combined.permission_status = Status.PERMISSION_OK
                        combined.permission_details = "~/.skills allowed (repaired)"

        results.append(combined)

    return results


def print_report(results: list[AuditResult]):
    """Print a formatted status report."""
    if IS_WINDOWS:
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"{'Platform':<20} {'Symlink':<12} {'Permissions':<14} {'Details'}")
    print("-" * 70)

    for r in results:
        symlink_str = r.symlink_status.value
        perm_str = r.permission_status.value if r.permission_status else "N/A"
        details = r.symlink_details or r.permission_details or ""
        print(f"{r.platform_name:<20} {symlink_str:<12} {perm_str:<14} {details}")

    print("=" * 70)

    synced = sum(1 for r in results if r.symlink_status == Status.SYNCED)
    total = len([r for r in results if r.symlink_status != Status.NOT_INSTALLED])
    print(f"\nSummary: {synced}/{total} platforms synced")

    if any(
        r.symlink_status not in (Status.SYNCED, Status.NOT_INSTALLED) for r in results
    ):
        print("Some platforms need attention. Run without --audit to repair.")


# ─── CLI Entry Point ────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Universal Skills Sync System")
    parser.add_argument("--audit", action="store_true", help="Audit only, no repairs")
    parser.add_argument("--project", type=str, help="Add project-level .skills symlink")
    parser.add_argument(
        "--verbose", action="store_true", default=True, help="Verbose output (default)"
    )
    parser.add_argument("--quiet", action="store_true", help="Silent mode")
    args = parser.parse_args()

    verbose = not args.quiet
    logger = Logger(verbose=verbose, log_file=None if args.audit else LOG_FILE)

    external = sorted(
        skill.name for skill in SKILLS_DIR.iterdir()
        if not skill.name.startswith(".") and (skill / "SKILL.md").is_file()
        and not (skill / "SKILL.md").resolve().is_relative_to(SKILLS_DIR.resolve())
    ) if SKILLS_DIR.is_dir() else []
    if external:
        logger.error(
            "External skill definitions in the shared store: " + ", ".join(external)
            + ". Reconcile approved native consumer links, then retire these shared imports; "
            "nothing synced."
        )
        return 1

    if args.project:
        project_dir = Path(args.project).resolve()
        logger.info(f"Adding project symlink for: {project_dir}")
        if args.audit:
            parser.error("--audit cannot be combined with --project")
        return 0 if add_project_symlink(project_dir, logger) else 1

    source_command = [sys.executable, str(Path(__file__).with_name("skill_sources.py"))]
    if args.audit:
        source_command.append("--audit")
    source_result = subprocess.run(source_command)
    if source_result.returncode:
        return source_result.returncode

    results = full_audit(audit_only=args.audit, logger=logger)
    print_report(results)
    return int(any(
        result.symlink_status in (Status.BROKEN, Status.WRONG_TARGET, Status.MISSING) or
        (result.symlink_status != Status.NOT_INSTALLED and
         result.permission_status in (Status.PERMISSION_MISSING, Status.PERMISSION_BROKEN))
        for result in results
    ))


if __name__ == "__main__":
    sys.exit(main())
