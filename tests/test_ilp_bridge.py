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
    assert 0 < report["work"]["total"] <= report["work"]["ceiling"] == count * 33
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
