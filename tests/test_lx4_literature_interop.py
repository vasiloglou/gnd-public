"""LX4 integrated extraction, rebind, checking, fidelity and optional advice."""

import hashlib
import json
import shutil
import subprocess
import sys
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
    proof = read(run / "witness.json")
    assert proof["version"] == 4
    assert {node["origin"]["kind"] for node in proof["nodes"] if node["kind"] == "base"} == {
        "candidate", "reference",
    }
    assert read(run / "replay.json")["exit_code"] == 0
    assert read(run / "fidelity.json")["cases"]["ran"] == 2
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


def test_rebind_is_rederived_before_check_or_advice(example, tmp_path, monkeypatch):
    interop, good = example
    bad = tmp_path.resolve() / "forged-rebind"
    shutil.copytree(good, bad)
    member = "sources/survey/rebind.json"
    changed = read(bad / member)
    changed["document_sha256"] = "0" * 64
    write(bad / member, changed)
    manifest = read(bad / "interop.json")
    manifest["sha256"][member] = sha(bad / member)
    write(bad / "interop.json", manifest)

    def unreachable(*_args):
        pytest.fail("semantic checking or advice ran before rebind validation")

    monkeypatch.setattr(interop, "_check", unreachable)
    monkeypatch.setattr(interop, "_advice", unreachable)
    assert interop.main(["verify", str(bad)]) == 3


def test_report_digest_cannot_replace_advice_rederivation(example, tmp_path):
    interop, good = example
    bad = tmp_path.resolve() / "forged-advice"
    shutil.copytree(good, bad)
    report = read(bad / "dates.json")
    row = next(edge for edge in report["edges"] if edge["id"] == "pinn")
    row["ancestor_date"] = 2019
    write(bad / "dates.json", report)
    manifest = read(bad / "interop.json")
    manifest["sha256"]["dates.json"] = sha(bad / "dates.json")
    write(bad / "interop.json", manifest)
    assert interop.main(["verify", str(bad)]) == 3


def test_fidelity_rechecks_re_pinned_flat_artifact(example, tmp_path, capsys):
    _, good = example
    bad = tmp_path.resolve() / "forged-fidelity-bundle"
    shutil.copytree(good, bad)
    index_path = bad / "artifacts/extraction.orm.artifacts.json"
    index = read(index_path)
    file_name = index["flattening"]["flat_model"]
    flat = index_path.with_name(file_name)
    flat.write_bytes(flat.read_bytes() + b" ")
    index["artifacts"][file_name]["sha256"] = sha(flat)
    write(index_path, index)
    assert main(["fidelity", str(bad / "extraction.orm.json"), "--cases", str(bad / "sources"),
                 "--artifacts", str(bad / "artifacts"), "--format", "json"]) == 3
    assert "flat model does not match" in capsys.readouterr().out


def test_fidelity_failure_cannot_be_pinned_as_a_verified_run(example, tmp_path):
    interop, good = example
    bad = tmp_path.resolve() / "unscored-case"
    shutil.copytree(good, bad)
    member = "sources/survey/document.manifest.json"
    write(bad / member, {})
    report = interop._stage(bad, "fidelity", "extraction.orm.json", "--cases", "sources",
                            "--artifacts", "artifacts", "--format", "json")
    assert json.loads(report)["cases"]["failed"] == 1
    (bad / "fidelity.json").write_bytes(report)
    manifest = read(bad / "interop.json")
    for name in (member, "fidelity.json"):
        manifest["sha256"][name] = sha(bad / name)
    write(bad / "interop.json", manifest)
    assert interop.main(["verify", str(bad)]) == 3


def test_verified_proof_must_name_the_fixture_targets(example, tmp_path, capsys):
    interop, good = example
    bad = tmp_path.resolve() / "alternate-proof"
    shutil.copytree(good, bad)
    alternate = read(bad / "targets.json")
    alternate["targets"].pop()
    write(bad / "other-target.json", alternate)
    (bad / "witness.json").unlink()
    interop._stage(bad, "witness", "checking.orm.json", "composed.population.json",
                   "--targets", "other-target.json", "--composition", "composition.json",
                   "--raw", "--out", "witness.json")
    (bad / "replay.json").write_bytes(interop._replay(bad))
    recorded = read(bad / "interop.json")
    for name in ("witness.json", "replay.json"):
        recorded["sha256"][name] = sha(bad / name)
    write(bad / "interop.json", recorded)
    assert interop.main(["verify", str(bad)]) == 3
    assert "witness targets differ" in capsys.readouterr().err


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


def test_temporal_constraint_distinguishes_checking_model(example, tmp_path, capsys, monkeypatch):
    interop, good = example
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
    for name in EXPECTED["sources"]:
        for leaf, content in interop.rebind(bad, name).items():
            (bad / "sources" / name / leaf).write_bytes(content)
        assert read(bad / "sources" / name / "rebind.json")["checking_root_sha256"] == sha(model)
    out, record = bad / "control.population.json", bad / "control.record.json"
    assert main(["compose", str(model), str(bad / "sources"), "--out", str(out), "--record", str(record)]) == 0
    capsys.readouterr()
    assert main(["check", str(model), str(out), "--composition", str(record),
                 "--sources", str(bad / "sources"), "--format", "json"]) == 1
    verdicts = json.loads(capsys.readouterr().out)["report"]["verdicts"]
    assert any(row["constraint_type"] == "guarded" and row["verdict"] == "fail" for row in verdicts)
    assert main(["verify", str(model), str(bad / "sources/survey/extracted.population.json"),
                 "--artifacts", str(bad / "artifacts"), "--format", "json"]) == 3
    wrong_root = json.loads(capsys.readouterr().out)
    assert wrong_root["issues"][0]["rule_id"] == "extraction:binding-mismatch"
    assert "checking.orm.artifacts.json" in wrong_root["extraction"]["reason"]

    # Exercise the example verifier with this independently valid test fixture,
    # so its exact fixture-root check passes and the stale source is decisive.
    fixture = tmp_path / "fixture"
    shutil.copytree(interop.FIXTURE, fixture)
    shutil.copyfile(model, fixture / model.name)
    monkeypatch.setattr(interop, "FIXTURE", fixture)
    member = "sources/survey/rebind.json"
    rebind = read(bad / member)
    rebind["checking_root_sha256"] = sha(checking)
    write(bad / member, rebind)
    write(bad / "interop.json", interop._manifest(bad, EXPECTED["sources"], dates=True))

    def unreachable(*_args):
        pytest.fail("check or advice ran with a stale temporal rebind")

    monkeypatch.setattr(interop, "_check", unreachable)
    monkeypatch.setattr(interop, "_advice", unreachable)
    assert interop.main(["verify", str(bad)]) == 3
    assert "rebind differs at survey/rebind.json" in capsys.readouterr().err


@pytest.mark.parametrize("kind", ["extraction", "rendering", "verbalization", "unexpected-report"])
def test_repinning_cannot_make_forged_handoff_evidence_valid(example, tmp_path, kind):
    interop, good = example
    bad = tmp_path.resolve() / "forged-handoff"
    shutil.copytree(good, bad)
    sources = bad / "sources" / "survey"
    if kind == "extraction":
        path = sources / "extracted.population.extraction.json"
        value = read(path)
        value.update(executing_model="forged", skill_version="99")
        write(path, value)
        (sources / "rebind.json").write_bytes(interop.rebind(bad, "survey")["rebind.json"])
    elif kind == "rendering":
        path = sources / "document.manifest.json"
        value = read(path)
        value.update(executing_model="forged", renderer_skill_version="99")
        write(path, value)
    elif kind == "verbalization":
        path = bad / "artifacts/extraction.orm.verbalization.txt"
        path.write_text("Forged extraction instructions.\n")
    else:
        path = bad / "dates.json"
        value = read(path)
        value["counts"]["advisory"] = 0
        write(path, value)
    write(bad / "interop.json", interop._manifest(bad, EXPECTED["sources"], dates=kind != "unexpected-report"))
    assert interop.main(["verify", str(bad)]) == 3


def test_layout_measures_copies_of_all_original_artifacts(example, tmp_path):
    interop, good = example
    copied = tmp_path.resolve() / "copied"
    shutil.copytree(good, copied)
    survey = copied / "sources" / "survey"
    shutil.copyfile(survey / "extracted.population.json", survey / "extra-population.json")
    shutil.copyfile(survey / "extracted.population.extraction.json", survey / "extra-sidecar.json")
    layout = interop._manifest(copied, EXPECTED["sources"], dates=True)["layout"]
    assert layout["additional_copies"] == {"document": 2, "extraction_population": 1, "extraction_sidecar": 1}


def test_missing_work_link_is_unresolved():
    from gnd.examples.literature import interop

    candidate = {
        "schema": "literature-candidate-edges/1", "edges": [{
            "id": "unlinked", "relation": "extends",
            "descendant_work": None, "ancestor_work": EXPECTED["pinn"][0],
        }],
    }
    report = interop.advise(canonical_json_bytes(candidate),
                            (interop.FIXTURE / "publication-dates.json").read_bytes(),
                            interop.POLICY.read_bytes())
    edge = report["edges"][0]
    assert edge["outcome"] == "unresolved"
    assert edge["reason"] == "missing-work-link"
    assert edge["descendant_work"] is None


@pytest.mark.parametrize(("filename", "diagnostic"), [
    ("extraction.orm.json", "fixture input differs at extraction.orm.json"),
    ("checking.orm.json", "fixture input differs at checking.orm.json"),
    ("vocabulary/literature.orm.json", "fixture input differs at vocabulary/literature.orm.json"),
    ("reference/catalog.json", "fixture input differs at reference/catalog.json"),
    ("publication-dates.json", "fixture input differs at publication-dates.json"),
    ("artifacts/extraction.orm.artifacts.json", "extraction artifact differs at extraction.orm.artifacts.json"),
])
def test_repinned_input_still_refuses_before_semantic_stages(
    example, tmp_path, capsys, monkeypatch, filename, diagnostic,
):
    interop, good = example
    bad = tmp_path.resolve() / "repinned-input"
    shutil.copytree(good, bad)
    path = bad / filename
    if filename == "publication-dates.json":
        dates = read(path)
        dates["dates"][0]["role"] = "preprint"
        write(path, dates)
    else:
        path.write_bytes(path.read_bytes() + b" ")
    write(bad / "interop.json", interop._manifest(bad, EXPECTED["sources"], dates=True))

    def unreachable(*_args):
        pytest.fail("semantic work started on a re-pinned input")

    monkeypatch.setattr(interop, "_check", unreachable)
    monkeypatch.setattr(interop, "_advice", unreachable)
    assert interop.main(["verify", str(bad)]) == 3
    assert diagnostic in capsys.readouterr().err


def test_repinned_composition_cannot_replace_source_rederivation(example, tmp_path, capsys, monkeypatch):
    interop, good = example
    bad = tmp_path.resolve() / "repinned-composition"
    shutil.copytree(good, bad)
    path = bad / "composition.json"
    record = read(path)
    record["facts"][0]["sources"][0]["fact_index"] += 1
    write(path, record)
    write(bad / "interop.json", interop._manifest(bad, EXPECTED["sources"], dates=True))

    def unreachable(*_args):
        pytest.fail("proof replay started before composition verification")

    monkeypatch.setattr(interop, "_replay", unreachable)
    monkeypatch.setattr(interop, "_advice", unreachable)
    assert interop.main(["verify", str(bad)]) == 3
    assert "check exited 3" in capsys.readouterr().err
    direct = subprocess.run(
        [sys.executable, "-m", "gnd", "check", "checking.orm.json", "composed.population.json",
         "--composition", "composition.json", "--sources", "sources", "--format", "json"],
        cwd=bad, capture_output=True, text=True, check=False, timeout=30,
    )
    assert direct.returncode == 3
    assert "re-derived composition differs from the record at facts" in direct.stdout
