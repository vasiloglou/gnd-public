"""Explicit isolated compiler work; elaboration never discharges obligations."""

import os
import re
import shutil
import stat
import tempfile
import time
from pathlib import Path

from gnd import artifacts

from .lean_io import verify_lean_bundle
from .lean_types import DEFAULT_LIMITS, checked_limits, refused
from .souffle import digest
from .souffle_io import read_file
from .souffle_runtime import NativeFailure, command


def compile_lean(bundle_path, *, executable="lake", elaborate_stubs=False, limits=DEFAULT_LIMITS):
    result = refused()
    records = {
        name: {
            "attempted": False,
            "native_exit": None,
            "status": "not-attempted",
            "elapsed_seconds": 0,
        }
        for name in ["definitions", "stubs"]
    }
    tool = {"version": None, "raw_sha256": None}
    try:
        checked_limits(limits)
        result = verify_lean_bundle(bundle_path, limits=limits)
        if result.exit_code:
            result.native = {"tool": tool, **records}
            return result
        path = shutil.which(str(executable))
        if path is None:
            raise NativeFailure("tool-error" if Path(executable).exists() else "tool-absent")
        path = Path(path).resolve()
        if path.stat().st_mode & (stat.S_ISUID | stat.S_ISGID):
            raise NativeFailure("tool-error")
        start = time.monotonic()
        deadline = start + limits.native_seconds
        raw = read_file(path, DEFAULT_LIMITS.document_bytes)
        tool["raw_sha256"] = digest(raw)
        with tempfile.TemporaryDirectory(prefix="gnd-lean-") as directory:
            root = Path(directory)
            bundle = root / "bundle"
            bundle.mkdir()
            compiled = root / "compiled"
            compiled.mkdir()
            # Only module bytes and the exact release pin enter the compiler cwd.
            for name in ["Definitions.lean", "ProofObligations.lean", "lean-toolchain"]:
                (bundle / name).write_bytes(result.files[name])
            env = {**os.environ, "LEAN_PATH": os.pathsep.join([str(compiled), str(bundle)])}
            prior = 0

            def run(argv):
                nonlocal prior
                if read_file(path, DEFAULT_LIMITS.document_bytes) != raw:
                    raise NativeFailure("tool-error")
                code, out, err = command(
                    argv,
                    root,
                    deadline,
                    limits.native_output_bytes,
                    prior=prior,
                    cwd=bundle,
                    env=env,
                    output=root,
                    output_baseline={
                        "bundle/" + name: len(result.files[name])
                        for name in ["Definitions.lean", "ProofObligations.lean", "lean-toolchain"]
                    },
                )
                prior += len(out) + len(err)
                if any(
                    (bundle / name).read_bytes() != result.files[name]
                    for name in ["Definitions.lean", "ProofObligations.lean", "lean-toolchain"]
                ):
                    raise NativeFailure("tool-error")
                if read_file(path, DEFAULT_LIMITS.document_bytes) != raw:
                    raise NativeFailure("tool-error")
                return code, out, err

            code, out, err = run([str(path), "--version"])
            expected = result.files["lean-toolchain"].decode().strip().split(":v")[1]
            text = (out + err).decode("utf-8")
            # Lake has a separate version in official Lean releases.
            marker = "Lean version " if "Lean version " in text else "Lake version "
            if code or not re.search(
                re.escape(marker) + re.escape(expected) + r"(?:[\s)]|$)", text
            ):
                raise NativeFailure("tool-version-unsupported")
            tool["version"] = expected
            for name, filename in [
                ("definitions", "Definitions.lean"),
                ("stubs", "ProofObligations.lean"),
            ]:
                if name == "stubs" and not elaborate_stubs:
                    continue
                record = records[name]
                record["attempted"] = True
                began = time.monotonic()
                argv = (
                    [str(path), "env", "lean"]
                    + (["-o", str(compiled / "Definitions.olean")] if name == "definitions" else [])
                    + [filename]
                )
                try:
                    code, _, _ = run(argv)
                    record.update(native_exit=code, status="completed" if code == 0 else "failed")
                    if code:
                        raise NativeFailure("tool-error")
                except NativeFailure as e:
                    if record["status"] != "failed":
                        record["status"] = "timeout" if e.reason == "tool-timeout" else "refused"
                    raise
                finally:
                    record["elapsed_seconds"] = time.monotonic() - began
        result.status = "compiled"
    except NativeFailure as e:
        result = refused(
            4,
            e.reason
            if e.reason
            in {
                "tool-absent",
                "tool-version-unsupported",
                "tool-timeout",
                "tool-error",
                "output-limit",
            }
            else "tool-error",
        )
    except (artifacts.ArtifactError, ValueError, OSError, UnicodeError):
        result = refused(4, "tool-error")
    result.native = dict(tool=tool, **records)
    return result
