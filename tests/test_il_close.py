"""IL-close part A: the close repairs, driven by their approval corpus.

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL-close-spec.md (r1,
approved 2026-10-29, §12). Under ILC-D9 (o) the cases are a corpus written
before the code: tests/fixtures/ilp_learners/close/cases.json, stories inline.
Each test names the cases it drives.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "gnd"
REFUNDS = SRC / "examples" / "refunds"
CLOSE = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "close"
IL4 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il4"
CASES = json.loads((CLOSE / "cases.json").read_text(encoding="utf-8"))
EVIDENCE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence"
BRIDGE = REPO_ROOT / "docs" / "reference" / "ilp-bridge.md"
TOOL = REPO_ROOT / "tools" / "ilp_comparison.py"
#: The IL4 run records as the runs wrote them, before ILC-D3 (o) re-derived them.
R0 = {1: "365eda612c7b62ce1e579c21533fb4793ad93ea2c9d35a2bb5d8497a94eca8c3",
      2: "366cefd20acc5f26bafb2c7582011db31bfa04695da4c69253582e3373128c74"}


def _ids(case: dict[str, Any]) -> str:
    return case["id"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# C1, C2: the mined-rules import (spec §6.1, §6.2).
# ---------------------------------------------------------------------------

def _fixture(name: str, kind: str) -> Path:
    if name == "STAFFING":
        return IL4 / ("model.orm.yaml" if kind == "model" else "population.yaml")
    return CLOSE / name if not Path(name).is_absolute() else Path(name)


def _rules(case: dict[str, Any]) -> list[str]:
    if case["rules"] == "IL4-A1":
        corpus = json.loads((IL4 / "rules.json").read_text(encoding="utf-8"))
        return next(c for c in corpus["import"] if c["id"] == "a1")["rules"]
    return case["rules"]


def _facts(tmp_path: Path, model: Path, population: Path) -> bytes:
    out = tmp_path / "export"
    result = run_main(["export", "ilp", str(model), "--population", str(population),
                       "--target", "amie", "--out", str(out)])
    assert result.returncode == 0, result.stderr
    return (out / "amie" / "facts.tsv").read_bytes()


def _binds_facts() -> bool:
    """Whether the shipped run-record schema has ``facts_sha256``; the red corpus is
    run against the old schema too, so each case shows its own defect, not the schema's."""
    schema = json.loads((SRC / "mined-import.schema.json").read_text(encoding="utf-8"))
    return "facts_sha256" in schema["$defs"]["run"]["properties"]


def _mined(tmp_path: Path, case: dict[str, Any]) -> tuple[Any, Path]:
    work = tmp_path / "import"
    work.mkdir()
    model = shutil.copy(_fixture(case["model"], "model"), work / "model.orm.yaml")
    population = shutil.copy(_fixture(case["population"], "population"), work / "population.yaml")
    rules = work / "rules.txt"
    rules.write_text("".join(f"{line}\n" for line in _rules(case)), encoding="utf-8")
    record = {"schema_version": "gnd-mined-run/1", "learner": {"name": "amie", "version": "4.0.0"},
              "rules_sha256": _sha(rules.read_bytes()),
              "population_sha256": _sha(Path(population).read_bytes())}
    facts = (EVIDENCE / "IL4/live/invocation-1/facts.tsv").read_bytes() if case.get("record") == "staffing" \
        else _facts(tmp_path, Path(model), Path(population))
    if case.get("record") != "no-facts" and _binds_facts():
        record["facts_sha256"] = _sha(facts)
    (work / "reported.json").write_text(json.dumps(record), encoding="utf-8")
    out = work / "proposal.json"
    result = run_main(["import", "mined-rules", str(model), str(rules), "--population", str(population),
                       "--reported", str(work / "reported.json"), "--target", "amie", "--out", str(out),
                       "--actor", "il-close", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json"])
    return result, out


@pytest.mark.parametrize("case", [c for c in CASES["mined"] if "rules" in c], ids=_ids)
def test_c1_c2_the_mined_import(tmp_path, case):
    """C1a, C1b, C1d, C1e, C2a, C2b."""
    result, out = _mined(tmp_path, case)
    expect = case["expect"]
    stderr = result.stderr.decode()
    assert result.returncode == expect["exit"], stderr
    if expect["exit"] != 0:
        assert not out.exists()
        if "refusal" in expect:
            assert re.match(rf"(?:rule \d+: )?{re.escape(expect['refusal'])}:", stderr), stderr
        assert expect.get("message", "") in stderr, stderr
        return
    report = json.loads(result.stdout)
    assert [[row["support"]["numerator"], row["support"]["denominator"]]
            for row in report["rules"]] == expect["support"]


def test_c1b_one_family_spells_every_value(tmp_path):
    """C1b: the family name, ``person``, spells staff, person and manager values alike."""
    case = next(c for c in CASES["mined"] if c["id"] == "C1b")
    facts = _facts(tmp_path, CLOSE / case["model"], CLOSE / case["population"])
    assert facts.decode("utf-8").splitlines() == case["expect"]["facts_tsv"]


def test_c1_the_family_is_the_least_top_type_of_the_component():
    """ILC-D1 (a), ILC-D2 (a): ``ilp_amie.family`` over the three fixture models."""
    from gnd.export import ilp_amie
    from gnd.model import load_model

    families = {name: ilp_amie.family(load_model(CLOSE / f"{name}.orm.yaml"))
                for name in ("subtype", "multi", "family")}
    assert families["subtype"]["manager"] == families["subtype"]["staff"] == "staff"
    assert {families["multi"][t] for t in ("manager", "staff", "person")} == {"person"}
    assert {families["family"][t] for t in ("p", "q", "x", "y", "w", "z")} == {"p"}
    for name, family in families.items():
        assert family["team"] == "team", name


def test_c1c_the_staffing_facts_are_unchanged(tmp_path):
    """C1c: no subtypes, so the staffing facts.tsv is the one both runs read."""
    facts = _facts(tmp_path, IL4 / "model.orm.yaml", IL4 / "population.yaml")
    assert facts == (EVIDENCE / "IL4/live/invocation-1/facts.tsv").read_bytes()


@pytest.mark.parametrize("invocation", [1, 2])
def test_c2c_the_run_records_are_re_derived(invocation):
    """C2c: each record gains the digest of its own retained facts.tsv; the run's bytes are kept."""
    live = EVIDENCE / f"IL4/live/invocation-{invocation}"
    original = (live / "reported-r0.json").read_bytes()
    assert _sha(original) == R0[invocation]
    derived = json.loads((live / "reported.json").read_text(encoding="utf-8"))
    assert derived == {**json.loads(original), "facts_sha256": _sha((live / "facts.tsv").read_bytes())}
    name = "amie" if invocation == 1 else "amie-2"
    assert (SRC / "examples/staffing/learners" / name / "reported.json").read_bytes() == \
        (live / "reported.json").read_bytes()


def test_c2_facts_mismatch_is_an_input_refusal_after_population_mismatch():
    from gnd.export.ilp_service import MINED_INPUT_REFUSALS

    assert MINED_INPUT_REFUSALS == ("learner-mismatch", "rules-mismatch", "population-mismatch",
                                    "facts-mismatch")


# ---------------------------------------------------------------------------
# C3, C11: the comparison tool (spec §6.3).
# ---------------------------------------------------------------------------

def _tool(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root)], capture_output=True,
                          text=True, timeout=300, check=False, cwd=REPO_ROOT)


def test_c3_an_uncountable_rule_fails_the_tool_loudly(tmp_path):
    case = next(c for c in CASES["comparison"] if c["id"] == "C3")
    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    for relative in (tool.EVIDENCE, tool.STAFFING, tool.GOLDEN, tool.BRIDGE):
        source, target = REPO_ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if source.is_dir() else shutil.copy)(source, target)
    rules = tmp_path / tool.EVIDENCE / "IL4/live/invocation-1/rules.txt"
    rules.write_text(rules.read_text(encoding="utf-8") + case["plant"] + "\n", encoding="utf-8")
    completed = _tool(tmp_path)
    assert completed.returncode == case["expect"]["exit"], completed.stderr
    assert case["expect"]["message"] in completed.stderr
    assert "Traceback" not in completed.stderr


def test_c11_the_committed_evidence_gives_the_committed_table():
    completed = _tool(REPO_ROOT)
    assert completed.returncode == 0, completed.stderr


# ---------------------------------------------------------------------------
# C4, C8a: check 9b and infix comparisons (spec §6.4, §6.8).
# ---------------------------------------------------------------------------

def _rewrite(model: Path, text: str) -> dict[str, Any]:
    from gnd.export import ilp
    from gnd.export.ilp_popper import parse_program
    from gnd.export.ilp_rewrite import rewrite
    from gnd.model import load_model

    loaded = load_model(model)
    shape, columns = ilp.schema(loaded, frozenset())
    return rewrite(parse_program(text)["clauses"][0], 0, shape, columns,
                   closures=ilp.type_closures(loaded))


@pytest.mark.parametrize("case", CASES["join"], ids=_ids)
def test_c4_an_infix_comparison_is_a_join(case):
    from gnd.export.ilp import IlpError

    expect = case["expect"]
    if "refusal" in expect:
        with pytest.raises(IlpError) as raised:
            _rewrite(CLOSE / case["model"], case["clause"])
        assert str(raised.value) == f"clause 0: {expect['refusal']}: {expect['message']}"
    else:
        assert _rewrite(CLOSE / case["model"], case["clause"])["consequent"] == expect["consequent"]


def test_c8a_the_join_check_counts_its_type_pairs():
    """C8a (IL1-Q5): one variable at three sites of three types is three pairs."""
    from gnd.export import ilp
    from gnd.export.ilp_rewrite import check_join_types
    from gnd.model import load_model

    model = load_model(CLOSE / "family.orm.yaml")
    shape, _columns = ilp.schema(model, frozenset())
    atoms = [{"predicate": name, "args": [{"var": "_"}, {"var": "A"}, {"var": "T"}]}
             for name in ("f_ry", "f_rw", "f_rp")]
    assert check_join_types(atoms, [], 0, shape, closures=ilp.type_closures(model)) == 3
    assert check_join_types(atoms[:2], [], 0, shape, closures=ilp.type_closures(model)) == 1


def test_c8b_a_subtype_closure_holds_its_supertypes():
    """C8b (IL6-Q1): ``type_closures`` with a subtype."""
    from gnd.export import ilp
    from gnd.model import load_model

    closures = ilp.type_closures(load_model(CLOSE / "subtype.orm.yaml"))
    assert closures["manager"] == frozenset({"manager", "staff"})
    assert closures["staff"] == frozenset({"staff"})
    multi = ilp.type_closures(load_model(CLOSE / "multi.orm.yaml"))
    assert multi["manager"] == frozenset({"manager", "staff", "person"})


# ---------------------------------------------------------------------------
# C5: ILASP comparison constants (spec §6.5).
# ---------------------------------------------------------------------------

def _ilasp(tmp_path: Path, text: str, coverage: list[list[str]]):
    export = tmp_path / "export"
    assert run_main(["export", "ilp", str(REFUNDS / "model.orm.yaml"), "--labels",
                     str(REFUNDS / "labels.json"), "--target", "ilasp", "--out", str(export)]).returncode == 0
    hypothesis = tmp_path / "hypothesis.las"
    hypothesis.write_text(text, encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": "ilasp", "version": "4.4.1"},
        "export_sha256": _sha((export / "export.json").read_bytes()),
        "clauses_sha256": _sha(hypothesis.read_bytes()),
        "coverage": [{"clause": k, "covered": ids} for k, ids in enumerate(coverage)]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(REFUNDS / "model.orm.yaml"), str(hypothesis),
                       "--labels", str(REFUNDS / "labels.json"), "--reported-coverage", str(run),
                       "--target", "ilasp", "--out", str(out), "--format", "json"])
    return result, out


@pytest.mark.parametrize("case", CASES["ilasp"], ids=_ids)
def test_c5_an_ilasp_constant_must_be_a_rendered_threshold(tmp_path, case):
    result, out = _ilasp(tmp_path, case["text"], case["coverage"])
    expect = case["expect"]
    stderr = result.stderr.decode()
    assert result.returncode == expect["exit"], stderr
    if expect["exit"]:
        assert stderr.startswith(f"clause {expect['clause']}: {expect['refusal']}:"), stderr
        assert expect.get("message", "") in stderr
        assert not out.exists()


def test_c5_off_threshold_is_an_import_refusal_of_the_ilasp_adapter():
    from gnd.export import ilp_asp

    assert ilp_asp.IMPORT_REFUSALS == ("off-threshold",)
    assert "off-threshold" not in ilp_asp.REFUSALS


# ---------------------------------------------------------------------------
# C6, C7: the Popper reader (spec §6.6, §6.7).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CASES["extract"], ids=_ids)
def test_c6_every_rule_in_the_solution_block_is_extracted(case):
    from gnd.export.ilp_popper import extract_program

    if "log" in case:
        assert extract_program(case["log"]) == case["expect"]
    else:
        live = EVIDENCE / case["evidence"]
        assert extract_program((live / "raw-stderr.txt").read_text(encoding="utf-8")) == \
            (live / case["expect"]).read_text(encoding="utf-8")


def test_c7_a_bare_boolean_is_a_boolean():
    from gnd.export.ilp_popper import parse_program

    case = CASES["booleans"][0]
    body = parse_program(case["clause"])["clauses"][0]["body"]
    found = [body[k]["atom"]["args"][position]["const"]
             for k, (position, _value) in enumerate(case["expect"])]
    assert [(type(value), value) for value in found] == \
        [(type(value), value) for _position, value in case["expect"]]


# ---------------------------------------------------------------------------
# C8c, C9: the bridge sections and the public names (spec §6.8, §6.9).
# ---------------------------------------------------------------------------

def _sections() -> dict[str, str]:
    text = BRIDGE.read_text(encoding="utf-8")
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    return {parts[k].strip(): parts[k + 1] for k in range(1, len(parts), 2)}


def _refusal_homes() -> dict[str, tuple[str, ...]]:
    from gnd.export import ilp_amie, ilp_asp, ilp_popper, ilp_rewrite, ilp_rules
    from gnd.export.ilp_service import MINED_INPUT_REFUSALS

    return {
        "Import": ilp_popper.IMPORT_REFUSALS,
        "ILASP adapter": (*ilp_asp.REFUSALS, *getattr(ilp_asp, "IMPORT_REFUSALS", ("off-threshold",))),
        "Boolean rule sets": (*ilp_rules.EXPORT_REFUSALS, *ilp_rules.REFUSALS),
        "AMIE-style miner": (*ilp_amie.EXPORT_REFUSALS, *MINED_INPUT_REFUSALS, "facts-mismatch",
                             *ilp_amie.MAPPING_REFUSALS, *ilp_amie.COUNT_REFUSALS),
        "The fragment table": ilp_rewrite.REFUSALS,
    }


@pytest.mark.parametrize("section", sorted(_refusal_homes()))
def test_c8c_each_refusal_is_named_in_its_adapter_section(section):
    text = _sections()[section]
    missing = [name for name in _refusal_homes()[section] if f"`{name}`" not in text]
    assert not missing, f"{section} does not name {missing}"


def test_c9_the_public_names_replace_the_private_ones():
    from gnd.export import ilp, ilp_popper

    assert "threshold_rows" in ilp_popper.__all__ and not hasattr(ilp_popper, "_threshold_rows")
    assert "export_value" in ilp.__all__ and not hasattr(ilp, "_value")


# ---------------------------------------------------------------------------
# R1 to R6: the adversarial review's findings (notes/phase-IL-close-agent-review.md),
# successors to the approved corpus; each was red against 2c4fba9.
# ---------------------------------------------------------------------------

_HOLDS = "?a  f_manages  ?b   => ?a  f_works_in  ?b\t1.000000\t1.000000\t1.000000\t2\t-1\t2\t-1"


def test_r1_an_own_reference_subtype_is_its_own_family(tmp_path):
    """Review 1: manager 1 (Integer) and staff "1" (String) are different values to the
    checker, so they must not share a spelling; the import refuses by name, never exit 70."""
    case = {"model": "ownref.orm.yaml", "population": "ownref.population.yaml", "rules": [_HOLDS]}
    (tmp_path / "facts").mkdir()
    facts = _facts(tmp_path / "facts", CLOSE / case["model"], CLOSE / case["population"]).decode()
    assert "manager:1\tf_manages\tteam:t1" in facts and "staff:1\tf_works_in\tteam:t1" in facts
    result, out = _mined(tmp_path, case)
    assert result.returncode == 3 and not out.exists(), result.stderr
    # IH2, IH-D1 (b) (o): refused by its own name before any count, not support-mismatch.
    assert result.stderr.decode().startswith("rule 0: own-reference-join:")


def test_r2_a_cyclic_hierarchy_is_one_family(tmp_path):
    """Review 2: a component with no top type is named by its least member."""
    from gnd.export import ilp_amie
    from gnd.model import load_model

    assert ilp_amie.family(load_model(CLOSE / "cyclic.orm.yaml"))["staff"] == "manager"
    result, _out = _mined(tmp_path, {"model": "cyclic.orm.yaml", "population": "subtype.population.yaml",
                                     "rules": [_HOLDS]})
    assert result.returncode == 0, result.stderr


def test_r3_an_undeclared_comparison_is_left_to_the_fragment_table(tmp_path):
    """Review 3: a predicate the export never declared is unknown-predicate, not off-threshold."""
    result, _out = _ilasp(tmp_path, "wrong :- f_refund_amount(V1,V2), gt_t_bogus(V2,5).\n", [[]])
    assert result.stderr.decode().startswith("clause 0: unknown-predicate:"), result.stderr


def test_r4_facts_no_export_could_write_are_a_facts_mismatch(tmp_path):
    """Review 4: the re-render's own refusal is reported as facts-mismatch, in the input order."""
    work = tmp_path / "pop"
    work.mkdir()
    population = work / "population.yaml"
    population.write_text((CLOSE / "subtype.population.yaml").read_text(encoding="utf-8")
                          .replace("covers: [manages, works_in]", "covers: []"), encoding="utf-8")
    # Any recorded digest will do: no export can write these facts.
    case = {"model": "subtype.orm.yaml", "population": str(population), "rules": [_HOLDS], "record": "staffing"}
    result, _out = _mined(tmp_path, case)
    assert result.returncode == 3
    assert result.stderr.decode().startswith("facts-mismatch:"), result.stderr
    assert "no-relations" in result.stderr.decode()


def test_r5_unreadable_rules_fail_the_tool_loudly(tmp_path):
    """Review 5: an unparsable rules file is exit 2 with its reason, not a traceback and exit 1."""
    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    for relative in (tool.EVIDENCE, tool.STAFFING, tool.GOLDEN, tool.BRIDGE):
        source, target = REPO_ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if source.is_dir() else shutil.copy)(source, target)
    rules = tmp_path / tool.EVIDENCE / "IL4/live/invocation-1/rules.txt"
    rules.write_text(rules.read_text(encoding="utf-8") + "garbage line\n", encoding="utf-8")
    completed = _tool(tmp_path)
    assert completed.returncode == 2, completed.stderr
    assert "unparsable: line 9" in completed.stderr and "Traceback" not in completed.stderr


@pytest.mark.parametrize(("change", "expected"), [
    ({"learner": {"name": "popper", "version": "1"}}, "learner-mismatch"),
    ({"rules_sha256": "0" * 64}, "rules-mismatch"),
    ({"population_sha256": "0" * 64}, "population-mismatch"),
])
def test_r6_facts_mismatch_comes_after_the_other_input_refusals(tmp_path, change, expected):
    """Review 6: with the facts also wrong, the earlier input refusal is named."""
    case = {"model": "subtype.orm.yaml", "population": "subtype.population.yaml", "rules": [_HOLDS]}
    (tmp_path / "good").mkdir()
    good, _out = _mined(tmp_path / "good", case)
    assert good.returncode == 0, good.stderr
    record = json.loads((tmp_path / "good" / "import" / "reported.json").read_text(encoding="utf-8"))
    work = tmp_path / "bad"
    work.mkdir()
    reported = work / "reported.json"
    reported.write_text(json.dumps({**record, "facts_sha256": "1" * 64, **change}), encoding="utf-8")
    imports = tmp_path / "good" / "import"
    result = run_main(["import", "mined-rules", str(imports / "model.orm.yaml"), str(imports / "rules.txt"),
                       "--population", str(imports / "population.yaml"), "--reported", str(reported),
                       "--target", "amie", "--out", str(work / "p.json")])
    assert result.returncode == 3
    assert result.stderr.decode().startswith(f"{expected}:"), result.stderr


# ---------------------------------------------------------------------------
# R7 to R9: the predicate-7 review's findings (notes/phase-IL-close-p7-review.md),
# successors to the approved corpus; each was red against 3c01567.
# ---------------------------------------------------------------------------

def _amounts(values: list[int]) -> dict[str, Any]:
    return {"predicates": [{"name": "f_r", "types": ["ex", "t_amount"]}],
            "comparisons": [{"name": f"{p}_t_amount", "operator": o, "type": "t_amount"}
                            for p, o in (("ge", ">="), ("gt", ">"), ("le", "<="), ("lt", "<"))],
            "examples": [{"id": f"e{k}", "label": "pos" if k % 2 else "neg"} for k in range(len(values))],
            "facts": [{"example": f"e{k}", "predicate": "f_r", "values": [v]} for k, v in enumerate(values)]}


@pytest.mark.parametrize("value", [2**31, -2**31 - 1])
def test_r7_popper_refuses_an_integer_clingo_would_wrap(value):
    """P7 review 1: Popper grounds bk.pl in clingo, so IL2-D14 binds its export too."""
    from gnd.export import ilp_popper
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError) as error:
        ilp_popper.render(_amounts([5, value]))
    assert error.value.code == 3
    assert str(error.value) == f"unrepresentable: {value} is outside clingo's 32-bit integer range (IL2-D14)"
    assert b"2147483647" in ilp_popper.render(_amounts([5, 2**31 - 1, -2**31]))["popper/bk.pl"]


def _popper(tmp_path: Path, text: str) -> tuple[Any, Path]:
    export = tmp_path / "export"
    assert run_main(["export", "ilp", str(REFUNDS / "model.orm.yaml"), "--labels",
                     str(REFUNDS / "labels.json"), "--target", "popper", "--out", str(export)]).returncode == 0
    clauses = tmp_path / "clauses.pl"
    clauses.write_text(text, encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": "popper", "version": "5.0.1"},
        "export_sha256": _sha((export / "export.json").read_bytes()),
        "clauses_sha256": _sha(clauses.read_bytes()), "coverage": [{"clause": 0, "covered": []}]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(REFUNDS / "model.orm.yaml"), str(clauses),
                       "--labels", str(REFUNDS / "labels.json"), "--reported-coverage", str(run),
                       "--target", "popper", "--out", str(out), "--format", "json"])
    return result, out


@pytest.mark.parametrize("name", ["gt_t_amount__501", "gt_t_amount__99999999999", "gt_t_amount__1500"])
def test_r8_a_popper_threshold_must_be_rendered(tmp_path, name):
    """P7 review 2: a threshold name not in bias.pl is off-threshold, as for ILASP.

    501 is no observed amount, 99999999999 none any export could hold, and
    gt at the maximum, 1500, holds for nothing, so it is not rendered."""
    result, out = _popper(tmp_path, f"wrong(V0):- f_refund_amount(V0,V1,V2), {name}(V2).\n")
    assert result.returncode == 3
    assert result.stderr.decode().startswith(f"clause 0: off-threshold: {name} "), result.stderr
    assert not out.exists()


def test_r8_a_rendered_popper_threshold_passes_the_check(tmp_path):
    result, _out = _popper(tmp_path, "wrong(V0):- f_refund_amount(V0,V1,V2), gt_t_amount__500(V2).\n")
    assert "off-threshold" not in result.stderr.decode(), result.stderr


def test_r8_off_threshold_is_an_import_refusal_of_the_popper_adapter():
    from gnd.export import ilp_popper
    from gnd.export.ilp_learners import LEARNERS

    assert ilp_popper.IMPORT_REFUSALS == ("off-threshold",)
    assert LEARNERS["popper"].vet is ilp_popper.check_thresholds


def test_r9_the_ilasp_extractor_hands_a_second_block_to_the_reader():
    """P7 review 3: every non-blank line after the last %% line, as IL2-F8 recorded."""
    from gnd.export.ilp import IlpError
    from gnd.export.ilp_asp import extract_hypothesis, parse_hypothesis

    text = extract_hypothesis("%%%%\n%% Total : 1s\n%%%%\nwrong :- p(V1).\n\n:- q(V1).\n")
    assert text == "wrong :- p(V1).\n:- q(V1).\n"
    with pytest.raises(IlpError, match="asp-constraint"):
        parse_hypothesis(text)
