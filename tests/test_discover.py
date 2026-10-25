"""IK4: constraint discovery, ``gnd discover`` (induced-knowledge milestone).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-spec.md. Under
IK4-D1 the cases are an owner-approved corpus: inputs in
tests/fixtures/induced_knowledge/ik4-corpus/cases.json, hand-written answers in
expected.json, and stories in that directory's README.md.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik4-corpus"
CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))["cases"]
ENVELOPE = {"source", "status", "modality", "provenance"}
POPULATION_CAP = 10 * 1024 * 1024


def _generated(kind: str, header_from: Path) -> str:
    header = header_from.read_text(encoding="utf-8").split("instances:")[0]
    if kind == "over-cap":
        rows = "".join(f'    - {{ person: {i}, team: "A" }}\n' for i in range(400_000))
        return header + "instances: {}\nfacts:\n  person_in_team:\n" + rows
    # JSON, not YAML: GND caps a YAML population at 1,000,000 parse events,
    # which a near-10-MiB file of small rows exceeds (IK4 finding F1).
    recipe = CASES["generated"]["near-cap"]
    people = recipe["persons"]
    document = {
        "population": {
            "model": "staff.orm.yaml",
            "source": "fixture",
            "covers": ["person_in_team", "person_has_grade", "team_led_by", "person_has_skill"],
        },
        "instances": {},
        "facts": {
            "person_in_team": [{"person": i, "team": f"T{i % 200}"} for i in range(people)],
            "person_has_grade": [{"person": i, "grade": f"g{i % 5}"} for i in range(people)],
            "team_led_by": [{"team": f"T{t}", "leader": t} for t in range(200)],
            "person_has_skill": [
                {"person": i, "skill": f"s{(i + j) % 50}"} for i in range(people) for j in range(2)
            ],
        },
    }
    return json.dumps(document, separators=(", ", ": "))


def _prepare(tmp_path: Path, case: dict[str, Any]) -> tuple[list[str], Path, Path, Path]:
    model = tmp_path / case["model"]
    shutil.copyfile(CORPUS / case["model"], model)
    population_name = case["population"]
    if population_name.startswith("GENERATED:"):
        kind = population_name.split(":", 1)[1]
        suffix = "json" if kind == "near-cap" else "yaml"
        population = tmp_path / f"{kind}.population.{suffix}"
        population.write_text(
            _generated(kind, CORPUS / "staff.population.yaml"), encoding="utf-8"
        )
    else:
        population = tmp_path / population_name
        if (CORPUS / population_name).exists():
            shutil.copyfile(CORPUS / population_name, population)
    out = tmp_path / "proposal.json"
    report = tmp_path / "report.json"
    if case.get("out_is_symlink"):
        target = tmp_path / "elsewhere.json"
        target.write_text("{}\n", encoding="utf-8")
        out.symlink_to(target)
    common = list(CASES["common_argv"])
    for flag in case.get("omit", []):
        index = common.index(flag)
        del common[index : index + 2]
    argv = [
        "discover", str(model), str(population), *common, *case["argv"],
        "--out", str(out), "--report", str(report),
    ]
    return argv, model, out, report


def _host(ref: str) -> str | None:
    if ref.startswith("fact_types["):
        return ref[len("fact_types[") : ref.index("]")]
    return None


def _core(constraint: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in constraint.items() if key not in ENVELOPE}


def _emitted(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "family": row["family"],
            "host": _host(row["ref"]),
            "constraint": _core(row["constraint"]),
            "support": row["support"],
            "examples": row["constraint"]["provenance"]["induction"]["examples"],
        }
        for row in report["emitted"]
    ]


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_ik4_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = EXPECTED[case["id"]]
    argv, model, out, report_path = _prepare(tmp_path, case)
    result = run_main(argv)
    output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    assert result.returncode == answer["exit"], output
    if answer["exit"] != 0:
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    emitted = _emitted(report)
    for row in emitted:
        support = row.pop("support")
        assert support["numerator"] == support["denominator"] > 0, row
        row["support"] = support["numerator"]
    if "emitted" in answer:
        expected = answer["emitted"]
        shown = [
            {key: value for key, value in row.items() if key != "examples" or "examples" in want}
            for row, want in zip(emitted, expected, strict=False)
        ]
        assert len(emitted) == len(expected)
        assert shown == expected
    for row in answer.get("present", []):
        assert {k: v for k, v in emitted[[e["constraint"] for e in emitted].index(row["constraint"])].items() if k != "examples"} == row
    for row in answer.get("absent", []):
        assert {"host": row["host"], "constraint": row["constraint"]} not in [
            {"host": e["host"], "constraint": e["constraint"]} for e in emitted
        ]
    if "rejected" in answer:
        assert report["rejected"] == answer["rejected"]
    if "suppressed" in answer:
        assert {k: v for k, v in report["suppressed"].items() if v} == answer["suppressed"]
    for key, value in answer.get("skipped", {}).items():
        skipped = report["skipped"][key]
        assert (sum(skipped.values()) if isinstance(skipped, dict) else skipped) == value
    for key, value in answer.get("bounds", {}).items():
        assert report["bounds"][key] == value
    if "near_misses" in answer:
        assert [
            {"family": row["family"], "host": row["host"], "constraint": _core(row["constraint"]),
             "violations": row["violations"], "subjects": row["subjects"],
             "counterexamples": row["counterexamples"]}
            for row in report["near_misses"]
        ] == answer["near_misses"]
    assert out.exists() is answer["proposal"]
    assert (report["proposal"] is not None) is answer["proposal"]
    if "work_ceiling" in answer:
        population = Path(argv[2])
        assert population.stat().st_size <= answer["population_bytes_max"]
        assert 0 < report["work"]["total"] <= answer["work_ceiling"]
    if answer.get("preview_exit") is not None:
        preview = run_main([
            "evolve", "preview", str(model), str(out), "--workspace", str(tmp_path),
            "--records", str(tmp_path / "records"), "--out", str(tmp_path / "preview.json"),
        ])
        assert preview.returncode == answer["preview_exit"], preview.stdout + preview.stderr
    if answer.get("deterministic"):
        first = (out.read_bytes(), report_path.read_bytes())
        for seed in ("1", "2"):
            out.unlink()
            subprocess.run(
                [sys.executable, "-m", "gnd", *argv], check=True, cwd=REPO_ROOT,
                env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True,
            )
            assert (out.read_bytes(), report_path.read_bytes()) == first


def test_answer_key_covers_every_case() -> None:
    assert set(EXPECTED) == {case["id"] for case in CASES["cases"]}


# ---- implementation tests (spec section 8: T3-T5, T10, T11) -----------------

DISCOVERY_CASES = [c for c in CASES["cases"] if c["id"].startswith("K")]


def _run(tmp_path: Path, case_id: str) -> tuple[Path, Path, Path, Path, int]:
    case = next(c for c in CASES["cases"] if c["id"] == case_id)
    argv, model, out, report = _prepare(tmp_path, case)
    result = run_main(argv)
    return model, Path(argv[2]), out, report, result.returncode


def _assert_emitted_pass(model: Path, population: Path, proposal: dict[str, Any], refs: list[str]) -> None:
    """T3's assertion: every emitted ref passes ``gnd check`` on the proposed model."""
    from gnd.checker import check
    from gnd.model import load_model_bytes
    from gnd.population import load_population_bytes

    candidate = load_model_bytes(
        proposal["candidate_model"]["text"].encode("utf-8"), source=model
    )
    checked = check(candidate, load_population_bytes(population.read_bytes(), source=population,
                                                     model=candidate))
    verdicts = {v.constraint_ref: v.verdict for v in checked.verdicts}
    for ref in refs:
        assert verdicts[ref] == "pass", (ref, verdicts[ref])


@pytest.mark.parametrize(
    "case_id", [c["id"] for c in DISCOVERY_CASES if EXPECTED[c["id"]].get("proposal")]
)
def test_t3_every_emitted_ref_passes_check(tmp_path: Path, case_id: str) -> None:
    model, population, out, report_path, code = _run(tmp_path, case_id)
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    proposal = json.loads(out.read_text(encoding="utf-8"))
    _assert_emitted_pass(model, population, proposal, [row["ref"] for row in report["emitted"]])
    assert all(row["support"]["numerator"] > 0 for row in report["emitted"])


def test_t4_a_wrong_discoverer_fails_the_t3_assertion(tmp_path: Path) -> None:
    # A discoverer that keeps `warning` emits a violated deontic candidate:
    # uniqueness on person_in_team.team (team A holds three people).
    model, population, out, _, code = _run(tmp_path, "K01")
    assert code == 0
    proposal = json.loads(out.read_text(encoding="utf-8"))
    document = json.loads(proposal["candidate_model"]["text"])
    host = next(ft for ft in document["fact_types"] if ft["id"] == "person_in_team")
    wrong = json.loads(json.dumps(host["constraints"][0]))
    wrong["roles"] = ["team"]
    host["constraints"].append(wrong)
    proposal["candidate_model"]["text"] = json.dumps(document)
    ref = f"fact_types[person_in_team].constraints[{len(host['constraints']) - 1}]"
    with pytest.raises(AssertionError):
        _assert_emitted_pass(model, population, proposal, [ref])


def test_t4_discovery_refuses_a_pass_it_counted_violations_for(tmp_path: Path, monkeypatch) -> None:
    # Defense in depth: a checker that passed a candidate discovery saw violated
    # is an internal defect (exit 70), never a silent emission.
    from gnd.discover import service

    real = service.check

    def lenient(model, population):
        report = real(model, population)
        for verdict in report.verdicts:
            if verdict.verdict == "warning":
                object.__setattr__(verdict, "verdict", "pass")
        return report

    monkeypatch.setattr(service, "check", lenient)
    *_, code = _run(tmp_path, "K01")
    assert code == 70


def _oracle_support(population: dict[str, Any], model: dict[str, Any], row: dict[str, Any]) -> int:
    """Brute force, from the raw documents only (T5)."""
    facts = population["facts"]
    constraint = row["constraint"]
    family = row["family"]
    host = row["ref"].split("[", 1)[1].split("]", 1)[0] if row["ref"].startswith("fact_types[") else None

    def column(ft: str, role: str) -> list[str]:
        return [json.dumps(f[role]) for f in facts.get(ft, []) if role in f]

    if family == "uniqueness":
        return len({tuple(json.dumps(f[r]) for r in constraint["roles"])
                    for f in facts[host] if all(r in f for r in constraint["roles"])})
    if family == "frequency":
        return len(set(column(host, constraint["roles"][0])))
    if family == "value":
        return len(column(host, constraint["role_ref"]["role"]))
    if family == "mandatory":
        types = {(ft["id"], r["role_name"]): r["object_type"]
                 for ft in model["fact_types"] for r in ft["roles"]}
        target = types[(host, constraint["role"])]
        denoting = [o["id"] for o in model["object_types"]
                    if (o.get("reference") or {}).get("value_type") == target]
        roster = {json.dumps(v) for ot in [target, *denoting]
                  for v in (population.get("instances") or {}).get(ot, [])}
        roster |= {json.dumps(f[role]) for (ft, role), ot in types.items()
                   if ot in (target, *denoting) for f in facts.get(ft, []) if role in f}
        return len(roster)
    sides = [(s["fact_type"], s["role"]) for key in ("subset_role_seq", "role_seq_a")
             if key in constraint for s in constraint[key]]
    others = [(s["fact_type"], s["role"]) for key in ("superset_role_seq", "role_seq_b")
              if key in constraint for s in constraint[key]]
    a, b = set(column(*sides[0])), set(column(*others[0]))
    return len(a) if family == "subset" else len(a | b)


@pytest.mark.parametrize("case_id", ["K01", "K02", "K03", "K05", "K06", "K08"])
def test_t5_support_equals_an_independent_oracle(tmp_path: Path, case_id: str) -> None:
    from ruamel.yaml import YAML

    model, population, _, report_path, code = _run(tmp_path, case_id)
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    raw_model = YAML(typ="safe").load(model.read_text(encoding="utf-8"))
    raw_population = YAML(typ="safe").load(population.read_text(encoding="utf-8"))
    assert report["emitted"]
    for row in report["emitted"]:
        assert row["support"]["denominator"] == _oracle_support(raw_population, raw_model, row), row


def test_t10_validation_order_is_pinned_in_source() -> None:
    import inspect

    from gnd.discover import service

    source = inspect.getsource(service.discover)
    steps = ["load_model(", "load_population(", "generate(", "catalogue.rule(", "check(",
             "redundancy("]
    positions = [source.index(step) for step in steps]
    assert positions == sorted(positions)


@pytest.mark.parametrize("case_id", ["K08", "K10", "K13"])
def test_t11_report_validates_against_its_schema(tmp_path: Path, case_id: str) -> None:
    from jsonschema import Draft202012Validator

    schema = json.loads((REPO_ROOT / "src/gnd/discover.schema.json").read_text(encoding="utf-8"))
    *_, report_path, code = _run(tmp_path, case_id)
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(report)) == []
    broken = {**report, "unexpected": 1}
    assert list(Draft202012Validator(schema).iter_errors(broken))
