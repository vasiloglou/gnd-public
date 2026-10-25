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
    steps = ["load_model_bytes(", "load_population_bytes(", "generate(", "catalogue.rule(",
             "check(", "redundancy("]
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


# ---- adversarial-review regressions (notes/phase-IK4-agent-review.md) -------
# Successor cases beside the approved corpus: new inputs, no changed answers.

AMOUNT_MODEL = """version: 1
model_id: r1
source: {kind: fixture}
object_types:
  - {id: amount, name: Amount, kind: value, primitive: Number}
  - {id: tag, name: Tag, kind: value, primitive: String}
fact_types:
  - id: a_tagged
    reading: "{Amount} is tagged {Tag}"
    roles:
      - {object_type: amount, role_name: amount}
      - {object_type: tag, role_name: tag}
  - id: a_flagged
    reading: "{Amount} is flagged {Tag}"
    roles:
      - {object_type: amount, role_name: amount}
      - {object_type: tag, role_name: tag}
constraints: []
"""


def _discover(tmp_path: Path, model: str, population: str, *extra: str,
              model_name: str = "m.orm.yaml") -> tuple[int, str, Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / model_name).write_text(model, encoding="utf-8")
    (tmp_path / "p.population.yaml").write_text(population, encoding="utf-8")
    out, report = tmp_path / "proposal.json", tmp_path / "report.json"
    result = run_main([
        "discover", str(tmp_path / model_name), str(tmp_path / "p.population.yaml"),
        *CASES["common_argv"], *extra, "--out", str(out), "--report", str(report),
    ])
    text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    return result.returncode, text, out, report


def _amount_population(cells: list[tuple[str, Any]], *, header: str = "") -> str:
    rows = {"a_tagged": [], "a_flagged": []}
    for fact_type, amount in cells:
        rows[fact_type].append(amount)
    lines = [header + "population: {model: m.orm.yaml, source: fixture, covers: [a_tagged, a_flagged]}",
             "instances: {}", "facts:"]
    for fact_type, amounts in rows.items():
        lines.append(f"  {fact_type}:")
        for i, amount in enumerate(amounts):
            lines.append(f"    - {{amount: {amount}, tag: {'xy'[i % 2]}}}")
    return "\n".join(lines) + "\n"


def test_r1_typed_identity_matches_the_checker(tmp_path: Path) -> None:
    # 1 and 1.0 are one Number value to `gnd check`, so to discovery too.
    population = _amount_population(
        [("a_tagged", "1"), ("a_tagged", "2"), ("a_flagged", "1.0"), ("a_flagged", "2")]
    )
    code, text, _, report_path = _discover(tmp_path, AMOUNT_MODEL, population)
    assert code == 0, text
    report = json.loads(report_path.read_text(encoding="utf-8"))
    families = {row["family"] for row in report["emitted"]}
    # The two amount columns are one set, so the equality is emitted and
    # absorbs both subsets (redundancy rule 1).
    assert "equality" in families
    assert report["suppressed"]["redundant-subset"] >= 2
    one_column = _amount_population(
        [("a_tagged", "1"), ("a_tagged", "1.0"), ("a_flagged", "2"), ("a_flagged", "3")]
    )
    code, text, _, report_path = _discover(tmp_path / "b", AMOUNT_MODEL, one_column,
                                           "--families", "value,uniqueness")
    assert code == 0, text
    report = json.loads(report_path.read_text(encoding="utf-8"))
    allowed = [row["constraint"]["allowed"] for row in report["emitted"]
               if row["family"] == "value" and row["ref"].startswith("fact_types[a_tagged]")
               and row["constraint"]["object_type"] == "amount"]
    assert allowed == [[1]]
    assert not any(row["family"] == "uniqueness" and row["constraint"]["roles"] == ["amount"]
                   and row["ref"].startswith("fact_types[a_tagged]") for row in report["emitted"])


def test_r2_opaque_cells_skip_value_candidates_and_never_leak(tmp_path: Path) -> None:
    population = _amount_population(
        [("a_tagged", '{"$opaque": "SECRET-OPAQUE-CANARY"}'), ("a_tagged", "2"), ("a_flagged", "2")],
        header="format_version: 2\n",
    )
    code, text, out, report_path = _discover(tmp_path, AMOUNT_MODEL, population)
    assert code == 0, text
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["skipped"]["unrepresentable_value_roles"] >= 1
    written = text + report_path.read_text() + (out.read_text() if out.exists() else "")
    assert "SECRET-OPAQUE-CANARY" not in written


def test_r2_repository_opaque_fixture_exits_0_without_canaries(tmp_path: Path) -> None:
    base = REPO_ROOT / "tests/fixtures/v70-phase5"
    for name in ("private.orm.yaml", "private.pop.json"):
        shutil.copyfile(base / name, tmp_path / name)
    out, report = tmp_path / "proposal.json", tmp_path / "report.json"
    result = run_main(["discover", str(tmp_path / "private.orm.yaml"), str(tmp_path / "private.pop.json"),
                       *CASES["common_argv"], "--out", str(out), "--report", str(report)])
    written = (result.stdout + result.stderr).decode() + report.read_text()
    written += out.read_text() if out.exists() else ""
    assert result.returncode == 0, written
    assert "SECRET-ROLE-CANARY" not in written and "SECRET-OPAQUE-CANARY" not in written


def test_r3_reference_bearing_models_bind_their_references(tmp_path: Path) -> None:
    shutil.copytree(REPO_ROOT / "src/gnd/examples/dispatch", tmp_path / "dispatch")
    root = tmp_path / "dispatch"
    out, report = tmp_path / "proposal.json", tmp_path / "report.json"
    result = run_main(["discover", str(root / "model.orm.json"), str(root / "seed.pop.json"),
                       *CASES["common_argv"], "--out", str(out), "--report", str(report)])
    assert result.returncode == 0, (result.stdout + result.stderr).decode()
    if out.exists():
        _assert_emitted_pass_bound(root / "model.orm.json", root / "seed.pop.json", out, report)


def _assert_emitted_pass_bound(model: Path, population: Path, out: Path, report: Path) -> None:
    from gnd.discover import service

    rows = json.loads(report.read_text(encoding="utf-8"))["emitted"]
    proposal = json.loads(out.read_text(encoding="utf-8"))
    from gnd.checker import check
    from gnd.model import load_model_bytes
    from gnd.population import load_population_bytes

    candidate = load_model_bytes(proposal["candidate_model"]["text"].encode(), source=model)
    bound, references = service._bind_references(
        candidate, load_population_bytes(population.read_bytes(), source=population,
                                         model=candidate), model.parent)
    verdicts = {v.constraint_ref: v.verdict for v in check(candidate, bound,
                                                           references=references).verdicts}
    assert all(verdicts[row["ref"]] == "pass" for row in rows)


@pytest.mark.parametrize(("model", "population"), [
    ("v62-phase1/models/static.orm.yaml", "v62-phase1/populations/pre-clean.pop.yaml"),
    ("v62-phase5/models/floats.orm.yaml", "v62-phase5/populations/float-clean.pop.yaml"),
])
def test_r4_derived_rosters_never_crash(tmp_path: Path, model: str, population: str) -> None:
    base = REPO_ROOT / "tests/fixtures"
    out, report = tmp_path / "proposal.json", tmp_path / "report.json"
    result = run_main(["discover", str(base / model), str(base / population),
                       *CASES["common_argv"], "--out", str(out), "--report", str(report)])
    assert result.returncode == 0, (result.stdout + result.stderr).decode()[-400:]
    assert json.loads(report.read_text())["skipped"]["derived_mandatory_roles"] >= 1


def test_r5_redacted_roles_never_emit_their_values(tmp_path: Path) -> None:
    base = REPO_ROOT / "tests/fixtures/v62-phase1"
    out, report = tmp_path / "proposal.json", tmp_path / "report.json"
    result = run_main(["discover", str(base / "models/static.orm.yaml"),
                       str(base / "populations/pre-clean.pop.yaml"), *CASES["common_argv"],
                       "--families", "value", "--out", str(out), "--report", str(report)])
    written = (result.stdout + result.stderr).decode() + report.read_text()
    written += out.read_text() if out.exists() else ""
    assert result.returncode == 0
    assert "SECRET-ITEM-314159" not in written
    assert json.loads(report.read_text())["skipped"]["redacted_value_roles"] >= 1


def test_r6_candidates_past_the_size_budget_are_skipped_and_counted(tmp_path: Path) -> None:
    tags = [("a_tagged", "1") for _ in range(20)] + [("a_flagged", "1")]
    population = _amount_population(tags)
    big = "\\\\" * 150_000
    population = population.replace("tag: x", f'tag: "x{big}"').replace("tag: y", f'tag: "y{big}"')
    population = "\n".join(
        line.replace(f'"x{big}"', f'"x{i}{big}"') for i, line in enumerate(population.splitlines())
    ) + "\n"
    code, text, _, report_path = _discover(tmp_path, AMOUNT_MODEL, population, "--families", "value")
    assert code == 0, text[-400:]
    assert json.loads(report_path.read_text())["skipped"]["over_budget"] >= 1


def test_r7_yaml_only_model_values_round_trip(tmp_path: Path) -> None:
    # `gnd evolve preview` itself cannot preview a model holding a YAML date
    # (pre-existing, IK4 finding F12); discovery's candidate must still equal
    # evolve's replay of its operations, which is what preview would compare.
    from gnd.evolve import EvolutionProposal
    from gnd.evolve.service import _apply_declared_operations, _parse_model_text

    model = (CORPUS / "staff.orm.yaml").read_text().replace(
        "source:\n  kind: fixture", "source:\n  kind: fixture\n  created: 2024-01-01")
    code, text, out, _ = _discover(tmp_path, model, (CORPUS / "staff.population.yaml").read_text(),
                                   "--families", "uniqueness", model_name="staff.orm.yaml")
    assert code == 0, text
    proposal = EvolutionProposal.model_validate(json.loads(out.read_text()))
    replayed = _apply_declared_operations(_parse_model_text(model), proposal.operations)
    assert replayed == _parse_model_text(proposal.candidate_model.text)


@pytest.mark.parametrize("actor", ["", "   "])
def test_r8_blank_actor_is_a_usage_error(tmp_path: Path, actor: str) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "K01")
    argv, *_ = _prepare(tmp_path, case)
    argv[argv.index("--actor") + 1] = actor
    assert run_main(argv).returncode == 64


@pytest.mark.parametrize("target", ["report", "model", "population"])
def test_r9_outputs_must_not_alias_each_other_or_an_input(tmp_path: Path, target: str) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "K01")
    argv, model, _, report = _prepare(tmp_path, case)
    before = model.read_bytes()
    aliased = {"report": report, "model": model, "population": Path(argv[2])}[target]
    argv[argv.index("--out") + 1] = str(aliased)
    assert run_main(argv).returncode == 64
    assert model.read_bytes() == before


def test_r10_inputs_are_read_once_through_the_cap(tmp_path: Path, monkeypatch) -> None:
    from gnd.discover import service

    reads: list[Path] = []
    real = Path.read_bytes

    def counted(self: Path) -> bytes:
        reads.append(self)
        return real(self)

    monkeypatch.setattr(Path, "read_bytes", counted)
    case = next(c for c in CASES["cases"] if c["id"] == "K01")
    argv, *_ = _prepare(tmp_path, case)
    reads.clear()
    assert run_main(argv).returncode == 0
    assert not [p for p in reads if p.name in ("staff.orm.yaml", "staff.population.yaml")]
    assert service._read_capped  # the one capped reader


@pytest.mark.parametrize("shape", ["wide-fact-type", "large-roster"])
def test_r11_work_never_exceeds_the_stated_ceiling(tmp_path: Path, shape: str) -> None:
    if shape == "wide-fact-type":
        model = """version: 1
source: {kind: fixture}
object_types:
  - {id: v, name: V, kind: value, primitive: Integer}
fact_types:
  - id: w
    reading: "{V} {V} {V} {V}"
    roles:
      - {object_type: v, role_name: a}
      - {object_type: v, role_name: b}
      - {object_type: v, role_name: c}
      - {object_type: v, role_name: d}
constraints: []
"""
        rows = "".join(f"    - {{a: {i}, b: {i % 7}, c: {i % 3}, d: {i % 11}}}\n" for i in range(1000))
        population = ("population: {model: m.orm.yaml, source: fixture, covers: [w]}\n"
                      "instances: {}\nfacts:\n  w:\n" + rows)
        extra = ("--max-pairs", "0")
    else:
        model = (CORPUS / "staff.orm.yaml").read_text()
        people = ", ".join(str(i) for i in range(30_000))
        population = (CORPUS / "staff.population.yaml").read_text().replace(
            "person: [1, 2, 3, 4, 5, 6]", f"person: [{people}]")
        extra = ()
    code, text, _, report_path = _discover(tmp_path, model, population, *extra)
    assert code == 0, text[-400:]
    work = json.loads(report_path.read_text())["work"]
    assert 0 < work["total"] <= work["ceiling"]


def test_r12_superkeys_of_a_declared_frequency_max_1_are_suppressed(tmp_path: Path) -> None:
    model = """version: 1
source: {kind: fixture}
object_types:
  - {id: v, name: V, kind: value, primitive: Integer}
fact_types:
  - id: t
    reading: "{V} {V} {V}"
    roles:
      - {object_type: v, role_name: a}
      - {object_type: v, role_name: b}
      - {object_type: v, role_name: c}
    constraints:
      - {type: frequency, scope: internal, roles: [a], bound: {max: 1}, source: explicit,
         status: confirmed, modality: alethic, provenance: {user_quote: q}}
constraints: []
"""
    rows = "".join(f"    - {{a: {i}, b: {i % 2}, c: {i % 3}}}\n" for i in range(6))
    population = ("population: {model: m.orm.yaml, source: fixture, covers: [t]}\n"
                  "instances: {}\nfacts:\n  t:\n" + rows)
    code, text, _, report_path = _discover(tmp_path, model, population, "--families", "uniqueness")
    assert code == 0, text
    report = json.loads(report_path.read_text())
    keys = [row["constraint"]["roles"] for row in report["emitted"]]
    assert ["a", "b"] not in keys and ["a", "c"] not in keys
    assert report["suppressed"]["superkey"] == 2


# ---- R13: branches the corpus could not fail ------------------------------

def test_r13_work_counts_are_exact(tmp_path: Path) -> None:
    # Uniqueness: two key candidates per binary fact type, each scanning its rows:
    # 2 x (6 + 5 + 2 + 4) = 34. Mandatory: per role, rows plus the roster:
    # (6+6)+(6+2) + (5+6)+(5+3) + (2+2)+(2+6) + (4+6)+(4+3) = 68.
    for case_id, counter, expected in (("K01", "uniqueness", 34), ("K02", "mandatory", 68)):
        (tmp_path / case_id).mkdir()
        *_, report_path, code = _run(tmp_path / case_id, case_id)
        assert code == 0
        assert json.loads(report_path.read_text())["work"][counter] == expected


def test_r13_examples_are_capped_at_256(tmp_path: Path) -> None:
    rows = "".join(f"    - {{amount: {i}, tag: t{i}}}\n" for i in range(300))
    population = ("population: {model: m.orm.yaml, source: fixture, covers: [a_tagged, a_flagged]}\n"
                  "instances: {}\nfacts:\n  a_tagged:\n" + rows + "  a_flagged: []\n")
    code, text, _, report_path = _discover(tmp_path, AMOUNT_MODEL, population, "--families", "uniqueness")
    assert code == 0, text
    row = next(r for r in json.loads(report_path.read_text())["emitted"]
               if r["constraint"]["roles"] == ["amount"])
    examples = row["constraint"]["provenance"]["induction"]["examples"]
    assert row["support"]["denominator"] == 300 and len(examples) == 256


def test_r13_exclusion_needs_both_sides(tmp_path: Path) -> None:
    population = ("population: {model: m.orm.yaml, source: fixture, covers: [a_tagged, a_flagged]}\n"
                  "instances: {}\nfacts:\n  a_tagged:\n    - {amount: 1, tag: x}\n  a_flagged: []\n")
    code, text, _, report_path = _discover(tmp_path, AMOUNT_MODEL, population, "--families", "exclusion")
    assert code == 0, text
    report = json.loads(report_path.read_text())
    assert report["emitted"] == [] and report["rejected"]["vacuous"] == 2


def test_r13_only_minimal_keys_are_emitted(tmp_path: Path) -> None:
    model = """version: 1
source: {kind: fixture}
object_types:
  - {id: v, name: V, kind: value, primitive: Integer}
fact_types:
  - id: t
    reading: "{V} {V} {V}"
    roles:
      - {object_type: v, role_name: a}
      - {object_type: v, role_name: b}
      - {object_type: v, role_name: c}
constraints: []
"""
    rows = "".join(f"    - {{a: {i}, b: {i % 2}, c: 0}}\n" for i in range(6))
    population = ("population: {model: m.orm.yaml, source: fixture, covers: [t]}\n"
                  "instances: {}\nfacts:\n  t:\n" + rows)
    code, text, _, report_path = _discover(tmp_path, model, population, "--families", "uniqueness")
    assert code == 0, text
    report = json.loads(report_path.read_text())
    assert [r["constraint"]["roles"] for r in report["emitted"]] == [["a"]]
    assert report["suppressed"]["redundant-superkey"] == 2  # {a,b} and {a,c}
