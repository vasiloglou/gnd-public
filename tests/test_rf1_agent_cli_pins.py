"""RF1 lane L-AGENT: agent_cli statuses, exits and stream handling (spec 6.6).

The fake subprocess is a real executable written into tmp_path, as in
tests/test_agent_cli.py, so the stream-draining code RF4 moves is exercised.
Monotonic timestamps are placeholders (rule N1 fallback): injecting a counting
clock into agent_cli would break its own deadline arithmetic.
"""

from __future__ import annotations

import asyncio
import os
import stat
from pathlib import Path

import pytest
from support.rf1_pins import CAPTURE_ENV, assert_golden, encode, observe

from gnd.agent_cli import (
    AgentAdapterId,
    ProcessLimits,
    build_agent_argv,
    invoke_agent,
    run_bounded_process,
)

PROGRAM = """#!/usr/bin/env python3
import os, sys, time
mode = sys.argv[1]
if mode == "ok":
    data = sys.stdin.buffer.read()
    os.write(1, b"out:" + data)
    os.write(2, b"err")
    raise SystemExit(0)
if mode == "exit":
    os.write(2, b"failing")
    raise SystemExit(int(sys.argv[2]))
if mode == "flood-stdout":
    os.write(1, b"o" * 5000)
    raise SystemExit(0)
if mode == "flood-stderr":
    os.write(2, b"e" * 5000)
    raise SystemExit(0)
if mode == "flood-both":
    os.write(1, b"o" * 4000)
    os.write(2, b"e" * 4000)
    raise SystemExit(0)
if mode == "secret":
    os.write(1, os.environ["SESSION_SECRET"].encode() + b"-suffix")
    raise SystemExit(0)
if mode == "sleep":
    time.sleep(30)
raise SystemExit(91)
"""

ADAPTER = """#!/usr/bin/env python3
import pathlib, sys, time
mode = pathlib.Path(__file__).with_name("mode").read_text()
if "--version" in sys.argv:
    if mode == "version-fails":
        raise SystemExit(3)
    print("rf1-fake-agent 1.0")
    raise SystemExit(0)
if mode == "fails":
    print("agent failed", file=sys.stderr)
    raise SystemExit(7)
if mode == "sleep":
    time.sleep(30)
print("agent stdout")
raise SystemExit(0)
"""

TIMING = ("started_monotonic", "ended_monotonic", "elapsed_seconds")


def _limits(**changes) -> ProcessLimits:
    values = {
        "timeout_seconds": 5.0,
        "terminate_grace_seconds": 0.1,
        "stdin_limit_bytes": 4096,
        "stdout_limit_bytes": 4096,
        "stderr_limit_bytes": 4096,
        "total_output_limit_bytes": 6144,
    }
    values.update(changes)
    return ProcessLimits.model_validate(values)


def _executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _wire(result) -> dict:
    data = result.model_dump(mode="json")
    for field in TIMING:
        if field in data:
            data[field] = "<monotonic>"
    return {"wire": data, "stdout": encode(result.stdout), "stderr": encode(result.stderr)}


RUN_SCENARIOS = {
    "success": (("./prog", "ok"), {}, {}, b"input"),
    "nonzero-exit": (("./prog", "exit", "3"), {}, {}, None),
    "stdout-over-limit": (("./prog", "flood-stdout"), {}, {}, None),
    "stderr-over-limit": (("./prog", "flood-stderr"), {}, {}, None),
    "aggregate-over-budget": (("./prog", "flood-both"), {}, {}, None),
    "missing-executable": (("./absent-program",), {}, {}, None),
    "timeout": (("./prog", "sleep"), {"timeout_seconds": 0.5}, {}, None),
    "secret-redaction": (("./prog", "secret"), {}, {"SESSION_SECRET": "rf1-secret-value-0123456789"}, None),
}


def test_agent_argv():
    observed = {
        adapter.value: observe(build_agent_argv, adapter, "a prompt with 'quotes'\nand a newline")
        for adapter in AgentAdapterId
    }
    observed["not-an-adapter"] = observe(build_agent_argv, "claude", "x")
    assert_golden("agent", "argv", observed)


@pytest.mark.parametrize("scenario", sorted(RUN_SCENARIOS))
def test_agent_run(scenario, tmp_path):
    _executable(tmp_path / "prog", PROGRAM)
    argv, limits, env, stdin = RUN_SCENARIOS[scenario]

    def run():
        return _wire(
            asyncio.run(run_bounded_process(argv, cwd=tmp_path, env=env, limits=_limits(**limits), stdin_bytes=stdin))
        )

    assert_golden("agent-run", scenario, observe(run))


INVOKE_SCENARIOS = {"success": ("ok", 5.0), "failure": ("fails", 5.0), "timeout": ("sleep", 1.0), "version-fails": ("version-fails", 5.0)}


@pytest.mark.parametrize("scenario", sorted(INVOKE_SCENARIOS))
def test_agent_invoke(scenario, tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(bin_dir / "claude", ADAPTER)
    mode, timeout = INVOKE_SCENARIOS[scenario]
    (bin_dir / "mode").write_text(mode)
    for name in list(os.environ):
        if name not in {"PATH", CAPTURE_ENV}:
            monkeypatch.delenv(name)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    work = tmp_path / "work"
    work.mkdir()

    def run():
        result = asyncio.run(
            invoke_agent(
                AgentAdapterId.claude,
                prompt="rf1 prompt",
                cwd=work,
                timeout_seconds=timeout,
                terminate_grace_seconds=0.1,
                feedback_bytes=None,
            )
        )
        return _wire(result)

    observed = observe(run)
    text = str(bin_dir.resolve())
    if isinstance(observed.get("ok"), dict):
        wire = observed["ok"]["wire"]
        for key in ("executable",):
            if isinstance(wire.get(key), str):
                wire[key] = wire[key].replace(text, "<bin>").replace(str(bin_dir), "<bin>")
    assert_golden("agent-invoke", scenario, observed)
