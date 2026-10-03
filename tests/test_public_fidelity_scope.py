"""Current fidelity exclusion/failed-case controls on hand-authored synthetic documents."""
from __future__ import annotations

import base64
import contextlib
import gzip
import hashlib
import io
import json
import shutil
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from test_public_extract_boundary import _workspace

from gnd.cli import main

_HOLDER, REPO_ROOT = _workspace()
CORPUS = REPO_ROOT / "tests/fixtures/v51-extraction-boundary"
ANSWER = json.loads((CORPUS / "answers/expected.json").read_text(encoding="utf-8"))
EXPECTED_APPLICABLE = CORPUS / "answers/bookrec.applicable.expected.json"
BOOKREC_MODEL = "examples/bookrec/model.orm.yaml"

def _install_fixtures():
    fixture = Path(__file__).parent / "fixtures/public-fidelity-scope/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    raw = fixture.read_bytes()
    assert len(raw) <= 16384 and hashlib.sha256(raw).hexdigest() == 'ec06ce96b32854cd44a3be63e4b03605d0a22025c88f0268dde4f84e53eb5f2d'
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(32769)
    assert len(expanded) <= 32768
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 6
    for name, member in payload["members"].items():
        path = PurePosixPath(name)
        assert path.parts and not path.is_absolute() and ".." not in path.parts and path.as_posix() == name
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 8192 and hashlib.sha256(data).hexdigest() == member["sha256"]
        assert member["mode"] == 420
        target = REPO_ROOT.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(member["mode"])
_install_fixtures()

@pytest.fixture(autouse=True)
def _fixture_cwd(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)


def _extract(out: Path) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["extract", BOOKREC_MODEL, "--out", str(out)]) == 0


def _fidelity(
    tmp_path: Path, case_names: list[str]
) -> tuple[int, dict[str, Any] | None, str]:
    artifacts = tmp_path / "artifacts"
    _extract(artifacts)
    cases = tmp_path / "cases"
    for case_name in case_names:
        shutil.copytree(CORPUS / case_name, cases / case_name)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(
            [
                "fidelity",
                BOOKREC_MODEL,
                "--cases",
                str(cases),
                "--artifacts",
                str(artifacts),
                "--format",
                "json",
            ]
        )
    rendered = stdout.getvalue()
    return int(code), json.loads(rendered) if code == 0 else None, rendered


def _rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in payload["per_fact_type"]}


def test_bookrec_applicable_artifact_matches_the_approved_future_bytes(
    tmp_path: Path,
) -> None:
    artifacts = tmp_path / "artifacts"
    _extract(artifacts)
    assert (artifacts / "model.applicable.json").read_bytes() == EXPECTED_APPLICABLE.read_bytes()


def test_three_case_fidelity_discloses_exclusion_and_failed_attempt(
    tmp_path: Path,
) -> None:
    code, payload, rendered = _fidelity(
        tmp_path,
        ["bookrec-mixed", "bookrec-derived-only", "bookrec-attempted-derived"],
    )
    assert code == 0, rendered
    assert payload is not None
    expected = ANSWER["bookrec"]["fidelity"]
    assert payload["schema_version"] == expected["schema_version"] == 2
    assert payload["cases"]["ran"] == expected["cases"]["ran"] == 2
    assert payload["cases"]["failed"] == expected["cases"]["failed"] == 1
    assert payload["cases"]["skipped"] == expected["cases"]["skipped"] == 0
    assert len(payload["cases"]["reasons"]) == 1
    assert payload["cases"]["reasons"][0]["case"] == expected["cases"]["failed_case"]
    assert expected["cases"]["failed_reason_contains"] in payload["cases"]["reasons"][0][
        "reason"
    ]

    rows = _rows(payload)
    for fact_type_id, expected_row in expected["per_fact_type"].items():
        row = rows[fact_type_id]
        assert row["applicable"] is expected_row["applicable"]
        if not expected_row["applicable"]:
            assert row["reason"] == expected_row["reason"]
            assert set(row["matched"].values()) == {0}
            for rate_name in ("precision", "recall", "unresolved"):
                assert row[rate_name] == {
                    "numerator": 0,
                    "denominator": 0,
                    "rate": None,
                }
        else:
            assert row["matched"]["source_total"] == expected_row["source_total"]
            assert row["matched"]["extracted_total"] == expected_row["extracted_total"]
            assert row["matched"]["tp"] == expected_row["tp"]


def test_all_observed_facts_derived_has_only_null_denominators(tmp_path: Path) -> None:
    code, payload, rendered = _fidelity(tmp_path, ["bookrec-derived-only"])
    assert code == 0, rendered
    assert payload is not None
    assert payload["cases"] == {"ran": 1, "skipped": 0, "failed": 0, "reasons": []}
    for row in payload["per_fact_type"]:
        for rate_name in ("precision", "recall", "unresolved"):
            assert row[rate_name]["denominator"] == 0
            assert row[rate_name]["rate"] is None

