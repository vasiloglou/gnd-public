"""Original supervisor transport used exclusively through original mocked unit test."""
from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import time
from pathlib import Path

from test_public_phase5_cache_support import ROOT

LIMIT = 8 * 1024 * 1024

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def neutral(raw: bytes) -> bytes:
    return raw.replace(str(ROOT).encode(), b"<repo>").replace(
        os.path.expanduser("~").encode(), b"<home>"
    )

def command(name: str, argv: list[str], out: Path, marker: bytes) -> dict[str, object]:
    started = time.monotonic()
    environment = dict(os.environ)
    environment.setdefault(
        "JAVA_HOME", "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    )
    process = subprocess.Popen(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=600)
        returncode = process.returncode
        timed_out = False
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGKILL)
        tail_stdout, tail_stderr = process.communicate()
        returncode = 124
        stdout = (error.stdout or b"") + (tail_stdout or b"")
        stderr = (error.stderr or b"") + (tail_stderr or b"")
        timed_out = True
    streams: dict[str, object] = {}
    for label, raw in (("stdout", stdout), ("stderr", stderr)):
        data = neutral(raw)
        path = out / f"{name}.{label}"
        path.write_bytes(data[:LIMIT])
        streams[label] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha(path),
            "bytes": len(data),
            "truncated": len(data) > LIMIT,
        }
    passed = (
        returncode == 0
        and marker in stdout
        and all(not streams[label]["truncated"] for label in streams)
    )
    return {
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "status": "passed" if passed else "timeout" if timed_out else "failed",
        "argv": [item.replace(str(ROOT), "<repo>") for item in argv],
        **streams,
    }
