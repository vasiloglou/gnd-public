"""RC1 (rule-check-adoption): declared rule identity in gnd check, report version 15.

The corpus under tests/fixtures/rc1-rule-ids is the phase's approval instrument;
its README tells each case and expected/ holds the answers. Every case runs
from the corpus directory so the paths in the report are the ones written in
the README.
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc1-rule-ids"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())

FAIL = ["check", "models/components.orm.yaml", "populations/graph-fail.pop.yaml", "--rule-ids"]
JSON_CASES = {
    "declared-fail": [*FAIL, "--format", "json"],
    "positional-pass": [
        "check", "models/components-positional.orm.yaml", "populations/graph-pass.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
    "derivation-plain": [
        "check", "models/exact-terms.orm.yaml", "populations/term-ok.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
    "derivation-mod-zero": [
        "check", "models/exact-terms.orm.yaml", "populations/term-input.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
}
REFUSAL_CASES = {
    "refuse-redaction": "models/exact-terms-redacted.orm.yaml",
    "refuse-temporal": "models/temporal.orm.yaml",
    "refuse-reference": "models/reference/model.orm.yaml",
}


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _run(argv: list[str]):
    return run_main(argv, cwd=CORPUS)


def test_corpus_lists_every_case_once() -> None:
    cases = {*JSON_CASES, *REFUSAL_CASES, "text-declared-fail", "conflict-populations"}
    assert set(_exits()) == cases
    assert not (CORPUS / "populations" / "absent.pop.yaml").exists()


@pytest.mark.parametrize("case", sorted(JSON_CASES))
def test_json_case_matches_answer_key(case: str) -> None:
    result = _run(JSON_CASES[case])
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


def test_text_case_matches_answer_key() -> None:
    result = _run(FAIL)
    assert result.returncode == _exits()["text-declared-fail"]
    assert result.stdout == (EXPECTED / "declared-fail.txt").read_bytes()


@pytest.mark.parametrize("case", sorted(REFUSAL_CASES))
def test_refusal_precedes_population_load(case: str) -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())[case]
    result = _run(
        ["check", REFUSAL_CASES[case], "populations/absent.pop.yaml", "--rule-ids", "--format", "json"]
    )
    assert result.returncode == _exits()[case]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code"):
        assert payload[key] == expected[key]
    report = payload["report"] if "report_issue_rule_ids" in expected else payload
    if "report_schema_version" in expected:
        assert report["schema_version"] == expected["report_schema_version"]
    rule_ids = expected.get("issue_rule_ids", expected.get("report_issue_rule_ids"))
    assert [issue["rule_id"] for issue in report["issues"]] == rule_ids
    assert report["error"] is None


def test_rule_ids_with_another_arm_is_a_usage_error() -> None:
    result = _run(
        ["check", "models/components.orm.yaml", "--populations", "populations",
         "--rule-ids", "--format", "json"]
    )
    assert result.returncode == _exits()["conflict-populations"]
    assert result.stdout == b""
    # 64 must come from the deliberate conflict check, not from an unknown flag.
    assert b"unrecognized arguments" not in result.stderr
    assert b"--rule-ids" in result.stderr


# --- direct cases (spec §8) ---------------------------------------------------

COMPONENTS = (CORPUS / "models" / "components.orm.yaml").read_text()


def _write_model(tmp_path, text: str):
    path = tmp_path / "model.orm.yaml"
    path.write_text(text)
    return path


@pytest.mark.parametrize("remedy", ["7", '""', '"' + "x" * 2001 + '"'])
def test_t2_remedy_must_be_a_bounded_nonempty_string(tmp_path, remedy: str) -> None:
    text = COMPONENTS.replace(
        'remedy: "Move the component out of the legacy area, or retire it."', f"remedy: {remedy}"
    )
    assert text != COMPONENTS
    result = run_main(["validate", str(_write_model(tmp_path, text))])
    assert result.returncode == 3
    assert b"jsonschema:" in result.stdout


def test_t2_a_2000_character_remedy_is_accepted(tmp_path) -> None:
    text = COMPONENTS.replace(
        'remedy: "Move the component out of the legacy area, or retire it."',
        'remedy: "' + "x" * 2000 + '"',
    )
    assert run_main(["validate", str(_write_model(tmp_path, text))]).returncode == 0


def _payload(case: str) -> dict:
    return json.loads((EXPECTED / f"{case}.json").read_text())


def test_t4b_derivation_rules_hold_in_version_15() -> None:
    validator = Draft202012Validator(REPORT_SCHEMA)
    base = _payload("derivation-plain")
    assert validator.is_valid(base)
    for verdict, findings, reason in (
        ("pass", [{"kind": "derived-extension-incomplete", "message": "m", "witness": {}}], None),
        ("fail", [], None),
        ("unchecked", [], None),
    ):
        broken = json.loads(json.dumps(base))
        broken["derivations"][0].update(verdict=verdict, findings=findings, reason_code=reason)
        assert not validator.is_valid(broken), (verdict, reason)


def test_t6_version_15_is_closed_and_version_7_stays_closed() -> None:
    validator = Draft202012Validator(REPORT_SCHEMA)
    payload = _payload("declared-fail")
    missing = json.loads(json.dumps(payload))
    del missing["verdicts"][0]["row_novelty"]
    extra = json.loads(json.dumps(payload))
    extra["verdicts"][0]["unexpected"] = 1
    as_seven = json.loads(json.dumps(payload))
    as_seven["schema_version"] = 7
    for broken in (missing, extra, as_seven):
        assert not validator.is_valid(broken)
    # A version-7 report with one new key is refused: version 7 stays closed.
    seven = run_main(
        ["check", "models/components-positional.orm.yaml", "populations/graph-pass.pop.yaml",
         "--format", "json"],
        cwd=CORPUS,
    )
    report = json.loads(seven.stdout)
    assert report["schema_version"] == 7 and validator.is_valid(report)
    report["verdicts"][0]["address"] = "constraint:x"
    assert not validator.is_valid(report)


CONFLICTS = [
    ["--populations", "populations"], ["--pre", "p"], ["--steps", "s"], ["--post", "q"],
    ["--anchors", "a", "--document", "d"], ["--composition", "c", "--sources", "s"],
    ["--admission"], ["--compiled-operations"],
]


@pytest.mark.parametrize("extra", CONFLICTS, ids=lambda flags: flags[0])
def test_t7_conflicts_exit_64_before_the_model_is_read(extra: list[str]) -> None:
    result = run_main(["check", "no/such/model.orm.yaml", "no/such/pop.yaml", "--rule-ids", *extra])
    assert result.returncode == 64
    assert result.stdout == b""
    assert b"--rule-ids applies to one plain snapshot check" in result.stderr


def test_t7_unredacted_is_accepted_with_rule_ids() -> None:
    result = _run([*JSON_CASES["positional-pass"], "--unredacted"])
    assert result.returncode == 0
    assert result.stdout == (EXPECTED / "positional-pass.json").read_bytes()


def test_t10_text_without_the_flag_is_unchanged(tmp_path) -> None:
    plain = _run(FAIL[:-1])
    assert plain.returncode == 1
    text = plain.stdout.decode()
    assert "remedy:" not in text and "constraint:no_import_loops" not in text
    assert "  [fail] fact_types[component_uses_component].constraints[0]: " in text


def test_t10_positional_and_hostile_remedy_text(tmp_path) -> None:
    text = COMPONENTS.replace(
        "      - id: no_import_loops\n        type: ring", "      - type: ring"
    ).replace(
        'remedy: "Move the component out of the legacy area, or retire it."',
        'remedy: "first line\\nsecond line \\u00e9"',
    )
    model = _write_model(tmp_path, text)
    result = run_main(
        ["check", str(model), str(CORPUS / "populations" / "graph-fail.pop.yaml"), "--rule-ids"]
    )
    assert result.returncode == 1
    lines = result.stdout.decode().splitlines()
    assert "  [fail] fact_types[component_uses_component].constraints[0]: " in "\n".join(lines)
    remedy = [line for line in lines if line.startswith("    remedy: ")]
    assert any("first line\\nsecond line é" in line for line in remedy), remedy
    assert "second line" not in [line.strip() for line in lines]


def test_t12_coverage_refuses_a_version_15_report(tmp_path) -> None:
    report = tmp_path / "check.json"
    report.write_bytes((EXPECTED / "declared-fail.json").read_bytes())
    result = run_main(
        ["coverage", str(CORPUS / "models" / "components.orm.yaml"), "--check", str(report)]
    )
    assert result.returncode == 3
    assert b"schema_version 15" in result.stdout + result.stderr


def test_t13_identity_walk_is_linear_and_copies_nothing(monkeypatch) -> None:
    import time

    from gnd import checking_service, model_index
    from gnd.model import load_model

    model = load_model(CORPUS / "models" / "components-positional.orm.yaml")
    ring = model.fact_types[0]["constraints"][0]
    model.fact_types[0]["constraints"][:] = [dict(ring) for _ in range(2000)]

    def refuse(*_args, **_kwargs):
        raise AssertionError("the identity walk copied a row")

    # Building the index copies the document once, linearly; the walk must copy nothing.
    model_index.ModelIndex.for_model(model)
    monkeypatch.setattr(model_index, "deepcopy", refuse)
    started = time.perf_counter()
    declared = checking_service._declared_identities(model)
    elapsed = time.perf_counter() - started
    assert elapsed < 0.5
    assert len(declared) == 2001
    monkeypatch.undo()
    refs = [ref for ref, _, _ in model_index.ModelIndex.for_model(model).iter_constraints()]
    assert list(declared) == refs


def test_t15_a_remedy_edit_is_admitted_by_evolve() -> None:
    from gnd.evolve.policy import constraint_change

    assert constraint_change("remedy", "a", "b") == constraint_change("rationale", "a", "b")
    assert constraint_change("remedy", "a", "b") == "admitted"
