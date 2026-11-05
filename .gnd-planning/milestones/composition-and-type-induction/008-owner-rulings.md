---
milestone: composition-and-type-induction
station: owner-rulings
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: CT-close questions
date: 2026-11-04
gate:
  command: "bash .gnd-planning/milestones/composition-and-type-induction/evidence/close/close-gate.sh"
  exit: 0
  output: "1902 passed, 42 deselected; 16 passed; 287 tutorial blocks passed; strict build; 14292 links; ruff clean"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/rulings/close-gate.txt
    sha256: 197330b9d7a02b95a9a52f1d1116decd288971fc63550d2c857917cf56c8c66d
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/rulings/dynamic-query-successor.json
    sha256: e4078200c584c0100cec4b408e6f68856240daec94c04fdb793ca784eada3fcd
  - path: src/gnd/composition.py
    sha256: 53f58a3ddccd3c00e5614e73d9a7dcc3ff6033a4c848fbf6f7e9933d85951acb
  - path: src/gnd/discover/types.py
    sha256: 55fbdbcd8f29b6d96079c51f1e8f255e2a83c51aff2b9670e9d2ff0062ba8031
  - path: src/gnd/discover/service.py
    sha256: 32cb5816f96b1d96316668f121a53211634c5d2f0eb13f4ab5dc7eec8fb2e178
  - path: src/gnd/commands/discover.py
    sha256: 448fe945e0b47676e95e05aa6d085830c70d5ef3ecd11dcdd93350c2e11d8877
  - path: src/gnd/discover.schema.json
    sha256: b9b6b256b63c4a2bd8c3c6cb820a48ed9149d85e4284839a3f1588d4a47d9596
  - path: docs/reference/composition.md
    sha256: 9b5451fd9a0bc003b37c66fbd1c02f42c7c894282af97467b286d191a55a7428
  - path: docs/reference/discover.md
    sha256: 9a04197fb8675eb1593ebb1b3f5b0f211dceb96f763d5a1187569aef9a14b7e5
  - path: docs/how-to/disclosure-mode.md
    sha256: 451500bec309af79ccf41ad9ef492db943b56ddb727791c0bf9d9d18211706fe
  - path: tests/test_composition.py
    sha256: 48a18bb2cf9da2aac1aabbb69d71c5f01d37df2c3fbe24d565576a519d1f9933
  - path: tests/test_discover_fact_type_family.py
    sha256: 6f1c072a1359fd9720e2ad2b7905864c1f51e8d8fc5ea95388d20a048656762a
  - path: tests/support/pyrel_application_successors.py
    sha256: 4a7aba9043eac51038b9471b0956bac7cf8fa87fe19658f25c95945ce7a34729
---

# Owner rulings on the close questions

**Authority.** The owner's own answers in conversation on 2026-11-04, after
reading the close record's question sweep
([007-milestone-close.md](007-milestone-close.md)). These are the owner's
rulings, not delegated ones. For questions 3 to 5 the owner asked for an
explanation or a recommendation, then said "Yes, apply both" to the two
recommendations.

| ID | Question | Owner's answer | Effect |
|---|---|---|---|
| CT-close-Q1 | how the fact-type family detects duplicates so it can keep proposing after one is applied | "semantically with a skill" | deferred to a new milestone: a skill judges semantic duplicates; the CLI stays deterministic and supplies evidence. A planning session was started for it |
| CT-close-Q2 | whether to propose fact types for multi-valued attributes | "with a skill a variant of rai-orm" | deferred to the same milestone: a skill variant of the `rai-orm-from-schema` dialect models them; the deterministic family keeps counting them as `multi_valued` |
| CT-close-Q3 | accept DC1 as missed | explanation given (the docs mock-up was skipped because the auto run started at CT1; DC2 was shown and accepted) | accepted as missed; auto runs should show the docs mock-up before phase 1 |
| CT-close-Q4 | refuse per-role renamings that split a value with no listed instance | recommendation (refuse) applied | `gnd compose` refuses a renaming that renames a value of one object type in one role of a source while another role keeps it, whether or not instances are listed; the error names the renaming index and the fact type and role still using the old value |
| CT4-Q1 | salt or omit the attribute digest | explanation and recommendation (omit under `customer`) applied | the `fact-type` family omits `attribute_sha256` from proposals and shape matches under `customer`; elsewhere it stays the SHA-256 of the name's canonical JSON. The schema makes the field optional |

## What changed

- `src/gnd/composition.py`: the split refusal, independent of instances.
  `tests/test_composition.py`: the case, the no-instance case, and a fixture
  that was itself a split manifest now renames both fact types.
- `src/gnd/discover/types.py`, `service.py`, `src/gnd/commands/discover.py`:
  `show_digests`, false under `customer`. `src/gnd/discover.schema.json`:
  `attribute_sha256` optional. `tests/test_discover_fact_type_family.py`:
  the customer case.
- Docs: `docs/reference/composition.md`, `docs/reference/discover.md`,
  `docs/how-to/disclosure-mode.md`.

Parity without the family and for version-1 inputs is unaffected (the
composition change applies only to `gnd compose`, which is new in this
milestone).

## Still open

CT-close-Q5 (maintenance), CT2-Q1, CT2-Q2, O18, and owner acceptance and
merge of PR #86.
