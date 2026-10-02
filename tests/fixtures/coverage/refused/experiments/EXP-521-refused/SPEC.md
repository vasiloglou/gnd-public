---
id: EXP-521-refused
kind: analysis
title: Distinguish failed evidence from a refused walk
questions:
  - id: Q1
    text: Does failed check evidence corroborate while a refused transition contributes nothing?
follows: []
covers:
  - operation: submit_expense_to_workday
  - constraint: fact_types[expense_has_status].constraints[0]
---

# Distinguish failed evidence from a refused walk

The operation is claimed, but the refused transition must not corroborate it. The positional
constraint is named by the all-fail check payload and must be corroborated despite `fail`.
