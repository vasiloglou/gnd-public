"""Original redaction/schema/temporal feedback and protected-edit authority guards."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
import test_public_v72_status as status

from gnd import api, checker
from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.exp.session_contract import DataDrivenContract, read_session_contract
from gnd.exp.session_eval import AttemptEvaluation
from gnd.exp.session_patch import PatchRefusal, apply_candidate_patch
from gnd.exp.session_v7 import _evaluate, _feedback

FIXES = ["add-fact", "replace-fact", "delete-fact", "replace-artifact"]

PRIVATE = "PRIVATE_OWNER_CANARY"

def prepare(row, root, monkeypatch):
    failed = row["class"] == "constraint"
    root, snapshot, selected, _payload, _model, _refs, _population = status.materialize(
        {
            "domain": row["domain"],
            "version": row.get("version", 12),
            "variant": "failure" if failed else "clean",
        },
        root,
        monkeypatch,
    )
    doc = json.loads((root / "model.orm.yaml").read_bytes())
    pop = json.loads((root / "candidate.pop.json").read_bytes())
    if failed:
        constraint = doc["constraints"][0]
        constraint["modality"] = row["modality"]
        if row["owner"] != "default":
            constraint.update(owner=row["owner"], allowed_fixes=FIXES)
        if row["variant"] == "mixed":
            left, right, fixed = doc["fact_types"][:3]
            key, lrole = [r["role_name"] for r in left["roles"]]
            rkey, rrole = [r["role_name"] for r in right["roles"]]
            fl, fr = [r["role_name"] for r in fixed["roles"]]
            constraint["antecedent"] = [
                {"fact_type": left["id"], "bind": {key: "$s", lrole: "$l"}},
                {"fact_type": fixed["id"], "bind": {fl: "$l", fr: "$r"}},
            ]
            constraint["consequent"] = {
                "exists": {"atoms": [{"fact_type": right["id"], "bind": {rkey: "$s", rrole: "$r"}}]}
            }
            constraint["provenance"]["user_quote"] = (
                "Every catalog row at a requested left key must have a candidate right assignment."
            )
        if row["variant"] == "redacted":
            for ft in doc["fact_types"][:2]:
                ft["roles"][0]["redact"] = True
                pop["facts"][ft["id"]][0][ft["roles"][0]["role_name"]] = PRIVATE
    if row["variant"] == "format":
        ft = doc["fact_types"][1]
        pop["facts"][ft["id"]][0][ft["roles"][1]["role_name"]] = {"unsupported": "shape"}
    status.write(root / "model.orm.yaml", doc)
    status.write(root / "candidate.pop.json", pop)
    status.write(snapshot / "candidate.pop.json", pop)
    contract = json.loads((root / "contract.json").read_bytes())
    raw = (root / "model.orm.yaml").read_bytes()
    contract["cases"][0]["verify"]["model"].update(sha256=sha256_hex(raw), size_bytes=len(raw))
    status.write(root / "contract.json", contract)
    selected = read_session_contract(
        root / "contract.json", experiment_root=root, experiment_id="EXP-72-status"
    )
    if row["variant"] == "runtime":

        def fail(*args, **kwargs):
            raise RuntimeError("RUNTIME_OWNER_CANARY")

        monkeypatch.setattr(checker, "check_partial", fail)
    if row["variant"] == "reference-error":
        (root / "references/catalog.pop.json").write_text("{}")
    payload = api.check("model.orm.yaml", "candidate.pop.json", admission=True)
    return root, snapshot, selected, payload, doc

def feedback(selected, payload, root, snapshot):
    result = _evaluate(
        selected.cases[0],
        canonical_json_bytes(payload),
        payload["exit_code"],
        snapshot,
        root,
        "a" * 64,
        "b" * 64,
    )
    assert result.payload_valid and not result.validation_errors
    evaluation = AttemptEvaluation(
        attempt_index=1, candidate_sha256="a" * 64, contract_sha256="b" * 64, results=(result,)
    )
    rows = _feedback(
        selected,
        evaluation,
        SimpleNamespace(exit_code=payload["exit_code"]),
        "rejected",
        root,
        None,
    )
    assert [r["audience"] for r in rows] == ["operator", "candidate"]
    assert all(r["schema_version"] == 8 for r in rows)
    return rows

def protected_case(row, root, monkeypatch):
    root, _snapshot, selected, _payload, model, _refs, _pop = status.materialize(
        {"domain": row["domain"], "version": 12, "variant": "clean"}, root, monkeypatch
    )
    authored = json.loads((root / "model.orm.yaml").read_bytes())
    authored["constraints"][0].update(owner="candidate", allowed_fixes=["replace-artifact"])
    status.write(root / "model.orm.yaml", authored)
    rebound = json.loads((root / "contract.json").read_bytes())
    raw = (root / "model.orm.yaml").read_bytes()
    rebound["cases"][0]["verify"]["model"].update(sha256=sha256_hex(raw), size_bytes=len(raw))
    status.write(root / "contract.json", rebound)
    selected = read_session_contract(
        root / "contract.json", experiment_root=root, experiment_id="EXP-72-status"
    )
    assert selected.cases[0].verify.model.sha256 == sha256_hex(raw)
    assert authored["constraints"][0]["allowed_fixes"] == ["replace-artifact"]
    doc = selected.model_dump(mode="json")
    ft = model.fact_types[0]
    doc["candidate_edits"] = {
        "patch_path": ".gnd-patch.json",
        "artifacts": [
            {
                "path": "candidate.pop.json",
                "collections": [
                    {"path": ["facts", ft["id"]], "key": [ft["roles"][0]["role_name"]]}
                ],
            }
        ],
    }
    contract = DataDrivenContract.model_validate(doc)
    protected = root / "references/catalog.pop.json"
    before = protected.read_bytes()
    proposal = {
        "schema_version": 1,
        "base_candidate_sha256": "a" * 64,
        "operations": [
            {"op": "replace-artifact", "artifact": "references/catalog.pop.json", "value": {}}
        ],
    }
    with pytest.raises(PatchRefusal) as refused:
        apply_candidate_patch(proposal, contract=contract, base_root=root, base_sha256="a" * 64)
    assert refused.value.reason == "protected"
    assert protected.read_bytes() == before
    # Descriptive annotation cannot add a protected artifact to this declared set.
    assert {a.path for a in contract.candidate_edits.artifacts} == {"candidate.pop.json"}

@pytest.mark.parametrize(
    "variant", ["valid", "empty-roles", "false-marker", "extra-field", "unknown-map"]
)
def test_redacted_witness_schema_boundary(variant, tmp_path, monkeypatch):
    from jsonschema import Draft202012Validator

    from gnd.report import load_report_schema

    row = {
        "class": "constraint",
        "domain": "dispatch",
        "modality": "alethic",
        "owner": "default",
        "variant": "redacted",
    }
    _root, _snapshot, _selected, payload, _doc = prepare(row, tmp_path, monkeypatch)
    marker = payload["report"]["verdicts"][0]["witnesses"][0]["$s"]
    assert marker["redacted"] is True and marker["roles"]
    if variant == "empty-roles":
        marker["roles"] = []
    elif variant == "false-marker":
        marker["redacted"] = False
    elif variant == "extra-field":
        marker["value"] = "FORBIDDEN_RAW_VALUE"
    elif variant == "unknown-map":
        marker.clear()
        marker["arbitrary"] = "unsupported"
    errors = list(Draft202012Validator(load_report_schema()).iter_errors(payload))
    assert bool(errors) is (variant != "valid")

@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_temporal_redacted_reference_feedback(domain, tmp_path, monkeypatch):
    row = {
        "class": "constraint",
        "domain": domain,
        "version": 14,
        "modality": "alethic",
        "owner": "default",
        "variant": "redacted",
    }
    root, snapshot, selected, payload, _doc = prepare(row, tmp_path, monkeypatch)
    assert payload["schema_version"] == 14 and payload["report"]["schema_version"] == 13
    rows = feedback(selected, payload, root, snapshot)
    assert PRIVATE.encode() not in canonical_json_bytes(rows)
    assert any(
        f["constraint_ref"] == "constraints[0]"
        for f in rows[1]["required"][0]["constraint_findings"]
    )

@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_review_descriptive_fix_cannot_grant_protected_permission(domain, tmp_path, monkeypatch):
    import sys

    original = apply_candidate_patch

    def future_coupling(doc, *, contract, base_root, **kwargs):
        model = json.loads((base_root / contract.cases[0].verify.model.path).read_bytes())
        if "replace-artifact" in model["constraints"][0].get("allowed_fixes", []):
            return {}  # Seed the forbidden future coupling of advice to permission.
        return original(doc, contract=contract, base_root=base_root, **kwargs)

    monkeypatch.setattr(sys.modules[__name__], "apply_candidate_patch", future_coupling)
    with pytest.raises(pytest.fail.Exception, match="DID NOT RAISE"):
        protected_case({"domain": domain}, tmp_path, monkeypatch)
