from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import test_public_v62_admission_support as sandbox
from test_public_v62_admission_support import CORPUS, load


def _fabricated_probe() -> dict:
    """Every frozen answer, copied into both surfaces, with no installed module."""
    return {
        "cases": {
            row["case_id"]: {
                "class": row["class"],
                **{
                    surface: {
                        "assurance_level": row["final_assurance_level"],
                        "evidence_not_current": False,
                        "uncovered_count": row["uncovered_new_count"],
                        "uncovered_sha256": row["uncovered_new_sha256"],
                    }
                    for surface in ("cli", "api")
                },
            }
            for row in load(CORPUS / "class-cases.json")["cases"]
        }
    }


def test_rv1_a_probe_that_did_not_run_the_installed_wheel_is_refused():
    origin = "/run/venv/lib/python3.11/site-packages/gnd/__init__.py"
    with pytest.raises(ValueError, match="installed wheel"):
        sandbox._admit_v62_probe(_fabricated_probe(), mode="final", module_origin=origin)
    elsewhere = {**_fabricated_probe(), "module": "/somewhere/else/gnd/__init__.py"}
    with pytest.raises(ValueError, match="installed wheel"):
        sandbox._admit_v62_probe(elsewhere, mode="final", module_origin=origin)
    assert sandbox._admit_v62_probe(
        {**_fabricated_probe(), "module": origin}, mode="final", module_origin=origin
    )


def _surface_set(payload: dict, exit_code: int) -> dict:
    row = {
        "operation": "phase1-matrix",
        "result": {"isolated": True, "exit_code": exit_code, "payload": payload},
    }
    wheel = {"size_bytes": 1, "sha256": "a" * 64}
    return {
        "artifact": wheel,
        "operations": [row],
        "probe": {"isolated": True},
        "live_assurance": True,
    }


def test_rv2_a_failing_v61_surface_cannot_satisfy_the_summary():
    wheel = {"size_bytes": 1, "sha256": "a" * 64}
    passed = {"accepted": True, "observations": [{"case_id": "x", "exit_code": 0}]}
    failed = {"accepted": False, "observations": [{"case_id": "x", "exit_code": 0}]}
    summary = sandbox._v62_surface_summary(
        {"baseline": _surface_set(passed, 0), "final": _surface_set(failed, 1)}, wheel
    )
    assert summary["functional_equal"] is False
    summary = sandbox._v62_surface_summary(
        {"baseline": _surface_set(failed, 1), "final": _surface_set(failed, 1)}, wheel
    )
    assert summary["functional_equal"] is False
    # A v6.1 driver written for not-current evidence may reject a final wheel
    # only for being recertified: identical function, recertified assurance.
    before = {
        "accepted": True,
        "observations": [{"assurance_level": "none", "evidence_not_current": True}],
    }
    after = {
        "accepted": False,
        "observations": [{"assurance_level": "proof-backed", "evidence_not_current": False}],
    }
    summary = sandbox._v62_surface_summary(
        {"baseline": _surface_set(before, 0), "final": _surface_set(after, 1)}, wheel
    )
    assert summary["functional_equal"] is True


def test_rv6_a_failed_install_restores_the_predecessor_bundle(tmp_path, monkeypatch):
    destination = tmp_path / "_assurance_evidence"
    destination.mkdir()
    (destination / "manifest.json").write_text("predecessor")
    source = tmp_path / "source"
    source.mkdir()
    (source / "manifest.json").write_text("successor")

    def failing_copy(src, dst, *args, **kwargs):
        Path(dst).mkdir()
        raise OSError("disk full")

    original = shutil.copytree
    monkeypatch.setattr(sandbox.shutil, "copytree", failing_copy)
    with pytest.raises(OSError):
        sandbox._install_bundle(source, destination, lambda: True)
    assert (destination / "manifest.json").read_text() == "predecessor"
    monkeypatch.setattr(sandbox.shutil, "copytree", original)
    with pytest.raises(ValueError, match="refuses"):
        sandbox._install_bundle(source, destination, lambda: False)
    assert (destination / "manifest.json").read_text() == "predecessor"

