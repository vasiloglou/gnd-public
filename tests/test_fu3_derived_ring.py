"""FU3 (rule-check-followups): the acyclic extent of a ring over an exact-term derived fact type.

The corpus under tests/fixtures/fu3-derived-ring is the phase's approval
instrument (spec D1); its README tells each case and expected/ holds the
answers, recorded at main 1e63aeb5. Spec D2: the rows are the in-group
edges of the asserted facts of the derived fact type, as the checker
judges them.
"""

from __future__ import annotations

import json
from itertools import pairwise

import pytest
import yaml
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.graphs import strongly_connected_components

CORPUS = REPO_ROOT / "tests" / "fixtures" / "fu3-derived-ring"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())
CASES = ("agree", "add-disjoint", "asserted-only", "derived-only", "mod-zero")


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _check(case: str, *flags: str):
    return run_main(
        ["check", "models/ring.orm.yaml", f"populations/{case}.pop.yaml", *flags], cwd=CORPUS
    )


def _rows(case: str) -> list[list[int]]:
    result = _check(case, "--rule-ids", "--format", "json")
    (verdict,) = json.loads(result.stdout)["verdicts"]
    return verdict["offending_facts"]


def _asserted_edges(case: str) -> list[tuple[int, int]]:
    doc = yaml.safe_load((CORPUS / "populations" / f"{case}.pop.yaml").read_text())
    return [(fact["from"], fact["to"]) for fact in doc["facts"]["leads"]]


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == set(CASES)
    assert {path.stem for path in (CORPUS / "populations").glob("*.pop.yaml")} == {
        f"{case}.pop" for case in CASES
    }


@pytest.mark.parametrize("case", CASES)
def test_t1_rule_ids_case_matches_answer_key(case: str) -> None:
    result = _check(case, "--rule-ids", "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


@pytest.mark.parametrize("case", ["agree", "add-disjoint", "asserted-only"])
def test_t2_rows_are_the_in_group_edges_of_the_asserted_facts(case: str) -> None:
    edges = _asserted_edges(case)
    nodes = sorted({node for edge in edges for node in edge})
    successors = {node: [used for user, used in edges if user == node] for node in nodes}
    group = {
        node: number
        for number, component in enumerate(strongly_connected_components(nodes, successors))
        if len(component) > 1
        for node in component
    }
    expected = [
        [user, used] for user, used in edges if user in group and group[user] == group.get(used)
    ]
    rows = _rows(case)
    assert rows == expected
    (cycle,) = json.loads(_check(case, "--format", "json").stdout)["verdicts"][0]["offending_facts"]
    assert all([user, used] in rows for user, used in pairwise(cycle))


def test_t3_a_cycle_only_in_the_derived_set_gets_no_extent() -> None:
    v15 = json.loads(_check("derived-only", "--rule-ids", "--format", "json").stdout)
    v7 = json.loads(_check("derived-only", "--format", "json").stdout)
    assert [v["verdict"] for v in v15["verdicts"]] == ["pass"]
    assert v15["verdicts"][0]["offending_facts"] == []
    assert {k: v15["verdicts"][0][k] for k in v7["verdicts"][0]} == v7["verdicts"][0]


def test_t4_a_disjoint_cycle_leaves_existing_rows_unchanged() -> None:
    old, new = _rows("agree"), _rows("add-disjoint")
    assert new[: len(old)] == old
    assert new[len(old) :] == [[20, 21], [21, 20]]


def test_t5_an_unavailable_term_leaves_the_ring_unchecked() -> None:
    for flags in (("--rule-ids",), ()):
        result = _check("mod-zero", *flags, "--format", "json")
        (verdict,) = json.loads(result.stdout)["verdicts"]
        assert (result.returncode, verdict["verdict"], verdict["reason_code"]) == (
            4,
            "unchecked",
            "term:mod-zero",
        )
        assert verdict["offending_facts"] == []


@pytest.mark.parametrize("case", CASES)
def test_t6_version_7_is_unchanged(case: str) -> None:
    result = _check(case, "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.v7.json").read_bytes()
