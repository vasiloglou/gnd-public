"""IH1: one counting entry for the mined import.

Spec: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH1-spec.md
(r1, approved 2026-10-30). Tests T1 to T10 of its test table; T8 and T11 are
the unchanged golden, replay, RF6 and architecture suites. Red first against
IH0's head (evidence/IH1/red.txt).
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "gnd"
IL4 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il4"
LIVE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence" / "IL4" / "live"
TOOL = REPO_ROOT / "tools" / "ilp_comparison.py"
BRIDGE = REPO_ROOT / "docs" / "reference" / "ilp-bridge.md"
#: Rule 0 of the committed amie-2 run, which holds; and a rule the mapping refuses.
HOLDS = "?e  f_based_at  ?b  ?e  f_works_in  ?a   => ?a  f_team_site  ?b\t1.000000\t1.000000\t1.000000\t5\t5\t5\t-1"
REFLEXIVE = "?a  f_works_in  ?a   => ?a  f_based_at  ?a\t1.000000\t1.000000\t1.000000\t1\t1\t1\t-1"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _import(tmp_path: Path, rules: str, *, population: Path | None = None,
            record: dict[str, Any] | None = None):
    work = tmp_path / "import"
    work.mkdir()
    model = shutil.copy(IL4 / "model.orm.yaml", work / "model.orm.yaml")
    population = shutil.copy(population or IL4 / "population.yaml", work / "population.yaml")
    rules_path = work / "rules.txt"
    rules_path.write_text(rules, encoding="utf-8")
    reported = json.loads((LIVE / "invocation-2" / "reported.json").read_text(encoding="utf-8"))
    reported["rules_sha256"] = _sha(rules_path.read_bytes())
    reported.update(record or {})
    (work / "reported.json").write_text(json.dumps(reported), encoding="utf-8")
    out = work / "proposal.json"
    result = run_main(["import", "mined-rules", str(model), str(rules_path), "--population",
                       str(population), "--reported", str(work / "reported.json"), "--target", "amie",
                       "--out", str(out), "--actor", "ih1", "--requested-at", "2026-01-01T00:00:00Z"])
    return result.returncode, result.stderr.decode(), out


# ---------------------------------------------------------------------------
# T1, T6, T10: the public names, the provenance home, the export refusals.
# ---------------------------------------------------------------------------

def test_t1_the_counting_entry_is_public_and_the_tool_uses_it():
    from gnd.export import ilp_service

    for name in ("MinedInputs", "MinedTables", "MinedCount", "load_mined_inputs", "mined_tables",
                 "count_mined_rules"):
        assert name in ilp_service.__all__ and hasattr(ilp_service, name), name
    assert ilp_service._mined_inputs is ilp_service.load_mined_inputs
    assert ilp_service._Mined is ilp_service.MinedInputs
    assert not [path for path in (REPO_ROOT / "tools").rglob("*.py")
                if re.search(r"(?<![A-Za-z0-9])_mined_inputs\b", path.read_text(encoding="utf-8"))]


def test_t6_provenance_lives_in_ilp_amie_without_a_discover_edge():
    from gnd.export import ilp_amie

    assert "provenance" in ilp_amie.__all__
    tree = ast.parse((SRC / "export" / "ilp_amie.py").read_text(encoding="utf-8"))
    imported = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imported += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                 for alias in node.names]
    assert not [name for name in imported if name and name.startswith("gnd.discover")]
    pairs = [("a", "x"), ("b", "y"), ("a", "x"), ("c", "z")]
    assert ilp_amie.provenance(pairs, (("c", "z"), ("a", "x")), lambda fact_type, row: f"{fact_type}#{row}",
                               "works_in") == ["works_in#3", "works_in#0"]


def test_t10_the_amie_export_names_every_refusal_it_raises():
    from gnd.export import ilp_amie

    assert ilp_amie.EXPORT_REFUSALS == ("no-relations", "unrepresentable", "opaque", "too-large")


# ---------------------------------------------------------------------------
# T2: one admitting import builds the relation table and the pairs once.
# ---------------------------------------------------------------------------

def test_t2_an_admitting_import_builds_the_tables_once(tmp_path, monkeypatch):
    from gnd.export import ilp_amie

    calls = {"relation_table": 0, "pairs": 0}
    for name in calls:
        original = getattr(ilp_amie, name)

        def wrapped(*args, _original=original, _name=name, **kwargs):
            calls[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(ilp_amie, name, wrapped)
    code, stderr, out = _import(tmp_path, (LIVE / "invocation-2" / "rules.txt").read_text(encoding="utf-8"))
    assert code == 0, stderr
    assert out.exists()
    assert calls == {"relation_table": 1, "pairs": 1}


# ---------------------------------------------------------------------------
# T3: the entry returns the counts of rules that do not hold.
# ---------------------------------------------------------------------------

def test_t3_the_entry_counts_rules_that_do_not_hold():
    from gnd.export import ilp_amie
    from gnd.export.ilp_service import count_mined_rules, load_mined_inputs

    inputs = load_mined_inputs(IL4 / "model.orm.yaml", IL4 / "population.yaml")
    parsed = ilp_amie.parse_rules((LIVE / "invocation-1" / "rules.txt").read_text(encoding="utf-8"))
    counted = count_mined_rules(inputs, parsed)
    assert len(counted.counts) == len(counted.rules) == 8
    holds = [c.denominator > 0 and c.numerator == c.denominator for c in counted.counts]
    assert holds.count(False) == 6


# ---------------------------------------------------------------------------
# T4, T9: the import's input order.
# ---------------------------------------------------------------------------

def test_t4_facts_mismatch_precedes_every_mapping_refusal(tmp_path):
    code, stderr, out = _import(tmp_path, REFLEXIVE + "\n", record={"facts_sha256": "0" * 64})
    assert code == 3, stderr
    assert stderr.startswith("facts-mismatch:"), stderr
    assert not out.exists()


def test_t9_population_mismatch_precedes_loading_the_population(tmp_path):
    broken = tmp_path / "broken.yaml"
    broken.write_text("format_version: 2\npopulation: [unclosed\n", encoding="utf-8")
    code, stderr, out = _import(tmp_path, HOLDS + "\n", population=broken)
    assert code == 3, stderr
    assert stderr.startswith("population-mismatch:"), stderr
    assert not out.exists()


# ---------------------------------------------------------------------------
# T5: the refusal order has one home, the AMIE section of the bridge page.
# ---------------------------------------------------------------------------

def _amie_section() -> str:
    text = BRIDGE.read_text(encoding="utf-8")
    return text.split("\n## AMIE-style miner\n", 1)[1].split("\n## ", 1)[0]


def _documented_order() -> tuple[list[str], list[str]]:
    section = _amie_section()
    mapping = section.split("**The mapping.**", 1)[1].split("**The counting.**", 1)[0]
    counting = section.split("**The counting.**", 1)[1].split("**The proposal**", 1)[0]
    table = [line for line in mapping.splitlines() if line.startswith("| ") and "refused `" in line]
    return ([re.search(r"refused `([a-z-]+)`", line).group(1) for line in table],
            re.findall(r"refused `([a-z-]+)`", counting))


def test_t5_the_refusal_tuples_follow_the_documented_order():
    from gnd.export import ilp_amie

    mapping, counting = _documented_order()
    assert list(ilp_amie.MAPPING_REFUSALS) == mapping
    assert list(ilp_amie.COUNT_REFUSALS) == counting


@pytest.mark.parametrize("name", ["MAPPING_REFUSALS", "COUNT_REFUSALS"])
def test_t5_the_pin_fails_on_a_swapped_tuple(monkeypatch, name):
    from gnd.export import ilp_amie

    names = list(getattr(ilp_amie, name))
    names[0], names[1] = names[1], names[0]
    monkeypatch.setattr(ilp_amie, name, tuple(names))
    with pytest.raises(AssertionError):
        test_t5_the_refusal_tuples_follow_the_documented_order()


# ---------------------------------------------------------------------------
# T7: hold() reports every mapping refusal before any count refusal (IH1-D2 (o)).
# ---------------------------------------------------------------------------

def _large_population() -> str:
    """Staffing with 1,001 staff, so rule HOLDS's body joins over 1,002,001 rows."""
    staff = [f"s{k:04d}" for k in range(1001)]
    document = {
        "format_version": 2,
        "population": {"model": "model.orm.yaml", "model_id": "staffing", "source": "fixture",
                       "covers": ["works_in", "team_site", "based_at", "parks_at", "is_contractor"]},
        "instances": {"staff": staff, "team": ["t1"], "site": ["north"]},
        "facts": {"works_in": [{"staff": s, "team": "t1"} for s in staff],
                  "team_site": [{"team": "t1", "site": "north"}],
                  "based_at": [{"staff": s, "site": "north"} for s in staff]},
    }
    return json.dumps(document)


def test_t7_hold_reports_mapping_refusals_before_too_large(tmp_path):
    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    staffing = tmp_path / tool.STAFFING
    staffing.mkdir(parents=True)
    shutil.copy(IL4 / "model.orm.yaml", staffing / "model.orm.yaml")
    (staffing / "population.yaml").write_text(_large_population(), encoding="utf-8")
    with pytest.raises(tool.ComparisonError, match=r"^rule 1: reflexive-atom:"):
        tool.hold(tmp_path, f"{HOLDS}\n{REFLEXIVE}\n")


# ---------------------------------------------------------------------------
# Fix review (IH1): H1, a population fault in hold(); C1, IH1-D4 on the import.
# ---------------------------------------------------------------------------

def test_t12_hold_names_a_population_fault_as_the_population(tmp_path):
    from gnd.export.ilp import IlpError

    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    staffing = tmp_path / tool.STAFFING
    staffing.mkdir(parents=True)
    shutil.copy(IL4 / "model.orm.yaml", staffing / "model.orm.yaml")
    text = (IL4 / "population.yaml").read_text(encoding="utf-8")
    (staffing / "population.yaml").write_text(
        text.replace('{ staff: "s01", team: "t1" }', '{ staff: {"$opaque": "x"}, team: "t1" }', 1),
        encoding="utf-8")
    with pytest.raises(IlpError, match=r"^opaque: fact type 'works_in'"):
        tool.hold(tmp_path, f"{HOLDS}\n")


#: A rule GND counts 0 of 1 while the miner reports Support 1: s0000 parks at east,
#: and t1 does not sit there, so it is refused support-mismatch.
MISCOUNTED = ("?e  f_parks_at  ?b  ?e  f_works_in  ?a   => ?a  f_team_site  ?b"
                  "\t1.000000\t1.000000\t1.000000\t1\t1\t1\t-1")


def test_t13_the_import_reports_too_large_before_an_earlier_admission_refusal(tmp_path):
    population = tmp_path / "large.yaml"
    document = json.loads(_large_population())
    document["population"]["covers"] = ["works_in", "team_site", "based_at", "parks_at"]
    document["instances"]["site"] = ["north", "east"]
    document["facts"]["parks_at"] = [{"staff": "s0000", "site": "east"}]
    population.write_text(json.dumps(document), encoding="utf-8")
    export = tmp_path / "export"
    assert run_main(["export", "ilp", str(IL4 / "model.orm.yaml"), "--population", str(population),
                     "--target", "amie", "--out", str(export)]).returncode == 0
    record = {"population_sha256": _sha(population.read_bytes()),
              "facts_sha256": _sha((export / "amie" / "facts.tsv").read_bytes())}
    code, stderr, out = _import(tmp_path, f"{MISCOUNTED}\n{HOLDS}\n", population=population,
                                record=record)
    assert code == 3, stderr
    assert stderr.startswith("rule 1: too-large:"), stderr
    assert not out.exists()
