"""Walking-skeleton end-to-end test.

Drives the full thin slice: model load (two-layer validation) -> population load
(one shared loader, YAML and JSON) -> deterministic checker (5-state verdict
lattice) -> CLI exit-code bands 0/1/2/3/4.

Band 4 is **indeterminate** (D-07, Phase 01.1): any *alethic* constraint carrying
an ``unchecked`` verdict withholds acceptance, because the checker never
mechanically evaluated a rule that IS the acceptance contract. Precedence is
3 > 1 > 4 > 2 > 0 (D-08), so an alethic ``fail`` still outranks indeterminacy.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from support.cli_runner import run_gnd_text as _run_cli

from gnd.checker import check
from gnd.commands import checking as patched_service
from gnd.model import ModelValidationError, load_model
from gnd.population import load_population

FIXTURES = Path(__file__).parent / "fixtures" / "skeleton"

MODEL = FIXTURES / "model.orm.yaml"
MODEL_BAD = FIXTURES / "model.bad.yaml"
POP_GOOD_YAML = FIXTURES / "population.good.yaml"
POP_GOOD_JSON = FIXTURES / "population.good.json"
POP_BAD = FIXTURES / "population.bad.yaml"
POP_VACUOUS = FIXTURES / "population.vacuous.yaml"


def test_good_population_all_pass():
    model = load_model(MODEL)
    population = load_population(POP_GOOD_YAML, model=model)
    report = check(model, population)

    assert report.verdicts, "checker must emit at least one verdict"
    bad = [v for v in report.verdicts if v.verdict in ("fail", "warning", "vacuous")]
    assert bad == [], f"good population must have no fail/warning/vacuous verdicts: {bad}"

    ring = [v for v in report.verdicts if v.constraint_type == "ring"]
    assert len(ring) == 1
    # Plan 01-03 implements the ring family: the skeleton's acyclic constraint
    # now evaluates (previously 'unchecked' under D-02).
    assert ring[0].verdict == "pass", "implemented ring constraint must evaluate to 'pass'"
    assert "acyclic" in ring[0].message


def test_json_yaml_parity():
    model = load_model(MODEL)
    from_yaml = load_population(POP_GOOD_YAML, model=model)
    from_json = load_population(POP_GOOD_JSON, model=model)
    assert from_yaml == from_json, "YAML and JSON must load to identical Population content"
    assert from_yaml.facts == from_json.facts
    assert from_yaml.instances == from_json.instances
    assert from_yaml.model == from_json.model
    assert from_yaml.source == from_json.source
    assert from_yaml.covers == from_json.covers


def test_bad_population_verdicts():
    model = load_model(MODEL)
    population = load_population(POP_BAD, model=model)
    report = check(model, population)

    uniqueness = [
        v
        for v in report.verdicts
        if v.constraint_type == "uniqueness" and "movie_has_title" in v.constraint_ref
    ]
    assert len(uniqueness) == 1
    assert uniqueness[0].modality == "alethic"
    assert uniqueness[0].verdict == "fail"
    assert uniqueness[0].message
    assert "1" in uniqueness[0].message, "message must name the offending movie instance"

    mandatory = [v for v in report.verdicts if v.constraint_type == "mandatory"]
    assert len(mandatory) == 1
    assert mandatory[0].modality == "alethic"
    assert mandatory[0].verdict == "fail"
    assert mandatory[0].message
    assert "3" in mandatory[0].message, "message must name the instance missing its mandatory role"

    value = [v for v in report.verdicts if v.constraint_type == "value"]
    assert len(value) == 1
    assert value[0].modality == "deontic"
    assert value[0].verdict == "warning", "violated deontic constraint yields warning, not fail"
    assert value[0].message
    assert "1520" in value[0].message, "message must name the out-of-range value"


def test_vacuous_population():
    model = load_model(MODEL)
    population = load_population(POP_VACUOUS, model=model)
    report = check(model, population)

    scoped = [v for v in report.verdicts if "movie_has_title" in v.constraint_ref]
    assert scoped, "movie_has_title constraints must receive verdicts"
    for verdict in scoped:
        assert verdict.verdict == "vacuous", (
            f"covered-but-empty fact type must yield 'vacuous', got {verdict!r}"
        )


def test_ill_formed_model_rejected():
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(MODEL_BAD)
    paths = [issue.path for issue in excinfo.value.issues]
    assert "$.fact_types" in paths, f"issues must point at $.fact_types, got {paths}"


def test_cli_exit_code_0_good():
    result = _run_cli("check", str(MODEL), str(POP_GOOD_YAML))
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_exit_code_1_bad_alethic_blocking():
    result = _run_cli("check", str(MODEL), str(POP_BAD))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "BLOCKING" in result.stdout


def test_cli_exit_code_2_vacuous():
    result = _run_cli("check", str(MODEL), str(POP_VACUOUS))
    assert result.returncode == 2, result.stdout + result.stderr


def test_cli_exit_code_3_ill_formed_model():
    result = _run_cli("validate", str(MODEL_BAD))
    assert result.returncode == 3, result.stdout + result.stderr
    assert "$.fact_types" in (result.stdout + result.stderr)


def test_cli_validate_good_model():
    result = _run_cli("validate", str(MODEL))
    assert result.returncode == 0, result.stdout + result.stderr


# --- band 4: indeterminate (D-07/D-08) ---

CHECKER_FIXTURES = Path(__file__).parent / "fixtures" / "checker"
MISC_MODEL = CHECKER_FIXTURES / "misc.orm.yaml"
POP_MISC_PASS = CHECKER_FIXTURES / "population.misc_pass.yaml"
POP_MISC_FAIL = CHECKER_FIXTURES / "population.misc_fail.yaml"


def test_cli_exit_code_4_unevaluated_alethic():
    """misc.orm.yaml carries three ALETHIC constraints the checker cannot
    mechanically evaluate (NOW() value-comparison, derivation-only
    subtype-partition, textual). Before band 4 this exited 0 — an affirmative
    claim of acceptance over data the checker never looked at."""
    result = _run_cli("check", str(MISC_MODEL), str(POP_MISC_PASS))
    assert result.returncode == 4, result.stdout + result.stderr
    blocking, advisory = result.stdout.split("ADVISORY (deontic)", maxsplit=1)
    assert "[unchecked]" in blocking
    assert "(none)" not in blocking
    assert "[unchecked]" not in advisory, (
        "alethic indeterminate results must not be presented as advisory"
    )


def test_cli_alethic_fail_outranks_indeterminate():
    """D-08 precedence 1 > 4: a definite failure is the more actionable signal,
    so the same model over a violating population still exits 1."""
    result = _run_cli("check", str(MISC_MODEL), str(POP_MISC_FAIL))
    assert result.returncode == 1, result.stdout + result.stderr


# --- CR-05: a population may not forge lines in the text renderer ---

ADVERSARIAL = Path(__file__).parent / "fixtures" / "adversarial"
OMISSION_MODEL = ADVERSARIAL / "models" / "omission.orm.yaml"
POP_LINE_FORGERY = ADVERSARIAL / "populations" / "line_forgery.json"


def test_a_hostile_fact_type_key_cannot_forge_lines_in_the_text_output():
    """`ValidationIssue.path` was built by raw f-string interpolation of the
    untrusted key (`path=f"$.facts.{key}"`) with no quoting or escaping at all,
    and `verbalize._quote` escaped only `\\` and `'`. `cli._print_issues` prints
    `f"ERROR at {issue.path}: {issue.message} [{issue.rule_id}]"` verbatim, so a
    fact-type key containing newlines forged BOTH the tool's `OK:` line and its
    verdict-tally line into the output an agent, a human or a log scraper reads
    — the verifier's own acceptance vocabulary, spoken by the population.

    The exit code was always 3 and the JSON payload always escaped correctly, so
    this is an output-integrity defect rather than a wrong verdict; the forged
    content is what makes it critical."""
    result = _run_cli("check", str(OMISSION_MODEL), str(POP_LINE_FORGERY))
    assert result.returncode == 3, result.stdout + result.stderr

    lines = result.stdout.splitlines()
    assert sum(line.startswith("ERROR at ") for line in lines) == 1, (
        f"one issue must render as exactly one line, got {lines!r}"
    )
    assert len(lines) == 1, f"the population added lines of its own: {lines!r}"
    for forged in ("OK: ", "pass=", "EXIT="):
        assert not any(line.lstrip().startswith(forged) for line in lines), (
            f"the population forged a {forged!r} line: {lines!r}"
        )
    assert "\\n" in result.stdout, "the newlines must survive as escape sequences"


# --- WR-03: usage/internal errors must never collide with the 0-4 bands ---


@pytest.mark.parametrize(
    "argv",
    [[], ["check"], ["check", "onlyonearg"], ["frobnicate"]],
    ids=["no-command", "check-no-args", "check-one-arg", "unknown-command"],
)
def test_cli_usage_errors_exit_64_not_band_2(argv):
    result = _run_cli(*argv)
    assert result.returncode == 64, (
        f"usage error must exit 64 (EX_USAGE), not a band code: "
        f"{result.returncode} — {result.stdout + result.stderr}"
    )


def test_internal_checker_error_exits_70_not_band_1(monkeypatch):
    """A checker bug must exit 70 (EX_SOFTWARE), never masquerade as an
    alethic fail (exit 1)."""
    import gnd.cli

    def _boom(model, population):
        raise ValueError("synthetic checker bug")

    monkeypatch.setattr(patched_service, "check", _boom)
    code = gnd.cli.main(["check", str(MODEL), str(POP_GOOD_YAML)])
    assert code == 70
