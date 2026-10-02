---
id: EXP-501-corroborated
kind: analysis
title: Exercise every mixed-model address form
questions:
  - id: Q1
    text: Do declared ids and the legacy positional reference resolve to their intended elements?
follows: []
covers:
  - operation: attach_review_note
  - fact_type: work_item_has_note
  - constraint: one_state_per_item
  - constraint: one_priority_per_item
  - constraint: fact_types[work_item_has_state].constraints[1]
---

# Exercise every mixed-model address form

This experiment deliberately claims one operation, one fact type, both constraints that
carry declared ids, and the remaining constraint through its legacy positional address.
