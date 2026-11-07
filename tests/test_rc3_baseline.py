"""RC3 (rule-check-adoption): gnd check --baseline, new vs standing violations.

The corpus under tests/fixtures/rc3-baseline is the phase's approval
instrument; its README tells each case and expected/ holds the answers.
"""

from __future__ import annotations

import ast
import json
import time

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.baseline import VerdictView, compare

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc3-baseline"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())
JSON_CASES = ("standing-only", "mixed", "rowless-new", "head-vacuous", "base-unchecked")


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _baseline(case: str, *flags: str, model: str = "models/graph.orm.yaml"):
    return run_main(
        ["check", model, f"populations/{case}.head.pop.yaml",
         "--baseline", f"populations/{case}.base.pop.yaml", *flags],
        cwd=CORPUS,
    )


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == {*JSON_CASES, "text-mixed", "bad-base", "refuse-derivation",
                             "refuse-temporal", "conflict-populations"}
    assert not (CORPUS / "populations" / "absent.pop.yaml").exists()


@pytest.mark.parametrize("case", JSON_CASES)
def test_baseline_case_matches_answer_key(case: str) -> None:
    result = _baseline(case, "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


def test_text_case_matches_answer_key() -> None:
    result = _baseline("mixed")
    assert result.returncode == _exits()["text-mixed"]
    assert result.stdout == (EXPECTED / "mixed.txt").read_bytes()


def test_an_ill_formed_base_is_named() -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())["bad-base"]
    result = _baseline("bad-base", "--format", "json")
    assert result.returncode == _exits()["bad-base"]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code", "population"):
        assert payload[key] == expected[key]
    assert [[issue["path"], issue["rule_id"]] for issue in payload["issues"]] == expected["issues"]


@pytest.mark.parametrize(("case", "model"), [
    ("refuse-derivation", "models/derivations.orm.yaml"),
    ("refuse-temporal", "models/temporal.orm.yaml"),
])
def test_refusal_precedes_both_population_loads(case: str, model: str) -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())[case]
    result = run_main(
        ["check", model, "populations/absent.pop.yaml", "--baseline", "populations/absent.pop.yaml",
         "--format", "json"],
        cwd=CORPUS,
    )
    assert result.returncode == _exits()[case]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code"):
        assert payload[key] == expected[key]
    assert [issue["rule_id"] for issue in payload["issues"]] == expected["issue_rule_ids"]
    assert payload["error"] is None


def test_baseline_with_another_arm_is_a_usage_error() -> None:
    result = run_main(
        ["check", "models/graph.orm.yaml", "--populations", "populations",
         "--baseline", "populations/mixed.base.pop.yaml", "--format", "json"],
        cwd=CORPUS,
    )
    assert result.returncode == _exits()["conflict-populations"]
    assert result.stdout == b""
    assert b"unrecognized arguments" not in result.stderr


# --- Direct tests (spec §8) -----------------------------------------------------------

ADDRESSES = {"r1": ("constraint:loops", "declared-id"), "r2": ("constraints[0]", "positional")}


def test_t1_standing_new_and_resolved() -> None:
    head = [VerdictView("r1", "fail", "alethic", [["a", "b"], ["c", "d"]])]
    base = [VerdictView("r1", "fail", "alethic", [["a", "b"], ["x", "y"]])]
    result = compare(head, base, ADDRESSES)
    assert result.novelty["r1"] == ("new", ["standing", "new"])
    assert dict(result.counts) == {"new": 1, "standing": 1, "resolved": 1, "positional_keyed": 0, "undecided": 0}
    assert result.new_alethic_fail and not result.undecided_alethic


def test_t1_deontic_warnings_are_marked_but_never_fail() -> None:
    head = [VerdictView("r2", "warning", "deontic", ["a"])]
    result = compare(head, [], ADDRESSES)
    assert result.novelty["r2"] == ("new", ["new"])
    assert not result.new_alethic_fail
    assert result.counts["positional_keyed"] == 1


def test_t5_a_new_alethic_failure_outranks_a_base_left_unchecked(tmp_path) -> None:
    head = (CORPUS / "populations" / "mixed.head.pop.yaml").read_text().replace(
        "../models/graph.orm.yaml", str(CORPUS / "models" / "graph.orm.yaml"))
    (tmp_path / "head.pop.yaml").write_text(head)
    result = run_main(
        ["check", "models/graph.orm.yaml", str(tmp_path / "head.pop.yaml"),
         "--baseline", "populations/base-unchecked.base.pop.yaml", "--format", "json"],
        cwd=CORPUS,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["baseline"]["undecided"] == 1


def test_t6_keys_survive_reordering_and_unrelated_facts(tmp_path) -> None:
    lines = (CORPUS / "populations" / "mixed.head.pop.yaml").read_text().splitlines()
    header, body = lines[:3], lines[3:]
    uses = [line for line in body if line.startswith("    - { user")]
    rest = [line for line in body if not line.startswith("    - { user")]
    reordered = "\n".join([*header, *reversed(uses), "    - { user: q, used: r }", *rest]) + "\n"
    reordered = reordered.replace("../models/graph.orm.yaml", str(CORPUS / "models" / "graph.orm.yaml"))
    (tmp_path / "head.pop.yaml").write_text(reordered)
    shuffled = json.loads(run_main(
        ["check", "models/graph.orm.yaml", str(tmp_path / "head.pop.yaml"),
         "--baseline", "populations/mixed.base.pop.yaml", "--format", "json"], cwd=CORPUS).stdout)
    expected = json.loads((EXPECTED / "mixed.json").read_text())
    def marks(payload):
        return {
            (v["address"], json.dumps(row, sort_keys=True)): mark
            for v in payload["verdicts"] if v["row_novelty"]
            for row, mark in zip(v["offending_facts"], v["row_novelty"], strict=True)
        }
    # The inserted edge's two components have no owner, which adds advisory rows of
    # its own; the loop and legacy rows must be judged exactly as in the corpus case.
    judged = {key: mark for key, mark in marks(shuffled).items() if key[0] != "constraint:should_have_owner"}
    assert judged == marks(expected)


def test_t7_declared_keys_survive_an_inserted_rule_positional_keys_move() -> None:
    before = {"r1": ("constraint:loops", "declared-id"), "r2": ("constraints[0]", "positional")}
    after = {"r1": ("constraint:loops", "declared-id"), "r2": ("constraints[1]", "positional")}
    row = [{"$c": "old", "$a": "legacy"}]
    base = [VerdictView("r1", "fail", "alethic", [["a", "b"]]), VerdictView("r2", "fail", "alethic", row)]
    from gnd.baseline import baseline_key
    base_keys = {baseline_key(before[v.ref][0], r) for v in base for r in v.rows}
    assert baseline_key(after["r1"][0], ["a", "b"]) in base_keys
    assert baseline_key(after["r2"][0], row[0]) not in base_keys


def test_t8_validation_order_is_pinned_in_source() -> None:
    source = (REPO_ROOT / "src" / "gnd" / "checking_service.py").read_text()
    function = next(node for node in ast.walk(ast.parse(source))
                    if isinstance(node, ast.FunctionDef) and node.name == "_run_check_raw")
    body = ast.get_source_segment(source, function)
    steps = [
        "_resolve_model(model_input)",
        "refused = refuse_rule_ids(model)\n    if refused is not None:\n        return refused\n    if rule_ids:",
        '_resolve_population(population_input, model=model, name="population")',
        "read_population_bytes(base_coordinate)",
        "(evaluator or checker_module.check)(model, population)",
        "(evaluator or checker_module.check)(model, base_population)",
    ]
    refusal = body[body.index("def refuse_rule_ids("):body.index("_resolve_model(model_input)")]
    assert refusal.index("_rule_ids_refusal(refused)") < refusal.index("check:baseline-unsupported")
    positions = [body.index(step) for step in steps]
    assert positions == sorted(positions)


def test_t9_two_thousand_rows_a_side_compare_within_bound() -> None:
    head = [VerdictView("r1", "fail", "alethic", [[f"h{i}", f"n{i}"] for i in range(2000)])]
    base = [VerdictView("r1", "fail", "alethic", [[f"h{i}", f"n{i}"] for i in range(1000, 3000)])]
    started = time.perf_counter()
    result = compare(head, base, ADDRESSES)
    assert time.perf_counter() - started < 0.5
    assert dict(result.counts)["standing"] == 1000


def test_t10_every_family_reports_rows_of_values_only() -> None:
    from gnd.constraint_families import FAMILIES

    hooks = {entry.witness for entry in FAMILIES.values()}
    assert hooks == {"_row_projected_witness", "_flat_projected_witness"}
    from gnd.checker import _core

    assert _core._row_projected_witness([("a", 1)]) == [["a", 1]]
    assert _core._row_projected_witness([{"$c": "a"}]) == [{"$c": "a"}]
    assert _core._flat_projected_witness([("a",)]) == ["a"]


@pytest.mark.parametrize("arm", [
    ["--populations", "populations"], ["--pre", "x", "--steps", "y", "--post", "z"],
    ["--anchors", "x", "--document", "y"], ["--composition", "x", "--sources", "y"],
    ["--admission"], ["--compiled-operations"],
])
def test_t11_baseline_excludes_every_other_arm(arm) -> None:
    result = run_main(
        ["check", "missing.orm.yaml", "missing.pop.yaml", *arm, "--baseline", "missing.pop.yaml"],
        cwd=CORPUS,
    )
    assert result.returncode == 64
    assert result.stdout == b""
    assert b"--baseline applies to one plain snapshot check" in result.stderr


# --- Review regressions (notes/phase-RC3-codex-review.md, B1-B3) -------------------


def test_b1_one_number_spelled_two_ways_is_one_key() -> None:
    base = [VerdictView("r1", "fail", "alethic", [{"$i": "x", "$a": 1}])]
    head = [VerdictView("r1", "fail", "alethic", [{"$i": "x", "$a": 1.0}])]
    result = compare(head, base, ADDRESSES)
    assert result.novelty["r1"] == ("standing", ["standing"])
    assert dict(result.counts)["resolved"] == 0
    # A string is never the number it spells, and a boolean is never 1.
    for other in ("1", True):
        assert compare([VerdictView("r1", "fail", "alethic", [other])],
                       [VerdictView("r1", "fail", "alethic", [1])], ADDRESSES).novelty["r1"][0] == "new"


def test_b2_base_warnings_are_reported_and_named(tmp_path) -> None:
    base = (CORPUS / "populations" / "standing-only.base.pop.yaml").read_text()
    base = base.replace(" model_id: urn:gnd-fixture:rc3-graph@1,", "").replace(
        "../models/graph.orm.yaml", str(CORPUS / "models" / "graph.orm.yaml"))
    (tmp_path / "base.pop.yaml").write_text(base)
    result = run_main(
        ["check", "models/graph.orm.yaml", "populations/standing-only.head.pop.yaml",
         "--baseline", str(tmp_path / "base.pop.yaml"), "--format", "json"],
        cwd=CORPUS,
    )
    warnings = json.loads(result.stdout)["warnings"]
    assert [w["rule_id"] for w in warnings] == ["population:model-id-absent"]
    assert warnings[0]["path"].startswith("baseline:")


def test_b3_a_failing_base_evaluation_is_an_internal_error_payload() -> None:
    from gnd import checker
    from gnd.checking_service import _run_check_raw

    calls = []

    def evaluator(model, population):
        calls.append(population)
        if len(calls) == 2:
            raise RuntimeError("base evaluation failed")
        return checker.check(model, population)

    result = _run_check_raw(
        CORPUS / "models" / "graph.orm.yaml", CORPUS / "populations" / "standing-only.head.pop.yaml",
        evaluator=evaluator, baseline=CORPUS / "populations" / "standing-only.base.pop.yaml",
    )
    assert result.exit_code == 70
    assert result.payload["exit_code"] == 70
