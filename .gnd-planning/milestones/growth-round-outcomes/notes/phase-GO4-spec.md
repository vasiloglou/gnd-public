# Phase GO4 · what a reply carries for an element the model already has · spec r1

## 1. Status

**Draft r1, 2026-11-23, awaiting its gate.** Planning only: no change to
`unattended-growth.md` until reviewed-vocabulary-growth VG2 and VG5 are
merged on `main` (plan §3) and the coordinating session answers
"READY GO4".

## 2. Provenance

- Derives from [plan r4](growth-round-outcomes-plan.md) (sha256
  `b107bd36…7431`): Goal (GO4), R0.6, §1 H15, H16, §2 GO4, §4 GO4-C1 to C3,
  §10 D3.
- From [#227](https://github.com/vasiloglou/gnd-public/issues/227),
  request 2.
- Read at `92cc161f`: `unattended-growth.md` "The reply shape"
  (`:235-291`), the evolution contract's additive matrix (`:250`). No
  review has read these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan GO4, D3 (a) | "The reply shape" states what a reply carries for an element the model already has | §6; T1 |
| plan H16 | today the page says only "ids that already exist are reused" | §6 |
| plan GO4-C2 | a guard test fails when the rule is removed | T2 |
| plan GO4-C3 | the packaged growth example's replies follow the rule, or change here | T3 |
| plan R0.6 | the rule has one home, "The reply shape" | §6 |
| **refuted premise (below)** | D3 (a)'s second half cannot hold under the additive policy | §7 GO4-D2; plan repair at close |

### Refuted premise

Plan r4 D3 (a), second half: a reply "carries rows for it only when the
document adds rows, and then under the existing id". The evolution
contract's additive matrix refuses any change to an existing fact type's
`sample_population` as `fact_types.modify`
(`gnd-model-evolve/references/evolution-contract.md:250`: "a changed
reading, role list, constraint or sample row included"). An unattended
round runs `--policy additive` (`unattended-growth.md`, "What one round
is"), so such rows would always be refused and sink the round, which is
#227's first cause. The plan's text is not rewritten here; the close
repairs it under GO4-D2's ruling, with this record as provenance.

## 4. The standing rules, bound to this phase

- **Totality, caps (rules 1, 2):** no code reads new input; inapplicable.
- **Validation order (rule 3):** inapplicable; no gate changes.
- **One walk (rule 4):** the guard reads the page's one table row, not a
  per-field copy.
- **One home (rule 5):** the rule lives in "The reply shape"; the
  additive matrix stays the home of what is admitted, and the new sentence
  cites it.
- **Measurement (rule 6):** T3 replays the packaged example's proposals
  through the policy to show its replies follow the rule.
- **General solutions:** the guard reads "The reply shape" section by its
  heading and its table rows by their first cell; a table row is one line
  of `|`-separated cells, a flat grammar the split states whole. No pattern
  over the example's JSON: T1 loads it with `json`.

## 5. Goal

"The reply shape" says: a reply names an object type or fact type the model
already has by its id only, wherever a field takes an id (`host`,
`roles[].object_type`, `subtype_links`, a derived rule's body), and never
repeats it in `object_types` or `fact_types`; rows the document gives for
an existing fact type are an `open_questions` entry, because the additive
policy refuses them.

## 6. Design

- The `object_types`, `fact_types` row of the table: "New elements only.
  An element the model already has is named by its id where a field takes
  an id and is not repeated here; the host drops a repeated one and logs
  it." (replacing "ids that already exist are reused").
- The `rows` row: "Rows for a new fact type only. Rows the document gives
  for a fact type the model already has are an `open_questions` entry: the
  additive policy refuses a changed sample row
  (the evolution contract's additive matrix, `../../gnd-model-evolve/references/evolution-contract.md` from the page)."
- The example: one constraint whose `host` is a fact type the model is
  assumed to hold (`policy_has_holder`), stated in one sentence above the
  example, beside the new fact type it already shows.
- No change to the host's translation outside the page; the test-only
  translator (`tests/test_unattended_growth_guidance.py:_translate`)
  already treats `host` as an id.

Homes: `unattended-growth.md`, `tests/test_unattended_growth_guidance.py`,
and the packaged growth example only if T3 finds a repeated element.

## 7. Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| GO4-D1 | Instrument | prose | prose |
| GO4-D2 | Rows for an existing fact type (refuted premise) | (a) an `open_questions` entry, the owner's to apply in a reviewed round. (b) a modify operation: refused by the additive policy every time. (c) a new GND admission for appended rows: a policy change the plan's R0.2 excludes | (a) |
| GO4-D3 | Object types too | (a) the rule covers object types and fact types alike: both are restated today (#227 counted fact types). (b) fact types only | (a) |

## 8. Tests

| # | Case | Expected |
|---|---|---|
| T1 | the page's table rows and its example (loaded with `json`) | the two rows carry the rule; the example has a reused `host` |
| T2 | the guard with the rule's sentence removed, and with "ids that already exist are reused" restored | fails both times (GO4-C2) |
| T3 | the packaged growth example's replies through `_translate` and the additive policy | no operation adds an element the model before that round has; no `fact_types.modify` (GO4-C3) |
| T4 | the existing `tests/test_unattended_growth_guidance.py` and `tests/test_growth_example.py` | exit 0 |

Gate: plan §9 GO4 lane, guard block, both lint commands, component check.

## 9. Out of scope

A GND check that refuses a repeated element (the host drops it); any
policy change (R0.2); GO5's summary of reused ids.

## 10. Size

About 15 lines of page and 60 lines of test.

## 11. Approval instrument

This prose.

## 12. Gate — delegated approval (auto=true)

**Delegated approval (auto=true), 2026-11-23**, of this spec r1, sha256
`35e84f907b0d6f40f20c3df32776e30a581f68e1ab6f38dd3e1163fadf7a8ed5` (the bytes above this section). Authorization: the owner's
delegation of `auto` for growth-round-outcomes, recorded in
`001-plan-gate.md`. An agent ruling under that delegation, not the owner's
reading of the spec. No spec review ran (optional, omitted).

- Rulings: GO4-D1 prose; GO4-D2 (a); GO4-D3 (a) [delegated].
- Sweep: the additive matrix refuses changed sample rows (`fact_types.modify`), which refutes plan D3 (a)'s second half; GO4-D2 (a) repairs it within the plan's goal (GO4-C1) and is carried to the close as a plan repair.
- Budget: one diff review round (D8), a second only if the first blocks.
- **Approval is of the design only. Implementation waits** for the
  start condition of plan §3 on `main` and the coordinating session's
  "GO" to "READY GO4". A spec approved now is re-read against `main` at
  that start; a change on `main` that moves a cited line or a premise
  amends this spec before code, with the prior wording retained.

## 13. Amendment r2 (2026-11-23)

The quoted page text in §6 carried a markdown link written relative to the
page it will land in, `unattended-growth.md`; from this note it pointed
nowhere and `tests/test_development_scaffold.py` refused it. r2 writes the
same target as a code span. Prior wording, retained in words (the scaffold
guard reads link syntax even inside a code span): a markdown link with the
text "evolution contract" to `../../gnd-model-evolve/references/evolution-contract.md`,
followed by ", the additive matrix", in parentheses.
The page itself gets the working link when GO4 edits it. No ruling changes.

### Gate of r2

**Delegated approval (auto=true), 2026-11-23**, of spec r2, sha256 `ad48ad7794a279428478b59b906802a110dc97dfb93b338721951bcf49f5ee62`
(the bytes above this subsection). r1's approval (§12) is retained as history.

## 14. Implementation findings

1. VG5 (on `main` at `8fea6da5`) added "Starting from a reviewed
   vocabulary": on a seeded root an element the model already has may be
   an included one. The rule says "its own or included".
2. The packaged examples ship proposals, not replies, so T3 reads the
   proposals of `growth` and `seeded_growth`: no `add` names an element the
   round's before-model has, and no element operation is other than `add`.
3. `tests/test_packaged_skills.py` pins the number of relative links in the
   packaged skills (248). The new `rows` row cites the matrix by name, not
   by a second link, so the pin does not move.
4. The guard reads the section by its heading and the table rows by their
   first cell; the example is loaded with `json`, as the existing guidance
   test does.
