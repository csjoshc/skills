"""Directory links shared by the installer and harness sync, using only the stdlib."""
import os
from pathlib import Path
import subprocess
import uuid


def is_link(path):
    path = Path(path)
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def remove_link(path):
    """Remove the link itself, never descend into its target."""
    path = Path(path)
    if not is_link(path):
        raise ValueError(f"Refusing to remove a real directory or file: {path}")
    if path.is_symlink():
        path.unlink()
    else:
        path.rmdir()


def create_link(link, target):
    """Stage a replacement before removing an old link; preserve physical entries."""
    link, target = Path(link), Path(target).absolute()
    if link.exists() and not is_link(link):
        raise FileExistsError(f"Local entry preserved: {link}")
    link.parent.mkdir(parents=True, exist_ok=True)
    staged = link.with_name(f".{link.name}.sync-{uuid.uuid4().hex}")
    try:
        try:
            os.symlink(target, staged, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt" or getattr(exc, "winerror", None) != 1314:
                raise
            # Junctions work without Developer Mode/admin on local Windows volumes.
            # Always quote both paths; refuse cmd expansion and quote characters.
            if any(c in str(p) for p in (staged, target) for c in '\"%\r\n'):
                raise ValueError("Junction paths contain unsupported cmd characters") from exc
            result = subprocess.run(
                f'cmd.exe /d /v:off /c mklink /J "{staged}" "{target}"',
                capture_output=True,
            )
            if result.returncode:
                raise OSError("Cannot create directory junction; use a local Windows volume") from exc
        if is_link(link):
            remove_link(link)
        staged.rename(link)
    finally:
        if is_link(staged):
            remove_link(staged)
