from pathlib import Path

import pytest

from gnd.correspondence import CorrespondedFinding, project_finding
from gnd.semantic_adapter import SnapshotObservation
from gnd.semantic_ir import Scalar

ROOT = Path(__file__).resolve().parents[1]

def test_correspondence_evidence_cannot_be_constructed_by_a_caller() -> None:
    from gnd.assurance import CorrespondenceEvidence

    with pytest.raises(TypeError, match="authenticated evidence loader"):
        CorrespondenceEvidence(  # type: ignore[call-arg]
            (), (), None, None, ()
        )


def test_semiderived_origins_retain_only_the_rows_that_produced_them(
    tmp_path: Path,
) -> None:
    from gnd.checker import _constraint_view, _evaluate_derivations
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.semantic_adapter import adapt_snapshot_observed

    fixture = (
        ROOT / "tests/fixtures/derivation-evaluation/cases" / "constraint-semiderived-computed-view"
    )
    model = load_model(fixture / "model.orm.yaml")
    population_path = tmp_path / "population.yaml"
    population_path.write_text(
        """population:
  model: model.orm.yaml
  model_id: urn:gnd-fixture:derivation-evaluation:constraint-semiderived-computed-view@1
  source: fixture
  label: boundary
  covers: [seed, result]
instances: {}
facts:
  seed: [{item: alpha}, {item: beta}]
  result: [{item: alpha}, {item: beta}]
""",
        encoding="utf-8",
    )
    population = load_population(population_path, model=model)
    extensions, _verdicts = _evaluate_derivations(model, population)
    effective = _constraint_view(model, population, extensions)

    adapted = adapt_snapshot_observed(
        model,
        population,
        effective_facts=effective.facts,
        effective_lineage=effective.lineages,
    )
    lineages = {
        origin.path: origin.dependency_paths
        for origin in adapted.observation.origins
        if origin.derivation_fact_type == "result"
    }

    assert lineages == {
        ("facts", "result", 0, "item"): (("facts", "seed", 0),),
        ("facts", "result", 1, "item"): (("facts", "seed", 1),),
    }


def test_projection_refuses_a_witness_without_an_admissible_origin() -> None:
    scalar = Scalar("number", "1/1", 1, 1, True, "number")
    finding = CorrespondedFinding(
        scope_id="snapshot:mandatory:inline:violated:alethic",
        constraint_id="fact_types[x].constraints[0]",
        family="mandatory",
        modality="alethic",
        verdict="fail",
        reason_code=None,
        witness=((scalar,),),
        witness_keys=(),
        applicable_scope_ids=("snapshot:mandatory:inline:violated:alethic",),
    )
    observation = SnapshotObservation((), (), (), ())
    with pytest.raises(ValueError, match="admissible origin"):
        project_finding(finding, observation)
