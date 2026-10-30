"""IL3: Boolean rule sets -- the feature-table export and the rule-set reader.

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL3-spec.md (r1, approved
2026-10-28, §13). Under IL3-D11 the reader's cases are a corpus written before the
code: tests/fixtures/ilp_learners/il3/rulesets.json, stories inline.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
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
IL3 = REPO_ROOT / "tests" / "fixtures" / "ilp_learners" / "il3"
CORPUS = json.loads((IL3 / "rulesets.json").read_text(encoding="utf-8"))
EVIDENCE = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-learners" / "evidence" / "IL3"
GOOD = "f_refund_amount__2__3__gt_t_amount__500"


def _ids(case: dict[str, Any]) -> str:
    return case["id"]


def _export(tmp_path: Path, target: str = "rules", model: Path | None = None,
            labels: Path | None = None) -> Path:
    out = tmp_path / f"export-{target}"
    result = run_main(["export", "ilp", str(model or REFUNDS / "model.orm.yaml"), "--labels",
                       str(labels or REFUNDS / "labels.json"), "--target", target, "--out", str(out)])
    assert result.returncode == 0, result.stderr
    return out


def _examples(tmp_path: Path) -> dict[str, tuple[Path, Path]]:
    work = _work(tmp_path)
    return {"refunds": (REFUNDS / "model.orm.yaml", REFUNDS / "labels.json"),
            "orders": (work / CASES["model"], work / "m.labels.json")}


def _neutral(tmp_path: Path) -> dict[str, Any]:
    export = _export(tmp_path, "neutral")
    return json.loads((export / "neutral.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# T1, T1b, T2: the feature table is golden, self-describing and exact.
# ---------------------------------------------------------------------------

_SEEDED = """\
import sys
from gnd.cli import main
sys.exit(main(["export", "ilp", sys.argv[1], "--labels", sys.argv[2], "--target", "rules",
               "--out", sys.argv[3]]))
"""


@pytest.mark.parametrize("name", ["refunds", "orders"])
def test_t1_the_feature_table_is_golden_under_two_hash_seeds(tmp_path, name):
    model, labels = _examples(tmp_path)[name]
    outputs = []
    for seed in ("0", "1"):
        out = tmp_path / f"seed-{seed}"
        env = {**os.environ, "PYTHONHASHSEED": seed}
        subprocess.run([sys.executable, "-c", _SEEDED, str(model), str(labels), str(out)],
                       check=True, capture_output=True, env=env)
        outputs.append({file: (out / file).read_bytes() for file in ("export.json", "rules/features.json")})
    assert outputs[0] == outputs[1]
    for file, data in outputs[0].items():
        assert data == (IL3 / "expected" / name / Path(file).name).read_bytes(), file


_COLUMN = re.compile(r"([a-z][a-z0-9_]*?)__([1-9][0-9]*)__([1-9][0-9]*)__((?:gt|lt)_t_[A-Za-z0-9_]+?)__(m?)(0|[1-9][0-9]*)")


@pytest.mark.parametrize("name", ["refunds", "orders"])
def test_t1b_the_table_validates_and_each_column_says_what_it_means(tmp_path, name):
    from jsonschema import Draft202012Validator

    model, labels = _examples(tmp_path)[name]
    export = _export(tmp_path, model=model, labels=labels)
    table = json.loads((export / "rules" / "features.json").read_text(encoding="utf-8"))
    schema = json.loads((SRC / "ilp-features.schema.json").read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(table))
    neutral = json.loads((export / "neutral.json").read_text(encoding="utf-8"))
    predicates = {row["name"]: row for row in neutral["predicates"]}
    for column in table["columns"]:
        predicate, position, arity, comparison, sign, digits = _COLUMN.fullmatch(column["name"]).groups()
        assert (column["predicate"], column["position"], column["arity"], column["comparison"]) == (
            predicate, int(position), int(arity), comparison)
        assert column["arity"] == len(predicates[predicate]["types"])
        assert column["threshold"] == (-int(digits) if sign else int(digits))
        assert column["operator"] == {"gt": ">", "lt": "<"}[comparison[:2]]
        assert column["type"] == predicates[predicate]["types"][int(position)]
        assert column["role"] == predicates[predicate]["roles"][int(position) - 1]
    assert all(len(row["values"]) == len(table["columns"]) for row in table["rows"])
    assert [row["example"] for row in table["rows"]] == [e["id"] for e in neutral["examples"]]
    assert [row["label"] for row in table["rows"]] == [e["label"] for e in neutral["examples"]]


@pytest.mark.parametrize("name", ["refunds", "orders"])
def test_t2_every_cell_matches_an_oracle(tmp_path, name):
    from gnd.export import ilp_popper

    model, labels = _examples(tmp_path)[name]
    export = _export(tmp_path, model=model, labels=labels)
    table = json.loads((export / "rules" / "features.json").read_text(encoding="utf-8"))
    neutral = json.loads((export / "neutral.json").read_text(encoding="utf-8"))
    rows = ilp_popper.threshold_rows(neutral)
    expected_columns = [
        f"{p['name']}__{k}__{len(p['types'])}__{name_}"
        for p in neutral["predicates"] for k in range(1, len(p["types"]))
        for name_, type_name, _holds in rows if type_name == p["types"][k]]
    assert [column["name"] for column in table["columns"]] == expected_columns
    for row in table["rows"]:
        facts = [f for f in neutral["facts"] if f["example"] == row["example"]]
        for column, cell in zip(table["columns"], row["values"], strict=True):
            test = (lambda v, t=column["threshold"]: v > t) if column["operator"] == ">" else (
                lambda v, t=column["threshold"]: v < t)
            hit = any(f["predicate"] == column["predicate"]
                      and isinstance(f["values"][column["position"] - 1], int)
                      and test(f["values"][column["position"] - 1]) for f in facts)
            assert cell == int(hit), (row["example"], column["name"])


def test_t2_the_refunds_table_has_the_size_the_spec_observed(tmp_path):
    export = _export(tmp_path)
    table = json.loads((export / "rules" / "features.json").read_text(encoding="utf-8"))
    assert (len(table["rows"]), len(table["columns"])) == (8, 38)
    assert table["work"]["cells"] == 304


# ---------------------------------------------------------------------------
# T3: the bounds, fixed before results (IL3-D5).
# ---------------------------------------------------------------------------

def test_t3_the_bounds_refuse_by_name(tmp_path, monkeypatch):
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    assert (ilp_rules.MAX_FEATURES, ilp_rules.MAX_CELLS) == (4096, 4_000_000)
    neutral = _neutral(tmp_path)
    assert "rules/features.json" in ilp_rules.render(neutral)
    monkeypatch.setattr(ilp_rules, "MAX_FEATURES", 38)
    monkeypatch.setattr(ilp_rules, "MAX_CELLS", 304)
    assert "rules/features.json" in ilp_rules.render(neutral)
    monkeypatch.setattr(ilp_rules, "MAX_FEATURES", 37)
    with pytest.raises(IlpError, match="^too-many-features"):
        ilp_rules.render(neutral)
    monkeypatch.setattr(ilp_rules, "MAX_FEATURES", 4096)
    monkeypatch.setattr(ilp_rules, "MAX_CELLS", 303)
    with pytest.raises(IlpError, match="^too-large"):
        ilp_rules.render(neutral)
    out = tmp_path / "refused"
    result = run_main(["export", "ilp", str(REFUNDS / "model.orm.yaml"), "--labels",
                       str(REFUNDS / "labels.json"), "--target", "rules", "--out", str(out)])
    assert result.returncode == 3 and b"too-large" in result.stderr
    assert not out.exists()


def test_t3_a_model_without_an_integer_argument_has_no_features(tmp_path):
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    neutral = _neutral(tmp_path)
    neutral["predicates"] = [p for p in neutral["predicates"] if p["name"] != "f_refund_amount"]
    neutral["facts"] = [f for f in neutral["facts"] if f["predicate"] != "f_refund_amount"]
    with pytest.raises(IlpError, match="^no-features"):
        ilp_rules.render(neutral)


# ---------------------------------------------------------------------------
# T4, T7: the reader corpus and its totality.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CORPUS["parse"], ids=_ids)
def test_t4_the_reader(case):
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    if "clauses" in case:
        assert ilp_rules.parse_ruleset(case["text"]) == case["clauses"]
        return
    with pytest.raises(IlpError) as raised:
        ilp_rules.parse_ruleset(case["text"])
    message = str(raised.value)
    prefix = f"clause {case['clause']}: " if case["clause"] is not None else ""
    assert message.startswith(f"{prefix}{case['refusal']}:"), message
    assert raised.value.code == 3


def _cond(k: int = 0) -> str:
    return f"f_p__1__2__gt_t_x__{k + 1}=1"


@pytest.mark.parametrize(("text", "detail"), [
    ("[" + " V ".join(f"[{_cond(k)}]" for k in range(33)) + "]", "more than 32 rules"),
    ("[[" + "^".join(_cond(k) for k in range(17)) + "]]", "more than 16 conditions"),
    ("[[f_" + "p" * 150 + "__1__2__gt_t_x__1=1]]", "longer than 160"),
    ("[[f_p__1__2__gt_t_x__" + "9" * 33 + "=1]]", "longer than 32 digits"),
    ("[[" + _cond() + "]] trailing", "unparsable"),
    ("[[" + _cond() + "]\n]", "unparsable"),
    ("", "unparsable"),
])
def test_t7_the_reader_is_total(text, detail):
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError) as raised:
        ilp_rules.parse_ruleset(text)
    assert raised.value.code == 3
    assert detail in str(raised.value)


def test_t7_non_utf8_input_is_refused_by_the_import(tmp_path):
    path = tmp_path / "ruleset.txt"
    path.write_bytes(b"[[" + GOOD.encode() + b"=1\xff]]")
    result, out = _import_file(tmp_path, path, [["harbor"]])
    assert result.returncode == 3 and b"unparsable" in result.stderr
    assert not out.exists()


# ---------------------------------------------------------------------------
# T5-T8: the rules import over the refunds example.
# ---------------------------------------------------------------------------

def _import_file(tmp_path: Path, path: Path, coverage: list[list[str]], *,
                 learner: str = "wittgenstein"):
    export = _export(tmp_path)
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": learner, "version": "0.3.5"},
        "export_sha256": hashlib.sha256((export / "export.json").read_bytes()).hexdigest(),
        "clauses_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "coverage": [{"clause": k, "covered": ids} for k, ids in enumerate(coverage)]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(REFUNDS / "model.orm.yaml"), str(path),
                       "--labels", str(REFUNDS / "labels.json"), "--reported-coverage", str(run),
                       "--target", "rules", "--out", str(out), "--format", "json"])
    return result, out


@pytest.mark.parametrize("case", CORPUS["import"], ids=_ids)
def test_t5_to_t8_the_rules_import(tmp_path, case):
    path = tmp_path / "ruleset.txt"
    path.write_text(case["text"], encoding="utf-8")
    result, out = _import_file(tmp_path, path, case["coverage"], learner=case["learner"])
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == case["exit"], stderr
    if case["exit"] == 0:
        proposal = json.loads(out.read_text())
        induction = [op["after"]["provenance"]["induction"] for op in proposal["operations"]]
        assert [block["method"] for block in induction] == ["ilp-rules"]
        assert induction[0]["inducer"]["name"] == "wittgenstein"
    else:
        assert case["refusal"] in stderr, stderr
        assert not out.exists()


def test_t8_positive_clauses_use_fresh_variables():
    """IL3-F1: fresh variables mean no atom-to-atom join; 9b fires only through D13."""
    from gnd.export import ilp_rules

    for case in CORPUS["parse"]:
        if "clauses" not in case:
            continue
        for clause in ilp_rules.parse_ruleset(case["text"])["clauses"]:
            atom, comparison = (literal["atom"] for literal in clause["body"])
            names = [arg["var"] for arg in atom["args"]]
            assert len(names) == len(set(names))
            assert comparison["args"][0]["var"] in names[1:]


# ---------------------------------------------------------------------------
# T10: the extractor.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CORPUS["extract"], ids=_ids)
def test_t10_the_extractor(case):
    from gnd.export import ilp_rules

    assert ilp_rules.extract_ruleset(case["stdout"]) == case["ruleset"]


# ---------------------------------------------------------------------------
# T13: the reference section matches the code.
# ---------------------------------------------------------------------------

def test_t13_the_reference_section_matches_the_code():
    from gnd.export import ilp_rewrite, ilp_rules

    doc = (REPO_ROOT / "docs" / "reference" / "ilp-bridge.md").read_text(encoding="utf-8")
    section = doc.split("\n## Boolean rule sets\n", 1)[1].split("\n## ", 1)[0]
    for name in (*ilp_rules.EXPORT_REFUSALS, *ilp_rules.REFUSALS):
        assert f"`{name}`" in section, name
    for spelling in (*ilp_rules.TRUE_SPELLINGS, *ilp_rules.FALSE_SPELLINGS):
        assert f"`{spelling}`" in section, spelling
    for bound in ("MAX_FEATURES", "MAX_CELLS"):
        assert f"{getattr(ilp_rules, bound):,}" in section, bound
    documented = set(re.findall(r"refused `([a-z-]+)`", section))
    assert documented <= {*ilp_rules.EXPORT_REFUSALS, *ilp_rules.REFUSALS, *ilp_rewrite.REFUSALS,
                          *getattr(ilp_rules, "IMPORT_REFUSALS", ()), "unparsable"}


# ---------------------------------------------------------------------------
# T9: the run of record replays from its committed bytes.
# ---------------------------------------------------------------------------

LIVE_ROOT = EVIDENCE / "live"
#: Invocation 1 is the run of record.
INVOCATIONS = (1,)
TERMINATIONS = {"rendering-rejected", "completed", "learner-timeout", "wall-clock-kill", "output-limit"}
REQUIRED = {"invocation", "run_of_record", "termination", "import", "export_sha256", "adapter_version",
            "learner", "process", "limits", "argv", "import_args", "numbers", "reproducibility"}


def _script():
    spec = importlib.util.spec_from_file_location("il3_run_rules", EVIDENCE / "run_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("invocation", INVOCATIONS)
def test_t9_the_recorded_run_replays(tmp_path, invocation):
    from gnd import input_policy
    from gnd.export import ilp_rules

    live = LIVE_ROOT / f"invocation-{invocation}"
    outcome = input_policy.loads((live / "outcome.json").read_bytes())
    assert REQUIRED <= set(outcome)
    assert outcome["invocation"] == invocation and outcome["run_of_record"] is (invocation == 1)
    assert outcome["termination"] in TERMINATIONS
    assert outcome["reproducibility"] == "single run, reproducibility not measured"
    assert outcome["adapter_version"] == ilp_rules.ADAPTER_VERSION
    script = _script()
    process = outcome["process"]
    assert outcome["termination"] == script.termination(process)
    assert json.loads((live / "invocation.json").read_text(encoding="utf-8")) == process
    stderr = (live / "raw-stderr.txt").read_text(encoding="utf-8")
    assert len(stderr.encode("utf-8")) == process["stderr_observed_bytes"]
    meta = json.loads((live / "run-meta.json").read_text(encoding="utf-8"))
    assert meta["learner"] == outcome["learner"]
    # Review 6: the recorded settings are the script's own constants.
    assert outcome["limits"] == script.LIMITS.model_dump()
    assert outcome["argv"] == script.RECORDED_ARGV
    assert outcome["import_args"] == list(script.IMPORT_ARGS)
    assert outcome["licence"] == script.LICENCE

    export = _export(tmp_path)
    digest = hashlib.sha256((export / "export.json").read_bytes()).hexdigest()
    assert digest == outcome["export_sha256"]

    stdout = (live / "raw-stdout.txt").read_text(encoding="utf-8")
    assert len(stdout.encode("utf-8")) == process["stdout_observed_bytes"]
    assert outcome["learner"] == script.learner(stdout)
    ruleset = script.read_ruleset(stdout, outcome["termination"])
    if not ruleset:
        assert outcome["import"] == "none" and not (live / "ruleset.txt").exists()
        return
    assert ruleset == (live / "ruleset.txt").read_text(encoding="utf-8")
    run = json.loads((live / "run.json").read_text(encoding="utf-8"))
    assert [row["covered"] for row in run["coverage"]] == script.covers(stdout)
    imports = tmp_path / "import"
    shutil.copytree(REFUNDS, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
    for name in ("ruleset.txt", "run.json"):
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
        assert refusal == (live / "import-stderr.txt").read_text().strip()
        assert outcome["import"] == script.import_outcome(refusal)


# ---------------------------------------------------------------------------
# T-live: the scratch learner reproduces the committed coverage.
# ---------------------------------------------------------------------------

_COVERS_OF = """\
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import pandas
from wittgenstein.base import ruleset_fromstr
table = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
frame = pandas.DataFrame([row["values"] for row in table["rows"]],
                         columns=[column["name"] for column in table["columns"]],
                         index=[row["example"] for row in table["rows"]])
ruleset = ruleset_fromstr(Path(sys.argv[3]).read_text(encoding="utf-8"))
for index, rule in enumerate(ruleset.rules):
    for cond in rule.conds:
        cond.val = int(cond.val)
    print(f"COVERS {index} {json.dumps(sorted(rule.covers(frame).index.tolist()))}")
"""


@pytest.mark.live
def test_live_the_learner_covers_what_it_reported(tmp_path):
    """Live (spec T-live): wittgenstein's own Rule.covers over the committed rule set gives the
    committed COVERS lines. It evaluates; it does not learn again (IL3-F5: RIPPER 0.3.5 is not
    deterministic under random_state=0). GND_IL3_PYTHON names the scratch venv's python,
    GND_IL3_LEARNER the extracted sdist."""
    python, learner = os.environ.get("GND_IL3_PYTHON"), os.environ.get("GND_IL3_LEARNER")
    if not (python and learner):
        pytest.skip("GND_IL3_PYTHON and GND_IL3_LEARNER are not set")
    export = _export(tmp_path)
    live = LIVE_ROOT / "invocation-1"
    result = subprocess.run([python, "-I", "-c", _COVERS_OF, learner, str(export / "rules" / "features.json"),
                             str(live / "ruleset.txt")], check=True, capture_output=True, text=True)
    script = _script()
    assert script.covers(result.stdout) == script.covers((live / "raw-stdout.txt").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Step 4 regressions (notes/phase-IL3-agent-review.md), each red before its fix.
# ---------------------------------------------------------------------------

def _valid(name_length: int) -> str:
    """A column name of exactly ``name_length`` characters the renderer could write."""
    tail = "__1__2__gt_t_x__5"
    return "f_" + "p" * (name_length - 2 - len(tail)) + tail


@pytest.mark.parametrize("arity", ["65", "5000000", "9" * 140])
def test_r1_the_arity_is_bounded_before_any_clause_is_built(arity):
    """Review 1: an atom has at most 64 arguments (ilp-clauses.schema.json)."""
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError, match="^unparsable"):
        ilp_rules.parse_ruleset(f"[[p__1__{arity}__gt_t_x__5=1]]")


def test_r1_arity_64_is_read():
    from gnd.export import ilp_rules

    clause = ilp_rules.parse_ruleset("[[p__63__64__gt_t_x__5=1]]")["clauses"][0]
    assert len(clause["body"][0]["atom"]["args"]) == 64
    assert clause["body"][1]["atom"]["args"][0] == {"var": "V63"}


def _long(neutral: dict[str, Any], predicate: str, type_name: str, extra: int | None = None) -> dict[str, Any]:
    old = neutral["predicates"][0]
    renamed = json.loads(json.dumps(neutral).replace(f'"{old["name"]}"', json.dumps(predicate))
                         .replace('"t_amount"', json.dumps(type_name))
                         .replace('"ge_t_amount"', json.dumps("ge_" + type_name))
                         .replace('"gt_t_amount"', json.dumps("gt_" + type_name))
                         .replace('"le_t_amount"', json.dumps("le_" + type_name))
                         .replace('"lt_t_amount"', json.dumps("lt_" + type_name)))
    if extra is not None:
        fact = next(f for f in renamed["facts"] if f["predicate"] == predicate)
        renamed["facts"].append({**fact, "values": [fact["values"][0], extra]})
    return renamed


@pytest.mark.parametrize(("predicate", "type_name", "extra"), [
    ("f_" + "q" * 59, "t_" + "m" * 59, 10 ** 25),
    ("f_refund_amount", "t_amount", 10 ** 33),
    ("f_a__1__2__gt_t_x", "t_amount", None),
])
def test_r2_r3_the_renderer_refuses_a_name_it_cannot_read_back(tmp_path, predicate, type_name, extra):
    """Reviews 2 and 3: a name over 160 characters, a 33-digit threshold, a name that
    parses two ways: one documented refusal, never a schema-invalid table."""
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    neutral = _long(_neutral(tmp_path), predicate, type_name, extra)
    with pytest.raises(IlpError, match="^column-name"):
        ilp_rules.render(neutral)
    assert "column-name" in ilp_rules.EXPORT_REFUSALS


def _live_common():
    sys.path.insert(0, str(EVIDENCE.parent))
    try:
        import live_common
    finally:
        sys.path.remove(str(EVIDENCE.parent))
    return live_common


@pytest.mark.parametrize("status", ["spawn-failed", "cleanup-failed"])
def test_r4_an_unruled_status_is_not_recorded(status):
    """Review 4: §6 rules succeeded, failed and timed-out only."""
    common = _live_common()
    with pytest.raises(SystemExit, match="unruled"):
        common.termination({"status": status, "stdout_truncated": False, "stderr_truncated": False})


def test_r4_only_exit_3_is_a_named_refusal():
    common = _live_common()
    assert common.import_outcome("clause 0: negation-as-failure: x") == "refused:negation-as-failure"
    with pytest.raises(SystemExit, match="exit 70"):
        common.refusal_for_exit(70, "internal: boom")
    assert common.refusal_for_exit(3, "unparsable: column 1: x") == "refused:unparsable"


_TAMPER = {
    "limits": ("outcome.json", lambda o: o["limits"].__setitem__("timeout_seconds", 6000)),
    "argv": ("outcome.json", lambda o: o["argv"].remove("-I")),
    "licence": ("outcome.json", lambda o: o.__setitem__("licence", "")),
    "import-args": ("outcome.json", lambda o: o["import_args"].__setitem__(-1, "text")),
    "learner": ("outcome.json", lambda o: o["learner"].__setitem__("version", "9.9")),
}


@pytest.mark.parametrize("name", ["control", *sorted(_TAMPER), "stdout"])
def test_r6_t9_fails_on_tampered_evidence(tmp_path, monkeypatch, name):
    """Review 6: every recorded field T9 claims to check can fail it."""
    live = tmp_path / "live"
    shutil.copytree(LIVE_ROOT, live)
    record = live / "invocation-1"
    if name == "control":
        pass
    elif name == "stdout":
        with (record / "raw-stdout.txt").open("a", encoding="utf-8") as stream:
            stream.write("junk\n")
    else:
        path, change = _TAMPER[name]
        outcome = json.loads((record / path).read_text(encoding="utf-8"))
        change(outcome)
        (record / path).write_text(json.dumps(outcome), encoding="utf-8")
        if name == "learner":
            meta = json.loads((record / "run-meta.json").read_text(encoding="utf-8"))
            meta["learner"]["version"] = "9.9"
            (record / "run-meta.json").write_text(json.dumps(meta), encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "LIVE_ROOT", live)
    replay = tmp_path / "replay"
    replay.mkdir()
    if name == "control":
        test_t9_the_recorded_run_replays(replay, 1)
        return
    with pytest.raises(AssertionError):
        test_t9_the_recorded_run_replays(replay, 1)


def test_r7_every_reader_cap_accepts_at_its_bound():
    """Review 7: the accept side of each cap, and an exact 161-character name."""
    from gnd.export import ilp_rules
    from gnd.export.ilp import IlpError

    rules = "[" + " V ".join(f"[{_cond(k)}]" for k in range(32)) + "]"
    assert len(ilp_rules.parse_ruleset(rules)["clauses"]) == 32
    conditions = "[[" + "^".join(_cond(k) for k in range(16)) + "]]"
    with pytest.raises(IlpError, match="propositional-conjunction"):
        ilp_rules.parse_ruleset(conditions)
    assert ilp_rules.parse_ruleset(f"[[{_valid(160)}=1]]")["clauses"]
    with pytest.raises(IlpError, match="longer than 160"):
        ilp_rules.parse_ruleset(f"[[{_valid(161)}=1]]")
    for threshold in ("9" * 32, "m" + "9" * 32):
        assert ilp_rules.parse_ruleset(f"[[f_p__1__2__gt_t_x__{threshold}=1]]")["clauses"]
    for spelling in ("  if a then b", "\tIf a then b"):
        with pytest.raises(IlpError, match="^ordered-rule-list"):
            ilp_rules.parse_ruleset(spelling)


def test_r8_the_help_names_the_rules_target():
    """Review 8: the export's --target help and the import's CLAUSES help name rules."""
    export = run_main(["export", "ilp", "--help"]).stdout.decode()
    assert "rules (neutral form plus rules/features.json)" in " ".join(export.split())
    imported = run_main(["import", "ilp-rules", "--help"]).stdout.decode()
    assert "rule set" in " ".join(imported.split())
