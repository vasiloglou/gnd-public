# Issue 16 compiled snapshot corpus

Public-source model generated from gnd-apps efc9c0e and GND packaged expense data.
No app dependency or private data is required to run these fixtures. The model
contains 9 object types, 47 fact types and 11 operations; retaining the complete
bounded model preserves compiler guards and derived-claim consistency.

The nonnumeric snapshot compares expense_in_category.category (a string) to 5.
The numeric control compares expense_has_amount.amount (a numeric role) to 5.
Both include correct plan_filter_literal, plan_answer_binding and answer_is_scalar
claims. The corresponding walks start from pre.pop.json. Other constraints are
vacuous, so a numeric control may still be inadequate. Read expected.json
separately for baseline and activated successor expectations.
