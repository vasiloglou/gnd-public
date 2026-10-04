"""Behavioral checks for the independently authored public BookRec tutorial."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files

import pytest

from gnd import api


@pytest.fixture
def bookrec(tmp_path):
    root = tmp_path / "bookrec"
    shutil.copytree(str(files("gnd").joinpath("examples", "bookrec")), root)
    return root


def run_app(root, tmp_path, *extra, model="model.orm.yaml", command="recommend"):
    output = tmp_path / "result.json"
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "bookrec.cli",
            command,
            "--model",
            str(root / model),
            "--input",
            str(root / "seed.population.json"),
            "--output",
            str(output),
            *extra,
        ],
        cwd=root / "extension",
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    return run, output


@pytest.mark.parametrize(
    ("name", "expected", "warnings", "failed_ref"),
    [
        ("seed", 0, 0, None),
        ("already-read", 1, 0, "constraints[0]"),
        ("adult-for-minor", 1, 0, "constraints[1]"),
        ("genre-warning", 0, 1, None),
    ],
)
def test_known_business_outcomes(bookrec, name, expected, warnings, failed_ref):
    report = api.check(
        bookrec / "model.orm.yaml", bookrec / f"{name}.population.json", unredacted=True
    )
    assert report["exit_code"] == expected
    assert report["counts"]["warning"] == warnings
    failed = [row for row in report["verdicts"] if row["verdict"] == "fail"]
    assert [row["constraint_ref"] for row in failed] == ([failed_ref] if failed_ref else [])


def test_checked_publication_and_preference_repair(bookrec, tmp_path):
    run, output = run_app(bookrec, tmp_path, "--user", "ada")
    assert run.returncode == 0, run.stderr
    report = json.loads(run.stdout)
    assert report["acceptance_ready"] and report["counts"]["warning"] == 1
    document = json.loads(output.read_text())
    assert [row["book"] for row in document["facts"]["recommendation"] if row["user"] == "ada"] == [
        "cosmos",
        "map",
    ]
    original = output.read_bytes()
    repeated, same = run_app(bookrec, tmp_path, "--user", "ada")
    assert repeated.returncode == 2 and same.read_bytes() == original
    assert "output already exists" in repeated.stderr


def test_rule_change_blocks_publication_until_algorithm_adjustment(bookrec, tmp_path):
    run, output = run_app(bookrec, tmp_path, "--user", "ada", model="strict.orm.yaml")
    assert run.returncode == 1, run.stderr
    assert not output.exists() and not list(tmp_path.glob(".bookrec-*"))
    accepted, output = run_app(
        bookrec, tmp_path, "--user", "ada", "--preferred-only", model="strict.orm.yaml"
    )
    assert accepted.returncode == 0, accepted.stderr
    assert json.loads(accepted.stdout)["counts"]["warning"] == 0
    assert api.check(bookrec / "strict.orm.yaml", output)["acceptance_ready"]


@pytest.mark.parametrize(
    ("args", "expected"), [(["--user", "ghost"], 3), (["--user", "ada", "--limit", "0"], 2)]
)
def test_application_refusals_preserve_input(bookrec, tmp_path, args, expected):
    before = (bookrec / "seed.population.json").read_bytes()
    run, output = run_app(bookrec, tmp_path, *args)
    assert run.returncode == expected, run.stderr
    assert not output.exists()
    assert (bookrec / "seed.population.json").read_bytes() == before


def test_complete_results_and_independent_missing_consequence(bookrec, tmp_path):
    run, output = run_app(bookrec, tmp_path, model="complete.orm.yaml", command="complete")
    assert run.returncode == 0, run.stderr
    document = json.loads(output.read_text())
    assert document == json.loads((bookrec / "complete.population.json").read_text())
    expected = {
        ("ada", "map"),
        ("ada", "river"),
        ("ben", "map"),
        ("ben", "night"),
        ("ben", "river"),
    }
    assert {(row["user"], row["book"]) for row in document["facts"]["recommendation"]} == expected
    document["facts"]["recommendation"].remove({"user": "ada", "book": "river"})
    output.write_text(json.dumps(document))
    report = api.check(bookrec / "complete.orm.yaml", output, unredacted=True)
    assert report["exit_code"] == 1 and report["counts"]["fail"] == 1
    assert all(row["verdict"] == "pass" for row in report["derivations"])
    assert [row["constraint_ref"] for row in report["verdicts"] if row["verdict"] == "fail"] == [
        "constraints[3]"
    ]


def test_missing_and_unsupported_derived_claims_are_independent_failures(bookrec, tmp_path):
    for change, kind in [
        ("missing", "derived-extension-incomplete"),
        ("extra", "derived-extension-unsound"),
    ]:
        document = json.loads((bookrec / "complete.population.json").read_text())
        claimed = document["facts"]["book_is_eligible"]
        if change == "missing":
            claimed.remove({"user": "ada", "book": "river"})
        else:
            claimed.append({"user": "ada", "book": "night"})
        path = tmp_path / f"{change}.json"
        path.write_text(json.dumps(document))
        report = api.check(bookrec / "complete.orm.yaml", path, unredacted=True)
        assert report["exit_code"] == 1
        assert any(
            finding["kind"] == kind for row in report["derivations"] for finding in row["findings"]
        )
