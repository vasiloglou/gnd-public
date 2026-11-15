"""LI0: witness and why-not accept version-1 models and models without model_id.

The witness producer and the why-not path re-enter intake with a dump of the
loaded model. That dump kept the loader defaults ``operations: []`` and
``model_id: None``, which the meta-schema refuses at version 1 and at every
version respectively. See .gnd-planning/milestones/literature-identity/notes/
phase-LI0-spec.md for the criteria (T1-T11) these tests discharge.

``golden.json`` was generated from the baseline tree (``ecd12986``) by running
this module as a script, before any source edit:

    uv run python tests/test_li0_witness_wire.py --write-golden
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
LI0 = FIXTURES / "li0"
GOLDEN = LI0 / "golden.json"
SCHEMA = ROOT / "src" / "gnd" / "schema" / "orm-meta.schema.json"
WITH_ID = ("grandparent-v1.orm.yaml",)
WITHOUT_ID = ("grandparent-v1-no-id.orm.yaml", "grandparent-v2-no-id.orm.yaml")
SUPPORTED = ("grandparent-v2.orm.yaml",)  # accepted before LI0 (golden certificate)
DUMP_CALL = "model.model_dump("


def gnd(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "gnd", *map(str, args)],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


def _json(run):
    return json.loads(run.stdout)


def _fixture_models():
    """Every loadable fixture model without includes, in a stable order."""
    from gnd.model import ModelValidationError, load_model

    for path in sorted(FIXTURES.rglob("*.orm.yaml")):
        try:
            model = load_model(path)
        except ModelValidationError:  # deliberately invalid fixtures are out of T4 scope
            continue
        if model.includes:
            continue
        yield path, model


def _identities(model):
    from gnd.values import ModelIdentityError, _model_digest, model_identity

    try:
        canonical = model_identity(model)
    except ModelIdentityError as error:
        canonical = f"error:{type(error).__name__}"
    return {"legacy": _model_digest(model), "canonical": canonical}


def _certificate_sha(model_name, tmp_dir):
    out = Path(tmp_dir) / f"{model_name}.witness.json"
    run = gnd("witness", LI0 / model_name, LI0 / "population.json",
              "--targets", LI0 / "targets.json", "--raw", "--out", out)
    assert _json(run)["exit_code"] == 0, run.stdout + run.stderr
    return hashlib.sha256(out.read_bytes()).hexdigest()


def build_golden(tmp_dir):
    identities = {
        str(path.relative_to(ROOT)): _identities(model) for path, model in _fixture_models()
    }
    from gnd.model import load_model

    for name in WITH_ID + WITHOUT_ID + SUPPORTED:
        identities[f"tests/fixtures/li0/{name}"] = _identities(load_model(LI0 / name))
    certificates = {name: _certificate_sha(name, tmp_dir) for name in SUPPORTED}
    return {"baseline": "ecd12986", "identities": identities, "certificates": certificates}


# --- T1, T2, T3: witness then replay ------------------------------------------------


@pytest.mark.parametrize("name", WITH_ID + WITHOUT_ID + SUPPORTED)
def test_witness_and_replay_exit_0(name, tmp_path):
    out = tmp_path / "w.json"
    made = gnd("witness", LI0 / name, LI0 / "population.json",
               "--targets", LI0 / "targets.json", "--raw", "--out", out)
    assert _json(made)["exit_code"] == 0, made.stdout
    replayed = gnd("replay", LI0 / name, LI0 / "population.json", out)
    assert _json(replayed)["exit_code"] == 0, replayed.stdout


# --- T5: why-not ---------------------------------------------------------------------


@pytest.mark.parametrize("name", WITH_ID + WITHOUT_ID)
def test_why_not_exit_0(name):
    run = gnd("why-not", LI0 / name, LI0 / "population.json",
              "--fact-type", "person_grandparent_of_person")
    payload = _json(run)
    assert payload["exit_code"] == 0, run.stdout
    assert payload["mode"] == "rule"


# --- T4: round trip over the committed fixture models ---------------------------------


def test_model_wire_round_trips_every_fixture_model():
    from gnd.model import load_model_bytes
    from gnd.witness.io import model_wire

    def view(model):
        return model.model_dump(mode="json", exclude={"warnings"})

    walked = 0
    for path, model in _fixture_models():
        wire = model_wire(model)
        again = load_model_bytes(
            json.dumps(wire, ensure_ascii=False, allow_nan=False).encode("utf-8"),
            source="model.orm.json",
        )
        assert view(again) == view(model), path
        walked += 1
    assert walked >= 200, walked


# --- T6: include-bearing models keep their reason -------------------------------------


def test_include_bearing_model_keeps_its_include_reason(tmp_path):
    vocabulary = tmp_path / "vocab.orm.yaml"
    vocabulary.write_text((LI0 / "grandparent-v2.orm.yaml").read_text())
    digest = hashlib.sha256(vocabulary.read_bytes()).hexdigest()
    includer = tmp_path / "model.orm.yaml"
    includer.write_text(
        "version: 5\nmodel_id: urn:gnd-fixture:li0-includer@1\n"
        f"includes:\n  - {{id: vocab, path: vocab.orm.yaml, sha256: {digest}}}\n"
        "constraints: []\n"
    )
    run = gnd("witness", includer, LI0 / "population.json", "--targets", LI0 / "targets.json")
    payload = _json(run)
    assert payload["exit_code"] == 3
    assert payload["reason"].startswith("include:")


# --- T7, T11: golden certificate bytes and model identities ---------------------------


def test_supported_certificates_match_baseline_golden(tmp_path):
    golden = json.loads(GOLDEN.read_text())
    for name, digest in golden["certificates"].items():
        assert _certificate_sha(name, tmp_path) == digest, name


def test_model_identities_match_baseline_golden():
    from gnd.model import load_model

    golden = json.loads(GOLDEN.read_text())["identities"]
    current = {str(path.relative_to(ROOT)): _identities(model) for path, model in _fixture_models()}
    for name in WITH_ID + WITHOUT_ID + SUPPORTED:
        current[f"tests/fixtures/li0/{name}"] = _identities(load_model(LI0 / name))
    assert current == golden
    assert sum(1 for k in golden if "li0" in k and "no-id" in k) == 2


# --- T8: hostile wire documents still refuse at 3 -------------------------------------


@pytest.mark.parametrize("hostile", ["nan", "deep", "long-int"])
def test_hostile_wire_document_refuses_at_3(hostile, monkeypatch):
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.witness import io, producer
    from gnd.witness.io import load_targets

    model = load_model(LI0 / "grandparent-v2.orm.yaml")
    candidate = load_population(LI0 / "population.json", model=model)
    targets = load_targets(LI0 / "targets.json")
    original = io.model_wire

    def poisoned(m):
        document = original(m)
        if hostile == "nan":
            document["source"] = {"confidence": float("nan")}
        elif hostile == "deep":
            nested = {}
            for _ in range(70):
                nested = {"x": nested}
            document["source"] = nested
        else:
            document["source"] = {"n": 10**200}
        return document

    monkeypatch.setattr(producer, "model_wire", poisoned)
    result = producer.produce_witness(model, candidate, targets)
    assert result.exit_code == 3


# --- T9: no re-serialization of a model remains in the witness package ----------------


def test_no_direct_model_dump_in_witness_package():
    offenders = [
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "src" / "gnd" / "witness").rglob("*.py"))
        if DUMP_CALL in path.read_text()
    ]
    assert offenders == ["src/gnd/witness/io.py"], offenders


# --- T10: every optional section gated by the meta-schema is omitted when empty -------


def test_wire_omits_every_schema_gated_optional_section_when_empty():
    from gnd.model import load_model
    from gnd.witness.io import model_wire

    schema = json.loads(SCHEMA.read_text())
    gated = {
        key
        for clause in schema["allOf"]
        for key in clause["if"].get("required", [])
    }
    assert gated == {"operations", "reference_populations", "includes", "fact_type_constraints"}
    wire = model_wire(load_model(LI0 / "grandparent-v1-no-id.orm.yaml"))
    assert gated.isdisjoint(wire)
    assert "model_id" not in wire


if __name__ == "__main__" and sys.argv[1:] == ["--write-golden"]:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        GOLDEN.write_text(json.dumps(build_golden(tmp), indent=1, sort_keys=True) + "\n")
    print(f"wrote {GOLDEN.relative_to(ROOT)}")
