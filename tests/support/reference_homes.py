"""Run each load-then-bind home over the dispatch reference fixture.

Evolve-loading follow-up r2 (spec r2.4, H2/H3): one entry per home that binds
reference populations, each reduced to a comparable outcome. The fixture is a
scratch copy of tests/fixtures/reference-corpus/dispatch/.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DISPATCH = ROOT / "tests" / "fixtures" / "reference-corpus" / "dispatch"
REFERENCE = Path("references") / "catalog.pop.json"


def workspace(tmp_path: Path, damage: str | None) -> Path:
    work = tmp_path / "ws"
    shutil.copytree(DISPATCH, work)
    reference = work / REFERENCE
    if damage == "missing":
        reference.unlink()
    elif damage == "changed":
        reference.write_bytes(reference.read_bytes() + b"\n")
    elif damage == "linked":
        outside = tmp_path / "outside.pop.json"
        outside.write_bytes(reference.read_bytes())
        reference.unlink()
        reference.symlink_to(outside)
    return work


def _outcome(call, work: Path):
    try:
        value = call()
    except BaseException as error:  # noqa: BLE001 -- the outcome is what is compared
        return ["raise", type(error).__name__, str(error).replace(str(work), "<WS>")]
    if isinstance(value, dict) and "outcome" in value:
        return ["return", value["outcome"], value.get("error")]
    if hasattr(value, "exit_code"):
        return ["return", value.exit_code, getattr(value, "reason", None)]
    return ["return", type(value).__name__]


def _judgments(work: Path, tmp_path: Path, monkeypatch):
    import gnd.judgments
    from gnd import api

    for name in ("policy.json", "receipts.json"):
        (tmp_path / name).write_text("{}")
    monkeypatch.setattr(gnd.judgments, "read_judgment_policy", lambda raw: {"probe": True})
    monkeypatch.setattr(gnd.judgments, "read_judgment_receipts", lambda raw: [])
    return api.judgments(work / "model.orm.yaml", work / "candidate.pop.json",
                         tmp_path / "policy.json", tmp_path / "receipts.json",
                         trusted_root=tmp_path)


def _replay(work: Path):
    from gnd.exp.session_replay import _model

    raw = (work / "model.orm.yaml").read_bytes()
    model = SimpleNamespace(path="model.orm.yaml", size_bytes=len(raw),
                            sha256=hashlib.sha256(raw).hexdigest())
    case = SimpleNamespace(verify=SimpleNamespace(model=model), reference_root=".")
    return _model(case, work)


def run(home: str, work: Path, tmp_path: Path, monkeypatch):
    from support.cli_runner import run_main

    model, population = work / "model.orm.yaml", work / "candidate.pop.json"
    calls = {
        "discover": lambda: SimpleNamespace(exit_code=run_main([
            "discover", str(model), str(population), "--out", str(work / "d.json"),
            "--report", str(work / "r.json"), "--actor", "h", "--requested-at",
            "2026-10-27T00:00:00+00:00"]).returncode),
        "lean": lambda: __import__("gnd.export.lean_io", fromlist=["x"]).export_lean(
            model, population, toolchain="leanprover/lean4:v4.34.0"),
        "souffle": lambda: __import__("gnd.export.souffle_io", fromlist=["x"]).export_souffle(
            model, population),
        "pyrel": lambda: __import__("gnd.export.pyrel_rules", fromlist=["x"]).render(
            model, "duckdb"),
        "witness": lambda: __import__("gnd.witness.service", fromlist=["x"])._witness_inputs(
            model, population, None),
        "judgments": lambda: _judgments(work, tmp_path, monkeypatch),
        "replay": lambda: _replay(work),
    }
    return _outcome(calls[home], work)


HOMES = ("discover", "lean", "souffle", "pyrel", "witness", "judgments", "replay")
DAMAGES = (None, "missing", "changed", "linked")
