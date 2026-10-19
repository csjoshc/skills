"""Materialize pinned third-party skills before harness discovery."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True, timeout=180
    )
    if result.returncode:
        raise RuntimeError(f"Git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def read_sources(master):
    manifest = master / "sync/skill-sources.json"
    if not manifest.exists():
        return []
    entries = json.loads(manifest.read_text())
    if not isinstance(entries, list):
        raise ValueError("Skill sources must be a list")
    names = set()
    for entry in entries:
        name, repository, commit, path = (entry[key] for key in ("name", "repository", "commit", "path"))
        if not isinstance(name, str) or not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name):
            raise ValueError("Invalid skill name")
        if name in names:
            raise ValueError(f"Duplicate skill source: {name}")
        names.add(name)
        if not isinstance(repository, str) or not repository or repository.startswith("-"):
            raise ValueError(f"{name}: invalid repository")
        if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
            raise ValueError(f"{name}: commit must be a full lowercase Git SHA")
        if not isinstance(path, str) or not path or PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts or "\\" in path:
            raise ValueError(f"{name}: package path must stay inside the repository")
    return entries


def checkout_pin(clone, entry):
    pin = entry["commit"]
    probe = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", f"{pin}^{{commit}}"], capture_output=True)
    if probe.returncode:
        git(clone, "fetch", "--depth", "1", "origin", pin)
    git(clone, "cat-file", "-e", f"{pin}:{entry['path']}/SKILL.md")
    git(clone, "checkout", "--detach", pin)


def sync_sources(master, audit=False):
    master = Path(master)
    entries = read_sources(master)
    vendor = master / ".vendor"
    if vendor.is_symlink():
        raise RuntimeError("Refusing symlinked .vendor directory")
    for entry in entries:
        name, pin = entry["name"], entry["commit"]
        clone = vendor / name
        link = master / name
        package = clone / entry["path"]
        if link.is_symlink():
            if link.resolve() != package.resolve():
                raise RuntimeError(f"{name}: existing link targets another location")
        elif link.exists():
            raise RuntimeError(f"{name}: refusing to replace existing skill directory")
        if clone.is_symlink():
            raise RuntimeError(f"{name}: refusing symlinked source checkout")
        if clone.exists():
            # A nested path can otherwise silently use the parent skills repository.
            if not (clone / ".git").is_dir():
                raise RuntimeError(f"{name}: existing checkout is not an independent clone")
            if git(clone, "remote", "get-url", "origin") != entry["repository"]:
                raise RuntimeError(f"{name}: origin differs from manifest")
            if git(clone, "status", "--porcelain", "--untracked-files=all"):
                raise RuntimeError(f"{name}: local changes; refusing to change checkout")
            current = git(clone, "rev-parse", "HEAD")
            if audit and current != pin:
                raise RuntimeError(f"{name}: revision {current} differs from pin {pin}")
            if not audit and current != pin:
                branch = subprocess.run(["git", "-C", str(clone), "symbolic-ref", "-q", "HEAD"], capture_output=True)
                if branch.returncode == 0:
                    raise RuntimeError(f"{name}: attached branch; refusing to abandon local commits")
                checkout_pin(clone, entry)
        else:
            if audit:
                raise RuntimeError(f"{name}: source checkout missing")
            vendor.mkdir(parents=True, exist_ok=True)
            # Publish only a complete checkout, leaving no half-install after a failed fetch.
            with tempfile.TemporaryDirectory(prefix=f".{name}-", dir=vendor) as staging:
                staged_clone = Path(staging) / "repo"
                git(master, "clone", "--no-checkout", "--depth", "1", "--filter=blob:none", "--no-tags", "--", entry["repository"], str(staged_clone))
                checkout_pin(staged_clone, entry)
                staged_package = staged_clone / entry["path"]
                if not staged_package.resolve().is_relative_to(staged_clone.resolve()) or not (staged_package / "SKILL.md").is_file():
                    raise RuntimeError(f"{name}: package missing or escapes checkout")
                staged_clone.rename(clone)
        if not package.resolve().is_relative_to(clone.resolve()) or not (package / "SKILL.md").is_file():
            raise RuntimeError(f"{name}: package missing or escapes checkout")
        if not link.is_symlink():
            if audit:
                raise RuntimeError(f"{name}: skill link missing")
            os.symlink(Path(".vendor") / name / entry["path"], link, target_is_directory=True)
        print(f"[OK] Source {name}: {pin} -> {link}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=Path.home() / ".skills")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    try:
        sync_sources(args.master, audit=args.audit)
    except (RuntimeError, ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"[ERROR] Skill sources: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
