"""LX4 integrated extraction, rebind, checking, fidelity and optional advice."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.cli import main

EXPECTED = json.loads((Path(__file__).parent / "fixtures/lx4-literature-interop/expected.json").read_bytes())


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_bytes(canonical_json_bytes(value))


@pytest.fixture(scope="module")
def example(tmp_path_factory):
    try:
        from gnd.examples.literature import interop
    except ImportError:
        pytest.fail("the integrated literature example must expose its public run and verify commands")
    directory = tmp_path_factory.mktemp("lx4").resolve() / "run"
    assert interop.main(["run", "--out", str(directory), "--dates"]) == 0
    return interop, directory


def test_public_integration_checks_every_stage(example):
    interop, run = example
    assert interop.main(["verify", str(run)]) == 0
    manifest = read(run / "interop.json")
    assert manifest["schema"] == EXPECTED["manifest_schema"]
    assert manifest["layout"]["additional_copies"] == EXPECTED["extra_copies"]
    assert list(manifest["source_order"]) == EXPECTED["sources"]
    for name in EXPECTED["sources"]:
        folder = run / "sources" / name
        rebind = read(folder / "rebind.json")
        assert rebind["schema"] == EXPECTED["rebind_schema"]
        assert len(rebind["includes"]) == 2
        assert len(rebind["references"]) == 1
        assert rebind["extraction_root_sha256"] != rebind["checking_root_sha256"]
        assert rebind["document_sha256"] == sha(folder / "document.md") == sha(folder / "document.txt")
        assert read(folder / "extracted.population.json")["population"]["model_id"] != (
            read(folder / "population.json")["population"]["model_id"]
        )
        assert rebind["rebound_population_sha256"] == sha(folder / "population.json")
    report = read(run / "check.json")
    assert report["exit_code"] == 0
    assert any(row["constraint_type"] == "guarded" and row["verdict"] == "pass"
               for row in report["report"]["verdicts"])
    assert read(run / "witness.json")["version"] == 4
    assert read(run / "replay.json")["exit_code"] == 0
    assert read(run / "fidelity.json")["case_census"]["counts"]["ran"] == 2
    composition = read(run / "composition.json")
    assert composition["schema"] == "gnd-composition/2"
    assert all(row["decisions"] == [0] for row in composition["facts"]
               if row["fact_type"] == "paper_names_parent_method")


def test_advisory_is_optional_and_pinn_stays_a_candidate(example, tmp_path):
    interop, run = example
    report = read(run / "dates.json")
    assert report["schema"] == EXPECTED["dates_schema"]
    assert report["counts"] == EXPECTED["counts"]
    row = next(row for row in report["edges"] if row["outcome"] == "advisory")
    assert [row["descendant_work"], row["ancestor_work"]] == EXPECTED["pinn"]
    assert [row["descendant_date"], row["ancestor_date"], row["role"]] == [2019, 2021, "publication"]
    unresolved = {row["reason"] for row in report["edges"] if row["outcome"] == "unresolved"}
    assert unresolved == {"unknown-work", "conflicting-date", "missing-date", "mixed-precision", "publication-date-missing"}
    assert "non-chaining" not in {row["id"] for row in report["edges"]}
    composed = json.dumps(read(run / "composed.population.json"))
    assert "Bayesian PINNs" not in composed
    plain = tmp_path.resolve() / "plain"
    assert interop.main(["run", "--out", str(plain)]) == 0
    assert not (plain / "dates.json").exists()
    for name in ("composition.json", "check.json", "witness.json", "replay.json"):
        assert (plain / name).read_bytes() == (run / name).read_bytes()
    out = tmp_path / "same-advice.json"
    assert interop.main(["dates", str(plain), "--out", str(out)]) == 0
    assert out.read_bytes() == (run / "dates.json").read_bytes()


@pytest.mark.parametrize("filename", [
    "sources/survey/rebind.json",
    "extraction.orm.json",
    "checking.orm.json",
    "vocabulary/literature.orm.json",
    "artifacts/extraction.orm.artifacts.json",
    "sources/survey/document.md",
    "sources/survey/extracted.population.json",
    "sources/survey/extracted.population.extraction.json",
    "sources/survey/extracted.population.json.anchors.json",
    "sources/survey/population.json",
    "sources/survey/population.json.anchors.json",
    "reference/catalog.json",
    "sources/resolution.json",
    "composition.json",
    "composed.population.json",
    "witness.json",
    "candidate-edges.json",
    "publication-dates.json",
])
def test_stale_stage_evidence_refuses(example, tmp_path, filename):
    interop, good = example
    bad = tmp_path.resolve() / "stale"
    shutil.copytree(good, bad)
    path = bad / filename
    path.write_bytes(path.read_bytes() + b" ")
    assert interop.main(["verify", str(bad)]) == 3


def test_rebind_refuses_a_valid_root_with_different_pins(example, tmp_path):
    interop, good = example
    bad = tmp_path.resolve() / "alternate"
    shutil.copytree(good, bad)
    checking = bad / "checking.orm.json"
    root = read(checking)
    vocab = bad / "vocabulary/literature.orm.json"
    alternate = vocab.with_name("alternate.orm.json")
    alternate.write_bytes(vocab.read_bytes() + b" ")
    root["includes"][0].update(path="vocabulary/alternate.orm.json", sha256=sha(alternate))
    write(checking, root)
    from gnd.model import load_model

    assert load_model(checking)._included
    with pytest.raises(ValueError, match="root vocabulary pins differ"):
        interop.rebind(bad, "survey")


def test_rebind_refuses_a_valid_root_with_a_different_catalog(example, tmp_path):
    interop, good = example
    bad = tmp_path.resolve() / "alternate"
    shutil.copytree(good, bad)
    checking = bad / "checking.orm.json"
    root = read(checking)
    catalog = bad / "reference/catalog.json"
    alternate = catalog.with_name("alternate.json")
    alternate.write_bytes(catalog.read_bytes() + b" ")
    root["reference_populations"][0].update(path="reference/alternate.json", sha256=sha(alternate))
    write(checking, root)
    from gnd.model import load_model

    assert load_model(checking)._references
    with pytest.raises(ValueError, match="root catalog bindings differ"):
        interop.rebind(bad, "survey")


def test_temporal_constraint_distinguishes_checking_model(example, tmp_path, capsys):
    _, good = example
    checking = good / "checking.orm.json"
    assert main(["extract", str(checking), "--out", str(tmp_path / "refused")]) == 3
    assert "temporal:consumer-unsupported" in capsys.readouterr().out
    bad = tmp_path.resolve() / "chronology"
    shutil.copytree(good, bad)
    model = bad / checking.name
    root = read(model)
    temporal = next(c for c in root["constraints"] if c["type"] == "guarded")
    temporal["consequent"]["comparison"]["left"]["args"][1]["duration_days"] = 3650
    write(model, root)
    out, record = bad / "control.population.json", bad / "control.record.json"
    assert main(["compose", str(model), str(bad / "sources"), "--out", str(out), "--record", str(record)]) == 0
    capsys.readouterr()
    assert main(["check", str(model), str(out), "--composition", str(record),
                 "--sources", str(bad / "sources"), "--format", "json"]) == 1
    verdicts = json.loads(capsys.readouterr().out)["report"]["verdicts"]
    assert any(row["constraint_type"] == "guarded" and row["verdict"] == "fail" for row in verdicts)
    assert main(["verify", str(model), str(bad / "sources/survey/extracted.population.json"),
                 "--artifacts", str(bad / "artifacts")]) == 3
