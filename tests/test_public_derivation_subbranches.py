"""Raw full-evaluation controls for F01--F04 subbranches found in review."""

from __future__ import annotations

from pathlib import Path

import pytest

from gnd import checker
from gnd.model import ModelValidationError, load_model
from gnd.population import load_population


def _check(tmp_path: Path, model_text: str, population_text: str):
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.yaml"
    model_path.write_text(model_text, encoding="utf-8")
    population_path.write_text(population_text, encoding="utf-8")
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    return checker.check(model, population)


HEADER = """version: 1
model_id: urn:gnd-fixture:phase5-review@1
source: {kind: text-conversation, confidence: standard, mode: one-shot}
object_types:
  - {id: item, name: Item, kind: value, primitive: String}
"""


def test_repeated_variables_and_positive_and_negative_literals_reach_full_evaluation(tmp_path):
    model = (
        HEADER
        + """fact_types:
  - id: pair
    reading: "{Item} pairs with {Item}"
    roles: [{object_type: item, role_name: left}, {object_type: item, role_name: right}]
  - id: link
    reading: "{Item} links to {Item}"
    roles: [{object_type: item, role_name: left}, {object_type: item, role_name: right}]
  - id: tag
    reading: "{Item} has {Item}"
    roles: [{object_type: item, role_name: item}, {object_type: item, role_name: tag}]
  - id: blocked
    reading: "{Item} has blocker {Item}"
    roles: [{object_type: item, role_name: item}, {object_type: item, role_name: marker}]
  - id: result
    reading: "{Item} qualifies"
    roles: [{object_type: item, role_name: item}]
    derivation: derived
    derivation_rule:
      body:
        - {fact_type: pair, bind: {left: "$x", right: "$x"}}
        - {fact_type: link, bind: {left: "$x", right: "$y"}}
        - {fact_type: tag, bind: {item: "$y", tag: keep}}
      negate:
        - {fact_type: blocked, bind: {item: "$y", marker: blocked}}
      head: {item: "$y"}
constraints: []
rejected_proposals: []
"""
    )
    population = """population:
  model: model.orm.yaml
  model_id: urn:gnd-fixture:phase5-review@1
  source: fixture
  covers: [pair, link, tag, blocked, result]
instances: {}
facts:
  pair: [{left: a, right: a}, {left: b, right: c}]
  link: [{left: a, right: z}]
  tag: [{item: z, tag: keep}, {item: z, tag: nope}]
  blocked: []
  result: [{item: z}]
"""
    report = _check(tmp_path, model, population)
    assert report.derivations[0].verdict == "pass"


def test_disconnected_two_by_three_product_and_empty_factor_are_fully_evaluated(tmp_path):
    model = (
        HEADER
        + """fact_types:
  - id: left_seed
    reading: "{Item} is a left seed"
    roles: [{object_type: item, role_name: item}]
  - id: right_seed
    reading: "{Item} is a right seed"
    roles: [{object_type: item, role_name: item}]
  - id: result
    reading: "{Item} pairs with {Item}"
    roles: [{object_type: item, role_name: left}, {object_type: item, role_name: right}]
    derivation: derived
    derivation_rule:
      body:
        - {fact_type: left_seed, bind: {item: "$left"}}
        - {fact_type: right_seed, bind: {item: "$right"}}
      head: {left: "$left", right: "$right"}
constraints: []
rejected_proposals: []
"""
    )
    six = """population:
  model: model.orm.yaml
  model_id: urn:gnd-fixture:phase5-review@1
  source: fixture
  covers: [left_seed, right_seed, result]
instances: {}
facts:
  left_seed: [{item: l1}, {item: l2}]
  right_seed: [{item: r1}, {item: r2}, {item: r3}]
  result:
    - {left: l1, right: r1}
    - {left: l1, right: r2}
    - {left: l1, right: r3}
    - {left: l2, right: r1}
    - {left: l2, right: r2}
    - {left: l2, right: r3}
"""
    assert _check(tmp_path, model, six).derivations[0].verdict == "pass"
    empty = six.replace(
        "right_seed: [{item: r1}, {item: r2}, {item: r3}]", "right_seed: []"
    ).replace(
        "  result:\n    - {left: l1, right: r1}\n    - {left: l1, right: r2}\n    - {left: l1, right: r3}\n    - {left: l2, right: r1}\n    - {left: l2, right: r2}\n    - {left: l2, right: r3}",
        "  result: []",
    )
    assert _check(tmp_path, model, empty).derivations[0].verdict == "pass"


def test_grounded_existence_guard_remains_an_explicit_unproved_refusal(tmp_path):
    model = (
        HEADER
        + """fact_types:
  - id: seed
    reading: "{Item} is seeded"
    roles: [{object_type: item, role_name: item}]
  - id: flag
    reading: "{Item} is a flag"
    roles: [{object_type: item, role_name: item}]
  - id: result
    reading: "{Item} qualifies"
    roles: [{object_type: item, role_name: item}]
    derivation: derived
    derivation_rule:
      body:
        - {fact_type: seed, bind: {item: "$item"}}
        - {fact_type: flag, bind: {item: ready}}
      head: {item: "$item"}
constraints: []
rejected_proposals: []
"""
    )
    present = """population:
  model: model.orm.yaml
  model_id: urn:gnd-fixture:phase5-review@1
  source: fixture
  covers: [seed, flag, result]
instances: {}
facts:
  seed: [{item: alpha}]
  flag: [{item: ready}]
  result: [{item: alpha}]
"""
    with pytest.raises(ModelValidationError, match="existence guard"):
        _check(tmp_path, model, present)
    absent = present.replace("flag: [{item: ready}]", "flag: []").replace(
        "result: [{item: alpha}]", "result: []"
    )
    with pytest.raises(ModelValidationError, match="existence guard"):
        _check(tmp_path, model, absent)
