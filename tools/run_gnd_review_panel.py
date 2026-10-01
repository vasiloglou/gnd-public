"""Run the GND review panel with credentials from the trusted Codex env file.

Only the two panel credentials are imported from ``~/.codex/.env``.  The file
is parsed as data, never executed as shell, and repository ``.env`` files are
never consulted.
"""

from __future__ import annotations

import ast
import os
import re
import shutil
import stat
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from pathlib import Path

MAX_CREDENTIAL_FILE_BYTES = 64 * 1024
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_SOURCES = {
    "OPENROUTER_API_KEY": ("OPENROUTER_API_KEY", "QWEN_API_KEY_2"),
    "ZAI_API_KEY": ("ZAI_API_KEY", "Z_API_KEY"),
}


class CredentialError(Exception):
    """The trusted credential file cannot provide a safe, complete mapping."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an Authorization header to a redirected destination.
        return None


def check_openrouter_auth(environment: Mapping[str, str]) -> None:
    """Check the actual credential without buying a model completion or retrying.

    A populated environment variable proves loading, not authentication. Do not
    print response bodies or exception strings: either could contain secrets.
    This checks OpenRouter only; it makes no claim about other reviewer seats.
    """

    key = environment["OPENROUTER_API_KEY"]
    if not key or any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise CredentialError("OPENROUTER_API_KEY contains invalid header characters")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": "Bearer " + key},
    )
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=10) as response:
            if response.status != 200:
                raise CredentialError("OpenRouter authentication check did not return HTTP 200")
    except urllib.error.HTTPError as error:
        code = error.code
        error.close()
        if code in (401, 403):
            raise CredentialError(
                f"OpenRouter rejected OPENROUTER_API_KEY (HTTP {code}); replace its "
                "selected source with a valid OpenRouter key. QWEN_API_KEY_2 is "
                "only a legacy variable alias, not a conversion between providers."
            ) from None
        raise CredentialError(f"OpenRouter authentication check returned HTTP {code}") from None
    except (OSError, ValueError) as error:
        raise CredentialError(
            f"OpenRouter authentication check could not complete ({type(error).__name__})"
        ) from None


def _read_trusted_file(path: Path) -> str:
    """Read one owner-only regular file without following a symlink."""

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise CredentialError(f"trusted credential file is unavailable: {path}") from error
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise CredentialError("trusted credential path is not a regular file")
        if info.st_uid != os.getuid():
            raise CredentialError("trusted credential file is not owned by the current user")
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise CredentialError("trusted credential file must have mode 0600 or stricter")
        if info.st_size > MAX_CREDENTIAL_FILE_BYTES:
            raise CredentialError("trusted credential file exceeds the 64 KiB limit")
        data = os.read(descriptor, MAX_CREDENTIAL_FILE_BYTES + 1)
        if len(data) > MAX_CREDENTIAL_FILE_BYTES:
            raise CredentialError("trusted credential file exceeds the 64 KiB limit")
    finally:
        os.close(descriptor)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CredentialError("trusted credential file is not UTF-8") from error


def _value(raw: str, *, line_number: int) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as error:
            raise CredentialError(
                f"trusted credential line {line_number} has invalid quoting"
            ) from error
        if not isinstance(parsed, str):
            raise CredentialError(f"trusted credential line {line_number} is not a string")
        return parsed
    return value


def _parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, source_line in enumerate(text.splitlines(), start=1):
        line = source_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            raise CredentialError(f"trusted credential line {line_number} is not NAME=VALUE")
        name, raw = line.split("=", 1)
        name = name.strip()
        if _NAME.fullmatch(name) is None:
            raise CredentialError(
                f"trusted credential line {line_number} has an invalid variable name"
            )
        if name in values:
            raise CredentialError(f"trusted credential file repeats {name}")
        values[name] = _value(raw, line_number=line_number)
    return values


def panel_environment(
    parent: Mapping[str, str], *, home: Path | None = None
) -> tuple[dict[str, str], dict[str, str]]:
    """Return the panel environment and non-secret provenance by target name."""

    environment = dict(parent)
    provenance: dict[str, str] = {}
    missing = [name for name in _SOURCES if not environment.get(name)]
    if missing:
        base = Path.home() if home is None else home
        path = base / ".codex" / ".env"
        values = _parse(_read_trusted_file(path))
        for target in missing:
            source = next((name for name in _SOURCES[target] if values.get(name)), None)
            if source is not None:
                environment[target] = values[source]
                provenance[target] = source

    absent = [name for name in _SOURCES if not environment.get(name)]
    if absent:
        raise CredentialError(
            "missing required panel credential names after trusted-file import: "
            + ", ".join(absent)
        )
    for target in _SOURCES:
        provenance.setdefault(target, "parent environment")
    return environment, provenance


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    command = "panel"
    if arguments and arguments[0] == "--light":
        command = "panel-light"
        arguments.pop(0)
    try:
        environment, provenance = panel_environment(os.environ)
    except CredentialError as error:
        print(f"review credential preflight failed: {error}", file=sys.stderr)
        return 78

    print(
        "review credential names loaded (not yet authenticated): "
        + ", ".join(f"{name} from {provenance[name]}" for name in _SOURCES),
        flush=True,
    )
    if arguments == ["--check-credentials"]:
        return 0
    if not arguments:
        print(
            "usage: uv run python tools/run_gnd_review_panel.py "
            "[--light] REQUEST --out DIR [panel options]; "
            "--check-credentials checks names only; --check-auth verifies OpenRouter",
            file=sys.stderr,
        )
        return 64

    try:
        check_openrouter_auth(environment)
    except CredentialError as error:
        print(f"review authentication preflight failed: {error}", file=sys.stderr)
        return 78
    print("OpenRouter authentication preflight passed", flush=True)
    if arguments == ["--check-auth"]:
        return 0

    uv = shutil.which("uv")
    if uv is None:
        print("review panel launcher could not find uv", file=sys.stderr)
        return 69
    os.execve(
        uv,
        [uv, "run", "gnd", "review", command, *arguments],
        environment,
    )
    raise AssertionError("os.execve returned")


if __name__ == "__main__":
    raise SystemExit(main())
