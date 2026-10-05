import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import copy
import json
from pathlib import Path

from gnd.checker import structured_extension_facts
from gnd.coverage import _element_universe
from gnd.model import Model, semantic_validate
from gnd.model_verbalization import render_model_verbalization
from gnd.population import load_population
from gnd.transition import model_digest, operations_digest
from tests.support.v62_phase4_corpus import CASES_DOC, FIXTURE, document


def test_aggregate_fixture_evaluates_exact_grouped_extensions() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC["population"], model=model)
    extensions = structured_extension_facts(model, population)
    assert [dict(row) for row in extensions["scenario_count"]] == [
        {"scenario": "north", "count": 3},
        {"scenario": "south", "count": 1},
    ]
    assert [dict(row) for row in extensions["scenario_sum"]] == [
        {"scenario": "north", "sum": 320},
        {"scenario": "south", "sum": 180},
    ]
    assert [dict(row) for row in extensions["zero_sample_scenario"]] == [{"scenario": "empty"}]


def test_aggregate_rejects_an_unbound_head_group_key() -> None:
    document_with_error = copy.deepcopy(document())
    document_with_error["fact_types"][1]["derivation_rule"]["head"]["scenario"] = "$missing"
    assert "semantic:aggregate-head-scope" in {
        issue.rule_id for issue in semantic_validate(document_with_error)
    }


def test_v01_aggregate_verbalization_names_group_value_over_and_result() -> None:
    rendered = render_model_verbalization(Model.model_validate(document()))
    assert (
        "group by $scenario; aggregate count of $sample distinctly over ($sample) as $count"
    ) in rendered


def test_v02_canonical_reference_names_order_and_negation_alternative() -> None:
    reference = (
        Path(__file__).resolve().parents[1]
        / "src/gnd/skills/gnd-orm-core/references/representation-format.md"
    ).read_text(encoding="utf-8")
    assert "The normative aggregate order is:" in reference
    assert "An empty body produces no group" in reference
    assert "`scenario_has_sample`" in reference
    assert "`negate`" in reference
    assert "are the only admitted keys" not in reference
    assert "(aggregation, disjunction)" not in reference
    malformed = document()
    malformed["fact_types"][1]["derivation_rule"]["or"] = []
    shape_messages = [
        issue.message
        for issue in semantic_validate(malformed)
        if issue.rule_id == "semantic:derivation-rule-shape"
    ]
    assert shape_messages
    assert all("aggregation, arithmetic" not in message for message in shape_messages)
    from gnd.model import _layer1_structural

    public_messages = [issue.message for issue in _layer1_structural(malformed)]
    assert public_messages
    assert all("aggregation, arithmetic" not in message for message in public_messages)


def test_v03_each_aggregate_has_one_rule_level_coverage_address() -> None:
    model = Model.model_validate(document())
    universe, _positional = _element_universe(model)
    addresses = [address for address, _kind, _mode in universe]
    assert addresses.count("derivation:scenario_count") == 1
    assert not any(address.startswith("derivation:scenario_count:") for address in addresses)


def test_v04_canonical_and_vendored_aggregate_schemas_match() -> None:
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "src/gnd/schema/orm-meta.schema.json").read_bytes()
    vendored = (root / "src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json").read_bytes()
    assert canonical == vendored
    schema = json.loads(canonical)
    assert '"aggregate"' in json.dumps(schema)


def test_walk_digests_bind_the_future_loaded_model_bytes() -> None:
    model = Model.model_validate(document())
    walk = json.loads((FIXTURE / CASES_DOC["steps"]).read_text(encoding="utf-8"))
    assert walk["model_digest"] == model_digest(model)
    assert walk["operations_digest"] == operations_digest(model.operations)
