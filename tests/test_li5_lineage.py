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
    assert lineage["decisions"]
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
    assert any(row["verdict"] == "fail" for row in report["derivations"])


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
