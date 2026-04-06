#!/usr/bin/env python3
"""
Universal Skills Sync System
Cross-platform symlink audit, repair, and permission management.

Usage:
    python sync.py              # Full audit + repair (verbose)
    python sync.py --audit      # Audit only, no changes
    python sync.py --project    # Add project-level .skills symlink
    python sync.py --hook       # Silent mode for git hooks
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
LOG_FILE = SKILLS_DIR / "sync.log"


def resolve_path(path_str: str) -> Path:
    """Resolve a path string with ~ expansion."""
    return Path(path_str).expanduser()


def windows_path(path: Path) -> str:
    """Convert a Path to Windows-style for mklink."""
    return str(path).replace("/", "\\")


# ─── Platform Definitions ───────────────────────────────────────────────────


@dataclass
class PlatformConfig:
    name: str
    skills_symlink: Path
    permission_type: str  # "external_directory", "filesystem", "policy", "include_directories", "trust"
    config_path: Optional[Path] = None
    config_parser: Optional[str] = None  # "json", "toml"
    template_name: Optional[str] = None
    platform_key: str = ""  # Set during PLATFORMS construction


PLATFORMS = {
    "opencode": PlatformConfig(
        name="OpenCode",
        skills_symlink=HOME / ".config" / "opencode" / "skills",
        permission_type="external_directory",
        config_path=HOME / ".config" / "opencode" / "opencode.json",
        config_parser="json",
        template_name="opencode.json",
        platform_key="opencode",
    ),
    "codex": PlatformConfig(
        name="Codex",
        skills_symlink=HOME / ".codex" / "skills",
        permission_type="filesystem",
        config_path=HOME / ".codex" / "config.toml",
        config_parser="toml",
        template_name="codex-permissions.toml",
        platform_key="codex",
    ),
    "gemini": PlatformConfig(
        name="Gemini/Antigravity",
        skills_symlink=HOME / ".gemini" / "antigravity" / "skills",
        permission_type="policy",
        config_path=HOME / ".gemini" / "policies" / "skills.toml",
        template_name="gemini-policy.toml",
        platform_key="gemini",
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
    "qwen": PlatformConfig(
        name="Qwen",
        skills_symlink=HOME / ".qwen" / "skills",
        permission_type="include_directories",
        config_path=HOME / ".qwen" / "settings.json",
        config_parser="json",
        template_name="qwen-settings.json",
        platform_key="qwen",
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
    return path.is_symlink()


def get_symlink_target(path: Path) -> Optional[Path]:
    if is_symlink(path):
        return path.resolve()
    return None


def create_symlink(link_path: Path, target: Path) -> bool:
    """Create a symlink using OS-appropriate method."""
    if link_path.is_symlink():
        link_path.unlink()
    elif link_path.exists():
        if link_path.is_dir():
            shutil.rmtree(link_path, ignore_errors=True)
        else:
            link_path.unlink()

    link_path.parent.mkdir(parents=True, exist_ok=True)

    if IS_WINDOWS:
        try:
            result = subprocess.run(
                [
                    "cmd",
                    "//c",
                    "mklink",
                    "/D",
                    windows_path(link_path),
                    windows_path(target),
                ],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"mklink failed: {e.stderr.decode()}")
            return False
    else:
        try:
            os.symlink(target, link_path)
            return True
        except OSError as e:
            print(f"symlink failed: {e}")
            return False


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

    if not symlink_path.parent.exists():
        result.symlink_status = Status.NOT_INSTALLED
        result.symlink_details = (
            f"Parent directory {symlink_path.parent} does not exist"
        )
        logger.info(f"{config.name}: Not installed (parent dir missing)")
        return result

    if not symlink_path.exists() and not symlink_path.is_symlink():
        result.symlink_status = Status.MISSING
        result.symlink_details = "Symlink does not exist"
        logger.warn(f"{config.name}: Skills symlink missing")
        return result

    if not is_symlink(symlink_path):
        result.symlink_status = Status.BROKEN
        result.symlink_details = "Exists as real directory, not symlink"
        logger.warn(f"{config.name}: Skills path is a real directory, not a symlink")
        return result

    target = get_symlink_target(symlink_path)
    if target != SKILLS_DIR:
        result.symlink_status = Status.WRONG_TARGET
        result.symlink_details = f"Points to {target}, expected {SKILLS_DIR}"
        logger.warn(f"{config.name}: Symlink points to {target}, expected {SKILLS_DIR}")
        return result

    result.symlink_status = Status.SYNCED
    result.symlink_details = f"→ {SKILLS_DIR}"
    logger.info(f"{config.name}: Skills symlink OK")
    return result


def repair_symlink(config: PlatformConfig, logger: Logger) -> bool:
    """Repair a broken skills symlink."""
    logger.info(f"Repairing {config.name} skills symlink...")
    success = create_symlink(config.skills_symlink, SKILLS_DIR)
    if success:
        logger.info(f"  Created: {config.skills_symlink} → {SKILLS_DIR}")
    else:
        logger.error(f"  Failed to create symlink for {config.name}")
    return success


# ─── Permission Config Audit ────────────────────────────────────────────────


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

    if not config.config_path:
        result.permission_status = Status.PERMISSION_MISSING
        result.permission_details = "No config path defined"
        return result

    if not config.config_path.exists():
        result.permission_status = Status.PERMISSION_MISSING
        result.permission_details = f"Config file missing: {config.config_path}"
        logger.warn(f"{config.name}: Permission config missing")
        return result

    try:
        content = config.config_path.read_text()

        if config.config_parser == "json":
            data = json.loads(content)
            if config.platform_key == "opencode":
                perm = data.get("permission", {}).get("external_directory", {})
                if any(".skills" in k for k in perm):
                    result.permission_status = Status.PERMISSION_OK
                    result.permission_details = "external_directory configured"
                else:
                    result.permission_status = Status.PERMISSION_MISSING
                    result.permission_details = "No external_directory for .skills"
            elif config.platform_key == "qwen":
                include_dirs = data.get("context", {}).get("includeDirectories", [])
                if any(".skills" in str(d) for d in include_dirs):
                    result.permission_status = Status.PERMISSION_OK
                    result.permission_details = "includeDirectories configured"
                else:
                    result.permission_status = Status.PERMISSION_MISSING
                    result.permission_details = "No includeDirectories for .skills"
        elif config.config_parser == "toml":
            if ".skills" in content:
                result.permission_status = Status.PERMISSION_OK
                result.permission_details = "filesystem permission configured"
            else:
                result.permission_status = Status.PERMISSION_MISSING
                result.permission_details = "No .skills permission in config"
        elif config.permission_type == "policy":
            if ".skills" in content:
                result.permission_status = Status.PERMISSION_OK
                result.permission_details = "policy rules configured"
            else:
                result.permission_status = Status.PERMISSION_MISSING
                result.permission_details = "No .skills policy rules"

    except Exception as e:
        result.permission_status = Status.PERMISSION_BROKEN
        result.permission_details = f"Parse error: {e}"
        logger.error(f"{config.name}: Permission config parse error: {e}")

    return result


def repair_permissions(config: PlatformConfig, logger: Logger) -> bool:
    """Repair permission config from template."""
    if not config.template_name:
        logger.warn(f"No template available for {config.name}")
        return False

    template_path = SKILLS_DIR / "configs" / config.template_name
    if not template_path.exists():
        logger.error(f"Template missing: {template_path}")
        return False

    config.config_path.parent.mkdir(parents=True, exist_ok=True)

    template_content = template_path.read_text()

    if config.config_parser == "json" and config.config_path.exists():
        try:
            existing = json.loads(config.config_path.read_text())
            template_data = json.loads(template_content)
            existing.update(template_data)
            config.config_path.write_text(json.dumps(existing, indent=2))
            logger.info(f"  Merged permissions into {config.config_path}")
            return True
        except json.JSONDecodeError:
            config.config_path.write_text(template_content)
            logger.info(f"  Replaced {config.config_path} with template")
            return True
    else:
        config.config_path.write_text(template_content)
        logger.info(f"  Wrote {config.config_path} from template")
        return True


# ─── Project-Level Symlinks ─────────────────────────────────────────────────


def add_project_symlink(project_dir: Path, logger: Logger) -> bool:
    """Add a project-level .skills symlink."""
    project_skills = project_dir / ".skills"

    if project_skills.is_symlink():
        target = get_symlink_target(project_skills)
        if target == SKILLS_DIR:
            logger.info(f"Project symlink already exists: {project_skills}")
            return True
        logger.warn(f"Project symlink points to wrong target: {target}")
        project_skills.unlink()

    if project_skills.exists():
        logger.warn(f"Project .skills exists as real directory, removing...")
        shutil.rmtree(project_skills, ignore_errors=True)

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


# ─── Git Hook Installation ──────────────────────────────────────────────────


def install_git_hook(project_dir: Path, logger: Logger) -> bool:
    """Install the post-checkout hook in a project."""
    hooks_dir = project_dir / ".git" / "hooks"
    if not hooks_dir.exists():
        logger.warn(f"No .git/hooks directory in {project_dir}")
        return False

    hook_path = hooks_dir / "post-checkout"
    template_path = SKILLS_DIR / "hooks" / "post-checkout"

    if not template_path.exists():
        logger.error(f"Hook template missing: {template_path}")
        return False

    shutil.copy2(template_path, hook_path)
    if not IS_WINDOWS:
        hook_path.chmod(0o755)

    logger.info(f"Installed git hook: {hook_path}")
    return True


# ─── Main Sync Logic ────────────────────────────────────────────────────────


def full_audit(
    audit_only: bool = False, logger: Optional[Logger] = None
) -> list[AuditResult]:
    """Audit all platforms and optionally repair."""
    if logger is None:
        logger = Logger(verbose=True, log_file=LOG_FILE)

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

        if not audit_only:
            if symlink_result.symlink_status != Status.SYNCED:
                if symlink_result.symlink_status == Status.NOT_INSTALLED:
                    logger.info(f"  Skipping (not installed)")
                else:
                    repaired = repair_symlink(config, logger)
                    combined.repaired = repaired
                    if repaired:
                        combined.symlink_status = Status.SYNCED
                        combined.symlink_details = f"→ {SKILLS_DIR} (repaired)"

            if permission_result.permission_status in (
                Status.PERMISSION_MISSING,
                Status.PERMISSION_BROKEN,
            ):
                if config.template_name:
                    repaired = repair_permissions(config, logger)
                    if repaired:
                        combined.permission_status = Status.PERMISSION_OK
                        combined.permission_details = "Restored from template"

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
        print("Some platforms need attention. Run with --repair to fix.")


# ─── CLI Entry Point ────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Universal Skills Sync System")
    parser.add_argument("--audit", action="store_true", help="Audit only, no repairs")
    parser.add_argument("--project", type=str, help="Add project-level .skills symlink")
    parser.add_argument(
        "--hook", action="store_true", help="Install git hook in current project"
    )
    parser.add_argument(
        "--hook-dir", type=str, help="Install git hook in specific directory"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=True, help="Verbose output (default)"
    )
    parser.add_argument("--quiet", action="store_true", help="Silent mode (for hooks)")
    args = parser.parse_args()

    verbose = not args.quiet
    logger = Logger(verbose=verbose, log_file=LOG_FILE)

    if args.project:
        project_dir = Path(args.project).resolve()
        logger.info(f"Adding project symlink for: {project_dir}")
        add_project_symlink(project_dir, logger)
        return

    if args.hook or args.hook_dir:
        target = Path(args.hook_dir).resolve() if args.hook_dir else Path.cwd()
        logger.info(f"Installing git hook in: {target}")
        install_git_hook(target, logger)
        return

    results = full_audit(audit_only=args.audit, logger=logger)
    print_report(results)


if __name__ == "__main__":
    main()
