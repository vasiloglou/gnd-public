"""UG1: the unattended-model-growth asks, measured on shipped bytes through the CLI.

Spec: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG1-spec.md
(§8 T1-T14). Test-only: nothing under src/ or tools/ is touched. The replay
drives `gnd validate --document`, `gnd evolve preview --policy additive
--shape-report` and `gnd evolve apply` over three rounds of three documents
with no reviewer. Where a case below pins a gap or a deviation rather than a
wish (T9's omitted document, T12(a)), the comment says so.
"""

from __future__ import annotations

import builtins
import copy
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
import test_unattended_growth_guidance as growth
from ruamel.yaml import YAML
from support.cli_runner import run_main
from support.digests import sha256_bytes

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "unattended-model-growth"
SEED = REPO_ROOT / "tests" / "fixtures" / "unattended" / "conforming.orm.yaml"
SEED_DOCUMENT = REPO_ROOT / "tests" / "fixtures" / "unattended" / "source.txt"
CONTRACT = "src/gnd/skills/gnd-model-evolve/references/evolution-contract.md"
BASE_COMMIT = "12daa5b7"


# --- the replay's three rounds, in the reply shape the host produces -----------------------------


def _entity(object_id: str, name: str, value_type: str, quote: str) -> dict[str, Any]:
    return {"id": object_id, "name": name, "kind": "entity",
            "reference": {"mode": "popular", "value_type": value_type}, "quote": quote}


def _value(object_id: str, name: str, primitive: str, quote: str) -> dict[str, Any]:
    return {"id": object_id, "name": name, "kind": "value", "primitive": primitive, "quote": quote}


def _fact(fact_id: str, reading: str, players: tuple[str, str], quote: str) -> dict[str, Any]:
    return {"id": fact_id, "reading": reading, "rows": [], "quote": quote,
            "roles": [{"object_type": player, "role_name": player} for player in players]}


ROUND_1: dict[str, Any] = {
    "document": "round-1.txt",
    "object_types": [
        _entity("loan", "Loan", "loan_id", "Equipment loans"),
        _value("loan_id", "LoanId", "String", "loan id"),
        _entity("borrower", "Borrower", "borrower_id", "Borrowers are tracked"),
        _value("borrower_id", "BorrowerId", "String", "borrower id"),
        _entity("laptop", "Laptop", "laptop_tag", "Laptops are tracked"),
        _value("laptop_tag", "LaptopTag", "String", "laptop tag"),
        _value("due_date", "DueDate", "Date", "due date"),
        _value("loan_status", "LoanStatus", "String", "loan status"),
    ],
    "fact_types": [
        _fact("loan_has_due_date", "{Loan} has {DueDate}", ("loan", "due_date"),
              "Each loan has exactly one due date"),
        _fact("borrower_holds_laptop", "{Borrower} holds {Laptop}", ("borrower", "laptop"),
              "A borrower holds a laptop"),
    ],
    "subtype_links": [],
    "constraints": [
        {"host": "loan_has_due_date", "basis": "text-cue", "constraint": {"type": "uniqueness", "roles": ["loan"]},
         "cue": "exactly one", "quote": "Each loan has exactly one due date",
         "rationale": "The text gives each loan one due date."},
        {"host": "loan_has_due_date", "basis": "text-cue", "constraint": {"type": "mandatory", "role": "loan"},
         "cue": "Each loan has exactly one", "quote": "Each loan has exactly one due date",
         "rationale": "The text gives each loan a due date."},
        {"host": "model", "basis": "text-cue",
         "constraint": {"type": "value", "object_type": "loan_status", "allowed": ["open", "closed"]},
         "cue": "one of: open, closed", "quote": "one of: open, closed",
         "rationale": "The text lists the loan statuses as a closed set."},
    ],
}
ROUND_2: dict[str, Any] = {
    "document": "round-2.txt",
    "object_types": [],
    "fact_types": [_fact("loan_is_due_on", "{Loan} is due on {DueDate}", ("loan", "due_date"),
                         "A loan is due on a date")],
    "subtype_links": [],
    "constraints": [],
}
ROUND_3: dict[str, Any] = {
    "document": "round-3.txt",
    "object_types": [{"id": "staff_borrower", "name": "StaffBorrower", "kind": "entity", "quote": "staff borrower"}],
    "fact_types": [],
    "subtype_links": [{"subtype": "staff_borrower", "supertype": "borrower", "inherits_reference": True,
                       "quote": "A staff borrower is a kind of borrower",
                       "rationale": "A defined term naming a kind of borrower."}],
    "constraints": [],
}
ROUNDS = (ROUND_1, ROUND_2, ROUND_3)


def _document(n: int) -> bytes:
    return (FIXTURES / f"round-{n}.txt").read_bytes()


def _operations(reply: dict[str, Any], raw: bytes) -> tuple[Any, ...]:
    """The reply as additive operations: elements first, then each constraint with its host."""
    model = growth._translate(reply, raw)
    operations: list[Any] = []

    def add(locator: Any, after: dict[str, Any]) -> None:
        operations.append(policy._op("add", locator, after=after, operation_id=f"op-{len(operations)}"))

    for element in model["object_types"]:
        add(policy._element("object_types", element["id"]), element)
    for fact in model["fact_types"]:
        element = {key: value for key, value in fact.items() if key != "constraints"}
        for key in ("sample_population",):
            if not element.get(key):
                element.pop(key, None)
        if not element["provenance"].get("sample_spans"):
            element["provenance"].pop("sample_spans", None)
        add(policy._element("fact_types", fact["id"]), element)
    for fact in model["fact_types"]:
        for constraint in fact.get("constraints", []):
            add(policy._constraint_locator(fact["id"], None, constraint["type"]), constraint)
    for constraint in model["constraints"]:
        add(policy._constraint_locator(None, None, constraint["type"]), constraint)
    return tuple(operations)


# --- the replay driver: one workspace, one proposal and preview path per round --------------------


def _workspace(root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    (root / "records").mkdir(exist_ok=True)
    model = root / "model.orm.yaml"
    model.write_text(SEED.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    return {"workspace": root, "model": model, "records": root / "records"}


def _declare(model_path: Path, raw: bytes, label: str) -> None:
    """Declare a document in the model file, outside `evolve` (the O20 gap: UG3 (i) retires this)."""
    yaml = YAML()
    yaml.preserve_quotes = True
    document = yaml.load(model_path.read_text(encoding="utf-8"))
    document["source"]["documents"].append({"sha256": sha256_bytes(raw), "label": label})
    with model_path.open("w", encoding="utf-8") as handle:
        yaml.dump(document, handle)


def _round_paths(ws: dict[str, Path], tag: str) -> dict[str, Path]:
    return {**ws, "proposal": ws["workspace"] / f"proposal-{tag}.json", "preview": ws["workspace"] / f"preview-{tag}.json"}


def _write_proposal(ws: dict[str, Path], tag: str, operations: tuple[Any, ...]) -> dict[str, Path]:
    paths = _round_paths(ws, tag)
    text = ws["model"].read_text(encoding="utf-8")
    proposal = policy._proposal(text, operations, proposal_id=f"ug1-{tag}")
    paths["proposal"].write_text(json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    return paths


def _preview(paths: dict[str, Path], *extra: str, expect: int = 0) -> tuple[dict[str, Any] | None, Any]:
    """Run preview with `extra` flags; assert the exit before reading the preview file."""
    result = run_main(policy._preview_argv(paths, *extra))
    assert result.returncode == expect, (result.returncode, result.stderr.decode())
    document = json.loads(paths["preview"].read_text(encoding="utf-8")) if paths["preview"].exists() else None
    return document, result


def _validate(model: Path, documents: tuple[Path, ...] = (), *, expect: int = 0) -> dict[str, Any]:
    argv = ["validate", str(model), "--format", "json"]
    for document in documents:
        argv += ["--document", str(document)]
    result = run_main(argv)
    assert result.returncode == expect, (result.returncode, result.stderr.decode(), result.stdout.decode()[:400])
    return json.loads(result.stdout)


def _round(ws: dict[str, Path], n: int, reply: dict[str, Any]) -> dict[str, Any]:
    """Declare the round's document, preview with the additive policy and shape report, apply."""
    raw = _document(n)
    _declare(ws["model"], raw, f"round-{n}.txt")
    paths = _write_proposal(ws, f"r{n}", _operations(reply, raw))
    preview, _result = _preview(paths, "--policy", "additive", "--shape-report")
    result = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 0, (result.returncode, result.stderr.decode())
    return preview


def _shape_groups(preview: dict[str, Any]) -> list[dict[str, Any]]:
    return preview["shape_matches"]


# --- T1: three rounds, three documents, no reviewer -----------------------------------------------


def test_t1_three_round_replay_exits_zero_at_every_step(tmp_path: Path) -> None:
    ws = _workspace(tmp_path / "ws")
    documents = [FIXTURES / f"round-{n}.txt" for n in (1, 2, 3)]
    previews = []
    for n, reply in enumerate(ROUNDS, 1):
        previews.append(_round(ws, n, reply))
        _validate(ws["model"], (*documents[:n], SEED_DOCUMENT))
    for preview in previews:
        # Without --policy the key is absent, so a dropped flag would otherwise pass.
        assert preview["policy"] == "additive" and preview["policy_issues"] == []
    # Control: every added fact type gets a group, so a non-empty group alone proves nothing.
    assert all(group["existing"] == [] for group in _shape_groups(previews[0]))
    restated = [g for g in _shape_groups(previews[1]) if [a["fact_type"] for a in g["added"]] == ["loan_is_due_on"]]
    assert len(restated) == 1 and [m["fact_type"] for m in restated[0]["existing"]] == ["loan_has_due_date"]
    assert _shape_groups(previews[2]) == []
    # The final validate names the three round documents and the seed's own source.txt: a span whose
    # document is not supplied is not re-hashed (the O14 gap, pinned in T9), so a third-document run
    # would leave the seed's spans unchecked.
    final_documents = (*documents, SEED_DOCUMENT)
    assert len(final_documents) == 4 and len(set(final_documents)) == 4
    _validate(ws["model"], final_documents)
    published = ws["model"].read_text(encoding="utf-8")
    assert "staff_borrower" in published and "loan_is_due_on" in published


# --- the grown model every refusal case starts from (built once, copied per test) -----------------


@pytest.fixture(scope="module")
def grown_base(tmp_path_factory: pytest.TempPathFactory) -> Path:
    ws = _workspace(tmp_path_factory.mktemp("grown") / "ws")
    for n, reply in enumerate(ROUNDS, 1):
        _round(ws, n, reply)
    return ws["workspace"]


@pytest.fixture
def grown(grown_base: Path, tmp_path: Path) -> dict[str, Path]:
    destination = tmp_path / "ws"
    shutil.copytree(grown_base, destination)
    return {"workspace": destination, "model": destination / "model.orm.yaml", "records": destination / "records"}


def _current(ws: dict[str, Path]) -> dict[str, Any]:
    return policy._doc(ws["model"].read_text(encoding="utf-8"))


def _assert_refused(result: Any, preview: dict[str, Any] | None, cell: str, index: int = 0) -> None:
    """Exit 3 alone is no evidence (candidate-validation failures also exit 3): the cell must be named."""
    assert result.returncode == 3, result.stderr.decode()
    assert preview is not None and preview["policy_issues"], "a refused preview still carries its issues"
    assert any(issue["cell"] == cell and issue["operation_index"] == index for issue in preview["policy_issues"]), (
        preview["policy_issues"])
    # Preview's stderr counts the issues and points at the file; `apply` is the command that names the cell.
    assert b"additive policy refused" in result.stderr


def _apply_breaking(monkeypatch: pytest.MonkeyPatch, paths: dict[str, Path], preview: dict[str, Any], *extra: str,
                    eof: bool = False) -> Any:
    """`apply` of a rename or delete prompts for the exact blast-radius digest on stdin (EOF exits 11)."""
    digest = preview["blast_radius"]["report_sha256"]

    def answer(*_args: Any) -> str:
        if eof:
            raise EOFError
        return digest

    monkeypatch.setattr(builtins, "input", answer)
    return run_main(policy._apply_argv(paths, *extra))


def _span_of(raw: bytes, quote: str) -> dict[str, Any]:
    return growth._span(raw, quote)


def _constraint(constraint: dict[str, Any], raw: bytes, quote: str) -> dict[str, Any]:
    return {**constraint, "source": "llm-inferred", "status": "proposed", "modality": "deontic",
            "rationale": "A UG1 replay case.",
            "provenance": {"rationale_world_fact": "A UG1 replay case.", "spans": [_span_of(raw, quote)]}}


# --- T2, T3: breaking refusals (rename, delete) ----------------------------------------------------


@pytest.mark.parametrize(
    ("collection", "element_id", "new_id", "cell", "populated"),
    [("object_types", "staff_borrower", "staff_member", "object_types.rename", ()),
     ("fact_types", "borrower_holds_laptop", "borrower_has_laptop", "fact_types.rename", ()),
     ("fact_types", "borrower_holds_laptop", "borrower_has_laptop", "fact_types.rename", ("borrower_holds_laptop",))],
    ids=["object-type", "fact-type-unpopulated", "fact-type-populated"],
)
def test_t2_rename_is_refused_and_apply_cannot_publish(grown: dict[str, Path], monkeypatch: pytest.MonkeyPatch,
                                                      collection: str, element_id: str, new_id: str, cell: str,
                                                      populated: tuple[str, ...]) -> None:
    document = _current(grown)
    element = next(item for item in document[collection] if item["id"] == element_id)
    renamed = policy._modified(element, id=new_id)
    operations = (policy._op("rename", policy._element(collection, element_id), before=element, after=renamed),)
    tag = f"t2-{collection}-{len(populated)}"
    paths = _write_proposal(grown, tag, operations)
    flags = ["--policy", "additive", *[a for name in populated for a in ("--populated", name)]]
    before_bytes = grown["model"].read_bytes()
    preview, result = _preview(paths, *flags, expect=3)
    _assert_refused(result, preview, cell)
    applied = _apply_breaking(monkeypatch, paths, preview, *flags)
    assert applied.returncode == 3 and cell.encode() in applied.stderr, applied.stderr.decode()
    assert grown["model"].read_bytes() == before_bytes
    # Without the digest on stdin the exit is 11 (pinned: on a tty it would hang, under capture it is 74).
    eof = _apply_breaking(monkeypatch, paths, preview, *flags, eof=True)
    assert eof.returncode == 11 and b"requires exact blast radius acceptance" in eof.stderr
    assert grown["model"].read_bytes() == before_bytes


@pytest.mark.parametrize(
    ("collection", "element_id", "cell"),
    [("object_types", "staff_borrower", "object_types.delete"), ("fact_types", "borrower_holds_laptop", "fact_types.delete")],
)
def test_t3_delete_is_refused_for_both_kinds(grown: dict[str, Path], monkeypatch: pytest.MonkeyPatch, collection: str,
                                             element_id: str, cell: str) -> None:
    # Unreferenced on purpose: deleting a referenced element fails candidate validation (exit 3, no cell).
    document = _current(grown)
    element = next(item for item in document[collection] if item["id"] == element_id)
    operations = (policy._op("delete", policy._element(collection, element_id), before=element),)
    paths = _write_proposal(grown, f"t3-{element_id}", operations)
    before_bytes = grown["model"].read_bytes()
    preview, result = _preview(paths, "--policy", "additive", expect=3)
    _assert_refused(result, preview, cell)
    applied = _apply_breaking(monkeypatch, paths, preview, "--policy", "additive")
    assert applied.returncode == 3 and cell.encode() in applied.stderr, applied.stderr.decode()
    assert grown["model"].read_bytes() == before_bytes


# --- T4, T5, T6: the populated-constraint cells and the subtype link --------------------------------

POPULATED_FACT = "loan_has_due_date"


def _reply_one(fact_types: tuple[dict[str, Any], ...] = (), constraints: tuple[dict[str, Any], ...] = ()) -> dict[str, Any]:
    return {"document": "round-1.txt", "object_types": [], "fact_types": list(fact_types), "subtype_links": [],
            "constraints": list(constraints)}


def _new_fact(fact_id: str) -> dict[str, Any]:
    return _fact(fact_id, "{Borrower} is linked to " + fact_id + " {Loan}", ("borrower", "loan"),
                 "A borrower holds a laptop")


def _hosted(host: str, constraint: dict[str, Any]) -> dict[str, Any]:
    return {"host": host, "basis": "text-cue", "constraint": constraint, "cue": "A borrower holds a laptop",
            "quote": "A borrower holds a laptop", "rationale": "A UG1 replay case."}


def _subset(sub: tuple[str, str], sup: tuple[str, str]) -> dict[str, Any]:
    return _hosted("model", {"type": "subset",
                             "subset_role_seq": [{"fact_type": sub[0], "role": sub[1]}],
                             "superset_role_seq": [{"fact_type": sup[0], "role": sup[1]}]})


def test_t4_a_constraint_on_a_populated_fact_type_is_refused(grown: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    raw1 = _document(1)
    added = _constraint({"type": "mandatory", "role": "due_date"}, raw1, "Each loan has exactly one due date")
    on_existing = (policy._op("add", policy._constraint_locator(POPULATED_FACT, None, "mandatory"), after=added),)
    paths = _write_proposal(grown, "t4-flag", on_existing)
    flags = ("--policy", "additive", "--populated", POPULATED_FACT)
    preview, result = _preview(paths, *flags, expect=3)
    _assert_refused(result, preview, "constraint.populated.add")
    # `apply` of the refused preview is not breaking: it exits 3 directly, naming the cell, with no prompt.
    monkeypatch.setattr(builtins, "input", lambda *_a: pytest.fail("a non-breaking apply must not prompt"))
    applied = run_main(policy._apply_argv(paths, *flags))
    assert applied.returncode == 3 and b"constraint.populated.add" in applied.stderr
    # Control (a): the same constraint on the same fact type without --populated is admitted.
    paths = _write_proposal(grown, "t4-noflag", on_existing)
    document, _ = _preview(paths, "--policy", "additive")
    assert document is not None and document["policy_issues"] == []
    # Control (b): the same constraint on a fact type this proposal adds is admitted, flag or not.
    reply = _reply_one((_new_fact("borrower_holds_loan"),),
                       (_hosted("borrower_holds_loan", {"type": "mandatory", "role": "loan"}),))
    paths = _write_proposal(grown, "t4-new", _operations(reply, raw1))
    document, _ = _preview(paths, *flags)
    assert document is not None and document["policy_issues"] == []
    # Rows in the model count as population with no flag: the seed's order_placed_by_customer carries two.
    seed = _constraint({"type": "uniqueness", "roles": ["customer"]}, SEED_DOCUMENT.read_bytes(),
                       "An order has one placing customer")
    on_rows = (policy._op("add", policy._constraint_locator("order_placed_by_customer", None, "uniqueness"), after=seed),)
    paths = _write_proposal(grown, "t4-rows", on_rows)
    preview, result = _preview(paths, "--policy", "additive", expect=3)
    _assert_refused(result, preview, "constraint.populated.add")


def test_t5_a_spanning_constraint_needs_every_existing_subject_unpopulated(grown: dict[str, Path]) -> None:
    raw1 = _document(1)
    flags = ("--policy", "additive", "--populated", POPULATED_FACT)
    new = (_new_fact("borrower_holds_loan"),)
    both_new = (_new_fact("borrower_holds_loan"), _new_fact("borrower_returns_loan"))
    cases = {
        "a-subset": (new, _subset(("borrower_holds_loan", "loan"), (POPULATED_FACT, "loan")), 3),
        "a-superset": (new, _subset((POPULATED_FACT, "loan"), ("borrower_holds_loan", "loan")), 3),
        "b-both-new": (both_new, _subset(("borrower_holds_loan", "loan"), ("borrower_returns_loan", "loan")), 0),
        "c-populated-and-unpopulated": ((), _subset(("loan_is_due_on", "loan"), (POPULATED_FACT, "loan")), 3),
    }
    for tag, (facts, constraint, expected) in cases.items():
        paths = _write_proposal(grown, f"t5-{tag}", _operations(_reply_one(facts, (constraint,)), raw1))
        preview, result = _preview(paths, *flags, expect=expected)
        if expected:
            index = len(facts)  # the constraint follows the fact-type additions
            _assert_refused(result, preview, "constraint.populated.add", index)
        else:
            assert preview is not None and preview["policy_issues"] == []
    # (c) without the flag nothing is populated: the same constraint is admitted.
    paths = _write_proposal(grown, "t5-c-control", _operations(_reply_one((), (cases["c-populated-and-unpopulated"][1],)), raw1))
    document, _ = _preview(paths, "--policy", "additive")
    assert document is not None and document["policy_issues"] == []


def test_t6_a_subtype_link_on_an_existing_type_is_refused(grown: dict[str, Path]) -> None:
    document = _current(grown)
    borrower = next(item for item in document["object_types"] if item["id"] == "borrower")
    party = {"id": "party", "name": "Party", "kind": "entity", "reference": copy.deepcopy(borrower["reference"]),
             "provenance": {"spans": [_span_of(_document(1), "Borrowers are tracked")]}}
    linked = {**copy.deepcopy(borrower), "subtype_of": ["party"], "inherits_reference": True}
    operations = (
        policy._op("add", policy._element("object_types", "party"), after=party, operation_id="add"),
        policy._op("modify", policy._element("object_types", "borrower"), before=borrower, after=linked,
                   operation_id="link"),
    )
    paths = _write_proposal(grown, "t6", operations)
    preview, result = _preview(paths, "--policy", "additive", expect=3)
    # The rule is the `object_types.modify` allow-list (the matrix cell) and unattended-growth.md.
    _assert_refused(result, preview, "object_types.modify", 1)
    # The same proposal without --policy is admitted: the refusal is the policy's, not the model's.
    paths = _write_proposal(grown, "t6-open", operations)
    document, _ = _preview(paths)
    assert document is not None and "policy_issues" not in document


# --- T7: apply must repeat the preview's options ----------------------------------------------------


def test_t7_apply_repeats_the_previews_options(grown: dict[str, Path]) -> None:
    operations = _operations(_reply_one((_new_fact("borrower_holds_loan"),)), _document(1))
    paths = _write_proposal(grown, "t7a", operations)
    _preview(paths, "--policy", "additive", "--populated", POPULATED_FACT)
    omitted = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert omitted.returncode == 3 and b"--populated" in omitted.stderr
    paths = _write_proposal(grown, "t7b", operations)
    _preview(paths, "--policy", "additive")
    dropped = run_main(policy._apply_argv(paths))
    assert dropped.returncode == 3 and b"--policy" in dropped.stderr
    paths = _write_proposal(grown, "t7c", operations)
    _preview(paths)
    added = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert added.returncode == 3 and b"--policy" in added.stderr


# --- T8-T11: the unattended source rules, through `gnd validate` ------------------------------------


def _seed_document() -> dict[str, Any]:
    return YAML(typ="safe").load(SEED.read_text(encoding="utf-8"))


def _write_model(directory: Path, document: dict[str, Any], name: str = "model.orm.yaml") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    with path.open("w", encoding="utf-8") as handle:
        YAML().dump(document, handle)
    return path


def _issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return payload["issues"]


def _rules(payload: dict[str, Any]) -> set[str]:
    return {issue["rule_id"] for issue in _issues(payload)}


def _first_constraint(document: dict[str, Any]) -> dict[str, Any]:
    return document["fact_types"][0]["constraints"][0]


def test_t8a_a_confirmed_element_is_refused(tmp_path: Path) -> None:
    document = _seed_document()
    _first_constraint(document)["status"] = "confirmed"
    payload = _validate(_write_model(tmp_path, document), expect=3)
    assert "semantic:unattended-u2" in _rules(payload)


@pytest.mark.parametrize("source", ["user-supplied", "explicit"])
def test_t8b_a_human_source_is_refused(tmp_path: Path, source: str) -> None:
    document = _seed_document()
    _first_constraint(document)["source"] = source
    payload = _validate(_write_model(tmp_path, document), expect=3)
    assert "semantic:unattended-u3" in _rules(payload)


def test_t8c_only_common_sense_may_cite_a_library_entry_instead_of_a_span(tmp_path: Path) -> None:
    document = _seed_document()
    common_sense = document["fact_types"][0]["constraints"][2]
    assert common_sense["source"] == "common-sense" and "spans" not in common_sense["provenance"]
    _validate(_write_model(tmp_path / "control", document))  # the documented deviation: it passes
    spanless = {"type": "uniqueness", "roles": ["customer"], "source": "llm-inferred", "status": "proposed",
                "modality": "deontic", "rationale": "No span.", "provenance": {"rationale_world_fact": "No span."}}
    document["fact_types"][1]["constraints"] = [spanless]
    payload = _validate(_write_model(tmp_path / "spanless", document), expect=3)
    assert "semantic:unattended-u5" in _rules(payload)


def test_t8d_the_header_names_no_reviewer_and_at_least_one_document(tmp_path: Path) -> None:
    document = _seed_document()
    document["source"]["reviewer"] = "someone"
    assert "semantic:unattended-u1" in _rules(_validate(_write_model(tmp_path / "reviewer", document), expect=3))
    document = _seed_document()
    document["source"]["documents"] = []
    assert "semantic:unattended-u1" in _rules(_validate(_write_model(tmp_path / "documents", document), expect=3))


def _grown_documents() -> tuple[Path, ...]:
    return (*[FIXTURES / f"round-{n}.txt" for n in (1, 2, 3)], SEED_DOCUMENT)


@pytest.mark.parametrize(("n", "collection", "element_id"),
                         [(1, "object_types", "loan"), (2, "fact_types", "loan_is_due_on"),
                          (3, "object_types", "staff_borrower")])
def test_t9_a_tampered_span_is_found_only_when_its_document_is_supplied(grown: dict[str, Path], tmp_path: Path, n: int,
                                                                        collection: str, element_id: str) -> None:
    document = _current(grown)
    element = next(item for item in document[collection] if item["id"] == element_id)
    span = element["provenance"]["spans"][0]
    assert span["document_sha256"] == sha256_bytes(_document(n))
    span["excerpt_sha256"] = "0" * 64
    model = _write_model(tmp_path, document)
    payload = _validate(model, _grown_documents(), expect=3)
    mismatches = [issue for issue in _issues(payload) if issue["rule_id"] == "unattended:excerpt-mismatch"]
    assert [issue["path"] for issue in mismatches] == [f"$.{collection}[id={element_id}].provenance.spans[0]"]
    # Pinned O14 deviation: a tampered span on a document the caller did not supply passes (exit 0), and so does
    # a run with no --document at all. UG3 (ii) adds an opt-in strict flag; the default is not changed.
    omitted = tuple(path for path in _grown_documents() if path != FIXTURES / f"round-{n}.txt")
    _validate(model, omitted)
    _validate(model)


def test_t10_a_span_naming_an_undeclared_document_is_refused(tmp_path: Path) -> None:
    document = _seed_document()
    document["object_types"][0]["provenance"]["spans"][0]["document_sha256"] = "f" * 64
    assert "semantic:unattended-u7" in _rules(_validate(_write_model(tmp_path, document), expect=3))


def test_t11_model_issues_come_first_and_documents_are_read_only_for_a_valid_model(grown: dict[str, Path],
                                                                                  tmp_path: Path) -> None:
    document = _current(grown)
    document["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"] = "0" * 64  # would also be refused by --document
    next(item for item in document["fact_types"] if item["id"] == "loan_is_due_on")["provenance"]["spans"][0][
        "document_sha256"] = "f" * 64  # the model rule that comes first
    payload = _validate(_write_model(tmp_path, document), _grown_documents(), expect=3)
    # Model rules are `semantic:unattended-uN`; the document-level ones start with the exact prefix `unattended:`.
    assert "semantic:unattended-u7" in _rules(payload)
    assert not [rule for rule in _rules(payload) if rule.startswith("unattended:")]


# --- T12: a round cannot declare its own document through evolve (O20) -------------------------------


def test_t12_declaring_a_document_inside_a_round_is_refused_but_before_it_is_admitted(tmp_path: Path) -> None:
    from gnd.discover import output
    from gnd.evolve import CommittedText

    ws = _workspace(tmp_path / "a")
    raw = _document(1)
    text = ws["model"].read_text(encoding="utf-8")
    proposal = policy._proposal(text, _operations(ROUND_1, raw), proposal_id="ug1-t12a")
    candidate = YAML(typ="safe").load(proposal.candidate_model.text)
    candidate["source"]["documents"].append({"sha256": sha256_bytes(raw), "label": "round-1.txt"})
    declared = proposal.model_copy(update={"candidate_model": CommittedText.from_text(
        output.candidate_text(candidate), media_type="application/yaml")})
    paths = _round_paths(ws, "t12a")
    paths["proposal"].write_text(json.dumps(declared.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    # (a) Pinned gap, not a wish: no operation locator reaches `source`, so the replay equality refuses it.
    # UG3 (i) (UG-D9 (b)) will change this message and must edit this assertion knowingly.
    _document_after, result = _preview(paths, "--policy", "additive", expect=3)
    assert b"declared operations do not equal the canonical candidate model" in result.stderr
    assert ws["model"].read_text(encoding="utf-8") == text
    # (b) Declared in the model before the round, after an earlier round was applied: admitted.
    ws = _workspace(tmp_path / "b")
    previews = [_round(ws, n, reply) for n, reply in ((1, ROUND_1), (2, ROUND_2))]
    assert [preview["policy_issues"] for preview in previews] == [[], []]


# --- T13: defaults do not move: the policy is the flag, nothing else ----------------------------------


def test_t13_the_same_rename_is_admitted_without_the_flag_and_refused_with_it(grown: dict[str, Path],
                                                                            monkeypatch: pytest.MonkeyPatch) -> None:
    document = _current(grown)
    element = next(item for item in document["object_types"] if item["id"] == "staff_borrower")
    operations = (policy._op("rename", policy._element("object_types", "staff_borrower"), before=element,
                             after=policy._modified(element, id="staff_member")),)
    paths = _write_proposal(grown, "t13", operations)
    preview, _ = _preview(paths)
    assert preview is not None and preview["breaking"] is True
    assert "policy" not in preview and "policy_issues" not in preview
    # A breaking apply of the policy-free preview prompts for the digest; EOF exits 11 (measured, no band).
    eof = _apply_breaking(monkeypatch, paths, preview, eof=True)
    assert eof.returncode == 11 and b"requires exact blast radius acceptance" in eof.stderr
    paths = _write_proposal(grown, "t13-policy", operations)
    refused, result = _preview(paths, "--policy", "additive", expect=3)
    _assert_refused(result, refused, "object_types.rename")
    # A shape match is advice: the preview still exits 0 and `apply` rebuilds the report from the proposal.
    restated = _fact("loan_is_due_by", "{Loan} is due by {DueDate}", ("loan", "due_date"), "A borrower holds a laptop")
    paths = _write_proposal(grown, "t13-shape", _operations(_reply_one((restated,)), _document(1)))
    shaped, _ = _preview(paths, "--policy", "additive", "--shape-report")
    assert shaped is not None and shaped["policy_issues"] == []
    assert [m["fact_type"] for g in shaped["shape_matches"] for m in g["existing"]] == [POPULATED_FACT, "loan_is_due_on"]
    assert run_main(policy._apply_argv(paths, "--policy", "additive")).returncode == 0


# --- T14: refusal messages carry no document text and no sample value -----------------------------------

DOC_CANARY = "ZXQ-DOC-CANARY"
ROW_CANARY = "ZXQ-ROW-CANARY"
MODEL_CARRYING_KEYS = ("before_model", "candidate_model", "proposal", "verbalization", "blast_radius")


def test_t14_no_document_text_or_sample_value_in_what_the_replay_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = _workspace(tmp_path / "ws")
    raw = (f"Widgets are tracked by widget code. Widget {DOC_CANARY} is stored in a bin.\n"
           f"Bins are tracked by bin code. Row {ROW_CANARY} is one stored widget.\n").encode()
    reply = {
        "document": "canary.txt",
        "object_types": [_entity("widget", "Widget", "widget_code", "Widgets are tracked"),
                         _value("widget_code", "WidgetCode", "String", "widget code"),
                         _entity("bin", "Bin", "bin_code", "Bins are tracked"),
                         _value("bin_code", "BinCode", "String", "bin code")],
        "fact_types": [{**_fact("widget_in_bin", "{Widget} is stored in {Bin}", ("widget", "bin"), "is stored in a bin"),
                        "rows": [{"values": {"widget": ROW_CANARY, "bin": "B-1"}, "quote": "is one stored widget"}]}],
        "subtype_links": [], "constraints": [],
    }
    declared = ws["workspace"] / "canary.txt"
    declared.write_bytes(raw)
    _declare(ws["model"], raw, "canary.txt")
    paths = _write_proposal(ws, "t14-add", _operations(reply, raw))
    _preview(paths, "--policy", "additive")
    assert run_main(policy._apply_argv(paths, "--policy", "additive")).returncode == 0
    document = _current(ws)
    element = next(item for item in document["fact_types"] if item["id"] == "widget_in_bin")
    assert element["sample_population"][0]["widget"] == ROW_CANARY
    refusals = (
        policy._op("add", policy._constraint_locator("widget_in_bin", None, "uniqueness"), operation_id="late",
                   after=_constraint({"type": "uniqueness", "roles": ["widget"]}, raw, "is stored in a bin")),
        policy._op("rename", policy._element("fact_types", "widget_in_bin"), before=element,
                   after=policy._modified(element, id="widget_in_crate"), operation_id="rename"),
    )
    seen: list[bytes] = []
    for tag, operation in (("late", refusals[0]), ("rename", refusals[1])):
        paths = _write_proposal(ws, f"t14-{tag}", (operation,))
        preview, result = _preview(paths, "--policy", "additive", expect=3)
        assert preview is not None and preview["policy_issues"]
        # Positive control: the sample value does sit in the keys the scan excludes, so the scan can see it.
        assert ROW_CANARY in json.dumps({k: v for k, v in preview.items() if k in MODEL_CARRYING_KEYS})
        seen += [result.stderr, json.dumps([issue["detail"] for issue in preview["policy_issues"]]).encode(),
                 json.dumps({k: v for k, v in preview.items() if k not in MODEL_CARRYING_KEYS}).encode()]
        if tag == "rename":
            applied = _apply_breaking(monkeypatch, paths, preview, "--policy", "additive")
            seen.append(applied.stderr)
    tampered = _current(ws)
    tampered["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"] = "0" * 64
    result = run_main(["validate", str(_write_model(tmp_path / "bad", tampered)), "--document", str(declared),
                       "--format", "json"])
    seen += [result.stdout, result.stderr]
    for text in seen:
        assert DOC_CANARY.encode() not in text and ROW_CANARY.encode() not in text
    assert seen and all(isinstance(text, bytes) for text in seen)
