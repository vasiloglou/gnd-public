"""LI1: the staged assurance report over the literature corpus (T6-T23).

Spec: .gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md.
Committed RED at the corpus gate. The harness
``gnd.examples.literature.assurance_report`` does not exist yet, so every case
here fails on import until it lands. The expected outcomes live in
src/gnd/examples/literature/expected/ and were approved with the corpus. A
report must agree with every value they give.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from gnd.anchors import canonical_document_text

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/literature"
KEY = EXAMPLE / "answers/answer-key.json"
EXPECTED = EXAMPLE / "expected"
STAGES = ("model-population-validity", "source-binding", "semantic-support", "identity-decisions",
          "derivation", "coverage", "freshness")
FORBIDDEN = {"--allow-vacuous", "--baseline", "--baseline-model"}
EXCLUDED_WITH_COMPOSITION = {"--anchors", "--document", "--populations"}


def _builder():
    spec = importlib.util.spec_from_file_location("build_literature_example", ROOT / "tools/build_literature_example.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _harness():
    from gnd.examples.literature import assurance_report

    return assurance_report


def _score(run: Path, answers: Path = KEY, corpus: Path = EXAMPLE) -> dict:
    return _harness().score(corpus, answers, run)


# --- The mutation table (spec §6.6), one literal transform per case ------------------


def _drop_fact(source: dict, fact_type: str, roles: dict) -> None:
    builder = _builder()
    source["facts"][fact_type] = [row for row in source["facts"][fact_type] if row != roles]
    if not source["facts"][fact_type]:
        del source["facts"][fact_type]
    source["anchors"] = [a for a in source["anchors"]
                         if not (a["fact_key"]["fact_type"] == fact_type and a["fact_key"]["roles"] == roles)]
    source["facts"] = builder.with_derived(source["facts"])


def _shift(sources: dict, *, recompute: bool) -> None:
    anchor = next(a for a in sources["opencap-monocular"]["anchors"] if a["role"] == "base_method")
    anchor["span"] = {"start": anchor["span"]["start"] + 1, "end": anchor["span"]["end"]}
    if recompute:
        text = canonical_document_text((EXAMPLE / "corpus/documents/opencap-monocular.md").read_bytes())
        anchor["excerpt_sha256"] = hashlib.sha256(text[anchor["span"]["start"]:anchor["span"]["end"]].encode()).hexdigest()


def _m1(s):
    for source in s.values():
        source["facts"], source["anchors"] = {}, []


def _m4(s):
    facts = s["vampnet"]["facts"]
    facts.setdefault("work_builds_on_method", []).append({"work": "arXiv:2307.04686", "method": "WhAM"})
    s["vampnet"]["facts"] = {k: facts[k] for k in sorted(facts)}


def _m5(s):
    builder = _builder()
    raw = json.loads(builder.population_bytes(s["posex"]["facts"]))
    raw["unexpected"] = True
    s["posex"]["population_bytes"] = builder._dump(raw)


def _x1(s):
    _drop_fact(s["vampnet"], "method_builds_on_method", {"method": "VampNet", "base_method": "bidirectional transformer"})
    _drop_fact(s["wham-whale"], "method_builds_on_method", {"method": "WhAM", "base_method": "VampNet"})
    _drop_fact(s["wham-pose"], "method_builds_on_method", {"method": "WHAM", "base_method": "SLAM"})
    _drop_fact(s["apinn"], "method_builds_on_method", {"method": "XPINN", "base_method": "PINNs"})
    return ("vampnet.p2", "wham-whale.p2", "wham-pose.p2", "apinn.p3", "posex.p2", "sbi-frontier.p2")


def _stale(run: Path) -> None:
    path = run / "composition/vampnet/population.json"
    path.write_bytes(json.dumps(json.loads(path.read_bytes())).encode() + b"\n")


MUTATIONS = {
    "M1-drop-all": (_m1, None),
    "M2-drop-one": (lambda s: _drop_fact(s["apinn"], "method_builds_on_method", {"method": "XPINN", "base_method": "PINNs"}), None),
    "M3-stale": (lambda s: None, _stale),
    "M4-false-derived": (_m4, None),
    "M5-invalid-population": (_m5, None),
    "M6-shifted-span": (lambda s: _shift(s, recompute=False), None),
    "X1-abstain-6": (_x1, None),
    "X2-consistent-shift": (lambda s: _shift(s, recompute=True), None),
    "M7-false-merge": (lambda s: None, None),  # LI2 R6: built by build_case from M7_RENAMINGS
}

# LI2 R6 (spec phase-LI2 §6.7): rename vampnets' VAMPnet to VampNet in both of its roles,
# citing a same decision that replaces the answer key's different decision i01.
M7_RENAMINGS = [
    {"source": "vampnets", "fact_type": "method_is_used_in_field", "role": "method", "from": "VAMPnet", "to": "VampNet"},
    {"source": "vampnets", "fact_type": "work_introduces_method", "role": "method", "from": "VAMPnet", "to": "VampNet"},
]


def _m7_pairs(builder):
    pairs = [p for p in builder.IDENTITY_PAIRS if p[0] != "i01"]
    return [("m7", ("vampnets", "VAMPnet"), ("wham-whale", "VampNet"), "same", []), *pairs]


def build_case(name: str, tmp: Path) -> Path:
    builder = _builder()
    corpus_raw = (EXAMPLE / "corpus/corpus.json").read_bytes()
    corpus = json.loads(corpus_raw)
    sources = copy.deepcopy(builder.reference_sources(EXAMPLE, corpus))
    transform, post = MUTATIONS[name]
    abstentions = transform(sources) or ()
    run = tmp / name
    # LI2 D8: every case carries the resolution regenerated over its own sources.
    if name == "M7-false-merge":
        resolution = builder.resolution_for(sources, _m7_pairs(builder))
        renamings = [dict(r, decision=0) for r in M7_RENAMINGS]
    else:
        resolution, renamings = builder.resolution_for(sources), []
    builder.write_run(EXAMPLE, corpus, corpus_raw, run, sources, abstentions=abstentions,
                      resolution=resolution, renamings=renamings)
    if post:
        post(run)
    return run


def assert_matches_expectation(report: dict, name: str) -> None:
    expected = json.loads((EXPECTED / f"{name}.expected.json").read_text(encoding="utf-8"))
    assert report["schema"] == "literature-assurance-report/1"
    assert report["exit_code"] == expected["exit_code"], report["failed_stages"]
    assert report["failed_stages"] == expected["failed_stages"]
    stages = {stage["stage"]: stage for stage in report["stages"]}
    assert list(stages) == list(STAGES)
    for stage, wanted in expected["stages"].items():
        got = stages[stage]
        assert got["status"] == wanted["status"], (stage, got["status"])
        for metric in ("agreement", "precision", "recall", "abstention"):
            if metric in wanted:
                assert [got[metric]["numerator"], got[metric]["denominator"]] == wanted[metric], (stage, metric)
        for flag in ("refused_units", "route_refused", "owner"):
            if flag in wanted:
                assert got[flag] == wanted[flag], (stage, flag)


# --- T6-T8: the reference run ---------------------------------------------------------


def test_reference_run_exits_0():
    report = _score(EXAMPLE / "runs/reference")
    assert_matches_expectation(report, "reference")
    key = json.loads(KEY.read_text(encoding="utf-8"))
    sizes = {stage["stage"]: stage["sample_size"] for stage in report["stages"]}
    assert sizes["semantic-support"] == len(key["assertions"])
    assert sizes["source-binding"] == len(key["anchored_facts"])
    assert sizes["model-population-validity"] == len(key["populations"])


def test_report_states_labels_and_counts():
    report = _score(EXAMPLE / "runs/reference")
    assert report["labels"]["independent"] is False and report["labels"]["note"]
    for field in ("corpus_sha256", "answers_sha256", "run_sha256", "gnd_version", "harness_sha256"):
        assert report["inputs"][field]
    for stage in report["stages"]:
        if stage["active"]:
            for field in ("sample_size", "exclusions", "unresolved", "disagreements", "label_disagreements"):
                assert field in stage, (stage["stage"], field)


def test_dormant_stages():
    report = _score(EXAMPLE / "runs/reference")
    # LI2 D8: identity-decisions is active; only coverage stays dormant.
    assert report["not_measured"] == [{"stage": "coverage", "owner": "literature-depth LD3"}]
    assert report["exit_code"] == 0
    assert {u["kind"] for u in report["unscored_labels"]} == {"chains", "reuse_cases", "name_pairs"}


# --- T9: the one status function -------------------------------------------------------


@pytest.mark.parametrize(("kwargs", "status"), [
    ({"active": False, "route_present": True, "metrics": {}, "floors": {}}, "not-measured"),
    ({"active": True, "route_present": False, "metrics": {}, "floors": {}}, "not-measured"),
    ({"active": True, "route_present": True, "metrics": {"recall": (0, 0)}, "floors": {"recall": (9, 10)}}, "fail"),
    ({"active": True, "route_present": True, "metrics": {"recall": (9, 10)}, "floors": {"recall": (9, 10)}}, "pass"),
    ({"active": True, "route_present": True, "metrics": {"recall": (8, 9)}, "floors": {"recall": (9, 10)}}, "fail"),
    ({"active": True, "route_present": True, "metrics": {"abstention": (3, 12)}, "floors": {"abstention_max": (1, 5)}}, "fail"),
    ({"active": True, "route_present": True, "metrics": {"recall": (1, 1)}, "floors": {"recall": (1, 1)}, "refused": 1}, "fail"),
])
def test_stage_status_branch_table(kwargs, status):
    assert _harness().stage_status(**kwargs) == status


# --- T10-T15, T19: the scored cases -----------------------------------------------------


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_mutation(name, tmp_path):
    assert_matches_expectation(_score(build_case(name, tmp_path)), name)


def test_consistent_shift_is_accepted_by_the_route(tmp_path):
    report = _score(build_case("X2-consistent-shift", tmp_path))
    stage = next(s for s in report["stages"] if s["stage"] == "source-binding")
    assert all(route["exit"] == 0 for route in stage["routes"] if "opencap-monocular" in " ".join(route["argv"]))


def test_abstaining_run_c5(tmp_path):
    report = _score(build_case("X1-abstain-6", tmp_path))
    stage = next(s for s in report["stages"] if s["stage"] == "semantic-support")
    assert (stage["precision"]["rate"], stage["recall"]["rate"], stage["abstention"]["rate"]) == (1.0, 0.5, 0.5)
    assert report["exit_code"] == 1 and "semantic-support" in report["failed_stages"]


# --- T16-T18: routes -------------------------------------------------------------------------


def test_route_table_never_combines_excluded_flags():
    routes = _harness().ROUTES
    assert set(routes) == {"R1", "R2", "R3", "R4"}
    for argv in routes.values():
        assert not FORBIDDEN & set(argv)
        if "--composition" in argv:
            assert not EXCLUDED_WITH_COMPOSITION & set(argv)
    combined = subprocess.run(
        [sys.executable, "-m", "gnd", "check", str(EXAMPLE / "model.orm.yaml"),
         str(EXAMPLE / "runs/reference/composed/population.json"), "--anchors", "x", "--composition", "y", "--sources", "z"],
        capture_output=True, text=True, check=False)
    assert combined.returncode == 64


def test_withheld_route_is_not_measured_and_fails(tmp_path):
    run = tmp_path / "run"
    shutil.copytree(EXAMPLE / "runs/reference", run)
    shutil.rmtree(run / "composed")
    report = _score(run)
    derivation = next(s for s in report["stages"] if s["stage"] == "derivation")
    assert (derivation["status"], derivation["owner"]) == ("not-measured", "run")
    assert report["exit_code"] == 1 and "derivation" in report["failed_stages"]
    for sidecar in (run / "composition").glob("*/population.json.anchors.json"):
        sidecar.unlink()
    binding = next(s for s in _score(run)["stages"] if s["stage"] == "source-binding")
    assert (binding["status"], binding["owner"]) == ("not-measured", "run")


def test_vacuous_derivation_is_not_success(tmp_path):
    # M1's composed population claims no derived row and R4 reports the derivation
    # unchecked: the zero-denominator rule and the abstention floor both fail it.
    report = _score(build_case("M1-drop-all", tmp_path))
    derivation = next(s for s in report["stages"] if s["stage"] == "derivation")
    assert derivation["status"] == "fail"
    assert derivation["abstention"]["numerator"] == 1


# --- T20-T23: refusals, order and bounded work ----------------------------------------


def _copy_inputs(tmp: Path) -> tuple[Path, Path, Path]:
    corpus = tmp / "example"
    shutil.copytree(EXAMPLE, corpus, ignore=shutil.ignore_patterns("expected"))
    return corpus, corpus / "answers/answer-key.json", corpus / "runs/reference"


HOSTILE = {
    "nan": b'{"schema": NaN}',
    "deep": b"[" * 65 + b"]" * 65,
    "long-int": b'{"n": ' + b"9" * 200 + b"}",
    "not-object": b"[]",
    "invalid-utf8": b'{"a": "\xff"}',
}


@pytest.mark.parametrize("target", ["corpus", "answers", "run"])
@pytest.mark.parametrize("hostile", sorted(HOSTILE) + ["oversize"])
def test_hostile_inputs(target, hostile, tmp_path):
    corpus, answers, run = _copy_inputs(tmp_path)
    path = {"corpus": corpus / "corpus/corpus.json", "answers": answers, "run": run / "run.json"}[target]
    path.write_bytes(b" " * (4 * 1024 * 1024 + 1) if hostile == "oversize" else HOSTILE[hostile])
    completed = subprocess.run(
        [sys.executable, "-m", "gnd.examples.literature.assurance_report", str(corpus), str(answers), str(run)],
        capture_output=True, text=True, check=False)
    assert completed.returncode == 3
    assert "Traceback" not in completed.stderr
    report = json.loads(completed.stdout)
    assert report["exit_code"] == 3 and report["stages"] == []
    assert report["reason"].startswith(("input:too-large" if hostile == "oversize" else "input:",))


def test_validation_order(tmp_path):
    corpus, answers, run = _copy_inputs(tmp_path)
    answers.write_text('{"schema": "literature-answer-key/1"}', encoding="utf-8")
    doc = json.loads((run / "run.json").read_text())
    doc["corpus_sha256"] = "0" * 64
    (run / "run.json").write_text(json.dumps(doc))
    assert _score(run, answers, corpus)["reason"].startswith("input:schema")
    corpus, answers, run = _copy_inputs(tmp_path / "second")
    key = json.loads(answers.read_text())
    key["corpus_sha256"] = "0" * 64
    answers.write_text(json.dumps(key))
    doc = json.loads((run / "run.json").read_text())
    doc["sources"].append("not-a-document")
    (run / "run.json").write_text(json.dumps(doc))
    assert _score(run, answers, corpus)["reason"] == "corpus:digest-mismatch"


@pytest.mark.parametrize(("reason", "edit"), [
    ("run:unknown-source", lambda doc, run: doc["sources"].append("not-a-document")),
    ("run:unknown-passage", lambda doc, run: doc["abstentions"].append("vampnet.p99")),
    ("run:abstained-passage-asserted", lambda doc, run: doc["abstentions"].append("vampnet.p2")),
    ("run:document-mismatch", lambda doc, run: (run / "composition/vampnet/document.txt").write_text("changed\n")),
])
def test_harness_refusals(reason, edit, tmp_path):
    corpus, answers, run = _copy_inputs(tmp_path)
    doc = json.loads((run / "run.json").read_text())
    edit(doc, run)
    (run / "run.json").write_text(json.dumps(doc))
    report = _score(run, answers, corpus)
    assert (report["exit_code"], report["reason"]) == (3, reason)


def test_symlinked_run_path_is_resolved(tmp_path):
    # Implementation finding: gnd refuses paths through a symlink, so an unresolved
    # symlinked run directory would score every route as refused.
    real = tmp_path / "real"
    shutil.copytree(EXAMPLE / "runs/reference", real)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert _score(link)["exit_code"] == 0


# --- Review regressions (one per reproduced finding, notes/phase-LI1-codex-review.md) ---


def test_composition_missing_a_source_fails(tmp_path):
    # R1: a composition that leaves out one of the run's sources must not pass.
    run = tmp_path / "run"
    shutil.copytree(EXAMPLE / "runs/reference", run)
    manifest_path = run / "composition/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sources"].remove("posex")
    manifest["scope_tags"] = [t for t in manifest["scope_tags"] if t["source"] != "posex"]
    manifest_path.write_text(json.dumps(manifest, indent=2))
    subprocess.run([sys.executable, "-m", "gnd", "compose", str(EXAMPLE / "model.orm.yaml"), str(run / "composition"),
                    "--out", str(run / "composed/population.json"), "--record", str(run / "composed/record.json")],
                   check=True, capture_output=True)
    report = _score(run)
    assert report["exit_code"] == 1
    freshness = next(s for s in report["stages"] if s["stage"] == "freshness")
    assert "composition:sources-differ" in freshness["disagreements"]["units"]


FAKE_GND = '''
import os, runpy, sys
args = sys.argv[1:]
route = "R4" if "--composition" in args else "R2" if "--anchors" in args else "R3" if args[:1] == ["fidelity"] else "R1"
if route == os.environ["FAKE_GND_BREAK"]:
    print("not a report")
    sys.exit(4 if route == "R1" else 3)
sys.argv = ["gnd", *args]
runpy.run_module("gnd", run_name="__main__")
'''


@pytest.mark.parametrize(("route", "stage"), [("R1", "model-population-validity"), ("R2", "freshness")])
def test_unreported_route_is_refused(route, stage, tmp_path, monkeypatch):
    # R2: a route that prints no report is a refused unit, never an agreement.
    fake = tmp_path / "fake_gnd.py"
    fake.write_text(FAKE_GND)
    monkeypatch.setenv("FAKE_GND_BREAK", route)
    report = _harness().score(EXAMPLE, KEY, EXAMPLE / "runs/reference", gnd=(sys.executable, str(fake)))
    got = next(s for s in report["stages"] if s["stage"] == stage)
    assert got["status"] == "fail" and got["refused_units"] == 12
    assert report["exit_code"] == 1


@pytest.mark.parametrize(("target", "edit"), [
    ("corpus/corpus.json", lambda doc: doc["documents"][0].__setitem__("split", [])),
    ("answers/answer-key.json", lambda doc: doc["assertions"][0].__setitem__("support", [])),
    ("answers/answer-key.json", lambda doc: doc["populations"][0].__setitem__("source", {"a": 1})),
])
def test_shape_type_errors_refuse_as_schema(target, edit, tmp_path):
    # R3: a field of the wrong type is a schema refusal, not an internal one.
    corpus, answers, run = _copy_inputs(tmp_path)
    path = corpus / target
    doc = json.loads(path.read_text())
    edit(doc)
    path.write_text(json.dumps(doc))
    assert _score(run, answers, corpus)["reason"] == "input:schema"


def test_cli_unwritable_out_has_no_traceback(tmp_path):
    # R4: an output path that cannot be written ends in a report, not a traceback.
    completed = subprocess.run(
        [sys.executable, "-m", "gnd.examples.literature.assurance_report", str(EXAMPLE), str(KEY),
         str(EXAMPLE / "runs/reference"), "--out", str(tmp_path)],
        capture_output=True, text=True, check=False)
    assert "Traceback" not in completed.stderr
    assert completed.returncode == 3
    assert json.loads(completed.stdout)["reason"] == "output:unwritable"


def test_harness_reads_gnd_only_through_the_cli():
    # R5: no gnd module is imported; the version comes from a route's own payload.
    import ast

    tree = ast.parse((EXAMPLE / "assurance_report.py").read_text(encoding="utf-8"))
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    assert not {name for name in imported if name == "gnd" or name.startswith("gnd.")}
    assert _score(EXAMPLE / "runs/reference")["inputs"]["gnd_version"] != "unknown"


def test_time_bound():
    harness = _harness()
    passages = [{"id": f"d.p{i}", "document": "d", "span": {"start": i * 10, "end": i * 10 + 9}} for i in range(5000)]
    anchors = [{"document": "d", "span": {"start": i * 10, "end": i * 10 + 9}} for i in range(5000)]
    started = time.monotonic()
    index = harness.passage_index(passages)
    assert len(harness.anchors_in_passages(index, anchors)) == 5000
    assert time.monotonic() - started < 10


# --- T24 (implementation successor, amendment A5): full report goldens -----------------

GOLDEN_CASES = ("reference", *sorted(MUTATIONS))


def _report_for(name: str, tmp: Path) -> dict:
    return _score(EXAMPLE / "runs/reference" if name == "reference" else build_case(name, tmp))


@pytest.mark.parametrize("name", GOLDEN_CASES)
def test_report_golden(name, tmp_path):
    golden = json.loads((EXPECTED / f"{name}.report.json").read_text(encoding="utf-8"))
    assert _report_for(name, tmp_path) == golden
    assert_matches_expectation(golden, name)


if __name__ == "__main__" and sys.argv[1:] == ["--write-goldens"]:
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        for case in GOLDEN_CASES:
            report = _report_for(case, Path(scratch).resolve())
            (EXPECTED / f"{case}.report.json").write_text(
                json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"wrote expected/{case}.report.json exit {report['exit_code']}")


def test_malformed_identity_label_is_schema_refusal(tmp_path):
    corpus, answers, run = _copy_inputs(tmp_path)
    key = json.loads(answers.read_text())
    key["identity_pairs"][0]["left"]["value"] = {}
    answers.write_text(json.dumps(key))
    assert _score(run, answers, corpus)["reason"] == "input:schema"


def test_identity_scoring_refuses_resolution_replaced_after_route(tmp_path, monkeypatch):
    _, answers, run = _copy_inputs(tmp_path)
    harness = _harness()
    original = harness._routes

    def routes(inputs, gnd, work):
        results = original(inputs, gnd, work)
        directory = inputs.run_dir / "composition"
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        resolution_path = directory / manifest["resolution"]["path"]
        resolution = json.loads(resolution_path.read_text())
        resolution["decisions"][0]["producer"]["id"] = "replaced-after-verification"
        raw = json.dumps(resolution).encode()
        resolution_path.write_bytes(raw)
        manifest["resolution"]["sha256"] = hashlib.sha256(raw).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        return results

    monkeypatch.setattr(harness, "_routes", routes)
    report = harness.score(EXAMPLE, answers, run)
    stage = next(s for s in report["stages"] if s["stage"] == "identity-decisions")
    assert stage["route_refused"] is True
    assert report["exit_code"] == 1
    assert any(item["kind"] == "identity_pairs" for item in report["unscored_labels"])
