#!/usr/bin/env python3
"""Update the five GND review harnesses without changing install source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NATIVE_KIMI_INSTALLER = "https://code.kimi.com/kimi-code/install.sh"
NATIVE_KIMI_LATEST = "https://code.kimi.com/kimi-code/latest"
MAX_DOWNLOAD_BYTES = 1024 * 1024

# Digest of the reviewed Kimi installer. `None` means "no digest has been reviewed
# yet", and the native install path REFUSES TO EXECUTE in that state.
#
# Why fail-closed rather than trust-on-first-use: `_install_native_kimi` pipes these
# bytes into `bash`, so whatever this URL serves runs with the maintainer's full
# privileges. Transport hardening in `_https_bytes` (https-only, host-confined,
# size-capped) proves *where* the bytes came from, never *what they are* -- a
# compromised or merely changed upstream serves different code over the same good
# TLS. Recording whatever the first fetch happened to return would launder that
# unknown into a constant that looks audited; it would be trust-on-first-use wearing
# a pin's clothes.
#
# This is also the one network egress under `src/gnd/` that the repository's
# no-network gates cannot see: it leaves via `subprocess` -> `curl`, so the
# banned-import test finds no banned import and the in-process socket patch in
# `test_a_panel_run_attempts_no_outbound_connection` has no subprocess to observe.
# That is exactly the blind spot `test_review_modules_import_no_network_client`'s
# docstring names. With no in-band gate to catch a regression here, the guard has to
# be the refusal below.
#
# To pin: run with `--check`, read the `native_kimi_installer` block it prints, review
# the script at that digest, then set this constant (or pass `--installer-sha256`
# for a single reviewed run). Upstream publishing a new installer SHOULD break this
# and require a fresh review -- that is the feature, not a defect.
NATIVE_KIMI_INSTALLER_SHA256: str | None = (
    "270a86f2d2304529b6d8a3783fca9534874ebaeecb6cfcc1aebcdb6ce20ae1d7"
)
KIMI_DOWNLOAD_HOSTS = frozenset({"code.kimi.com", "cdn.kimi.com"})
QWEN_OPENROUTER_MODEL = "qwen/qwen3.8-max"
QWEN_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
QWEN_OPENROUTER_ENV_KEY = "OPENROUTER_API_KEY"
MAX_QWEN_SETTINGS_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Harness:
    reviewer: str
    command: str
    npm_package: str


HARNESSES: tuple[Harness, ...] = (
    Harness("claude", "claude", "@anthropic-ai/claude-code"),
    Harness("codex", "codex", "@openai/codex"),
    Harness("qwen", "qwen", "@qwen-code/qwen-code"),
    Harness("gemini", "gemini", "@google/gemini-cli"),
    Harness("kimi", "kimi", "@moonshot-ai/kimi-code"),
)


class UpdateError(RuntimeError):
    """A fail-closed preflight, update, or verification failure."""


def _run(
    argv: Sequence[str],
    *,
    timeout: float,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            tuple(argv),
            input=input_bytes,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise UpdateError(f"could not run {argv[0]!r}: {error}") from error
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise UpdateError(
            f"{' '.join(argv)} exited {result.returncode}"
            + (f": {stderr}" if stderr else "")
        )
    return result


def _text(argv: Sequence[str], *, timeout: float = 30.0) -> str:
    try:
        return _run(argv, timeout=timeout).stdout.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as error:
        raise UpdateError(f"{argv[0]!r} returned non-UTF-8 output") from error


def _npm_inventory(npm: str) -> dict[str, str]:
    raw = _text((npm, "ls", "-g", "--depth=0", "--json"))
    try:
        document = json.loads(raw)
        dependencies = document.get("dependencies", {})
    except (json.JSONDecodeError, AttributeError) as error:
        raise UpdateError("npm global inventory was not a JSON object") from error
    inventory: dict[str, str] = {}
    for name, entry in dependencies.items():
        if (
            isinstance(name, str)
            and isinstance(entry, dict)
            and isinstance(entry.get("version"), str)
        ):
            inventory[name] = entry["version"]
    return inventory


def _npm_latest(npm: str, package: str) -> str:
    raw = _text((npm, "view", package, "version", "--json"))
    try:
        version = json.loads(raw)
    except json.JSONDecodeError as error:
        raise UpdateError(f"npm returned invalid JSON for {package}") from error
    if not isinstance(version, str) or not re.fullmatch(r"[0-9A-Za-z.+-]+", version):
        raise UpdateError(f"npm returned an invalid latest version for {package}: {version!r}")
    return version


def _qwen_settings_path() -> Path:
    return Path.home() / ".qwen" / "settings.json"


def _load_qwen_settings(path: Path) -> dict[str, Any]:
    try:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise UpdateError(f"Qwen settings must be a regular non-symlink file: {path}")
        if info.st_size > MAX_QWEN_SETTINGS_BYTES:
            raise UpdateError(f"Qwen settings exceed the {MAX_QWEN_SETTINGS_BYTES}-byte cap")
        document = json.loads(path.read_bytes())
    except UpdateError:
        raise
    except (OSError, json.JSONDecodeError) as error:
        raise UpdateError(f"could not read Qwen settings at {path}: {error}") from error
    if not isinstance(document, dict):
        raise UpdateError(f"Qwen settings are not a JSON object: {path}")
    return document


def _qwen_openrouter_status(path: Path | None = None) -> dict[str, Any]:
    settings_path = _qwen_settings_path() if path is None else path
    document = _load_qwen_settings(settings_path)
    providers = document.get("modelProviders")
    openai_models = providers.get("openai") if isinstance(providers, dict) else None
    if not isinstance(openai_models, list):
        raise UpdateError("Qwen settings do not define modelProviders.openai as a list")
    matches = [
        entry
        for entry in openai_models
        if isinstance(entry, dict) and entry.get("id") == QWEN_OPENROUTER_MODEL
    ]
    if len(matches) != 1:
        raise UpdateError(
            f"Qwen requires exactly one {QWEN_OPENROUTER_MODEL!r} provider entry; "
            f"found {len(matches)}"
        )
    route = matches[0]
    base_url = route.get("baseUrl")
    env_key = route.get("envKey")
    if base_url != QWEN_OPENROUTER_BASE_URL or env_key != QWEN_OPENROUTER_ENV_KEY:
        raise UpdateError(
            f"Qwen model {QWEN_OPENROUTER_MODEL!r} must use "
            f"{QWEN_OPENROUTER_BASE_URL} and {QWEN_OPENROUTER_ENV_KEY}"
        )
    selected = document.get("model")
    active = (
        isinstance(selected, dict)
        and selected.get("name") == QWEN_OPENROUTER_MODEL
        and selected.get("baseUrl") == QWEN_OPENROUTER_BASE_URL
    )
    return {
        "active": active,
        "base_url": base_url,
        "env_key": env_key,
        "model": QWEN_OPENROUTER_MODEL,
        "provider": "openrouter",
        "settings_path": str(settings_path),
    }


def _select_qwen_openrouter(path: Path | None = None) -> bool:
    settings_path = _qwen_settings_path() if path is None else path
    status = _qwen_openrouter_status(settings_path)
    if status["active"] is True:
        return False
    document = _load_qwen_settings(settings_path)
    model = document.get("model")
    if not isinstance(model, dict):
        model = {}
        document["model"] = model
    model["name"] = QWEN_OPENROUTER_MODEL
    model["baseUrl"] = QWEN_OPENROUTER_BASE_URL
    try:
        original_mode = stat.S_IMODE(settings_path.stat().st_mode)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=settings_path.parent,
            prefix=".settings.gnd-",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            os.fchmod(handle.fileno(), original_mode)
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, settings_path)
    except OSError as error:
        if "temporary_path" in locals():
            temporary_path.unlink(missing_ok=True)
        raise UpdateError(f"could not select Qwen's OpenRouter route: {error}") from error
    if _qwen_openrouter_status(settings_path)["active"] is not True:
        raise UpdateError("Qwen's OpenRouter route was not active after settings update")
    return True


def _https_bytes(url: str) -> bytes:
    curl = shutil.which("curl")
    if curl is None:
        raise UpdateError("curl is required to query Kimi's official HTTPS endpoints")
    result = _run(
        (
            curl,
            "-q",
            "--fail",
            "--silent",
            "--show-error",
            "--location",
            "--proto",
            "=https",
            "--proto-redir",
            "=https",
            "--max-time",
            "30",
            "--max-filesize",
            str(MAX_DOWNLOAD_BYTES),
            "--user-agent",
            "gnd-update-review-panel/1",
            "--write-out",
            "%{stderr}%{url_effective}",
            url,
        ),
        timeout=45.0,
    )
    try:
        final_url = result.stderr.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as error:
        raise UpdateError(f"curl returned a non-UTF-8 final URL for {url}") from error
    if not any(
        re.fullmatch(rf"https://{re.escape(host)}(?::443)?(?:/[^\r\n]*)?", final_url)
        for host in KIMI_DOWNLOAD_HOSTS
    ):
        raise UpdateError(f"Kimi endpoint redirected outside its official hosts: {final_url}")
    payload = result.stdout
    if not payload or len(payload) > MAX_DOWNLOAD_BYTES:
        raise UpdateError(f"refused empty or oversized response from {url}")
    return payload


def _native_kimi_latest() -> str:
    try:
        version = _https_bytes(NATIVE_KIMI_LATEST).decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise UpdateError("Kimi latest endpoint returned non-ASCII bytes") from error
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        raise UpdateError(f"Kimi latest endpoint returned an invalid version: {version!r}")
    return version


def _command_version(command: str) -> str:
    return _text((command, "--version"), timeout=15.0)


def _normalized_version(raw: str) -> str | None:
    match = re.search(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", raw)
    return match.group(0) if match else None


def _native_kimi_path(command_path: str) -> bool:
    expected = Path.home() / ".kimi-code" / "bin" / "kimi"
    try:
        return Path(command_path).resolve(strict=True) == expected.resolve(strict=True)
    except (OSError, RuntimeError):
        return False


def _npm_owns_command(npm_root: Path, package: str, command_path: str) -> bool:
    package_root = npm_root.joinpath(*package.split("/"))
    try:
        return Path(command_path).resolve(strict=True).is_relative_to(
            package_root.resolve(strict=True)
        )
    except (OSError, RuntimeError):
        return False


def _snapshot(
    npm: str,
    npm_root: Path,
    inventory: dict[str, str],
) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for harness in HARNESSES:
        path = shutil.which(harness.command)
        if path is None:
            snapshot[harness.reviewer] = {
                "command": harness.command,
                "source": "missing",
                "error": "command not found on PATH",
            }
            continue
        npm_version = inventory.get(harness.npm_package)
        if npm_version is not None and _npm_owns_command(npm_root, harness.npm_package, path):
            source = "npm"
            installed = npm_version
            latest = _npm_latest(npm, harness.npm_package)
        elif harness.reviewer == "kimi" and _native_kimi_path(path):
            source = "native"
            installed = _normalized_version(_command_version(path))
            latest = _native_kimi_latest()
        else:
            snapshot[harness.reviewer] = {
                "command": harness.command,
                "path": path,
                "source": "unsupported",
                "error": "resolved executable is not owned by a supported install source",
            }
            continue
        command_version = _command_version(path)
        entry = {
            "command": harness.command,
            "path": path,
            "source": source,
            "installed": installed,
            "command_version": command_version,
            "latest": latest,
            "current": installed == latest and _normalized_version(command_version) == latest,
        }
        if harness.reviewer == "qwen":
            route = _qwen_openrouter_status()
            entry["openrouter_route"] = route
            entry["current"] = entry["current"] and route["active"] is True
        snapshot[harness.reviewer] = entry
    return snapshot


def _assert_supported(snapshot: dict[str, dict[str, Any]]) -> None:
    refused = {
        reviewer: entry.get("error", entry.get("source", "unknown"))
        for reviewer, entry in snapshot.items()
        if entry.get("source") not in {"npm", "native"}
    }
    if refused:
        detail = "; ".join(f"{name}: {reason}" for name, reason in sorted(refused.items()))
        raise UpdateError(f"preflight refused before making changes: {detail}")


def _apply(
    npm: str,
    before: dict[str, dict[str, Any]],
    *,
    expected_installer_sha256: str | None = None,
) -> None:
    npm_packages = [
        f"{harness.npm_package}@latest"
        for harness in HARNESSES
        if before[harness.reviewer]["source"] == "npm"
    ]
    # Verify the installer digest BEFORE any mutation, so a refusal genuinely leaves the
    # machine untouched -- the same "preflight refused before making changes" contract
    # `_assert_supported` already holds. Verifying after `npm install -g` would make
    # partial application the guaranteed outcome of every run on a native-Kimi machine
    # (four harnesses upgraded, Kimi stale, Qwen route unselected) while the refusal
    # claimed nothing had changed. The bytes verified here are the bytes executed below;
    # they are never re-fetched, so there is no check/use gap.
    installer: bytes | None = None
    if before["kimi"]["source"] == "native":
        installer = _verified_native_kimi_installer(expected_sha256=expected_installer_sha256)

    if npm_packages:
        result = _run((npm, "install", "-g", *npm_packages), timeout=600.0)
        if result.stdout:
            print(result.stdout.decode("utf-8", errors="replace").rstrip(), file=sys.stderr)
        if result.stderr:
            print(result.stderr.decode("utf-8", errors="replace").rstrip(), file=sys.stderr)
    if installer is not None:
        _run_native_kimi_installer(installer)
    _select_qwen_openrouter()


def _normalized_sha256(value: str, *, source: str) -> str:
    """Accept a 64-hex-character digest in any case; reject anything else."""
    candidate = value.strip().lower()
    if len(candidate) != 64 or any(character not in "0123456789abcdef" for character in candidate):
        raise UpdateError(
            f"{source} must be a 64-character hex sha256 digest, got {value.strip()!r}"
        )
    return candidate


def _verified_native_kimi_installer(*, expected_sha256: str | None) -> bytes:
    """Fetch Kimi's official installer, returning its bytes ONLY at a reviewed digest.

    The refusal is the security control. `_https_bytes` already proves the bytes came
    from an official host over https, but transport provenance is not content
    integrity: the same host can serve different code tomorrow, and these bytes are
    handed to `bash`. This function never executes anything -- it either returns
    verified bytes or raises, so there is no code path from "digest unknown" to
    "installer executed".
    """
    installer = _https_bytes(NATIVE_KIMI_INSTALLER)
    observed = hashlib.sha256(installer).hexdigest()

    # `is not None`, not `or`: an explicitly supplied but empty/malformed digest is a
    # format error to report, not an absent pin to fall back from. Both still refuse,
    # but conflating them would hand the caller the wrong diagnosis.
    pinned = expected_sha256 if expected_sha256 is not None else NATIVE_KIMI_INSTALLER_SHA256
    if pinned is None:
        raise UpdateError(
            "refusing to execute Kimi's native installer: no reviewed sha256 is pinned. "
            f"Fetched {len(installer)} bytes from {NATIVE_KIMI_INSTALLER} with sha256 "
            f"{observed}. Review that script, then set NATIVE_KIMI_INSTALLER_SHA256 in "
            "update_harnesses.py or re-run with --installer-sha256 <digest>. This check "
            "runs before any harness is touched, so nothing was executed or modified."
        )
    pinned = _normalized_sha256(pinned, source="pinned installer digest")
    if observed != pinned:
        raise UpdateError(
            "refusing to execute Kimi's native installer: digest mismatch. "
            f"expected {pinned}, observed {observed}. Upstream published a different "
            "installer than the one that was reviewed; re-review it and update the pin. "
            "This check runs before any harness is touched, so nothing was executed or "
            "modified."
        )
    return installer


def _run_native_kimi_installer(installer: bytes) -> None:
    """Execute already-verified installer bytes. Callers MUST verify first."""
    bash = shutil.which("bash")
    if bash is None:
        raise UpdateError("bash is required by Kimi's official native installer")
    result = _run((bash,), timeout=600.0, input_bytes=installer)
    if result.stdout:
        print(result.stdout.decode("utf-8", errors="replace").rstrip(), file=sys.stderr)
    if result.stderr:
        print(result.stderr.decode("utf-8", errors="replace").rstrip(), file=sys.stderr)


def _install_native_kimi(*, expected_sha256: str | None) -> None:
    """Verify then execute — the single-shot composition of the two halves above."""
    _run_native_kimi_installer(_verified_native_kimi_installer(expected_sha256=expected_sha256))


def _installer_pin_status() -> dict[str, Any]:
    """Report the installer's current digest against the pin, WITHOUT executing it.

    This is the review surface for the pin: `--check` fetches and hashes, never runs.
    It is what a maintainer reads before deciding to set NATIVE_KIMI_INSTALLER_SHA256.
    """
    try:
        installer = _https_bytes(NATIVE_KIMI_INSTALLER)
    except UpdateError as error:
        return {"url": NATIVE_KIMI_INSTALLER, "error": str(error)}
    observed = hashlib.sha256(installer).hexdigest()
    pinned = NATIVE_KIMI_INSTALLER_SHA256
    return {
        "url": NATIVE_KIMI_INSTALLER,
        "bytes": len(installer),
        "observed_sha256": observed,
        "pinned_sha256": pinned,
        "pinned": pinned is not None,
        "matches_pin": pinned is not None and observed == _normalized_sha256(pinned, source="pin"),
        "apply_would_execute": pinned is not None
        and observed == _normalized_sha256(pinned, source="pin"),
    }


def _report(mode: str, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": mode,
        "before": before,
        "after": after,
        "all_current": all(entry.get("current") is True for entry in after.values()),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="inspect sources and latest versions")
    action.add_argument("--apply", action="store_true", help="update, then verify all five harnesses")
    parser.add_argument(
        "--installer-sha256",
        metavar="HEX",
        default=None,
        help=(
            "sha256 of the reviewed Kimi native installer, for a single run. Without "
            "this (and with NATIVE_KIMI_INSTALLER_SHA256 unset) the native install path "
            "refuses to execute. Run --check to see the current digest."
        ),
    )
    args = parser.parse_args(argv)

    expected_installer_sha256: str | None = None
    if args.installer_sha256 is not None:
        try:
            expected_installer_sha256 = _normalized_sha256(
                args.installer_sha256, source="--installer-sha256"
            )
        except UpdateError as error:
            print(json.dumps({"schema_version": 1, "error": str(error)}, sort_keys=True))
            return 1

    npm = shutil.which("npm")
    if npm is None:
        print(json.dumps({"schema_version": 1, "error": "npm not found on PATH"}, sort_keys=True))
        return 1
    try:
        npm_root = Path(_text((npm, "root", "-g"))).resolve(strict=True)
        before = _snapshot(npm, npm_root, _npm_inventory(npm))
        _assert_supported(before)
        if args.apply:
            _apply(npm, before, expected_installer_sha256=expected_installer_sha256)
            after = _snapshot(npm, npm_root, _npm_inventory(npm))
            _assert_supported(after)
            if not all(entry.get("current") is True for entry in after.values()):
                raise UpdateError("post-update verification found a harness below its latest release")
            report = _report("apply", before, after)
        else:
            report = _report("check", before, before)
            if before["kimi"]["source"] == "native":
                report["native_kimi_installer"] = _installer_pin_status()
    except UpdateError as error:
        print(json.dumps({"schema_version": 1, "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
