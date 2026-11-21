"""IR2 (include-root-routes): ``gnd flatten`` writes the flat model and its record.

The fixture is the packaged literature interop example; ``checking.orm.json``
is a temporal include root, which ``gnd extract`` refuses.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time

import pytest
from support.cli_runner import run_main

FLAT = "checking.orm.flat.orm.json"
RECORD = "checking.orm.flattening.json"
CHRONOLOGY = "vocabulary/chronology.orm.json"
POPULATION = "composed.population.json"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from gnd.examples.literature.interop import build

    out = tmp_path_factory.mktemp("ir2") / "interop"
    build(out)
    return out


@pytest.fixture
def case(built, tmp_path):
    root = tmp_path / "case"
    shutil.copytree(built, root)
    return root


def flatten(*args):
    result = run_main(["flatten", *map(str, args)])
    return result.returncode, (result.stdout + result.stderr).decode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def edit_include(root, mutate):
    doc = json.loads((root / CHRONOLOGY).read_bytes())
    mutate(doc)
    (root / CHRONOLOGY).write_text(json.dumps(doc))


def repin(root):
    doc = json.loads((root / "checking.orm.json").read_bytes())
    for entry in doc["includes"]:
        entry["sha256"] = _sha((root / entry["path"]).read_bytes())
    (root / "checking.orm.json").write_text(json.dumps(doc))


def expected(root):
    from gnd.model import load_model
    from gnd.model.flattening import flatten_model

    return flatten_model(load_model(root / "checking.orm.json"))


def test_T1_temporal_root_flattens(case, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    code, text = flatten(case / "checking.orm.json", "--out", out)
    assert code == 0, text
    flat = expected(case)
    assert (out / FLAT).read_bytes() == flat.model_bytes
    assert (out / RECORD).read_bytes() == flat.record_bytes
    record = json.loads(flat.record_bytes)
    assert record["format"] == "gnd-flattening/1"
    assert "includes[chronology]" in {o["origin"] for o in record["origins"]}
    ids = {c["id"] for c in json.loads(flat.model_bytes)["constraints"]}
    assert "publication_not_before_submission" in ids


def test_T2_check_parity_in_the_roots_directory(case):
    code, text = flatten(case / "checking.orm.json", "--out", case)
    assert code == 0, text

    def check(model):
        result = run_main(["check", str(case / model), str(case / POPULATION), "--format", "json"])
        return result.returncode, json.loads(result.stdout)["report"]["verdicts"]

    assert check("checking.orm.json") == check(FLAT)


def test_T3_model_without_includes_refuses(case, tmp_path):
    flatten(case / "checking.orm.json", "--out", case)
    code, text = flatten(case / FLAT, "--out", tmp_path)
    assert code == 3
    assert "flatten needs a model that declares includes" in text


def test_T4_unpinned_include_edit_refuses(case, tmp_path):
    with (case / CHRONOLOGY).open("ab") as handle:
        handle.write(b" ")
    code, text = flatten(case / "checking.orm.json", "--out", tmp_path)
    assert code == 3 and "include:hash-mismatch" in text
    assert not (tmp_path / FLAT).exists()


def test_T5_nested_include_refuses(case, tmp_path):
    literature = (case / "vocabulary/literature.orm.json").read_bytes()
    edit_include(case, lambda d: d.update(includes=[
        {"id": "nested", "path": "literature.orm.json", "sha256": _sha(literature)}]))
    repin(case)
    code, text = flatten(case / "checking.orm.json", "--out", tmp_path)
    assert code == 3 and "include:forbidden-section" in text


@pytest.mark.parametrize("present", [FLAT, RECORD])
def test_T6_existing_output_is_never_overwritten(case, tmp_path, present):
    out = tmp_path / "out"
    out.mkdir()
    (out / present).write_bytes(b"keep")
    code, text = flatten(case / "checking.orm.json", "--out", out)
    assert code == 11, text
    assert (out / present).read_bytes() == b"keep"
    assert sorted(p.name for p in out.iterdir()) == [present]


def test_T7_missing_model(tmp_path):
    code, _ = flatten(tmp_path / "absent.orm.json", "--out", tmp_path)
    assert code == 66


def test_T8_extract_names_flatten_for_a_temporal_include_root(case, tmp_path):
    result = run_main(["extract", str(case / "checking.orm.json"), "--out", str(tmp_path / "b")])
    assert result.returncode == 3
    assert b"gnd flatten" in result.stdout + result.stderr


def test_T10_json_digests(case, tmp_path):
    result = run_main(["flatten", str(case / "checking.orm.json"), "--out", str(tmp_path),
                       "--format", "json"])
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["command"] == "flatten"
    assert out["model"]["sha256"] == _sha((case / "checking.orm.json").read_bytes())
    assert out["flat_model"]["sha256"] == _sha((tmp_path / FLAT).read_bytes())
    assert out["record"]["sha256"] == _sha((tmp_path / RECORD).read_bytes())


def test_T11_elsewhere_notes_the_reference_coordinate(case, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    result = run_main(["flatten", str(case / "checking.orm.json"), "--out", str(out)])
    assert result.returncode == 0
    assert b"reference paths" in result.stderr
    check = run_main(["check", str(out / FLAT), str(case / POPULATION), "--format", "json"])
    assert check.returncode == 3


def test_T12_orphan_attachments_refuse(case, tmp_path):
    doc = json.loads((case / "checking.orm.json").read_bytes())
    del doc["includes"]
    doc["fact_type_constraints"] = [
        {"fact_type": "paper_names_parent_method", "constraints": [{"kind": "mandatory"}]}]
    (case / "checking.orm.json").write_text(json.dumps(doc))
    code, text = flatten(case / "checking.orm.json", "--out", tmp_path)
    assert code == 3 and "include:declaration" in text


def test_T13_large_include_within_bound(case, tmp_path):
    edit_include(case, lambda d: d["object_types"].extend(
        {"id": f"extra_{i}", "kind": "value", "name": f"Extra{i}", "primitive": "String"}
        for i in range(1000)))
    repin(case)
    started = time.monotonic()
    code, text = flatten(case / "checking.orm.json", "--out", tmp_path)
    assert code == 0, text
    assert time.monotonic() - started < 5


def test_T14_load_precedes_output_checks(case, tmp_path):
    (tmp_path / FLAT).write_bytes(b"keep")
    with (case / CHRONOLOGY).open("ab") as handle:
        handle.write(b" ")
    code, _ = flatten(case / "checking.orm.json", "--out", tmp_path)
    assert code == 3


def test_T15_help():
    result = run_main(["flatten", "--help"])
    assert result.returncode == 0
    assert b"--out" in result.stdout
