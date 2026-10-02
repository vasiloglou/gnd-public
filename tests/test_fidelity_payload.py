"""The fidelity payload's trust claims are SCHEMA facts (PANEL-1, R-11′, R-13′, D-22).

The claim this file defends is not "the report says it is uncalibrated" — prose
in a payload is a promise, and this phase is named after promises that cannot
fail. The claim is that ``fidelity.schema.json`` makes the alternative
*impossible to represent*: ``calibration.state`` is a required const,
``publishable`` is a required const ``false``, and every object is closed, so an
``interval``/``ci``/``bootstrap`` key cannot exist in a valid payload at any
depth. A reviewer confirms that by reading the schema, not by auditing the code.

R-06 (cross-family delta) and R-12 (the N=12 owner-labelled calibration set) are
panel-confirmed DEFERRALS. This machinery is their stand-in: the round trip
cannot bound its own bias, so the payload refuses to be publishable rather than
publishing a bound it did not establish.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as SchemaValidationError
from support.digests import sha256_file as _sha256
from support.documents import write_population

from gnd.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"
STEM = "setfam"

#: A tiny conforming source population over setfam: one composite-identified
#: booking (external mode) plus direct-mode teaching/taking/room facts.
SOURCE_FACTS: dict[str, list[dict[str, Any]]] = {
    "booking_by_person": [{"booking": "b1", "person": 1}],
    "booking_of_room": [{"booking": "b1", "room": "R1"}],
    "person_teaches_course": [{"person": 1, "course": "C1"}],
    "person_takes_course": [{"person": 2, "course": "C1"}],
    "room_has_seats": [{"room": "R1", "seats": 20}],
}

#: The same facts under the extractor's OWN invented booking token — the
#: composite identity is the joined (person, room) tuple, not the surrogate.
FAITHFUL_FACTS: dict[str, list[dict[str, Any]]] = {
    "booking_by_person": [{"booking": "bk-7", "person": 1}],
    "booking_of_room": [{"booking": "bk-7", "room": "R1"}],
    "person_teaches_course": [{"person": 1, "course": "C1"}],
    "person_takes_course": [{"person": 2, "course": "C1"}],
    "room_has_seats": [{"room": "R1", "seats": 20}],
}

DOCUMENT = (
    "Person 1 teaches course C1. Person 2 takes course C1.\n"
    "Room R1 has 20 seats and is booked by person 1.\n"
)


def _write_population(
    path: Path, facts: dict[str, list[dict[str, Any]]], *, source: str
) -> None:
    document = {
        "population": {
            "model": MODEL.name,
            "source": source,
            "covers": sorted(facts),
        },
        "facts": facts,
    }
    write_population(
        path.parent, json.dumps(document, indent=2, sort_keys=True) + "\n", name=path.name
    )


@pytest.fixture
def artifacts(tmp_path: Path) -> Path:
    """The per-model bundle ``gnd extract`` emits — the fidelity lane's
    fail-closed input."""
    out = tmp_path / "artifacts"
    assert main(["extract", str(MODEL), "--out", str(out)]) == 0
    return out


def write_case(
    case_dir: Path,
    artifacts: Path,
    *,
    facts: dict[str, list[dict[str, Any]]] | None = None,
    extracted: dict[str, list[dict[str, Any]]] | None = None,
    skipped_reason: str | None = None,
    sidecar_overrides: dict[str, Any] | None = None,
    document: str = DOCUMENT,
) -> Path:
    """One case directory in the committed convention.

    ``<case>/source.population.json``, ``document.md``,
    ``document.manifest.json``, ``extracted.population.json``,
    ``extracted.population.extraction.json``, and the optional
    ``extraction.skipped.json`` opt-out marker.
    """
    case_dir.mkdir(parents=True, exist_ok=True)
    source_path = case_dir / "source.population.json"
    _write_population(
        source_path, SOURCE_FACTS if facts is None else facts, source="fixture"
    )
    document_path = case_dir / "document.md"
    document_path.write_text(document, encoding="utf-8")
    applicable_path = artifacts / f"{STEM}.applicable.json"

    (case_dir / "document.manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "document": "document.md",
                "document_sha256": _sha256(document_path),
                "model": MODEL.name,
                "model_sha256": _sha256(MODEL),
                "source_population": "source.population.json",
                "source_population_sha256": _sha256(source_path),
                "applicable_sha256": _sha256(applicable_path),
                "renderer_skill": "gnd-render-doc",
                "renderer_skill_version": "0.1.0",
                "executing_model": "test-fixture",
                "distractors": [
                    {"kind": "out-of-model", "text": "Room R1 has 20 seats"}
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    if skipped_reason is not None:
        (case_dir / "extraction.skipped.json").write_text(
            json.dumps({"reason": skipped_reason}, indent=2) + "\n", encoding="utf-8"
        )
        return case_dir

    extracted_path = case_dir / "extracted.population.json"
    _write_population(
        extracted_path,
        FAITHFUL_FACTS if extracted is None else extracted,
        source="agent-output",
    )
    sidecar = {
        "schema_version": 1,
        "population": "extracted.population.json",
        "population_sha256": _sha256(extracted_path),
        "model": MODEL.name,
        "model_sha256": _sha256(MODEL),
        "projection_sha256": _sha256(artifacts / f"{STEM}.projection.schema.json"),
        "document": "document.md",
        "document_sha256": _sha256(document_path),
        "skill": "gnd-extract",
        "skill_version": "0.1.0",
        "executing_model": "test-fixture",
    }
    sidecar.update(sidecar_overrides or {})
    (case_dir / "extracted.population.extraction.json").write_text(
        json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return case_dir


def run_fidelity(
    cases: Path, artifacts: Path, out: Path | None = None, expect: int = 0
) -> dict[str, Any]:
    argv = [
        "fidelity",
        str(MODEL),
        "--cases",
        str(cases),
        "--artifacts",
        str(artifacts),
        "--format",
        "json",
    ]
    if out is not None:
        argv += ["--out", str(out)]
    code = main(argv)
    assert code == expect, f"gnd fidelity exited {code}, expected {expect}"
    if out is None:
        return {}
    return json.loads(out.read_text(encoding="utf-8"))


def test_applicable_artifact_cannot_redefine_model_obligations(
    tmp_path: Path, artifacts: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cases = tmp_path / "cases"
    case = write_case(cases / "tampered", artifacts)
    applicable_path = artifacts / f"{STEM}.applicable.json"
    payload = json.loads(applicable_path.read_text(encoding="utf-8"))
    payload["fact_types"] = []
    applicable_path.write_text(json.dumps(payload), encoding="utf-8")
    index_path = artifacts / f"{STEM}.artifacts.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["artifacts"][f"{STEM}.applicable.json"]["sha256"] = _sha256(
        applicable_path
    )
    index_path.write_text(json.dumps(index), encoding="utf-8")

    manifest_path = case / "document.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["applicable_sha256"] = _sha256(applicable_path)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert main(
        [
            "doccheck",
            str(MODEL),
            str(manifest_path),
            "--artifacts",
            str(artifacts),
        ]
    ) == 3
    assert "does not match the canonical disposition" in capsys.readouterr().out

    assert run_fidelity(cases, artifacts, expect=3) == {}
    assert "does not match the canonical disposition" in capsys.readouterr().out


def test_doccheck_requires_boundary_delimited_role_fillers(
    tmp_path: Path, artifacts: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    case = write_case(tmp_path / "case", artifacts)
    document_path = case / "document.md"
    document_path.write_text(
        DOCUMENT.replace("Person 1", "Person 10").replace("person 1", "person 10"),
        encoding="utf-8",
    )
    manifest_path = case / "document.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["document_sha256"] = _sha256(document_path)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert main(
        [
            "doccheck",
            str(MODEL),
            str(manifest_path),
            "--artifacts",
            str(artifacts),
        ]
    ) == 3
    assert "reference value 1 is not mentioned" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("fact_type", "roles", "message"),
    [
        ("bogus", {"person": 1}, "unknown fact type 'bogus'"),
        (
            "person_teaches_course",
            {"person": 1},
            "must supply exactly the declared roles",
        ),
    ],
)
def test_doccheck_rejects_uncheckable_absent_fact_distractors(
    tmp_path: Path,
    artifacts: Path,
    capsys: pytest.CaptureFixture[str],
    fact_type: str,
    roles: dict[str, Any],
    message: str,
) -> None:
    case = write_case(tmp_path / "case", artifacts)
    document_path = case / "document.md"
    document_path.write_text(DOCUMENT + "A distractor sentence.\n", encoding="utf-8")
    manifest_path = case / "document.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["document_sha256"] = _sha256(document_path)
    manifest["distractors"].append(
        {
            "kind": "absent-fact",
            "text": "A distractor sentence.",
            "fact_type": fact_type,
            "roles": roles,
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert main(
        [
            "doccheck",
            str(MODEL),
            str(manifest_path),
            "--artifacts",
            str(artifacts),
        ]
    ) == 3
    assert message in capsys.readouterr().out


def test_doccheck_recomputes_the_manifest_model_digest(
    tmp_path: Path, artifacts: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    case = write_case(tmp_path / "case", artifacts)
    manifest_path = case / "document.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["model_sha256"] = "f" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert main(
        [
            "doccheck",
            str(MODEL),
            str(manifest_path),
            "--artifacts",
            str(artifacts),
        ]
    ) == 3
    assert "binding: model_sha256 records" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("field", "filename"),
    [("document", "document.md"), ("source_population", "source.population.json")],
)
def test_doccheck_refuses_symlinked_manifest_inputs(
    tmp_path: Path,
    artifacts: Path,
    capsys: pytest.CaptureFixture[str],
    field: str,
    filename: str,
) -> None:
    case = write_case(tmp_path / "case", artifacts)
    outside = tmp_path / f"outside-{filename}"
    target = case / filename
    outside.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(outside)

    assert main(
        [
            "doccheck",
            str(MODEL),
            str(case / "document.manifest.json"),
            "--artifacts",
            str(artifacts),
        ]
    ) == 3
    output = capsys.readouterr().out
    assert field in output
    assert "symlink" in output


@pytest.fixture
def payload(tmp_path: Path, artifacts: Path) -> dict[str, Any]:
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts)
    return run_fidelity(cases, artifacts, tmp_path / "f.json")


def _walk_keys(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            found.append(str(key))
            found.extend(_walk_keys(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_keys(item))
    return found


# --------------------------------------------------------------------------- #
# PANEL-1 — un-publishability is a schema fact, in three named pieces
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "inject",
    ["top", "row", "calibration"],
    ids=("top-level", "per-fact-type-row", "calibration-block"),
)
def test_fidelity_payload_refuses_interval_fields(
    payload: dict[str, Any], inject: str
) -> None:
    """R-11′: no interval may exist while uncalibrated — and "may not" is
    enforced by ``additionalProperties: false`` at every object level, not by
    the builder declining to write one.

    Mutation (recorded): injecting ``interval`` / ``ci`` / ``bootstrap`` into a
    BUILT payload must red schema validation. A builder-side omission would
    leave the door open for the next caller; a closed schema shuts it for
    every caller at once.
    """
    from gnd.fidelity.report import load_fidelity_schema

    schema = load_fidelity_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    tampered = json.loads(json.dumps(payload))
    if inject == "top":
        tampered["interval"] = [0.4, 0.9]
    elif inject == "row":
        tampered["per_fact_type"][0]["ci"] = [0.4, 0.9]
    else:
        tampered["calibration"]["bootstrap"] = {"resamples": 1000}

    with pytest.raises(SchemaValidationError):
        Draft202012Validator(schema).validate(tampered)

    # And the vocabulary is absent from the contract itself, so no future
    # payload can carry one under a schema that permits it.
    schema_text = json.dumps(schema)
    for forbidden in ('"interval"', '"ci"', '"bootstrap"', '"confidence_interval"'):
        assert forbidden not in schema_text, (
            f"the schema declares {forbidden}; while R-12's calibration set is "
            f"deferred there is nothing an interval could be computed from"
        )


def test_calibration_state_is_schema_required(payload: dict[str, Any]) -> None:
    """PANEL-1: the calibration block is REQUIRED, its state is a const, and
    its two unquantified biases are fixed.

    Mutation (recorded): deleting ``calibration`` from a built payload reds
    here. So does relabelling the state ``"calibrated"`` — the escape hatch a
    future caller would reach for first.
    """
    from gnd.fidelity.report import load_fidelity_schema

    schema = load_fidelity_schema()
    assert payload["calibration"] == {
        "state": "uncalibrated",
        "unquantified_biases": [
            "self-consistency",
            "unmentioned-entity-recall",
            "relation-permutation",
        ],
    }

    for mutate in (
        lambda doc: doc.pop("calibration"),
        lambda doc: doc["calibration"].__setitem__("state", "calibrated"),
        lambda doc: doc["calibration"].__setitem__("unquantified_biases", []),
    ):
        tampered = json.loads(json.dumps(payload))
        mutate(tampered)
        with pytest.raises(SchemaValidationError):
            Draft202012Validator(schema).validate(tampered)


def test_no_single_bias_can_be_dropped_from_the_payload(payload: dict[str, Any]) -> None:
    """The asymmetry the ``const``→``contains`` change (owner decision, UAT item
    1) had to preserve: a bias may be ADDED without a schema bump, but none may
    be REMOVED.

    ``[]`` reddening proves almost nothing — it violates all three `contains`
    clauses at once, so a schema that required only ONE of them would still pass
    that check. This drops each member individually, which is the mutation that
    distinguishes a real per-bias pin from a single-clause one.

    The direction matters: dropping a bias flatters the number and must be
    impossible; adding one makes it look worse and needs no protection.
    """
    from gnd.fidelity.report import UNQUANTIFIED_BIASES, load_fidelity_schema

    schema = load_fidelity_schema()
    assert len(UNQUANTIFIED_BIASES) == 3, "a new bias needs its own drop-case here"

    for dropped in UNQUANTIFIED_BIASES:
        tampered = json.loads(json.dumps(payload))
        tampered["calibration"]["unquantified_biases"] = [
            bias for bias in UNQUANTIFIED_BIASES if bias != dropped
        ]
        with pytest.raises(SchemaValidationError):
            Draft202012Validator(schema).validate(tampered)

    # ...and the permitted direction genuinely is permitted, or the change bought
    # nothing over the `const` it replaced.
    widened = json.loads(json.dumps(payload))
    widened["calibration"]["unquantified_biases"] = [*UNQUANTIFIED_BIASES, "a-bias-found-later"]
    Draft202012Validator(schema).validate(widened)


def test_publishable_cannot_be_true(payload: dict[str, Any]) -> None:
    """PANEL-1: ``publishable`` is a required const ``false``.

    Mutation (recorded): flipping the field to ``true`` reds schema
    validation. The round trip measures the round trip — the renderer authored
    the ground truth — and until R-12's calibration set exists there is no
    evidence that would justify the other value.
    """
    from gnd.fidelity.report import load_fidelity_schema

    schema = load_fidelity_schema()
    assert payload["publishable"] is False

    tampered = json.loads(json.dumps(payload))
    tampered["publishable"] = True
    with pytest.raises(SchemaValidationError):
        Draft202012Validator(schema).validate(tampered)


# --------------------------------------------------------------------------- #
# R-11′ / D-01 — every rate with its base, no blended number, no verdict channel
# --------------------------------------------------------------------------- #


def test_every_rate_ships_with_numerator_and_denominator(
    payload: dict[str, Any]
) -> None:
    """R-11′: a rate is never published alone. Each of the three rates is an
    object ``{numerator, denominator, rate}`` whose ``rate`` is ``None`` exactly
    when the denominator is zero (``measure/score.py:294-303``'s rule).

    A bare float would be unauditable: 1.0 over one fact and 1.0 over two
    hundred are the same character string.
    """
    assert payload["per_fact_type"], "no rows at all is not a passing state"
    for row in payload["per_fact_type"]:
        for name in ("precision", "recall", "unresolved"):
            entry = row[name]
            assert set(entry) == {"numerator", "denominator", "rate"}
            if entry["denominator"] == 0:
                assert entry["rate"] is None
            else:
                assert entry["rate"] == pytest.approx(
                    entry["numerator"] / entry["denominator"]
                )
        matched = row["matched"]
        assert (
            matched["tp"]
            + matched["unmatched"]
            + matched["unresolved"]
            + matched["ambiguous"]
            == matched["extracted_total"]
        )
        assert matched["tp"] + matched["missed"] == matched["source_total"]


def test_no_blended_accuracy_number(payload: dict[str, Any]) -> None:
    """D-01: fidelity is reported PER FACT TYPE and nowhere else.

    A single "extraction accuracy" figure is the number that cannot come out
    badly — it averages the fact types the extractor found easy over the ones
    it never attempted. The schema is closed, so confirming the obvious names
    are absent is a real check rather than a spot sample.

    Asserted over KEY NAMES, not over the flattened text: a substring sweep
    reports "f1" against a sha256 digest, which is the shape of a guard that
    fails for reasons unrelated to its subject.
    """
    keys = {key.lower() for key in _walk_keys(payload)}
    for forbidden in (
        "accuracy",
        "overall",
        "overall_rate",
        "overall_precision",
        "blended",
        "f1",
        "macro",
        "micro",
        "aggregate",
        "score",
    ):
        assert forbidden not in keys, f"the payload leaked an aggregate: {forbidden}"
    assert "accuracy" not in json.dumps(payload).lower()

    ids = [row["id"] for row in payload["per_fact_type"]]
    assert ids == sorted(ids), "rows sorted by id keeps the emission byte-stable"


def test_fidelity_payload_carries_no_verdict_channel(payload: dict[str, Any]) -> None:
    """R-03″'s dual, and the exact mirror of plan 03's
    ``test_checker_pass_is_not_faithfulness``: no verdict key may appear at any
    depth of a fidelity payload, just as no rate key may appear at any depth of
    a verify payload.

    The two lanes answer different questions — "does this population satisfy
    the model" and "does this extraction reflect the document" — and a single
    output carrying both invites reading either as the other.
    """
    keys = set(_walk_keys(payload))
    for forbidden in (
        "verdict",
        "verdicts",
        "acceptance_ready",
        "counts",
        "band",
        "coverage_fraction",
    ):
        assert forbidden not in keys, (
            f"a fidelity payload carried {forbidden!r} — the verify channel and "
            f"the fidelity channel never mix (R-03″)"
        )


# --------------------------------------------------------------------------- #
# fail-closed inputs and an honest census (R-10′, R-13′)
# --------------------------------------------------------------------------- #


def test_fidelity_fails_closed_without_applicable_artifact(
    tmp_path: Path, artifacts: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The applicable set is the denominator's definition, so its absence is
    exit 66 (EX_NOINPUT) and never a run over "whatever fact types happened to
    appear".

    Without this, a missing artifact reads as full coverage of an empty
    applicable set — the flattered denominator the phase is named after.
    """
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts)
    (artifacts / f"{STEM}.applicable.json").unlink()

    code = main(
        [
            "fidelity",
            str(MODEL),
            "--cases",
            str(cases),
            "--artifacts",
            str(artifacts),
            "--format",
            "json",
        ]
    )

    assert code == 66
    assert f"{STEM}.applicable.json" in capsys.readouterr().out


def test_fidelity_census_never_folds_failures_into_recall(
    tmp_path: Path, artifacts: Path
) -> None:
    """R-13′/D-02: failed and skipped cases are COUNTED, never folded.

    Mutation (recorded): scoring a failed case as zero true positives lowers
    every rate and hides the failure inside the number; dropping it from the
    census hides it entirely. Adding a failed and a skipped case must leave
    every recall denominator byte-for-byte unchanged while the census moves.
    """
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts)
    before = run_fidelity(cases, artifacts, tmp_path / "before.json")

    # A case whose sidecar was never written: the handoff is broken, so it is
    # `failed` with a reason — not an extraction that found nothing.
    broken = write_case(cases / "case-broken", artifacts)
    (broken / "extracted.population.extraction.json").unlink()
    write_case(cases / "case-skipped", artifacts, skipped_reason="no key in CI")

    after = run_fidelity(cases, artifacts, tmp_path / "after.json")

    assert before["cases"] == {"ran": 1, "skipped": 0, "failed": 0, "reasons": []}
    assert after["cases"]["ran"] == 1
    assert after["cases"]["failed"] == 1
    assert after["cases"]["skipped"] == 1
    reasons = {entry["case"]: entry for entry in after["cases"]["reasons"]}
    assert reasons["case-broken"]["state"] == "failed"
    assert reasons["case-broken"]["reason"]
    assert reasons["case-skipped"]["state"] == "skipped"
    assert reasons["case-skipped"]["reason"] == "no key in CI"

    def bases(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            row["id"]: (
                row["recall"]["denominator"],
                row["precision"]["denominator"],
                row["recall"]["numerator"],
            )
            for row in doc["per_fact_type"]
        }

    assert bases(after) == bases(before), (
        "a failed or skipped case moved a denominator — failures must be "
        "counted in the census and nowhere else"
    )


def test_two_fidelity_runs_are_byte_identical(tmp_path: Path, artifacts: Path) -> None:
    """No timestamp, sorted keys, pre-sorted lists: the publication-pinning
    promise ``gnd measure`` already keeps, kept here too."""
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts)
    write_case(cases / "case-b", artifacts)
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    run_fidelity(cases, artifacts, first)
    run_fidelity(cases, artifacts, second)

    assert first.read_bytes() == second.read_bytes()
    assert "timestamp" not in first.read_text(encoding="utf-8")
    assert "generated_at" not in first.read_text(encoding="utf-8")


def test_a_case_set_spanning_two_model_digests_is_refused(
    tmp_path: Path, artifacts: Path
) -> None:
    """C4's analog: ``gnd fidelity`` is model-relative, so one payload
    represents exactly one model. A mixed case set is a usage error (64), never
    a silently-measured subset."""
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts)
    write_case(
        cases / "case-b", artifacts, sidecar_overrides={"model_sha256": "f" * 64}
    )

    assert (
        main(
            [
                "fidelity",
                str(MODEL),
                "--cases",
                str(cases),
                "--artifacts",
                str(artifacts),
            ]
        )
        == 64
    )


def test_a_tampered_extraction_exits_3(tmp_path: Path, artifacts: Path) -> None:
    """C6 inside a case: the sidecar's ``population_sha256`` is recomputed and
    compared against the bytes on disk. A digest that does not describe the
    file is a tamper signal, not a census state — measuring over it would
    publish a number about a file nobody can identify."""
    cases = tmp_path / "cases"
    case = write_case(cases / "case-a", artifacts)
    population = case / "extracted.population.json"
    population.write_text(
        population.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )

    assert (
        main(
            [
                "fidelity",
                str(MODEL),
                "--cases",
                str(cases),
                "--artifacts",
                str(artifacts),
            ]
        )
        == 3
    )


def test_fidelity_rejects_a_stale_projection_digest(
    tmp_path: Path, artifacts: Path
) -> None:
    cases = tmp_path / "cases"
    write_case(
        cases / "case-a",
        artifacts,
        sidecar_overrides={"projection_sha256": "f" * 64},
    )

    assert run_fidelity(cases, artifacts, expect=3) == {}


def test_evidence_quotes_a_verbatim_extracted_fact(payload: dict[str, Any]) -> None:
    """D-22: no published number without one raw artifact a reader can open.

    The excerpt names its case and quotes an extracted fact verbatim, and every
    case in the census carries its digests — so the reader can re-derive the
    row rather than trust it.
    """
    evidence = payload["evidence"]
    assert evidence["cases"], "the evidence names the cases the rates came from"
    for entry in evidence["cases"]:
        assert not Path(entry["case"]).is_absolute()
        assert len(entry["extracted_population_sha256"] or "") in (0, 64)
    excerpt = evidence["excerpt"]
    assert excerpt["case"] == "case-a"
    assert excerpt["fact_type"] in {row["id"] for row in payload["per_fact_type"]}
    assert isinstance(excerpt["fact"], dict) and excerpt["fact"]


def test_evidence_quotes_the_fact_with_the_advertised_outcome(
    tmp_path: Path, artifacts: Path
) -> None:
    cases = tmp_path / "cases"
    extra = {key: [dict(fact) for fact in facts] for key, facts in FAITHFUL_FACTS.items()}
    extra["room_has_seats"].append({"room": "R1", "seats": 21})
    write_case(cases / "case-a", artifacts, extracted=extra)
    out = tmp_path / "fidelity.json"

    result = run_fidelity(cases, artifacts, out)

    assert result["evidence"]["excerpt"] == {
        "case": "case-a",
        "fact_type": "room_has_seats",
        "outcome": "unmatched",
        "source": "extracted",
        "fact": {"room": "R1", "seats": 21},
        "reason": None,
    }


def test_ran_case_without_extracted_facts_uses_source_evidence(
    tmp_path: Path, artifacts: Path
) -> None:
    cases = tmp_path / "cases"
    write_case(cases / "case-a", artifacts, extracted={})
    out = tmp_path / "fidelity.json"

    result = run_fidelity(cases, artifacts, out)

    excerpt = result["evidence"]["excerpt"]
    assert excerpt["outcome"] == "missed"
    assert excerpt["source"] == "source"
    assert excerpt["fact"] in SOURCE_FACTS[excerpt["fact_type"]]


@pytest.mark.parametrize(
    "marker",
    [
        {"reason": None},
        {"reason": ""},
        {"reason": "   "},
        {"reason": 7},
        {"reason": "intentional", "extra": True},
    ],
)
def test_malformed_skip_markers_are_failed_not_skipped(
    tmp_path: Path, artifacts: Path, marker: dict[str, Any]
) -> None:
    cases = tmp_path / "cases"
    case = write_case(cases / "case-a", artifacts, skipped_reason="temporary")
    (case / "extraction.skipped.json").write_text(json.dumps(marker), encoding="utf-8")
    out = tmp_path / "fidelity.json"

    result = run_fidelity(cases, artifacts, out)

    assert result["cases"]["ran"] == 0
    assert result["cases"]["skipped"] == 0
    assert result["cases"]["failed"] == 1


def test_fidelity_text_neutralizes_case_names_and_reasons(
    tmp_path: Path, artifacts: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cases = tmp_path / "cases"
    case = write_case(
        cases / "case\npublishable: true",
        artifacts,
        skipped_reason="because\npublishable: true",
    )
    assert case.is_dir()

    assert main(
        [
            "fidelity",
            str(MODEL),
            "--cases",
            str(cases),
            "--artifacts",
            str(artifacts),
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "case\\npublishable: true" in output
    assert "because\\npublishable: true" in output
    assert "\npublishable: true\n" not in output
    assert "publishable: false" in output
