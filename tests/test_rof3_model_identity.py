"""ROF3 (report-output-fidelity): the canonical model identity and its producer (issue 111).

The corpus under tests/fixtures/rof3-model-identity is the phase's approval instrument;
its README tells each case and expected/ holds the vectors. Written before the
implementation: the cases that need ``model_identity`` or ``gnd validate --identity``
fail until ROF3 lands; the legacy pins and the corpus self-check pass now.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys

import pytest
from support.repository import REPO_ROOT

from gnd.model import load_model
from gnd.values import model_digest

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rof3-model-identity"
EXPECTED = CORPUS / "expected"
VECTORS = json.loads((EXPECTED / "vectors.json").read_text())
IDENTIFIED = sorted(case for case, row in VECTORS.items() if row["identity"] is not None)


def _values_function(name: str):
    function = getattr(importlib.import_module("gnd.values"), name, None)
    assert function is not None, f"gnd.values.{name} does not exist yet"
    return function


def _model(case: str):
    return load_model(CORPUS / VECTORS[case]["model"])


def _validate_identity(case: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", "validate", VECTORS[case]["model"], "--identity"],
        cwd=CORPUS, capture_output=True, check=False,
    )


@pytest.mark.parametrize("case", IDENTIFIED)
def test_identity_bytes_match_the_vector(case: str) -> None:
    model = _model(case)
    assert _values_function("model_identity_bytes")(model) == (EXPECTED / f"{case}.identity.json").read_bytes()
    assert _values_function("model_identity")(model) == (EXPECTED / f"{case}.digest").read_text().strip()


@pytest.mark.parametrize("case", sorted(VECTORS))
def test_legacy_digest_is_unchanged(case: str) -> None:
    assert model_digest(_model(case)) == (EXPECTED / f"{case}.legacy").read_text().strip()


@pytest.mark.parametrize("case", IDENTIFIED)
def test_producer_prints_the_digest_and_the_document(case: str) -> None:
    result = _validate_identity(case)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (EXPECTED / f"{case}.stdout.txt").read_bytes()
    first, document = result.stdout.decode("utf-8").splitlines()
    # A caller with hashlib alone recomputes the digest from the printed document.
    recomputed = "sha256:" + hashlib.sha256((document + "\n").encode("utf-8")).hexdigest()
    assert first.split()[2] == recomputed


def test_surrogate_model_is_refused_not_crashed() -> None:
    model = _model("surrogate")
    error = _values_function("ModelIdentityError")
    with pytest.raises(error) as raised:
        _values_function("model_identity")(model)
    assert raised.value.rule_id == "model:identity-unrepresentable"
    result = _validate_identity("surrogate")
    assert result.returncode == 3
    assert result.stdout.decode("utf-8", "replace").rstrip().endswith("[model:identity-unrepresentable]")
    assert b"Traceback" not in result.stderr


def test_operations_only_change_keeps_a_plain_identity_and_moves_a_reference_one() -> None:
    assert VECTORS["operations-a"]["identity"] == VECTORS["operations-b"]["identity"]
    assert VECTORS["reference"]["identity"] != VECTORS["reference-operations"]["identity"]
    identity = _values_function("model_identity")
    assert identity(_model("operations-a")) == identity(_model("operations-b"))
    assert identity(_model("reference")) != identity(_model("reference-operations"))


def test_versions_are_defined_only_where_the_definition_says() -> None:
    identity = _values_function("model_identity")
    error = _values_function("ModelIdentityError")
    reference, plain = _model("reference"), _model("plain-small")
    assert identity(reference, 1) == VECTORS["reference"]["identity"]
    assert identity(plain, 2) == VECTORS["plain-small"]["identity"]
    for model, version in ((reference, 2), (plain, 1), (plain, 3)):
        with pytest.raises(error):
            identity(model, version)


def test_corpus_lists_every_case_once() -> None:
    models = {path.relative_to(CORPUS).as_posix() for path in (CORPUS / "models").rglob("*.orm.*")}
    assert models == {row["model"] for row in VECTORS.values()}
    for case, row in VECTORS.items():
        assert (EXPECTED / f"{case}.legacy").is_file()
        has_vector = (EXPECTED / f"{case}.identity.json").is_file()
        assert has_vector == (row["identity"] is not None)
    assert {row["identity_version"] for row in VECTORS.values() if row["identity"]} == {1, 2}
