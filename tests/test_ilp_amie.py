"""IL4: the AMIE-style miner -- the typed triple export and the mined-rules import.

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL4-spec.md (r1, approved
2026-10-28, §13). Under IL4-D12 the reader's and the mapping's cases are a corpus
written before the code: tests/fixtures/ilp_learners/il4/rules.json, stories inline.
The counts are checked against a brute-force oracle written here (T4).
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import random
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
IL4 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il4"
MODEL, POPULATION = IL4 / "model.orm.yaml", IL4 / "population.yaml"
CORPUS = json.loads((IL4 / "rules.json").read_text(encoding="utf-8"))
EVIDENCE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence" / "IL4"
REQUESTED_AT = "2026-01-01T00:00:00Z"


def _ids(case: dict[str, Any]) -> str:
    return case["id"]


def _export(tmp_path: Path, model: Path = MODEL, population: Path = POPULATION,
            name: str = "export") -> Path:
    out = tmp_path / name
    result = run_main(["export", "ilp", str(model), "--population", str(population),
                       "--target", "amie", "--out", str(out)])
    assert result.returncode == 0, result.stderr
    return out


# ---------------------------------------------------------------------------
# T1: the export is golden and the same under two hash seeds.
# ---------------------------------------------------------------------------

EXPORTS = {"staffing": (MODEL, POPULATION),
           "north": (REFUNDS / "model.orm.yaml", REFUNDS / "batches" / "north.yaml")}


@pytest.mark.parametrize("name", sorted(EXPORTS))
def test_t1_the_export_is_golden_under_two_hash_seeds(tmp_path, name):
    model, population = EXPORTS[name]
    trees = []
    for seed in ("0", "1"):
        out = tmp_path / f"seed{seed}"
        completed = subprocess.run(
            [sys.executable, "-m", "gnd", "export", "ilp", str(model), "--population", str(population),
             "--target", "amie", "--out", str(out)],
            cwd=REPO_ROOT, env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True,
            timeout=120, check=False)
        assert completed.returncode == 0, completed.stderr
        trees.append({path.relative_to(out).as_posix(): path.read_bytes()
                      for path in sorted(out.rglob("*")) if path.is_file()})
    assert trees[0] == trees[1]
    expected = IL4 / "expected" / name
    assert sorted(trees[0]) == ["amie/facts.tsv", "amie/relations.json", "export.json"]
    for path, data in trees[0].items():
        assert data == (expected / path.split("/")[-1]).read_bytes(), path


def test_t1_skipped_lists_every_other_fact_type(tmp_path):
    out = _export(tmp_path)
    index = json.loads((out / "amie" / "relations.json").read_text(encoding="utf-8"))
    assert index["skipped"] == [{"fact_type": "is_contractor", "reason": "arity"},
                                {"fact_type": "mentors", "reason": "not-covered"}]
    assert index["population_sha256"] == hashlib.sha256(POPULATION.read_bytes()).hexdigest()
    lines = (out / "amie" / "facts.tsv").read_text(encoding="utf-8").splitlines()
    assert lines == sorted(set(lines)) and len(lines) == 65
    assert all(re.fullmatch(r"(staff|team):\S+\tf_[a-z_]+\t(team|site):\S+", line) for line in lines)


def test_t1_the_export_validates_against_the_export_schema(tmp_path):
    from jsonschema import Draft202012Validator

    out = _export(tmp_path)
    schema = json.loads((SRC / "ilp.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(json.loads((out / "export.json").read_text(encoding="utf-8")))


def test_t1_a_value_it_cannot_spell_is_refused(tmp_path):
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    assert ilp_amie.spell("site", "a\tb\\c\nd", where="w") == "site:a\\tb\\\\c\\nd"
    assert ilp_amie.spell("flag", True, where="w") == "flag:true"
    with pytest.raises(IlpError, match="^unrepresentable:"):
        ilp_amie.spell("site", "a\x07b", where="w")


def test_t1_a_population_without_binary_relations_is_refused(tmp_path):
    population = tmp_path / "population.yaml"
    text = POPULATION.read_text(encoding="utf-8")
    population.write_text(text.replace("covers: [works_in, team_site, based_at, parks_at, is_contractor]",
                                       "covers: [is_contractor]"), encoding="utf-8")
    shutil.copy(MODEL, tmp_path / "model.orm.yaml")
    result = run_main(["export", "ilp", str(tmp_path / "model.orm.yaml"), "--population", str(population),
                       "--target", "amie", "--out", str(tmp_path / "out")])
    assert result.returncode == 3
    assert result.stderr.decode().startswith("no-relations:")
    assert not (tmp_path / "out").exists()


# ---------------------------------------------------------------------------
# T2: the registry and its pins.
# ---------------------------------------------------------------------------

def test_t2_the_registry():
    from gnd.export import ilp_amie, ilp_learners

    assert ilp_learners.EXPORT_TARGETS == ("popper", "neutral", "ilasp", "rules", "amie")
    assert ilp_learners.IMPORT_TARGETS == ("popper", "neutral", "ilasp", "llm", "rules")
    assert ilp_learners.MINED_TARGETS == ("amie",)
    entry = ilp_learners.learner("amie")
    assert (entry.learner, entry.method, entry.contract, entry.adapter_version) == (
        "amie", "ilp-amie", "unlabelled-horn", ilp_amie.ADAPTER_VERSION)
    assert entry.render is ilp_amie.render and entry.parse is ilp_amie.parse_rules
    export = (SRC / "commands" / "export.py").read_text(encoding="utf-8")
    assert 'choices=("popper", "neutral", "ilasp", "rules", "amie")' in export
    checking = (SRC / "commands" / "checking.py").read_text(encoding="utf-8")
    assert 'choices=("amie",)' in checking
    schema = json.loads((SRC / "ilp.schema.json").read_text(encoding="utf-8"))
    assert tuple(schema["$defs"]["export"]["properties"]["target"]["enum"]) == ilp_learners.EXPORT_TARGETS
    mined = json.loads((SRC / "mined-import.schema.json").read_text(encoding="utf-8"))
    assert tuple(mined["$defs"]["report"]["properties"]["target"]["enum"]) == ilp_learners.MINED_TARGETS


# ---------------------------------------------------------------------------
# T3, T10: the reader corpus and its totality.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CORPUS["parse"], ids=_ids)
def test_t3_the_reader(case):
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    if "rules" in case["expect"]:
        assert ilp_amie.parse_rules(case["text"]) == case["expect"]["rules"]
    else:
        with pytest.raises(IlpError) as raised:
            ilp_amie.parse_rules(case["text"])
        assert raised.value.code == 3
        assert str(raised.value).startswith(case["expect"]["refusal"] + ":")


def _line(rule: str = "?a  r  ?b   => ?a  s  ?b", support: str = "2") -> str:
    return f"{rule}\t1.000000\t-2.000000\t1.000000\t{support}\t-1\t2\t-1"


def _distinct(count: int) -> str:
    return "".join(_line(f"?a  r{k}  ?b   => ?a  s  ?b") + "\n" for k in range(count))


@pytest.mark.parametrize(("text", "accepted"), [
    pytest.param(_distinct(256), True, id="256-rules"),
    pytest.param(_distinct(257), False, id="257-rules"),
    pytest.param(_line(support="9" * 18) + "\n", True, id="18-digits"),
    pytest.param(_line(support="9" * 19) + "\n", False, id="19-digits"),
    pytest.param(_line("?a  r  ?b  ?b  r  ?c  ?c  r  ?d   => ?a  s  ?d") + "\n", True, id="4-atoms"),
    pytest.param("x" * (1024 * 1024 + 1), False, id="over-1-mib"),
    pytest.param("\x00\t" * 4, False, id="nul"),
])
def test_t10_the_reader_is_total_and_its_caps_hold_at_the_bound(text, accepted):
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    if accepted:
        assert ilp_amie.parse_rules(text)
    else:
        with pytest.raises(IlpError, match="^unparsable:"):
            ilp_amie.parse_rules(text)


def test_t10_random_text_never_raises_anything_else():
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    generator = random.Random(4)
    alphabet = ["?a", "?b", "r", "=>", "  ", "\t", "\n", "1", "-1", "0.5", "?", "é", "x:y"]
    for _ in range(2000):
        text = "".join(generator.choice(alphabet) for _ in range(generator.randint(0, 40)))
        try:
            ilp_amie.parse_rules(text)
        except IlpError as error:
            assert str(error).startswith("unparsable:")


# ---------------------------------------------------------------------------
# T3, T5, T6, T6b, T8: the import over the staffing fixture.
# ---------------------------------------------------------------------------

def _population(tmp_path: Path, drop: list[str]) -> Path:
    """A copy of the fixture population with ``drop``'s facts removed, covers kept."""
    from ruamel.yaml import YAML

    yaml = YAML(typ="safe")
    document = yaml.load(POPULATION.read_text(encoding="utf-8"))
    for name in drop:
        document["facts"][name] = []
    path = tmp_path / "population.yaml"
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(document, handle)
    return path


def _import(tmp_path: Path, lines: list[str], *, drop: list[str] = (), learner: str = "amie",
            run: dict[str, Any] | None = None, fmt: str = "json") -> tuple[Any, Path]:
    work = tmp_path / "import"
    work.mkdir()
    shutil.copy(MODEL, work / "model.orm.yaml")
    population = _population(work, list(drop)) if drop else shutil.copy(POPULATION, work / "population.yaml")
    rules = work / "rules.txt"
    rules.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    record = run or {"schema_version": "gnd-mined-run/1",
                     "learner": {"name": learner, "version": "4.0.0"},
                     "rules_sha256": hashlib.sha256(rules.read_bytes()).hexdigest(),
                     "population_sha256": hashlib.sha256(Path(population).read_bytes()).hexdigest()}
    (work / "reported.json").write_text(json.dumps(record), encoding="utf-8")
    out = work / "proposal.json"
    result = run_main(["import", "mined-rules", str(work / "model.orm.yaml"), str(rules),
                       "--population", str(population), "--reported", str(work / "reported.json"),
                       "--target", "amie", "--out", str(out), "--actor", "il4-test",
                       "--requested-at", REQUESTED_AT, "--format", fmt])
    return result, out


def _constraints(out: Path) -> list[dict[str, Any]]:
    return [op["after"] for op in json.loads(out.read_text(encoding="utf-8"))["operations"]]


@pytest.mark.parametrize("case", CORPUS["import"], ids=_ids)
def test_t3_t5_the_import(tmp_path, case):
    result, out = _import(tmp_path, case["rules"], drop=case.get("drop", []))
    expect = case["expect"]
    assert result.returncode == expect["exit"], result.stderr
    if expect["exit"] != 0:
        message = result.stderr.decode().strip()
        assert re.match(rf"rule \d+: {re.escape(expect['refusal'])}:", message), message
        assert not out.exists()
        return
    constraints = _constraints(out)
    core = [{key: c[key] for key in ("type", "antecedent", "consequent")} for c in constraints]
    assert core == expect["constraints"]
    support = [[c["provenance"]["induction"]["support"][k] for k in ("numerator", "denominator")]
               for c in constraints]
    assert support == expect["support"]
    report = json.loads(result.stdout)
    if "body_size_agrees" in expect:
        assert [row["body_size_agrees"] for row in report["rules"]] == expect["body_size_agrees"]


def test_t6_an_admitted_rule_previews_with_discovers_provenance(tmp_path):
    case = next(c for c in CORPUS["import"] if c["id"] == "a2")
    result, out = _import(tmp_path, case["rules"])
    assert result.returncode == 0, result.stderr
    population_sha = hashlib.sha256(POPULATION.read_bytes()).hexdigest()
    for constraint in _constraints(out):
        assert (constraint["source"], constraint["status"], constraint["modality"]) == (
            "induced", "proposed", "deontic")
        induction = constraint["provenance"]["induction"]
        assert induction["inducer"] == {"name": "amie", "version": "4.0.0"}
        assert induction["method"] == "ilp-amie"
        assert induction["manifest_sha256"] == population_sha
        assert induction["counterexamples"] == []
        assert induction["evidence"][0] == {"ref": "population.yaml", "sha256": population_sha}
        assert all(re.fullmatch(r"ft\d+#\d+", example) for example in induction["examples"])
        assert len(induction["examples"]) == induction["support"]["numerator"]
    first, second = _constraints(out)
    # based_at is the model's third fact type (ft2); team_site the second (ft1).
    assert first["provenance"]["induction"]["examples"][:2] == ["ft2#0", "ft2#1"]
    assert second["provenance"]["induction"]["examples"] == [f"ft1#{k}" for k in range(5)]
    work = tmp_path / "import"
    preview = run_main(["evolve", "preview", str(work / "model.orm.yaml"), str(out), "--workspace",
                        str(work), "--records", str(work / "records"), "--out", str(work / "preview.json")])
    assert preview.returncode == 0, preview.stdout + preview.stderr


def test_t6b_all_or_nothing(tmp_path):
    case = next(c for c in CORPUS["import"] if c["id"] == "c4")
    result, out = _import(tmp_path, case["rules"])
    assert result.returncode == 3 and not out.exists()
    assert result.stderr.decode().startswith("rule 1: does-not-hold: 19 of 20")


def test_t8_the_report_validates(tmp_path):
    from jsonschema import Draft202012Validator

    case = next(c for c in CORPUS["import"] if c["id"] == "a2")
    result, _ = _import(tmp_path, case["rules"])
    report = json.loads(result.stdout)
    schema = json.loads((SRC / "mined-import.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(report)
    assert report["command"] == "import mined-rules" and report["schema_version"] == "gnd-mined-import/1"
    assert [row["confidence"] for row in report["rules"]] == [
        {"formula": "std-confidence-head-pairs", "value": 1.0}] * 2
    assert [row["body_size_agrees"] for row in report["rules"]] == [None, None]


def test_t5_the_run_record_binds_the_rules_the_population_and_the_learner(tmp_path):
    case = next(c for c in CORPUS["import"] if c["id"] == "a1")
    for name, change in (("learner-mismatch", {"learner": {"name": "popper", "version": "1"}}),
                         ("rules-mismatch", {"rules_sha256": "0" * 64}),
                         ("population-mismatch", {"population_sha256": "0" * 64})):
        work = tmp_path / name
        work.mkdir()
        good, _ = _import(work, case["rules"])
        record = json.loads((work / "import" / "reported.json").read_text(encoding="utf-8"))
        shutil.rmtree(work / "import")
        result, out = _import(work, case["rules"], run={**record, **change})
        assert good.returncode == 0
        assert result.returncode == 3 and not out.exists()
        assert result.stderr.decode().startswith(f"{name}:"), result.stderr


def test_t5_the_join_bound_refuses_before_it_runs(tmp_path, monkeypatch):
    from gnd.export import ilp_amie

    case = next(c for c in CORPUS["import"] if c["id"] == "a1")
    monkeypatch.setattr(ilp_amie, "MAX_JOIN_ROWS", 20 * 5 - 1)
    result, out = _import(tmp_path, case["rules"])
    assert result.returncode == 3 and not out.exists()
    assert result.stderr.decode().startswith("rule 0: too-large:")
    monkeypatch.setattr(ilp_amie, "MAX_JOIN_ROWS", 20 * 5)
    shutil.rmtree(tmp_path / "import")
    assert _import(tmp_path, case["rules"])[0].returncode == 0


def test_t10_non_utf8_and_oversized_rules_are_refused_by_the_import(tmp_path):
    work = tmp_path / "import"
    result, _ = _import(tmp_path, [])
    assert result.returncode == 3 and result.stderr.decode().startswith("unparsable: no rule")
    rules = work / "rules.txt"
    rules.write_bytes(b"\xff\n")
    shutil.rmtree(work / "records", ignore_errors=True)
    again = run_main(["import", "mined-rules", str(work / "model.orm.yaml"), str(rules), "--population",
                      str(work / "population.yaml"), "--reported", str(work / "reported.json"),
                      "--target", "amie", "--out", str(work / "p2.json")])
    assert again.returncode == 3 and again.stderr.decode().startswith("unparsable: the rules are not UTF-8")
    rules.write_bytes(b"x" * (1024 * 1024 + 1))
    big = run_main(["import", "mined-rules", str(work / "model.orm.yaml"), str(rules), "--population",
                    str(work / "population.yaml"), "--reported", str(work / "reported.json"),
                    "--target", "amie", "--out", str(work / "p3.json")])
    assert big.returncode == 3 and "exceeds the 1048576-byte cap" in big.stderr.decode()


# ---------------------------------------------------------------------------
# T4: the counts equal a brute-force oracle.
# ---------------------------------------------------------------------------

def oracle(body: list[tuple[str, str, str]], head: tuple[str, str, str],
           facts: dict[str, set[tuple[str, str]]]) -> tuple[int, int]:
    """Every assignment of the rule's variables over the active domain (spec §6)."""
    variables = sorted({term for atom in [*body, head] for term in (atom[0], atom[2])})
    domain = sorted({value for rows in facts.values() for pair in rows for value in pair})
    reached, held = set(), set()
    for values in itertools.product(domain, repeat=len(variables)):
        binding = dict(zip(variables, values, strict=True))
        if all((binding[s], binding[o]) in facts[r] for s, r, o in body):
            pair = (binding[head[0]], binding[head[2]])
            reached.add(pair)
            if pair in facts[head[1]]:
                held.add(pair)
    return len(held), len(reached)


def _mined(body, head):
    from gnd.export.ilp_amie import MinedRule

    return MinedRule({}, tuple(body), head)


def test_t4_the_fixture_counts_equal_the_oracle(tmp_path):
    from gnd.export import ilp_amie
    from gnd.model import load_model
    from gnd.population import load_population

    model = load_model(MODEL)
    population = load_population(POPULATION, model=model)
    relations, _, _ = ilp_amie.relation_table(model, list(population.covers))
    facts = ilp_amie.pairs(relations, population)
    sets = {name: set(rows) for name, rows in facts.items()}
    rules = [([("?a", "f_works_in", "?b"), ("?b", "f_team_site", "?c")], ("?a", "f_based_at", "?c"), (20, 20)),
             ([("?a", "f_works_in", "?b"), ("?b", "f_team_site", "?c")], ("?a", "f_parks_at", "?c"), (19, 20)),
             ([("?a", "f_works_in", "?b"), ("?a", "f_based_at", "?c")], ("?b", "f_team_site", "?c"), (5, 5)),
             ([("?a", "f_parks_at", "?b")], ("?a", "f_based_at", "?b"), (19, 20)),
             ([("?a", "f_based_at", "?b"), ("?c", "f_based_at", "?b")], ("?a", "f_parks_at", "?b"), (19, 20))]
    for body, head, expected in rules:
        counted = ilp_amie.count(_mined(body, head), facts, 0)
        assert (counted.numerator, counted.denominator) == oracle(body, head, sets) == expected


def test_t4_random_populations_count_as_the_oracle():
    from gnd.export import ilp_amie

    generator = random.Random(44)
    names = ["p", "q", "r"]
    variables = ["?a", "?b", "?c", "?d"]
    for _ in range(300):
        facts = {name: [(f"e:{generator.randint(0, 4)}", f"e:{generator.randint(0, 4)}")
                        for _ in range(generator.randint(0, 7))] for name in names}
        sets = {name: set(rows) for name, rows in facts.items()}
        size = generator.randint(1, 3)
        body = [(generator.choice(variables[:size + 1]), generator.choice(names),
                 generator.choice(variables[:size + 1])) for _ in range(size)]
        terms = sorted({t for s, _, o in body for t in (s, o)})
        head = (generator.choice(terms), generator.choice(names), generator.choice(terms))
        counted = ilp_amie.count(_mined(body, head), facts, 0)
        assert (counted.numerator, counted.denominator) == oracle(body, head, sets), (body, head, facts)


# ---------------------------------------------------------------------------
# T7: the post-parse checks (IL4-C5).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("argv", "message"), [
    (["--target", "amie"], "the following arguments are required: --population"),
    (["--target", "amie", "--population", "p.yaml", "--labels", "l.json"],
     "argument --labels: not allowed with --target amie"),
    (["--target", "popper"], "the following arguments are required: --labels"),
    (["--target", "neutral"], "the following arguments are required: --labels"),
    (["--target", "rules", "--labels", "l.json", "--population", "p.yaml"],
     "argument --population: not allowed with --target rules"),
])
def test_t7_the_target_decides_which_input_is_required(tmp_path, argv, message):
    result = run_main(["export", "ilp", str(MODEL), *argv, "--out", str(tmp_path / "out")])
    assert result.returncode == 64
    assert result.stderr.decode().strip().endswith(f"gnd export ilp: error: {message}")
    assert not (tmp_path / "out").exists()


# ---------------------------------------------------------------------------
# T13: the reference section matches the code.
# ---------------------------------------------------------------------------

def test_t13_the_reference_section_matches_the_code():
    from gnd.export import ilp_amie, ilp_service

    doc = (REPO_ROOT / "docs" / "reference" / "ilp-bridge.md").read_text(encoding="utf-8")
    section = doc.split("\n## AMIE-style miner\n", 1)[1].split("\n## ", 1)[0]
    names = (*ilp_amie.EXPORT_REFUSALS, *ilp_service.MINED_INPUT_REFUSALS, *ilp_amie.MAPPING_REFUSALS,
             *ilp_amie.COUNT_REFUSALS, "unparsable")
    for name in names:
        assert f"`{name}`" in section, name
    order = [section.index(f"`{name}`") for name in ilp_amie.MAPPING_REFUSALS]
    assert order == sorted(order), "the mapping table lists the refusals in check order"
    for bound in ("MAX_RULES", "MAX_ATOMS", "MAX_DIGITS", "MAX_JOIN_ROWS"):
        assert f"{getattr(ilp_amie, bound):,}" in section, bound
    assert f"`{ilp_amie.FORMULA}`" in section
    documented = set(re.findall(r"refused `([a-z-]+)`", section))
    assert documented <= set(names)


# ---------------------------------------------------------------------------
# T9: the run of record replays from its committed bytes.
# ---------------------------------------------------------------------------

LIVE_ROOT = EVIDENCE / "live"
#: Invocation 1 is the run of record.
INVOCATIONS = (1,)
TERMINATIONS = {"rendering-rejected", "completed", "learner-timeout", "wall-clock-kill", "output-limit"}
REQUIRED = {"invocation", "run_of_record", "termination", "import", "export_sha256", "population_sha256",
            "adapter_version", "learner", "jvm", "process", "limits", "argv", "import_args", "numbers",
            "reproducibility", "licence"}


def _script():
    spec = importlib.util.spec_from_file_location("il4_run_amie", EVIDENCE / "run_amie.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("invocation", INVOCATIONS)
def test_t9_the_recorded_run_replays(tmp_path, invocation):
    from gnd import input_policy
    from gnd.export import ilp_amie

    live = LIVE_ROOT / f"invocation-{invocation}"
    outcome = input_policy.loads((live / "outcome.json").read_bytes())
    assert REQUIRED <= set(outcome)
    assert outcome["invocation"] == invocation and outcome["run_of_record"] is (invocation == 1)
    assert outcome["termination"] in TERMINATIONS
    assert outcome["reproducibility"] == "single run, reproducibility not measured"
    assert outcome["adapter_version"] == ilp_amie.ADAPTER_VERSION
    script = _script()
    process = outcome["process"]
    assert outcome["termination"] == script.termination(process)
    assert json.loads((live / "invocation.json").read_text(encoding="utf-8")) == process
    stderr = (live / "raw-stderr.txt").read_text(encoding="utf-8")
    assert len(stderr.encode("utf-8")) == process["stderr_observed_bytes"]
    assert outcome["limits"] == script.LIMITS.model_dump()
    assert outcome["argv"] == script.RECORDED_ARGV
    assert outcome["import_args"] == list(script.IMPORT_ARGS)
    assert outcome["licence"] == script.LICENCE
    assert outcome["population_sha256"] == hashlib.sha256(POPULATION.read_bytes()).hexdigest()

    export = _export(tmp_path)
    assert hashlib.sha256((export / "export.json").read_bytes()).hexdigest() == outcome["export_sha256"]
    assert (export / "amie" / "facts.tsv").read_bytes() == (live / "facts.tsv").read_bytes()

    stdout = (live / "raw-stdout.txt").read_text(encoding="utf-8")
    assert len(stdout.encode("utf-8")) == process["stdout_observed_bytes"]
    # Review 7: AMIE prints no version, so the learner is the verified asset's (IL4-D2 (o)),
    # and the run record the import read names the same one.
    assert outcome["learner"] == script.LEARNER == script.learner(stdout)
    if (live / "reported.json").exists():
        assert json.loads((live / "reported.json").read_text(encoding="utf-8"))["learner"] == script.LEARNER
    rules = script.read_rules(stdout, outcome["termination"])
    if not rules:
        assert outcome["import"] == "none" and not (live / "rules.txt").exists()
        return
    assert rules == (live / "rules.txt").read_text(encoding="utf-8")
    imports = tmp_path / "import"
    imports.mkdir()
    for name in ("model.orm.yaml", "population.yaml"):
        shutil.copy(IL4 / name, imports / name)
    for name in ("rules.txt", "reported.json"):
        shutil.copy(live / name, imports / name)
    previous = os.getcwd()
    os.chdir(imports)
    try:
        replayed = run_main(list(outcome["import_args"]))
    finally:
        os.chdir(previous)
    assert replayed.returncode == outcome["import_exit"]
    if replayed.returncode == 0:
        assert outcome["import"] == "admitted"
        assert (imports / "proposal.json").read_bytes() == (live / "proposal.json").read_bytes()
        assert replayed.stdout.decode() == (live / "import-report.json").read_text(encoding="utf-8")
    else:
        refusal = replayed.stderr.decode().strip()
        assert refusal == (live / "import-stderr.txt").read_text(encoding="utf-8").strip()
        assert outcome["import"] == script.import_outcome(refusal)


# ---------------------------------------------------------------------------
# T-live: the scratch AMIE over the committed facts gives the committed rules.
# ---------------------------------------------------------------------------

@pytest.mark.live
def test_live_amie_mines_the_committed_rules(tmp_path):
    """Live (spec T-live): AMIE over the committed facts.tsv prints the committed rules with
    the same figures. AMIE prints them in its threads' order and names variables run to run
    (IL4-F10: ?e in one run, ?f in the next), so rules compare up to renaming and body
    order. GND_IL4_JAR names the scratch jar."""
    jar = os.environ.get("GND_IL4_JAR")
    if not jar:
        pytest.skip("GND_IL4_JAR is not set")
    script = _script()
    live = LIVE_ROOT / "invocation-1"
    shutil.copy(live / "facts.tsv", tmp_path / "facts.tsv")
    result = subprocess.run([*script.java_argv(Path(jar)), "facts.tsv"], cwd=tmp_path, check=True,
                            capture_output=True, text=True, timeout=600,
                            env=script.java_environment(tmp_path))
    committed = (live / "raw-stdout.txt").read_text(encoding="utf-8")
    assert sorted(_canonical(result.stdout)) == sorted(_canonical(committed))
    assert len(_canonical(committed)) == len((live / "rules.txt").read_text(encoding="utf-8").splitlines())


def _canonical(stdout: str) -> list[tuple[Any, ...]]:
    """Each printed rule up to variable renaming and body order, with its figures."""
    from gnd.export import ilp_amie

    out = []
    for rule in ilp_amie.parse_rules(ilp_amie.extract_rules(stdout)):
        out.append((ilp_amie.canonical(rule["body"], rule["head"]), rule["support"], rule["body_size"],
                    tuple(sorted(rule["figures"].items()))))
    return out


# ---------------------------------------------------------------------------
# IL4-F9: a mined-rules refusal is named by the shared outcome mapping.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("message", "name"), [
    ("rule 0: does-not-hold: 19 of 20 head pairs hold", "does-not-hold"),
    ("rule 12: type-confused-join: variable ?b joins team and site", "type-confused-join"),
    ("clause 1: recursion: the head predicate is in the body", "recursion"),
    ("learner-mismatch: a amie import needs a amie run record", "learner-mismatch"),
])
def test_f9_the_refusal_name_reads_a_rule_prefix(message, name):
    from gnd.export.ilp import refusal_name

    assert refusal_name(message) == name
    assert _script().import_outcome(message) == f"refused:{name}"


# ---------------------------------------------------------------------------
# Step 4 regressions (notes/phase-IL4-agent-review.md), each red before its fix.
# ---------------------------------------------------------------------------

GOOD = "?a  f_works_in  ?b  ?b  f_team_site  ?c   => ?a  f_based_at  ?c"


def test_r1_a_disconnected_body_is_refused_by_name(tmp_path):
    """Review 1: a holding rule whose body falls apart reached the exit-70 checker disagreement."""
    rule = "?a  f_works_in  ?f  ?f  f_team_site  ?b  ?x  f_parks_at  ?y   => ?a  f_based_at  ?b"
    result, out = _import(tmp_path, [_line(rule, "20")])
    assert result.returncode == 3 and not out.exists(), result.stderr
    assert result.stderr.decode().startswith("rule 0: disconnected-body:")


def test_r1_a_connected_body_with_a_lone_variable_is_still_admitted(tmp_path):
    rule = "?a  f_works_in  ?b  ?b  f_team_site  ?c  ?a  f_parks_at  ?y   => ?a  f_based_at  ?c"
    result, _ = _import(tmp_path, [_line(rule, "20")])
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("second", [
    pytest.param("?c  f_works_in  ?d  ?d  f_team_site  ?e   => ?c  f_based_at  ?e", id="renamed"),
    pytest.param("?b  f_team_site  ?c  ?a  f_works_in  ?b   => ?a  f_based_at  ?c", id="permuted"),
])
def test_r3_a_rule_printed_twice_up_to_renaming_is_refused(second):
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError, match="^unparsable: line 2: the rule is printed twice"):
        ilp_amie.parse_rules(_line(GOOD, "20") + "\n" + _line(second, "20") + "\n")


@pytest.mark.parametrize("value", ["a b", "a\u200bb", "a\x07b"])
def test_r5_the_refusal_names_what_it_refuses(value):
    from gnd.export import ilp_amie
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError, match="^unrepresentable: x holds a non-printable character"):
        ilp_amie.spell("t", value, where="x")


def test_r7_a_body_size_that_agrees_is_recorded_true(tmp_path):
    result, _ = _import(tmp_path, [f"{GOOD}\t1.000000\t1.000000\t1.000000\t20\t20\t20\t-1"])
    assert result.returncode == 0, result.stderr
    assert [row["body_size_agrees"] for row in json.loads(result.stdout)["rules"]] == [True]
