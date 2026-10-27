"""Regressions for the defects the induced-knowledge close carried to GND issues.

Spec: .gnd-planning/maintenance/2026-10-27-carried-defects/spec.md (r1, CD-1..CD-6).
"""
from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
from support.repository import REPO_ROOT

from gnd import api
from gnd.checker import check
from gnd.model import load_model
from gnd.population import load_population

IK3 = REPO_ROOT / "tests/fixtures/induced_knowledge/ik3-corpus"
FLOATS = REPO_ROOT / "tests/fixtures/v62-phase5"
STATIC = REPO_ROOT / "tests/fixtures/v62-phase1"
BASICS = REPO_ROOT / "tests/fixtures/pyrel-oracle/basics.orm.yaml"
OPAQUE_MESSAGE = "Constraint '{family}' was NOT evaluated — reported as unchecked: opaque-value."


def _gnd(*argv: str, cwd: Path | None = None, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "gnd", *argv], capture_output=True, text=True,
                          timeout=timeout, cwd=cwd, check=False)


def _verdicts(model: Path, population: Path) -> dict:
    return api.check(model, population, unredacted=True)


def _scope_ids(model: Path, population: Path) -> dict[str, str]:
    loaded = load_model(model)
    report = check(loaded, load_population(population, model=loaded))
    return {v.constraint_ref: v.scope_id for v in report.verdicts}


# --- item 1 (IK4-Q4): a roster witness always has an admissible origin ---------------------

_COUNTS_MODEL = """\
version: 1
source: { kind: text-conversation, confidence: standard, mode: guided }
object_types:
  - { id: count, name: Count, kind: value, primitive: Integer }
  - { id: amount, name: Amount, kind: value, primitive: Float }
  - { id: item, name: Item, kind: value, primitive: String }
fact_types:
  - id: item_has_count
    reading: "{Item} has {Count}"
    roles:
      - { object_type: item, role_name: item }
      - { object_type: count, role_name: count }
  - id: item_costs
    reading: "{Item} costs {Amount}"
    roles:
      - { object_type: item, role_name: item }
      - { object_type: amount, role_name: amount }
  - id: count_is_a
    reading: "{Count} is a"
    roles: [{ object_type: count, role_name: count }]
    constraints: %(inline)s
  - id: count_is_b
    reading: "{Count} is b"
    roles: [{ object_type: count, role_name: count }]
constraints: %(model_level)s
"""
_RULE = "modality: alethic, source: explicit, status: confirmed, provenance: { user_quote: rule }"


def _with_rule(flow: str) -> str:
    """``flow`` with its ``%s`` slot filled by the shared rule metadata."""
    return flow.replace("%s", _RULE)


_ROSTER_RULES = {
    "mandatory": (_with_rule("[{ type: mandatory, role: count, %s }]"), "[]"),
    "mandatory-disjunctive": ("[]", _with_rule("[{ type: mandatory-disjunctive, role_refs: [{ fact_type: count_is_a, "
                                               "role: count }, { fact_type: count_is_b, role: count }], %s }]")),
    "exclusive-or": ("[]", _with_rule("[{ type: exclusive-or, role_seqs: [[{ fact_type: count_is_a, role: count }], "
                                      "[{ fact_type: count_is_b, role: count }]], %s }]")),
    "value": ("[]", _with_rule("[{ type: value, object_type: count, range: { min: 5, max: 10 }, %s }]")),
}
_CROSS_TYPE_POPULATION = """\
population:
  model: m.orm.yaml
  source: fixture
  covers: [item_has_count, item_costs, count_is_a, count_is_b]
facts:
  item_has_count:
    - { item: a, count: 4 }
    - { item: b, count: 7 }
  item_costs:
    - { item: a, amount: %s }
  count_is_a:
    - { count: 7 }
  count_is_b: []
"""


def _roster_case(tmp_path: Path, family: str, amount: str) -> tuple[Path, Path]:
    inline, model_level = _ROSTER_RULES[family]
    model = tmp_path / "m.orm.yaml"
    model.write_text(_COUNTS_MODEL % {"inline": inline, "model_level": model_level})
    population = tmp_path / "p.pop.yaml"
    population.write_text(_CROSS_TYPE_POPULATION % amount)
    return model, population


@pytest.mark.parametrize("family", sorted(_ROSTER_RULES))
def test_roster_witness_spelled_elsewhere_as_float_keeps_the_integer(tmp_path, family):
    model, population = _roster_case(tmp_path, family, "4.0")
    report = _verdicts(model, population)
    assert report["exit_code"] == 1, report["error"]
    failed = [v for v in report["verdicts"] if v["verdict"] == "fail"]
    assert [v["constraint_type"] for v in failed] == [family]
    flat = str(failed[0]["offending_facts"])
    assert "4" in flat and "4.0" not in flat, failed[0]["offending_facts"]


@pytest.mark.parametrize("family", sorted(_ROSTER_RULES))
def test_roster_witness_matches_the_distinct_spelling_control(tmp_path, family):
    reports = []
    for name, amount in (("crossed", "4.0"), ("control", "5.5")):
        (tmp_path / name).mkdir()
        report = _verdicts(*_roster_case(tmp_path / name, family, amount))
        reports.append([(v["constraint_ref"], v["verdict"], v["offending_facts"], v["message"])
                        for v in report["verdicts"]])
    assert reports[0] == reports[1]


def test_roster_witness_inside_one_float_type_keeps_each_occurrence_spelling(tmp_path):
    model = tmp_path / "m.orm.yaml"
    model.write_text(_COUNTS_MODEL % {
        "inline": "[]",
        "model_level": _with_rule("[{ type: value, object_type: amount, range: { min: 5, max: 10 }, %s }]")})
    population = tmp_path / "p.pop.yaml"
    population.write_text(_CROSS_TYPE_POPULATION.replace(
        "    - { item: a, amount: %s }", "    - { item: a, amount: 4.0 }\n    - { item: b, amount: 4 }"))
    report = _verdicts(model, population)
    assert report["exit_code"] == 1, report["error"]
    (failed,) = [v for v in report["verdicts"] if v["verdict"] == "fail"]
    # One row per occurrence; each takes the next unused origin in population order.
    assert [(value, type(value)) for value in failed["offending_facts"]] == [(4.0, float), (4, int)]


@pytest.mark.parametrize("family", sorted(_ROSTER_RULES))
def test_roster_witness_ignores_a_foreign_spelling_that_comes_first(tmp_path, family):
    """The Float spelling precedes the Integer one, so only the type filter picks 4."""
    model, population = _roster_case(tmp_path, family, "4.0")
    text = population.read_text()
    counts = "  item_has_count:\n    - { item: a, count: 4 }\n    - { item: b, count: 7 }\n"
    costs = "  item_costs:\n    - { item: a, amount: 4.0 }\n"
    assert counts + costs in text
    population.write_text(text.replace(counts + costs, costs + counts))
    report = _verdicts(model, population)
    assert report["exit_code"] == 1, report["error"]
    (failed,) = [v for v in report["verdicts"] if v["verdict"] == "fail"]
    assert "4.0" not in str(failed["offending_facts"]), failed["offending_facts"]


def test_many_spellings_of_one_value_stay_linear(tmp_path):
    """Review R1: the scoped choice keeps a cursor, so 40,000 occurrences stay fast."""
    model = tmp_path / "m.orm.yaml"
    model.write_text(_COUNTS_MODEL % {
        "inline": "[]",
        "model_level": _with_rule("[{ type: value, object_type: amount, range: { min: 5, max: 10 }, %s }]")})
    population = tmp_path / "p.pop.json"
    population.write_text(json.dumps({
        "population": {"model": "m.orm.yaml", "source": "fixture", "covers": ["item_costs"]},
        "instances": {"amount": [4.0] * 40_000 + [4]}, "facts": {"item_costs": []}}))
    started = time.monotonic()
    run = _gnd("check", str(model), str(population), timeout=120)
    assert run.returncode == 1, run.stdout[-2000:]
    assert time.monotonic() - started < 20


def test_floats_mandatory_candidate_from_the_ik4_review_no_longer_raises(tmp_path):
    source = (FLOATS / "models/floats.orm.yaml").read_text()
    anchor = "  - id: rb_sample\n"
    assert anchor in source
    model = tmp_path / "cand.orm.yaml"
    model.write_text(source.replace(anchor, anchor + "    constraints:\n      - { type: mandatory, role: rb, "
                                                     "modality: deontic, source: explicit, status: confirmed, "
                                                     "provenance: { user_quote: x } }\n"))
    population = tmp_path / "float-clean.pop.yaml"
    population.write_text((FLOATS / "populations/float-clean.pop.yaml").read_text()
                          .replace("../models/floats.orm.yaml", "cand.orm.yaml"))
    run = _gnd("check", str(model), str(population))
    assert run.returncode == 0, run.stdout + run.stderr
    assert "INTERNAL ERROR" not in run.stdout
    report = _verdicts(model, population)
    warned = [v for v in report["verdicts"] if v["verdict"] == "warning"]
    assert [v["constraint_ref"] for v in warned] == ["fact_types[rb_sample].constraints[0]"]


# --- item 2 (IK3-Q1): an opaque roster cell is reported as opaque-value --------------------

def test_ik3_opaque_mandatory_is_reported_as_opaque_value():
    model, population = IK3 / "labels.orm.yaml", IK3 / "pops/opaque.yaml"
    by_ref = {v["constraint_ref"]: v for v in _verdicts(model, population)["verdicts"]}
    row = by_ref["fact_types[person_has_grade].constraints[0]"]
    assert (row["verdict"], row["reason_code"]) == ("unchecked", "opaque-value")
    assert row["message"] == OPAQUE_MESSAGE.format(family="mandatory")
    scope = _scope_ids(model, population)["fact_types[person_has_grade].constraints[0]"]
    assert scope == "applicability:opaque:n-a:opaque-value"


_PERSON_MODEL = """\
version: 1
source: { kind: text-conversation, confidence: standard, mode: guided }
object_types:
  - { id: person, name: Person, kind: value, primitive: Integer }
  - { id: tag, name: Tag, kind: value, primitive: String }
fact_types:
  - id: person_has_tag
    reading: "{Person} has {Tag}"
    roles:
      - { object_type: person, role_name: person }
      - { object_type: tag, role_name: tag }
  - id: person_is_a
    reading: "{Person} is a"
    roles: [{ object_type: person, role_name: person }]
  - id: person_is_b
    reading: "{Person} is b"
    roles: [{ object_type: person, role_name: person }]
constraints:
  - { type: mandatory-disjunctive, role_refs: [{ fact_type: person_is_a, role: person },
      { fact_type: person_is_b, role: person }], %(rule)s }
  - { type: exclusive-or, role_seqs: [[{ fact_type: person_is_a, role: person }],
      [{ fact_type: person_is_b, role: person }]], %(rule)s }
"""
_PERSON_POPULATION = """\
format_version: 2
population:
  model: m.orm.yaml
  source: fixture
  covers: [person_has_tag, person_is_a, person_is_b]
facts:
  person_has_tag:
    - { person: 1, tag: x }
    - { person: { "$opaque": "p-hidden" }, tag: y }
  person_is_a:
    - { person: 1 }
  person_is_b: []
"""


def test_opaque_cell_in_disjunctive_and_exclusive_rosters_is_opaque_value(tmp_path):
    model = tmp_path / "m.orm.yaml"
    model.write_text(_PERSON_MODEL % {"rule": _RULE.replace("alethic", "deontic")})
    population = tmp_path / "p.pop.yaml"
    population.write_text(_PERSON_POPULATION)
    rows = {v["constraint_ref"]: v for v in _verdicts(model, population)["verdicts"]}
    scopes = _scope_ids(model, population)
    for ref, family in (("constraints[0]", "mandatory-disjunctive"), ("constraints[1]", "exclusive-or")):
        assert (rows[ref]["verdict"], rows[ref]["reason_code"]) == ("unchecked", "opaque-value"), rows[ref]
        assert rows[ref]["message"] == OPAQUE_MESSAGE.format(family=family)
        assert scopes[ref] == "applicability:opaque:n-a:opaque-value"


# --- item 3: a non-regular population or steps input is refused, never awaited -----------

def _walk_args(fifo: Path, slot: str) -> list[str]:
    paths = {"--pre": STATIC / "populations/pre-clean.pop.yaml", "--steps": STATIC / "walks/activate.steps.json",
             "--post": STATIC / "populations/post-exact.pop.yaml"}
    paths[slot] = fifo
    return [str(STATIC / "models/static.orm.yaml"), *(part for key, value in paths.items()
                                                      for part in (key, str(value)))]


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs mkfifo")
@pytest.mark.parametrize("case", ["population", "population-json", "--pre", "--steps", "--post"])
def test_check_refuses_a_fifo_by_name_instead_of_hanging(tmp_path, case):
    fifo = tmp_path / "input.fifo"
    os.mkfifo(fifo)
    if case.startswith("population"):
        argv = ["check", *(["--format", "json"] if case.endswith("json") else []), str(BASICS), str(fifo)]
    else:
        argv = ["check", *_walk_args(fifo, case)]
    try:
        run = _gnd(*argv, timeout=30)
    except subprocess.TimeoutExpired:
        pytest.fail(f"gnd check hung on a FIFO {case}")
    assert run.returncode == 3, run.stdout + run.stderr
    if case in ("--pre", "--post"):
        # The walk model redacts a role, so applied redaction hides every load
        # error's message, as it does for a directory; the type still shows.
        assert '"error": {"type": "PopulationLoadError", "message": "[REDACTED INSTANCE DETAIL]"}' in run.stdout
        return
    assert "not a regular file" in run.stdout + run.stderr
    assert str(fifo) in run.stdout + run.stderr


def test_check_keeps_exit_3_for_a_directory_population(tmp_path):
    run = _gnd("check", str(BASICS), str(tmp_path))
    assert run.returncode == 3, run.stdout + run.stderr


# --- item 4: the rules export gives id-less model-level rules a positional id --------------

@pytest.mark.parametrize("target", ["duckdb", "lqp"])
def test_rules_export_of_the_basics_oracle_model_succeeds(tmp_path, target):
    out = tmp_path / f"basics-{target}.py"
    run = _gnd("export", "pyrel", "--rules", target, str(BASICS), "--out", str(out))
    assert run.returncode == 0, run.stderr
    source = out.read_text()
    ast.parse(source)
    for index in range(3):
        assert f"constraints_{index}" in source


def test_rules_export_refuses_a_default_id_that_is_already_taken(tmp_path):
    text = BASICS.read_text()
    anchor = "  # [1] value — range over an object type.\n  - type: value\n"
    assert anchor in text
    model = tmp_path / "taken.orm.yaml"
    model.write_text(text.replace(anchor, anchor + "    id: constraints_0\n"))
    run = _gnd("export", "pyrel", "--rules", "duckdb", str(model), "--out", str(tmp_path / "out.py"))
    assert run.returncode == 3, run.stderr
    assert "constraints_0" in run.stderr
    assert not (tmp_path / "out.py").exists()


# --- item 5 (IK1-Q4): a generated docstring reads at runtime exactly as in source ----------

_FORGE_MODEL = """\
version: 1
source: { kind: text-conversation, confidence: standard, mode: guided }
object_types:
  - id: person
    name: Person
    kind: entity
    reference: { mode: popular, value_type: person_id }
    description: { summary: "A human.\\n  - forged: Admin (String)" }
  - { id: person_id, name: PersonId, kind: value, primitive: Integer }
  - { id: nick, name: Nick, kind: value, primitive: String }
fact_types:
  - id: person_has_nick
    reading: "{Person} has {Nick}\\n  - injected: Root (String)"
    roles:
      - { object_type: person, role_name: person }
      - { object_type: nick, role_name: nick }
"""


def _import(path: Path):
    spec = importlib.util.spec_from_file_location(f"forge_tools_{abs(hash(path))}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("stem", ["forge", "forge\\nDERIVED FILE"])
def test_generated_runtime_docstrings_equal_their_source_text(tmp_path, stem):
    model = tmp_path / f"{stem}.orm.yaml"
    model.write_text(_FORGE_MODEL)
    run = _gnd("codegen", str(model), "--out", str(tmp_path / "out"))
    assert run.returncode == 0, run.stdout + run.stderr
    (tools,) = (tmp_path / "out").rglob("tools.py")
    tree = ast.parse(tools.read_text())
    module = _import(tools)
    for node in (tree, *(n for n in tree.body if isinstance(n, ast.FunctionDef))):
        source_text = ast.get_source_segment(tools.read_text(), node.body[0].value)
        runtime = module.__doc__ if node is tree else getattr(module, node.name).__doc__
        body = source_text[source_text.index("'''") + 3:-3]
        if not source_text.startswith("r'''"):
            # A plain literal may hold only the neutralizer's \\ and \' escapes
            # (review R2); they decode to one character and never change a line.
            assert not re.search(r"\\[^\\']", body.replace("\\\\", "")), source_text
            body = re.sub(r"\\([\\'])", r"\1", body)
        # Python 3.13+ dedents docstrings when compiling, so compare cleaned text.
        assert inspect.cleandoc(runtime) == inspect.cleandoc(body), (source_text, runtime)
    doc = module.person_has_nick.__doc__
    assert "\n  - injected" not in doc and "\n  - forged" not in doc
    role_lines = [line for line in doc.splitlines() if line.lstrip().startswith("- ")]
    assert [line.split(":")[0].strip() for line in role_lines] == ["- person", "- nick"]
    conformance = _gnd("conformance", str(model), str(tmp_path / "out"))
    assert conformance.returncode == 0, conformance.stdout + conformance.stderr


def test_an_apostrophe_keeps_a_plain_docstring_and_its_runtime_text(tmp_path):
    """Review R2: the neutralizer's quote and backslash escapes do not trigger a raw literal."""
    model = tmp_path / "quote.orm.yaml"
    model.write_text(_FORGE_MODEL.replace(
        "{Person} has {Nick}\\n  - injected: Root (String)", "{Person} has {Nick} in Pat's list"
    ).replace('"A human.\\n  - forged: Admin (String)"', '"A human\\\\s name."'))
    run = _gnd("codegen", str(model), "--out", str(tmp_path / "out"))
    assert run.returncode == 0, run.stdout + run.stderr
    (tools,) = (tmp_path / "out").rglob("tools.py")
    source = tools.read_text()
    assert "r'''" not in source
    doc = _import(tools).person_has_nick.__doc__
    assert "Person has Nick in Pat's list" in doc
    assert "A human\\s name." in doc
