from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

from gnd.report import legacy_report_projection

REPO_ROOT=Path(__file__).resolve().parents[1]


def _public_baselines():
    packed=(Path(__file__).parent/"fixtures/public-guarded-baseline/closure.json.gz").read_bytes()
    assert len(packed)<=65536
    assert hashlib.sha256(packed).hexdigest()=='f7ecf5624980a1f0567828fae61158f40c29a6fa47ad54003772a3774deab595'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw=stream.read(65537)
    assert len(raw)<=65536
    assert hashlib.sha256(raw).hexdigest()=='ec7ac55529196f3bca731ae927642fa57a38743acc1179876ba55bb671ff36ff'
    documents=json.loads(raw)
    assert set(documents)=={'setfam.validate.json', 'v2_worked_example.validate.json', 'ring_pass.check.json', 'ring.validate.json', 'setfam_pass.check.json'}
    temporary=tempfile.TemporaryDirectory(prefix="gnd-public-guarded-baselines-")
    root=Path(temporary.name)
    for name,text in documents.items():
        (root/name).write_text(text,encoding="utf-8")
    return temporary,root

_TEMPORARY,BASELINE=_public_baselines()
atexit.register(_TEMPORARY.cleanup)

PHASE3_REWIRED_REPORT_SHA256 = {
    "setfam_fail.check.json": "419cefba80ab06bd78c6ca96c155cb584374aa6bb92b31ec6708a03eaedeee16",
    "ring_fail.check.json": "2ac4018d81f33cc688d0ec899eba2e0659d6a2bfc501c37ae7acc0a39ca1dffb",
}

# Issue #34 request 2: role-scoped value constraint messages now name their role,
# so the two setfam reports move again. Each entry pins the complete new wire
# bytes at the projection version its predecessor pin used; the predecessor
# fixture and the Phase 3 digest above stay unchanged for historical comparison.
ROLE_SCOPED_VALUE_REPORT_SHA256 = {
    "setfam_pass.check.json": (3, "37e341e82b09be3ba07fed91a69ad5c8b2de37853fe616833a21dd19ab710ab7"),
    "setfam_fail.check.json": (5, "5569f1a1b3728a557abfa72a5d5ab0138b16b1bda5113377e72ad6caec1da887"),
}

def _run_cli(*args: str, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=text,
        check=False,
    )

BASELINE_CASES = [
    pytest.param(
        ("validate", "tests/fixtures/models/v2_worked_example.orm.yaml", "--format", "json"),
        "v2_worked_example.validate.json",
        id="v2-worked-example-validate",
    ),
    pytest.param(
        ("validate", "tests/fixtures/checker/setfam.orm.yaml", "--format", "json"),
        "setfam.validate.json",
        id="setfam-validate",
    ),
    pytest.param(
        ("validate", "tests/fixtures/checker/ring.orm.yaml", "--format", "json"),
        "ring.validate.json",
        id="ring-validate",
    ),
    pytest.param(
        (
            "check",
            "tests/fixtures/checker/setfam.orm.yaml",
            "tests/fixtures/checker/population.setfam_pass.yaml",
            "--format",
            "json",
        ),
        "setfam_pass.check.json",
        id="setfam-pass-check",
    ),
    pytest.param(
        (
            "check",
            "tests/fixtures/checker/setfam.orm.yaml",
            "tests/fixtures/checker/population.setfam_fail.yaml",
            "--format",
            "json",
        ),
        "setfam_fail.check.json",
        id="setfam-fail-check",
    ),
    pytest.param(
        (
            "check",
            "tests/fixtures/checker/ring.orm.yaml",
            "tests/fixtures/checker/population.ring_pass.yaml",
            "--format",
            "json",
        ),
        "ring_pass.check.json",
        id="ring-pass-check",
    ),
    pytest.param(
        (
            "check",
            "tests/fixtures/checker/ring.orm.yaml",
            "tests/fixtures/checker/population.ring_fail.yaml",
            "--format",
            "json",
        ),
        "ring_fail.check.json",
        id="ring-fail-check",
    ),
]

@pytest.mark.parametrize(("args", "golden_name"), BASELINE_CASES)
def test_zero_guarded_reports_match_immutable_baseline(
    args: tuple[str, ...], golden_name: str
) -> None:
    result = _run_cli(*args, text=False)
    payload = json.loads(result.stdout)
    if golden_name in ROLE_SCOPED_VALUE_REPORT_SHA256:
        version, digest = ROLE_SCOPED_VALUE_REPORT_SHA256[golden_name]
        wire = (json.dumps(legacy_report_projection(payload, version)) + "\n").encode()
        assert hashlib.sha256(wire).hexdigest() == digest
        return
    if golden_name in PHASE3_REWIRED_REPORT_SHA256:
        # These two broad reports deliberately move when Phase 3 makes the v6
        # semantic providers authoritative. Pin the complete new wire bytes;
        # the predecessor fixture remains immutable for historical comparison.
        phase3_wire = (
            json.dumps(legacy_report_projection(payload, 5)) + "\n"
        ).encode()
        assert hashlib.sha256(phase3_wire).hexdigest() == PHASE3_REWIRED_REPORT_SHA256[
            golden_name
        ]
        return
    # The predecessor bytes stay the pin: undoing ONLY Phase 3's declared model
    # binding must reproduce the baseline byte for byte (see spec IF-P3-16).
    normalized = result.stdout
    if args[0] in {"check", "verify"}:
        normalized = (json.dumps(legacy_report_projection(payload, 3)) + "\n").encode()
    assert normalized == (BASELINE / golden_name).read_bytes()

