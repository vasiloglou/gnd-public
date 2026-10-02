---
id: EXP-511-positional
kind: analysis
title: Address v1 constraints only by position
questions:
  - id: Q1
    text: Are legacy v1 constraints claimable while remaining visibly unstable?
follows: []
covers:
  - constraint: fact_types[borrower_has_name].constraints[0]
  - constraint: constraints[0]
---

# Address v1 constraints only by position

The v1 model has no operations and none of its constraints has a declared id. This
experiment therefore uses one inline and one top-level positional reference.
