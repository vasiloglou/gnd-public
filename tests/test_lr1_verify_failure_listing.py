"""LR1: the documented steps list why `gnd verify` fails a source.

The steps live in ``docs/guides/documents.md``, "Reading a failed verification".
``listing`` below is the page's own ``failed`` function, read out of the page's
runnable block by the tutorial runner's block reader and ``ast``, so every case
exercises the documented code. Every case runs the real CLI in a subprocess,
with ``GND_DISCLOSURE`` removed unless the case sets it.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

from gnd.redaction import INSTANCE_DETAIL

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guides" / "documents.md"
SCHEMA = ROOT / "src" / "gnd" / "report.schema.json"
SKELETON = ROOT / "tests" / "fixtures" / "skeleton"
EXAMPLE = files("gnd").joinpath("examples", "literature")

# The field names the documented steps use, by the level they sit at. The page's
# code reads all of them but `message`, which the prose names and the code does not print.
REPORT_FIELDS = ("verdicts", "derivations", "outcome")
VERDICT_FIELDS = ("verdict", "modality", "constraint_ref", "constraint_type", "message", "offending_facts")
DERIVATION_FIELDS = ("verdict", "derivation_ref", "findings")
PROSE_ONLY = {"message"}

# Default `gnd verify` output at the phase base (11a7ebf7), staged as `staged` does,
# run from the staged folder with relative paths (LR1-C5, R0.1).
BASE_DIGESTS = {
    ("reported-conflict", "text"): "14abf8f84fdb624c5489e6ac265399f3d9246fdd310999469cc1362d0dff9c4b",
    ("reported-conflict", "json"): "54f103b14b8e7834c6702df285580251c0a45bec834266e53948fdbd0ac47ca5",
    ("broad", "text"): "0114303b483a0f2104c77b80a9d5b10ca76a10fa5dcf915ac6ad4b3f065e0ce5",
    ("broad", "json"): "06245aceda3e535708f28fb134a490be2541e97396959955deba7e223e0fadaf",
}


def _page_block() -> ast.Module:
    spec = importlib.util.spec_from_file_location("run_tutorials", ROOT / "tools" / "run_tutorials.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    (block,) = [code for language, _, code, _ in runner.parsed_blocks(GUIDE) if language == "python"]
    return ast.parse(block)


def _page_failed():
    module = _page_block()
    (function,) = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "failed"]
    namespace: dict = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(GUIDE), "exec"), namespace)  # noqa: S102 -- the repository page's one function only
    return namespace["failed"]


FAILED = _page_failed()


def listing(report: dict) -> list[dict]:
    """The page's documented steps 1 and 3, as its own code applies them."""
    constraints, derivations = FAILED(report)
    return [*constraints, *derivations]


def _keys_read(module: ast.Module) -> set[str]:
    """Every string key the page's code reads with a subscript."""
    return {node.slice.value for node in ast.walk(module)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)}


def _env(disclosure: str | None = None) -> dict:
    env = {key: value for key, value in os.environ.items() if key != "GND_DISCLOSURE"}
    if disclosure is not None:
        env["GND_DISCLOSURE"] = disclosure
    return env


def _gnd(cwd: Path, *args: str, disclosure: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "gnd", *args], cwd=cwd, env=_env(disclosure),
                          capture_output=True, check=False)


def _verify_json(cwd: Path, model: str, population: str, *extra: str,
                 disclosure: str | None = None) -> tuple[dict, int]:
    done = _gnd(cwd, "verify", model, population, "--no-extraction", "--format", "json", *extra,
                disclosure=disclosure)
    return json.loads(done.stdout), done.returncode


@pytest.fixture(scope="module")
def staged(tmp_path_factory) -> Path:
    """The packaged reading run, with the model and its included vocabulary beside it."""
    root = tmp_path_factory.mktemp("lr1")
    subprocess.run([sys.executable, "-m", "gnd.examples.literature.reading", "run", "--out", "run"],
                   cwd=root, env=_env(), capture_output=True, check=True)
    run = root / "run"
    for part, name in (("reading_fixture", "reading.orm.json"), ("depth_fixture", "vocabulary.orm.json")):
        shutil.copyfile(EXAMPLE.joinpath(part, name), run / name)
    return run


def test_t1_reported_conflict_lists_one_constraint_and_its_rows(staged: Path) -> None:
    report, code = _verify_json(staged, "reading.orm.json", "reported-conflict.population.json")
    assert code == 1 and report["outcome"] == "violated"
    (entry,) = listing(report)
    assert entry["constraint_ref"] == "fact_types[subject_label].constraints[0]"
    assert entry["constraint_type"] == "uniqueness"
    rows = entry["offending_facts"]
    assert len(rows) == 2
    assert rows[0]["subject"] == rows[1]["subject"] and rows[0]["label"] != rows[1]["label"]
    vocabulary = json.loads((staged / "vocabulary.orm.json").read_text(encoding="utf-8"))
    (fact_type,) = [ft for ft in vocabulary["fact_types"] if ft["id"] == "subject_label"]
    assert fact_type["constraints"][0]["id"] == "subject_has_one_label"


def test_t2_broad_population_lists_nothing(staged: Path) -> None:
    report, code = _verify_json(staged, "reading.orm.json", "broad.population.json")
    assert code == 0 and listing(report) == []


def test_t3_every_field_the_steps_use_is_in_the_schema_and_the_report(staged: Path) -> None:
    page = GUIDE.read_text(encoding="utf-8")
    listed = {*REPORT_FIELDS, *VERDICT_FIELDS, *DERIVATION_FIELDS}
    read = _keys_read(_page_block()) - {"facts"}
    assert read == listed - PROSE_ONLY, read ^ (listed - PROSE_ONLY)
    defs = json.loads(SCHEMA.read_text(encoding="utf-8"))["$defs"]
    levels = (
        (REPORT_FIELDS, defs["legacy_reference_report"]["properties"]),
        (VERDICT_FIELDS, defs["verdict"]["properties"]),
        (DERIVATION_FIELDS, defs["derivation_verdict"]["properties"]),
    )
    for names, properties in levels:
        for name in names:
            assert f"`{name}`" in page, name
            assert name in properties, name
    report, _ = _verify_json(staged, "reading.orm.json", "reported-conflict.population.json")
    assert set(REPORT_FIELDS) <= report.keys()
    assert set(VERDICT_FIELDS) <= listing(report)[0].keys()
    derivation = _derivation_failure_report(staged.parent / "t3-derivation")[0]
    assert set(DERIVATION_FIELDS) <= listing(derivation)[0].keys()


def test_t4_deontic_only_violation_is_a_warning_and_not_listed(tmp_path: Path) -> None:
    population = {
        "population": {"model": "model.orm.yaml", "source": "agent-output",
                       "covers": ["movie_has_title", "movie_released_in_year", "movie_sequel_of_movie"]},
        "instances": {"movie": [1, 2]},
        "facts": {
            "movie_has_title": [{"movie": 1, "title": "The Departed"}, {"movie": 2, "title": "Infernal Affairs"}],
            "movie_released_in_year": [{"movie": 1, "year": 1520}, {"movie": 2, "year": 2002}],
            "movie_sequel_of_movie": [{"sequel": 1, "original": 2}],
        },
    }
    shutil.copyfile(SKELETON / "model.orm.yaml", tmp_path / "model.orm.yaml")
    (tmp_path / "pop.json").write_text(json.dumps(population), encoding="utf-8")
    report, code = _verify_json(tmp_path, "model.orm.yaml", "pop.json")
    assert code == 0 and listing(report) == []
    warnings = [v for v in report["verdicts"] if v["verdict"] == "warning"]
    assert len(warnings) == 1 and warnings[0]["modality"] == "deontic"


def _redacting_copy(staged: Path, folder: Path) -> Path:
    folder.mkdir()
    vocabulary = json.loads((staged / "vocabulary.orm.json").read_text(encoding="utf-8"))
    (fact_type,) = [ft for ft in vocabulary["fact_types"] if ft["id"] == "subject_label"]
    fact_type["redact"] = True
    raw = json.dumps(vocabulary, indent=2).encode("utf-8")
    (folder / "vocabulary.orm.json").write_bytes(raw)
    model = json.loads((staged / "reading.orm.json").read_text(encoding="utf-8"))
    (include,) = [row for row in model["includes"] if row["path"] == "vocabulary.orm.json"]
    include["sha256"] = hashlib.sha256(raw).hexdigest()
    (folder / "reading.orm.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    shutil.copyfile(staged / "reported-conflict.population.json", folder / "pop.json")
    return folder


def test_t5_redacting_model_lists_the_constraint_with_markers(staged: Path, tmp_path: Path) -> None:
    folder = _redacting_copy(staged, tmp_path / "redacting")
    labels = {row["label"] for row in listing(_verify_json(staged, "reading.orm.json",
                                                           "reported-conflict.population.json")[0])[0]["offending_facts"]}
    report, code = _verify_json(folder, "reading.orm.json", "pop.json")
    assert code == 1
    (entry,) = listing(report)
    assert entry["constraint_ref"] == "fact_types[subject_label].constraints[0]"
    assert entry["message"] == INSTANCE_DETAIL
    (marker,) = entry["offending_facts"]
    assert marker["redacted"] is True
    assert marker["roles"] and all(role.startswith("subject_label.") for role in marker["roles"])
    payload = json.dumps(report)
    assert not any(label in payload for label in labels)
    for extra, disclosure in ((("--unredacted",), None), ((), "internal")):
        shown, code = _verify_json(folder, "reading.orm.json", "pop.json", *extra, disclosure=disclosure)
        assert code == 1
        assert {row["label"] for row in listing(shown)[0]["offending_facts"]} == labels


@pytest.mark.parametrize(("population", "fmt"), sorted(BASE_DIGESTS))
def test_t6_default_verify_output_is_unchanged(staged: Path, population: str, fmt: str) -> None:
    done = _gnd(staged, "verify", "reading.orm.json", f"{population}.population.json", "--no-extraction",
                "--format", fmt)
    assert hashlib.sha256(done.stdout).hexdigest() == BASE_DIGESTS[(population, fmt)]


def test_t7_the_steps_have_one_home_and_two_citations() -> None:
    sentence = "`offending_facts` lists the witnesses of the violation"
    pages = [*sorted((ROOT / "docs").rglob("*.md")), *sorted((ROOT / "src" / "gnd" / "skills").rglob("*.md"))]
    homes = [page for page in pages if sentence in page.read_text(encoding="utf-8")]
    assert homes == [GUIDE]
    contract = (ROOT / "src/gnd/skills/gnd-extract/references/extraction-contract.md").read_text(encoding="utf-8")
    assert contract.count("https://vasiloglou.github.io/gnd-public/guides/documents/#reading-a-failed-verification") == 1
    commands = (ROOT / "docs/literature/commands.md").read_text(encoding="utf-8")
    assert commands.count("../guides/documents.md#reading-a-failed-verification") == 1


def _derivation_failure_report(folder: Path) -> tuple[dict, int]:
    shutil.copytree(files("gnd").joinpath("examples", "bookrec"), folder)
    population = json.loads((folder / "complete.population.json").read_text(encoding="utf-8"))
    population["facts"]["book_is_eligible"].remove({"user": "ada", "book": "river"})
    (folder / "missing.json").write_text(json.dumps(population), encoding="utf-8")
    return _verify_json(folder, "complete.orm.yaml", "missing.json")


def test_t8_derivation_failure_is_listed(tmp_path: Path) -> None:
    report, code = _derivation_failure_report(tmp_path / "bookrec")
    assert code == 1
    assert [v for v in report["verdicts"] if v["verdict"] == "fail"] == []
    (entry,) = listing(report)
    assert entry["derivation_ref"] == "derivation:book_is_eligible"
    assert entry["findings"]


def test_t10_a_mandatory_failure_lists_bare_instance_witnesses(tmp_path: Path) -> None:
    """The steps hold for a witness that is not a row object (review finding F1)."""
    for name in ("model.orm.yaml", "population.bad.yaml"):
        shutil.copyfile(SKELETON / name, tmp_path / name)
    report, code = _verify_json(tmp_path, "model.orm.yaml", "population.bad.yaml")
    assert code == 1
    by_kind = {entry["constraint_type"]: entry["offending_facts"] for entry in listing(report)}
    assert by_kind["mandatory"] == [3]
    assert all(isinstance(row, dict) for row in by_kind["uniqueness"])
