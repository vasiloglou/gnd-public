"""VG4 (reviewed-vocabulary-growth): growth rounds on an unattended root that includes a reviewed vocabulary.

Issue 222, case 3. The spec is
``.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG4-spec.md``;
the test names are its section 8 rows. The root is VG3's (``tests/vg3_cases.py``).
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import vg3_cases as cases
from support.cli_runner import run_main

from gnd.model._unattended import _INCLUDED, _rule_unattended

REPO = Path(__file__).resolve().parents[1]
DIGEST = hashlib.sha256(cases.DOCUMENT.encode()).hexdigest()
U1_DOCUMENTS = "an unattended model must declare at least one source document"


def _op(kind: str, locator, after=None, before=None, oid: str = "op"):
    from gnd.evolve import EvolutionOperation, EvolutionOperationKind

    return EvolutionOperation(operation_id=oid, kind=EvolutionOperationKind(kind), locator=locator,
                              before=before, after=after)


def _proposal(root: Path, operations: tuple, proposal_id: str = "vg4", *, replay: bool = True):
    """A proposal over ROOT. Without REPLAY the candidate is the authored root unchanged: an
    operation on an included element cannot be replayed on the authored file, and ownership
    is refused before the candidate is read (evolution contract, "Shared vocabulary evolution")."""
    from gnd.discover import output
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal
    from gnd.model import parse_model_document

    text = root.read_text()
    candidate_text = text
    if replay:
        candidate = output.candidate_document(parse_model_document(text.encode(), source=root), operations)
        candidate_text = output.candidate_text(candidate)
    return EvolutionProposal(
        schema_version=3, proposal_id=proposal_id,
        expected_model_sha256=hashlib.sha256(text.encode()).hexdigest(),
        candidate_model=CommittedText.from_text(candidate_text, media_type="application/yaml"),
        operations=operations, rationale="A VG4 round.",
        audit=EvolutionOperationAudit(actor_id="agent:vg4", origin="test_vg4_seeded_growth_rounds",
                                      requested_at=datetime(2026, 11, 23, tzinfo=UTC)))


def _service(root: Path):
    from gnd.evolve import EvolutionService

    return EvolutionService(model_path=root, evidence_root=root.parent / "records", allowed_project_root=root.parent)


def _undocumented(directory: Path, **own) -> Path:
    """Issue 222's root with no ``documents`` key."""
    root = cases.write(directory, **own)
    doc = json.loads(root.read_text())
    doc["source"].pop("documents")
    root.write_text(json.dumps(doc))
    return root


def _first_document():
    from gnd.evolve import SourceDocumentLocator

    return _op("add", SourceDocumentLocator(sha256=DIGEST), after={"sha256": DIGEST, "label": cases.DOC}, oid="doc")


AUTHOR = {"id": "author", "kind": "value", "primitive": "String",
          "provenance": {"spans": [cases.span("An author writes works")]}}
ATTACHED = {"type": "mandatory", "role": "work", "source": "llm-inferred", "status": "proposed",
            "modality": "deontic", "rationale": "r",
            "provenance": {"rationale_world_fact": "w", "spans": [cases.span("Each version belongs to one work")]}}


def _owned_round():
    from gnd.evolve import ConstraintLocator, ElementLocator

    writes = {"id": "author_writes_work", "reading": "{Author} writes {WorkKey}",
              "roles": [{"object_type": "author", "role_name": "author"},
                        {"object_type": "work", "role_name": "work"}],
              "sample_population": [{"author": "a1", "work": "w1"}],
              "provenance": {"spans": [cases.span("An author writes works")],
                             "sample_spans": [{"row": 0, "span": cases.span("An author writes works")}]}}
    return (_op("add", ElementLocator(collection="object_types", element_id="author"), after=AUTHOR, oid="author"),
            _op("add", ElementLocator(collection="fact_types", element_id="author_writes_work"), after=writes,
                oid="writes"),
            _op("add", ConstraintLocator(host="included_fact_type", host_id="work_has_version", family="mandatory"),
                after=ATTACHED, oid="attach"))


def _documented_validate(root: Path) -> int:
    return run_main(["validate", str(root), "--document", str(root.parent / cases.DOC), "--require-documents"]
                    ).returncode


# --- T1 (VG4-C1): a round on the VG3 root -------------------------------------


def test_T1_a_round_adds_owned_elements_and_an_attached_constraint(tmp_path):
    root = cases.write(tmp_path / "ws")
    service = _service(root)
    reviewed = service.preview(_proposal(root, _owned_round()), policy="additive")
    assert reviewed.policy_issues == ()
    record = service.finalize(service.apply(reviewed))
    assert record.new_model_sha256 == hashlib.sha256(root.read_bytes()).hexdigest()
    authored = json.loads(root.read_text()) if root.read_text().lstrip().startswith("{") else None
    published = root.read_text()
    assert "author_writes_work" in published and "fact_type_constraints" in published
    assert authored is None or "work_has_version" not in [f["id"] for f in authored.get("fact_types", [])]
    assert _documented_validate(root) == 0


# --- T2 (VG4-C2): included elements stay read-only ----------------------------


def _included_operations():
    from gnd.evolve import ConstraintLocator, ElementLocator, canonical_sha256

    seed = cases.seed()
    work = seed["object_types"][0]
    fact = seed["fact_types"][0]
    constraint = fact["constraints"][0]
    element = ElementLocator(collection="object_types", element_id="work")
    on_fact = ElementLocator(collection="fact_types", element_id="work_has_version")
    on_constraint = ConstraintLocator(host="fact_type", host_id="work_has_version", family="uniqueness",
                                      canonical_before_sha256=canonical_sha256(constraint))
    return {
        "modify-object-type": _op("modify", element, before=work, after=dict(work, name="Work")),
        "rename-object-type": _op("rename", element, before=work, after=dict(work, id="opus")),
        "delete-fact-type": _op("delete", on_fact, before={k: v for k, v in fact.items() if k != "constraints"}),
        "delete-constraint": _op("delete", on_constraint, before=constraint),
    }


@pytest.mark.parametrize("name", sorted(_included_operations()))
def test_T2_an_operation_on_an_included_element_is_refused(tmp_path, name):
    from gnd.evolve import EvolutionIncludeError

    root = cases.write(tmp_path / "ws")
    operation = _included_operations()[name]
    with pytest.raises(EvolutionIncludeError, match="evolve:included-element"):
        _service(root).preview(_proposal(root, (operation,), replay=False))


# --- T3 (VG4-C3): the first document --------------------------------------------


def test_T3_a_root_with_includes_and_nothing_of_its_own_validates_without_documents(tmp_path):
    root = _undocumented(tmp_path / "ws")
    assert run_main(["validate", str(root)]).returncode == 0


def test_T3_its_first_round_declares_the_document_and_adds_an_element(tmp_path):
    root = _undocumented(tmp_path / "ws")
    service = _service(root)
    reviewed = service.preview(_proposal(root, (_first_document(), *_owned_round())), policy="additive")
    assert reviewed.policy_issues == ()
    service.finalize(service.apply(reviewed))
    assert _documented_validate(root) == 0


OWNED = {
    "object-type": {"object_types": [AUTHOR]},
    "fact-type": {"fact_types": [{"id": "f", "reading": "{WorkKey} is f", "roles": [
        {"object_type": "work", "role_name": "work"}]}]},
    "attached-constraint": {"fact_type_constraints": [{"fact_type": "work_has_version", "constraints": [ATTACHED]}]},
    "top-level-constraint": {"constraints": [{**{k: v for k, v in ATTACHED.items() if k != "role"},
                                              "type": "value", "object_type": "work", "allowed": ["w1"]}]},
    "deontic-note": {"deontic_notes": [{"text": "Works should be dated."}]},
}


@pytest.mark.parametrize("name", sorted(OWNED))
def test_T3_a_root_that_owns_anything_keeps_U1(tmp_path, name):
    root = _undocumented(tmp_path / "ws", **OWNED[name])
    result = run_main(["validate", str(root), "--format", "json"])
    issues = [(i["rule_id"], i["message"]) for i in json.loads(result.stdout)["issues"]]
    assert result.returncode == 3
    assert ("semantic:unattended-u1", U1_DOCUMENTS) in issues, issues


def _rule_issues(doc: dict, included: frozenset[int]) -> list[tuple[str, str]]:
    token = _INCLUDED.set(included)
    try:
        return [(issue.rule_id, issue.message) for issue in _rule_unattended(doc)]
    finally:
        _INCLUDED.reset(token)


def _composed(**own) -> tuple[dict, frozenset[int]]:
    """A composed root at the rule: the seed's elements appended and marked included."""
    doc = cases.root(b"x")
    doc["source"].pop("documents")
    seed = cases.seed()
    doc["object_types"] = list(seed["object_types"])
    doc["fact_types"] = list(seed["fact_types"])
    included = {id(row) for row in doc["object_types"] + doc["fact_types"]}
    included |= {id(c) for row in doc["fact_types"] for c in row["constraints"]}
    doc.update(own)
    return doc, frozenset(included)


@pytest.mark.parametrize("own", [
    {"operations": [{"id": "op", "status": "proposed", "source": "llm-inferred"}]},
    {"operations": [{"id": "op", "postconditions": [{"id": "ob"}]}]},
    {"rejected_proposals": [{"type": "ring", "status": "rejected"}]},
    {"reference_populations": [{"id": "r"}]},
], ids=["operation", "operation-with-obligation", "rejected-proposal", "reference-population"])
def test_T3_sections_an_include_cannot_hold_keep_U1_at_the_rule(own):
    doc, included = _composed(**own)
    assert ("semantic:unattended-u1", U1_DOCUMENTS) in _rule_issues(doc, included)
    bare, bare_included = _composed()
    assert ("semantic:unattended-u1", U1_DOCUMENTS) not in _rule_issues(bare, bare_included)


@pytest.mark.parametrize(("change", "message"), [
    (lambda s: s.pop("reviewer"), "an unattended model must declare reviewer: none"),
    (lambda s: s.update(reviewer="owner"), "an unattended model must declare reviewer: none"),
    (lambda s: s.update(documents="doc.md"), U1_DOCUMENTS),
], ids=["reviewer-absent", "reviewer-not-none", "documents-not-a-list"])
def test_T3_the_header_still_keeps_U1(change, message):
    doc, included = _composed()
    change(doc["source"])
    assert ("semantic:unattended-u1", message) in _rule_issues(doc, included)


def test_T3_an_unattended_model_without_includes_keeps_U1():
    doc = {"version": 4, "source": {"kind": "prose", "mode": "unattended", "reviewer": "none"},
           "object_types": [], "fact_types": []}
    assert ("semantic:unattended-u1", U1_DOCUMENTS) in _rule_issues(doc, frozenset())


# --- T4 (VG4-C4): no re-pin on an unattended root -----------------------------


def _repin(root: Path):
    from gnd.evolve import IncludeLocator

    doc = json.loads(root.read_text())
    before = dict(doc["includes"][0])
    after = dict(before, sha256="f" * 64)
    return _op("repin-include", IncludeLocator(include_id="seed"), before=before, after=after, oid="repin")


@pytest.mark.parametrize("policy", [None, "additive"])
def test_T4_repin_include_on_an_unattended_root_is_refused_under_every_policy(tmp_path, policy):
    from gnd.evolve import EvolutionIncludeError

    root = cases.write(tmp_path / "ws")
    with pytest.raises(EvolutionIncludeError, match="evolve:unattended-repin: "):
        _service(root).preview(_proposal(root, (_repin(root),), replay=False), policy=policy)


def test_T4_control_a_root_without_the_mode_gets_todays_answer(tmp_path):
    from gnd.evolve import EvolutionError

    root = cases.write(tmp_path / "ws", unattended=False)
    with pytest.raises(EvolutionError) as caught:
        _service(root).preview(_proposal(root, (_repin(root),), replay=False), policy="additive")
    assert "evolve:unattended-repin" not in str(caught.value)


# --- T5 (VG4-C5): --populated and --check-population ------------------------


def test_T5_populated_refuses_an_attached_constraint_as_on_any_model(tmp_path):
    root = cases.write(tmp_path / "ws")
    reviewed = _service(root).preview(_proposal(root, _owned_round()[2:]), policy="additive",
                                      populated=("work_has_version",))
    assert [issue.cell for issue in reviewed.policy_issues] == ["constraint.populated.add"]


def test_T5_check_population_reads_the_composed_root(tmp_path):
    root = cases.write(tmp_path / "ws")
    population = root.parent / "population.json"
    population.write_text(json.dumps({
        "population": {"source": "fixture", "model": cases.ROOT, "model_id": "urn:example:growth",
                       "covers": ["work_has_version"]},
        "instances": {"work": ["w1", "w2"]},
        "facts": {"work_has_version": [{"work": "w1", "version": "v1"}]}}))
    reviewed = _service(root).preview(_proposal(root, _owned_round()[2:]), policy="additive",
                                      check_population=str(population))
    assert reviewed.population_check is not None


# --- T6: the pages ----------------------------------------------------------------


def test_T6_the_pages_state_the_first_document_rule_and_the_repin_refusal():
    page = (REPO / "src/gnd/skills/gnd-orm-core/references/representation-format.md").read_text()
    contract = (REPO / "src/gnd/skills/gnd-model-evolve/references/evolution-contract.md").read_text()
    assert "may wait for its first document" in page
    assert "`evolve:unattended-repin: <reference>`, exit `3`" in contract


# --- review round 1 (notes/reviews/phase-VG4-r1), regression case ------------


def test_R1_F1_a_null_documents_value_keeps_U1(tmp_path):
    """F1: ``documents: null`` passed U1 but the first round could not append to it."""
    root = _undocumented(tmp_path / "ws")
    doc = json.loads(root.read_text())
    doc["source"]["documents"] = None
    root.write_text(json.dumps(doc))
    result = run_main(["validate", str(root), "--format", "json"])
    issues = [(i["rule_id"], i["message"]) for i in json.loads(result.stdout)["issues"]]
    assert result.returncode == 3
    assert ("semantic:unattended-u1", U1_DOCUMENTS) in issues, issues
