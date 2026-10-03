"""Production trace refusal controls; no proof tool or certificate run."""
from pathlib import Path

import pytest

from gnd import proof_kernel
from gnd.checker import check
from gnd.model import load_model
from gnd.population import load_population

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "tests/fixtures/public-phase1-trace"


def test_a_fourth_constraint_withholds_the_trace(tmp_path: Path) -> None:
    """Review finding R4, reproduced red before repair: A14.1 admits at most
    three constraints, yet a four-constraint model received a phase1 trace --
    the whole-result claim -- because nothing counted constraints anywhere.
    The predicate sees one SliceInput at a time, so the count gate lives at
    the one place that sees them all: the trace decision."""
    import copy
    import io

    from ruamel.yaml import YAML

    yaml = YAML(typ="safe", pure=True)
    base = CORPUS / "fixtures" / "c01"
    model_doc = yaml.load((base / "model.orm.yaml").read_text(encoding="utf-8"))
    target = next(ft for ft in model_doc["fact_types"] if ft.get("constraints"))
    constraint = copy.deepcopy(target["constraints"][0])
    target["constraints"] = [copy.deepcopy(constraint) for _ in range(4)]
    buffer = io.StringIO()
    yaml.dump(model_doc, buffer)
    (tmp_path / "model.orm.yaml").write_text(buffer.getvalue(), encoding="utf-8")
    population_text = (base / "population.yaml").read_text(encoding="utf-8")
    (tmp_path / "population.yaml").write_text(population_text, encoding="utf-8")
    model = load_model(tmp_path / "model.orm.yaml")
    population = load_population(tmp_path / "population.yaml", model=model)
    report = check(model, population)
    assert len(report.verdicts) == 4
    assert report.phase1_trace is None, (
        "a model above the admitted constraint bound carried the whole-result claim"
    )

def test_a_subtype_widened_universe_withholds_the_trace() -> None:
    """Review finding R8, reproduced red before repair: N2 excludes subtype
    closure from the slice, yet a subtype model's mandatory constraint was
    admitted with the closure-widened universe and shipped a phase1 trace --
    the right bytes under CORE-06 semantics, but a slice-coverage claim over a
    semantic path the proof does not model. The bridge must refuse, and the
    legacy path must decide, exactly as it does for every other exclusion."""
    model = load_model(REPO_ROOT / "tests/fixtures/adversarial/models/subtype_mandatory.orm.yaml")
    population = load_population(
        REPO_ROOT / "tests/fixtures/adversarial/populations/subtype_mandatory.no_plate.yaml",
        model=model,
    )
    report = check(model, population)
    assert [verdict.verdict for verdict in report.verdicts] == ["fail"]
    assert report.phase1_trace is None, "a subtype-closed universe carried the slice-coverage claim"

def test_t23_an_upgraded_scope_predicate_reds_the_refusal_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T23 (review finding R5): the in-scope predicate is a semantic decision,
    so widening it -- accepting what the slice refuses -- must red a named
    gate. The named gate is the kernel refusal table
    (tests/test_v6_phase1_kernel.py's hostile rows, which assert
    phase1_decide(hostile) is None): with the predicate upgraded to accept
    everything, phase1_decide DECIDES a contradictory-bounds input it must
    refuse, so those assertions fail. The production wire cannot carry this
    mutation alone because the bridge's candidate builder refuses the
    out-of-scope families before the predicate runs -- that layering is
    defense in depth, and this test documents it rather than pretending the
    wire observes the predicate directly."""
    hostile = proof_kernel.SliceInput(
        "constraints[0]",
        "frequency",
        "alethic",
        True,
        True,
        (),
        (),
        (proof_kernel.SliceGroup(("p1",), 1),),
        2,
        1,
    )
    assert proof_kernel.phase1_decide(hostile) is None
    monkeypatch.setattr(proof_kernel, "phase1_in_scope", lambda value: True)
    decided = proof_kernel.phase1_decide(hostile)
    assert decided is not None, "the upgrade was not observable, so no gate could red on it"
    assert decided.verdict in proof_kernel.SLICE_VERDICT_NAMES
