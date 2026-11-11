"""RF2 predecessor controls. Answers captured on f5a8318 before any move."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

from support.recorded_version import tree_as_recorded
from test_measure_offline import MODEL, corpus  # noqa: F401 -- fixture reuse

from gnd import cli
from gnd.export import emit, pyrel_runtime
from gnd.measure import coverage, report
from gnd.synth import frontier

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = ROOT / "tests/fixtures/rf2-pins/pre-move.json"
# Issue 172: the version the measure successor was recorded at.
RECORDED_AT = "0.3.0"


def pin(name, value):
    value = json.loads(json.dumps(value))
    capture = os.environ.get("GND_RF2_CAPTURE")
    if capture:
        target = Path(capture) / f"{name}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists()
        target.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")
    else:
        expected = json.loads(ANSWERS.read_text())[name]
        if name == 'standalone_pyrel_output_bytes':
            from support.rf9_ci_sources import EVIDENCE
            successor = json.loads((EVIDENCE / 'pyrel-successor.json').read_text())
            assert successor['before'] == expected and successor['reason']
            from support.pyrel_application_successors import rendered_bytes
            expected = rendered_bytes(successor['after'], EVIDENCE / 'pyrel-successor.json')
        if name == 'measure_output_bytes':
            successor = json.loads((ANSWERS.parent / 'measure-successor.json').read_text())
            assert successor['before'] == expected and successor['reason']
            expected = successor['after']
        assert value == expected


def test_measure_guarded_exists_refs(monkeypatch):
    # Isolate the reference filter, retaining its real traversal and output.
    monkeypatch.setattr(coverage, "observed_cells", lambda *_: {})
    monkeypatch.setattr(coverage, "applicability_matrix", lambda *_: [])
    monkeypatch.setattr(coverage, "coverage_fraction", lambda *_: (0, 0, None))
    monkeypatch.setattr(coverage, "families_in_model", lambda *_: [])
    monkeypatch.setattr(frontier, "frontier_codes_for", lambda *_: [])
    model = SimpleNamespace(constraints=[
        {"type": "textual"},
        {"type": "guarded", "consequent": {"exists": {}}},
        {"type": "guarded", "consequent": {"exists": []}},
        {"type": "guarded", "consequent": None},
        {"type": "guarded", "consequent": {"exists": {"roles": []}}},
    ])
    records = [{"constraint_ref": f"constraints[{i}]", "mechanism": "fixture"}
               for i in range(6)]
    result = report._coverage_matrix_summary(model, [], {"not_derivable": records})
    assert [r["constraint_ref"] for r in result["unsupported_exists_rules"]] == [
        "constraints[1]", "constraints[4]"]
    pin("measure_guarded_exists_refs", result)


def test_pyrel_inline_and_top_level_refs():
    index = pyrel_runtime.ModelIndex({"fact_types": [
        {"id": "B", "constraints": [{"type": "textual"}, {"type": "value"}]},
        {"id": "A", "constraints": [{"type": "uniqueness"}]},
    ], "constraints": [{"type": "equality"}, {"type": "subset"}]})
    rows = pyrel_runtime._constraint_entries(index)
    assert [row[0] for row in rows] == [
        "fact_types[B].constraints[0]", "fact_types[B].constraints[1]",
        "fact_types[A].constraints[0]", "constraints[0]", "constraints[1]"]
    pin("pyrel_inline_and_top_level_refs", rows)


def test_measure_output_bytes(corpus, tmp_path):  # noqa: F811 -- imported fixture
    target = tmp_path / "measurement.json"
    assert cli.main(["measure", str(MODEL), "--populations", str(corpus),
                     "--format", "json", "--out", str(target)]) == 0
    # Issue 172: the successor pins the bytes written at RECORDED_AT. The corpus is
    # synthesized for this test, so its sidecars carry the version and the payload cites
    # their digests: the payload is taken together with the corpus it cites.
    files = {path.relative_to(corpus).as_posix(): path.read_bytes()
             for path in sorted(Path(corpus).rglob("*")) if path.is_file()}
    assert "<payload>" not in files
    raw = tree_as_recorded({**files, "<payload>": target.read_bytes()}, RECORDED_AT)["<payload>"]
    pin("measure_output_bytes", {"sha256": hashlib.sha256(raw).hexdigest(),
                                 "size_bytes": len(raw)})


def test_standalone_pyrel_output_bytes(monkeypatch):
    monkeypatch.chdir(ROOT)
    source = emit.render_pyrel(Path("tests/fixtures/pyrel-oracle/basics.orm.yaml"))
    raw = source.encode()
    pin("standalone_pyrel_output_bytes", {"sha256": hashlib.sha256(raw).hexdigest(),
                                          "size_bytes": len(raw)})
