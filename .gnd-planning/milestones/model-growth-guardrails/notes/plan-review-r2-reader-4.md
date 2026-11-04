# Confirmation reader 4 -- test design, falsifiability

Retained text of the reader's returned report, lightly edited for layout.
Confirmation round (round 2) over r2 of both milestones. Scratch paths read
`<scratch>`.

All four r2 SHA-256 match. Read-only at `1446f90`. Probes:
`<scratch>/plan-review-r2/reader4/` (`probe_*.py`). 12 findings, 11
r2-introduced: the self-inflicted ratio exceeds one half, so the declared
stop rule fires (repair without another round).

**Verdict: request-changes.** B and J resolved; H and E mostly; A, C, D, F,
G and I still have declared branches or fixtures that cannot fail.

## Theme status

| Theme | Status | Evidence |
|---|---|---|
| A | partly | corpus probe (282 accepted, 118 with rules, 301 rules, 19 prose): T3 passes 282/282; T3b's `text[:-1]` passes 0; floors confirmed; gaps F5, F6 |
| B | resolved | 23 path-input crashes, 0 loaded (reproduced); T7 gap F12 |
| C | partly | every mutation refused (probed); D6 loads and renders; gaps F7, F8 |
| D | partly | falsifiable through MG2-C4's bytes table; MG2-C3 cannot tell its refusals apart (F4) |
| E | resolved | MG2-C2/C3 pin absence and invariance (minor F12) |
| F | partly | F1, F2, F3 |
| G | partly | F9 |
| H | resolved | 4,000 short-key anchors measure 826 KB (the spec's 961 KB is fixture-dependent); counter gap F11 |
| I | partly | F10 |
| J | resolved | §2.2, CT2-C4, CT-D4 agree; the C4 case can fail (compose 0, check 1) |

CT-D2: T3 and T4 tell "every" from "any", "first only" and "last only"
(today's keep-last). Sound.

## Findings

**C4-F1 (blocking; r2-introduced) -- MG §2.2 MODIFY cells, MG2-C1/C2.** An
element MODIFY replaces the whole element (`service.py:915-916`,
`collection[index] = after`), including a fact type's embedded
`constraints`, `roles`, `sample_population`. The fact-type MODIFY cell
refuses a closed list and admits "only description/rationale"; every other
key has no verdict and no case, so a mandatory or uniqueness constraint added
through an element MODIFY on a populated fact type bypasses the Constraint
row. `objectification` is not a schema property (`objectified_as` is);
`$defs.fact_type` has no `description`, so that admitted half is
unreachable. Object-type MODIFY leaves `primitive`, `precision`, `scale`,
`kind`, `independent`, `inherits_reference` without a verdict. Reproduced
from source and the schema. Repair: whitelist MODIFY cells (admitted iff the
diff touches only description or `rationale`, else refused); cases for a
constraint added through an element MODIFY on a populated fact type, for
`objectified_as`, for `primitive`; drop the fact-type description cell.

**C4-F2 (high; r2-introduced) -- §2.2 Role ADD and `operations` rows, MG2-C1.**
`service.py:634-637` gates a role ADD only when an existing operation
references the fact type; probe: a role ADD on bookrec (no operations) is
admitted by `_enforce_operations_gate`. So "already gated today" is false,
and a fixture built on it either masks the policy (18 first) or passes an
unimplemented refusal. The operations gate always exits 18 on operations
MODIFY, RENAME, DELETE before the policy runs, so those cells cannot fail
under the opposite verdict. Repair: the policy refuses role ADD on its own,
tested on a model with no operations (3); mark operations MODIFY, RENAME,
DELETE "pre-empted by 18", with no policy case; policy-cell fixtures carry no
operation referencing the subject.

**C4-F3 (medium; r2-introduced) -- §2.2 Constraint rows.**
`ConstraintLocator.host == "model"` has no row; "on a populated fact type"
does not say any or every spanned fact type, and no fixture discriminates.
Repair: a row and a case with a model constraint spanning one populated and
one unpopulated fact type. **Owner** picks the reading (proposed: any).

**C4-F4 (medium; r2-introduced) -- MG2-C3.** Every expected result is 3, but
option mismatch, digest or version refusal (`EvolutionError`) and the re-run
all exit 3; the tamper case cannot show "caught only by the re-run". Repair:
assert the refusal names the re-run issue (operation index and cell); a
mutation control with the re-run disabled applies (0).

**C4-F5 (medium; r2-introduced) -- MG1 T3.** Only ` reading=` occurs in the
corpus (282/282); the other two continuations have no case. Probe: a derived
fact type with `redact: true`, and one with `depends_on`, both validate.
Repair: T3d with both.

**C4-F6 (medium; r2-introduced) -- MG1 T3c.** `_canonical` JSON-escapes
constants (`"a\u0007b"` reaches the text as the six characters `\u0007`), so
`line_text` has nothing to escape and T3c passes even without it. Probe: a
variable `$u`+U+0007 validates and the raw character reaches
`_derivation_cnl`. Repair: use the variable; assert `\x07` present and the
raw character absent.

**C4-F7 (medium; r2-introduced) -- MG1 fallback table, T4b.** bookrec is below
model version 3, so any `date_add` (even valid) is refused with "temporal
syntax requires model version 3"; the arity row cannot fail. bookrec has no
`where`, so `where[0]` rows build new structure, and T4b checks only
"raises". Repair: a nearest-valid control per row (probed: `$u != $b`
loads); assert the refusal names the mutated element; the `date_add` row on a
version ≥ 3 model.

**C4-F8 (medium; r2-introduced) -- MG1 Design, "raises `VerbalizationError`
… cannot happen through the public path".** `_coerce_model` returns a `Model`
unrevalidated, and a loaded `Model` holds mutable dicts. Probe: setting
`head` to `"x"` in place makes `render_model_verbalization` raise
`AttributeError`; `body[0] = "x"` renders partially (`when "x" and …`). The
`VerbalizationError` branch is reachable, has no case, and "asserts the model
is validated" has no mechanism. Repair: T4c mutates a loaded `Model` per row
and expects `VerbalizationError` and no partial text; name the mechanism.

**C4-F9 (medium; r2-introduced) -- MG5 U3, MG5-C2.** U3 is subsumed: an
`explicit`/`user-supplied` constraint is `confirmed` (U2) or not
(`semantic:status-source`, `_validation.py:884`, every mode); no fixture
violates U3 alone. "One case per rule" leaves branches: U1 has 5, U4 2, U5 3,
U7 2, U8 3; U6 needs two or more rows with `sample_spans` covering one (the
any/every trap). Repair: drop or record U3 as subsumed; one case per branch;
assert each `semantic:unattended-*` rule id.

**C4-F10 (medium; r2-introduced) -- CT1 P1–P3, T11, CT1-C4.** Probe: the
parser also refuses inputs `json.loads` accepts: duplicate keys, `NaN`,
`1e400`, a 19-digit integer. The list is incomplete; T11 runs over fixtures
and T2 only, so cannot expose it; P2 (start ≥ end, probed refused) and P3
(> 1 MiB) have no T2 case. Repair: list every parser-only rule; one T2 case
each, including start = end and a sidecar over 1 MiB.

**C4-F11 (low; r2-introduced; unproved) -- CT1 T8.** 1,000 rows × 4 anchors
never exercises per-(row, role) growth; T2's 4,000-on-one-role is parse-only.
Repair: a check-time case with 4,000 anchors on one (row, role), counting
evaluations (4,000) and occurrence-set insertions.

**C4-F12 (low; r2-introduced) -- MG1 T7/T11, MG3.** T7 hashes only loaded
renders, which never crash, so its exception list is vacuous; the path fix is
checked on 2 models (T1b): record path-input digests for all 282. T11 does not
fix its selection; with `fact_types=None` the per-id lookup never runs: run
with 2,000 ids, reversed, with duplicates. MG3 lacks its own MG-R1 table: add
one.

**Pre-existing (folded into C4-F2):** the role-ADD premise first appears in
the round-1 disposition (R4-F5, theme F); r2 adopted it as matrix text.
