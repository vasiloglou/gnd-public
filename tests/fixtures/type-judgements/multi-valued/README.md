# Type judgements fixture: multi-valued round two

The second round of a generic fact type `item_has_attribute` (Item,
AttributeName, AttributeValue), after one applied many-to-many induction. It
is the input of the TS4 recorded run of `gnd-model-multivalued` and of
`tests/test_model_multivalued_skill.py`.

- `model.orm.yaml`: the generic fact type; `item_has_attribute_induced_0`,
  applied in round one as a many-to-many fact type and renamed by review
  ("Item is tagged"), whose `provenance.induced_from` names its attribute
  (the digest a real round-one run wrote); and `item_has_label`, a
  hand-modelled many-to-many binary over the value type Label. Both carry a
  uniqueness spanning their two roles.
- `items.population.json`: five attributes over 24 items, with canary names
  that appear in no model text. Every group is `multi_valued`. The applied
  fact type holds the first attribute's pairs; `item_has_label` holds all
  of the second's and half of the fifth's (TS4 review F3). The third has two
  values for half the items and one repeated row; the fourth has a second
  value for one item only.
- `answer-key.json`: the expected verdict per group and the decision rule
  (S1 to S4 of the skill) that gives it. It is never copied into a recording
  workspace; the skill sees only the model and the evidence.
