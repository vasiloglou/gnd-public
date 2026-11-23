"""IR1 (include-root-routes): ``gnd judgments check`` on a version-5 include root.

The fixture is the packaged literature interop example: ``checking.orm.json``
is the temporal root of issue 217 (two includes, one reference population),
``extraction.orm.json`` the non-temporal root over the same includes.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from support.cli_runner import run_main

from gnd.artifacts import canonical_json_bytes
from gnd.errors import ModelValidationError
from gnd.judgments import JudgmentInputError, evaluate_judgments, judgment_fact_digest

TARGET = "paper_names_parent_method"
POPULATION = "composed.population.json"
CHRONOLOGY = "vocabulary/chronology.orm.json"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from gnd.examples.literature.interop import build

    out = tmp_path_factory.mktemp("ir1") / "interop"
    build(out)
    return out


@pytest.fixture
def case(built, tmp_path):
    root = tmp_path / "case"
    shutil.copytree(built, root)
    return root


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def bind(root, model, population=POPULATION):
    """Write a consumer-pinned two-judge policy and approving receipts for MODEL."""
    model_doc = json.loads((root / model).read_bytes())
    population_raw = (root / population).read_bytes()
    fact = json.loads(population_raw)["facts"][TARGET][0]
    (root / "evidence.txt").write_bytes(b"evidence")
    identity = {"identity_version": 1, "references": [
        {"id": ref["id"], "sha256": ref["sha256"]} for ref in model_doc["reference_populations"]]}
    receipts = [{
        "receipt_id": f"r-{judge}", "judge_id": judge, "verdict": "approve",
        "trust": "consumer-pinned",
        "subject": {"model_sha256": _sha((root / model).read_bytes()),
                    "population_sha256": _sha(population_raw),
                    "reference_identity": identity, "fact_type": TARGET, "index": 0,
                    "fact_sha256": judgment_fact_digest(TARGET, 0, fact)},
        "sources": [{"path": "evidence.txt", "sha256": _sha(b"evidence"), "quote": None}],
        "external_evidence": None,
    } for judge in ("a", "b")]
    policy = {
        "admission": {"evidence_floor": None, "minimum_approvals": 2},
        "judges": ["a", "b"], "policy_id": "ir1",
        "repair": {"evidence_floor": None, "minimum_rejections": 1},
        "schema_version": 1, "targets": [{"fact_type": TARGET, "index": 0}],
        "trust_mode": "consumer-pinned",
        "trusted_receipts": [
            {"judge_id": r["judge_id"],
             "receipt_sha256": _sha(canonical_json_bytes(r, exact_numbers=True))}
            for r in receipts],
    }
    (root / "policy.json").write_bytes(canonical_json_bytes(policy))
    (root / "receipts.json").write_bytes(
        canonical_json_bytes({"schema_version": 1, "receipts": receipts}))


def judge(root, model, population=POPULATION):
    result = run_main(["judgments", "check", str(root / model), str(root / population),
                       "--policy", str(root / "policy.json"),
                       "--receipts", str(root / "receipts.json"),
                       "--trusted-root", str(root), "--format", "json"])
    return result.returncode, json.loads(result.stdout)


def repin(root, model, include_id):
    doc = json.loads((root / model).read_bytes())
    for entry in doc["includes"]:
        if entry["id"] == include_id:
            entry["sha256"] = _sha((root / entry["path"]).read_bytes())
    (root / model).write_text(json.dumps(doc))


def edit_include(root, mutate, path=CHRONOLOGY):
    doc = json.loads((root / path).read_bytes())
    mutate(doc)
    (root / path).write_text(json.dumps(doc))


def extra_types(count):
    def mutate(doc):
        doc["object_types"].extend(
            {"id": f"extra_{i}", "kind": "value", "name": f"Extra{i}", "primitive": "String"}
            for i in range(count))
    return mutate


def report_validator():
    schema = json.loads((files("gnd") / "judgment.schema.json").read_text())
    report = json.loads((files("gnd") / "report.schema.json").read_text())
    registry = Registry().with_resource("report.schema.json", Resource.from_contents(report))
    return Draft202012Validator(schema, registry=registry)


def relabel_for_extraction(root):
    population = json.loads((root / POPULATION).read_bytes())
    model_id = json.loads((root / "extraction.orm.json").read_bytes())["model_id"]
    population["population"].update(model_id=model_id, model="extraction.orm.json")
    (root / "extraction.population.json").write_text(json.dumps(population))
    return "extraction.population.json"


# --- T1: the issue 217 temporal root judges -------------------------------


def test_T1_temporal_include_root_judges(case):
    bind(case, "checking.orm.json")
    code, out = judge(case, "checking.orm.json")
    assert code == 0, out
    assert out["outcome"] == 0 and out["error"] is None
    assert out["judgment_policy"]["admission"] is True


# --- T2: same verdicts directly and through the flat model ----------------


def test_T2_direct_and_flat_agree(case):
    from gnd.model import load_model
    from gnd.model.flattening import flatten_model

    population = relabel_for_extraction(case)
    flat = flatten_model(load_model(case / "extraction.orm.json"))
    (case / "extraction.flat.orm.json").write_bytes(flat.model_bytes)
    decisions = {}
    for model in ("extraction.orm.json", "extraction.flat.orm.json"):
        bind(case, model, population)
        code, out = judge(case, model, population)
        assert code == 0, out
        decision = out["judgment_policy"]
        for target in decision["targets"]:
            for row in target["judgments"]:
                row.pop("receipt_sha256")
        decisions[model] = {k: decision[k] for k in
                            ("admission", "repair", "review_required", "targets")}
    assert decisions["extraction.orm.json"] == decisions["extraction.flat.orm.json"]


# --- T3, T4, T5: include integrity through the judgments route ------------


def test_T3_unpinned_include_edit_refuses(case):
    bind(case, "checking.orm.json")
    with (case / CHRONOLOGY).open("ab") as handle:
        handle.write(b" ")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"] == {"reason": "binding", "message": "include:hash-mismatch"}


def test_T4_repinned_include_edit_makes_receipts_stale(case):
    bind(case, "checking.orm.json")
    edit_include(case, extra_types(1))
    repin(case, "checking.orm.json", "chronology")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"] == {"reason": "binding", "message": "stale judgment subject"}


def test_T5_nested_include_refuses(case):
    literature = (case / "vocabulary/literature.orm.json").read_bytes()
    edit_include(case, lambda doc: doc.update(includes=[
        {"id": "nested", "path": "literature.orm.json", "sha256": _sha(literature)}]))
    repin(case, "checking.orm.json", "chronology")
    bind(case, "checking.orm.json")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"] == {"reason": "binding", "message": "include:forbidden-section"}


# --- T6: hostile declarations give schema-valid refusals ------------------


def _hostile(root, kind):
    doc = json.loads((root / "checking.orm.json").read_bytes())
    if kind == "escape":
        doc["includes"][1]["path"] = "../escape.orm.json"
    elif kind == "absent":
        doc["includes"][1]["path"] = "vocabulary/absent.orm.json"
    elif kind == "not-a-list":
        doc["includes"] = {}
    elif kind == "mismatch":
        doc["includes"][1]["sha256"] = "0" * 64
    elif kind == "nested":
        literature = (root / "vocabulary/literature.orm.json").read_bytes()
        edit_include(root, lambda d: d.update(includes=[
            {"id": "nested", "path": "literature.orm.json", "sha256": _sha(literature)}]))
        doc["includes"][1]["sha256"] = _sha((root / CHRONOLOGY).read_bytes())
    (root / "checking.orm.json").write_text(json.dumps(doc))


HOSTILE = {"escape": "include:path", "absent": "include:unreadable",
           "not-a-list": "include:declaration", "mismatch": "include:hash-mismatch",
           "nested": "include:forbidden-section"}


@pytest.mark.parametrize("kind", sorted(HOSTILE))
def test_T6_hostile_declarations_refuse_within_the_schema(case, kind):
    _hostile(case, kind)
    bind(case, "checking.orm.json")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"] == {"reason": "binding", "message": HOSTILE[kind]}
    assert list(report_validator().iter_errors(out)) == []


def test_T6_validator_negative_control():
    """The validator reds on the report shape 0.4.0 wrote for an include refusal."""
    old = {"command": "judgments", "error": {"message": "include:unsupported-route",
           "reason": "include:unsupported-route"}, "judgment_policy": None,
           "mechanical_report": None, "outcome": 3, "schema_version": 15}
    assert list(report_validator().iter_errors(old))


# --- T7: direct evaluate_judgments callers --------------------------------


def test_T7_evaluate_without_model_root_keeps_refusing(case):
    raw = (case / "checking.orm.json").read_bytes()
    with pytest.raises(ModelValidationError, match="include:unsupported-route"):
        evaluate_judgments(None, (), model=None, candidate=None, mechanical_report={},
                           model_bytes=raw, population_bytes=b"{}", trusted_root=case,
                           model_root=None)


def test_T7_evaluate_with_model_root_skips_the_include_refusal(case):
    raw = (case / "checking.orm.json").read_bytes()
    with pytest.raises(JudgmentInputError):
        evaluate_judgments(None, (), model=None, candidate=None, mechanical_report={},
                           model_bytes=raw, population_bytes=b"{}", trusted_root=case,
                           model_root=case)


# --- T8: validation order --------------------------------------------------


def test_T8_policy_shape_precedes_include_integrity(case):
    bind(case, "checking.orm.json")
    (case / "policy.json").write_bytes(b"{}")
    with (case / CHRONOLOGY).open("ab") as handle:
        handle.write(b" ")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"]["reason"] == "shape"


# --- T9: time bound over the composition layer ----------------------------
#
# Corrected during implementation (spec section 4, rule 2): the first T9 timed
# the whole judgments route and measured the existing checker, which is
# superlinear in the number of object types (gnd check alone: 7.7 s at 300
# extra types, 266 s at 1,000, with or without includes). IR1 adds the
# composition, twice per run; this case times that layer.


def test_T9_composition_layer_within_bound(case):
    from gnd.model import load_model_bytes_composed
    from gnd.model._includes import bytes_declare_includes

    edit_include(case, extra_types(1000))
    repin(case, "checking.orm.json", "chronology")
    raw = (case / "checking.orm.json").read_bytes()
    started = time.monotonic()
    for _ in range(2):  # api.judgments and the raw-subject check each compose once
        assert bytes_declare_includes(raw, source="checking.orm.json")
        model = load_model_bytes_composed(raw, source=case / "checking.orm.json", root=case,
                                          bind_references=False)
    elapsed = time.monotonic() - started
    assert len(model.object_types) > 1000
    assert elapsed < 5, elapsed


# --- T9, route level: restored by reviewed-vocabulary-growth VG1 ---------
#
# The row IR1 withdrew (its spec, T9, prior row) is restored at the bound it
# first named, now that the checker is no longer superlinear in object types
# (VG1-C5). The composition-only T9 above stays beside it.


def test_T9_route_level_judgments_check_at_1000_extra_types_within_bound(case):
    edit_include(case, extra_types(1000))
    repin(case, "checking.orm.json", "chronology")
    bind(case, "checking.orm.json")
    started = time.monotonic()
    code, out = judge(case, "checking.orm.json")
    elapsed = time.monotonic() - started
    assert code in (0, 1), out
    assert out["outcome"] in (0, 1)
    assert elapsed < 20, elapsed


# --- T12: references of an include root bind at --reference-root ----------


def test_T12_reference_root_is_honoured_for_include_roots(case, tmp_path):
    bind(case, "checking.orm.json")
    reference_root = tmp_path / "references"
    (reference_root / "reference").mkdir(parents=True)
    (case / "reference/catalog.json").rename(reference_root / "reference/catalog.json")
    result = run_main(["judgments", "check", str(case / "checking.orm.json"),
                       str(case / POPULATION), "--policy", str(case / "policy.json"),
                       "--receipts", str(case / "receipts.json"),
                       "--trusted-root", str(case), "--reference-root", str(reference_root),
                       "--format", "json"])
    out = json.loads(result.stdout)
    assert result.returncode == 0, out
    assert out["judgment_policy"]["admission"] is True


# --- T13: an orphan attachment takes the composed route and is refused -----


def test_T13_orphan_fact_type_constraints_refuse_as_declaration(case):
    doc = json.loads((case / "checking.orm.json").read_bytes())
    del doc["includes"]
    doc["fact_type_constraints"] = [{"fact_type": TARGET, "constraints": [{"kind": "mandatory"}]}]
    (case / "checking.orm.json").write_text(json.dumps(doc))
    bind(case, "checking.orm.json")
    code, out = judge(case, "checking.orm.json")
    assert code == 3
    assert out["error"] == {"reason": "binding", "message": "include:declaration"}


# --- T11: a model without includes keeps its exact report bytes -------------
#
# Added after the phase review (finding F1): the golden was produced by the
# base code at 1e419a88 over the flat (include-free) extraction model, with
# the case folder replaced by "<case>".

GOLDEN = Path(__file__).parent / "fixtures/ir1/include-free-judgments-report.json"


def _include_free_report(case):
    from gnd.model import load_model
    from gnd.model.flattening import flatten_model

    population = relabel_for_extraction(case)
    flat = flatten_model(load_model(case / "extraction.orm.json")).model_bytes
    (case / "extraction.flat.orm.json").write_bytes(flat)
    bind(case, "extraction.flat.orm.json", population)
    result = run_main(["judgments", "check", str(case / "extraction.flat.orm.json"),
                       str(case / population), "--policy", str(case / "policy.json"),
                       "--receipts", str(case / "receipts.json"),
                       "--trusted-root", str(case), "--format", "json"])
    assert result.returncode == 0, result.stdout
    return result.stdout.replace(str(case).encode(), b"<case>")


def test_T11_include_free_report_is_byte_identical(case):
    assert _include_free_report(case) == GOLDEN.read_bytes()


def test_T11_golden_negative_control(case):
    """A one-field change to the report is caught by the byte comparison."""
    report = json.loads(_include_free_report(case))

    def rendered(value):  # the CLI prints canonical JSON and a newline
        return canonical_json_bytes(value, exact_numbers=True) + b"\n"

    assert rendered(report) == GOLDEN.read_bytes()
    report["schema_version"] = 14
    assert rendered(report) != GOLDEN.read_bytes()
