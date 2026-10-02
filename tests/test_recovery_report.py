

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

import gnd.recovery.verify as recovery_verify
from gnd.model_verbalization import render_model_verbalization
from gnd.recovery import (
    AmbiguousProposal,
    CensusEntry,
    EvidenceRecord,
    ExcludedRoot,
    FrontierItem,
    JsonPointerLocator,
    LineLocator,
    ModeledElementEvidence,
    OutputArtifact,
    PythonSymbolLocator,
    RecoveryInventory,
    RecoveryReport,
    RecoveryScope,
    RecoveryVerificationResult,
    SelectedRoot,
    YamlPathLocator,
    scan_recovery_scope,
    verify_recovery_bundle,
)

PUBLIC_MODELS = (
    SelectedRoot,
    ExcludedRoot,
    RecoveryScope,
    PythonSymbolLocator,
    LineLocator,
    JsonPointerLocator,
    YamlPathLocator,
    EvidenceRecord,
    CensusEntry,
    ModeledElementEvidence,
    AmbiguousProposal,
    FrontierItem,
    OutputArtifact,
    RecoveryInventory,
    RecoveryReport,
    RecoveryVerificationResult,
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _evidence(
    *,
    evidence_id: str = "ev-order",
    symbol: str = "Order",
    digest: str = "1" * 64,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        path="src/domain.py",
        sha256=digest,
        byte_length=47,
        media_type="text/x-python",
        encoding="utf-8",
        locator=PythonSymbolLocator(kind="python-symbol", symbol=symbol, line_start=1, line_end=2),
        excerpt_sha256=_sha(f"class {symbol}:\n".encode()),
    )


def _scope(*, excluded: tuple[ExcludedRoot, ...] = ()) -> RecoveryScope:
    return RecoveryScope(
        repository_root=".",
        selected_roots=(SelectedRoot(category="source", path="src"),),
        excluded_roots=excluded,
        max_file_bytes=1_000_000,
        max_total_bytes=8_000_000,
        max_files=1_000,
    )


def _report(*, outputs: tuple[OutputArtifact, ...] | None = None) -> RecoveryReport:
    evidence = (_evidence(),)
    inventory = RecoveryInventory(
        scope=_scope(),
        evidence=evidence,
        ambiguities=(),
        frontier=(),
        census=(
            CensusEntry(
                path="src/domain.py",
                disposition="parsed",
                reference_ids=("ev-order",),
            ),
        ),
    )
    return RecoveryReport(
        schema_version=1,
        inventory=inventory,
        modeled_elements=(
            ModeledElementEvidence(
                element_id="object:order",
                element_kind="object-type",
                model_pointer="/object_types/0",
                evidence_ids=("ev-order",),
            ),
        ),
        proposals=(),
        outputs=outputs
        or (
            OutputArtifact(path="model.orm.yaml", sha256="2" * 64),
            OutputArtifact(path="model.verbalization.txt", sha256="3" * 64),
            OutputArtifact(path="model.recovery.json", sha256=None),
        ),
    )


def test_all_serialized_boundaries_are_frozen_closed_pydantic_models() -> None:
    for model in PUBLIC_MODELS:
        assert issubclass(model, BaseModel), model
        assert model.model_config.get("extra") == "forbid", model
        assert model.model_config.get("frozen") is True, model

    report = _report()
    assert isinstance(report.inventory.evidence, tuple)
    assert isinstance(report.inventory.census, tuple)
    assert isinstance(report.modeled_elements, tuple)
    assert isinstance(report.proposals, tuple)
    assert isinstance(report.outputs, tuple)
    with pytest.raises(ValidationError):
        report.schema_version = 2
    with pytest.raises(ValidationError):
        report.inventory.scope.repository_root = "elsewhere"
    with pytest.raises(ValidationError):
        report.outputs[0].path = "other.yaml"


@pytest.mark.parametrize(
    ("path", "extra"),
    [
        (("inventory", "scope"), {"secret": True}),
        (("inventory", "evidence", 0, "locator"), {"column": 9}),
        (("inventory", "census", 0), {"guess": "complete"}),
        (("modeled_elements", 0), {"confidence": 1.0}),
        (("outputs", 0), {"verified": True}),
    ],
)
def test_unknown_fields_are_rejected_recursively(
    path: tuple[str | int, ...], extra: dict[str, Any]
) -> None:
    data = _report().model_dump(mode="json")
    cursor: Any = data
    for part in path:
        cursor = cursor[part]
    cursor.update(extra)
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)


def test_locator_union_is_discriminated_and_rejects_cross_kind_fields() -> None:
    evidence = _evidence().model_dump(mode="json")
    evidence["locator"] = {
        "kind": "json-pointer",
        "pointer": "/$defs/Order",
        "symbol": "Order",
    }
    with pytest.raises(ValidationError):
        EvidenceRecord.model_validate(evidence)
    evidence["locator"] = {"kind": "regex", "pattern": "Order"}
    with pytest.raises(ValidationError):
        EvidenceRecord.model_validate(evidence)


def test_evidence_serialization_contains_only_locator_and_hash_not_source_text() -> None:
    evidence = _evidence()
    data = evidence.model_dump(mode="json")
    rendered = json.dumps(data, sort_keys=True)
    assert "excerpt" not in evidence.__class__.model_fields
    assert "class Order" not in rendered
    assert "password" not in rendered
    assert data["excerpt_sha256"] == _sha(b"class Order:\n")

    with pytest.raises(ValidationError):
        EvidenceRecord.model_validate({**data, "excerpt": "password=hunter2"})


def test_all_four_locator_records_are_closed_and_nonempty() -> None:
    locators = (
        PythonSymbolLocator(kind="python-symbol", symbol="Order", line_start=1, line_end=2),
        LineLocator(kind="line", line_start=1, line_end=1),
        JsonPointerLocator(kind="json-pointer", pointer="/$defs/Order"),
        YamlPathLocator(kind="yaml-path", path=("order", "status")),
    )
    assert [locator.kind for locator in locators] == [
        "python-symbol",
        "line",
        "json-pointer",
        "yaml-path",
    ]
    with pytest.raises(ValidationError):
        YamlPathLocator(kind="yaml-path", path=())
    with pytest.raises(ValidationError):
        LineLocator(kind="line", line_start=3, line_end=2)


def test_modeled_element_uses_a_typed_json_pointer_into_the_loaded_model() -> None:
    claim = ModeledElementEvidence(
        element_id="role:order-has-id:order",
        element_kind="role",
        model_pointer="/fact_types/0/roles/0",
        evidence_ids=("ev-order",),
    )
    assert claim.model_pointer == "/fact_types/0/roles/0"
    with pytest.raises(ValidationError):
        ModeledElementEvidence(
            element_id="object:order",
            element_kind="object-type",
            model_pointer="object_types[0]",
            evidence_ids=("ev-order",),
        )


def test_provenance_is_exactly_five_sources_and_code_derived_is_impossible() -> None:
    common = {
        "proposal_id": "proposal:relation",
        "element_id": "fact:request-has-approver",
        "element_kind": "fact-type",
        "status": "proposed",
        "modality": "deontic",
        "rationale": "Owner review is required.",
        "evidence_ids": ("ev-order",),
        "prior_proposal_id": None,
    }
    allowed = {"explicit", "sample", "common-sense", "llm-inferred", "user-supplied"}
    for source in allowed:
        assert AmbiguousProposal(source=source, **common).source == source
    with pytest.raises(ValidationError):
        AmbiguousProposal(source="code-derived", **common)


def test_sample_and_llm_inferred_cannot_auto_confirm_or_become_alethic() -> None:
    common = {
        "proposal_id": "proposal:relation",
        "element_id": "fact:request-has-approver",
        "element_kind": "fact-type",
        "rationale": "Semantic interpretation requires the owner.",
        "evidence_ids": ("ev-order",),
        "prior_proposal_id": None,
    }
    for source in ("sample", "llm-inferred"):
        with pytest.raises(ValidationError):
            AmbiguousProposal(source=source, status="confirmed", modality="alethic", **common)


def test_a_modeled_element_cannot_carry_an_invented_alethic_constraint() -> None:

















    common = {
        "element_id": "constraint:policy",
        "element_kind": "constraint",
        "model_pointer": "/constraints/0",
        "evidence_ids": ("ev-order",),
    }
    inferred = ("sample", "common-sense", "llm-inferred")

    for source in inferred:
        
        with pytest.raises(ValidationError):
            ModeledElementEvidence(source=source, status="confirmed", modality="alethic", **common)
        
        with pytest.raises(ValidationError):
            ModeledElementEvidence(source=source, status="confirmed", modality="deontic", **common)
        
        with pytest.raises(ValidationError):
            ModeledElementEvidence(source=source, status="proposed", modality="alethic", **common)

    for source in inferred:
        claim = ModeledElementEvidence(
            source=source, status="proposed", modality="deontic", **common
        )
        assert (claim.source, claim.status, claim.modality) == (source, "proposed", "deontic")

    for source in ("explicit", "user-supplied"):
        owned = ModeledElementEvidence(
            source=source, status="confirmed", modality="alethic", **common
        )
        assert (owned.source, owned.status, owned.modality) == (source, "confirmed", "alethic")


def test_owner_confirmation_references_and_retains_the_reviewed_proposal() -> None:
    original = AmbiguousProposal(
        proposal_id="proposal:relation:v1",
        element_id="fact:request-has-approver",
        element_kind="fact-type",
        source="llm-inferred",
        status="rejected",
        modality="deontic",
        rationale="The owner rejected the one-approver interpretation.",
        evidence_ids=("ev-order",),
        prior_proposal_id=None,
    )
    replacement = AmbiguousProposal(
        proposal_id="proposal:relation:v2",
        element_id="fact:request-may-have-approver",
        element_kind="fact-type",
        source="user-supplied",
        status="confirmed",
        modality="alethic",
        rationale="The owner supplied the optional relation.",
        evidence_ids=("ev-order",),
        prior_proposal_id=original.proposal_id,
    )
    base = _report().model_dump(mode="json")
    base["proposals"] = [
        original.model_dump(mode="json"),
        replacement.model_dump(mode="json"),
    ]
    report = RecoveryReport.model_validate(base)
    assert [item.status for item in report.proposals] == ["rejected", "confirmed"]

    without_history = copy.deepcopy(base)
    without_history["proposals"] = [replacement.model_dump(mode="json")]
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(without_history)


def test_inventoried_ambiguity_cannot_disappear_or_change_identity() -> None:
    proposal = AmbiguousProposal(
        proposal_id="proposal:relation",
        element_id="fact:request-has-approver",
        element_kind="fact-type",
        source="llm-inferred",
        status="proposed",
        modality="deontic",
        rationale="Owner review is required.",
        evidence_ids=("ev-order",),
        prior_proposal_id=None,
    )
    data = _report().model_dump(mode="json")
    data["inventory"]["ambiguities"] = [proposal.model_dump(mode="json")]
    data["inventory"]["census"][0] = {
        "path": "src/domain.py",
        "disposition": "ambiguous",
        "reference_ids": [proposal.proposal_id],
    }
    with pytest.raises(ValidationError, match="retained"):
        RecoveryReport.model_validate(data)

    data["proposals"] = [proposal.model_dump(mode="json")]
    assert RecoveryReport.model_validate(data).proposals == (proposal,)
    data["proposals"][0]["evidence_ids"] = ["ev-missing"]
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)


def test_report_collections_have_a_hard_observation_cap() -> None:
    selected = SelectedRoot(category="source", path="src")
    with pytest.raises(ValidationError):
        RecoveryScope(
            repository_root=".",
            selected_roots=(selected,) * 10_001,
            max_file_bytes=1,
            max_total_bytes=1,
            max_files=1,
        )


def test_every_modeled_or_proposed_claim_requires_resolving_concrete_evidence() -> None:
    data = _report().model_dump(mode="json")
    data["modeled_elements"][0]["evidence_ids"] = []
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)

    data = _report().model_dump(mode="json")
    data["modeled_elements"][0]["evidence_ids"] = ["ev-missing"]
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)

    data = _report().model_dump(mode="json")
    data["proposals"] = [
        {
            "proposal_id": "proposal:evidence-free",
            "element_id": "fact:guess",
            "element_kind": "fact-type",
            "source": "llm-inferred",
            "status": "proposed",
            "modality": "deontic",
            "rationale": "A rationale is not evidence.",
            "evidence_ids": [],
            "prior_proposal_id": None,
        }
    ]
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)


def test_census_is_exact_and_each_disposition_has_the_right_reference_shape() -> None:
    data = _report().model_dump(mode="json")
    data["inventory"]["census"] = []
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)

    data = _report().model_dump(mode="json")
    data["inventory"]["census"].append(copy.deepcopy(data["inventory"]["census"][0]))
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)

    data = _report().model_dump(mode="json")
    data["inventory"]["census"][0] = {
        "path": "src/domain.py",
        "disposition": "frontier",
        "reference_ids": ["ev-order"],
    }
    with pytest.raises(ValidationError):
        RecoveryReport.model_validate(data)


def test_output_digests_avoid_impossible_recursive_self_hash() -> None:
    _report()
    with pytest.raises(ValidationError):
        _report(
            outputs=(
                OutputArtifact(path="model.orm.yaml", sha256=None),
                OutputArtifact(path="model.verbalization.txt", sha256="3" * 64),
                OutputArtifact(path="model.recovery.json", sha256=None),
            )
        )
    with pytest.raises(ValidationError):
        _report(
            outputs=(
                OutputArtifact(path="model.orm.yaml", sha256="2" * 64),
                OutputArtifact(path="model.verbalization.txt", sha256="3" * 64),
                OutputArtifact(path="model.recovery.json", sha256="4" * 64),
            )
        )


def _write_bundle(root: Path) -> RecoveryReport:
    source = b"class OrderId(int):\n    pass\n\nclass Order:\n    order_id: OrderId\n"
    docs = b"Order evidence\n"
    config = b"order:\n  status: open\n"
    schema = b'{"type":"object","properties":{"id":{"type":"integer"}}}\n'
    blobs = {
        "src/domain.py": source,
        "docs/domain.md": docs,
        "config/domain.yaml": config,
        "schema/domain.schema.json": schema,
    }
    for relpath, raw in blobs.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    model = {
        "version": 1,
        "model_id": "recovered-order",
        "source": {"kind": "codebase"},
        "object_types": [
            {
                "id": "order",
                "name": "Order",
                "kind": "entity",
                "reference": {"mode": "popular", "value_type": "order_id"},
            },
            {"id": "order_id", "name": "OrderId", "kind": "value", "primitive": "Integer"},
        ],
        "fact_types": [],
        "constraints": [],
        "rejected_proposals": [],
    }
    model_path = root / "model.orm.yaml"
    model_path.write_text(json.dumps(model, separators=(",", ":")) + "\n", encoding="utf-8")
    verbalization_path = root / "model.verbalization.txt"
    verbalization_path.write_text(render_model_verbalization(model_path), encoding="utf-8")

    selected_roots = (
        SelectedRoot(category="source", path="src"),
        SelectedRoot(category="docs", path="docs"),
        SelectedRoot(category="config", path="config"),
        SelectedRoot(category="schema", path="schema"),
    )
    inventory = scan_recovery_scope(
        root,
        selected_roots,
        max_file_bytes=1_000_000,
        max_total_bytes=8_000_000,
        max_files=1_000,
    )
    report = RecoveryReport(
        schema_version=1,
        inventory=inventory,
        modeled_elements=(
            ModeledElementEvidence(
                element_id="object:order",
                element_kind="object-type",
                model_pointer="/object_types/0",
                evidence_ids=("ev-order-class",),
            ),
            ModeledElementEvidence(
                element_id="object:order_id",
                element_kind="object-type",
                model_pointer="/object_types/1",
                evidence_ids=("ev-order-id-class",),
            ),
        ),
        proposals=(),
        outputs=(
            OutputArtifact(path="model.orm.yaml", sha256=_sha(model_path.read_bytes())),
            OutputArtifact(
                path="model.verbalization.txt", sha256=_sha(verbalization_path.read_bytes())
            ),
            OutputArtifact(path="model.recovery.json", sha256=None),
        ),
    )
    (root / "model.recovery.json").write_text(
        report.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    return report


def test_loaded_model_kind_and_constraint_provenance_must_match_report() -> None:
    wrong_kind_data = _report().model_dump(mode="json")
    wrong_kind_data["modeled_elements"][0]["element_kind"] = "fact-type"
    wrong_kind = RecoveryReport.model_validate(wrong_kind_data)
    with pytest.raises(ValueError, match="expected object-type"):
        recovery_verify._verify_model_mapping(
            wrong_kind,
            {"object_types": [{"id": "order"}], "fact_types": [], "constraints": []},
        )

    forged_data = _report().model_dump(mode="json")
    forged_data["modeled_elements"].append(
        ModeledElementEvidence(
            element_id="constraint:policy",
            element_kind="constraint",
            model_pointer="/constraints/0",
            evidence_ids=("ev-order",),
            source="explicit",
            status="confirmed",
            modality="alethic",
        ).model_dump(mode="json")
    )
    forged = RecoveryReport.model_validate(forged_data)
    with pytest.raises(ValueError, match="provenance differs"):
        recovery_verify._verify_model_mapping(
            forged,
            {
                "object_types": [{"id": "order"}],
                "fact_types": [],
                "constraints": [{"source": "sample", "status": "proposed", "modality": "deontic"}],
            },
        )


def test_rejected_and_confirmed_transition_evidence_must_match_loaded_model() -> None:
    rejected = AmbiguousProposal(
        proposal_id="proposal:rejected",
        element_id="fact:rejected",
        element_kind="fact-type",
        source="llm-inferred",
        status="rejected",
        modality="deontic",
        rationale="The owner rejected this interpretation.",
        evidence_ids=("ev-order",),
        prior_proposal_id=None,
    )
    data = _report().model_dump(mode="json")
    data["proposals"] = [rejected.model_dump(mode="json")]
    report = RecoveryReport.model_validate(data)
    with pytest.raises(ValueError, match="rejection history differs"):
        recovery_verify._verify_proposal_transitions(
            report,
            {"rejected_proposals": []},
        )
    recovery_verify._verify_proposal_transitions(
        report,
        {"rejected_proposals": [rejected.model_dump(mode="json")]},
    )

    mutations = {
        "element_id": "fact:substituted",
        "element_kind": "constraint",
        "source": "sample",
        "status": "proposed",
        "modality": "alethic",
        "rationale": "A substituted rationale.",
        "evidence_ids": ["ev-substituted"],
        "prior_proposal_id": "proposal:substituted-prior",
        "type": "ring",
    }
    for field, value in mutations.items():
        archived = rejected.model_dump(mode="json")
        archived[field] = value
        with pytest.raises(ValueError, match="immutable fields"):
            recovery_verify._verify_proposal_transitions(
                report,
                {"rejected_proposals": [archived]},
            )


def test_malformed_yaml_locator_is_a_closed_verification_failure() -> None:
    evidence = EvidenceRecord(
        evidence_id="ev-malformed-yaml",
        path="config/malformed.yaml",
        sha256=_sha(b"value: [\n"),
        byte_length=len(b"value: [\n"),
        media_type="application/yaml",
        encoding="utf-8",
        locator=YamlPathLocator(path=("value",)),
        excerpt_sha256="0" * 64,
    )
    with pytest.raises(ValueError, match="cannot be parsed"):
        recovery_verify._resolve_locator(evidence, b"value: [\n")


def test_verifier_calls_canonical_loader_checks_full_verbalization_and_returns_report_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_bundle(tmp_path)
    calls: list[str] = []
    canonical_loader = recovery_verify.load_model

    def load_spy(path: str) -> Any:
        calls.append(path)
        return canonical_loader(path)

    monkeypatch.setattr(recovery_verify, "load_model", load_spy)
    result = verify_recovery_bundle(tmp_path)
    assert result.ok is True, result.errors
    assert len(calls) == 1
    assert Path(calls[0]).name == "model.orm.yaml"
    assert result.model_sha256 == _sha((tmp_path / "model.orm.yaml").read_bytes())
    assert result.verbalization_sha256 == _sha((tmp_path / "model.verbalization.txt").read_bytes())
    assert result.report_sha256 == _sha((tmp_path / "model.recovery.json").read_bytes())
    assert set(result.verified_evidence_ids) == {
        "ev-domain-schema",
        "ev-order-class",
        "ev-status-config",
        "ev-order-doc",
        "ev-order-id-class",
    }
    assert result.verified_census_paths == (
        "config/domain.yaml",
        "docs/domain.md",
        "schema/domain.schema.json",
        "src/domain.py",
    )


@pytest.mark.parametrize(
    ("mutation", "error_fragment"),
    [
        ("stale-digest", "stale-digest"),
        ("missing-symbol", "unresolved-locator"),
        ("missing-line", "unresolved-locator"),
        ("missing-json-pointer", "unresolved-locator"),
        ("missing-yaml-path", "unresolved-locator"),
        ("invalid-model-pointer", "invalid-model-pointer"),
        ("incomplete-verbalization", "incomplete-verbalization"),
        ("parent-traversal", "parent-traversal"),
    ],
)
def test_adversarial_digest_locator_verbalization_and_path_mutations_fail_closed(
    tmp_path: Path,
    mutation: str,
    error_fragment: str,
) -> None:
    _write_bundle(tmp_path)
    report_path = tmp_path / "model.recovery.json"
    if mutation == "stale-digest":
        (tmp_path / "src" / "domain.py").write_text("class Changed:\n    pass\n", encoding="utf-8")
    elif mutation == "incomplete-verbalization":
        (tmp_path / "model.verbalization.txt").write_text("=== Header ===\n", encoding="utf-8")
    else:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        if mutation == "missing-symbol":
            data["inventory"]["evidence"][3]["locator"]["symbol"] = "Missing"
        elif mutation == "missing-line":
            data["inventory"]["evidence"][1]["locator"] = {
                "kind": "line",
                "line_start": 99,
                "line_end": 99,
            }
        elif mutation == "missing-json-pointer":
            data["inventory"]["evidence"][2]["locator"]["pointer"] = "/missing"
        elif mutation == "missing-yaml-path":
            data["inventory"]["evidence"][0]["locator"]["path"] = ["missing"]
        elif mutation == "invalid-model-pointer":
            data["modeled_elements"][0]["model_pointer"] = "/object_types/99"
        else:
            data["inventory"]["evidence"][3]["path"] = "../outside.py"
            data["inventory"]["census"][3]["path"] = "../outside.py"
        report_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    result = verify_recovery_bundle(tmp_path)
    assert result.ok is False
    assert any(error_fragment in error for error in result.errors), result.errors


@pytest.mark.parametrize(
    "artifact",
    ["model.orm.yaml", "model.verbalization.txt", "model.recovery.json"],
)
def test_missing_any_canonical_artifact_fails_closed(tmp_path: Path, artifact: str) -> None:
    _write_bundle(tmp_path)
    (tmp_path / artifact).unlink()
    result = verify_recovery_bundle(tmp_path)
    assert result.ok is False
    assert any("missing-artifact" in error and artifact in error for error in result.errors)


def test_unaccounted_file_under_a_selected_root_fails_exact_census(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    (tmp_path / "src" / "hidden.py").write_text("password = 'secret'\n", encoding="utf-8")
    result = verify_recovery_bundle(tmp_path)
    assert result.ok is False
    assert any("unaccounted-selected-path" in error for error in result.errors)


def test_mutation_between_evidence_read_and_census_rescan_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_bundle(tmp_path)
    original_scan = recovery_verify.scan_recovery_scope

    def mutate_then_scan(*args: Any, **kwargs: Any) -> RecoveryInventory:
        (tmp_path / "src" / "domain.py").write_text("class Changed:\n    pass\n", encoding="utf-8")
        return original_scan(*args, **kwargs)

    monkeypatch.setattr(recovery_verify, "scan_recovery_scope", mutate_then_scan)
    result = verify_recovery_bundle(tmp_path)
    assert result.ok is False
    assert any("stale-inventory" in error for error in result.errors)


@pytest.mark.parametrize("target", ["bundle-root", "evidence-leaf"])
def test_symlinked_bundle_or_evidence_leaf_is_refused(tmp_path: Path, target: str) -> None:
    real = tmp_path / "real"
    _write_bundle(real)
    if target == "bundle-root":
        alias = tmp_path / "alias"
        alias.symlink_to(real, target_is_directory=True)
        result = verify_recovery_bundle(alias)
    else:
        source = real / "src" / "domain.py"
        moved = tmp_path / "outside-domain.py"
        source.replace(moved)
        source.symlink_to(moved)
        result = verify_recovery_bundle(real)
    assert result.ok is False
    assert any("unsafe-artifact" in error for error in result.errors)


def test_verifier_source_uses_model_loader_and_complete_verbalizer_but_not_conformance() -> None:
    path = Path(recovery_verify.__file__).resolve()
    text = path.read_text(encoding="utf-8")
    assert "load_model" in text
    assert "render_model_verbalization" in text
    assert "gnd.conformance" not in text
    assert "GEN-02" not in text
    assert "PyRel" not in text
