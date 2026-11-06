# Example: judging induced fact types

Round two of one generic fact type, `item_has_attribute` (an item has an
attribute with a value), after one applied induction. It is the input of the
how-to "Judge induced fact types with two skills" (`docs/how-to/judge-induced-fact-types.md`).

- `duplicates/`: a model whose earlier induction was applied and renamed by
  review, a hand-modelled `item_has_colour`, and a population of four
  attributes. `duplicates.judgements.json` is the file `gnd-judge-fact-types`
  wrote in a recorded Claude Code session (Sonnet 5.5, 2026-11-05).
- `multi-valued/`: a model whose earlier induction was applied as a
  many-to-many fact type, a hand-modelled `item_has_label`, and a population
  of five attributes with several values per item. `shapes.judgements.json`
  is the file `gnd-model-multivalued` wrote in a recorded session (Sonnet
  5.5, 2026-11-05).

The attribute names in the populations are deliberately meaningless, so a
judge that reads only the evidence cannot see them. Each judgements file is
bound to the evidence `gnd discover --type-evidence` writes for its folder
in unset disclosure mode without `--show-values`.
