"""``gnd verify MODEL POPULATION`` — composition, state machine, header
ownership, stage-qualified acceptance (R-03″, R-02, R-13′, PANEL-2, PANEL-6).

``verify`` composes popvalidate → check over a PRE-EXTRACTED population file —
it never orchestrates extraction (R-03″); the skill-to-code handoff is a file
on disk plus a sidecar (R-04‴). Its value over ``gnd check``: provenance on
every verdict plus the always-present ``extraction`` metadata block, which is
its OWN channel, separate from the checker outcome (PANEL-2) — so a checker
pass over an uncalibrated extraction can never read as proof of faithfulness.

Every test here drives the CLI and asserts on the EMITTED payload (G-5), and
every payload is validated against ``report.schema.json`` with
``command == "verify"`` — the same discipline as ``test_report_json.py``.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_gnd_text as _run_cli
from support.digests import sha256_file as _sha256
from support.documents import write_population

from gnd import cli
from gnd.cli import main
from gnd.report import load_report_schema

SKELETON = Path(__file__).parent / "fixtures" / "skeleton"
MODEL = SKELETON / "model.orm.yaml"
POP_BAD = SKELETON / "population.bad.yaml"

#: The full sorted fact-type id list of the skeleton model — what PANEL-6's
#: header ownership recomputes from the model and enforces on the ran path.
ALL_FACT_TYPES = [
    "movie_has_title",
    "movie_released_in_year",
    "movie_sequel_of_movie",
]

#: The rate-shaped keys R-03″ bans from every verify payload at ANY depth.
FORBIDDEN_RATE_KEYS = {"fidelity", "precision", "recall", "unresolved"}


def _payload(*args: str) -> tuple[dict, int]:
    argv = list(args)
    if argv and argv[0] == "verify" and "--no-extraction" not in argv and "--artifacts" not in argv:
        argv.extend(["--artifacts", str(Path(argv[2]).parent / "artifacts")])
    result = _run_cli(*argv, "--format", "json")
    try:
        return json.loads(result.stdout), result.returncode
    except json.JSONDecodeError as error:
        pytest.fail(
            f"--format json must emit a parseable payload on every verify exit "
            f"path, but {args} produced none ({error}).\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    return Draft202012Validator(load_report_schema())


def _conforming_population(**header_overrides: Any) -> dict:
    """A conforming skeleton population with the AGENT-OUTPUT header contract
    (source + full covers) that `gnd extract`'s header_template pins."""
    header: dict[str, Any] = {
        "model": MODEL.as_posix(),
        "source": "agent-output",
        "covers": list(ALL_FACT_TYPES),
    }
    header.update(header_overrides)
    return {
        "population": header,
        "instances": {"movie": [1, 2]},
        "facts": {
            "movie_has_title": [
                {"movie": 1, "title": "The Departed"},
                {"movie": 2, "title": "Infernal Affairs"},
            ],
            "movie_released_in_year": [
                {"movie": 1, "year": 2006},
                {"movie": 2, "year": 2002},
            ],
            "movie_sequel_of_movie": [{"sequel": 1, "original": 2}],
        },
    }


def _write_population(tmp_path: Path, doc: dict, name: str = "pop.json") -> Path:
    return write_population(tmp_path, json.dumps(doc), name=name)


def _write_sidecar(
    population_path: Path, model_path: Path = MODEL, **overrides: Any
) -> Path:
    """A valid extraction sidecar beside its population, digests computed over
    the REAL file bytes (C6)."""
    artifacts = population_path.parent / "artifacts"
    assert main(["extract", str(model_path), "--out", str(artifacts)]) == 0
    stem = model_path.name.removesuffix(".orm.yaml")
    projection = artifacts / f"{stem}.projection.schema.json"
    (population_path.parent / "doc.md").write_bytes(b"doc")
    doc: dict[str, Any] = {
        "schema_version": 1,
        "population": population_path.name,
        "population_sha256": _sha256(population_path),
        "model": model_path.name,
        "model_sha256": _sha256(model_path),
        "projection_sha256": _sha256(projection),
        "document": "doc.md",
        "document_sha256": hashlib.sha256(b"doc").hexdigest(),
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "claude-fable-5",
    }
    doc.update(overrides)
    sidecar_path = population_path.with_suffix(".extraction.json")
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")
    return sidecar_path


def _issue_rule_ids(payload: dict) -> set[str]:
    return {issue["rule_id"] for issue in payload["issues"]}


# --- R-13′: the state machine ---


def test_verify_absent_sidecar_is_failed_never_skipped(tmp_path: Path) -> None:
    """No --no-extraction and no sidecar file → ``extraction.state`` is
    ``failed`` at exit 3 with ``extraction:sidecar-missing`` (R-13′,
    T-02.1-11: an unrun extraction must never read as green).

    Mutation this test guards: mapping ABSENCE to ``skipped`` (or to a clean
    exit 0). ``skipped`` is reserved for the intentional ``--no-extraction``
    opt-out; a missing sidecar reading as skipped would make a silently-lost
    handoff file look like a deliberate choice — the exact repudiation
    T-02.1-11 names. Rewiring the missing-sidecar arm to
    ``state="skipped"``/checker-band exit reds this test on all three
    assertions.
    """
    pop = _write_population(tmp_path, _conforming_population())
    payload, code = _payload("verify", str(MODEL), str(pop))
    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:sidecar-missing" in _issue_rule_ids(payload)


def test_verify_no_extraction_is_the_only_skip_path(tmp_path: Path) -> None:
    """``skipped`` is written ONLY by the intentional ``--no-extraction``
    opt-out (R-13′), with the reason recorded; combining the opt-out with
    ``--sidecar`` is a usage contradiction → exit 64, no payload."""
    pop = _write_population(tmp_path, _conforming_population())
    payload, code = _payload("verify", str(MODEL), str(pop), "--no-extraction")
    assert code == 0
    assert payload["extraction"]["state"] == "skipped"
    assert payload["extraction"]["reason"] == "extraction opted out (--no-extraction)"
    assert payload["acceptance_ready"] is True

    conflict = _run_cli(
        "verify",
        str(MODEL),
        str(pop),
        "--no-extraction",
        "--sidecar",
        str(tmp_path / "s.json"),
    )
    assert conflict.returncode == 64
    assert conflict.stdout.strip() == "", "exit 64 deliberately emits no payload"


def test_verify_sidecar_invalid_exits_3(tmp_path: Path) -> None:
    """A sidecar with unknown fields / bad shape → ``extraction:sidecar-invalid``
    at exit 3, state ``failed`` — extra="forbid" surfaced at the command level."""
    pop = _write_population(tmp_path, _conforming_population())
    sidecar = _write_sidecar(pop, fidelity=1.0)
    payload, code = _payload("verify", str(MODEL), str(pop), "--sidecar", str(sidecar))
    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:sidecar-invalid" in _issue_rule_ids(payload)


def test_verify_binding_mismatch_exits_3(tmp_path: Path) -> None:
    """A ``population_sha256`` or ``model_sha256`` that does not match the file
    bytes → ``extraction:binding-mismatch`` at exit 3, state ``failed`` — the
    C6 measure precedent (T-02.1-10: a population passed off as an extraction
    it is not). Dropping the recompute-and-compare reds both halves."""
    pop = _write_population(tmp_path, _conforming_population())
    _write_sidecar(pop, population_sha256=hashlib.sha256(b"other").hexdigest())
    payload, code = _payload("verify", str(MODEL), str(pop))
    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:binding-mismatch" in _issue_rule_ids(payload)

    _write_sidecar(pop, model_sha256=hashlib.sha256(b"other-model").hexdigest())
    payload, code = _payload("verify", str(MODEL), str(pop))
    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:binding-mismatch" in _issue_rule_ids(payload)


@pytest.mark.parametrize("target", ["document", "projection"])
def test_verify_recomputes_every_published_digest(tmp_path: Path, target: str) -> None:
    pop = _write_population(tmp_path, _conforming_population())
    _write_sidecar(pop)
    if target == "document":
        (tmp_path / "doc.md").write_bytes(b"changed document")
    else:
        (tmp_path / "artifacts" / "model.projection.schema.json").write_bytes(
            b"changed projection"
        )

    payload, code = _payload("verify", str(MODEL), str(pop))

    assert code == 3
    assert "extraction:binding-mismatch" in _issue_rule_ids(payload)


def test_verify_refuses_a_sidecar_document_symlink(tmp_path: Path) -> None:
    pop = _write_population(tmp_path, _conforming_population())
    outside = tmp_path.parent / "outside-document.txt"
    outside.write_bytes(b"outside")
    _write_sidecar(
        pop,
        document_sha256=hashlib.sha256(b"outside").hexdigest(),
    )
    document = tmp_path / "doc.md"
    document.unlink()
    document.symlink_to(outside)

    payload, code = _payload("verify", str(MODEL), str(pop))

    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:binding-mismatch" in _issue_rule_ids(payload)


def test_verify_binds_the_sidecar_population_to_the_argument(tmp_path: Path) -> None:
    pop = _write_population(tmp_path, _conforming_population())
    other = _write_population(tmp_path, _conforming_population(), name="other.json")
    _write_sidecar(
        pop,
        population=other.name,
        population_sha256=_sha256(other),
    )

    payload, code = _payload("verify", str(MODEL), str(pop))

    assert code == 3
    assert payload["extraction"]["state"] == "failed"
    assert "extraction:binding-mismatch" in _issue_rule_ids(payload)


# --- PANEL-6: header ownership ---


def test_verify_rejects_covers_omission_gaming(tmp_path: Path) -> None:
    """On the ran path, ``covers`` must equal ALL fact-type ids and ``source``
    must be ``agent-output`` — both RECOMPUTED from the model, never trusted
    from artifacts (PANEL-6). Omitting one fact type from ``covers`` is the
    vacuity-gaming move this closes: an uncovered fact type reads as
    undeclared, so its constraints could go vacuous instead of failing."""
    gamed = _conforming_population(covers=ALL_FACT_TYPES[:-1])
    pop = _write_population(tmp_path, gamed)
    _write_sidecar(pop)
    payload, code = _payload("verify", str(MODEL), str(pop))
    assert code == 3
    assert "extraction:header-mismatch" in _issue_rule_ids(payload)
    assert payload["acceptance_ready"] is False

    wrong_source = _conforming_population(source="fixture")
    pop2 = _write_population(tmp_path, wrong_source, name="pop2.json")
    _write_sidecar(pop2)
    payload, code = _payload("verify", str(MODEL), str(pop2))
    assert code == 3
    assert "extraction:header-mismatch" in _issue_rule_ids(payload)


@pytest.mark.parametrize(
    "override",
    [
        {"model": "different-spelling.orm.yaml"},
        {"label": "conforming"},
        {"covers": list(reversed(ALL_FACT_TYPES))},
    ],
)
def test_verify_rejects_every_non_template_header_shape(
    tmp_path: Path, override: dict[str, Any]
) -> None:
    pop = _write_population(tmp_path, _conforming_population(**override))
    _write_sidecar(pop)

    payload, code = _payload("verify", str(MODEL), str(pop))

    assert code == 3
    assert "extraction:header-mismatch" in _issue_rule_ids(payload)


# --- R-02: modality routing through the verify path ---


def test_verify_alethic_fail_and_deontic_warning_route_unchanged(
    tmp_path: Path,
) -> None:
    """Alethic violation → exit 1; deontic-only violation → exit 0 with warning
    verdicts and non-empty CNL messages — R-02 proven END-TO-END through the
    verify path without rebuilding modality routing (the band decision stays
    ``checker.band`` via ``_band``).

    The deontic case is a skeleton population violating ONLY the deontic year
    value-range constraint (year 1520, outside [1888, 2100] — the D-03
    warning-path constraint at ``constraints[0]``); full_vocabulary cannot
    serve here because its alethic textual constraint parks every population at
    band 4."""
    payload, code = _payload("verify", str(MODEL), str(POP_BAD), "--no-extraction")
    assert code == 1
    assert payload["outcome"] == "violated"
    assert any(v["verdict"] == "fail" for v in payload["verdicts"])

    deontic_only = _conforming_population()
    deontic_only["facts"]["movie_released_in_year"][0]["year"] = 1520
    pop = _write_population(tmp_path, deontic_only)
    payload, code = _payload("verify", str(MODEL), str(pop), "--no-extraction")
    assert code == 0
    warnings = [v for v in payload["verdicts"] if v["verdict"] == "warning"]
    assert warnings, "the deontic violation must surface as a warning verdict"
    assert all(v["message"].strip() for v in warnings), (
        "warning verdicts must carry non-empty CNL feedback (R-02)"
    )
    assert all(v["modality"] == "deontic" for v in warnings)


# --- PANEL-2: stage-qualified acceptance ---


def _walk_keys(node: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            keys.add(key)
            keys |= _walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            keys |= _walk_keys(item)
    return keys


def test_checker_pass_is_not_faithfulness(tmp_path: Path) -> None:
    """A checker pass over an extraction is CHECKER-stage acceptance, never
    proof of faithfulness (PANEL-2).

    The scope proposal's "garbage → exit 3/1, never a silent pass" was an
    overclaim: popvalidate + checker reject *malformed* and *violating*, not
    *unfaithful* — a hallucinated, well-shaped, conforming extraction exits 0
    and is an extractor error by definition. So the payload separates the two
    channels — ``acceptance_ready`` stays the D-08 band-0 checker claim,
    ``extraction.state`` is its own channel — and NO rate-shaped key
    (``fidelity``/``precision``/``recall``/``unresolved``) may exist at any
    depth (R-03″ hard rule, D-01: never a fidelity rate in a verify payload).
    """
    pop = _write_population(tmp_path, _conforming_population())
    _write_sidecar(pop)
    payload, code = _payload("verify", str(MODEL), str(pop))
    assert code == 0
    assert payload["acceptance_ready"] is True
    assert payload["extraction"]["state"] == "ran"
    assert payload["extraction"]["skill"] == "gnd-extract"
    assert payload["extraction"]["executing_model"] == "claude-fable-5"

    overlap = _walk_keys(payload) & FORBIDDEN_RATE_KEYS
    assert not overlap, (
        f"a verify payload must never carry a rate-shaped key (R-03″); "
        f"found {sorted(overlap)}"
    )


# --- the payload contract ---


def test_verify_payload_validates_against_report_schema(
    validator: Draft202012Validator, tmp_path: Path
) -> None:
    """Every verify exit path emits a payload that validates against
    ``report.schema.json`` with ``command == "verify"`` — the exact sweep
    ``test_report_json.py`` runs for check/validate, extended to verify."""
    pop = _write_population(tmp_path, _conforming_population())
    orphan = _write_population(
        tmp_path, _conforming_population(), name="orphan.json"
    )

    cases: list[tuple[list[str], int]] = [
        (["verify", str(MODEL), str(orphan)], 3),  # sidecar-missing
        (["verify", str(MODEL), str(pop), "--no-extraction"], 0),  # skipped
        (["verify", str(MODEL), str(POP_BAD), "--no-extraction"], 1),  # alethic
    ]
    _write_sidecar(pop)
    cases.append((["verify", str(MODEL), str(pop)], 0))  # ran

    gamed = _conforming_population(covers=ALL_FACT_TYPES[:-1])
    pop_gamed = _write_population(tmp_path, gamed, name="gamed.json")
    _write_sidecar(pop_gamed)
    cases.append((["verify", str(MODEL), str(pop_gamed)], 3))  # header-mismatch

    pop_bound = _write_population(tmp_path, _conforming_population(), name="bound.json")
    _write_sidecar(pop_bound, population_sha256=hashlib.sha256(b"z").hexdigest())
    cases.append((["verify", str(MODEL), str(pop_bound)], 3))  # binding-mismatch

    for argv, expected in cases:
        payload, code = _payload(*argv)
        assert code == expected, f"{argv}: expected exit {expected}, got {code}"
        assert payload["command"] == "verify"
        assert payload["exit_code"] == expected
        errors = sorted(validator.iter_errors(payload), key=lambda e: e.json_path)
        assert not errors, (
            f"{argv} payload must validate against report.schema.json; violations: "
            + "; ".join(f"{e.json_path}: {e.message}" for e in errors)
        )


def test_verify_band_is_delegated_to_the_one_owner() -> None:
    """Source-level acceptance: ``_cmd_verify`` delegates its band decision to
    ``_band(report)`` (checker.band, the ONE owner) and never re-derives it
    with a comprehension over verdicts."""
    source = inspect.getsource(cli._cmd_verify)
    start = source.index("def _cmd_verify")
    end = len(source)
    body = source[start:end]
    assert "_band(report)" in body
    assert "for verdict in report.verdicts" not in body
