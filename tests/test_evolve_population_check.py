"""UG2: population-checked constraint admission on gnd evolve preview and apply.

Spec: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG2-spec.md
(§8, §11). Approval instrument: corpus-first (UG2-D12 (a)). The corpus is
tests/fixtures/unattended-model-growth/ug2/: README.md narrates each case
without its outcome, expected.json is the answer key, parity-baseline.json is
the flag-free baseline captured on 8eb4fe60 before the first source edit.

The corpus cases (C01 to C11) are red until UG2 lands: `--check-population`
does not exist on the base. The parity test (T10) is green on the base and must
stay green. Builders are local, not imported from other test modules (UG1's
refactoring note).
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "unattended-model-growth" / "ug2"
BASE = CORPUS / "base.orm.yaml"
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
PARITY = json.loads((CORPUS / "parity-baseline.json").read_text(encoding="utf-8"))


# --- builders ---------------------------------------------------------------


def _doc() -> dict[str, Any]:
    return YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))


def _fact_constraint(fact_type_id: str, index: int) -> dict[str, Any]:
    fact = next(item for item in _doc()["fact_types"] if item["id"] == fact_type_id)
    return copy.deepcopy(fact["constraints"][index])


def _constraint_locator(host: str | None, before: dict[str, Any] | None, family: str) -> Any:
    from gnd.evolve import ConstraintLocator, canonical_sha256

    digest = canonical_sha256(before) if before is not None else None
    if host is None:
        return ConstraintLocator(host="model", family=family, canonical_before_sha256=digest)
    return ConstraintLocator(host="fact_type", host_id=host, family=family, canonical_before_sha256=digest)


def _op(kind: str, locator: Any, *, before: Any = None, after: Any = None, operation_id: str = "op-0") -> Any:
    from gnd.evolve import EvolutionOperation, EvolutionOperationKind

    return EvolutionOperation(operation_id=operation_id, kind=EvolutionOperationKind(kind), locator=locator,
                              before=copy.deepcopy(before), after=copy.deepcopy(after))


def _proposal(operations: tuple[Any, ...], proposal_id: str) -> Any:
    from gnd.discover import output
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal

    text = BASE.read_text(encoding="utf-8")
    candidate = output.candidate_document(_doc(), operations)
    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        candidate_model=CommittedText.from_text(output.candidate_text(candidate), media_type="application/yaml"),
        operations=operations,
        rationale="UG2 corpus case.",
        audit=EvolutionOperationAudit(actor_id="owner:fixture", origin="test_evolve_population_check",
                                      requested_at=datetime(2026, 11, 9, 12, 0, tzinfo=UTC)),
    )


LLM = {"source": "llm-inferred", "status": "proposed", "modality": "deontic"}

UNIQUE_ORDER = {"type": "uniqueness", "roles": ["order"], **LLM,
                "rationale": "Each order is placed by one customer.",
                "provenance": {"rationale_world_fact": "An order has one buyer."}}
UNIQUE_ORDER_ALETHIC = {"type": "uniqueness", "roles": ["order"], "source": "user-supplied",
                        "status": "confirmed", "modality": "alethic",
                        "provenance": {"user_quote": "An order is placed by exactly one customer."}}
UNIQUE_CHANNEL_ORDER = {"type": "uniqueness", "roles": ["order"], **LLM,
                        "rationale": "Each order arrives by one channel.",
                        "provenance": {"rationale_world_fact": "An order arrives once."}}
MEMO_SUBSET = {"type": "subset",
               "subset_role_seq": [{"fact_type": "order_has_memo", "role": "order"}],
               "superset_role_seq": [{"fact_type": "customer_places_order", "role": "order"}],
               **LLM, "rationale": "A memo is only kept for a placed order.",
               "provenance": {"rationale_world_fact": "Memos annotate placed orders."}}


def _order_range() -> dict[str, Any]:
    return _fact_constraint("customer_places_order", 0)


def _order_range_tightened() -> dict[str, Any]:
    after = _order_range()
    after["range"]["max"] = 100
    return after


def _order_range_to_allowed() -> dict[str, Any]:
    after = _order_range()
    del after["range"]
    after["allowed"] = [10, 11]
    return after


def _case_operations(case_id: str) -> tuple[Any, ...]:
    """The proposal of each corpus case. README.md tells the same stories in prose."""
    add_unique = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=UNIQUE_ORDER),)
    table: dict[str, tuple[Any, ...]] = {
        "C01": add_unique,
        "C02": (_op("modify", _constraint_locator("customer_places_order", _order_range(), "value"),
                    before=_order_range(), after=_order_range_tightened()),),
        "C03": add_unique,
        "C04": add_unique,
        "C05": (_op("add", _constraint_locator(None, None, "subset"), after=MEMO_SUBSET),),
        "C06": add_unique,
        "C07a": add_unique,
        "C07b": add_unique,
        "C08a": (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"),
                     after=UNIQUE_ORDER_ALETHIC),),
        "C08b": (_op("modify", _constraint_locator("customer_places_order", _order_range(), "value"),
                     before=_order_range(), after=_order_range_to_allowed()),),
        "C09": (_op("add", _constraint_locator("order_has_channel", None, "uniqueness"),
                    after=UNIQUE_CHANNEL_ORDER),),
        "C10": add_unique,
        "C11a": add_unique,
        "C11b": add_unique,
        "C11c": add_unique,
    }
    return table[case_id]


def _workspace(root: Path, case_id: str) -> dict[str, Path]:
    root.mkdir(parents=True)
    (root / "records").mkdir()
    model = root / "model.orm.yaml"
    shutil.copyfile(BASE, model)
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    shutil.copytree(CORPUS / "populations", root / "populations")
    proposal = _proposal(_case_operations(case_id), proposal_id=f"ug2-{case_id.lower()}")
    proposal_path = root / "proposal.json"
    proposal_path.write_text(json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    return {"workspace": root, "model": model, "records": root / "records", "proposal": proposal_path,
            "preview": root / "preview.json"}


def _preview_argv(paths: dict[str, Path], flags: list[str]) -> list[str]:
    return ["evolve", "preview", str(paths["model"]), str(paths["proposal"]), "--workspace", str(paths["workspace"]),
            "--records", str(paths["records"]), "--out", str(paths["preview"]), "--format", "json",
            *_resolve(paths, flags)]


def _apply_argv(paths: dict[str, Path], flags: list[str]) -> list[str]:
    return ["evolve", "apply", str(paths["model"]), str(paths["proposal"]), "--preview", str(paths["preview"]),
            "--workspace", str(paths["workspace"]), "--records", str(paths["records"]), "--format", "json",
            *_resolve(paths, flags)]


def _resolve(paths: dict[str, Path], flags: list[str]) -> list[str]:
    """A `--check-population NAME` value is a file under the workspace's populations/."""
    out: list[str] = []
    for previous, flag in zip([None, *flags], flags, strict=False):
        out.append(str(paths["workspace"] / "populations" / flag) if previous == "--check-population" else flag)
    return out


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- the corpus: C01 to C11, judged against expected.json -------------------


def _assert_issue(preview: dict[str, Any], expected: dict[str, Any]) -> None:
    issues = preview["policy_issues"]
    assert len(issues) == 1, issues
    issue = issues[0]
    assert issue["operation_index"] == expected["operation_index"]
    assert issue["cell"] == expected["cell"]
    if expected["population"] is None:
        assert "; population:" not in issue["detail"], issue["detail"]
    else:
        assert issue["detail"].endswith(f"; population: {expected['population']}"), issue["detail"]


def _assert_step(result: Any, paths: dict[str, Path], step: dict[str, Any], stage: str) -> None:
    stderr = result.stderr.decode()
    assert result.returncode == step["exit"], (stage, result.returncode, stderr)
    for needle in step.get("stderr_contains", ()):
        assert needle in stderr, (stage, needle, stderr)
    if stage != "preview":
        return
    if not step.get("preview_written", True):
        assert not paths["preview"].exists()
        return
    preview = json.loads(paths["preview"].read_text(encoding="utf-8"))
    if "issue" in step:
        _assert_issue(preview, step["issue"])
    else:
        assert preview.get("policy_issues") == [], preview.get("policy_issues")
    if "admitted" in step:
        check = preview["population_check"]
        assert [row["operation_index"] for row in check["admitted"]] == step["admitted"]
        assert all(row["outcome"] == "pass" for row in check["admitted"])
        assert check["model_id"] == "ug2-orders"
        assert check["sha256"] == _sha(paths["workspace"] / "populations" / step["population_file"])


@pytest.mark.parametrize("case_id", sorted(EXPECTED["cases"]))
def test_corpus_case(tmp_path: Path, case_id: str) -> None:
    case = EXPECTED["cases"][case_id]
    paths = _workspace(tmp_path / "ws", case_id)
    model_before = paths["model"].read_bytes()
    _assert_step(run_main(_preview_argv(paths, case["preview"]["flags"])), paths, case["preview"], "preview")
    if "replace_population" in case:
        source, target = case["replace_population"]
        shutil.copyfile(paths["workspace"] / "populations" / source, paths["workspace"] / "populations" / target)
    if "apply" not in case:
        return
    result = run_main(_apply_argv(paths, case["apply"]["flags"]))
    _assert_step(result, paths, case["apply"], "apply")
    if case["apply"]["exit"] == 0:
        published = YAML(typ="safe").load(paths["model"].read_text(encoding="utf-8"))
        operation = _case_operations(case_id)[0]
        after = operation.model_dump(mode="json")["after"]
        hosts = (published["constraints"] if operation.locator.host == "model" else
                 next(f for f in published["fact_types"] if f["id"] == operation.locator.host_id)["constraints"])
        assert after in hosts  # UG-R3: published as proposed, never relabelled
    else:
        assert paths["model"].read_bytes() == model_before


def test_answer_key_is_split_from_the_narration() -> None:
    """Every case is narrated, and the narration gives no outcome (spec §11)."""
    readme = (CORPUS / "README.md").read_text(encoding="utf-8").lower()
    narrated = {line.split()[1] for line in readme.splitlines() if line.startswith("### c")}
    assert narrated == {case.lower() for case in EXPECTED["cases"]}
    for word in ("exit", "refuse", "admit", "uncovered", "not eligible", "sample-rows", "warning", "stale", "pass"):
        assert word not in readme, word


# --- T10: flag-free parity (UG-R1), green on the base and after UG2 ----------


@pytest.mark.parametrize("row", PARITY["rows"], ids=lambda row: f"{row['case']}-{row['mode']}")
def test_t10_flag_free_preview_bytes_do_not_move(tmp_path: Path, row: dict[str, Any]) -> None:
    paths = _workspace(tmp_path / "ws", row["case"])
    result = run_main(_preview_argv(paths, row["flags"]))
    assert result.returncode == row["exit"], result.stderr.decode()
    if row["preview_sha256"] is None:
        assert not paths["preview"].exists()
    else:
        assert _sha(paths["preview"]) == row["preview_sha256"]


# --- implementation tests (spec §8, beyond the approval corpus) -------------
#
# These are separately identified successors of the approved corpus (process
# step 3): they add cases, they change no approved answer.

P_ORDERS = ["--policy", "additive", "--populated", "customer_places_order"]


def _service(root: Path) -> Any:
    from gnd.evolve import EvolutionService

    return EvolutionService(model_path=root / "model.orm.yaml", evidence_root=root / "records",
                            allowed_project_root=root)


def _service_workspace(tmp_path: Path, operations: tuple[Any, ...], population: dict[str, Any] | None = None,
                       *, name: str = "pop.json") -> tuple[Any, Any, Path]:
    root = tmp_path.resolve() / "ws"
    root.mkdir(parents=True)
    (root / "records").mkdir()
    shutil.copyfile(BASE, root / "model.orm.yaml")
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    if population is not None:
        (root / name).write_text(json.dumps(population), encoding="utf-8")
    return _service(root), _proposal(operations, proposal_id="ug2-service"), root


def _population(facts: dict[str, list[dict[str, Any]]], **header: Any) -> dict[str, Any]:
    return {"population": {"model": "base.orm.yaml", "model_id": "ug2-orders", "source": "agent-output",
                           "covers": sorted(facts), **header}, "facts": facts}


PLACEMENTS = [{"customer": 1, "order": 10}, {"customer": 2, "order": 11}]
LLM_TEXT = {"rationale": "Stated by the host.", "provenance": {"rationale_world_fact": "Seen in the text."}}

FAMILIES = {
    "uniqueness": ("customer_places_order", {"type": "uniqueness", "roles": ["order"]}),
    "mandatory": ("customer_places_order", {"type": "mandatory", "role": "customer"}),
    "frequency": ("customer_places_order",
                  {"type": "frequency", "scope": "internal", "roles": ["customer"], "bound": {"min": 1, "max": 5}}),
    "value": ("customer_places_order",
              {"type": "value", "object_type": "order",
               "role_ref": {"fact_type": "customer_places_order", "role": "order"}, "range": {"min": 1, "max": 50}}),
    "subset": (None, {"type": "subset",
                      "subset_role_seq": [{"fact_type": "order_has_amount", "role": "order"}],
                      "superset_role_seq": [{"fact_type": "customer_places_order", "role": "order"}]}),
}


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_t1_each_family_is_cleared_by_a_clean_population(tmp_path: Path, family: str) -> None:
    host, shape = FAMILIES[family]
    after = {**shape, **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator(host, None, shape["type"]), after=after),)
    facts = {"customer_places_order": PLACEMENTS,
             "order_has_amount": [{"order": 10, "amount": 40}, {"order": 11, "amount": 75}]}
    service, proposal, _root = _service_workspace(tmp_path, operations, _population(facts))
    populated = ("customer_places_order", "order_has_amount")
    refused = service.preview(proposal, policy="additive", populated=populated)
    assert [issue.cell for issue in refused.policy_issues] == ["constraint.populated.add"]
    preview = service.preview(proposal, policy="additive", populated=populated, check_population="pop.json")
    assert preview.policy_issues == ()
    assert [row.operation_index for row in preview.population_check.admitted] == [0]


def test_t5b_an_unchecked_verdict_is_its_own_word(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.evolve import population_check

    real = population_check.check

    def unchecked(model: Any, population: Any) -> Any:
        report = real(model, population)
        rows = [row.model_copy(update={"verdict": "unchecked"}) for row in report.verdicts]
        return report.model_copy(update={"verdicts": rows})

    monkeypatch.setattr(population_check, "check", unchecked)
    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    service, proposal, _ = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    assert preview.policy_issues[0].detail.endswith("; population: unchecked")
    assert preview.population_check.admitted == ()


def test_not_located_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.evolve import population_check

    real = population_check.check
    monkeypatch.setattr(population_check, "check",
                        lambda model, population: real(model, population).model_copy(update={"verdicts": []}))
    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    service, proposal, _ = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    assert preview.policy_issues[0].detail.endswith("; population: not-located")


def test_t4b_vacuous_and_t3b_fail_reachability(tmp_path: Path) -> None:
    """`vacuous` needs a populated subject that is covered yet empty for the constraint: unreachable,
    because `uncovered` is decided first (precedence, spec §6.1). `fail` is an alethic verdict, and an
    alethic constraint is never eligible. Both words stay in the vocabulary for the checker's sake; this
    test pins the precedence that makes them unreachable through the CLI."""
    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    empty = _population({"customer_places_order": []})
    service, proposal, _ = _service_workspace(tmp_path, operations, empty)
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    assert preview.policy_issues[0].detail.endswith("; population: uncovered")


def test_t9_bytes_changed_between_fresh_preview_and_service_reread(tmp_path: Path) -> None:
    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    service, proposal, root = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    before = (root / "model.orm.yaml").read_bytes()
    (root / "pop.json").write_text(json.dumps(_population({"customer_places_order": PLACEMENTS[:1]})),
                                   encoding="utf-8")
    from gnd.evolve import EvolutionError

    with pytest.raises(EvolutionError, match="population changed before apply"):
        service.apply(preview, check_population="pop.json")
    assert (root / "model.orm.yaml").read_bytes() == before
    with pytest.raises(EvolutionError, match="--check-population differs"):
        service.apply(preview)


CANARIES = ("zqx-canary-customer", "zqx-canary-memo")


def test_t11_no_population_value_reaches_any_output(tmp_path: Path) -> None:
    root = tmp_path.resolve() / "ws"
    paths = _workspace(root, "C05")
    memo_rows = [{"order": 10, "memo": CANARIES[1]}]
    pop = _population({"customer_places_order": [{"customer": 1, "order": 10}], "order_has_memo": memo_rows})
    pop_bad = _population({"customer_places_order": [{"customer": 1, "order": 10}],
                           "order_has_memo": [{"order": CANARIES[0], "memo": CANARIES[1]}]})
    (root / "populations" / "canary.json").write_text(json.dumps(pop), encoding="utf-8")
    (root / "populations" / "canary-bad.json").write_text(json.dumps(pop_bad), encoding="utf-8")
    flags = P_ORDERS + ["--populated", "order_has_memo", "--check-population", "canary.json"]
    channels = []
    for argv in (_preview_argv(paths, flags), _apply_argv(paths, flags)):
        result = run_main(argv)
        channels += [result.stdout, result.stderr]
    preview = json.loads(paths["preview"].read_text(encoding="utf-8"))
    for key in ("candidate_model", "before_model", "verbalization", "proposal"):
        preview.pop(key)
    channels.append(json.dumps(preview).encode())
    channels += [path.read_bytes() for path in paths["records"].rglob("*") if path.is_file()]
    bad = _workspace(tmp_path.resolve() / "bad", "C05")
    (bad["workspace"] / "populations" / "canary-bad.json").write_text(json.dumps(pop_bad), encoding="utf-8")
    result = run_main(_preview_argv(bad, P_ORDERS + ["--populated", "order_has_memo",
                                                     "--check-population", "canary-bad.json"]))
    assert result.returncode == 3
    channels += [result.stdout, result.stderr]
    blob = b"\n".join(channels)
    assert not any(canary.encode() in blob for canary in CANARIES)
    # positive control: the scan finds a planted canary
    assert CANARIES[0].encode() in blob + CANARIES[0].encode()
    assert CANARIES[1].encode() in json.dumps(pop).encode()


def _hostile(root: Path, name: str) -> str:
    pops = root / "populations"
    target = pops / name
    good = json.dumps(_population({"customer_places_order": PLACEMENTS}))
    if name == "oversize.json":
        target.write_bytes(b" " * (10 * 1024 * 1024 + 1))
    elif name == "latin1.json":
        target.write_bytes(good.replace("agent-output", "agent-\xe9").encode("latin-1"))
    elif name == "nan.json":
        target.write_text(good.replace('"order": 10', '"order": NaN'), encoding="utf-8")
    elif name == "longint.json":
        target.write_text(good.replace('"order": 10', '"order": ' + "9" * 100_000), encoding="utf-8")
    elif name == "deep.json":
        target.write_text("[" * 65 + "]" * 65, encoding="utf-8")
    elif name == "bomb.yaml":
        lines = ["a: &a [x, x, x, x, x, x, x, x, x]"] + [
            f"{chr(98 + i)}: &{chr(98 + i)} [*{chr(97 + i)}, *{chr(97 + i)}, *{chr(97 + i)}, *{chr(97 + i)}]"
            for i in range(9)]
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    elif name == "list.json":
        target.write_text("[]", encoding="utf-8")
    elif name == "dir.json":
        target.mkdir()
    elif name == "fifo.json":
        import os

        os.mkfifo(target)
    elif name == "link.json":
        target.symlink_to(pops / "clean.json")
    return name


@pytest.mark.parametrize(("name", "exit_code"), [
    ("missing.json", 66), ("link.json", 74), ("dir.json", 74), ("fifo.json", 74), ("oversize.json", 3),
    ("latin1.json", 3), ("nan.json", 3), ("longint.json", 3), ("deep.json", 3), ("bomb.yaml", 3), ("list.json", 3),
])
def test_t12_hostile_population_files(tmp_path: Path, name: str, exit_code: int) -> None:
    paths = _workspace(tmp_path.resolve() / "ws", "C01")
    _hostile(paths["workspace"], name)
    result = run_main(_preview_argv(paths, P_ORDERS + ["--check-population", name]))
    assert result.returncode == exit_code, result.stderr.decode()
    assert b"Traceback" not in result.stderr
    assert not paths["preview"].exists()


def test_t12_reference_bearing_candidate_is_refused(tmp_path: Path) -> None:
    from gnd.evolve import population_check
    from gnd.evolve.population_check import EvolutionPopulationError

    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    service, proposal, _ = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))

    class Bearing:
        reference_populations = ({"id": "r"},)

    with pytest.raises(EvolutionPopulationError) as caught:
        service._population_check("pop.json", None, proposal, Bearing(), frozenset(), [])
    assert caught.value.exit_code == 3
    assert population_check  # the module owns the refusal type


@pytest.mark.parametrize("count", [1, 10, 100])
def test_t13_one_check_call_and_linear_mapping(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, count: int) -> None:
    from gnd.evolve import population_check
    from gnd.evolve import service as service_module

    calls = {"check": 0, "placed": 0}
    real_check = population_check.check
    real_record = service_module._record_placement

    def counting_check(model: Any, population: Any) -> Any:
        calls["check"] += 1
        return real_check(model, population)

    def counting_record(*args: Any) -> None:
        calls["placed"] += 1
        real_record(*args)

    operations = tuple(
        _op("add", _constraint_locator("customer_places_order", None, "frequency"), operation_id=f"op-{i}",
            after={"type": "frequency", "scope": "internal", "roles": ["customer"],
                   "bound": {"min": 1, "max": 5 + i}, **LLM, **LLM_TEXT})
        for i in range(count))
    service, proposal, _ = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    # Spies installed after setup: building the proposal replays the operations too.
    monkeypatch.setattr(population_check, "check", counting_check)
    monkeypatch.setattr(service_module, "_record_placement", counting_record)
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    assert calls["check"] == 1
    assert calls["placed"] == count  # one placement per operation: linear, not quadratic
    assert len(preview.population_check.admitted) == count


def test_t14_order_replay_before_the_population_read() -> None:
    import inspect

    from gnd.evolve.service import EvolutionService

    source = inspect.getsource(EvolutionService.preview)
    assert source.index("_enforce_d12(") < source.index("self._policy_values(")
    values = inspect.getsource(EvolutionService._policy_values)
    assert values.index("checked = population(effective)") < values.index("population_outcomes=")
    apply_source = inspect.getsource(EvolutionService.apply)
    assert apply_source.index("_enforce_d12(") < apply_source.index("check_population=check_population")


def test_t14_a_replay_mismatch_is_reported_before_a_missing_population(tmp_path: Path) -> None:
    paths = _workspace(tmp_path.resolve() / "ws", "C01")
    declared = _case_operations("C01")
    other = _proposal((_op("add", _constraint_locator("customer_places_order", None, "uniqueness"),
                           after={**UNIQUE_ORDER, "roles": ["customer"]}),), proposal_id="ug2-c01")
    mismatched = _proposal(declared, proposal_id="ug2-c01").model_copy(
        update={"candidate_model": other.candidate_model})
    paths["proposal"].write_text(json.dumps(mismatched.model_dump(mode="json")), encoding="utf-8")
    result = run_main(_preview_argv(paths, P_ORDERS + ["--check-population", "missing.json"]))
    assert result.returncode == 3, result.stderr.decode()
    assert b"declared operations" in result.stderr


def test_t15_a_declared_constraint_id_is_located(tmp_path: Path) -> None:
    after = {**FAMILIES["uniqueness"][1], "id": "one_buyer_per_order", **LLM, **LLM_TEXT}
    operations = (_op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after),)
    service, proposal, _ = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    preview = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                              check_population="pop.json")
    assert preview.policy_issues == ()


def test_t16_placement_follows_a_later_delete(tmp_path: Path) -> None:
    after = {**FAMILIES["uniqueness"][1], **LLM, **LLM_TEXT}
    existing = _order_range()
    operations = (
        _op("add", _constraint_locator("customer_places_order", None, "uniqueness"), after=after, operation_id="a"),
        _op("delete", _constraint_locator("customer_places_order", existing, "value"), before=existing,
            operation_id="b"),
    )
    violating = [{"customer": 1, "order": 10}, {"customer": 2, "order": 10}]
    service, proposal, root = _service_workspace(tmp_path, operations, _population({"customer_places_order": PLACEMENTS}))
    clean = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                            check_population="pop.json")
    assert clean.policy_issues == () and [r.operation_index for r in clean.population_check.admitted] == [0]
    (root / "bad.json").write_text(json.dumps(_population({"customer_places_order": violating})), encoding="utf-8")
    bad = service.preview(proposal, policy="additive", populated=("customer_places_order",),
                          check_population="bad.json")
    assert bad.policy_issues[0].detail.endswith("; population: warning")
