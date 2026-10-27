"""IL2: the ILASP adapter -- task.las rendering and the closed ASP hypothesis reader.

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL2-spec.md (r1, approved
2026-10-27, §13). Under IL2-D11 the reader's cases are a corpus written before
the code: tests/fixtures/ilp_learners/il2/hypotheses.json, stories inline.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main
from test_ilp_bridge import CASES, _work

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "gnd"
REFUNDS = SRC / "examples" / "refunds"
IL2 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il2"
CORPUS = json.loads((IL2 / "hypotheses.json").read_text(encoding="utf-8"))
#: The weeks the IL1 invocation-3 rule covers (amount > 500), as GND computed them.
COVERED = ["harbor", "market", "airport", "station"]


def _ids(case: dict[str, Any]) -> str:
    return case["id"]


def _parse(text: str) -> dict[str, Any]:
    from gnd.export.ilp_asp import parse_hypothesis

    return parse_hypothesis(text)


def _refused(text: str) -> str:
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError) as raised:
        _parse(text)
    assert raised.value.code == 3
    return str(raised.value)


# ---------------------------------------------------------------------------
# T3, T5, T4, T6: the reader over the corpus.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CORPUS["accept"], ids=_ids)
def test_t3_the_reader_maps_a_hypothesis_to_the_clause_form(case):
    assert _parse(case["text"]) == {"schema_version": "gnd-ilp-clauses/1", "clauses": case["clauses"]}


def _constants(document: dict[str, Any]) -> list[Any]:
    return [term["const"] for clause in document["clauses"] for literal in clause["body"]
            for term in literal.get("atom", {}).get("args", []) if "const" in term]


@pytest.mark.parametrize("case", CORPUS["constants"], ids=_ids)
def test_t5_the_constants_table(case):
    constants = _constants(_parse(case["text"]))
    assert constants == case["constants"]
    assert [type(c) for c in constants] == [type(c) for c in case["constants"]]


@pytest.mark.parametrize("case", CORPUS["refuse"], ids=_ids)
def test_t4_each_construct_is_refused_by_name(case):
    message = _refused(case["text"])
    assert message.startswith(f"clause {case['clause']}: {case['refusal']}: "), message


@pytest.mark.parametrize("case", CORPUS["unparsable"], ids=_ids)
def test_t6_the_reader_is_total(case):
    message = _refused(case["text"])
    assert message.startswith(f"unparsable: line {case['line']}, column "), message


# ---------------------------------------------------------------------------
# Imports over the refunds example: T3 admission, T4b and T8 checker names, T7.
# ---------------------------------------------------------------------------

def _export(tmp_path: Path, target: str = "ilasp", example: Path = REFUNDS) -> Path:
    out = tmp_path / f"export-{target}"
    result = run_main(["export", "ilp", str(example / "model.orm.yaml"), "--labels",
                       str(example / "labels.json"), "--target", target, "--out", str(out)])
    assert result.returncode == 0, result.stderr
    return out


def _import(tmp_path: Path, text: str, coverage: list[list[str]], *, learner: str = "ilasp",
            digest: str | None = None):
    export = _export(tmp_path)
    hypothesis = tmp_path / "hypothesis.las"
    hypothesis.write_text(text, encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": learner, "version": "4.4.1"},
        "export_sha256": digest or hashlib.sha256((export / "export.json").read_bytes()).hexdigest(),
        "clauses_sha256": hashlib.sha256(hypothesis.read_bytes()).hexdigest(),
        "coverage": [{"clause": k, "covered": ids} for k, ids in enumerate(coverage)]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(REFUNDS / "model.orm.yaml"), str(hypothesis),
                       "--labels", str(REFUNDS / "labels.json"), "--reported-coverage", str(run),
                       "--target", "ilasp", "--out", str(out), "--format", "json"])
    return result, out


def test_t3_the_refunds_rule_imports_through_the_shared_checker(tmp_path):
    result, out = _import(tmp_path, CORPUS["accept"][0]["text"], [COVERED])
    assert result.returncode == 0, result.stderr
    proposal = json.loads(out.read_text())
    induction = [op["after"]["provenance"]["induction"] for op in proposal["operations"]]
    assert [block["method"] for block in induction] == ["ilp-ilasp"]
    assert induction[0]["inducer"]["name"] == "ilasp"


@pytest.mark.parametrize("case", CORPUS["checker"], ids=_ids)
def test_t4b_t8_the_fragment_checker_names_what_the_reader_passes_on(tmp_path, case):
    result, out = _import(tmp_path, case["text"], [[]])
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 3, stderr
    assert f"clause {case['clause']}: {case['refusal']}" in stderr, stderr
    assert not out.exists()


def test_t7_a_popper_run_record_is_a_learner_mismatch(tmp_path):
    result, out = _import(tmp_path, CORPUS["accept"][0]["text"], [COVERED], learner="popper")
    assert result.returncode == 3
    assert b"learner-mismatch" in result.stderr
    assert not out.exists()


def test_t7_a_wrong_claimed_coverage_is_refused(tmp_path):
    result, out = _import(tmp_path, CORPUS["accept"][0]["text"], [COVERED[:2]])
    assert result.returncode == 3
    assert b"clause 0: coverage-mismatch" in result.stderr
    assert not out.exists()


# ---------------------------------------------------------------------------
# T1, T1b, T3b, T5b: the task.las rendering.
# ---------------------------------------------------------------------------

EXAMPLES = {"refunds": (REFUNDS / "model.orm.yaml", REFUNDS / "labels.json")}


def _examples(tmp_path: Path) -> dict[str, tuple[Path, Path]]:
    work = _work(tmp_path)
    return {**EXAMPLES, "orders": (work / CASES["model"], work / "m.labels.json")}


def _seeded_export(model: Path, labels: Path, out: Path, seed: str) -> None:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(model), "--labels",
                    str(labels), "--target", "ilasp", "--out", str(out)],
                   check=True, capture_output=True, env=env)


@pytest.mark.parametrize("name", ["refunds", "orders"])
def test_t1_the_task_is_golden_under_two_hash_seeds(tmp_path, name):
    model, labels = _examples(tmp_path)[name]
    trees = []
    for seed in ("0", "1"):
        out = tmp_path / f"{name}-{seed}"
        _seeded_export(model, labels, out, seed)
        trees.append({path: (out / path).read_bytes() for path in ("ilasp/task.las", "export.json")})
    assert trees[0] == trees[1]
    expected = IL2 / "expected" / name
    for path, data in trees[0].items():
        assert data == (expected / path).read_bytes(), path


def _task(tmp_path: Path) -> tuple[str, dict[str, Any]]:
    export = _export(tmp_path)
    neutral = json.loads((export / "neutral.json").read_text())
    return (export / "ilasp" / "task.las").read_text(encoding="utf-8"), neutral


def test_t1b_the_task_layout(tmp_path):
    from gnd.export.ilp_popper import thresholds

    task, neutral = _task(tmp_path)
    head, examples = re.split(r"^#(?:pos|neg)\(", task, maxsplit=1, flags=re.MULTILINE)
    background = [line for line in head.splitlines() if line and not line.startswith("#")]
    assert background and all(re.match(r"(dom|thr|gt|lt)_t_\w+\(", line) for line in background)
    for predicate in neutral["predicates"]:
        arity = len(predicate["types"]) - 1
        mode = re.search(rf"^#modeb\(2, {predicate['name']}\((.*)\)\)\.$", task, re.MULTILINE)
        assert mode and mode.group(1).count("var(") == arity
    assert "#modeh(wrong).\n" in task and "#maxv(4).\n" in task
    amounts = {fact["values"][1] for fact in neutral["facts"] if fact["predicate"] == "f_refund_amount"}
    assert re.findall(r"^thr_t_amount\((-?\d+)\)\.$", task, re.MULTILINE) == \
        [str(v) for v in thresholds(amounts)]
    assert re.findall(r"^#constant\(t_amount, (-?\d+)\)\.$", task, re.MULTILINE) == \
        [str(v) for v in thresholds(amounts)]
    ids = re.findall(r"^#(pos|neg)\((e\d+), \{wrong\}, \{\}, \{$", task, re.MULTILINE)
    assert ids == [(e["label"], f"e{i}") for i, e in enumerate(neutral["examples"], 1)]
    for example in neutral["examples"]:
        assert f"'{example['id']}'" not in examples and f'"{example["id"]}"' not in examples


def test_t3b_every_context_fact_reads_back_as_its_neutral_values(tmp_path):
    from gnd.export.ilp_asp import context_fact

    _task_text, neutral = _task(tmp_path)
    for fact in neutral["facts"]:
        line = context_fact(fact)
        clause = _parse(f"wrong :- {line[:-2]}.\n")["clauses"][0]
        args = clause["body"][0]["atom"]["args"]
        assert [term["const"] for term in args[1:]] == fact["values"]


def test_t5b_a_control_character_is_unrepresentable(tmp_path):
    from gnd.export import ilp_asp
    from gnd.export.ilp import IlpError

    fact = {"example": "w", "predicate": "f_refund_channel", "values": [1, "a\tb"]}
    with pytest.raises(IlpError) as raised:
        ilp_asp.context_fact(fact)
    assert raised.value.code == 3 and str(raised.value).startswith("unrepresentable")
    assert ilp_asp.context_fact({**fact, "values": [1, 'a"\\\nb']}) == \
        'f_refund_channel(1,"a\\"\\\\\\nb").\n'


# ---------------------------------------------------------------------------
# The extractor, pinned to the IL2-D4 probe's recorded ILASP output (IL2-F5).
# ---------------------------------------------------------------------------

PROBE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence" / "IL2" / "probe"


def test_extract_reads_the_hypothesis_after_the_timing_block():
    from gnd.export.ilp_asp import extract_hypothesis

    assert extract_hypothesis((PROBE / "toy.stdout.txt").read_text()) == "wrong :- p(V1).\n"
    assert extract_hypothesis((PROBE / "toy-unsat.stdout.txt").read_text()) == ""


def test_extract_takes_one_run_after_the_last_banner():
    from gnd.export.ilp_asp import extract_hypothesis

    log = "wrong :- early(V1).\n%%%%\n%% Total : 1s\n%%%%\nwrong :- a(V1).\nwrong :- b(V1).\n\nwrong :- c(V1).\n"
    assert extract_hypothesis(log) == "wrong :- a(V1).\nwrong :- b(V1).\n"
    assert extract_hypothesis("") == ""


# ---------------------------------------------------------------------------
# T12: the reference section lists the reader's tables, and nothing else.
# ---------------------------------------------------------------------------

def test_t12_the_reference_section_matches_the_reader():
    from gnd.export import ilp_asp

    doc = (REPO_ROOT / "docs" / "reference" / "ilp-bridge.md").read_text(encoding="utf-8")
    section = doc.split("## ILASP adapter", 1)[1].split("\n## ", 1)[0]
    named = set(re.findall(r"\| `([a-z-]+)` \|$", section, re.MULTILINE))
    assert named == set(ilp_asp.REFUSALS)
    assert set(CORPUS_REFUSALS) == set(ilp_asp.REFUSALS)


CORPUS_REFUSALS = {case["refusal"] for case in CORPUS["refuse"]}


# ---------------------------------------------------------------------------
# T9: the recorded live run replays from its committed bytes (IL-R9).
# ---------------------------------------------------------------------------

LIVE_ROOT = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence" / "IL2" / "live"
#: Invocation 1 is the run of record.
INVOCATIONS = (1,)
TERMINATIONS = {"rendering-rejected", "completed", "learner-timeout", "wall-clock-kill", "output-limit"}
REQUIRED = {"invocation", "run_of_record", "termination", "import", "export_sha256", "adapter_version",
            "ilasp", "limits", "import_args", "numbers", "reproducibility"}


@pytest.mark.parametrize("invocation", INVOCATIONS)
def test_t9_each_recorded_run_replays(tmp_path, invocation):
    import shutil

    from gnd import input_policy
    from gnd.export import ilp_asp
    from gnd.export.ilp_asp import extract_hypothesis

    live = LIVE_ROOT / f"invocation-{invocation}"
    data = (live / "outcome.json").read_bytes()
    assert len(data) < 1024 * 1024
    outcome = input_policy.loads(data)
    assert REQUIRED <= set(outcome)
    assert outcome["invocation"] == invocation and outcome["run_of_record"] is (invocation == 1)
    assert outcome["termination"] in TERMINATIONS
    assert outcome["reproducibility"] == "single run, reproducibility not measured"
    process = outcome["ilasp"]["process"]
    if process is None:
        # IL2-F6: invocation 1's process result was lost; the record must say so and why.
        assert invocation == 1
        assert "IL2-F6" in outcome["process_record"] and outcome["termination"] == "completed"
    else:
        assert outcome["termination"] == (
            "wall-clock-kill" if process["status"] == "timed-out"
            else "output-limit" if process["stdout_truncated"] or process["stderr_truncated"]
            else "rendering-rejected" if process["return_code"] != 0 else "completed")

    export = _export(tmp_path)
    digest = hashlib.sha256((export / "export.json").read_bytes()).hexdigest()
    assert outcome["adapter_version"] == ilp_asp.ADAPTER_VERSION
    assert digest == outcome["export_sha256"]

    hypothesis = extract_hypothesis((live / "raw-stdout.txt").read_text(encoding="utf-8"))
    assert hypothesis == (live / "hypothesis.las").read_text(encoding="utf-8")
    if not hypothesis:
        assert outcome["import"] == "none" and not (live / "run.json").exists()
        return
    imports = tmp_path / "import"
    shutil.copytree(REFUNDS, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
    for name in ("hypothesis.las", "run.json"):
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
    else:
        refusal = replayed.stderr.decode().strip()
        assert refusal == (live / "import-stderr.txt").read_text().strip()
        assert outcome["import"] == "refused:" + ilp_asp.refusal_name(refusal)


# ---------------------------------------------------------------------------
# T-live: clingo, an evaluator that is not GND, agrees with GND's coverage.
# ---------------------------------------------------------------------------

@pytest.mark.live
def test_live_clingo_covers_what_gnd_covers(tmp_path):
    """Live: GND_IL2_CLINGO_PYTHON names the scratch Python with clingo 5.8.2."""
    python = os.environ.get("GND_IL2_CLINGO_PYTHON")
    if not python:
        pytest.skip("GND_IL2_CLINGO_PYTHON is not set")
    from gnd.export.ilp_asp import split_task

    task, neutral = _task(tmp_path)
    background, contexts = split_task(task)
    covered = []
    for index, context in enumerate(contexts):
        program = background + context + CORPUS["accept"][0]["text"]
        result = subprocess.run([python, "-m", "clingo", "--outf=2", "-"], input=program.encode(),
                                capture_output=True, check=False)
        assert result.returncode in (0, 10, 30), result.stderr  # python -m clingo exits 0
        atoms = json.loads(result.stdout)["Call"][0]["Witnesses"][0]["Value"]
        if "wrong" in atoms:
            covered.append(neutral["examples"][index]["id"])
    assert sorted(covered) == sorted(COVERED)


# ---------------------------------------------------------------------------
# Step 4 review successors (notes/phase-IL2-agent-review.md). Each R case is a
# regression for one reproduced finding and failed against bf15642.
# ---------------------------------------------------------------------------

BANNER = "%%%%\n%% Total : 1s\n%%%%\n"


@pytest.mark.parametrize(("log", "refusal"), [
    (BANNER + ":- f_refund_by(V1,V2).\nwrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500).\n",
     "clause 0: asp-constraint"),
    (BANNER + "wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500).\n:- f_refund_by(V1,V2).\n",
     "clause 1: asp-constraint"),
    (BANNER + ":- f_refund_by(V1,V2).\n", "clause 0: asp-constraint"),
    (BANNER + "p :- f_refund_by(V1,V2).\nwrong :- p.\n", "clause 0: head-shape"),
], ids=["constraint-first", "constraint-after", "constraint-only", "other-head"])
def test_r1_the_extractor_hands_every_learned_rule_to_the_reader(log, refusal):
    from gnd.export.ilp_asp import extract_hypothesis

    assert _refused(extract_hypothesis(log)).startswith(refusal + ": ")


def test_r1_a_trailing_comment_stays_with_its_rule():
    from gnd.export.ilp_asp import extract_hypothesis

    text = extract_hypothesis(BANNER + "wrong :- f_refund_by(V1,V2). % penalty 1\n")
    assert _parse(text)["clauses"][0]["body"][0]["atom"]["predicate"] == "f_refund_by"


@pytest.mark.parametrize(("text", "detail"), [
    ("wrong :- f_refund_channel(V1,_cash).\n", "an underscore-prefixed constant"),
    ("wrong :- f_refund_amount(V1,V').\n", "a primed identifier"),
    ("wrong :- f_refund_amount(V1',V2).\n", "a primed identifier"),
    ("wrong :- f_refund_amount(V1,V2) %* *% , gt_t_amount(V2,500)\n.\n", "a block comment"),
    ("wrong :- f_refund_amount(V1,V2), ge_t_amount(V2,500).\n", "a comparison the renderer never writes"),
    ("wrong :- f_refund_amount(V1,V2), le_t_amount(V2,500).\n", "a comparison the renderer never writes"),
    ("wrong :- f_refund_amount(V1,V2), gt_t_amount(500,V2).\n", "a comparison must be (variable, integer)"),
    ("wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,V1).\n", "a comparison must be (variable, integer)"),
    ("wrong :- f_refund_amount(V1,V2), gt_t_amount(V2).\n", "a comparison must be (variable, integer)"),
    ("wrong :- f_refund_amount(V1,2147483648).\n", "outside clingo's 32-bit integer range"),
    ("wrong :- f_refund_amount(V1,-2147483649).\n", "outside clingo's 32-bit integer range"),
    ("wrong :- f_refund_amount(V1,0500).\n", "a leading zero"),
], ids=["underscore-constant", "prime", "prime-2", "block-comment", "ge", "le", "swapped",
        "two-variables", "unary", "int-over", "int-under", "leading-zero"])
def test_r3_to_r10_the_reader_refuses_what_clingo_reads_differently(text, detail):
    message = _refused(text)
    assert message.startswith("unparsable: line ") and message.endswith(detail), message


@pytest.mark.parametrize("text", [
    "wrong :- f_refund_amount(V1,2147483647).\n",
    "wrong :- f_refund_amount(V1,-2147483648).\n",
    "wrong :- f_refund_amount(V1,0).\n",
    "wrong :- f_refund_amount(V1,_V2).\n",
], ids=["int-max", "int-min", "zero", "underscore-variable"])
def test_r6_the_range_and_variable_boundaries_are_admitted(text):
    assert _parse(text)["clauses"]


def test_r7_the_script_and_the_replay_share_one_refusal_name():
    from gnd.export.ilp_asp import refusal_name

    assert refusal_name("clause 0: empty-antecedent: nothing is left") == "empty-antecedent"
    assert refusal_name("unparsable: line 1, column 30: nesting deeper than 4") == "unparsable"
    assert refusal_name("learner-mismatch: the run record names popper") == "learner-mismatch"


RULE = "wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500).\n"


@pytest.mark.parametrize(("text", "detail"), [
    (RULE * 33, "more than 32 rules"),
    ("wrong :- " + ", ".join(["f_refund_amount(V1,V2)"] * 17) + ".\n", "more than 16 body literals"),
    ("wrong :- f_refund_amount(V1,V2), " + "not " * 5 + "f_refund_by(V1,V3).\n", "nesting deeper than 4"),
    ("wrong :- f_refund_amount(V1," + "1" * 33 + ").\n", "an integer longer than 32 digits"),
], ids=["rules", "literals", "depth", "digits"])
def test_r9_one_over_each_cap_names_the_cap(text, detail):
    assert _refused(text).endswith(detail)


@pytest.mark.parametrize("text", [
    RULE * 32,
    "wrong :- " + ", ".join(["f_refund_amount(V1,V2)"] * 16) + ".\n",
    "wrong :- f_refund_amount(V1,V2), " + "not " * 4 + "f_refund_by(V1,V3).\n",
], ids=["rules", "literals", "depth"])
def test_r9_each_cap_is_admitted_at_its_bound(text):
    assert _parse(text)["clauses"]


def test_r9_a_hypothesis_over_1_mib_is_refused(tmp_path):
    text = RULE + "%" + "x" * (1024 * 1024) + "\n"
    result, out = _import(tmp_path, text, [COVERED])
    assert result.returncode == 3 and b"1048576-byte cap" in result.stderr, result.stderr
    assert not out.exists()


def test_r8_the_constants_table_matches_the_reader():
    doc = (REPO_ROOT / "docs" / "reference" / "ilp-bridge.md").read_text(encoding="utf-8")
    section = doc.split("\n**Constants:**\n", 1)[1].strip("\n").split("\n\n", 1)[0]
    rows = [line.strip("| ").split(" | ") for line in section.splitlines()[2:]]
    kinds = {"an integer": int, "a string": str, "a boolean": bool}
    read = {}
    for spelling, reading in rows:
        kind = kinds[next(k for k in kinds if reading.startswith(k))]
        for term in re.findall(r"`([^`]+)`", spelling):
            constants = _constants(_parse(f"wrong :- f_refund_channel(V1,{term}).\n"))
            assert [type(c) for c in constants] == [kind], (term, reading)
            read[term] = kind
    assert set(read.values()) == {int, str, bool}
    assert set(read) == {"40", "-3", '"a\\"b"', "web", "true", "false"}
