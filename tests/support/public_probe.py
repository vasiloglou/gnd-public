"""Executed with base-wheel Python; no pytest or checkout runtime imports."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from public_release_fixture import publish, synthetic_release

import gnd
from gnd import api
from gnd.assurance import evidence as reader

FIXTURES = Path(sys.argv[1]).resolve()
CASE = sys.argv[2]
MODEL = FIXTURES / "model.orm.yaml"
CLEAN = FIXTURES / "clean.population.json"
DIGESTS = [
    "scope_digest",
    "semantics_digest",
    "production_roster_digest",
    "proof_digest",
    "toolchain_digest",
]


def cli(command, *paths):
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            command,
            *map(str, paths),
            "--format",
            "json",
            "--unredacted",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert "Traceback" not in run.stderr, run.stderr
    return run.returncode, json.loads(run.stdout)


def unavailable(value):
    assert not value.available and value.reason == "unavailable-or-invalid-evidence"
    assert not value.covered_scope_ids and value.digests is None


def projection(payload):
    block = payload["assurance"]
    assert block["assurance_level"] == "none"
    assert all(block[name] is None for name in DIGESTS)
    assert block["assumptions"] == []


def check(model, population, expected):
    payload = api.check(model, population, unredacted=True)
    exit_code, emitted = cli("check", model, population)
    assert exit_code == payload["exit_code"] == expected, (exit_code, payload)
    assert emitted == payload
    assert (
        payload["assurance"]["semantic_decision"]
        == {0: "accept", 1: "refuse", 2: "indeterminate", 4: "indeterminate"}[expected]
    )
    projection(payload)
    return payload


if CASE in {"C0", "C1", "C2", "C4", "C5"}:
    model = FIXTURES / "textual.orm.yaml" if CASE in {"C4", "C5"} else MODEL
    population = (
        FIXTURES
        / {"C0": "clean", "C1": "violation", "C2": "empty", "C4": "clean", "C5": "violation"}[CASE]
    )
    population = population.with_suffix(".population.json")
    expected = {"C0": 0, "C1": 1, "C2": 2, "C4": 4, "C5": 1}[CASE]
    payload = check(model, population, expected)
    if CASE == "C0":
        status, validate = cli("validate", MODEL)
        assert status == validate["exit_code"] == 0
        assert validate == api.validate(MODEL, unredacted=True)
    if CASE == "C1":
        assert any(
            row["constraint_type"] == "value"
            and row["verdict"] == "fail"
            and "Outside" in row["offending_facts"]
            for row in payload["verdicts"]
        )
    if CASE == "C2":
        assert payload["counts"]["vacuous"] > 0
    if CASE in {"C4", "C5"}:
        rows = [v for v in payload["verdicts"] if v["verdict"] == "unchecked"]
        assert rows and "Each Movie title is reviewed before publication." in str(rows)
elif CASE == "C3":
    status, payload = cli("validate", FIXTURES / "invalid.orm.yaml")
    assert status == payload["exit_code"] == 3
    assert payload == api.validate(FIXTURES / "invalid.orm.yaml", unredacted=True)
    assert any(
        row["rule_id"] == "semantic:cross-ref" and "nonsmoker" in row["message"]
        for row in payload["issues"]
    )
elif CASE == "C6":
    run = subprocess.run(
        [sys.executable, "-m", "gnd", "--definitely-not-an-option"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert run.returncode == 64 and "Traceback" not in run.stderr
elif CASE == "C7":
    assert not (Path(gnd.__file__).parent / "_assurance_evidence").exists()
    unavailable(reader.load_assurance_evidence())
    check(MODEL, CLEAN, 0)
elif CASE in {"C8", "C9", "C10"}:
    with tempfile.TemporaryDirectory() as tmp:
        package, manifest = synthetic_release(Path(tmp), Path(gnd.__file__).parent)
        reader._assurance_cache.clear()
        reader.resources.files = lambda name: package
        control = reader.load_assurance_evidence()
        assert control.available and not control.covered_scope_ids
        current = api.check(MODEL, CLEAN, unredacted=True)
        assert current["assurance"]["assumptions"] == ["synthetic-release-test"]
        if CASE == "C8":
            (package / "new_module.py").write_text("test_only = True\n")
            message = None
        elif CASE == "C9":
            manifest["runtime_domain"]["version"] = "0.0.0"
            assert reader.runtime_identity(list(reader.RUNTIME_DEPENDENCIES))["version"] != "0.0.0"
            publish(package, manifest)
            message = "stale runtime identity"
        else:
            p = package / "_assurance_evidence/manifest.json"
            p.write_bytes(p.read_bytes() + b" ")
            message = "stale release manifest"
        try:
            reader._load(package)
        except (OSError, ValueError) as error:
            if message:
                assert message in str(error), str(error)
        else:
            raise AssertionError("stale/corrupt bundle authenticated")
        unavailable(reader.load_assurance_evidence())
        stale = api.check(MODEL, CLEAN, unredacted=True)
        projection(stale)
        assert {k: v for k, v in current.items() if k != "assurance"} == {
            k: v for k, v in stale.items() if k != "assurance"
        }
        assert stale["assurance"]["semantic_decision"] == current["assurance"]["semantic_decision"]
        reader._assurance_cache.clear()
else:
    raise AssertionError(CASE)
print(json.dumps({"case": CASE, "exit": 0, "gnd_file": gnd.__file__}))
