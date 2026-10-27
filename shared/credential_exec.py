"""Exec a consumer with scoped file credentials, never a harness-wide export."""
# Broad exports expose unrelated credentials; per-tool wrappers duplicate security-sensitive logic.
# One tested launcher shares that boundary without taking over each harness's configuration.
import argparse
import base64
import binascii
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
# Credential names are not predictable enough for a denylist of inherited variables.
RUNTIME = frozenset((
    "HOME", "PATH", "TMPDIR", "TMP", "TEMP", "LANG", "LANGUAGE", "LC_ALL",
    "LC_CTYPE", "LC_COLLATE", "LC_MESSAGES", "LC_MONETARY", "LC_NUMERIC", "LC_TIME",
    "TZ", "TERM", "COLORTERM", "NO_COLOR",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS",
))


class Failure(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Argparse diagnostics can echo arguments that contain credentials.
        raise Failure("invalid arguments")


def clean_env():
    return {k: v for k, v in os.environ.items() if k in RUNTIME}


def required_values(path, names, env):
    if not names:
        return {}
    if not path:
        raise Failure("credential file required")
    path = str(Path(path).expanduser())
    try:
        # Validate and source the same open file so a pathname swap cannot bypass the checks.
        # Nonblocking open lets us reject a FIFO without waiting for a writer.
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as source:
            info = os.fstat(source.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077 or not info.st_mode & 0o400):
                raise Failure(f"{path}: private owner-readable file required")
            # Bash invents defaults such as PATH; those must not satisfy a missing file assignment.
            script = (
                "builtin unset -v -- " + " ".join(names) + " 2>/dev/null || exit 1\n"
                f'. /dev/fd/{source.fileno()} >/dev/null 2>&1 || exit 1\n'
                'builtin printf "%s\\0" ' + " ".join('"${' + name + '-}"' for name in names)
            )
            # Trusted files need shell expansion; a clean subprocess contains exports and noise.
            result = subprocess.run(
                ["/bin/bash", "--noprofile", "--norc", "-c", script, "credential-source"],
                check=False,
                env={k: v for k, v in env.items() if k not in names},
                pass_fds=(source.fileno(),), stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, timeout=10,
            )
    except (OSError, subprocess.TimeoutExpired):
        raise Failure(f"{path}: cannot read credential file") from None
    if result.returncode or len(result.stdout.split(b"\0")) != len(names) + 1:
        raise Failure(f"{path}: cannot source credential file")
    values = dict(zip(names, (os.fsdecode(v) for v in result.stdout.split(b"\0")[:-1])))
    for name, value in values.items():
        if not value:
            raise Failure(f"{path}: required variable {name} is empty or missing")
    return values


def descriptor(encoded):
    try:
        data = json.loads(base64.b64decode(encoded, validate=True))
    except (ValueError, binascii.Error):
        raise Failure("invalid descriptor") from None
    if (not isinstance(data, dict) or data.get("version") != 1
            or set(data) - {"version", "file", "vars", "env", "argv", "headers", "path_prepend"}
            or not {"version", "file", "vars", "env", "argv"} <= set(data)):
        raise Failure("invalid descriptor")
    if data["file"] is not None and not isinstance(data["file"], str):
        raise Failure("invalid descriptor file")
    names, command = data["vars"], data["argv"]
    if (not isinstance(names, list) or any(not isinstance(n, str) or not NAME.fullmatch(n) for n in names)
            or not isinstance(command, list) or not command
            or any(not isinstance(v, str) or "\0" in v or REF.search(v) for v in command)):
        raise Failure("invalid descriptor variables or command")
    for field in ("env", "headers"):
        mapping = data.get(field, {})
        if not isinstance(mapping, dict):
            raise Failure("invalid descriptor mapping")
        for k, v in mapping.items():
            if (not isinstance(k, str) or not isinstance(v, str) or "\0" in k + v
                    or (field == "env" and (not k or "=" in k))
                    or not set(REF.findall(v)) <= set(names)):
                raise Failure("invalid descriptor template")
    prefix = data.get("path_prepend", "")
    if not isinstance(prefix, str) or "\0" in prefix or REF.search(prefix):
        raise Failure("invalid descriptor path")
    return data


def run(argv):
    ap = Parser(description=__doc__)
    ap.add_argument("--file")
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--descriptor")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    env = clean_env()
    if args.descriptor:
        if args.file or args.var or args.set or args.command:
            raise Failure("descriptor cannot be combined with other options")
        data = descriptor(args.descriptor)
        values = required_values(data["file"], data["vars"], env)
        env.update(values)
        env.update({k: REF.sub(lambda m: values[m[1]], v) for k, v in data["env"].items()})
        command = list(data["argv"])
        # Bridges resolve these placeholders from their environment; expansion here would expose
        # secret values in process arguments.
        for k, v in data.get("headers", {}).items():
            command += ["--header", f"{k}:{v}"]
        if data.get("path_prepend"):
            env["PATH"] = data["path_prepend"] + os.pathsep + env.get("PATH", os.defpath)
    else:
        names = list(dict.fromkeys(args.var))
        if any(not NAME.fullmatch(n) for n in names):
            raise Failure("invalid variable name")
        settings = {}
        for item in args.set:
            key, sep, value = item.partition("=")
            if not sep or not NAME.fullmatch(key) or key in names or "\0" in value:
                raise Failure("invalid runtime setting")
            settings[key] = value
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            raise Failure("command required")
        env.update(required_values(args.file, names, env))
        env.update(settings)
    # Replacement keeps the consumer's signals and exit status without a supervising wrapper.
    os.execvpe(command[0], command, env)


def main(argv=None):
    try:
        run(argv)
    except (Failure, OSError, ValueError) as exc:
        message = str(exc) if isinstance(exc, Failure) else "cannot execute consumer"
        print(f"credential_exec: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
