"""IK5: the ILP bridge, ``gnd export ilp`` and ``gnd import ilp-rules`` (induced-knowledge).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK5-spec.md. Under
IK5-D1 the cases are an owner-approved corpus: inputs in
tests/fixtures/induced_knowledge/ik5-corpus/cases.json, hand-written answers in
expected.json and expected-export/, and stories in that directory's README.md.
The learner outputs are hand-authored in Popper's printed syntax (IK5-D13 (a)).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik5-corpus"
CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
ANSWERS = EXPECTED["cases"]
BY_ID = {case["id"]: case for case in CASES["cases"]}


def _work(tmp_path: Path) -> Path:
    work = tmp_path / "corpus"
    if not work.exists():
        shutil.copytree(CORPUS, work, symlinks=True)
        (work / "pops" / "link.yaml").symlink_to(work / "pops" / "n1.yaml")
    return work


def _argv(work: Path, case: dict[str, Any], out: Path) -> list[str]:
    model = str(work / CASES["model"])
    manifest = str(work / case["manifest"])
    if case["command"] == "export":
        return ["export", "ilp", model, "--labels", manifest, "--target", case["target"],
                "--out", str(out)]
    return ["import", "ilp-rules", model, str(work / case["clauses"]), "--labels", manifest,
            "--reported-coverage", str(work / case["run"]), "--target", case["target"],
            "--out", str(out), "--format", "json"]


def _tree(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


def _run(tmp_path: Path, case: dict[str, Any]) -> tuple[Any, Path]:
    work = _work(tmp_path)
    out = tmp_path / f"{case['id'].lower()}.out"
    if case.get("out_exists") or case["id"] == "XE3":
        out.mkdir() if case["command"] == "export" else out.write_text("{}\n", encoding="utf-8")
    return run_main(_argv(work, case, out)), out


CORPUS_CASES = [case for case in CASES["cases"] if case["command"] != "preview"]


@pytest.mark.parametrize("case", CORPUS_CASES, ids=lambda case: case["id"])
def test_ik5_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = ANSWERS[case["id"]]
    existed = case.get("out_exists") or case["id"] == "XE3"
    result, out = _run(tmp_path, case)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == answer["exit"], stdout + stderr
    if "refusal" in answer:
        assert answer["refusal"] in stderr, stderr
        if "clause" in answer:
            assert f"clause {answer['clause']}" in stderr, stderr
    if answer["exit"] != 0:
        if not existed:
            assert not out.exists(), "a refused run wrote its output"
        return
    if case["command"] == "export":
        assert answer["export_sha256"] in stdout
        assert _tree(out) == _tree(CORPUS / answer["tree"])
        return
    proposal = json.loads(out.read_text(encoding="utf-8"))
    added = [operation["after"] for operation in proposal["operations"]]
    assert added == answer["constraints"]
    assert all(operation["kind"] == "add" for operation in proposal["operations"])
    report = json.loads(stdout)
    assert report["schema_version"] == "gnd-ilp-import/1"
    assert {str(k): row["vacuous"] for k, row in enumerate(report["clauses"])} == answer["vacuous"]


def test_answer_key_covers_every_case() -> None:
    assert {case["id"] for case in CASES["cases"]} == set(ANSWERS)


def test_popper_and_neutral_imports_add_the_same_rules(tmp_path: Path) -> None:
    """I1 and I2 differ only in the method spelling and the evidence digests."""
    def core(constraint: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in constraint.items() if key != "provenance"}

    assert [core(c) for c in ANSWERS["I1"]["constraints"]] == [
        core(c) for c in ANSWERS["I2"]["constraints"]]


def test_i3_the_proposal_previews(tmp_path: Path) -> None:
    result, out = _run(tmp_path, BY_ID["I1"])
    assert result.returncode == 0, result.stderr
    work = _work(tmp_path)
    preview = run_main([
        "evolve", "preview", str(work / CASES["model"]), str(out), "--workspace", str(tmp_path),
        "--records", str(tmp_path / "records"), "--out", str(tmp_path / "preview.json"),
    ])
    assert preview.returncode == ANSWERS["I3"]["exit"], preview.stdout + preview.stderr


def test_d1_export_is_the_same_under_two_hash_seeds(tmp_path: Path) -> None:
    work = _work(tmp_path)
    trees = []
    for seed in ("0", "1"):
        out = tmp_path / f"seed{seed}"
        completed = subprocess.run(
            [sys.executable, "-m", "gnd", *_argv(work, BY_ID["X1"], out)], cwd=REPO_ROOT,
            env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, timeout=120, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        trees.append(_tree(out))
    assert trees[0] == trees[1] == _tree(CORPUS / ANSWERS["X1"]["tree"])


# ---------------------------------------------------------------------------
# Implementation tests (spec §8 T3, T5, T9, T10, T12 and corpus finding C-F1).
# Separately identified successors of the approved corpus; none changes an
# approved answer.
# ---------------------------------------------------------------------------

SRC = REPO_ROOT / "src" / "gnd"


def _schema(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SRC / name).read_text(encoding="utf-8")))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_for(work: Path, model: Path, populations: list[tuple[str, str, str]]) -> Path:
    document = {"schema_version": "gnd-labels/1", "model_sha256": _sha(model), "mode": "class",
                "populations": [{"id": pid, "path": f"pops/{name}",
                                 "sha256": _sha(work / "pops" / name), "class": klass}
                                for pid, name, klass in populations],
                "rules": {"id:u_order_customer": {"fires_on": "negative"}}}
    path = work / f"{model.stem}.gen.labels.json"
    path.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    return path


def _variant(work: Path, name: str, old: str, new: str) -> Path:
    text = (work / CASES["model"]).read_text(encoding="utf-8")
    assert old in text
    model = work / name
    model.write_text(text.replace(old, new), encoding="utf-8")
    for population in (work / "pops").glob("*.yaml"):
        if population.is_symlink():
            continue
        body = population.read_text(encoding="utf-8")
        (work / "pops" / f"{model.stem}-{population.name}").write_text(
            body.replace(f"model: {CASES['model']}", f"model: {name}"), encoding="utf-8")
    return model


def _export(argv_model: Path, manifest: Path, out: Path, target: str = "popper"):
    return run_main(["export", "ilp", str(argv_model), "--labels", str(manifest),
                     "--target", target, "--out", str(out)])


@pytest.mark.parametrize(("label", "old", "new", "refusal"), [
    ("redacted", "      - { object_type: amount, role_name: amount }",
     "      - { object_type: amount, role_name: amount, redact: true }", "redacted"),
    ("name", "  - id: order_flagged\n", "  - id: order_flagged_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n", "name"),
    ("primitive", "    name: Amount\n    kind: value\n    primitive: Integer",
     "    name: Amount\n    kind: value\n    primitive: Decimal", "primitive"),
])
def test_t3_export_refuses_what_it_cannot_render(tmp_path, label, old, new, refusal):
    work = _work(tmp_path)
    model = _variant(work, f"{label}.orm.yaml", old, new)
    if label == "name":
        for population in (work / "pops").glob(f"{model.stem}-*.yaml"):
            population.write_text(population.read_text().replace("order_flagged", "order_flagged_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
    manifest = _manifest_for(work, model, [("n1", f"{model.stem}-n1.yaml", "negative")])
    out = tmp_path / "out"
    result = _export(model, manifest, out)
    assert result.returncode == 3, result.stderr
    assert refusal in result.stderr.decode()
    assert not out.exists()


def test_t3_export_refuses_over_the_facts_bound(tmp_path, monkeypatch):
    from gnd.export import ilp

    monkeypatch.setattr(ilp, "MAX_FACTS", 3)
    work = _work(tmp_path)
    out = tmp_path / "out"
    result = _export(work / CASES["model"], work / "m.labels.json", out)
    assert result.returncode == 3 and b"too-large" in result.stderr
    assert not out.exists()


def _import(work: Path, clauses: Path, run: Path, out: Path, target: str = "neutral", *extra):
    return run_main(["import", "ilp-rules", str(work / CASES["model"]), str(clauses),
                     "--labels", str(work / "m.labels.json"), "--reported-coverage", str(run),
                     "--target", target, "--out", str(out), "--format", "json", *extra])


def _bound_run(work: Path, clauses: Path, coverage: list[list[str]], target: str = "neutral") -> Path:
    export = json.loads((CORPUS / "expected.json").read_text())["export_sha256"][target]
    run = work / f"{clauses.name}.run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": "popper", "version": "1"},
        "export_sha256": export, "clauses_sha256": _sha(clauses),
        "coverage": [{"clause": k, "covered": ids} for k, ids in enumerate(coverage)]}))
    return run


HOSTILE_CLAUSES = {
    "over-cap": b'{"schema_version": "gnd-ilp-clauses/1", "clauses": [], "pad": "'
                + b"x" * (1024 * 1024) + b'"}',
    "deep": b"[" * 70 + b"]" * 70,
    "duplicate-key": b'{"schema_version": "gnd-ilp-clauses/1", "schema_version": "x", "clauses": []}',
    "nan": b'{"schema_version": "gnd-ilp-clauses/1", "clauses": [NaN]}',
    "version": b'{"schema_version": "gnd-ilp-clauses/2", "clauses": []}',
    "long-int": b'{"schema_version": "gnd-ilp-clauses/1", "clauses": [' + b"9" * 5000 + b"]}",
}


@pytest.mark.parametrize("name", sorted(HOSTILE_CLAUSES))
def test_t3_hostile_clause_documents_are_refused(tmp_path, name):
    work = _work(tmp_path)
    clauses = work / f"{name}.clauses.json"
    clauses.write_bytes(HOSTILE_CLAUSES[name])
    out = tmp_path / "out.json"
    result = _import(work, clauses, work / "i1.run.json", out)
    assert result.returncode == 3, result.stderr
    assert not out.exists()


def _clause_doc(*clauses) -> dict:
    return {"schema_version": "gnd-ilp-clauses/1", "clauses": list(clauses)}


ATOM = {"atom": {"predicate": "f_order_amount", "args": [{"var": "A"}, {"var": "B"}, {"var": "C"}]}}
GT = {"compare": {"operator": ">", "left": {"var": "C"}, "right": {"const": 100}}}
HEAD = {"predicate": "wrong", "args": [{"var": "A"}]}


@pytest.mark.parametrize("label", ["clauses-33", "literals-17", "nesting-5"])
def test_t3_clause_bounds(tmp_path, label):
    work = _work(tmp_path)
    if label == "clauses-33":
        document = _clause_doc(*[{"head": HEAD, "body": [ATOM, GT]}] * 33)
    elif label == "literals-17":
        document = _clause_doc({"head": HEAD, "body": [ATOM] * 16 + [GT]})
    else:
        literal: dict = ATOM
        for _ in range(5):
            literal = {"not": literal}
        document = _clause_doc({"head": HEAD, "body": [ATOM, literal]})
    clauses = work / f"{label}.clauses.json"
    clauses.write_text(json.dumps(document))
    result = _import(work, clauses, _bound_run(work, clauses, [[]]), tmp_path / "out.json")
    assert result.returncode == 3, result.stderr


HOSTILE_POPPER = {
    "unknown-character": "wrong(A):- f_order_amount(A,B,C) @ gt_t_amount(C,1).\n",
    "bad-escape": "wrong(A):- f_order_by(A,B,'\\q'),f_order_flagged(A,B).\n",
    "escape-range": "wrong(A):- f_order_by(A,B,'\\x110000\\'),f_order_flagged(A,B).\n",
    "nesting": "wrong(A):- f_order_amount(A,B,C),(((((gt_t_amount(C,1)))))).\n",
    "truncated": "wrong(A):- f_order_amount(A,B,",
    "not-utf8": b"wrong(A):- f_order_by(A,B,'\xff').\n",
}


@pytest.mark.parametrize("name", sorted(HOSTILE_POPPER))
def test_t3_hostile_popper_programs_are_unparsable(tmp_path, name):
    work = _work(tmp_path)
    clauses = work / f"{name}.popper.pl"
    text = HOSTILE_POPPER[name]
    clauses.write_bytes(text if isinstance(text, bytes) else text.encode())
    result = _import(work, clauses, _bound_run(work, clauses, [[]], "popper"),
                     tmp_path / "out.json", "popper")
    assert result.returncode == 3, result.stderr
    assert b"unparsable" in result.stderr


def test_t3_hostile_run_records_are_refused(tmp_path, monkeypatch):
    from gnd.export import ilp_service

    work = _work(tmp_path)
    for name, data in {"duplicate": b'{"schema_version": "gnd-ilp-run/1", "schema_version": 1}',
                       "version": b'{"schema_version": "gnd-ilp-run/2"}'}.items():
        run = work / f"{name}.run.json"
        run.write_bytes(data)
        result = _import(work, work / "i1.clauses.json", run, tmp_path / f"{name}.json")
        assert result.returncode == 3, (name, result.stderr)
    monkeypatch.setattr(ilp_service, "RUN_CAP", 64)
    result = _import(work, work / "i1.clauses.json", work / "i1.run.json", tmp_path / "cap.json")
    assert result.returncode == 3 and b"cap" in result.stderr


def test_t5_outputs_validate_against_their_schemas(tmp_path):
    for target in ("popper", "neutral"):
        tree = CORPUS / ANSWERS["X1" if target == "popper" else "X2"]["tree"]
        for name in ("neutral.json", "export.json"):
            errors = list(_schema("ilp.schema.json").iter_errors(json.loads((tree / name).read_text())))
            assert not errors, (target, name, errors[:1])
    result, _out = _run(tmp_path, BY_ID["I2"])
    assert result.returncode == 0
    assert not list(_schema("ilp-import.schema.json").iter_errors(json.loads(result.stdout)))
    from gnd.export.ilp_popper import parse_program

    parsed = parse_program((CORPUS / "i2.popper.pl").read_text())
    assert not list(_schema("ilp-clauses.schema.json").iter_errors(parsed))


def test_t5_popper_and_neutral_runs_add_the_same_rules(tmp_path):
    first, out1 = _run(tmp_path, BY_ID["I1"])
    second, out2 = _run(tmp_path, BY_ID["I2"])
    assert first.returncode == second.returncode == 0

    def cores(out: Path) -> list[dict]:
        rows = [op["after"] for op in json.loads(out.read_text())["operations"]]
        return [{k: v for k, v in row.items() if k != "provenance"} for row in rows]

    assert cores(out1) == cores(out2)


def test_t9_work_counters_at_the_bounds(tmp_path):
    """7,500 examples (the 1 MiB manifest holds about that many) and 32 clauses."""
    work = _work(tmp_path)
    count = 7500
    populations = [(f"x{i}", "n1.yaml", "negative") for i in range(count)]
    manifest = _manifest_for(work, work / CASES["model"], populations)
    assert manifest.stat().st_size <= 1024 * 1024
    out = tmp_path / "export"
    result = _export(work / CASES["model"], manifest, out, "neutral")
    assert result.returncode == 0, result.stderr
    neutral = json.loads((out / "neutral.json").read_text())
    assert len(neutral["facts"]) == 4 * count
    rule = {"head": HEAD, "body": [ATOM, GT]}
    clauses = work / "near-cap.clauses.json"
    clauses.write_text(json.dumps(_clause_doc(*[rule] * 32)))
    export = hashlib.sha256((out / "export.json").read_bytes()).hexdigest()
    run = work / "near-cap.run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": "popper", "version": "1"},
        "export_sha256": export, "clauses_sha256": _sha(clauses),
        "coverage": [{"clause": k, "covered": [p for p, _n, _c in populations]} for k in range(32)]}))
    result = run_main(["import", "ilp-rules", str(work / CASES["model"]), str(clauses),
                       "--labels", str(manifest), "--reported-coverage", str(run),
                       "--target", "neutral", "--out", str(tmp_path / "near.json"),
                       "--format", "json"])
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    # IK5-Q6 (close): the ceiling adds the K + 2 candidate reloads.
    assert 0 < report["work"]["total"] <= report["work"]["ceiling"] == count * 33 + 34
    assert all(len(row["vacuous"]) == 0 for row in report["clauses"])
    added = json.loads((tmp_path / "near.json").read_text())["operations"][0]["after"]
    induction = added["provenance"]["induction"]
    assert induction["support"] == {"numerator": count, "denominator": count}
    assert len(induction["examples"]) == 256


def test_t9_the_parser_is_linear_on_a_megabyte(tmp_path):
    import time

    from gnd.export.ilp_popper import parse_program

    body = ",".join(f"f_order_amount(A,B{i},C{i})" for i in range(9000))
    text = f"wrong(A):- {body}.\n"
    assert len(text) <= 1024 * 1024
    started = time.perf_counter()
    parsed = parse_program(text)
    assert time.perf_counter() - started < 10
    assert len(parsed["clauses"][0]["body"]) == 9000


def test_t10_validation_order_is_pinned():
    import inspect

    from gnd.export import ilp_service

    source = inspect.getsource(ilp_service._cmd_import_ilp_rules)
    order = ["_read_clauses(", "_read_capped(run_path", "clauses-mismatch", "_prepare(",
             "export-mismatch", "learner-mismatch", "coverage-shape", "rewrite(",
             "_validated(", "score_populations(", "unknown-example", "coverage-mismatch",
             "covers-nothing", 'open("xb")']
    positions = [source.index(token) for token in order]
    assert positions == sorted(positions)
    prepare = inspect.getsource(ilp_service._prepare)
    order = ["read_label_manifest(", "expected-state", "load_model_bytes(", "bind_manifest(",
             "read_population(", "build_neutral(", "export_tree("]
    positions = [prepare.index(token) for token in order]
    assert positions == sorted(positions)


def test_t10_exits_for_missing_inputs_links_and_usage(tmp_path):
    work = _work(tmp_path)
    clauses, run = work / "i1.clauses.json", work / "i1.run.json"
    for missing in ("model", "clauses", "run"):
        argv = ["import", "ilp-rules", str(work / CASES["model"]), str(clauses), "--labels",
                str(work / "m.labels.json"), "--reported-coverage", str(run), "--target",
                "neutral", "--out", str(tmp_path / "out.json")]
        argv[{"model": 2, "clauses": 3, "run": 7}[missing]] = str(tmp_path / "absent")
        assert run_main(argv).returncode == 66, missing
    (tmp_path / "target.json").write_text("{}")
    (tmp_path / "link.json").symlink_to(tmp_path / "target.json")
    assert _import(work, clauses, run, tmp_path / "link.json").returncode == 74
    (tmp_path / "linkdir").symlink_to(tmp_path)
    assert _export(work / CASES["model"], work / "m.labels.json", tmp_path / "linkdir").returncode == 74
    usage = run_main(["export", "ilp", str(work / CASES["model"]), "--labels",
                      str(work / "m.labels.json"), "--out", str(tmp_path / "x")])
    assert usage.returncode == 64
    assert _export(tmp_path / "absent.orm.yaml", work / "m.labels.json",
                   tmp_path / "y").returncode == 66


def test_t12_imports_are_deterministic(tmp_path):
    work = _work(tmp_path)
    outputs = []
    for attempt in ("a", "b"):
        out = tmp_path / f"{attempt}.json"
        result = _import(work, work / "i1.clauses.json", work / "i1.run.json", out, "neutral",
                         "--requested-at", "2026-10-26T00:00:00+00:00")
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        report["proposal"] = None
        outputs.append((out.read_bytes(), report))
    assert outputs[0] == outputs[1]


def test_c_f1_unchecked_and_fail_branches():
    from gnd.export.ilp_service import coverage

    seen = coverage([{"ref": "r", "verdict": v} for v in ("warning", "pass", "vacuous", "unchecked")],
                    ["a", "b", "c", "d"])
    assert seen == {"covered": ["a"], "vacuous": ["c"], "unchecked": ["d"]}
    with pytest.raises(RuntimeError):
        coverage([{"ref": "r", "verdict": "fail"}], ["a"])


def test_c_f1_a_fail_verdict_is_exit_70(tmp_path, monkeypatch):
    from gnd.export import ilp_service

    def broken(verdicts, ids):
        raise RuntimeError("seeded: a deontic constraint drew fail")

    monkeypatch.setattr(ilp_service, "coverage", broken)
    work = _work(tmp_path)
    out = tmp_path / "out.json"
    result = _import(work, work / "i1.clauses.json", work / "i1.run.json", out)
    assert result.returncode == 70, result.stderr
    assert not out.exists()


# ---------------------------------------------------------------------------
# Review regressions (notes/phase-IK5-agent-review.md, R1-R8). Each fails on
# the pre-fix source at abc872a unless marked as coverage.
# ---------------------------------------------------------------------------


def _popper_import(tmp_path: Path, text: str | bytes):
    work = _work(tmp_path)
    clauses = work / "review.popper.pl"
    clauses.write_bytes(text if isinstance(text, bytes) else text.encode())
    out = tmp_path / "review.json"
    return _import(work, clauses, _bound_run(work, clauses, [[]], "popper"), out, "popper"), out


def test_r1_nested_aggregates_are_bounded(tmp_path):
    goal = "count(" * 300 + "f_order_flagged(A,B)" + ")" * 300
    result, out = _popper_import(tmp_path, f"wrong(A):- f_order_amount(A,B,C),{goal}.\n")
    assert result.returncode == 3, result.stderr
    assert b"unparsable" in result.stderr and not out.exists()


def test_r2_a_huge_integer_is_unparsable(tmp_path):
    result, out = _popper_import(tmp_path, f"wrong(A):- f_order_amount(A,B,C),C > {'1' * 4301}.\n")
    assert result.returncode == 3, result.stderr
    assert b"unparsable" in result.stderr and not out.exists()


@pytest.mark.parametrize("value", ["\ud800", "\u0085x", "x\u007f", "a b", "tab\there"])
def test_r3_r4_constants_yaml_would_not_keep_are_refused(tmp_path, value):
    """R3: a lone surrogate was a traceback; R4: NEL and friends were admitted
    although evolve's YAML reader then saw a different constant."""
    work = _work(tmp_path)
    clause = {"head": HEAD, "body": [
        {"atom": {"predicate": "f_order_by", "args": [{"var": "A"}, {"var": "B"}, {"var": "C"}]}},
        {"atom": {"predicate": "f_customer_blocked", "args": [{"var": "A"}, {"const": value}]}}]}
    clauses = work / "r4.clauses.json"
    clauses.write_text(json.dumps(_clause_doc(clause)), encoding="utf-8")
    out = tmp_path / "r4.json"
    result = _import(work, clauses, _bound_run(work, clauses, [[]]), out)
    assert result.returncode == 3, result.stderr
    assert b"constant-spelling" in result.stderr and not out.exists()


def test_r6_the_export_reports_its_work(tmp_path):
    work = _work(tmp_path)
    result = _export(work / CASES["model"], work / "m.labels.json", tmp_path / "out")
    assert result.returncode == 0
    assert b"work 27 (ceiling 500006)" in result.stdout  # 6 populations + 21 facts


def test_r6_import_counts_one_read_per_population_and_clause(tmp_path):
    """Coverage: the arithmetic form also gave 18; the read is now counted."""
    result, _out = _run(tmp_path, BY_ID["I1"])
    work = json.loads(result.stdout)["work"]
    assert (work["checks"], work["verdicts"], work["reloads"], work["ceiling"]) == (6, 18, 5, 29)


def test_r7_quoted_atoms_round_trip(tmp_path):
    from gnd.export.ilp_popper import parse_program, quote

    for value in ["it's", "back\\slash", "c\u0001'\\x", "line\nbreak", "é ü"]:
        parsed = parse_program(f"wrong(A):- f_order_by(A,B,{quote(value)}).\n")
        assert parsed["clauses"][0]["body"][0]["atom"]["args"][2] == {"const": value}
    assert quote("a'b\\c") == "'a\\'b\\\\c'"


def test_r8_an_anonymous_variable_is_never_ground(tmp_path):
    result, out = _popper_import(tmp_path, "wrong(A):- f_order_amount(A,B,C),f_order_by(A,B,_).\n")
    assert result.returncode == 3, result.stderr
    assert b"non-ground-absence" in result.stderr and not out.exists()


# R5: the rewrite's semantics, pinned operator by operator (mutation coverage).

def _rewrite_one(text: str, neutral: dict | None = None, columns: dict | None = None) -> dict:
    from gnd.export import ilp
    from gnd.export.ilp_popper import parse_program
    from gnd.export.ilp_rewrite import rewrite
    from gnd.model import load_model

    if neutral is None:
        shape, columns = ilp.schema(load_model(CORPUS / CASES["model"]), frozenset())
        neutral = shape
    return rewrite(parse_program(text)["clauses"][0], 0, neutral, columns)


@pytest.mark.parametrize(("literal", "operator", "left", "right"), [
    ("C > 100", "<=", "$v_c", 100), ("C < 100", ">=", "$v_c", 100),
    ("C >= 100", "<", "$v_c", 100), ("C =< 100", ">", "$v_c", 100),
    ("C = 100", "!=", "$v_c", 100), ("C =:= 100", "!=", "$v_c", 100),
    ("C \\= 100", "=", "$v_c", 100), ("C =\\= 100", "=", "$v_c", 100),
    ("100 < C", ">=", 100, "$v_c"), ("C > -5", "<=", "$v_c", -5),
    ("gt_t_amount(C,100)", "<=", "$v_c", 100), ("lt_t_amount(100,C)", ">=", 100, "$v_c"),
    ("ge_t_amount(C,7)", "<", "$v_c", 7), ("le_t_amount(C,7)", ">", "$v_c", 7),
])
def test_r5_every_operator_is_negated_exactly(literal, operator, left, right):
    core = _rewrite_one(f"wrong(A):- f_order_amount(A,B,C),{literal}.\n")
    assert core["consequent"] == {"comparison": {"operator": operator, "left": left, "right": right}}


def test_r5_variable_spelling_is_injective():
    from gnd.export.ilp_rewrite import variable

    spellings = {name: variable(name) for name in ("B", "Ab", "AB", "A_b", "_G1", "Bc", "BC")}
    assert spellings["B"] == "$v_b" and spellings["Ab"] == "$v_a_b" and spellings["AB"] == "$v_ab"
    assert len(set(spellings.values())) == len(spellings)
    core = _rewrite_one("wrong(A):- f_order_amount(A,Bc,BC),gt_t_amount(BC,1).\n")
    assert core["antecedent"][0]["bind"] == {"order": "$v_b_c", "amount": "$v_bc"}


def test_r5_each_anonymous_variable_is_fresh():
    core = _rewrite_one("wrong(A):- f_order_amount(A,B,C),f_order_by(A,B,_),f_order_by(A,B,_),"
                        "gt_t_amount(C,1).\n")
    customers = [item["bind"]["customer"] for item in core["antecedent"][1:]]
    assert customers == ["$anon1", "$anon2"]


@pytest.mark.parametrize(("text", "refusal"), [
    ("wrong(A):- f_order_amount(A,B,C),gt_t_amount(A,1).\n", "example-variable"),
    ("wrong(A):- f_order_amount(A,B,C),gt_t_amount(C).\n", "arity"),
])
def test_r5_comparison_refusals(text, refusal):
    from gnd.export.ilp import IlpError

    with pytest.raises(IlpError, match=refusal):
        _rewrite_one(text)


def test_r5_the_last_qualifying_atom_is_designated():
    core = _rewrite_one("wrong(A):- f_order_by(A,B,C),f_order_flagged(A,B),f_customer_blocked(A,C).\n")
    assert core["consequent"] == {"absence": {"fact_type": "customer_blocked",
                                              "bind": {"customer": "$v_c"}}}
    assert [item["fact_type"] for item in core["antecedent"]] == ["order_by", "order_flagged"]


def test_r5_boolean_atoms_become_booleans_at_boolean_roles():
    from gnd.export.ilp import Column

    neutral = {"comparisons": [], "types": [
        {"name": "t_order", "object_type": "order", "primitive": None},
        {"name": "t_flag", "object_type": "flag", "primitive": "boolean"},
        {"name": "t_note", "object_type": "note", "primitive": "string"}]}
    columns = {
        "f_order_note": Column("order_note", ("order", "note"), ("ex", "t_order", "t_note")),
        "f_order_paid": Column("order_paid", ("order", "paid"), ("ex", "t_order", "t_flag")),
    }
    core = _rewrite_one("wrong(A):- f_order_note(A,B,true),f_order_paid(A,B,true).\n",
                        neutral, columns)
    assert core["antecedent"][0]["bind"]["note"] == "true"
    assert core["consequent"]["absence"]["bind"]["paid"] is True


def test_r5_facts_are_sorted_by_their_canonical_values(tmp_path):
    work = _work(tmp_path)
    text = (work / "pops" / "n1.yaml").read_text()
    shuffled = text.replace("    - { order: 1, amount: 50 }\n    - { order: 2, amount: 150 }\n",
                            "    - { order: 2, amount: 150 }\n    - { order: 1, amount: 50 }\n")
    assert shuffled != text
    (work / "pops" / "shuffled.yaml").write_text(shuffled)
    manifest = _manifest_for(work, work / CASES["model"], [("n1", "shuffled.yaml", "negative")])
    out = tmp_path / "out"
    assert _export(work / CASES["model"], manifest, out, "neutral").returncode == 0
    facts = json.loads((out / "neutral.json").read_text())["facts"]
    assert [f["values"] for f in facts if f["predicate"] == "f_order_amount"] == [[1, 50], [2, 150]]


def test_r7_prolog_escapes_are_read():
    from gnd.export.ilp_popper import parse_program

    parsed = parse_program("wrong(A):- f_order_by(A,B,'a\\nb\\tc\\\\d\\'e\\x41\\').\n")
    assert parsed["clauses"][0]["body"][0]["atom"]["args"][2] == {"const": "a\nb\tc\\d'eA"}


# Amendment IK5-Q1 (owner ruling 2026-10-26): both export bounds can refuse
# with their real values, no monkeypatch.

def _hundred_fact_population(work: Path) -> str:
    orders = list(range(1, 51))
    rows = "".join(f"    - {{ order: {o}, amount: {o} }}\n" for o in orders)
    owners = "".join(f"    - {{ order: {o}, customer: \"c1\" }}\n" for o in orders)
    text = ("format_version: 2\npopulation:\n  model: orders.orm.yaml\n  source: fixture\n"
            "  covers: [order_by, order_amount, order_flagged, customer_blocked]\n"
            f"instances:\n  order: {orders}\n  customer: [\"c1\"]\nfacts:\n"
            f"  order_by:\n{owners}  order_amount:\n{rows}"
            "  order_flagged: []\n  customer_blocked: []\n")
    (work / "pops" / "hundred.yaml").write_text(text)
    return "hundred.yaml"


@pytest.mark.parametrize(("copies", "cause"), [
    (5001, b"exceeds 500000 facts"),      # 500,100 facts: the facts bound refuses
    (4800, b"would exceed 67108864 bytes"),  # 480,000 wide facts: under it, but neutral.json is too big
])
def test_q1_each_export_bound_refuses_at_its_real_value(tmp_path, copies, cause):
    from gnd.export import ilp

    assert ilp.MAX_FACTS == 500_000 and ilp.MAX_FILE_BYTES == 64 * 1024 * 1024
    work = _work(tmp_path)
    name = _hundred_fact_population(work)
    manifest = _manifest_for(work, work / CASES["model"],
                             [(f"x{i:039d}" if copies == 4800 else f"x{i}", name, "negative")
                              for i in range(copies)])
    assert manifest.stat().st_size <= 1024 * 1024
    out = tmp_path / "out"
    result = _export(work / CASES["model"], manifest, out, "neutral")
    assert result.returncode == 3, result.stderr
    assert b"too-large" in result.stderr and cause in result.stderr, result.stderr
    assert not out.exists()
