"""IH2: own-reference subtype joins are refused by name.

Spec: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH2-spec.md
(r1, delegated approval 2026-10-30, IH-D1 (b)). Tests T1, T3, T4 and T5 of its
test table; T2 is R1 in tests/test_il_close.py. Red first against IH1's head
(evidence/IH2/red.txt).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
IH2 = REPO_ROOT / "tests" / "fixtures" / "ilp_import_hardening" / "ih2"
CLOSE = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "close"
TOOL = REPO_ROOT / "tools" / "ilp_comparison.py"
#: R1's rule: a manager's team is the team a staff member of the same value works in.
HOLDS = "?a  f_manages  ?b   => ?a  f_works_in  ?b\t1.000000\t1.000000\t1.000000\t2\t-1\t2\t-1"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _import(tmp_path: Path, model: Path, population: Path, rules: str):
    work = tmp_path / "import"
    work.mkdir(parents=True)
    model = Path(shutil.copy(model, work / "model.orm.yaml"))
    population = Path(shutil.copy(population, work / "population.yaml"))
    export = work / "export"
    result = run_main(["export", "ilp", str(model), "--population", str(population),
                       "--target", "amie", "--out", str(export)])
    assert result.returncode == 0, result.stderr
    rules_path = work / "rules.txt"
    rules_path.write_text(f"{rules}\n", encoding="utf-8")
    record = {"schema_version": "gnd-mined-run/1", "learner": {"name": "amie", "version": "4.0.0"},
              "rules_sha256": _sha(rules_path.read_bytes()),
              "population_sha256": _sha(population.read_bytes()),
              "facts_sha256": _sha((export / "amie" / "facts.tsv").read_bytes())}
    (work / "reported.json").write_text(json.dumps(record), encoding="utf-8")
    out = work / "proposal.json"
    result = run_main(["import", "mined-rules", str(model), str(rules_path), "--population",
                       str(population), "--reported", str(work / "reported.json"), "--target", "amie",
                       "--out", str(out), "--actor", "ih2", "--requested-at", "2026-01-01T00:00:00Z"])
    return result.returncode, result.stderr.decode(), out


def _string_case(tmp_path: Path):
    return _import(tmp_path, IH2 / "ownref-string.orm.yaml", IH2 / "ownref-string.population.yaml", HOLDS)


# ---------------------------------------------------------------------------
# T1, T5: the plan's reproduction, refused before any count.
# ---------------------------------------------------------------------------

def test_t1_a_string_own_reference_join_is_refused_by_name(tmp_path):
    """The checker reads manager "1" and staff "1" as one value; the count spells them
    in two families. Before IH2 this was a false support-mismatch."""
    code, stderr, out = _string_case(tmp_path)
    assert code == 3 and not out.exists(), stderr
    assert stderr.startswith("rule 0: own-reference-join:"), stderr
    assert "?a" in stderr and "manager" in stderr and "staff" in stderr, stderr


def test_t5_the_mapping_refuses_before_the_count(tmp_path, monkeypatch):
    from gnd.export import ilp_amie

    def never(*_args, **_kwargs):
        raise AssertionError("an own-reference join reached the count")

    monkeypatch.setattr(ilp_amie, "count", never)
    code, stderr, _out = _string_case(tmp_path)
    assert code == 3 and stderr.startswith("rule 0: own-reference-join:"), stderr


# ---------------------------------------------------------------------------
# T3: the name's place in the tuple (IH1's T5 pins the docs table to it).
# ---------------------------------------------------------------------------

def test_t3_own_reference_join_is_the_last_mapping_refusal():
    from gnd.export import ilp_amie

    assert ilp_amie.MAPPING_REFUSALS[-2:] == ("type-confused-join", "own-reference-join")


# ---------------------------------------------------------------------------
# T4: joins inside one family are admitted as before; no version moves.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["subtype", "family"])
def test_t4_a_join_inside_one_family_is_admitted(tmp_path, name):
    """C1a and C1e's shapes: an inheriting subtype joined with its supertype, and two
    siblings of one family; both counted and admitted as before."""
    from gnd.export import ilp_amie

    cases = json.loads((CLOSE / "cases.json").read_text(encoding="utf-8"))["mined"]
    case = next(c for c in cases if c["model"] == f"{name}.orm.yaml" and c["expect"]["exit"] == 0)
    code, stderr, out = _import(tmp_path, CLOSE / case["model"], CLOSE / case["population"],
                                "\n".join(case["rules"]))
    assert code == 0 and out.exists(), stderr
    assert ilp_amie.ADAPTER_VERSION == "2"


# ---------------------------------------------------------------------------
# T6 to T8: the review's successors (notes/phase-IH2-review.md, F1 and F2).
# ---------------------------------------------------------------------------

def test_t6_a_diamond_with_two_reference_primitives_is_refused(tmp_path):
    """F1: director under manager and staff puts both in one family, but manager 1
    (Integer) and staff "1" (String) differ to the checker; before, exit 70."""
    code, stderr, out = _import(tmp_path, IH2 / "diamond.orm.yaml", IH2 / "diamond.population.yaml", HOLDS)
    assert code == 3 and not out.exists(), stderr
    assert stderr.startswith("rule 0: own-reference-join: variable ?a joins references of Integer and String"), \
        stderr


def test_t7_the_same_diamond_with_one_primitive_is_admitted(tmp_path):
    """F1's control: one reference primitive across the family, so the count agrees."""
    code, stderr, out = _import(tmp_path, IH2 / "diamond-string.orm.yaml",
                                IH2 / "diamond-string.population.yaml", HOLDS)
    assert code == 0 and out.exists(), stderr


def test_t8_an_own_reference_join_in_the_object_position_is_refused(tmp_path):
    """F2: the same join with the roles reversed, so ?a is each atom's object."""
    rule = "?b  f_manages  ?a   => ?b  f_works_in  ?a\t1.000000\t1.000000\t1.000000\t2\t-1\t2\t-1"
    code, stderr, out = _import(tmp_path, IH2 / "ownref-object.orm.yaml", IH2 / "ownref-object.population.yaml",
                                rule)
    assert code == 3 and not out.exists(), stderr
    assert stderr.startswith("rule 0: own-reference-join: variable ?a joins the families"), stderr


def test_t9_a_variable_over_a_type_with_two_kinds_of_reference_is_refused(tmp_path):
    """Close review 1, finding 1 (and reader 4's H1, overruled): director's reference
    resolves to Integer and String, so director may hold both 1 and "1"; the count spells
    them alike and the checker does not. A variable over director alone is refused too:
    with the mixed population, IH1's head exited 70 there."""
    model = IH2 / "diamond-director.orm.yaml"
    alone = "?a  f_directs  ?b   => ?a  f_heads  ?b\t1.000000\t1.000000\t1.000000\t1\t-1\t1\t-1"
    joined = "?a  f_directs  ?b   => ?a  f_works_in  ?b\t1.000000\t1.000000\t1.000000\t1\t-1\t1\t-1"
    for name, population, rule in (("mixed", "diamond-director-mixed", alone), ("alone", "diamond-director", alone),
                                   ("joined", "diamond-director", joined)):
        code, stderr, out = _import(tmp_path / name, model, IH2 / f"{population}.population.yaml", rule)
        assert code == 3 and not out.exists(), (name, stderr)
        assert stderr.startswith("rule 0: own-reference-join: variable ?a joins references of Integer and String"), \
            (name, stderr)


def test_t10_integer_and_number_references_are_one_kind(tmp_path):
    """Close review 1, finding 3: Integer and Number values spell and compare alike, so
    the diamond with those references is admitted, as before this milestone."""
    code, stderr, out = _import(tmp_path, IH2 / "diamond-number.orm.yaml", IH2 / "diamond-number.population.yaml",
                                HOLDS)
    assert code == 0 and out.exists(), stderr


def test_t11_a_type_under_two_unrelated_references_is_refused(tmp_path):
    """Close review 1, finding 2: d under x (String) and y (Integer), with no
    own-reference subtype; before, exit 70."""
    rule = "?a  f_leads  ?b   => ?a  f_heads  ?b\t1.000000\t1.000000\t1.000000\t1\t-1\t1\t-1"
    code, stderr, out = _import(tmp_path, IH2 / "tops.orm.yaml", IH2 / "tops.population.yaml", rule)
    assert code == 3 and not out.exists(), stderr
    assert stderr.startswith("rule 0: own-reference-join: variable ?a joins references of Integer and String"), stderr


def test_t4_the_comparison_tool_still_exits_0():
    result = subprocess.run([sys.executable, str(TOOL)], cwd=REPO_ROOT, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr.decode()
