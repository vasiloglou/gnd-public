---
id: EXP-504-conclusions-without-evidence
kind: analysis
title: Claim an element no payload names, and write conclusions about it
questions:
  - id: Q1
    text: Does a CONCLUSIONS.md beside a claim promote that claim to corroborated?
follows: []
covers:
  - operation: flag_work_item
---

# Claim an element no payload names, and write conclusions about it

This experiment exists to make **D6 falsifiable**, and it is the only case in the
corpus that can do so.

`flag_work_item` is the one addressable element in this tree that no cited
payload names. This experiment claims it and DOES carry a `CONCLUSIONS.md`. So
the element carries two claims -- `EXP-502`'s without conclusions and this one
with them -- and no evidence at all.

Its status must therefore remain `claimed`. If a build ever treated
`conclusions-present` as corroboration, this row and this row alone would flip to
`corroborated`, and the census would move with it. Every other
`conclusions-present` claim in this tree sits on an element a payload already
corroborates, where the two readings are indistinguishable -- which is exactly
how the rule shipped unguarded until a mutation found it.
