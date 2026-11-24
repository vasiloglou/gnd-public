# Rmap corpus (OB2)

The fixture corpus for `gnd.rmap`, the Halpin relational mapping of phase OB2
in the ossie-relational-bundle milestone. Under spec ruling S11 it was authored
**before any `gnd.rmap` code**, and the owner approves OB2 by reading the
stories below.

Each case folder holds:
- `model.yaml`: a minimal model that GND's loader admits. It is not named
  `*.orm.yaml` because `tests/test_li0_witness_wire.py` pins the identity of
  every `*.orm.yaml` under `tests/fixtures` against a golden file frozen in
  phase LI0, and that historical pin is not extended here;
- `STORY.md`: what the model says, and in words what a Halpin reader expects.

The exact expected schemas are kept apart in [`answers/`](answers/README.md),
so the stories can be read, or re-derived blind, without them. Variant
answers exist only where the D5 variants differ (07, 08, 15).

| Case | Story |
|---|---|
| 01-functional-binary | [Functional binary (rule 5)](cases/01-functional-binary/STORY.md) |
| 02-popular-reference-fact | [Reference fact type carried as the key (rule 1, S4)](cases/02-popular-reference-fact/STORY.md) |
| 03-general-reference | [General reference](cases/03-general-reference/STORY.md) |
| 04-many-to-many | [Many-to-many binary (rule 6)](cases/04-many-to-many/STORY.md) |
| 05-no-uniqueness | [A fact type with no declared uniqueness (S1)](cases/05-no-uniqueness/STORY.md) |
| 06-one-to-one-one-mandatory | [1:1 with one mandatory role](cases/06-one-to-one-one-mandatory/STORY.md) |
| 07-one-to-one-both-mandatory | [1:1 with both roles mandatory (D5 variant)](cases/07-one-to-one-both-mandatory/STORY.md) |
| 08-one-to-one-neither-mandatory | [1:1 with neither role mandatory (D5 variant)](cases/08-one-to-one-neither-mandatory/STORY.md) |
| 09-unary | [Unary fact type (rule 4, S6)](cases/09-unary/STORY.md) |
| 10-ternary-n-minus-one | [Ternary with an n−1 uniqueness (rule 6, S5)](cases/10-ternary-n-minus-one/STORY.md) |
| 11-quaternary-spanning | [Quaternary with a spanning uniqueness](cases/11-quaternary-spanning/STORY.md) |
| 12-single-and-compound | [A single-role and a compound uniqueness on one fact type (plan F9)](cases/12-single-and-compound/STORY.md) |
| 13-candidate-keys | [Own table with two candidate keys, one preferred](cases/13-candidate-keys/STORY.md) |
| 14-external-identification | [Composite external identification and a composite foreign key (rule 2)](cases/14-external-identification/STORY.md) |
| 15-subtype-inherits | [Subtype inheriting its supertype's identifier (D5 variant)](cases/15-subtype-inherits/STORY.md) |
| 16-subtype-own-identifier | [Subtype with its own identifier](cases/16-subtype-own-identifier/STORY.md) |
| 17-objectification | [Objectification (rule 3, S8)](cases/17-objectification/STORY.md) |
| 18-derived | [Derived fact types (rule 0, S3)](cases/18-derived/STORY.md) |
| 19-unconfirmed-uniqueness | [Proposed and deontic uniqueness (S2)](cases/19-unconfirmed-uniqueness/STORY.md) |
| 20-value-type-table | [A value type as the determining player (S7)](cases/20-value-type-table/STORY.md) |
| 21-self-reference-and-collision | [Self-referencing binary and a column-name collision (S10)](cases/21-self-reference-and-collision/STORY.md) |
| 22-entity-without-table | [An entity with no placements (S7)](cases/22-entity-without-table/STORY.md) |
| 23-unit-based | [Unit-based reference (S9)](cases/23-unit-based/STORY.md) |
| 24-not-relational | [Constraints a relational schema does not carry (§6.4)](cases/24-not-relational/STORY.md) |
| 25-nested-composite | [Unmatchable identification](cases/25-nested-composite/STORY.md) |
