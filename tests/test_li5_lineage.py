"""LI5 corpus, ordered paths, transfer, cycle and proof bindings."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes

EXAMPLE = Path(__file__).resolve().parents[1] / "src/gnd/examples/literature"
DATA = EXAMPLE / "lineage"
MODEL = DATA / "model.orm.yaml"


def read(path):
    return json.loads(path.read_bytes())


def gnd(*args):
    return subprocess.run([sys.executable, "-m", "gnd", *map(str, args)], capture_output=True, text=True, check=False)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    from gnd.examples.literature.lineage_run import assemble

    top = tmp_path_factory.mktemp("li5")
    result = {}
    for name in ("development", "control", "cycle"):
        path = top / name
        assemble(EXAMPLE, MODEL, DATA / f"{name}-input.json", path)
        result[name] = path
    return result


def query(run, tmp_path, fact, pair):
    target = tmp_path / "target.json"
    target.write_bytes(canonical_json_bytes({"version": 1, "targets": [
        {"fact_type": fact, "tuple": [{"primitive": "String", "value": value} for value in pair]}]}))
    proof = tmp_path / "proof.json"
    proof.unlink(missing_ok=True)
    done = gnd("witness", MODEL, run / "composed.population.json", "--targets", target, "--composition",
               run / "composition.json", "--raw", "--out", proof)
    return done, proof


def test_named_development_paths(runs, tmp_path):
    from gnd.examples.literature.lineage_run import score

    result = score(MODEL, runs["development"], EXAMPLE / "answers/answer-key.json")
    assert result["counts"] == read(DATA / "cases.json")["development"]
    assert result["exit_code"] == 0
    statements = read(runs["development"] / "composed.population.json")["facts"]["assertion_statement"]
    assert any(r["predicate"] == "evaluated-as" and r["object"] == "Boltz-1 family" for r in statements)
    assert query(runs["development"], tmp_path, "lineage_ancestor", ["PoseX", "Boltz-1 family"])[0].returncode == 2


def test_only_eligible_relationships_supply_a_lineage_edge(runs, tmp_path):
    cases = read(DATA / "cases.json")
    run = runs["control"]
    statements = read(run / "composed.population.json")["facts"]["assertion_statement"]
    for pair in cases["non_chaining"]:
        assert any([r["actor"], r["object"]] == pair for r in statements)
    for pair in (["Adaptor A", "System P"], ["Tuned A", "System P"], ["Port A", "System P"]):
        assert query(run, tmp_path, "lineage_ancestor", pair)[0].returncode == 0
    assert query(run, tmp_path, "lineage_ancestor", ["Atlas", "Nimbus"])[0].returncode == 2
    for pair in cases["non_chaining"] + cases["blocked"]:
        assert query(run, tmp_path, "lineage_ancestor", pair)[0].returncode == cases["missing_exit"]


def test_qualified_transfer_and_transitive_missing_interface(runs, tmp_path):
    cases = read(DATA / "cases.json")
    run = runs["control"]
    assert query(run, tmp_path, "transfer_ancestor", cases["transfer_kept"])[0].returncode == 0
    for key in ("transfer_missing", "transfer_chain_missing"):
        assert query(run, tmp_path, "lineage_ancestor", cases[key])[0].returncode == 0
        assert query(run, tmp_path, "transfer_ancestor", cases[key])[0].returncode == cases["missing_exit"]


def test_proof_binds_contextual_claims_and_decision_lineage(runs, tmp_path):
    cases = read(DATA / "cases.json")
    run = runs["development"]
    record = run / "composition.json"
    population = run / "composed.population.json"
    answer, proof = query(run, tmp_path, "lineage_ancestor", ["WhAM", "bidirectional transformer"])
    assert answer.returncode == 0, answer.stdout + answer.stderr
    witness = read(proof)
    assert witness["version"] == 2
    contextual = [node for node in witness["nodes"]
                  if node["kind"] == "base" and node.get("fact_type") == "assertion_statement"]
    assert {s["source"] for n in contextual for s in n["sources"]} >= {"vampnet", "wham-whale"}
    decoded = read(record)
    source = contextual[0]["sources"][0]
    lineage = next(row for row in decoded["facts"] if source in row["sources"])
    assert all(next(row for row in decoded["facts"] if src in row["sources"])["decisions"]
               for node in contextual for src in node["sources"])
    # Modify the asserted source coordinate and the decision binding independently.
    assert gnd("replay", MODEL, population, proof, "--composition", record, "--raw", "--json").returncode == 0
    contextual[0]["sources"][0]["fact_index"] += 100
    altered = tmp_path / "changed-proof.json"
    altered.write_bytes(canonical_json_bytes(witness))
    rejected = gnd("replay", MODEL, population, altered, "--composition", record, "--raw", "--json")
    assert rejected.returncode == cases["replay_proof_exit"] and "proof-invalid" in rejected.stdout
    other = tmp_path / "changed-record.json"
    lineage["decisions"] = []
    other.write_bytes(canonical_json_bytes(decoded))
    stale = gnd("replay", MODEL, population, proof, "--composition", other, "--raw", "--json")
    assert stale.returncode == cases["replay_record_exit"] and "binding-stale" in stale.stdout
    rebound = gnd("check", MODEL, population, "--composition", other, "--sources", run / "sources",
                  "--format", "json")
    assert rebound.returncode == 3 and "differs from the record at facts" in rebound.stdout


def test_cycle_warning_and_reversed_relation(runs, tmp_path):
    run = runs["cycle"]
    original = read(run / "composed.population.json")
    assert len(original["facts"]["assertion_statement"]) == 2

    def check(subject, name):
        path = tmp_path / f"{name}.json"
        path.write_bytes(canonical_json_bytes(subject))
        result = gnd("check", MODEL, path, "--format", "json")
        return result, json.loads(result.stdout)

    a, b = "Clockwise", "Counterclockwise"
    ordinary = original["facts"]
    original["population"]["covers"].extend(
        ["lineage_step", "lineage_arc", "lineage_ancestor", "transfer_step", "transfer_ancestor"])
    for number, keep_cycle in enumerate((True, False)):
        width = 2 if keep_cycle else 1
        ordinary["assertion_statement"] = ordinary["assertion_statement"][:width]
        for fact in ("assertion_names_passage", "assertion_names_work"):
            ordinary[fact] = ordinary[fact][:width]
        arcs = [(a, b), (b, a)][:width]
        ordinary["lineage_step"] = [{"descendant": head, "ancestor": base, "assertion": f"cycle.p{i+1}"}
                                    for i, (head, base) in enumerate(arcs)]
        ordinary["lineage_arc"] = [{"descendant": head, "ancestor": base} for head, base in arcs]
        ordinary["lineage_ancestor"] = [{"descendant": head, "ancestor": base}
                                        for head, base in (arcs + ([(a, a), (b, b)] if keep_cycle else []))]
        result, report = check(original, f"control-{number}")
        warnings = [item for item in report["verdicts"] if item.get("verdict") == "warning"]
        assert result.returncode == 0, report
        assert bool(warnings) is keep_cycle
        assert len(ordinary["assertion_statement"]) == width

    ordinary["lineage_arc"] = [{"descendant": b, "ancestor": a}]
    result, report = check(original, "reversed")
    assert result.returncode == 1
    verdict = next(row for row in report["derivations"] if row["derivation_ref"] == "derivation:lineage_arc")
    assert verdict["verdict"] == "fail"
    assert {item["kind"] for item in verdict["findings"]} >= {"derived-extension-unsound"}


def test_invalid_annotation_and_changed_resolution_refuse(runs, tmp_path):
    import shutil

    from gnd.examples.literature.lineage_run import main

    annotation = tmp_path / "bad.json"
    annotation.write_bytes(b'{"sources":NaN}')
    out = tmp_path / "refused"
    assert main(["assemble", str(EXAMPLE), str(MODEL), str(annotation), str(out)]) == 3
    assert not out.exists()

    run = tmp_path / "stale"
    shutil.copytree(runs["development"], run)
    with (run / "sources/resolution.json").open("a") as stream:
        stream.write(" ")
    assert main(["score", str(MODEL), str(run), str(EXAMPLE / "answers/answer-key.json")]) == 3


def test_score_requires_the_admission_publication(runs, tmp_path):
    import shutil

    from gnd.examples.literature.lineage_run import main

    run = tmp_path / "missing-admission"
    shutil.copytree(runs["development"], run)
    (run / "admissions/wham-whale/admission.json").unlink()
    assert main(["score", str(MODEL), str(run), str(EXAMPLE / "answers/answer-key.json")]) == 3


def test_false_chain_exclusion_can_fail(tmp_path):
    from gnd.examples.literature.lineage_run import assemble, score

    doc = read(DATA / "development-input.json")
    changed = {"sbi-frontier.p2", "sensor-placement.p2"}
    for source in doc["sources"]:
        for statement in source["statements"]:
            if statement["passage"] in changed:
                statement["disposition"] = "supported"
    shared = "simulation-based inference"
    doc["decisions"].append({"decision": "same", "keys": [
        {"source": source, "value": shared} for source in ("sbi-frontier", "sensor-placement")]})
    path = tmp_path / "incorrectly-approved-input.json"
    path.write_bytes(canonical_json_bytes(doc))
    run = tmp_path / "mutated"
    assemble(EXAMPLE, MODEL, path, run)
    report = score(MODEL, run, EXAMPLE / "answers/answer-key.json")
    assert report["exit_code"] == 1
    assert report["counts"] == {"supported": [3, 3], "excluded": [4, 5]}
    assert {"id": "c08", "witness_exit": 0, "correct": False} in report["paths"]


def test_transfer_model_checks_the_assumption_separately(runs, tmp_path):
    population = read(runs["control"] / "composed.population.json")
    statement = next(row for row in population["facts"]["assertion_statement"] if row["actor"] == "Nimbus")
    assert statement["regime"] != "unspecified"
    statement["condition"] = "unspecified"
    subject = tmp_path / "model-layer-control.json"
    subject.write_bytes(canonical_json_bytes(population))
    target = tmp_path / "targets.json"
    for relation, expect in (("lineage_ancestor", 0), ("transfer_ancestor", 2)):
        target.write_bytes(canonical_json_bytes({"version": 1, "targets": [{
            "fact_type": relation, "tuple": [{"primitive": "String", "value": name} for name in ("Nimbus", "Atlas")],
        }]}))
        got = gnd("witness", MODEL, subject, "--targets", target, "--raw")
        assert got.returncode == expect, got.stdout + got.stderr


def test_model_regeneration_matches_the_path_policy(tmp_path):
    root = EXAMPLE.parents[3]
    generated = tmp_path / "lineage.orm.yaml"
    result = subprocess.run([sys.executable, str(root / "tools/build_literature_lineage_model.py"),
                             "--out", str(generated)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert generated.read_bytes() == MODEL.read_bytes()
    policy = read(DATA / "path-policy.json")
    assert set(policy["chainable"]).isdisjoint(policy["non_chaining"])
