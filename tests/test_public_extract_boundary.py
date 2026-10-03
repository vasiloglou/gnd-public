"""Public-CLI proof for the v5.1 Phase 2 extraction boundary corpus."""

from __future__ import annotations

import base64
import contextlib
import gzip
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath

import pytest

from gnd.cli import main


def _workspace():
    fixture = Path(__file__).parent / "fixtures/public-extract-boundary/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    raw = fixture.read_bytes()
    assert len(raw) <= 32768 and hashlib.sha256(raw).hexdigest() == '5d5c8f6bd7235b25e1abf76e2a969687c41e10571c6693531c9c6012e884e279'
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(131073)
    assert len(expanded) <= 131072
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 20
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-extract-boundary-")
    root = Path(holder.name).resolve()
    for name, member in payload["members"].items():
        path = PurePosixPath(name)
        assert path.parts and not path.is_absolute() and ".." not in path.parts and path.as_posix() == name
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 32768 and hashlib.sha256(data).hexdigest() == member["sha256"]
        assert member["mode"] == 420
        target = root.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(member["mode"])
    return holder, root

_HOLDER, REPO_ROOT = _workspace()

@pytest.fixture(autouse=True)
def _fixture_cwd(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

CORPUS = REPO_ROOT / "tests" / "fixtures" / "v51-extraction-boundary"
ANSWER = json.loads((CORPUS / "answers" / "expected.json").read_text(encoding="utf-8"))
MIXED_MODEL = CORPUS / "models" / "mixed.orm.yaml"
BOOKREC_MODEL = REPO_ROOT / "examples" / "bookrec" / "model.orm.yaml"
BOOKREC_MODEL_ARG = "examples/bookrec/model.orm.yaml"


def _run_json(arguments: list[str]) -> tuple[int, dict]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main([*arguments, "--format", "json"])
    return int(code), json.loads(stdout.getvalue())


def _extract_bookrec(out: Path) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["extract", BOOKREC_MODEL_ARG, "--out", str(out)]) == 0


@pytest.mark.parametrize(
    "expected",
    ANSWER["population_cases"],
    ids=[row["id"] for row in ANSWER["population_cases"]],
)
def test_mixed_population_matrix_matches_the_approved_answer(expected: dict) -> None:
    population = CORPUS / "populations" / f"{expected['id']}.population.yaml"
    code, payload = _run_json(["check", str(MIXED_MODEL), str(population)])

    assert code == payload["exit_code"] == expected["exit"]
    assert [issue["rule_id"] for issue in payload["issues"]] == expected[
        "population_rule_ids"
    ]
    observed = {
        row["derivation_ref"]: [row["verdict"], row["reason_code"]]
        for row in payload["derivations"]
    }
    for derivation_ref, disposition in expected.get("derivations", {}).items():
        assert observed[derivation_ref] == disposition


def test_real_extract_emits_the_approved_filtered_bookrec_header(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _extract_bookrec(artifacts)
    index = json.loads((artifacts / "model.artifacts.json").read_text(encoding="utf-8"))

    assert index["header_template"] == ANSWER["bookrec"]["generated_header"]


def test_bookrec_filtered_population_is_band_four_on_check() -> None:
    population = CORPUS / "bookrec-mixed" / "extracted.population.json"
    code, payload = _run_json(["check", BOOKREC_MODEL_ARG, str(population)])
    expected = ANSWER["bookrec"]["filtered_check"]

    assert code == payload["exit_code"] == expected["exit"] == 4
    assert payload["counts"] == expected["counts"]
    assert {
        row["derivation_ref"]: {
            "verdict": row["verdict"],
            "reason_code": row["reason_code"],
        }
        for row in payload["derivations"]
    } == expected["derivations"]


def test_bookrec_filtered_population_is_band_four_on_verify(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _extract_bookrec(artifacts)
    case = CORPUS / "bookrec-mixed"
    code, payload = _run_json(
        [
            "verify",
            BOOKREC_MODEL_ARG,
            str(case / "extracted.population.json"),
            "--sidecar",
            str(case / "extracted.population.extraction.json"),
            "--artifacts",
            str(artifacts),
        ]
    )

    assert code == payload["exit_code"] == 4
    assert payload["extraction"]["state"] == "ran"
    assert [row["reason_code"] for row in payload["derivations"]] == [
        "derivation-not-covered",
        "derivation-not-covered",
    ]


def test_old_all_covered_header_is_the_band_one_discriminator() -> None:
    population = CORPUS / "bookrec-mixed" / "current-header.population.json"
    code, payload = _run_json(["check", BOOKREC_MODEL_ARG, str(population)])

    assert code == payload["exit_code"] == 1
    assert [finding["kind"] for row in payload["derivations"] for finding in row["findings"]] == [
        "derived-extension-incomplete",
        "derived-extension-incomplete",
    ]


def test_verify_reaches_a8_after_valid_bindings(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _extract_bookrec(artifacts)
    case = CORPUS / "bookrec-attempted-derived"
    code, payload = _run_json(
        [
            "verify",
            BOOKREC_MODEL_ARG,
            str(case / "extracted.population.json"),
            "--sidecar",
            str(case / "extracted.population.extraction.json"),
            "--artifacts",
            str(artifacts),
        ]
    )

    assert code == payload["exit_code"] == 3
    assert payload["extraction"]["state"] == "ran"
    assert [issue["rule_id"] for issue in payload["issues"]] == [
        "population:uncovered-structured-derived-facts"
    ]


def test_verify_bad_binding_precedes_a8(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _extract_bookrec(artifacts)
    case = tmp_path / "case"
    shutil.copytree(CORPUS / "bookrec-attempted-derived", case)
    sidecar = case / "extracted.population.extraction.json"
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    payload["population_sha256"] = "0" * 64
    sidecar.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    code, report = _run_json(
        [
            "verify",
            BOOKREC_MODEL_ARG,
            str(case / "extracted.population.json"),
            "--sidecar",
            str(sidecar),
            "--artifacts",
            str(artifacts),
        ]
    )

    assert code == report["exit_code"] == 3
    assert report["extraction"]["state"] == "failed"
    assert "binding" in report["extraction"]["reason"]
    assert [issue["rule_id"] for issue in report["issues"]] == [
        "extraction:binding-mismatch"
    ]
