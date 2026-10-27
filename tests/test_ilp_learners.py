"""IL1: the learner registry, the type-confused join check and SWI octal escapes (ilp-learners).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL1-spec.md (r3, approved
2026-10-27, with its §12-§14 gate record and findings). Under IL1-D1 the escape
and join cases are a corpus written before the code:
tests/fixtures/ilp_learners/il1/escapes.json and joins.json, stories inline.
"""

from __future__ import annotations

import argparse
import getpass
import importlib.util
import json
import re
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main
from test_ik_close import DOWNSTREAM_JOINED, joined_hits
from test_ilp_bridge import CASES, CORPUS, _bound_run, _import, _work

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "gnd"
IL1 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il1"
ESCAPES = json.loads((IL1 / "escapes.json").read_text(encoding="utf-8"))
JOINS = json.loads((IL1 / "joins.json").read_text(encoding="utf-8"))
MILESTONE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners"


# ---------------------------------------------------------------------------
# T2, T3: one registry, in declaration order; the CLI and both schema enums equal it.
# ---------------------------------------------------------------------------

def _subparser(parser: argparse.ArgumentParser, *path: str) -> argparse.ArgumentParser:
    for name in path:
        action = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
        parser = action.choices[name]
    return parser


def _root_parser(monkeypatch: pytest.MonkeyPatch) -> argparse.ArgumentParser:
    from gnd import cli

    captured: list[argparse.ArgumentParser] = []

    class Captured(Exception):
        pass

    def capture(parser, _args=None, _namespace=None):
        captured.append(parser)
        raise Captured

    monkeypatch.setattr(cli._BandSafeParser, "parse_args", capture)
    with pytest.raises(Captured):
        cli.main([])
    return captured[0]


def _choices(parser: argparse.ArgumentParser, dest: str) -> tuple[str, ...]:
    return tuple(next(a for a in parser._actions if a.dest == dest).choices)


def test_t2_registry_cli_and_schema_enums_agree(monkeypatch):
    from gnd.export import ilp_learners

    assert tuple(ilp_learners.LEARNERS) == ("popper", "neutral")
    assert ilp_learners.EXPORT_TARGETS == ("popper", "neutral")
    assert ilp_learners.IMPORT_TARGETS == ("popper", "neutral")
    root = _root_parser(monkeypatch)
    assert _choices(_subparser(root, "export", "ilp"), "target") == ilp_learners.EXPORT_TARGETS
    assert _choices(_subparser(root, "import", "ilp-rules"), "target") == ilp_learners.IMPORT_TARGETS
    export_enum = json.loads((SRC / "ilp.schema.json").read_text())
    import_enum = json.loads((SRC / "ilp-import.schema.json").read_text())

    def enums(node: Any) -> list[list[str]]:
        found = []
        if isinstance(node, dict):
            if isinstance(node.get("target"), dict) and "enum" in node["target"]:
                found.append(node["target"]["enum"])
            for value in node.values():
                found += enums(value)
        elif isinstance(node, list):
            for value in node:
                found += enums(value)
        return found

    assert enums(export_enum) == [list(ilp_learners.EXPORT_TARGETS)]
    assert enums(import_enum) == [list(ilp_learners.IMPORT_TARGETS)]


def test_t3_the_registry_is_what_the_service_consults(tmp_path, monkeypatch):
    """A fake entry reaches the export tree, the method token and the learner check."""
    from gnd.export import ilp_learners, ilp_service

    def render(neutral: dict[str, Any]) -> dict[str, bytes]:
        return {"fake/examples.txt": "\n".join(e["id"] for e in neutral["examples"]).encode()}

    monkeypatch.setitem(ilp_learners.LEARNERS, "fake", ilp_learners.Learner(
        target="fake", learner="fake", method="ilp-fake", exports=True, render=render,
        parse=None, contract="labelled-clauses"))
    work = _work(tmp_path)
    model, labels = work / CASES["model"], work / "m.labels.json"
    prepared = ilp_service._prepare(model, labels, "fake")
    assert "fake/examples.txt" in prepared.tree

    clauses = work / "i1.clauses.json"
    i1 = json.loads((work / "i1.run.json").read_text())
    run = work / "fake.run.json"

    def importing(name: str, out: Path) -> int:
        run.write_text(json.dumps({**i1, "learner": {"name": name, "version": "1"},
                                   "export_sha256": prepared.digest}))
        return ilp_service._cmd_import_ilp_rules(
            str(model), str(clauses), str(labels), str(run), target="fake", out=str(out),
            actor="t3", requested_at=None, output_format="json")

    assert importing("popper", tmp_path / "refused.json") == 3
    assert importing("fake", tmp_path / "admitted.json") == 0
    proposal = json.loads((tmp_path / "admitted.json").read_text())
    methods = {op["after"]["provenance"]["induction"]["method"] for op in proposal["operations"]}
    assert methods == {"ilp-fake"}


def test_t3_learner_mismatch_names_the_registered_learner(tmp_path, capfd):
    work = _work(tmp_path)
    run = json.loads((work / "i2.run.json").read_text())
    run["learner"]["name"] = "aleph"
    path = work / "aleph.run.json"
    path.write_text(json.dumps(run))
    result = _import(work, work / "i2.popper.pl", path, tmp_path / "out.json", "popper")
    assert result.returncode == 3
    assert b"learner-mismatch: a popper import needs a popper run record, not 'aleph'" in result.stderr


def test_t3_the_service_names_no_learner():
    source = (SRC / "export" / "ilp_service.py").read_text(encoding="utf-8")
    assert '"popper"' not in source and "'popper'" not in source


@pytest.mark.parametrize("command", [
    ["export", "ilp", "m.yaml", "--labels", "l.json", "--target", "bogus", "--out", "o"],
    ["import", "ilp-rules", "m.yaml", "c.json", "--labels", "l.json", "--reported-coverage",
     "r.json", "--target", "bogus", "--out", "o.json"],
])
def test_t3b_an_unknown_target_is_a_usage_error(command):
    assert run_main(command).returncode == 64


# ---------------------------------------------------------------------------
# T4, T4b: SWI octal escapes (corpus escapes.json).
# ---------------------------------------------------------------------------

def _constants(document: dict[str, Any]) -> list[Any]:
    return [term["const"] for clause in document["clauses"] for literal in clause["body"]
            for term in literal.get("atom", {}).get("args", []) if "const" in term]


@pytest.mark.parametrize("case", ESCAPES["accept"], ids=lambda case: case["id"])
def test_t4_octal_escapes_parse(case):
    from gnd.export.ilp_popper import parse_program

    assert _constants(parse_program(case["program"])) == case["constants"]


@pytest.mark.parametrize("case", ESCAPES["refuse"], ids=lambda case: case["id"])
def test_t4b_malformed_octal_escapes_are_refused(case):
    from gnd.export.ilp import IlpError
    from gnd.export.ilp_popper import parse_program

    with pytest.raises(IlpError) as raised:
        parse_program(case["program"])
    assert raised.value.code == 3
    message = str(raised.value)
    assert message.startswith(f"unparsable: line {case['line']}, column ")
    assert ESCAPES["refusal"] in message


# ---------------------------------------------------------------------------
# T5: the type-confused join check (corpus joins.json), D12 (o) and D13 (o).
# ---------------------------------------------------------------------------

def _join_import(tmp_path: Path, case: dict[str, Any]):
    work = _work(tmp_path)
    if case["target"] == "popper":
        clauses = work / f"{case['id']}.popper.pl"
        clauses.write_text(case["program"] + "\n", encoding="utf-8")
    else:
        clauses = work / f"{case['id']}.clauses.json"
        clauses.write_text(json.dumps({"schema_version": "gnd-ilp-clauses/1",
                                       "clauses": case["clauses"]}), encoding="utf-8")
    run = _bound_run(work, clauses, [[]], case["target"])
    out = tmp_path / f"{case['id']}.out.json"
    return _import(work, clauses, run, out, case["target"]), out


@pytest.mark.parametrize("case", JOINS["cases"], ids=lambda case: case["id"])
def test_t5_type_confused_joins(tmp_path, case):
    result, out = _join_import(tmp_path, case)
    stderr = result.stderr.decode("utf-8", errors="replace")
    if "refusal" in case:
        assert result.returncode == case["exit"], stderr
        assert f"clause {case['clause']}: {case['refusal']}" in stderr, stderr
        assert not out.exists()
    else:
        assert case["not_refusal"] not in stderr, stderr


def _orders_shape(extra: str = "") -> tuple[dict[str, Any], dict[str, Any], dict[str, frozenset[str]]]:
    from gnd.export import ilp
    from gnd.model import load_model_bytes

    text = (CORPUS / CASES["model"]).read_text(encoding="utf-8")
    if extra:
        text = text.replace("fact_types:\n", QUANTITY_TYPE + "fact_types:\n").replace(
            "constraints: []\n", extra)
    model = load_model_bytes(text.encode("utf-8"), source=CORPUS / CASES["model"])
    shape, columns = ilp.schema(model, frozenset())
    return shape, columns, ilp.type_closures(model)


QUANTITY_TYPE = """\
  - id: quantity
    name: Quantity
    kind: value
    primitive: Integer
"""
QUANTITY = """\
  - id: order_quantity
    reading: "{Order} has {Quantity}"
    roles:
      - { object_type: order, role_name: order }
      - { object_type: quantity, role_name: quantity }
constraints: []
"""


def _clause(program: str) -> dict[str, Any]:
    from gnd.export.ilp_popper import parse_program

    return parse_program(program)["clauses"][0]


def test_t5e_a_comparison_of_another_integer_type_is_type_confused():
    from gnd.export.ilp import IlpError
    from gnd.export.ilp_rewrite import rewrite

    shape, columns, closures = _orders_shape(QUANTITY)
    shape_text = json.dumps(shape)
    assert "t_quantity" in shape_text
    clause = _clause("wrong(A):- f_order_amount(A,B,C),gt_t_quantity(C,5).")
    with pytest.raises(IlpError, match=r"^clause 0: type-confused-join: "):
        rewrite(clause, 0, shape, columns, closures=closures)
    same = _clause("wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,5).")
    assert rewrite(same, 0, shape, columns, closures=closures)["type"] == "guarded"


def test_t5f_without_closures_the_join_check_is_skipped():
    from gnd.export.ilp_rewrite import rewrite

    shape, columns, _closures = _orders_shape()
    confused = _clause(JOINS["cases"][0]["program"])
    assert rewrite(confused, 0, shape, columns)["type"] == "guarded"


def test_t5b_subtypes_join_their_supertypes():
    from gnd.export.ilp import IlpError
    from gnd.export.ilp_rewrite import check_join_types

    neutral = {
        "types": [{"name": "t_vip", "object_type": "vip", "primitive": None},
                  {"name": "t_customer", "object_type": "customer", "primitive": None},
                  {"name": "t_amount", "object_type": "amount", "primitive": "integer"}],
        "predicates": [{"name": "f_vip_since", "types": ["ex", "t_vip"]},
                       {"name": "f_customer_blocked", "types": ["ex", "t_customer"]},
                       {"name": "f_amount_seen", "types": ["ex", "t_amount"]}],
        "comparisons": [],
    }
    closures = {"vip": frozenset({"vip", "customer"}), "customer": frozenset({"customer"}),
                "amount": frozenset({"amount"})}

    def atom(predicate: str, var: str) -> dict[str, Any]:
        return {"predicate": predicate, "args": [{"var": "A"}, {"var": var}]}

    assert check_join_types([atom("f_vip_since", "X"), atom("f_customer_blocked", "X")], [], 0,
                            neutral, closures=closures) > 0
    with pytest.raises(IlpError, match="type-confused-join: clause 0|clause 0: type-confused-join"):
        check_join_types([atom("f_vip_since", "X"), atom("f_amount_seen", "X")], [], 0,
                         neutral, closures=closures)
    anonymous = [atom("f_vip_since", "_"), atom("f_amount_seen", "_")]
    assert check_join_types(anonymous, [], 0, neutral, closures=closures) == 0


def test_t5c_the_join_check_is_bounded_on_the_largest_clauses():
    """Standing rule 2: 32 clauses of 16 atoms each, one variable at every site."""
    from gnd.export.ilp_rewrite import check_join_types

    shape, _columns, closures = _orders_shape()
    atoms = [{"predicate": "f_order_flagged", "args": [{"var": "A"}, {"var": "B"}]}] * 16
    started = time.perf_counter()
    pairs = sum(check_join_types(atoms, [], k, shape, closures=closures) for k in range(32))
    assert time.perf_counter() - started < 1.0
    assert pairs == 0  # one distinct object type per variable: no pair to compare


# ---------------------------------------------------------------------------
# T7: no learner is a dependency (IL-R1).
# ---------------------------------------------------------------------------

LEARNER_NAMES = ("popper", "ilasp", "fastlas", "clingo", "swipl", "amie", "imodels", "corels")


def _named(requirements: list[str]) -> list[str]:
    return [line for line in requirements
            if re.split(r"[\s;<>=!~\[]", line.strip().lower(), maxsplit=1)[0] in LEARNER_NAMES]


def test_t7_no_learner_in_pyproject_or_the_built_wheel(tmp_path):
    import tomllib

    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    declared = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        declared += group
    assert _named(declared) == []
    uv = shutil.which("uv")
    assert uv, "uv builds the wheel T7 reads"
    built = subprocess.run([uv, "build", "--wheel", "--out-dir", str(tmp_path), str(REPO_ROOT)],
                           capture_output=True, timeout=300, check=False)
    assert built.returncode == 0, built.stderr
    wheel = next(tmp_path.glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        metadata = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        lines = archive.read(metadata).decode("utf-8").splitlines()
    requires = [line.split(":", 1)[1] for line in lines if line.startswith("Requires-Dist:")]
    assert requires, "the wheel declares its dependencies"
    assert _named(requires) == []


# ---------------------------------------------------------------------------
# T8: evidence is private-clean (IL-R10).
# ---------------------------------------------------------------------------

def _private_hits(text: str, user: str) -> list[str]:
    roots = ["/" + "Users" + "/", "/" + "home" + "/", "-" + "Users" + "-"]
    hits = [root for root in roots if root in text]
    if re.search(r"(^|[/\\\-])" + re.escape(user) + r"([/\\\-]|$)", text, flags=re.MULTILINE):
        hits.append("username")
    if joined_hits(text, DOWNSTREAM_JOINED):
        hits.append("downstream")
    return hits


def test_t8_the_milestone_directory_is_private_clean():
    user = getpass.getuser()
    planted = f"see {'/' + 'Users' + '/'}{user}/scratch and -{user}-x"
    assert _private_hits(planted, user)
    listed = subprocess.run(["git", "ls-files", "--", str(MILESTONE)], cwd=REPO_ROOT,
                            capture_output=True, text=True, check=True).stdout.split()
    assert listed, "the milestone directory is tracked"
    offenders = {}
    for name in listed:
        hits = _private_hits((REPO_ROOT / name).read_text(encoding="utf-8", errors="replace"), user)
        if hits:
            offenders[name] = hits
    assert offenders == {}


# ---------------------------------------------------------------------------
# T11: the stand-in learner's join space (IK6 carried row).
# ---------------------------------------------------------------------------

def _stand_in():
    path = SRC / "examples" / "refunds" / "stand_in_learner.py"
    spec = importlib.util.spec_from_file_location("il1_stand_in_learner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_t11_the_stand_in_learner_proposes_a_join_that_imports(tmp_path):
    learner = _stand_in()
    work = _work(tmp_path)
    export = tmp_path / "export"
    result = run_main(["export", "ilp", str(work / CASES["model"]), "--labels",
                       str(work / "m.labels.json"), "--target", "neutral", "--out", str(export)])
    assert result.returncode == 0, result.stderr
    neutral, rows, integer, predicates = learner.load(export)
    ids = [example["id"] for example in neutral["examples"]]
    joins = [(text, clause, covers) for text, clause, covers in learner.candidates(rows, integer, predicates)
             if sum("atom" in literal for literal in clause["body"]) == 2]
    assert joins, "the orders model gives the stand-in learner a join candidate"
    text, clause, covers = next((j for j in joins if any(j[2](i) for i in ids)), joins[0])
    clauses = work / "t11.clauses.json"
    clauses.write_text(json.dumps({"schema_version": "gnd-ilp-clauses/1", "clauses": [clause]}))
    run = _bound_run(work, clauses, [[i for i in ids if covers(i)]], "neutral")
    out = tmp_path / "t11.json"
    imported = _import(work, clauses, run, out, "neutral")
    assert imported.returncode == 0, (text, imported.stderr)
