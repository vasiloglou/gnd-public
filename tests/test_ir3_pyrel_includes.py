"""IR3 (include-root-routes): ``gnd export pyrel`` exports an include root's flat model.

Fixtures: the packaged literature interop example (``extraction.orm.json``,
non-temporal; ``checking.orm.json``, temporal, both with two includes) and the
small two-file include root of ``tests/test_mc1_model_includes.py``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import time
from pathlib import Path

import pytest
from support.cli_runner import run_main
from test_mc1_model_includes import write_case

MODES = ("default", "duckdb", "lqp")
CHRONOLOGY = "vocabulary/chronology.orm.json"
GOLDENS = Path(__file__).parent / "fixtures/ir3"
CONSTANT_LINES = re.compile(r"^(FLATTENING_RECORD_SHA256|MODEL_INCLUDES|MODEL_NAME) = .*$\n", re.MULTILINE)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from gnd.examples.literature.interop import build

    out = tmp_path_factory.mktemp("ir3") / "interop"
    build(out)
    return out


@pytest.fixture
def case(built, tmp_path):
    root = tmp_path / "case"
    shutil.copytree(built, root)
    return root


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def export(model, out, mode="default"):
    argv = ["export", "pyrel", str(model), "--out", str(out)]
    if mode != "default":
        argv += ["--rules", mode]
    result = run_main(argv)
    return result.returncode, (result.stdout + result.stderr).decode()


def write_flat(root, name):
    from gnd.model import load_model
    from gnd.model.flattening import flatten_model

    flat = flatten_model(load_model(root / name))
    target = root / name.replace(".orm.json", ".orm.flat.orm.json")
    target.write_bytes(flat.model_bytes)
    return target, flat


def constants(program: str):
    found = {}
    for name in ("FLATTENING_RECORD_SHA256", "MODEL_INCLUDES"):
        match = re.search(rf"^{name} = (.*)$", program, re.MULTILINE)
        found[name] = None if match is None else ast.literal_eval(match[1])
    return found


def pins(root, name):
    return tuple((e["id"], e["path"], e["sha256"])
                 for e in json.loads((root / name).read_bytes())["includes"])


def repin(root, name):
    doc = json.loads((root / name).read_bytes())
    for entry in doc["includes"]:
        entry["sha256"] = _sha((root / entry["path"]).read_bytes())
    (root / name).write_text(json.dumps(doc))


def small_root(tmp_path):
    folder = tmp_path / "small"
    folder.mkdir()
    path, _, _ = write_case(folder)
    return path


# --- T1, T2, T3: the interop roots in each mode -----------------------------


def test_T1_default_export_of_the_extraction_root(case, tmp_path):
    code, text = export(case / "extraction.orm.json", tmp_path / "root.py")
    assert code == 0, text
    flat_path, _ = write_flat(case, "extraction.orm.json")
    code, text = export(flat_path, tmp_path / "flat.py")
    assert code == 0, text
    root_program = (tmp_path / "root.py").read_text()
    flat_program = (tmp_path / "flat.py").read_text()
    assert CONSTANT_LINES.sub("", root_program) == CONSTANT_LINES.sub("", flat_program)
    assert root_program != flat_program


def test_T2_default_export_of_the_temporal_root_refuses_as_temporal(case, tmp_path):
    code, text = export(case / "checking.orm.json", tmp_path / "out.py")
    assert code == 3
    assert "PyRel export does not support temporal models in Phase 1" in text
    assert "include:" not in text


def unchecked(program: str):
    """The rules a rules program lists as not checked, read from its syntax tree."""
    for node in ast.parse(program).body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == ["UNCHECKED"]:
            (argument,) = node.value.args
            return json.loads(ast.literal_eval(argument))
    raise AssertionError("the program has no UNCHECKED list")


@pytest.mark.parametrize("mode", ["duckdb", "lqp"])
@pytest.mark.parametrize("name", ["extraction.orm.json", "checking.orm.json"])
def test_T3_rules_modes_reach_the_flat_models_outcome(case, tmp_path, mode, name):
    """A rules mode gives an include root what it gives the root's flat model.

    At IR3 that outcome was a refusal, exit 3 naming the anchored rule
    ``paper_names_parent_method#0``. Since RP2 of pyrel-rules-coverage (6e04fe7f)
    a rules program lists an anchored rule as not checked and exits 0, so the
    shared outcome is now that listing."""
    code, text = export(case / name, tmp_path / "root.py", mode)
    flat_path, _ = write_flat(case, name)
    flat_code, flat_text = export(flat_path, tmp_path / "flat.py", mode)
    assert (code, flat_code) == (0, 0), (text, flat_text)
    root_program = (tmp_path / "root.py").read_text()
    flat_program = (tmp_path / "flat.py").read_text()
    assert [rule["id"] for rule in unchecked(root_program)] == ["paper_names_parent_method#0"]
    assert unchecked(root_program) == unchecked(flat_program)
    assert CONSTANT_LINES.sub("", root_program) == CONSTANT_LINES.sub("", flat_program)
    assert root_program != flat_program
    report = "1 rule(s) are not checked (listed in the program)"
    assert report in text and report in flat_text


# --- T4, T5: the program records the flattening -----------------------------


def test_T4_default_program_records_the_flattening(case, tmp_path):
    assert export(case / "extraction.orm.json", tmp_path / "out.py")[0] == 0
    _, flat = write_flat(case, "extraction.orm.json")
    found = constants((tmp_path / "out.py").read_text())
    assert found["FLATTENING_RECORD_SHA256"] == _sha(flat.record_bytes)
    assert found["MODEL_INCLUDES"] == pins(case, "extraction.orm.json")


@pytest.mark.parametrize("mode", ["duckdb", "lqp"])
def test_T4_rules_programs_record_the_flattening(tmp_path, mode):
    from gnd.model import load_model
    from gnd.model.flattening import flatten_model

    root = small_root(tmp_path)
    code, text = export(root, tmp_path / "out.py", mode)
    assert code == 0, text
    found = constants((tmp_path / "out.py").read_text())
    assert found["FLATTENING_RECORD_SHA256"] == _sha(flatten_model(load_model(root)).record_bytes)
    assert found["MODEL_INCLUDES"] == pins(root.parent, root.name)


def test_T5_a_repinned_include_changes_the_recorded_digest(case, tmp_path):
    assert export(case / "extraction.orm.json", tmp_path / "before.py")[0] == 0
    doc = json.loads((case / CHRONOLOGY).read_bytes())
    doc["object_types"].append({"id": "extra", "kind": "value", "name": "Extra", "primitive": "String"})
    (case / CHRONOLOGY).write_text(json.dumps(doc))
    repin(case, "extraction.orm.json")
    assert export(case / "extraction.orm.json", tmp_path / "after.py")[0] == 0
    before = constants((tmp_path / "before.py").read_text())
    after = constants((tmp_path / "after.py").read_text())
    assert before["FLATTENING_RECORD_SHA256"] != after["FLATTENING_RECORD_SHA256"]
    assert before["MODEL_INCLUDES"] != after["MODEL_INCLUDES"]


# --- T6: models without includes keep their exact program bytes -------------
#
# The goldens were produced by the base code at 68e426ca, with the case folder
# replaced by "<case>", and all three still matched at IR3 (6aacb928). The two
# rules programs were recorded again after the pyrel-rules-coverage milestone
# changed the program every model gets (RP2 6e04fe7f, RP1 1350db9a, RP3 33bd03db,
# close 825078c8): they are that close's bytes, and nothing since has changed
# them. The default program's golden is the original.


def _include_free_programs(case, tmp_path):
    extraction_flat, _ = write_flat(case, "extraction.orm.json")
    small_flat, _ = write_flat(small_root(tmp_path).parent, "project.orm.json")
    programs = {}
    for key, model, mode in (("default-extraction-flat", extraction_flat, "default"),
                             ("duckdb-small-flat", small_flat, "duckdb"),
                             ("lqp-small-flat", small_flat, "lqp")):
        out = tmp_path / f"{key}.py"
        code, text = export(model, out, mode)
        assert code == 0, text
        programs[key] = (out.read_text().replace(str(case), "<case>")
                         .replace(str(tmp_path), "<tmp>"))
    return programs


def test_T6_include_free_programs_are_byte_identical(case, tmp_path):
    for key, program in _include_free_programs(case, tmp_path).items():
        assert program == (GOLDENS / f"{key}.py.txt").read_text(), key


def test_T6_golden_negative_control(case, tmp_path):
    programs = _include_free_programs(case, tmp_path)
    changed = programs["default-extraction-flat"].replace("MODEL_NAME = ", "MODEL_NAME  = ", 1)
    assert changed != (GOLDENS / "default-extraction-flat.py.txt").read_text()


# --- T7: include refusals exit 3 in every mode ------------------------------


def _hostile(root, kind):
    doc = json.loads((root / "project.orm.json").read_bytes())
    if kind == "stale":
        (root / "vocab.orm.json").write_bytes((root / "vocab.orm.json").read_bytes() + b" ")
    elif kind == "nested":
        vocab = json.loads((root / "vocab.orm.json").read_bytes())
        vocab["includes"] = [{"id": "x", "path": "vocab.orm.json", "sha256": "0" * 64}]
        (root / "vocab.orm.json").write_text(json.dumps(vocab))
        doc["includes"][0]["sha256"] = _sha((root / "vocab.orm.json").read_bytes())
    elif kind == "not-a-list":
        doc["includes"] = {}
    elif kind == "escape":
        doc["includes"][0]["path"] = "../escape.orm.json"
    elif kind == "absent":
        doc["includes"][0]["path"] = "absent.orm.json"
    (root / "project.orm.json").write_text(json.dumps(doc))


HOSTILE = {"stale": "include:hash-mismatch", "nested": "include:forbidden-section",
           "not-a-list": "include:declaration", "escape": "include:path",
           "absent": "include:unreadable"}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("kind", sorted(HOSTILE))
def test_T7_include_refusals_exit_3(tmp_path, mode, kind):
    root = small_root(tmp_path)
    _hostile(root.parent, kind)
    code, text = export(root, tmp_path / "out.py", mode)
    assert code == 3, text
    assert HOSTILE[kind] in text
    assert not (tmp_path / "out.py").exists()


# --- T8, T9: the added layer ------------------------------------------------


def test_T8_flatten_for_export_within_bound(case):
    from gnd.export.include_roots import flatten_for_export

    doc = json.loads((case / CHRONOLOGY).read_bytes())
    doc["object_types"].extend({"id": f"extra_{i}", "kind": "value", "name": f"Extra{i}",
                                "primitive": "String"} for i in range(1000))
    (case / CHRONOLOGY).write_text(json.dumps(doc))
    repin(case, "checking.orm.json")
    raw = (case / "checking.orm.json").read_bytes()
    started = time.monotonic()
    flat = flatten_for_export(case / "checking.orm.json", raw)
    assert time.monotonic() - started < 5
    assert len(json.loads(flat.model_bytes)["object_types"]) > 1000


def test_T9_include_free_model_takes_the_one_read_path(case, monkeypatch):
    import gnd.model
    from gnd.export.include_roots import flatten_for_export

    flat_path, _ = write_flat(case, "extraction.orm.json")
    monkeypatch.setattr(gnd.model, "load_model", lambda *a, **k: pytest.fail("loader called"))
    assert flatten_for_export(flat_path, flat_path.read_bytes()) is None


# --- Phase review r1 regression ---------------------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_F1_unencodable_include_path_exits_3_not_70(tmp_path, mode):
    root = tmp_path / "root.orm.json"
    root.write_text(json.dumps({"version": 5, "includes": [
        {"id": "v", "path": "bad\ud800", "sha256": "0" * 64}]}))
    code, text = export(root, tmp_path / "out.py", mode)
    assert code == 3, text
    assert not (tmp_path / "out.py").exists()


@pytest.mark.parametrize("mode,prefix", [("default", "invalid model: "),
                                         ("duckdb", "cannot write the rules program: "),
                                         ("lqp", "cannot write the rules program: ")])
def test_include_refusal_message_has_one_prefix(tmp_path, mode, prefix):
    root = small_root(tmp_path)
    _hostile(root.parent, "stale")
    code, text = export(root, tmp_path / "out.py", mode)
    assert code == 3
    assert text.strip() == prefix + "include:hash-mismatch"
