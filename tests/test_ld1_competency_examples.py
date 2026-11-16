"""Check the literature depth example through its packaged entry point."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

EXPECTED = json.loads(
    (Path(__file__).parent / "fixtures" / "ld1-competency" / "expected.json").read_bytes()
)


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    output = tmp_path_factory.mktemp("ld1").resolve() / "out"
    run = subprocess.run(
        [sys.executable, "-m", "gnd.examples.literature.depth", "--out", str(output)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr
    return json.loads((output / "report.json").read_bytes())


@pytest.mark.parametrize("case", EXPECTED["questions"])
def test_competency_questions(report, case):
    assert report["format"] == "literature-depth/1"
    observed = report["cases"][case]["questions"]
    assert [
        (row["id"], row["status"], set(row["facts"])) for row in observed
    ] == [
        (question, status, set(facts)) for question, status, facts in EXPECTED["questions"][case]
    ]
    assert all(row["evidence"] for row in observed)
    if case == "dynamics":
        assert observed[0]["claim_kind"] == "reported-equation"


def test_experiment_comparisons(report):
    assert {row["id"]: [row["status"], row["fields"]] for row in report["comparisons"]} == EXPECTED["comparison"]


def test_three_quantity_probes_are_reported(report):
    assert [row["axis"] for row in report["quantities"]] == EXPECTED["quantities"]
    assert all(row["observed"] and type(row["opens_ld2"]) is bool for row in report["quantities"])


def test_synthetic_context_is_separate_and_optional(report):
    experiments = report["synthetic_experiments"]
    assert experiments["reference"]["baseline"] == "reference configuration"
    assert experiments["reference"]["uncertainty"] == "2 points"
    assert "conditions" not in experiments["missing-conditions"]
    assert all(row["origin"] == "synthetic" for row in report["comparisons"])
    assert report["cases"]["algorithms"]["relationships"]["subject_has_component"]
    assert report["cases"]["dynamics"]["relationships"]["subject_specializes"]
    assert all(case["binding"]["verification"] == case["binding"]["check"] == "accepted"
               for case in report["cases"].values())


@pytest.fixture
def case_inputs(tmp_path):
    import shutil

    from gnd.examples.literature.depth import FIXTURE

    path = tmp_path / "inputs"
    shutil.copytree(FIXTURE, path)
    return path, tmp_path / "out"


@pytest.mark.parametrize("mutation", ["citation", "span", "source", "fabricated-answer"])
def test_source_support_binding_refuses_tampering(case_inputs, monkeypatch, mutation):
    from gnd.examples.literature import depth

    inputs, output = case_inputs
    if mutation in {"citation", "span"}:
        path = inputs / "support.json"
        support = json.loads(path.read_bytes())
        row = support["dynamics"]["rows"][0]
        if mutation == "citation":
            row["primary"]["url"] = support["molecular"]["rows"][0]["primary"]["url"]
        else:
            row["span"][1] -= 1
            raw = json.dumps(support).encode()
            monkeypatch.setattr(depth, "SUPPORT_SHA", depth.sha256_hex(raw))
        path.write_text(json.dumps(support))
    elif mutation == "source":
        path = inputs / "dynamics.txt"
        path.write_text(path.read_text() + "\nUnreviewed source text.\n")
    else:
        path = inputs / "dynamics.facts.json"
        facts = json.loads(path.read_bytes())
        facts["equation"][0]["value"] = "Unreviewed replacement equation"
        path.write_text(json.dumps(facts))
    with pytest.raises(depth.ExampleError, match={
        "citation": "reviewed support.json binding differs",
        "span": "reviewed source span differs",
        "source": "reviewed source document binding differs",
        "fabricated-answer": "unreviewed facts",
    }[mutation]):
        depth.build(output, fixture=inputs)
    assert not output.exists()


@pytest.mark.parametrize("removed", ["assumptions", "cost_model"])
def test_bound_is_suppressed_without_each_qualification(case_inputs, removed):
    from gnd.examples.literature import depth

    inputs, _ = case_inputs
    cases = json.loads((inputs / "cases.json").read_bytes())
    support = json.loads((inputs / "support.json").read_bytes())
    facts = json.loads((inputs / "algorithms.facts.json").read_bytes())
    del facts[removed]
    rows = depth._question_rows(cases["algorithms"], support["algorithms"],
                                (inputs / "algorithms.txt").read_bytes(), facts)
    guarded = next(row for row in rows if row["id"] == "qualified-complexity")
    assert (guarded["status"], guarded["facts"], guarded["missing"]) == ("unknown", {}, [removed])


def test_label_change_preserves_identity_and_conflict_fails(case_inputs, report):
    from gnd.examples.literature import depth

    inputs, output = case_inputs
    source = inputs / "dynamics.facts.json"
    facts = json.loads(source.read_bytes())
    old = report["cases"]["dynamics"]
    facts["subject_label"][0]["label"] = "New public label"
    source.write_text(json.dumps(facts))
    changed = depth.build(output, fixture=inputs)["cases"]["dynamics"]
    assert changed["subject"] == old["subject"]
    assert changed["questions"] == old["questions"]
    assert changed["labels"][0]["label"] != old["labels"][0]["label"]
    population = output / "dynamics" / "population.json"
    payload = json.loads(population.read_bytes())
    payload["facts"]["subject_label"].append(old["labels"][0])
    population.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "-m", "gnd", "check", "root.orm.json", "population.json", "--format", "json"],
        cwd=population.parent, capture_output=True, check=False, timeout=20,
    )
    assert result.returncode == 1, result.stderr
    verdicts = json.loads(result.stdout)["verdicts"]
    assert any(row["constraint_type"] == "uniqueness" and row["verdict"] == "fail" for row in verdicts)


@pytest.mark.parametrize("raw", [b"[]", b'{"x": 1, "x": 2}', b'{"x": NaN}', b" " * (128 * 1024 + 1)])
def test_invalid_input_refuses_before_product_calls(case_inputs, monkeypatch, raw):
    from gnd.examples.literature import depth

    inputs, output = case_inputs
    (inputs / "cases.json").write_bytes(raw)
    output.mkdir()
    def unexpected(*_args):
        pytest.fail("the worked example called GND before authenticating inputs")

    monkeypatch.setattr(depth, "_command", unexpected)
    with pytest.raises((depth.ExampleError, depth.ArtifactError)):
        depth.build(output, fixture=inputs)
    assert list(output.iterdir()) == []


def test_quantity_observations_are_discriminating(report):
    by_axis = {row["axis"]: row for row in report["quantities"]}
    assert by_axis["dimensions"]["observed"]["matching_integer_spans"] == ["2 fs", "2 eV"]
    assert by_axis["dimensions"]["opens_ld2"]
    assert by_axis["percent-versus-points"]["observed"]["recognized_percentages"] == [40, 45]
    assert not by_axis["percent-versus-points"]["opens_ld2"]
    assert by_axis["exact-decimal-witness"]["observed"] == {
        "exit": 2, "reason": "fragment-unsupported", "checked_value": "0.002",
    }
    assert by_axis["exact-decimal-witness"]["opens_ld2"]


def test_fresh_run_is_deterministic_and_existing_output_is_preserved(tmp_path, report):
    from gnd.examples.literature import depth

    output = tmp_path / "independent"
    depth.build(output)
    report_path = output / "report.json"
    before = report_path.read_bytes()
    assert json.loads(before) == report
    assert depth.main(["--out", str(output)]) == 3
    assert report_path.read_bytes() == before


def test_comparison_shape_refuses_before_product_calls(case_inputs, monkeypatch):
    from gnd.examples.literature import depth

    inputs, output = case_inputs
    path = inputs / "comparison.json"
    fixture = json.loads(path.read_bytes())
    fixture["facts"]["experiment_score"][0].pop("score")
    path.write_text(json.dumps(fixture))

    def unexpected(*_args):
        pytest.fail("the worked example called GND before validating comparison inputs")

    monkeypatch.setattr(depth, "_command", unexpected)
    with pytest.raises(depth.ExampleError, match="invalid synthetic experiment field score"):
        depth.build(output, fixture=inputs)
    assert not output.exists()
