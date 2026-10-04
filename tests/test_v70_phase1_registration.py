import json
from pathlib import Path

from gnd.checker import IMPLEMENTED_FAMILIES, _is_implemented
from gnd.export.pyrel_runtime import PyrelOracle
from gnd.model import load_model
from gnd.model_verbalization import render_model_verbalization
from gnd.semantic_registry import branch, constraint_variant
from gnd.synth.boundary import derive_boundary_cases
from gnd.synth.frontier import BAND4_REASON_CODES, frontier_codes_for
from gnd.synth.mutate import operators_for

FIXTURE = Path(__file__).parent / "fixtures/v70-phase1"

MODEL = FIXTURE / "model.orm.yaml"

POPULATION = FIXTURE / "population.pop.json"

def test_anchor_branch_registry_covers_both_selectors_and_all_outcomes():
    model = load_model(MODEL)
    assert "anchored" in IMPLEMENTED_FAMILIES
    for fact_type in model.fact_types:
        for rule in fact_type.get("constraints") or []:
            assert constraint_variant(rule, fact_type) in {"role", "all"}
            assert _is_implemented(rule, fact_type)
            assert not _is_implemented(rule, None)
    for selector in ("role", "all"):
        for event, outcome, reason in (
            ("clean", "pass", None),
            ("violated:alethic", "fail", None),
            ("violated:deontic", "warning", None),
            ("sidecar-absent", "unchecked", "anchor-sidecar-absent"),
            ("non-lexical", "unchecked", "anchor-non-lexical"),
            ("vacuous", "vacuous", None),
        ):
            row = branch(f"snapshot:anchored:{selector}:{event}")
            assert (row.outcome, row.reason_code) == (outcome, reason)

def test_population_only_consumers_declare_source_limit():
    model = load_model(MODEL)
    baseline = json.loads(POPULATION.read_text())
    reference = "fact_types[record_has_label].constraints[0]"
    mutations, stand_downs = operators_for(model, reference, baseline)
    assert mutations == []
    assert "bound source anchor" in stand_downs[0]["mechanism"]
    boundary, unmutated = derive_boundary_cases(model, reference, baseline)
    assert boundary == []
    assert "document and sidecar" in unmutated[0].reason
    assert {"anchor-sidecar-absent", "anchor-non-lexical"}.isdisjoint(BAND4_REASON_CODES)
    assert {"anchor-sidecar-absent", "anchor-non-lexical"} <= set(frontier_codes_for(model))

def test_exporter_and_verbalization_do_not_claim_semantic_export():
    oracle = PyrelOracle.__new__(PyrelOracle)
    status, reason = oracle.evaluate({"type": "anchored"}, "record_has_label")
    assert (status, reason) == ("unsupported", "anchored-needs-bound-source-document")
    rendered = render_model_verbalization(MODEL)
    assert "bound source anchor" in rendered
