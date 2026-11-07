"""FU2 (rule-check-followups): population header integrity (issues 115, 116).

The approval instrument for phase FU2 (spec D1): this file lands red before
any source edit. Each test names its spec case (T1-T8). Pinned digests were
measured at main 12daa5b7, before the fix.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from support.repository import REPO_ROOT

from gnd import api
from gnd.model import load_model
from gnd.population import (
    Population,
    _combine_validated_populations,
    load_population,
    load_population_bytes,
)
from gnd.references import bind_population, bind_references
from gnd.values import content_digest
from gnd.witness.io import witness_input_identity

DISPATCH = REPO_ROOT / "tests" / "fixtures" / "reference-corpus" / "dispatch"
FU1 = REPO_ROOT / "tests" / "fixtures" / "fu1-term-reasons"
PRODUCER_MESSAGE = "producer is allowed only with source tool-output"
LENGTH_MESSAGE = "producer must be 1 to 200 characters"

#: The dispatch candidate bound to its references, label unset, at 12daa5b7.
UNLABELLED_COMBINED_DIGEST = "da4730379a19da674f8583c2c63fb08cb412476a3d8a3a568e9a8f78ccb6e465"
#: witness_input_identity for the dispatch candidate labelled "violating", at 12daa5b7.
LABELLED_WITNESS_IDENTITY = {
    "model_digest": "sha256:fab46dd5bddbf385c6984f5c445240b9308de53d3749fb54fe9e8a356961cc3b",
    "candidate_digest": "sha256:25ca34166845eb8c3578dc14330a88f1e229b48b4057a035762060f53644a29d",
    "references": [
        {"id": "catalog", "raw_sha256": "f0bb10d4f6769540041e01c2de21bd3cb3aa8958d06cead9050019bfdd94d214"}
    ],
}


def _tool_output() -> Population:
    return Population(model="m", source="tool-output", producer="gnd-graph 1.2")


def _dispatch(root: Path = DISPATCH, label: str | None = None):
    """Model, references and the candidate (optionally labelled), bound."""
    model = load_model(root / "model.orm.yaml")
    references = bind_references(model, root=root)
    doc = json.loads((root / "candidate.pop.json").read_bytes())
    if label is not None:
        doc["population"]["label"] = label
    candidate = load_population_bytes(
        json.dumps(doc).encode(), source="candidate.pop.json", model=model
    )
    return model, references, candidate


def _relabelled_reference_root(tmp_path: Path, label: str) -> Path:
    """A copy of the dispatch fixture whose reference population carries ``label``."""
    root = tmp_path / "dispatch"
    shutil.copytree(DISPATCH, root)
    reference = root / "references" / "catalog.pop.json"
    old = hashlib.sha256(reference.read_bytes()).hexdigest()
    doc = json.loads(reference.read_bytes())
    doc["population"]["label"] = label
    data = json.dumps(doc, indent=2).encode()
    reference.write_bytes(data)
    model = root / "model.orm.yaml"
    text = model.read_text()
    assert text.count(old) == 1
    model.write_text(text.replace(old, hashlib.sha256(data).hexdigest()))
    return root


# --- issue 115: the producer invariant on copy -------------------------------


@pytest.mark.parametrize(
    ("make", "update", "message"),
    [
        pytest.param(_tool_output, {"source": "fixture"}, PRODUCER_MESSAGE, id="a-source-drops-tool-output"),
        pytest.param(lambda: Population(model="m", source="fixture"), {"producer": "y"}, PRODUCER_MESSAGE,
                     id="b-producer-on-fixture"),
        pytest.param(_tool_output, {"producer": ""}, LENGTH_MESSAGE, id="c-empty-producer"),
        pytest.param(_tool_output, {"producer": "x" * 201}, LENGTH_MESSAGE, id="d-201-characters"),
    ],
)
def test_t1_a_copy_cannot_break_the_producer_invariant(make, update, message) -> None:
    with pytest.raises(ValueError, match=message):
        make().model_copy(update=update)


def test_t2_a_copy_that_keeps_a_valid_pair_succeeds() -> None:
    model = load_model(FU1 / "models" / "terms.orm.yaml")
    population = load_population(FU1 / "populations" / "mod-zero.pop.yaml", model=model)
    same = population.model_copy()
    assert same.matches_validation_marker(model)

    tool = _tool_output()
    assert tool.model_copy(update={"facts": {"f": []}}).producer == "gnd-graph 1.2"
    dropped = tool.model_copy(update={"source": "fixture", "producer": None})
    assert (dropped.source, dropped.producer) == ("fixture", None)


def test_t3_model_construct_is_unvalidated_and_check_refuses_it() -> None:
    """Spec D3: model_construct stays out of scope; this pins why that is safe."""
    model = load_model(FU1 / "models" / "terms.orm.yaml")
    population = load_population(FU1 / "populations" / "mod-zero.pop.yaml", model=model)
    built = Population.model_construct(
        **{**population.__dict__, "source": "fixture", "producer": "z"}
    )
    assert (built.source, built.producer) == ("fixture", "z")
    assert not built.matches_validation_marker(model)
    result = api.check(model, built)
    assert result["exit_code"] == 70
    assert result["error"]["type"] == "UnvalidatedPopulationError"


# --- issue 116: label through the binder -------------------------------------


def test_t4_the_binder_keeps_the_candidate_label() -> None:
    model, references, candidate = _dispatch(label="violating")
    assert candidate.label == "violating"
    assert bind_population(model, candidate, references=references).combined.label == "violating"


@pytest.mark.parametrize(
    ("candidate_label", "expected"),
    [
        pytest.param("violating", "violating", id="candidate-wins"),
        pytest.param(None, None, id="unset-candidate-stays-unset"),
    ],
)
def test_t5_the_candidate_label_wins_over_a_reference_label(tmp_path, candidate_label, expected) -> None:
    root = _relabelled_reference_root(tmp_path, "conforming")
    model, references, candidate = _dispatch(root, label=candidate_label)
    assert references._populations[0].label == "conforming"
    assert bind_population(model, candidate, references=references).combined.label == expected


def test_t6_the_combined_content_digest() -> None:
    model, references, unlabelled = _dispatch()
    unset = content_digest(bind_population(model, unlabelled, references=references).combined)
    assert unset == UNLABELLED_COMBINED_DIGEST

    model, references, labelled = _dispatch(label="violating")
    combined = bind_population(model, labelled, references=references).combined
    expected = content_digest(
        Population(
            model=combined.model,
            model_id=combined.model_id,
            source=combined.source,
            label="violating",
            covers=combined.covers,
            instances=combined.instances,
            facts=combined.facts,
        )
    )
    assert content_digest(combined) == expected != UNLABELLED_COMBINED_DIGEST


def test_t7_the_witness_candidate_binding_does_not_move() -> None:
    model, references, labelled = _dispatch(label="violating")
    assert witness_input_identity(model, labelled, references=references) == LABELLED_WITNESS_IDENTITY


def test_t8_the_combiner_reads_label_from_its_header() -> None:
    model, _references, candidate = _dispatch(label="boundary")
    combined = _combine_validated_populations(
        model,
        (candidate,),
        {
            "format_version": candidate.format_version,
            "population": {
                "model": candidate.model,
                "model_id": candidate.model_id,
                "source": candidate.source,
                "label": candidate.label,
                "covers": candidate.covers,
            },
            "facts": candidate.facts,
            "instances": candidate.instances,
        },
    )
    assert combined.label == "boundary"
