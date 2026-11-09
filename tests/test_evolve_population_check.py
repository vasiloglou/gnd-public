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
