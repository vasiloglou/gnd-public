"""Original parser refusal and completely mocked supervisor timeout guards."""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
from pathlib import Path

import pytest
import test_public_phase5_cache_support as run
import test_public_phase5_timeout_support as run_formal
from test_public_phase5_cache_support import ROOT


def test_formal_timeout_returns_bounded_closed_evidence(monkeypatch):
    class HangingProcess:
        pid = 42
        returncode = None

        def __init__(self, *_args, **_kwargs):
            self.calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired(["formal"], 1, output=b"partial", stderr=b"problem")
            self.returncode = -9
            return b"", b""

    killed = []
    monkeypatch.setattr(run_formal.subprocess, "Popen", HangingProcess)
    monkeypatch.setattr(run_formal.os, "killpg", lambda pid, sig: killed.append((pid, sig)))
    with tempfile.TemporaryDirectory(prefix="phase5-review-", dir=ROOT) as directory:
        result = run_formal.command("formal", ["formal"], Path(directory), b"success")
        assert result["status"] == "timeout"
        assert result["timed_out"] is True
        assert result["returncode"] == 124
        assert killed == [(42, run_formal.signal.SIGKILL)]

def test_hostile_float_and_nonobject_cache_are_closed(tmp_path: Path):
    path = tmp_path / "hostile.json"
    path.write_text('{"x":1e1000000}', encoding="utf-8")
    with pytest.raises(run.CorrespondenceError, match="nonfinite"):
        run.load_json(path)
    path.write_text("[]", encoding="utf-8")
    assert run._cached(path) is False
    assert not math.isfinite(json.loads('{"x":1e1000000}')["x"])
