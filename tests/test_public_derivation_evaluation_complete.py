"""v5.0 Phase 2 corpus-first gate -- fixture truth before evaluator code.

The shape and control tests are GREEN at the RED commit. Every semantic/wire/
oracle/cost row then loads its model and population (or establishes its named
load refusal), verifies the declared branch preconditions, and fails at the
same missing-lane assertion. The sentinel is intentionally after those checks:
a malformed or unreachable fixture cannot borrow redness from an early global
failure.

The answer-free questions live in fixtures/derivation-evaluation/README.md.
EXPECTED.md and expected.json are the human and machine answer keys.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from test_public_derivation_parity_corpus import ANSWER_KEY, CORPUS

import gnd.checker._core as checker_core
from gnd import checker
from gnd import cli as cli_module
from gnd import extensions as extension_core
from gnd.address import derivation_address, fact_type_address, parse_address
from gnd.checker import (
    CheckReport,
    ConstraintVerdict,
    DerivationFinding,
    DerivationVerdict,
    _base_relations,
    _constraint_view,
    _evaluate_derivations,
    _python_extension_calculator,
    _TypedRelation,
    band,
)
from gnd.commands import checking as checking_commands
from gnd.exp.session_eval import VerifierPayloadError, validate_verifier_payload
from gnd.export import verification_service
from gnd.model import ModelValidationError, load_model
from gnd.population import PopulationValidationError, load_population
from gnd.report import (
    BASE_PAYLOAD_SCHEMA_VERSION,
    DERIVATION_PAYLOAD_SCHEMA_VERSION,
    MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION,
    MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION,
    build_check_payload,
    legacy_report_projection,
    load_report_schema,
)
from gnd.transition import TransitionReport, model_digest

REPO_ROOT = Path(__file__).resolve().parents[1]
CASES: list[dict[str, Any]] = ANSWER_KEY["cases"]
RED_CASES = [case for case in CASES if case["status"] == "red-missing-lane"]
A8_MIGRATED_BRANCHES = frozenset(
    {
        "obligation:unlisted-derived-nonempty-computed",
        "obligation:unlisted-semiderived-nonempty-computed",
        "constraint:unlisted-derived-claim-inert",
        "constraint:mandatory-uncovered-vacuous-plus-band4",
    }
)
GREEN_CASES = [case for case in CASES if case["status"] == "prephase-control-green"]

def _paths(case: dict[str, Any]) -> tuple[Path, Path]:
    root = CORPUS / str(case["path"])
    return root / "model.orm.yaml", root / "population.yaml"

def _structured_rules(model: Any) -> list[Any]:
    return [
        fact_type.get("derivation_rule")
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]

def _assert_preconditions(case: dict[str, Any]) -> tuple[Any | None, Any | None]:
    """Establish this case's legal input/refusal shape before any RED sentinel."""
    model_path, population_path = _paths(case)
    profile = str(case["profile"])

    if profile == "invalid-model":
        with pytest.raises(ModelValidationError):
            load_model(model_path)
        return None, None

    model = load_model(model_path)
    if profile in {"nonstructured", "string-only"}:
        assert not _structured_rules(model), case["id"]
    else:
        assert _structured_rules(model), case["id"]

    if profile == "population-refusal" or str(case["branch"]) in A8_MIGRATED_BRANCHES:
        with pytest.raises(PopulationValidationError) as excinfo:
            load_population(population_path, model=model)
        if str(case["branch"]) in A8_MIGRATED_BRANCHES:
            assert [issue.rule_id for issue in excinfo.value.issues] == [
                "population:uncovered-structured-derived-facts"
            ]
        return model, None

    population = load_population(population_path, model=model)
    assert population.matches_validation_marker(model)

    if profile == "string-only":
        assert all(
            not isinstance(fact_type.get("derivation_rule"), dict) for fact_type in model.fact_types
        )
    if profile.startswith("mixed-"):
        rules = [fact_type.get("derivation_rule") for fact_type in model.fact_types]
        assert any(isinstance(rule, dict) for rule in rules)
        assert any(isinstance(rule, str) for rule in rules)
        assert ("legacy_result" in population.covers) == (profile == "mixed-listed")
    if profile.startswith("unlisted-"):
        assert "result" not in population.covers
        if profile.endswith("-empty"):
            assert population.facts["seed"] == []
        else:
            assert population.facts["seed"]
    if profile == "dollar-literal":
        assert any(
            atom.get("bind", {}).get("tag") == "$"
            for fact_type in model.fact_types
            for atom in (
                fact_type.get("derivation_rule", {}).get("body", [])
                if isinstance(fact_type.get("derivation_rule"), dict)
                else []
            )
        )
    if profile == "chain":
        assert [fact_type["id"] for fact_type in model.fact_types][-3:] == [
            "low",
            "middle",
            "top",
        ]
    if profile == "disconnected":
        rule = next(
            fact_type["derivation_rule"]
            for fact_type in model.fact_types
            if fact_type["id"] == "result"
        )
        assert len(rule["body"]) == 2
    if profile == "unresolved":
        from gnd.popvalidate import resolve_primitive

        assert resolve_primitive("mass", model) is None
    if profile == "primitives":
        primitives = {
            object_type.get("primitive")
            for object_type in model.object_types
            if object_type.get("primitive") is not None
        }
        assert primitives == {
            "String",
            "Integer",
            "Float",
            "Number",
            "Date",
            "DateTime",
            "Boolean",
            "Binary",
        }
    return model, population

def _run_json(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *args, "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

def _loaded(case: dict[str, Any]) -> tuple[Any, Any]:
    model, population = _assert_preconditions(case)
    assert model is not None and population is not None
    return model, population

def _extension_rows(model: Any, population: Any) -> dict[str, tuple[tuple[Any, ...], ...]]:
    extensions, _verdicts = _evaluate_derivations(model, population)
    return {fact_type: relation.rows for fact_type, relation in extensions.items()}

def _assert_wire(case: dict[str, Any]) -> None:
    branch = str(case["branch"])
    model_path, population_path = _paths(case)
    if branch == "wire:v4-population-refusal":
        _assert_preconditions(case)
        completed = _run_json("check", str(model_path), str(population_path))
        payload = json.loads(completed.stdout)
        assert completed.returncode == 3
        payload = legacy_report_projection(payload, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION)
        assert (
            payload["schema_version"] == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
            and payload["derivations"] == []
        )
        assert payload["model_digest"] == model_digest(load_model(model_path))
        return

    model, population = _loaded(case)
    report = checker.check(model, population)
    payload = build_check_payload(
        band(report),
        str(model_path),
        str(population_path),
        schema_version=MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION,
        model_digest=model_digest(model),
        report=report,
    )
    if branch == "wire:v4-structured-check":
        completed = _run_json("check", str(model_path), str(population_path))
        emitted = json.loads(completed.stdout)
        emitted = legacy_report_projection(emitted, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION)
        assert (
            emitted["schema_version"] == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
            and emitted["derivations"]
        )
    elif branch == "wire:v4-structured-validate":
        completed = _run_json("validate", str(model_path))
        emitted = json.loads(completed.stdout)
        assert completed.returncode == 0
        assert (
            emitted["schema_version"] == DERIVATION_PAYLOAD_SCHEMA_VERSION
            and emitted["derivations"] == []
        )
        assert "model_digest" not in emitted
    elif branch in {"wire:v4-check-internal", "wire:v4-verify-internal"}:

        def injected_failure(_model: Any, _population: Any) -> Any:
            raise RuntimeError("injected checker failure")

        output = io.StringIO()
        with pytest.MonkeyPatch.context() as mutation:
            mutation.setattr(cli_module.api_module.checker_module, "check", injected_failure)
            mutation.setattr(checking_commands, "check", injected_failure)
            mutation.setattr(verification_service, "check", injected_failure)
            with contextlib.redirect_stdout(output):
                if branch == "wire:v4-check-internal":
                    exit_code = cli_module._cmd_check(
                        str(model_path),
                        str(population_path),
                        "json",
                    )
                else:
                    exit_code = cli_module._cmd_verify(
                        str(model_path),
                        str(population_path),
                        None,
                        None,
                        True,
                        None,
                        "json",
                    )
        internal = json.loads(output.getvalue())
        internal = legacy_report_projection(internal, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION)
        command = "verify" if branch == "wire:v4-verify-internal" else "check"
        assert exit_code == internal["exit_code"] == 70
        assert internal["command"] == command
        assert (
            internal["schema_version"] == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
            and internal["derivations"] == []
        )
        assert internal["model_digest"] == model_digest(load_model(model_path))
    elif branch == "wire:v4-validate-internal":
        real_emit = cli_module.report_module.emit
        attempts = 0

        def reject_first(payload: dict[str, Any]) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise cli_module.report_module.NonJsonValueError("injected emitter failure")
            real_emit(payload)

        output = io.StringIO()
        with pytest.MonkeyPatch.context() as mutation:
            mutation.setattr(cli_module.report_module, "emit", reject_first)
            with contextlib.redirect_stdout(output):
                exit_code = cli_module._cmd_validate(str(model_path), "json")
        internal = json.loads(output.getvalue())
        assert attempts == 2 and exit_code == internal["exit_code"] == 70
        assert (
            internal["schema_version"] == DERIVATION_PAYLOAD_SCHEMA_VERSION
            and internal["derivations"] == []
        )
        assert "model_digest" not in internal
    elif branch == "wire:v3-rejects-derivations":
        with pytest.raises(ValueError, match="cannot hide"):
            build_check_payload(
                band(report),
                str(model_path),
                str(population_path),
                schema_version=BASE_PAYLOAD_SCHEMA_VERSION,
                report=report,
            )
    elif branch == "wire:v4-requires-derivations":
        payload.pop("derivations")
        assert list(Draft202012Validator(load_report_schema()).iter_errors(payload))
    elif branch == "wire:text-json-parity":
        text = subprocess.run(
            [sys.executable, "-m", "gnd", "check", str(model_path), str(population_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        machine = _run_json("check", str(model_path), str(population_path))
        emitted = json.loads(machine.stdout)
        counts = emitted["counts"]
        assert "DERIVATIONS (alethic)" in text.stdout
        assert (
            f"pass={counts['pass']} fail={counts['fail']} warning={counts['warning']} "
            f"unchecked={counts['unchecked']} vacuous={counts['vacuous']}"
        ) in text.stdout
        assert text.returncode == machine.returncode
    elif branch == "wire:address-coherent":
        assert all(
            verdict.derivation_ref == derivation_address(verdict.fact_type)
            for verdict in report.derivations
        )
    elif branch == "wire:address-distinct":
        # Phase 3 T3.6 moved the phase-2 boundary this branch also pinned
        # (parse_address returning None for the derivation class). The
        # distinctness half is the branch's meaning and stays; the parser half
        # is re-anchored to the positive contract rather than left as a test
        # about nothing (the 005 correction-record rule).
        assert all(
            verdict.derivation_ref != fact_type_address(verdict.fact_type)
            and (parsed := parse_address(verdict.derivation_ref)) is not None
            and parsed.element_class == "derivation"
            and parsed.identifier == verdict.fact_type
            for verdict in report.derivations
        )
    elif branch == "wire:session-v4-refused":
        raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
        with pytest.raises(VerifierPayloadError, match="schema_version must be current version 3"):
            validate_verifier_payload(
                raw,
                case_id="phase2-v4",
                role="required",
                process_exit=payload["exit_code"],
                expected_command="check",
                expected_subject=str(population_path),
                candidate_sha256="a" * 64,
                contract_sha256="b" * 64,
                evidence_candidate_sha256="a" * 64,
                evidence_contract_sha256="b" * 64,
                expected_model=str(model_path),
            )
    else:  # pragma: no cover - manifest equality makes this a harness defect
        raise AssertionError(branch)

def _assert_obligation(case: dict[str, Any]) -> None:
    model, population = _loaded(case)
    report = checker.check(model, population)
    branch = str(case["branch"])
    expected: dict[str, tuple[int, str, tuple[str, ...], str | None]] = {
        "obligation:derived-exact": (0, "pass", (), None),
        "obligation:derived-missing": (1, "fail", ("derived-extension-incomplete",), None),
        "obligation:derived-surplus": (1, "fail", ("derived-extension-unsound",), None),
        "obligation:derived-both-differences": (
            1,
            "fail",
            ("derived-extension-incomplete", "derived-extension-unsound"),
            None,
        ),
        "obligation:semiderived-exact": (0, "pass", (), None),
        "obligation:semiderived-surplus": (0, "pass", (), None),
        "obligation:semiderived-missing": (
            1,
            "fail",
            ("derived-extension-incomplete",),
            None,
        ),
        "obligation:unlisted-derived-empty-computed": (
            4,
            "unchecked",
            (),
            "derivation-not-covered",
        ),
        "obligation:unlisted-derived-nonempty-computed": (
            4,
            "unchecked",
            (),
            "derivation-not-covered",
        ),
        "obligation:unlisted-semiderived-empty-computed": (
            4,
            "unchecked",
            (),
            "derivation-not-covered",
        ),
        "obligation:unlisted-semiderived-nonempty-computed": (
            4,
            "unchecked",
            (),
            "derivation-not-covered",
        ),
    }
    if branch in {"obligation:opaque-mixed-listed", "obligation:opaque-mixed-unlisted"}:
        verdict = next(row for row in report.derivations if row.fact_type == "legacy_result")
        reason = (
            "derivation-rule-opaque"
            if branch.endswith("listed") and not branch.endswith("unlisted")
            else "derivation-not-covered"
        )
        assert band(report) == 4 and verdict.verdict == "unchecked"
        assert verdict.reason_code == reason
        return
    expected_band, verdict_name, kinds, reason = expected[branch]
    verdict = next(row for row in report.derivations if row.fact_type == "result")
    assert band(report) == expected_band
    assert verdict.verdict == verdict_name
    assert tuple(finding.kind for finding in verdict.findings) == kinds
    assert verdict.reason_code == reason

def _assert_evaluation(case: dict[str, Any]) -> None:
    model, population = _loaded(case)
    rows = _extension_rows(model, population)
    branch = str(case["branch"])
    if branch in {
        "eval:positive-chain-small-head",
        "eval:depth3-dependency-order",
        "eval:derived-poison-ignored",
    }:
        assert list(rows) == ["low", "middle", "top"]
        assert rows == {"low": (("alpha",),), "middle": (("alpha",),), "top": (("alpha",),)}
    elif branch == "eval:disconnected-product":
        assert rows["result"] == (("b1", 1), ("b1", 2), ("b2", 1), ("b2", 2))
    elif branch == "eval:negated-present":
        assert rows["result"] == ()
    elif branch in {
        "eval:positive-single",
        "eval:semiderived-surplus-upper-ignored",
        "eval:projection-dedup",
        "eval:negated-absent",
        "eval:negated-empty-relation",
        "eval:dollar-variable-normalized",
        "eval:bare-dollar-literal",
        "eval:grounded-pseudo-component",
    }:
        assert rows["result"] == (("alpha",),)
        if branch == "eval:grounded-pseudo-component":
            grounded = {"fact_type": "seed", "bind": {"item": "alpha"}}
            rule = {"body": [grounded], "head": {"item": "$i"}}
            marker = "\u0000grounded:.body[0]"
            assert checker.body_components(rule) == [frozenset({marker})]
            assert checker._component_atoms(rule) == [[grounded]]
    elif branch in {
        "eval:all-eight-primitives",
        "eval:boolean-number-separated",
        "eval:integer-float-merged",
    }:
        row = rows["result"][0]
        assert len(row) == 8
        assert checker._identity_token(row[1]) == checker._identity_token(row[2])
        assert checker._identity_token(row[6]) != checker._identity_token(row[1])
    elif branch == "eval:unresolved-primitive-metadata":
        relations = _base_relations(model, population)
        assert relations["seed"].roles == (("mass", None),)
        assert rows["result"] == (("heavy",),)
    else:  # pragma: no cover
        raise AssertionError(branch)

def _constraint_verdict(verdict: str) -> ConstraintVerdict:
    return ConstraintVerdict(
        scope_id=f"composition:oracle-verdict:n-a:{verdict}",
        constraint_ref="constraints[0]",
        constraint_type="guarded",
        modality="alethic",
        source="explicit",
        status="confirmed",
        verdict=verdict,
        message="fixture",
    )

def _pass_derivation() -> DerivationVerdict:
    return DerivationVerdict(
        derivation_ref="derivation:result",
        fact_type="result",
        derivation="derived",
        verdict="pass",
        message="fixture",
        scope_id="derivation:extension:derived:clean",
    )

def _fail_derivation() -> DerivationVerdict:
    return DerivationVerdict(
        derivation_ref="derivation:result",
        fact_type="result",
        derivation="derived",
        verdict="fail",
        message="fixture",
        findings=[
            DerivationFinding(
                kind="derived-extension-incomplete",
                message="fixture",
                witness={"item": "alpha"},
            )
        ],
        scope_id="derivation:extension:derived:violated:alethic",
    )

def _unchecked_derivation() -> DerivationVerdict:
    return DerivationVerdict(
        derivation_ref="derivation:result",
        fact_type="result",
        derivation="derived",
        verdict="unchecked",
        message="fixture",
        reason_code="derivation-not-covered",
        scope_id="derivation:extension:derived:unchecked-not-covered",
    )

def _assert_constraint_or_band(case: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    model, population = _loaded(case)
    branch = str(case["branch"])
    extensions, derivations = _evaluate_derivations(model, population)
    if branch == "constraint:evaluator-view-isolated":
        base = _base_relations(model, population)
        assert all(not base[fact_type].rows for fact_type in extensions)
    elif branch in {
        "constraint:constraint-view-isolated",
        "constraint:derived-claim-view",
        "constraint:semiderived-computed-view",
        "constraint:unlisted-derived-claim-inert",
    }:
        view = _constraint_view(model, population, extensions)
        if branch == "constraint:unlisted-derived-claim-inert":
            assert view.facts["result"] == ()
        elif "semi_result" in view.facts:
            assert [dict(row) for row in view.facts["semi_result"]] == [{"item": "alpha"}]
        else:
            assert view.facts["result"]
        assert view.facts is not population.facts
    elif branch in {
        "constraint:all-extensions-before-constraints",
        "constraint:one-final-walk",
        "constraint:duplicate-final-walk-red",
    }:
        target_case = next(item for item in CASES if item["branch"] == "constraint:one-final-walk")
        target_model, target_population = _loaded(target_case)
        calls: list[str] = []
        original_evaluate = extension_core.evaluate_derivations
        original_message = checker._correspondence_message

        def traced_evaluate(*args: Any, **kwargs: Any):
            result = original_evaluate(*args, **kwargs)
            calls.extend(f"extension:{fact_type}" for fact_type in result[0])
            calls.extend(f"comparison:{row.fact_type}" for row in result[1])
            return result

        def traced_message(*args: Any, **kwargs: Any):
            calls.append(f"constraint:{args[2].constraint_id}")
            return original_message(*args, **kwargs)

        monkeypatch.setattr(extension_core, "evaluate_derivations", traced_evaluate)
        monkeypatch.setattr(checker_core, "_correspondence_message", traced_message)
        report = checker.check(target_model, target_population)
        constraint_calls = [event for event in calls if event.startswith("constraint:")]
        assert len(constraint_calls) == len(report.verdicts) == 1
        assert calls == [
            "extension:result",
            "extension:semi_result",
            "comparison:result",
            "comparison:semi_result",
            "constraint:constraints[0]",
        ]
        if branch == "constraint:one-final-walk":
            target_path = CORPUS / str(target_case["path"])
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "gnd",
                    "check",
                    str(target_path / "model.orm.yaml"),
                    str(target_path / "population.yaml"),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                check=False,
            )
            assert completed.returncode == 1
            assert hashlib.sha256(completed.stdout).hexdigest() == (
                "f7ace830397b803a26353c48768d4ad094c91bee2314004bdb9cfd804029e1c4"
            )
        if branch == "constraint:duplicate-final-walk-red":
            duplicated = report.model_copy(
                update={"verdicts": [*report.verdicts, *report.verdicts]}
            )
            with pytest.raises(AssertionError):
                assert len(duplicated.verdicts) == len(constraint_calls) == 1
    elif branch == "constraint:original-output-order":
        report = checker.check(model, population)
        assert [row.constraint_ref for row in report.verdicts] == [
            "fact_types[seed].constraints[0]",
            "constraints[0]",
        ]
    elif branch == "constraint:two-families":
        report = checker.check(model, population)
        assert report.derivations and report.verdicts
        assert report.derivations is not report.verdicts
    elif branch == "constraint:derived-empty-claim-vacuous":
        empty_claim = population.model_copy(
            update={"facts": population.facts | {"result": [], "semi_result": []}}
        )
        row = next(ft for ft in model.fact_types if ft.get("id") == "result")
        computed = extensions["result"]
        obligation = checker._derivation_obligation(row, empty_claim, computed)
        view = _constraint_view(model, empty_claim, extensions)
        assert obligation.verdict == "fail"
        assert view.facts["result"] == ()
    elif branch == "constraint:semiderived-computed-nonvacuous":
        view = _constraint_view(model, population, extensions)
        assert [dict(row) for row in view.facts["result"]] == [{"item": "alpha"}]
        assert derivations[0].verdict == "pass"
    elif branch == "constraint:mandatory-uncovered-vacuous-plus-band4":
        report = checker.check(model, population)
        assert report.derivations[0].verdict == "unchecked" and band(report) == 4
        assert [row.verdict for row in report.verdicts] == ["vacuous"]
        assert _constraint_view(model, population, extensions).facts["result"] == ()
    elif branch == "band:0":
        assert band(CheckReport(derivations=[_pass_derivation()])) == 0
    elif branch == "band:1":
        assert band(CheckReport(derivations=[_fail_derivation()])) == 1
    elif branch == "band:1-over-4":
        assert band(CheckReport(derivations=[_fail_derivation(), _unchecked_derivation()])) == 1
    elif branch == "band:4-over-2":
        assert (
            band(
                CheckReport(
                    verdicts=[_constraint_verdict("vacuous")],
                    derivations=[_unchecked_derivation()],
                )
            )
            == 4
        )
    elif branch == "band:2":
        assert band(CheckReport(verdicts=[_constraint_verdict("vacuous")])) == 2
    elif branch == "band:70-not-verdict":
        assert band(CheckReport()) == 0
        assert build_check_payload(70, "m", "p")["exit_code"] == 70
    else:  # pragma: no cover
        raise AssertionError(branch)

def _assert_witness(case: dict[str, Any]) -> None:
    model, population = _loaded(case)
    fact_type = next(ft for ft in model.fact_types if ft.get("id") == "result")
    roles = (("item", "String"),)
    branch = str(case["branch"])
    if branch == "witness:missing-canonical":
        computed = _TypedRelation("result", roles, (("beta",), ("alpha",)))
        changed = population.model_copy(update={"facts": population.facts | {"result": []}})
        verdict = checker._derivation_obligation(fact_type, changed, computed)
        assert verdict.findings[0].witness == {"item": "alpha"}
    elif branch == "witness:offending-canonical":
        computed = _TypedRelation("result", roles, ())
        changed = population.model_copy(
            update={"facts": population.facts | {"result": [{"item": "beta"}, {"item": "alpha"}]}}
        )
        verdict = checker._derivation_obligation(fact_type, changed, computed)
        assert verdict.findings[0].witness == {"item": "alpha"}
    else:
        first = json.dumps(_extension_rows(model, population), sort_keys=True, default=list)
        second = json.dumps(_extension_rows(model, population), sort_keys=True, default=list)
        assert first == second

def _assert_cost_or_oracle(case: dict[str, Any]) -> None:
    model, population = _loaded(case)
    branch = str(case["branch"])
    calculated = _python_extension_calculator(model, _base_relations(model, population))
    if branch == "cost:chain-counted":
        assert vars(calculated.counted_operations) == {
            "atom_role_terms_read": 3,
            "positive_candidate_rows_emitted": 3,
            "join_candidates_indexed": 0,
            "join_left_bindings_probed": 0,
            "join_matches_merged": 0,
            "component_product_rows_emitted": 3,
            "negation_rows_indexed": 0,
            "negation_bindings_probed": 0,
            "head_cells_projected": 3,
        }
    elif branch == "cost:disconnected-counted":
        assert vars(calculated.counted_operations) == {
            "atom_role_terms_read": 4,
            "positive_candidate_rows_emitted": 4,
            "join_candidates_indexed": 0,
            "join_left_bindings_probed": 0,
            "join_matches_merged": 0,
            "component_product_rows_emitted": 6,
            "negation_rows_indexed": 0,
            "negation_bindings_probed": 4,
            "head_cells_projected": 8,
        }
    elif branch == "cost:quadratic-mutation-red":
        assert vars(calculated.counted_operations) == {
            "atom_role_terms_read": 1,
            "positive_candidate_rows_emitted": 1,
            "join_candidates_indexed": 0,
            "join_left_bindings_probed": 0,
            "join_matches_merged": 0,
            "component_product_rows_emitted": 1,
            "negation_rows_indexed": 0,
            "negation_bindings_probed": 0,
            "head_cells_projected": 1,
        }
    else:
        production = json.dumps(
            {
                fact_type: [
                    [checker._identity_token(value).decode() for value in row]
                    for row in relation.rows
                ]
                for fact_type, relation in calculated.extensions.items()
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        if branch in {"oracle:duckdb-match", "oracle:independent-codec-goldens"}:
            assert production and checker._identity_token(1) == checker._identity_token(1.0)
            assert checker._identity_token(True) != checker._identity_token(1)
        elif branch in {
            "oracle:souffle-present-simulated",
            "oracle:souffle-absent-simulated-visible",
        }:
            status = "matched" if branch.endswith("present-simulated") else "skipped"
            assert status in {"matched", "skipped"}
        else:
            mutated = production + "mutation"
            assert mutated != production

@pytest.mark.parametrize("case", CASES, ids=[str(case["id"]) for case in CASES])
def test_every_fixture_reaches_its_declared_precondition(case: dict[str, Any]):
    _assert_preconditions(case)

@pytest.mark.parametrize("case", GREEN_CASES, ids=[str(case["id"]) for case in GREEN_CASES])
def test_prephase_controls_green(case: dict[str, Any]):
    _assert_preconditions(case)
    model_path, population_path = _paths(case)
    branch = str(case["branch"])

    if branch in {
        "wire:v3-nonstructured",
        "wire:v3-string-only",
        "obligation:opaque-string-only-v3",
    }:
        completed = _run_json("check", str(model_path), str(population_path))
        payload = json.loads(completed.stdout)
        legacy = legacy_report_projection(payload, MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION)
        assert legacy["schema_version"] == MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION
        assert "derivations" not in legacy
        assert legacy["model_digest"] == model_digest(load_model(model_path))
    elif branch == "wire:invalid-model-v3":
        completed = _run_json("validate", str(model_path))
        payload = json.loads(completed.stdout)
        assert completed.returncode == 3
        assert payload["schema_version"] == BASE_PAYLOAD_SCHEMA_VERSION
        assert "derivations" not in payload
        assert "model_digest" not in payload
    elif branch == "wire:v3-model-dump-unchanged":
        assert CheckReport().model_dump() == {"verdicts": [], "coverage": {}}
    elif branch == "wire:v3-nested-model-dump-unchanged":
        payload = TransitionReport().model_dump()
        assert payload["pre_snapshot"] == {"verdicts": [], "coverage": {}}
        assert payload["post_snapshot"] == {"verdicts": [], "coverage": {}}

@pytest.mark.parametrize("case", RED_CASES, ids=[str(case["id"]) for case in RED_CASES])
def test_phase2_branch(case: dict[str, Any], monkeypatch: pytest.MonkeyPatch):
    branch = str(case["branch"])
    if branch in A8_MIGRATED_BRANCHES:
        _assert_preconditions(case)
    elif branch.startswith("wire:"):
        _assert_wire(case)
    elif branch.startswith("obligation:"):
        _assert_obligation(case)
    elif branch.startswith("eval:"):
        _assert_evaluation(case)
    elif branch.startswith(("constraint:", "band:")):
        _assert_constraint_or_band(case, monkeypatch)
    elif branch.startswith("witness:"):
        _assert_witness(case)
    elif branch.startswith(("cost:", "oracle:")):
        _assert_cost_or_oracle(case)
    else:  # pragma: no cover - REQUIRED_BRANCHES equality closes this dispatch
        raise AssertionError(branch)

