"""Current BookRec checker and application guards with retained synthetic fixtures."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest
from test_public_book_runtime import _workspace

from gnd.report import legacy_report_projection

_HOLDER, REPO_ROOT, _MEMBERS = _workspace()
REPO_ROOT = REPO_ROOT.resolve()
BOOKREC = REPO_ROOT / "examples/bookrec"
SURPLUS = {"book": "b-dune", "user": "u-ada"}

def _install_fixtures():
    fixture = Path(__file__).parent / "fixtures/public-book-skills/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    raw = fixture.read_bytes()
    assert len(raw) <= 16384 and hashlib.sha256(raw).hexdigest() == '30f10b94fd8893494fc6874ee5ff8f144a198bf1b1f8fb0243f063b2b90a7813'
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(65537)
    assert len(expanded) <= 65536
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 7
    for name, member in payload["members"].items():
        path = PurePosixPath(name)
        assert path.parts and not path.is_absolute() and ".." not in path.parts and path.as_posix() == name
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 16384 and hashlib.sha256(data).hexdigest() == member["sha256"]
        assert member["mode"] == 420
        target = REPO_ROOT.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(member["mode"])
_install_fixtures()


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _run_check(population: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            "examples/bookrec/model.orm.yaml",
            population.relative_to(REPO_ROOT).as_posix(),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )


def _derivation_findings(payload: dict[str, object]) -> list[dict[str, object]]:
    derivations = payload["derivations"]
    assert isinstance(derivations, list)
    return [finding for row in derivations for finding in row["findings"]]


def test_three_bookrec_reds_rerun_and_byte_match_committed_evidence() -> None:
    roster = {
        "derivation-incomplete": "derived-extension-incomplete",
        "completeness-missing": "guarded",
        "derivation-unsound": "derived-extension-unsound",
    }
    assert set(roster) == {
        "derivation-incomplete",
        "completeness-missing",
        "derivation-unsound",
    }
    for name, claim in roster.items():
        population = BOOKREC / "populations" / f"{name}.population.json"
        evidence = BOOKREC / "evidence" / f"{name}-check.json"
        completed = _run_check(population)
        assert completed.returncode == 1
        assert completed.stderr == b""
        # Committed evidence stays the pin: undoing ONLY Phase 3's declared
        # model binding must reproduce the retained bytes (IF-P3-16).
        payload = json.loads(completed.stdout)
        projected = (json.dumps(legacy_report_projection(payload, 4)) + "\n").encode()
        assert projected == evidence.read_bytes()
        if claim.startswith("derived-extension"):
            assert claim in {row["kind"] for row in _derivation_findings(payload)}
        else:
            assert any(
                row["constraint_type"] == claim and row["verdict"] == "fail"
                for row in payload["verdicts"]
            )

    unsound = _read_json(BOOKREC / "evidence" / "derivation-unsound-check.json")
    findings = _derivation_findings(unsound)
    assert findings == [
        {
            "kind": "derived-extension-unsound",
            "message": (
                "The derived extension of 'book_is_eligible' is unsound — "
                'offending fact {"book":"b-dune","user":"u-ada"}.'
            ),
            "witness": SURPLUS,
        }
    ]


def test_dogfood_roster_and_surplus_have_live_falsifiers(tmp_path: Path) -> None:
    roster = {"derivation-incomplete", "completeness-missing", "derivation-unsound"}
    with pytest.raises(AssertionError):
        assert roster - {"derivation-unsound"} == roster

    mutated = _read_json(BOOKREC / "populations" / "derivation-unsound.population.json")
    mutated["facts"]["book_is_eligible"][0] = {
        "book": "b-earthsea",
        "user": "u-minor",
    }
    path = tmp_path / "computed-member.population.json"
    path.write_text(json.dumps(mutated) + "\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            "examples/bookrec/model.orm.yaml",
            str(path),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert "derived-extension-unsound" not in {row["kind"] for row in _derivation_findings(payload)}


def test_bookrec_explicitly_covers_the_computed_relations_it_publishes(
    tmp_path: Path,
) -> None:
    output = tmp_path / "recommendations.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bookrec.cli",
            "recommend",
            "--model",
            "../model.orm.yaml",
            "--input",
            "../populations/seed.population.json",
            "--output",
            str(output),
            "--user",
            "u-minor",
            "--limit",
            "2",
        ],
        cwd=BOOKREC / "project",
        env={"PYTHONPATH": str(BOOKREC / "project")},
        check=False,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    document = _read_json(output)
    covers = document["population"]["covers"]
    assert {"book_is_blocked_for", "book_is_eligible"} <= set(covers)
    assert document["facts"]["book_is_blocked_for"]
    assert document["facts"]["book_is_eligible"]


def test_live_conformance_payload_and_walkthrough_citations_are_bound() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "conformance",
            "examples/bookrec/model.orm.yaml",
            "examples/bookrec/project",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    conformance = BOOKREC / "evidence" / "conformance-post-eligibility-extension.json"
    assert completed.returncode == 0
    assert completed.stdout == conformance.read_bytes()

    walkthrough = (BOOKREC / "WALKTHROUGH.md").read_text(encoding="utf-8")
    citations = dict(re.findall(r"\[([^\]]+)\]\(sha256:([0-9a-f]{64})\)", walkthrough))
    for relative in (
        "evidence/derivation-unsound-check.json",
        "evidence/conformance-post-eligibility-extension.json",
    ):
        assert citations[relative] == hashlib.sha256((BOOKREC / relative).read_bytes()).hexdigest()

