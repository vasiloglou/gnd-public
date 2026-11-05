# Type judgements fixture: round two

The second round of a generic fact type `item_has_attribute` (Item,
AttributeName, AttributeValue), after one applied induction. It is the input
of the TS3 recorded run of `gnd-judge-fact-types` and of
`tests/test_judge_fact_types_skill.py`.

- `model.orm.yaml`: the generic fact type; `item_has_attribute_induced_0`,
  applied in round one and renamed by review ("Item has dimension"), whose
  `provenance.induced_from` names its attribute; and `item_has_colour`, a
  hand-modelled binary over the value type Colour.
- `items.population.json`: four attributes over 24 items, with canary names
  that appear in no model text. The applied fact type holds the first
  attribute's pairs; `item_has_colour` holds all of the second attribute's
  pairs and half of the fourth's.
- `answer-key.json`: the expected verdict per group and the decision rule
  (R1 to R4 of the skill) that gives it. It is never copied into a recording
  workspace; the judge sees only the model and the evidence.

Every group is a `shape_match` against `item_has_attribute_induced_0`,
because every group of one generic fact type has the same role players.
