"""UG3 part B: a source-document operation locator on gnd evolve.

Spec: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG3-spec.md
(§6.3 to §6.6, §8 part B, §11). Approval instrument: corpus-first (UG3-D14
(a)). The corpus is tests/fixtures/unattended-model-growth/ug3/: README.md
narrates each case without its outcome, expected.json is the answer key
("part_b"), parity-baseline.json ("part_b") was captured on 5c6a0c5f before the
first source edit.

The corpus cases (B1 to B8) are red until part B lands: SourceDocumentLocator
does not exist on the base, so building a case's proposal fails. The parity
test (B9) and the schema-version control are green on the base and must stay
green. Set GND_UG3_CAPTURE=1 to rewrite the baseline; only ever on the base
commit named above. Builders are local (UG1's refactoring note).
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "unattended-model-growth" / "ug3"
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))["part_b"]
BASELINE_PATH = CORPUS / "parity-baseline.json"
ROUNDS = CORPUS / "models" / "rounds.orm.yaml"
PLAIN = CORPUS / "models" / "plain.orm.yaml"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


LEDGER = _sha((CORPUS / "documents" / "ledger.txt").read_bytes())
ANNEX = _sha((CORPUS / "documents" / "annex.txt").read_bytes())
ROUND = _sha((CORPUS / "documents" / "round.txt").read_bytes())


def _span(name: str, excerpt: str) -> dict[str, Any]:
    import unicodedata

    raw = (CORPUS / "documents" / name).read_bytes()
    text = unicodedata.normalize("NFC", raw.decode("utf-8"))
    start = text.index(excerpt)
    return {"document_sha256": _sha(raw), "start": start, "end": start + len(excerpt),
            "excerpt_sha256": _sha(excerpt.encode("utf-8"))}


INVOICE_NO = {"id": "invoice_no", "name": "InvoiceNo", "kind": "value", "primitive": "Integer",
              "provenance": {"spans": [_span("round.txt", "invoice number")]}}
LEDGER_NOTE = {"id": "ledger_no", "name": "LedgerNo", "kind": "value", "primitive": "Integer",
               "provenance": {"spans": [_span("ledger.txt", "ledger of customers")]}}


# --- builders ---------------------------------------------------------------


def _doc(path: Path) -> dict[str, Any]:
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


def _op(kind: str, locator: Any, *, before: Any = None, after: Any = None, operation_id: str = "op-0") -> Any:
    from gnd.evolve import EvolutionOperation, EvolutionOperationKind

    return EvolutionOperation(operation_id=operation_id, kind=EvolutionOperationKind(kind), locator=locator,
                              before=copy.deepcopy(before), after=copy.deepcopy(after))


def _element(kind: str, collection: str, element_id: str, *, before: Any = None, after: Any = None,
             operation_id: str = "op-0") -> Any:
    from gnd.evolve import ElementLocator

    return _op(kind, ElementLocator(collection=collection, element_id=element_id), before=before, after=after,
               operation_id=operation_id)


def _declaration(kind: str, sha256: str, *, before: Any = None, after: Any = None,
                 operation_id: str = "op-0") -> Any:
    """A source-document operation. Red on the base: the locator does not exist there."""
    from gnd.evolve import SourceDocumentLocator  # type: ignore[attr-defined]

    return _op(kind, SourceDocumentLocator(locator_kind="source-document", sha256=sha256), before=before,
               after=after, operation_id=operation_id)


def _declared_candidate(before: dict[str, Any], operations: tuple[Any, ...]) -> dict[str, Any]:
    """The candidate the narration describes, written independently of the service's replay.

    Element operations go through discover's replay (shipped); declarations are applied
    here by hand to ``source.documents``, in operation order.
    """
    from gnd.discover import output

    elements = tuple(op for op in operations if op.locator.locator_kind != "source-document")
    candidate = output.candidate_document(before, elements) if elements else copy.deepcopy(before)
    for op in operations:
        if op.locator.locator_kind != "source-document":
            continue
        documents = candidate.setdefault("source", {}).setdefault("documents", [])
        sha256 = op.locator.sha256
        if op.kind.value == "add":
            documents.append(dict(op.after))
        elif op.kind.value == "modify":
            documents[[entry["sha256"] for entry in documents].index(sha256)] = dict(op.after)
        elif op.kind.value == "delete":
            documents.remove(next(entry for entry in documents if entry["sha256"] == sha256))
    return candidate


def _proposal(base: Path, operations: tuple[Any, ...], proposal_id: str, *,
              candidate: dict[str, Any] | None = None) -> Any:
    from gnd.discover import output
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal

    text = base.read_text(encoding="utf-8")
    document = candidate if candidate is not None else _declared_candidate(_doc(base), operations)
    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=_sha(text.encode("utf-8")),
        candidate_model=CommittedText.from_text(output.candidate_text(document), media_type="application/yaml"),
        operations=operations,
        rationale="UG3 corpus case.",
        audit=EvolutionOperationAudit(actor_id="owner:fixture", origin="test_evolve_source_document",
                                      requested_at=datetime(2026, 11, 9, 12, 0, tzinfo=UTC)),
    )


def _round_add() -> Any:
    return _declaration("add", ROUND, after={"sha256": ROUND, "label": "round.txt"})


def _annex(label: str = "annex.txt") -> dict[str, str]:
    return {"sha256": ANNEX, "label": label}


def _ledger() -> dict[str, str]:
    return {"sha256": LEDGER, "label": "ledger.txt"}


def _mutated(proposal: Any, mutate: Any) -> dict[str, Any]:
    """The proposal's JSON with one hand edit, for shapes the closed model would refuse to build."""
    data = proposal.model_dump(mode="json")
    mutate(data)
    return data


def _case(case_id: str) -> tuple[Path, dict[str, Any]]:
    """(starting model, proposal JSON) of each corpus case. README.md tells the same stories."""
    b1 = (_round_add(), _element("add", "object_types", "invoice_no", after=INVOICE_NO, operation_id="op-1"))
    if case_id == "B1":
        return ROUNDS, _proposal(ROUNDS, b1, "ug3-b1").model_dump(mode="json")
    if case_id == "B2":
        ops = (_declaration("modify", ANNEX, before=_annex(), after=_annex("annex-2025.txt")),)
        return ROUNDS, _proposal(ROUNDS, ops, "ug3-b2").model_dump(mode="json")
    if case_id == "B3a":
        return ROUNDS, _proposal(ROUNDS, (_declaration("delete", ANNEX, before=_annex()),), "ug3-b3a").model_dump(
            mode="json")
    if case_id == "B3b":
        return ROUNDS, _proposal(ROUNDS, (_declaration("delete", LEDGER, before=_ledger()),), "ug3-b3b").model_dump(
            mode="json")
    if case_id == "B4":
        return ROUNDS, _proposal(ROUNDS, (_declaration("add", LEDGER, after=_ledger()),), "ug3-b4").model_dump(
            mode="json")
    if case_id in {"B5a", "B5b", "B5c"}:
        valid = _proposal(ROUNDS, b1, f"ug3-{case_id.lower()}")
        edits = {
            "B5a": lambda data: data["operations"][0]["locator"].update(sha256="ABC"),
            "B5b": lambda data: data["operations"][0]["after"].update(sha256=ANNEX),
            "B5c": lambda data: data["operations"][0]["after"].update(note="third key"),
        }
        return ROUNDS, _mutated(valid, edits[case_id])
    if case_id == "B6":
        valid = _proposal(ROUNDS, (_declaration("modify", ANNEX, before=_annex(), after=_annex("annex-2025.txt")),),
                          "ug3-b6")
        return ROUNDS, _mutated(valid, lambda data: data["operations"][0].update(kind="rename"))
    if case_id in {"B7a", "B7b"}:
        valid = _proposal(ROUNDS, (_round_add(),), f"ug3-{case_id.lower()}")
        version = 1 if case_id == "B7a" else 2
        return ROUNDS, _mutated(valid, lambda data: data.update(schema_version=version))
    if case_id == "B8":
        return PLAIN, _proposal(PLAIN, (_round_add(),), "ug3-b8").model_dump(mode="json")
    raise KeyError(case_id)


def _workspace(root: Path, base: Path, proposal: dict[str, Any]) -> dict[str, Path]:
    root.mkdir(parents=True)
    (root / "records").mkdir()
    model = root / "model.orm.yaml"
    shutil.copyfile(base, model)
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    proposal_path = root / "proposal.json"
    proposal_path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"workspace": root, "model": model, "records": root / "records", "proposal": proposal_path,
            "preview": root / "preview.json"}


def _preview(paths: dict[str, Path], flags: list[str]) -> Any:
    return run_main(["evolve", "preview", str(paths["model"]), str(paths["proposal"]), "--workspace",
                     str(paths["workspace"]), "--records", str(paths["records"]), "--out", str(paths["preview"]),
                     "--format", "json", *flags])


def _apply(paths: dict[str, Path], flags: list[str]) -> Any:
    return run_main(["evolve", "apply", str(paths["model"]), str(paths["proposal"]), "--preview",
                     str(paths["preview"]), "--workspace", str(paths["workspace"]), "--records",
                     str(paths["records"]), "--format", "json", *flags])


# --- the corpus: B1 to B8, judged against expected.json ----------------------


def _assert_preview(result: Any, paths: dict[str, Path], step: dict[str, Any], stage: str) -> None:
    stderr = result.stderr.decode()
    assert result.returncode == step["exit"], (stage, result.returncode, stderr)
    for needle in step.get("stderr_contains", ()):
        assert needle in stderr, (stage, needle, stderr)
    if not step["preview_written"]:
        assert not paths["preview"].exists(), stage
        return
    preview = json.loads(paths["preview"].read_text(encoding="utf-8"))
    issues = preview.get("policy_issues") or []
    if "issue" in step:
        assert len(issues) == 1, issues
        assert {"operation_index": issues[0]["operation_index"], "cell": issues[0]["cell"]} == step["issue"]
    else:
        assert issues == [], issues


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_corpus_case(tmp_path: Path, case_id: str) -> None:
    case = EXPECTED[case_id]
    base, proposal = _case(case_id)
    for stage in ("preview_without_policy", "preview"):
        if stage not in case:
            continue
        paths = _workspace(tmp_path / stage, base, proposal)
        model_before = paths["model"].read_bytes()
        _assert_preview(_preview(paths, case[stage]["flags"]), paths, case[stage], stage)
        assert paths["model"].read_bytes() == model_before
    if "apply" not in case:
        return
    result = _apply(paths, case["apply"]["flags"])
    assert result.returncode == case["apply"]["exit"], result.stderr.decode()
    published = _doc(paths["model"])
    assert [entry["label"] for entry in published["source"]["documents"]] == case["published_documents"]
    check = case["validate_after"]
    argv = ["validate", str(paths["model"]), "--format", "json"]
    for name in check["documents"]:
        argv += ["--document", str(CORPUS / "documents" / name)]
    validated = run_main(argv)
    assert validated.returncode == check["exit"], validated.stdout.decode()
    payload = json.loads(validated.stdout)
    assert payload["warnings"] == check["warnings"]
    assert (payload["issues"] or []) == check["issues"]


def test_b7_control_old_schema_versions_parse_and_reach_the_version_gate(tmp_path: Path) -> None:
    """B7 is not vacuous. A v1 or v2 proposal with an ordinary operation is read, and then
    preview refuses it as read-only compatibility evidence (70, green on the base). So a 3 in
    B7 can only come from reading the proposal, before that gate (UG3-D10 (a))."""
    for version in (1, 2):
        proposal = _proposal(ROUNDS, (_element("add", "object_types", "ledger_no", after=LEDGER_NOTE),),
                             f"ug3-b7-control-v{version}").model_dump(mode="json")
        proposal["schema_version"] = version
        paths = _workspace(tmp_path / f"v{version}", ROUNDS, proposal)
        result = _preview(paths, ["--policy", "additive"])
        assert result.returncode == 70, result.stderr.decode()
        assert "versions 1 and 2 are read-only compatibility evidence" in result.stderr.decode()


# --- B9: proposals without the locator keep their bytes (UG-R1) --------------


def _parity_proposals() -> dict[str, Any]:
    return {
        "add-object-type": _proposal(ROUNDS, (_element("add", "object_types", "ledger_no", after=LEDGER_NOTE),),
                                     "ug3-parity-add"),
        # The O20 gap as it stands: the element cites round.txt, which nothing declares.
        "add-citing-undeclared": _proposal(ROUNDS, (_element("add", "object_types", "invoice_no",
                                                             after=INVOICE_NO),), "ug3-parity-undeclared"),
        "delete-fact-type": _proposal(
            ROUNDS, (_element("delete", "fact_types", "customer_listed",
                              before=next(f for f in _doc(ROUNDS)["fact_types"] if f["id"] == "customer_listed")),),
            "ug3-parity-delete"),
    }


def _parity_rows(tmp_path: Path) -> list[dict[str, Any]]:
    rows = []
    for name, proposal in _parity_proposals().items():
        data = proposal.model_dump(mode="json")
        for flags in ([], ["--policy", "additive"]):
            paths = _workspace(tmp_path / f"{name}-{len(flags)}", ROUNDS, data)
            result = _preview(paths, flags)
            rows.append({"proposal": name, "flags": flags, "exit": result.returncode,
                         "proposal_sha256": proposal.proposal_sha256,
                         "proposal_file_sha256": _sha(paths["proposal"].read_bytes()),
                         "preview_sha256": _sha(paths["preview"].read_bytes()) if paths["preview"].exists() else None})
    return rows


def test_b9_capture_or_compare_the_locator_free_baseline(tmp_path: Path) -> None:
    rows = _parity_rows(tmp_path)
    if os.environ.get("GND_UG3_CAPTURE"):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.exists() else {}
        baseline["part_b"] = {"base": "5c6a0c5f", "rows": rows}
        BASELINE_PATH.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return
    base_rows = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["part_b"]["rows"]
    assert rows == base_rows
    # Each kind of outcome is represented, so the comparison can move.
    assert {row["exit"] for row in base_rows} == {0, 3}
    assert any(row["preview_sha256"] is None for row in base_rows)


# --- B10 to B16: the spec's successor cases beyond the approved corpus --------


def test_b10_a_declaration_without_an_operation_is_still_refused(tmp_path: Path) -> None:
    """UG1 T12 (a) unchanged: the candidate declares round.txt, but no operation says so."""
    element = _element("add", "object_types", "invoice_no", after=INVOICE_NO)
    candidate = _declared_candidate(_doc(ROUNDS), (_round_add(), element))
    proposal = _proposal(ROUNDS, (element,), "ug3-b10", candidate=candidate).model_dump(mode="json")
    paths = _workspace(tmp_path / "ws", ROUNDS, proposal)
    result = _preview(paths, ["--policy", "additive"])
    assert result.returncode == 3
    assert b"declared operations do not equal the canonical candidate model" in result.stderr
    assert not paths["preview"].exists()


def test_b11_a_locator_kind_without_a_policy_rule_is_refused_by_type() -> None:
    from gnd.evolve import (
        EvolutionOperation,
        EvolutionOperationKind,
        EvolutionPolicyGapError,
        EvolutionProposal,
        SourceDocumentLocator,
    )
    from gnd.evolve.cli_service import _evolve_error_exit
    from gnd.evolve.policy import additive_policy_issues
    from gnd.model import load_model

    forged = SourceDocumentLocator.model_construct(locator_kind="forged", sha256=ROUND)
    operation = EvolutionOperation.model_construct(operation_id="op-0", kind=EvolutionOperationKind.ADD,
                                                   locator=forged, before=None, after=None)
    proposal = EvolutionProposal.model_construct(operations=(operation,))
    with pytest.raises(EvolutionPolicyGapError) as raised:
        additive_policy_issues(load_model(str(ROUNDS)), proposal, populated=frozenset())
    assert raised.value.locator_kind == "forged"
    assert _evolve_error_exit(raised.value) == 3
    # Control: the same walk over a real declaration admits it.
    assert additive_policy_issues(load_model(str(ROUNDS)), EvolutionProposal.model_construct(
        operations=(_round_add(),)), populated=frozenset()) == ()


def test_b12_the_target_and_delta_never_reach_the_constraint_fall_through(monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.evolve import service

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("the constraint fall-through was reached")

    monkeypatch.setattr(service, "_find_constraint", forbidden)
    document = _doc(ROUNDS)
    documents = document["source"]["documents"]
    modify = _declaration("modify", ANNEX, before=_annex(), after=_annex("annex-2025.txt"))
    assert service._operation_target(document, modify) == (documents, 1)
    assert service._operation_target(document, _round_add()) == (documents, None)
    assert service._delta_element_ids(modify) == frozenset()
    assert service._delta_element_ids(_round_add()) == frozenset()


def test_b14_a_declaration_only_proposal_has_a_blast_radius(tmp_path: Path) -> None:
    proposal = _proposal(ROUNDS, (_round_add(),), "ug3-b14").model_dump(mode="json")
    paths = _workspace(tmp_path / "ws", ROUNDS, proposal)
    result = _preview(paths, ["--policy", "additive"])
    assert result.returncode == 0, result.stderr.decode()
    preview = json.loads(paths["preview"].read_text(encoding="utf-8"))
    assert preview["policy_issues"] == []
    assert preview["blast_radius"]["entries"] != []


def test_b15_apply_re_runs_the_policy_over_a_stripped_preview(tmp_path: Path) -> None:
    """Apply never trusts the preview's issue list: a preview whose issues were stripped is refused again.

    Corrected from the spec's CLI wording (finding F-i2): the CLI refuses a --policy that
    differs from the preview's before the policy runs, so the re-run is reached with the
    same policy and a stripped issue list, as MG2's T3b does for its cells."""
    import test_evolve_additive_policy as policy

    from gnd.evolve import EvolutionPolicyRefusedError, EvolutionProposal
    from gnd.evolve.cli_service import _evolve_error_exit

    text = ROUNDS.read_text(encoding="utf-8")
    service = policy._service(tmp_path, text)
    preview = service.preview(EvolutionProposal.model_validate(_case("B2")[1]), policy="additive")
    assert [issue.cell for issue in preview.policy_issues] == ["source_document.modify"]
    stripped = policy._stripped_preview(preview)
    assert stripped.policy_issues == ()
    with pytest.raises(EvolutionPolicyRefusedError) as raised:
        service.apply(stripped)
    assert raised.value.issues[0].cell == "source_document.modify"
    assert raised.value.issues[0].operation_index == 0
    assert _evolve_error_exit(raised.value) == 3


@pytest.mark.parametrize("count", [1, 10, 100])
def test_b16_a_run_of_adds_is_linear(count: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Review finding 6: the digests are read once per replay, and an add never rescans the list."""
    from gnd.evolve import service

    calls = {"digests": 0, "positions": 0}
    digests_of, positions_of = service._declared_digests, service._declared_positions

    def digests(*args: Any) -> Any:
        calls["digests"] += 1
        return digests_of(*args)

    def positions(*args: Any) -> Any:
        calls["positions"] += 1
        return positions_of(*args)

    monkeypatch.setattr(service, "_declared_digests", digests)
    monkeypatch.setattr(service, "_declared_positions", positions)
    added = [_sha(f"document {index}".encode()) for index in range(count)]
    operations = tuple(_declaration("add", digest, after={"sha256": digest, "label": f"d{index}.txt"},
                                    operation_id=f"op-{index}") for index, digest in enumerate(added))
    replayed = service._apply_declared_operations(_doc(ROUNDS), operations)
    assert [entry["sha256"] for entry in replayed["source"]["documents"]][-count:] == added
    assert calls == {"digests": 1, "positions": 0}
    # A duplicate later in the same run is still caught by the kept set.
    with pytest.raises(service.EvolutionError, match="already declared"):
        service._apply_declared_operations(_doc(ROUNDS), (*operations, _declaration(
            "add", added[0], after={"sha256": added[0], "label": "again.txt"}, operation_id="op-again")))


# --- review regressions (notes/phase-UG3-codex-review.md) --------------------


def test_r3_an_old_record_cannot_carry_the_locator() -> None:
    """Review finding 3: records share EvolutionOperation, so their readers refuse it below version 3 too."""
    import test_public_evolution_legacy_readers as legacy
    from pydantic import ValidationError

    from gnd.evolve import EvolutionRecord, canonical_sha256

    record, _conformance = legacy._legacy_clean_record_documents()
    declaration = _round_add().model_dump(mode="json")
    for version in (1, 2):
        for operations, refused in ((record["operations"], False), ([declaration], True)):
            document = dict(record, schema_version=version, operations=operations, linked_conformance=[],
                            conformance_exit_code=0, published_with_drift=False)
            document["record_identity_sha256"] = canonical_sha256(
                {key: value for key, value in document.items() if key != "record_identity_sha256"})
            for read in (lambda document=document: EvolutionRecord.model_validate(document),
                         lambda document=document: EvolutionRecord.model_validate_json(json.dumps(document))):
                if refused:
                    with pytest.raises(ValidationError, match="require record schema_version 3"):
                        read()
                else:
                    assert read().schema_version == version


def test_r5_a_digest_declared_twice_is_an_ambiguous_target() -> None:
    """Review finding 5: modify and delete need exactly one entry with the digest."""
    from gnd.evolve import service
    from gnd.evolve.cli_service import _evolve_error_exit

    before = _doc(ROUNDS)
    second = {"sha256": ANNEX, "label": "second-annex.txt"}
    before["source"]["documents"].append(second)
    for operation in (_declaration("modify", ANNEX, before=_annex(), after=_annex("x.txt")),
                      _declaration("modify", ANNEX, before=second, after=_annex("x.txt")),
                      _declaration("delete", ANNEX, before=_annex())):
        with pytest.raises(service.EvolutionError, match="is ambiguous: 2 entries declare it") as raised:
            service._apply_declared_operations(before, (operation,))
        assert _evolve_error_exit(raised.value) == 3


# --- close review regressions (notes/close-review-reader-2.md) ----------------


@pytest.mark.parametrize(("before", "after", "message"), [
    (None, {"sha256": ROUND, "label": "  "}, "non-blank"),
    ({"sha256": ANNEX, "label": "annex.txt"}, {"sha256": ROUND, "label": "x.txt"}, "must match the stable locator"),
])
def test_close_r2_f7_label_and_before_digest_are_checked_at_the_operation(before: Any, after: Any,
                                                                          message: str) -> None:
    from pydantic import ValidationError

    kind = "add" if before is None else "modify"
    with pytest.raises(ValidationError, match=message):
        _declaration(kind, ROUND, before=before, after=after)


def test_close_r2_f8_delete_then_add_moves_the_entry_to_the_end() -> None:
    """Replay never reorders on its own; an explicit delete and re-add does, as the contract says."""
    from gnd.evolve import service

    operations = (_declaration("delete", LEDGER, before=_ledger(), operation_id="op-0"),
                  _declaration("add", LEDGER, after=_ledger(), operation_id="op-1"))
    replayed = service._apply_declared_operations(_doc(ROUNDS), operations)
    assert [entry["label"] for entry in replayed["source"]["documents"]] == ["annex.txt", "ledger.txt"]
