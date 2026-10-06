"""``--format json`` payload contract (D-10, D-11, D-12).

One fixed-shape record on every exit path a verdict can reach — 0, 1, 2, 3, 4
and 70 — validated against ``src/gnd/report.schema.json``. Exit 64 deliberately
emits none.

The load-bearing assertion in this module is
``test_json_counts_match_the_text_renderer``: it proves the JSON payload is
computed FROM the same ``CheckReport`` the text renderer prints, not beside it
(Pitfall 7). Text saying ``unchecked=3`` while JSON says ``unchecked=2`` would
be a worse defect than the silent pass this phase closes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_gnd_text as _run_cli

from gnd.model import ValidationIssue, load_model
from gnd.report import (
    BASE_PAYLOAD_SCHEMA_VERSION,
    DERIVATION_PAYLOAD_SCHEMA_VERSION,
    MAX_POPULATION_ISSUES,
    MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION,
    MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION,
    PAYLOAD_SCHEMA_VERSION,
    build_check_payload,
    load_report_schema,
)
from gnd.transition import model_digest

SKELETON = Path(__file__).parent / "fixtures" / "skeleton"
CHECKER = Path(__file__).parent / "fixtures" / "checker"
ADVERSARIAL = Path(__file__).parent / "fixtures" / "adversarial"

MODEL_GOOD = SKELETON / "model.orm.yaml"
MODEL_BAD = SKELETON / "model.bad.yaml"
POP_GOOD = SKELETON / "population.good.yaml"
POP_BAD = SKELETON / "population.bad.yaml"

SETFAM = CHECKER / "setfam.orm.yaml"
POP_EMPTY = CHECKER / "population.empty.yaml"
MISC = CHECKER / "misc.orm.yaml"
POP_MISC_PASS = CHECKER / "population.misc_pass.yaml"

HOSTILE_MODEL = ADVERSARIAL / "models" / "hostile_values.orm.yaml"
HOSTILE_POP = ADVERSARIAL / "populations" / "hostile_values.yaml"

_COUNTS_LINE = re.compile(r"pass=(\d+) fail=(\d+) warning=(\d+) unchecked=(\d+) vacuous=(\d+)")


def _payload(*args: str) -> tuple[dict, int]:
    result = _run_cli(*args, "--format", "json")
    try:
        return json.loads(result.stdout), result.returncode
    except json.JSONDecodeError as error:
        pytest.fail(
            f"--format json must emit a parseable payload on every band, but "
            f"{args} produced none ({error}).\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    return Draft202012Validator(load_report_schema())


# --- the discriminated shape across every exit path (D-11) ---

BAND_CASES = [
    pytest.param(("check", str(MODEL_GOOD), str(POP_GOOD)), 0, "accepted", id="exit-0-accepted"),
    pytest.param(("check", str(MODEL_GOOD), str(POP_BAD)), 1, "violated", id="exit-1-violated"),
    pytest.param(("check", str(SETFAM), str(POP_EMPTY)), 2, "inadequate", id="exit-2-inadequate"),
    pytest.param(("validate", str(MODEL_BAD)), 3, "ill_formed", id="exit-3-ill-formed"),
    pytest.param(
        ("check", str(MISC), str(POP_MISC_PASS)),
        4,
        "indeterminate",
        id="exit-4-indeterminate",
    ),
]


@pytest.mark.parametrize(("argv", "exit_code", "outcome"), BAND_CASES)
def test_every_band_emits_a_payload_validating_against_the_schema(
    validator, argv, exit_code, outcome
):
    payload, returncode = _payload(*argv)

    assert returncode == exit_code, f"expected exit {exit_code}, got {returncode}"
    assert payload["exit_code"] == exit_code, (
        f"payload exit_code must agree with the process exit code: "
        f"{payload['exit_code']} != {returncode}"
    )
    assert payload["outcome"] == outcome, (
        f"outcome discriminator must be {outcome!r}, got {payload['outcome']!r}"
    )
    model = load_model(argv[1]) if argv[0] == "check" else None
    if model is None:
        assert payload["schema_version"] == PAYLOAD_SCHEMA_VERSION
        assert "model_digest" not in payload
    else:
        assert payload["schema_version"] == 7
        assert payload["model_digest"] == model_digest(model)
    assert payload["tool"] == "gnd"

    errors = sorted(validator.iter_errors(payload), key=lambda e: e.json_path)
    assert not errors, (
        "payload must validate against src/gnd/report.schema.json; violations: "
        + "; ".join(f"{e.json_path}: {e.message}" for e in errors)
    )


@pytest.mark.parametrize(("argv", "exit_code", "outcome"), BAND_CASES)
def test_acceptance_ready_is_true_only_at_exit_0(argv, exit_code, outcome):
    payload, _ = _payload(*argv)
    assert payload["acceptance_ready"] is (exit_code == 0), (
        f"acceptance_ready must be true if and only if exit_code == 0 (D-08); "
        f"exit {exit_code} reported {payload['acceptance_ready']!r}"
    )


def test_every_key_is_always_present():
    """Fixed shape, not a variant record: a consumer never branches before
    reading a key."""
    expected = {
        "schema_version",
        "tool",
        "command",
        "outcome",
        "exit_code",
        "acceptance_ready",
        "model",
        "population",
        "counts",
        "verdicts",
        "coverage",
        "extraction",
        "issues",
        "issues_total",
        "issues_truncated",
        "warnings",
        "error",
        # Phase 2 (v2.0): three-valued and always present, like `extraction`.
        # null here -- every case in this file is a SNAPSHOT check or a
        # validate, and null is what "not a transition run" looks like.
        "transition",
    }
    for argv, _, _ in [case.values for case in BAND_CASES]:
        payload, _ = _payload(*argv)
        case_expected = expected | ({"model_digest", "derivations", "assurance"} if argv[0] == "check" else set())
        assert set(payload) == case_expected, (
            f"{argv} payload key set drifted: missing "
            f"{case_expected - set(payload)}, unexpected {set(payload) - case_expected}"
        )


def test_extraction_block_is_present_on_every_exit_path():
    """PANEL-3 / R-03'': `extraction` is present on EVERY payload — bands
    0/1/2/3/4 for both commands AND the internal-error path at 70 — as an
    empty dict until `gnd verify` (plan 03) populates it. A fixed shape means
    Phase 4's consumer reads `payload["extraction"]` unconditionally."""
    for argv, _, _ in [case.values for case in BAND_CASES]:
        payload, _ = _payload(*argv)
        assert payload["extraction"] == {}, (
            f"{argv} must carry an EMPTY extraction block (populated only by "
            f"gnd verify); got {payload.get('extraction')!r}"
        )
    internal = build_check_payload(70, "m.orm.yaml", "p.yaml", error=RuntimeError("checker bug"))
    assert internal["extraction"] == {}, (
        "the internal-error payload at exit 70 must carry the extraction "
        f"block too; got {internal.get('extraction')!r}"
    )


def test_schema_enforces_command_specific_extraction_shape(validator):
    check_payload, _ = _payload("check", str(MODEL_GOOD), str(POP_GOOD))

    verify_missing = json.loads(json.dumps(check_payload))
    verify_missing["command"] = "verify"
    assert list(validator.iter_errors(verify_missing))

    populated_check = json.loads(json.dumps(check_payload))
    populated_check["extraction"] = {
        "state": "ran",
        "reason": None,
        "sidecar": "s.json",
        "population_sha256": "a" * 64,
        "model_sha256": "b" * 64,
        "projection_sha256": "c" * 64,
        "document": "doc.md",
        "document_sha256": "d" * 64,
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "test-model",
    }
    assert list(validator.iter_errors(populated_check))

    verify_bad_digest = json.loads(json.dumps(populated_check))
    verify_bad_digest["command"] = "verify"
    verify_bad_digest["extraction"]["model_sha256"] = "NOT-A-DIGEST"
    assert list(validator.iter_errors(verify_bad_digest))


# --- one report, two renderings (Pitfall 7) ---


@pytest.mark.parametrize(
    ("model", "population"),
    [
        pytest.param(MODEL_GOOD, POP_GOOD, id="skeleton-good"),
        pytest.param(MODEL_GOOD, POP_BAD, id="skeleton-bad"),
        pytest.param(SETFAM, POP_EMPTY, id="setfam-empty"),
        pytest.param(MISC, POP_MISC_PASS, id="misc-pass"),
    ],
)
def test_json_counts_match_the_text_renderer(model, population):
    text = _run_cli("check", str(model), str(population)).stdout
    match = _COUNTS_LINE.search(text)
    assert match, f"text renderer must print a counts line; got:\n{text}"
    from_text = {
        "pass": int(match.group(1)),
        "fail": int(match.group(2)),
        "warning": int(match.group(3)),
        "unchecked": int(match.group(4)),
        "vacuous": int(match.group(5)),
    }

    payload, _ = _payload("check", str(model), str(population))
    assert payload["counts"] == from_text, (
        "the JSON payload must be computed FROM the same CheckReport the text "
        f"renderer prints, never beside it: JSON {payload['counts']} vs text "
        f"{from_text}"
    )


def test_unchecked_verdicts_carry_a_reason_code_and_others_do_not():
    payload, _ = _payload("check", str(MISC), str(POP_MISC_PASS))
    unchecked = [v for v in payload["verdicts"] if v["verdict"] == "unchecked"]
    assert unchecked, "misc.orm.yaml must produce unchecked verdicts"
    for verdict in unchecked:
        assert verdict["reason_code"], (
            f"every unchecked verdict must name why (D-12); "
            f"{verdict['constraint_ref']} carries {verdict['reason_code']!r}"
        )
    for verdict in payload["verdicts"]:
        if verdict["verdict"] != "unchecked":
            assert verdict["reason_code"] is None, (
                f"reason_code must be null for a {verdict['verdict']!r} verdict, "
                f"got {verdict['reason_code']!r}"
            )


# --- validate (D-10: --format on BOTH subcommands) ---


def test_validate_payload_has_no_population(validator):
    payload, returncode = _payload("validate", str(MODEL_GOOD))
    assert returncode == 0
    assert payload["command"] == "validate"
    assert payload["population"] is None, "validate never has a population"
    assert payload["verdicts"] == []
    assert payload["counts"] == {
        "pass": 0,
        "fail": 0,
        "warning": 0,
        "unchecked": 0,
        "vacuous": 0,
    }
    assert not list(validator.iter_errors(payload))


# --- exit 3 carries structured issues, not a flattened string (D-04) ---


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_ill_formed_population_exit_3_carries_structured_issues(tmp_path, validator):
    """Before Phase 01.1 this arm printed str(error) — a flattened summary. A
    retry loop needs actionable records precisely here."""
    bad_population = _write(tmp_path, "no_header.yaml", "facts: {}\n")
    payload, returncode = _payload("check", str(MODEL_GOOD), str(bad_population))

    assert returncode == 3, f"a layer-1 schema failure is band 3, got {returncode}"
    assert payload["outcome"] == "ill_formed"
    assert payload["issues"], (
        "exit 3 must carry structured issues[], not a flattened summary string"
    )
    for issue in payload["issues"]:
        assert issue["path"], f"every issue needs a path: {issue}"
        assert issue["message"], f"every issue needs a message: {issue}"
        assert issue["rule_id"], f"every issue needs a rule_id: {issue}"
    assert payload["issues_total"] == len(payload["issues"])
    assert payload["issues_truncated"] is False
    assert not list(validator.iter_errors(payload))


def test_layer2_population_issues_reach_the_payload(validator):
    """CORE-04: a model-relative structural failure is exit 3 with the same
    structured issues[] a layer-1 failure produces — one error vocabulary end
    to end, from popvalidate through ValidationIssue to the payload."""
    payload, returncode = _payload(
        "check",
        str(ADVERSARIAL / "models" / "omission.orm.yaml"),
        str(ADVERSARIAL / "populations" / "omission.missing_role.yaml"),
    )
    assert returncode == 3, (
        f"an omitted role is ill-formed SHAPE (3), never a mandatory "
        f"violation (1): got {returncode}"
    )
    assert payload["outcome"] == "ill_formed"
    assert payload["acceptance_ready"] is False
    rule_ids = [issue["rule_id"] for issue in payload["issues"]]
    assert rule_ids == ["population:missing-role"] * 2, rule_ids
    assert all(issue["path"].startswith("$.facts.") for issue in payload["issues"])
    assert not list(validator.iter_errors(payload))


def test_population_warnings_are_forwarded_to_the_payload(monkeypatch, validator):
    """Warning-severity layer-2 issues never abort the load, so the CLI's
    forward is the ONLY path by which they reach a consumer. Empty today (every
    CORE-04 rule is error-severity); asserted now so the first warning rule
    cannot land into a silent drop."""
    import gnd.cli as cli_module
    from gnd.population import load_population

    warning = ValidationIssue(
        path="$.population.model_id",
        message="synthetic warning",
        rule_id="population:test-only",
        severity="warning",
    )

    def _loader(path, *, model=None):
        population = load_population(path, model=model)
        # `model_copy(update=...)`, not attribute assignment: Population is
        # frozen (CR-01). `warnings` is deliberately EXCLUDED from the content
        # digest — it is layer 2's own output, written onto the population after
        # validation ran and read by no verdict — so this copy keeps a valid
        # marker while a copy that replaced `facts` would not.
        return population.model_copy(update={"warnings": [warning]})

    from gnd import checking_service

    monkeypatch.setattr(checking_service, "load_population", _loader)

    payload_lines: list[str] = []
    monkeypatch.setattr(
        cli_module.report_module, "emit", lambda p: payload_lines.append(json.dumps(p))
    )

    exit_code = cli_module._cmd_check(str(MODEL_GOOD), str(POP_GOOD), "json")
    assert exit_code == 0
    payload = json.loads(payload_lines[0])
    assert payload["warnings"] == [warning.model_dump()], (
        "population warnings must reach the payload, not be dropped"
    )
    assert not list(validator.iter_errors(payload))


def test_ill_formed_model_exit_3_carries_structured_issues():
    payload, returncode = _payload("check", str(MODEL_BAD), str(POP_GOOD))
    assert returncode == 3
    assert payload["issues"], "a model validation failure must carry issues[]"
    assert any("$.fact_types" in issue["path"] for issue in payload["issues"])


# --- bounded payload (T-01.1-02) ---


def test_issues_are_capped_with_the_elision_reported():
    """A systematically malformed 10 MB population must not produce a payload
    larger than its own input."""
    overflow = [
        ValidationIssue(path=f"$.facts.x[{i}]", message="m", rule_id="jsonschema:type")
        for i in range(MAX_POPULATION_ISSUES + 37)
    ]
    payload = build_check_payload(3, "m.orm.yaml", "p.yaml", issues=overflow)

    assert len(payload["issues"]) == MAX_POPULATION_ISSUES
    assert payload["issues_total"] == MAX_POPULATION_ISSUES + 37, (
        "the pre-truncation count must be reported, so the elision is never silent"
    )
    assert payload["issues_truncated"] is True


def test_internal_error_payload_is_tagged_and_valid(validator):
    payload = build_check_payload(70, "m.orm.yaml", "p.yaml", error=RuntimeError("checker bug"))
    assert payload["outcome"] == "internal_error"
    assert payload["acceptance_ready"] is False
    assert payload["error"] == {"type": "RuntimeError", "message": "checker bug"}
    assert not list(validator.iter_errors(payload))


# --- untrusted content echo (T-01.1-04) ---


def test_hostile_fact_values_round_trip_without_breaking_the_payload(validator):
    """Quote, backslash, newline and control characters in agent-supplied fact
    values reach the payload via json.dumps, which escapes them correctly."""
    payload, returncode = _payload("check", str(HOSTILE_MODEL), str(HOSTILE_POP))

    assert returncode == 1, "the hostile population violates an alethic uniqueness"
    assert not list(validator.iter_errors(payload))

    bodies = [
        fact["body"]
        for verdict in payload["verdicts"]
        for fact in verdict["offending_facts"]
        if isinstance(fact, dict) and "body" in fact
    ]
    assert bodies, f"the offending facts must reach the payload: {payload['verdicts']}"
    joined = "".join(bodies)
    for char in ('"', "\\", "\n", "\x01", "\x00"):
        assert char in joined, (
            f"{char!r} must survive the JSON round trip intact, so the payload "
            f"echoes untrusted content faithfully rather than mangling it; got "
            f"{joined!r}"
        )


# --- WR-05: a warning must survive the presence of an error ---

MODEL_ID_A = ADVERSARIAL / "models" / "model_id_a.orm.yaml"
POP_ABSENT_AND_MALFORMED = ADVERSARIAL / "populations" / "model_id_absent_and_malformed.yaml"


def test_exit_3_carries_the_warnings_from_the_same_layer_2_pass(validator):
    """`load_population` computed `warnings` only AFTER the error check raised,
    and `PopulationValidationError` carried only errors — so the warning was
    assembled for a CLEAN load and discarded for a dirty one.

    It matters most on the dirty one: "unknown fact type + missing role" plus
    "no model_id, so the header cross-check was skipped" together read as "you
    may have validated against the wrong model", which is the repair. The errors
    alone read as "typo somewhere"."""
    payload, returncode = _payload("check", str(MODEL_ID_A), str(POP_ABSENT_AND_MALFORMED))
    assert returncode == 3

    assert {i["rule_id"] for i in payload["issues"]} == {
        "population:unknown-fact-type",
        "population:missing-role",
    }
    assert [w["rule_id"] for w in payload["warnings"]] == ["population:model-id-absent"], (
        f"the warning from the same pass must survive the errors, got {payload['warnings']!r}"
    )
    assert not list(validator.iter_errors(payload))


def test_exit_3_text_output_prints_those_warnings_too():
    result = _run_cli("check", str(MODEL_ID_A), str(POP_ABSENT_AND_MALFORMED))
    assert result.returncode == 3
    assert "population:model-id-absent" in result.stdout, result.stdout
    assert "population:missing-role" in result.stdout, result.stdout


# --- WR-03: model warnings must reach the check payload too ---


def test_check_forwards_model_warnings_alongside_the_band_they_explain(validator):
    """`_cmd_check` forwarded only `population.warnings`, so `Model.warnings` —
    carrying this phase's own `semantic:textual-alethic` (D-20) — reached
    `gnd validate` and nothing else. The canonical band-4 fixture returned
    "indeterminate" with an EMPTY warnings array: the one authoring-time record
    explaining why that model can NEVER reach exit 0, for any population,
    discarded on the command that surfaces the consequence.

    `report.schema.json` documents `warnings` with `semantic:modality-policy` —
    a MODEL rule — as its example, so the schema and the emitter disagreed."""
    payload, returncode = _payload("check", str(MISC), str(POP_MISC_PASS))
    assert returncode == 4, "misc.orm.yaml is the canonical band-4 fixture"

    rule_ids = [warning["rule_id"] for warning in payload["warnings"]]
    assert "semantic:textual-alethic" in rule_ids, (
        f"the D-20 warning explaining this exit 4 must travel with it, got {rule_ids!r}"
    )
    validate_payload, _ = _payload("validate", str(MISC))
    assert rule_ids == [w["rule_id"] for w in validate_payload["warnings"]], (
        "validate and check must agree about the model's warnings"
    )
    assert not list(validator.iter_errors(payload))


def test_check_text_output_prints_model_warnings():
    """One assembly, two renderings — the text path must not drop what the JSON
    path forwards."""
    result = _run_cli("check", str(MISC), str(POP_MISC_PASS))
    assert result.returncode == 4
    assert "semantic:textual-alethic" in result.stdout, result.stdout


# --- WR-01: the issue cap must bound every consumer, not only the payload ---


def _systematically_malformed(tmp_path, fact_count: int):
    """A population whose every fact omits a declared role — one issue each."""
    facts = "\n".join(f'    - {{ title: "T{i}" }}' for i in range(fact_count))
    path = tmp_path / "malformed.yaml"
    path.write_text(
        "population:\n  model: model.orm.yaml\n  source: agent-output\n"
        f"facts:\n  movie_has_title:\n{facts}\n",
        encoding="utf-8",
    )
    return path


def test_text_output_is_capped_like_the_payload(tmp_path, capsys):
    """The cap used to apply only where issues were SERIALIZED. Measured on a
    3.1 MB population with 120 000 role-omitting facts: the JSON payload was a
    correct 63 KB while the text renderer wrote 32 MB — a 10x amplification of
    the input, i.e. ~100 MB of stdout at the 10 MB file cap."""
    import gnd.cli as cli_module
    import gnd.report as report_module

    count = report_module.MAX_POPULATION_ISSUES + 25
    path = _systematically_malformed(tmp_path, count)

    exit_code = cli_module._cmd_check(str(MODEL_GOOD), str(path), "text")
    assert exit_code == 3

    lines = capsys.readouterr().out.splitlines()
    errors = [line for line in lines if line.startswith("ERROR at ")]
    assert len(errors) == report_module.MAX_POPULATION_ISSUES, (
        f"the text renderer must honour the same cap as the payload, got "
        f"{len(errors)} lines for {count} issues"
    )
    assert any("further issue(s) elided" in line for line in lines), (
        "the elision must be reported, never silent"
    )


def test_the_exception_summary_is_bounded_too(tmp_path):
    """`PopulationValidationError.__init__` joined ALL issue messages into one
    string — and neither `_cmd_check` arm ever reads `str(error)` (both use
    `error.issues`), so it was unbounded work whose product is discarded."""
    from gnd.population import (
        MAX_SUMMARY_ISSUES,
        PopulationValidationError,
        load_population,
    )

    path = _systematically_malformed(tmp_path, MAX_SUMMARY_ISSUES + 50)
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path, model=load_model(MODEL_GOOD))

    assert len(excinfo.value.issues) == MAX_SUMMARY_ISSUES + 50, (
        "the STRUCTURED list stays complete — only the summary string is capped"
    )
    assert str(excinfo.value).count("population:missing-role") == MAX_SUMMARY_ISSUES
    assert "(+50 more)" in str(excinfo.value)


# --- CR-04: no non-RFC-8259 literal may ever leave the emitter ---


def test_emit_refuses_a_non_finite_value_rather_than_writing_a_bare_nan():
    """`json.dumps`' default `allow_nan=True` writes the bare token `NaN`, which
    `JSON.parse`, Go `encoding/json`, serde_json, jq and `json.loads` with a
    strict `parse_constant` all reject. The D-11/D-12 machine interface would be
    unparseable exactly when the population is hostile — the case Phase 4's
    controller most needs it."""
    import gnd.report as report_module

    payload = build_check_payload(1, "m.orm.yaml", "p.yaml")
    payload["verdicts"] = [{"offending_facts": [float("nan")]}]
    with pytest.raises(report_module.NonJsonValueError):
        report_module.emit(payload)

    payload["verdicts"] = [{"offending_facts": [float("inf")]}]
    with pytest.raises(report_module.NonJsonValueError):
        report_module.emit(payload)


def test_a_non_emittable_payload_degrades_to_a_valid_internal_error(monkeypatch, capsys, validator):
    """D-11 promises a payload on EVERY exit path, so the guard must not turn
    into "no output at all". The fallback record carries no verdicts and no
    issues, so it cannot itself trip the guard."""
    import gnd.cli as cli_module
    from gnd.checker import CheckReport, ConstraintVerdict

    poisoned = CheckReport(
        verdicts=[
            ConstraintVerdict(
                scope_id="snapshot:value:enum:violated:alethic",
                constraint_ref="constraints[0]",
                constraint_type="value",
                modality="alethic",
                source="explicit",
                status="confirmed",
                verdict="fail",
                message="poisoned",
                offending_facts=[float("nan")],
            )
        ],
        coverage={},
    )
    monkeypatch.setattr(
        cli_module.api_module.checker_module,
        "check",
        lambda model, population: poisoned,
    )

    exit_code = cli_module._cmd_check(str(MODEL_GOOD), str(POP_GOOD), "json")
    assert exit_code == 70, "an unrepresentable value is a tool problem, not a verdict"

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["outcome"] == "internal_error"
    assert payload["acceptance_ready"] is False
    assert payload["error"]["type"] == "NonJsonValueError"
    assert not list(validator.iter_errors(payload))


# --- exit 64 emits no payload ---


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["check", str(MODEL_GOOD), str(POP_GOOD), "--format", "xml"], id="check-xml"),
        pytest.param(["validate", str(MODEL_GOOD), "--format", "yaml"], id="validate-yaml"),
    ],
)
def test_invalid_format_exits_64_with_no_payload(argv):
    result = _run_cli(*argv)
    assert result.returncode == 64, (
        f"an invalid --format choice is an argparse usage error (WR-03), got "
        f"{result.returncode}: {result.stdout + result.stderr}"
    )
    assert result.stdout.strip() == "", (
        f"exit 64 deliberately emits no payload — the format flag is not known "
        f"until parse_args() returns; stdout was {result.stdout!r}"
    )


def test_default_format_is_text():
    result = _run_cli("check", str(MODEL_GOOD), str(POP_GOOD))
    assert result.returncode == 0
    assert "BLOCKING (alethic)" in result.stdout, (
        f"omitting --format must keep the human rendering; got:\n{result.stdout}"
    )
    with pytest.raises(json.JSONDecodeError):
        json.loads(result.stdout)


def test_v5_v6_keysets_and_schema(validator):
    """The derivation discriminator, on the model-bound pair it now selects.

    v5.1 Phase 3 pairs the wire: 5 is 3's model-bound successor and 6 is 4's,
    so the same closed choice -- does this payload carry derivation
    obligations -- separates 5 from 6 exactly as it separated 3 from 4. Both
    arms additionally require the model digest, and versions 3 and 4 keep
    forbidding it. The four closed arms are exercised in both directions here.
    """
    root = Path(__file__).parent / "fixtures" / "derivation-evaluation" / "cases"
    structured = root / "wire-v4-structured-check"
    base_payload, _ = _payload("check", str(MODEL_GOOD), str(POP_GOOD))
    derived_payload, returncode = _payload(
        "check",
        str(structured / "model.orm.yaml"),
        str(structured / "population.yaml"),
    )
    # Current CLI emits v7; the compatibility projection must still satisfy
    # every frozen v3-v6 acceptance and rejection below.
    from gnd.report import legacy_report_projection
    for payload in (base_payload, derived_payload):
        assert payload["schema_version"] == 7
        assert not list(validator.iter_errors(payload))
    base_payload = legacy_report_projection(base_payload, 5)
    derived_payload = legacy_report_projection(derived_payload, 6)
    assert base_payload["schema_version"] == MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION
    assert "derivations" not in base_payload
    assert derived_payload["schema_version"] == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
    assert list(derived_payload).index("derivations") == list(derived_payload).index("verdicts") + 1
    assert returncode == derived_payload["exit_code"]
    assert sum(derived_payload["counts"].values()) == (
        len(derived_payload["verdicts"]) + len(derived_payload["derivations"])
    )
    for payload in (base_payload, derived_payload):
        keys = list(payload)
        assert keys.index("model_digest") == keys.index("model") + 1
        assert not list(validator.iter_errors(payload))
    v5_with_derivations = dict(base_payload, derivations=[])
    assert list(validator.iter_errors(v5_with_derivations))
    v6_without_derivations = dict(derived_payload)
    del v6_without_derivations["derivations"]
    assert list(validator.iter_errors(v6_without_derivations))
    v5_without_digest = {k: v for k, v in base_payload.items() if k != "model_digest"}
    assert list(validator.iter_errors(v5_without_digest))
    v6_without_digest = {k: v for k, v in derived_payload.items() if k != "model_digest"}
    assert list(validator.iter_errors(v6_without_digest))
    v3_with_digest = dict(v5_without_digest, schema_version=BASE_PAYLOAD_SCHEMA_VERSION)
    v3_with_digest["model_digest"] = base_payload["model_digest"]
    assert list(validator.iter_errors(v3_with_digest))
    v4_with_digest = dict(
        derived_payload, schema_version=DERIVATION_PAYLOAD_SCHEMA_VERSION
    )
    assert list(validator.iter_errors(v4_with_digest))
    assert not list(validator.iter_errors(dict(v5_without_digest,
                                               schema_version=BASE_PAYLOAD_SCHEMA_VERSION)))
    assert not list(validator.iter_errors(
        {k: v for k, v in v4_with_digest.items() if k != "model_digest"}
    ))
    assert list(validator.iter_errors(dict(base_payload, model_digest="sha256:nope")))


def test_v4_derivation_invariants_are_schema_enforced(validator):
    root = Path(__file__).parent / "fixtures" / "derivation-evaluation" / "cases"
    derived, _ = _payload(
        "check",
        str(root / "obligation-derived-both-differences" / "model.orm.yaml"),
        str(root / "obligation-derived-both-differences" / "population.yaml"),
    )
    assert not list(validator.iter_errors(derived))
    row = derived["derivations"][0]
    assert "fact_type" not in row
    assert row["derivation_ref"] == "derivation:result"
    assert [finding["kind"] for finding in row["findings"]] == [
        "derived-extension-incomplete",
        "derived-extension-unsound",
    ]

    bad_order = json.loads(json.dumps(derived))
    bad_order["derivations"][0]["findings"].reverse()
    assert list(validator.iter_errors(bad_order))
    unchecked_with_findings = json.loads(json.dumps(derived))
    unchecked_with_findings["derivations"][0]["verdict"] = "unchecked"
    unchecked_with_findings["derivations"][0]["reason_code"] = "derivation-not-covered"
    assert list(validator.iter_errors(unchecked_with_findings))
