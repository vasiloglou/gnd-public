"""LI2: sense-resolution decisions bound to composition (T1-T20).

Spec: .gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md.
Committed RED at the corpus gate. Composition does not yet understand a
``resolution`` entry, so the manifest parser refuses it. The fixtures and
their approved outcomes live in src/gnd/examples/literature/resolution/
(cases.json). The controls that pass before the implementation are W-flat,
the mentions check (T2) and the baseline bytes (T16).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "src/gnd/examples/literature/resolution"
MODEL = FIXTURES / "model.orm.yaml"
CASES = json.loads((FIXTURES / "cases.json").read_text(encoding="utf-8"))["cases"]
BY_ID = {case["id"]: case for case in CASES}


def _compose(directory: Path) -> dict:
    from gnd import api

    return api.compose(str(MODEL), str(directory))


def _gnd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "gnd", *map(str, args)], capture_output=True, text=True, check=False)


def _copy_case(case_id: str, tmp: Path) -> Path:
    target = tmp / case_id
    shutil.copytree(FIXTURES / "cases" / case_id, target)
    return target


def _rebind(directory: Path, resolution: dict) -> None:
    """Rewrite resolution.json and the manifest digest that binds it."""
    raw = (json.dumps(resolution, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    (directory / "resolution.json").write_bytes(raw)
    manifest = json.loads((directory / "manifest.json").read_text())
    manifest["resolution"]["sha256"] = hashlib.sha256(raw).hexdigest()
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def _values(population: dict, fact_type: str = "method_builds_on_method") -> set:
    return {value for row in population["facts"].get(fact_type, []) for value in row.values()}


def _ancestor_target(tmp: Path, method: str, ancestor: str) -> Path:
    path = tmp / "targets.json"
    path.write_text(json.dumps({"version": 1, "targets": [{"fact_type": "method_has_ancestor_method", "tuple": [
        {"primitive": "String", "value": method}, {"primitive": "String", "value": ancestor}]}]}))
    return path


def _compose_to(directory: Path, tmp: Path, name: str) -> tuple[Path, Path]:
    population, record = tmp / f"{name}.population.json", tmp / f"{name}.record.json"
    done = _gnd("compose", MODEL, directory, "--out", population, "--record", record)
    assert done.returncode == 0, done.stdout + done.stderr
    return population, record


# --- Every approved case: exit and exact refusal message ----------------------------


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case_outcome(case):
    result = _compose(FIXTURES / case["directory"])
    assert result["exit_code"] == case["exit"], result.get("error")
    if case["exit"] == 3:
        assert result["error"]["message"] == case["message"]


# --- T1 (R1): the whale ---------------------------------------------------------------


def test_whale_flat_derives_the_false_chain_and_resolution_removes_it(tmp_path):
    target = _ancestor_target(tmp_path, "OpenCap Monocular", "DMD")
    population, record = _compose_to(FIXTURES / "cases/W-flat", tmp_path, "flat")
    flat = _gnd("witness", MODEL, population, "--targets", target, "--composition", record, "--raw",
                "--out", tmp_path / "flat.witness.json")
    assert flat.returncode == 0
    population, record = _compose_to(FIXTURES / "cases/W-resolved", tmp_path, "resolved")
    composed = json.loads(population.read_text())
    edges = composed["facts"]["method_builds_on_method"]
    assert len(edges) == 3
    assert {"VampNet", "VampNet [music]", "WHAM", "WhAM [whale]"} <= _values(composed)
    resolved = _gnd("witness", MODEL, population, "--targets", target, "--composition", record, "--raw",
                    "--out", tmp_path / "resolved.witness.json")
    assert resolved.returncode == 2


# --- T2 (R2): two senses, one spelling, one document -----------------------------------


def test_mentions_keep_two_senses_and_anchors_pass():
    folder = FIXTURES / "mentions"
    done = _gnd("check", MODEL, folder / "population.json", "--anchors", folder / "population.json.anchors.json",
                "--document", folder / "document.txt", "--format", "json")
    report = json.loads(done.stdout)
    assert report["exit_code"] == 0 and report["counts"]["fail"] == 0
    population = json.loads((folder / "population.json").read_text())
    surfaces = population["facts"]["mention_has_surface_text"]
    assert len(surfaces) == 2 and {r["surface"] for r in surfaces} == {"VampNet"}
    assert len({r["sense"] for r in population["facts"]["mention_denotes_sense"]}) == 2


# --- T4 (R3): the record names the decisions applied --------------------------------------


def test_alias_record_names_its_decision():
    result = _compose(FIXTURES / "cases/A-alias")
    assert result["exit_code"] == 0
    record = result["record"]
    assert record["resolution_sha256"] == hashlib.sha256((FIXTURES / "cases/A-alias/resolution.json").read_bytes()).hexdigest()
    assert [fact["decisions"] for fact in record["facts"]] == [[0], [0], [0]]
    assert "AF3" not in _values(json.loads(json.dumps(result["population"])))


# --- T6 (R7): unresolved keys take their placeholders -----------------------------------------


def test_unresolved_keys_take_distinct_placeholders():
    result = _compose(FIXTURES / "cases/H-unresolved")
    assert result["exit_code"] == 0
    assert {"TRACE#1", "TRACE#2"} <= _values(result["population"])
    assert "TRACE" not in _values(result["population"])


# --- T7-T12: refusals are value-free -------------------------------------------------------------


@pytest.mark.parametrize("case", [c for c in CASES if c["exit"] == 3], ids=lambda c: c["id"])
def test_refusals_name_no_value(case):
    resolution = FIXTURES / case["directory"] / "resolution.json"
    values = set()
    if resolution.is_file():
        for decision in json.loads(resolution.read_text())["decisions"]:
            values |= {key["value"] for key in decision["keys"]}
    message = case["message"].removeprefix("composition:invalid: ")
    assert not {v for v in values if f" {v} " in f" {message} " or f"'{v}'" in message}


# --- T13, T14 (R5): a changed decision makes the composition stale ---------------------------------


def test_changed_decision_is_stale_for_check(tmp_path):
    directory = _copy_case("W-resolved", tmp_path)
    population, record = _compose_to(directory, tmp_path, "before")
    resolution = json.loads((directory / "resolution.json").read_text())
    resolution["decisions"][0]["producer"]["id"] = "second-reviewer"
    (directory / "resolution.json").write_text(json.dumps(resolution, indent=2, sort_keys=True) + "\n")
    unbound = _gnd("check", MODEL, population, "--composition", record, "--sources", directory, "--format", "json")
    assert unbound.returncode == 3
    assert "resolution digest differs from the manifest" in json.loads(unbound.stdout)["error"]["message"]
    _rebind(directory, resolution)
    rebound = _gnd("check", MODEL, population, "--composition", record, "--sources", directory, "--format", "json")
    assert rebound.returncode == 3
    assert "differs from the record at manifest_sha256" in json.loads(rebound.stdout)["error"]["message"]


def test_changed_decision_is_stale_for_replay_and_the_old_snapshot_replays(tmp_path):
    directory = _copy_case("W-resolved", tmp_path / "now")
    old_population, old_record = _compose_to(directory, tmp_path, "old")
    target = _ancestor_target(tmp_path, "OpenCap Monocular", "WHAM")
    witness = tmp_path / "old.witness.json"
    made = _gnd("witness", MODEL, old_population, "--targets", target, "--composition", old_record, "--raw", "--out", witness)
    assert made.returncode == 0
    resolution = json.loads((directory / "resolution.json").read_text())
    resolution["decisions"][1]["producer"]["id"] = "second-reviewer"
    _rebind(directory, resolution)
    new_population, new_record = _compose_to(directory, tmp_path, "new")
    stale = _gnd("replay", MODEL, new_population, witness, "--composition", new_record)
    assert stale.returncode == 3 and "binding-stale" in stale.stdout
    assert _gnd("replay", MODEL, old_population, witness, "--composition", old_record).returncode == 0


# --- T16 (R5): without a resolution, the bytes are the baseline's -----------------------------------


def test_no_resolution_keeps_baseline_bytes(tmp_path):
    baseline = json.loads((FIXTURES / "baseline.json").read_text())
    for name, case in baseline["cases"].items():
        directory = tmp_path / name
        shutil.copytree(ROOT / case["directory"], directory)
        manifest = json.loads((directory / "manifest.json").read_text())
        if manifest.pop("resolution", None) is not None:
            (directory / "resolution.json").unlink()
            manifest["renamings"] = [{k: v for k, v in r.items() if k != "decision"} for r in manifest["renamings"]]
            (directory / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        population, record = tmp_path / f"{name}.population.json", tmp_path / f"{name}.record.json"
        done = _gnd("compose", ROOT / case["model"], directory, "--out", population, "--record", record)
        assert done.returncode == 0, done.stdout + done.stderr
        assert hashlib.sha256(population.read_bytes()).hexdigest() == case["population_sha256"], name
        assert hashlib.sha256(record.read_bytes()).hexdigest() == case["record_sha256"], name


# --- T17: one walk over the four identity-changing outcomes ------------------------------------------


def _key(source, value, outcome, coordinate):
    return {"source": source, "object_type": "method", "value": value, "outcome": outcome, "coordinate": coordinate}


def _decision(kind, left, right, placeholders=None):
    return {"decision": kind, "keys": [{"source": s, "object_type": "method", "value": v} for s, v in (left, right)],
            "placeholders": placeholders}


ONE_WALK = [
    # merging renaming, covered / uncovered
    ([_key("a", "AlphaFold3", "AlphaFold3", "a f#0.m"), _key("b", "AF3", "AlphaFold3", "b f#0.m")],
     [_decision("same", ("a", "AlphaFold3"), ("b", "AF3"))], None),
    ([_key("a", "AlphaFold3", "AlphaFold3", "a f#0.m"), _key("b", "AF3", "AlphaFold3", "b f#0.m")],
     [], "joined without a same decision"),
    # separating renaming, covered / uncovered
    ([_key("a", "TRACE", "TRACE", "a f#0.m"), _key("b", "TRACE", "TRACE [b]", "b f#0.m")],
     [_decision("different", ("a", "TRACE"), ("b", "TRACE"))], None),
    ([_key("a", "TRACE", "TRACE", "a f#0.m"), _key("b", "TRACE", "TRACE [b]", "b f#0.m")],
     [], "end apart without a different or unresolved decision"),
    # equal values joined unchanged, covered / uncovered
    ([_key("a", "PINNs", "PINNs", "a f#0.m"), _key("b", "PINNs", "PINNs", "b f#0.m")],
     [_decision("same", ("a", "PINNs"), ("b", "PINNs"))], None),
    ([_key("a", "PINNs", "PINNs", "a f#0.m"), _key("b", "PINNs", "PINNs", "b f#0.m")],
     [_decision("different", ("a", "PINNs"), ("b", "PINNs"))], "(different) keys end joined"),
    # unresolved separation, taken / not taken
    ([_key("a", "TRACE", "TRACE#1", "a f#0.m"), _key("b", "TRACE", "TRACE#2", "b f#0.m")],
     [_decision("unresolved", ("a", "TRACE"), ("b", "TRACE"), ["TRACE#1", "TRACE#2"])], None),
    ([_key("a", "TRACE", "TRACE#1", "a f#0.m"), _key("b", "TRACE", "TRACE", "b f#0.m")],
     [_decision("unresolved", ("a", "TRACE"), ("b", "TRACE"), ["TRACE#1", "TRACE#2"])], "does not take its placeholder"),
]


@pytest.mark.parametrize(("keys", "decisions", "refusal"), ONE_WALK)
def test_one_walk_over_every_outcome(keys, decisions, refusal):
    from gnd.composition_resolution import check_coverage

    from gnd.composition import CompositionError

    if refusal is None:
        check_coverage(keys, decisions)
    else:
        with pytest.raises(CompositionError, match=refusal):
            check_coverage(keys, decisions)


def test_decision_kinds_are_compared_in_one_module():
    hits = []
    for path in sorted((ROOT / "src/gnd").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if any(f'== "{kind}"' in text or f"== '{kind}'" in text for kind in ("same", "different", "unresolved")):
            hits.append(path.name)
    assert hits == ["composition_resolution.py"]


# --- T18: the resolution reader is total --------------------------------------------------------------


HOSTILE = {
    "nan": b'{"schema": NaN}',
    "deep": b"[" * 65 + b"]" * 65,
    "long-int": b'{"n": ' + b"9" * 200 + b"}",
    "not-object": b"[]",
    "wrong-schema": b'{"schema": "gnd-resolution/2", "object_types": [], "decisions": []}',
    "bad-kind": json.dumps({"schema": "gnd-resolution/1", "object_types": ["method"], "decisions": [
        {"decision": "maybe", "keys": [], "evidence": [], "producer": {}, "input_sha256": {}, "placeholders": None}]}).encode(),
    "unknown-object-type": b'{"schema": "gnd-resolution/1", "object_types": ["planet"], "decisions": []}',
    "oversize": b" " * (4 * 1024 * 1024 + 1),
}


@pytest.mark.parametrize("hostile", sorted(HOSTILE))
def test_hostile_resolution_refuses_at_3(hostile, tmp_path):
    directory = _copy_case("R-uncovered", tmp_path)
    raw = HOSTILE[hostile]
    (directory / "resolution.json").write_bytes(raw)
    manifest = json.loads((directory / "manifest.json").read_text())
    manifest["resolution"]["sha256"] = hashlib.sha256(raw).hexdigest()
    (directory / "manifest.json").write_text(json.dumps(manifest))
    result = _compose(directory)
    assert result["exit_code"] == 3
    assert result["error"]["message"].startswith("composition:invalid: resolution")


# --- T20: the coverage walk is bounded ---------------------------------------------------------------------


def test_coverage_walk_time_bound():
    from gnd.composition_resolution import check_coverage

    keys, decisions = [], []
    for source in range(200):
        for value in range(200):
            keys.append(_key(f"s{source}", f"m{value}", f"m{value}", f"s{source} f#{value}.m"))
    for value in range(100):
        for source in range(1, 200):
            decisions.append(_decision("same", ("s0", f"m{value}"), (f"s{source}", f"m{value}")))
    started = time.monotonic()
    with pytest.raises(Exception, match="joined without a same decision"):
        check_coverage(keys, decisions[:19_900])
    assert time.monotonic() - started < 10
