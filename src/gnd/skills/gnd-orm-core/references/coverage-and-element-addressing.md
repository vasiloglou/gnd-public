# Coverage and element addressing

The one home for two things that are easy to conflate and expensive to get
wrong: **how a model element is named** by anything outside the model, and
**what the coverage view's verdict vocabulary means**. `gnd coverage` produces
that view; this file defines the words it prints.

## The addressable universe

A `covers:` row in an experiment's `SPEC.md` addresses exactly one of four
element classes:

    operation | fact_type | constraint | derivation

**Object types are not addressable, and the coverage view omits them entirely.**
They are not listed as uncovered, because a gap no author could ever close is
not a gap — it is noise that makes the census read as failure. A model
declaring eighteen object types and four fact types is not "eighteen elements
behind"; it has four addressable elements.

## Address forms

| Class | Form | Stability |
|---|---|---|
| operation | `operation:<id>` | stable — ids are declared |
| fact type | `fact_type:<id>` | stable — ids are declared |
| derivation | `derivation:<fact-type-id>` | stable — structured derivations are declared on id-addressed fact types |
| constraint, with a declared `id` | `constraint:<id>` | stable |
| constraint, without one | `fact_types[<ft>].constraints[<i>]` or `constraints[<i>]` | **unstable** |

`gnd check` schema-version-4 reports additionally produce
`derivation:<fact-type-id>` for a derivation obligation. It is deliberately
distinct from the fact type's `fact_type:<id>` address: one claim says the
experiment covers the computed extension, while the other says it covers the
fact type itself. The global parser, `ElementClass`, the `gnd coverage` census,
and experiment `covers:` claims all admit the derivation class coherently.

The positional forms are the exact strings `gnd check` has emitted in every
`ConstraintVerdict` since v1.0, and they remain supported because v1 models
carry no constraint ids at all — refusing them would make every v1 model
permanently unclaimable.

**A positional address is reported as unstable, never refused.** Reordering a
model's constraints silently retargets a positional claim at a different
constraint: the row still matches, the claim still reads as covered, and it now
covers something else. The view prints the word `unstable` on the element row
and lists every such claim in `unstable_addresses[]`, because the failure is
invisible in the address itself. Declaring an `id` on a constraint is the fix,
and it is the only fix.

## The three meanings of "coverage"

The word is already shipped in two other places. They are different things and
none of them is a percentage:

| Where | What it means |
|---|---|
| `population.covers` | the fact types a population declares it populates |
| `report.coverage` (from `gnd check`) | per fact type: whether it was declared, and how many facts were seen |
| `gnd coverage` | the element roadmap defined in this file |

The coverage payload uses **no key named `coverage`** at any level, precisely so
that a reader who greps for the word finds the one they meant.

## The verdict vocabulary

Three statuses, computed identically for all four element classes:

| Status | Definition |
|---|---|
| **corroborated** | a `covers:` row names the element, and a cited payload also names it |
| **claimed** | a `covers:` row names it and no cited payload does |
| **unclaimed** | no `covers:` row names it — a payload may still name it, and that evidence is listed |

Plus one count that is neither, and is the interesting quadrant:
`unclaimed_with_evidence` — the work happened and nobody claimed it.

### What corroboration is not

**A `covers:` row is a claim by the experiment's author, not a measurement.**
Corroboration says a payload produced by some other command named the same
element; it does not say the element is correctly implemented, that the payload
passed, or that the claim was honest.

**Evidence is reachability, never a grade.** A `fail`, `vacuous`, or `unchecked`
verdict corroborates exactly as a `pass` does: the checker reached that element
and said something about it. The view quotes each payload's own vocabulary
verbatim and never translates it, because translating a verdict is the first
step toward scoring it.

**`CONCLUSIONS.md` does not corroborate.** An experiment's conclusions are
written by the same author who wrote its `covers:` rows, so counting one as
evidence for the other is self-corroboration — a claim vouching for itself. The
view records `conclusions-present` on the claim row and it never changes
`status`. This is the single rule that keeps `corroborated` meaning anything.

**A refused walk is not an absence of findings.** A transition payload with
`evaluated: false` was refused *before* evaluation: its `steps` and
`frame_grading` are `null`, not empty. It contributes zero evidence rows and one
row in `sources.refused[]`. "We did not look" and "we looked and found none" are
different facts and the view keeps them apart.

**An exemption is a visible gap.** An experiment carrying
`covers_exemption: "tests-only"` contributes zero claims and one row in
`covers_exemptions[]` — the gap stays on the page rather than being invented
away by a synthetic claim.

## What the view refuses to do

- No aggregate number, no percentage, no `passed`, no score. The moment a
  roadmap emits one number, that number becomes the target.
- No gate. `gnd coverage` exits 0 whenever the view was computed, whatever the
  view shows. It holds no verdict about the work.
- No file, on any path. It writes to stdout and nothing else.
- **No other `gnd` command reads its output.** A committed census is a document
  a human chose to keep, never load-bearing state some other command depends on.
- No nearest-match suggestion for an unmatched cover. It prints the experiment,
  the file, the address as written, and the reason — a fuzzy guess is how an
  author "fixes" a stale claim by accepting the wrong element.

## Which sources the census could not bind

Coverage is assembled from `gnd check` and `gnd verify` payloads. A payload on a
frozen report wire names a model *path* and no model identity, so a row derived
from it cannot be tied to the model this census is about. That evidence is still
useful and is still indexed — refusing it would discard every report written
before model binding existed — but the reader must be able to tell the two apart.

Every output carries `sources.unbound`: one row per source the census read but
could not bind, naming the source kind, its path, its report `schema_version`,
and a stable reason. A frozen report carrying no model identity is disclosed as
`legacy-report-without-model-digest`. Sources are listed per path, never
deduplicated by content or basename: two byte-identical reports at two paths are
two sources, and a reader told about one of them has been told a half-truth.

`sources.unbound` is empty, not absent, when every source was bound. An absent
key would make "nothing was unbound" indistinguishable from "this producer does
not disclose", which is the exact confusion the field exists to end.

A source that *does* carry a model identity, and carries one that is not this
model's, is a different matter entirely: it is not a gap to disclose but a
contradiction to refuse, with `coverage:model-digest-mismatch`. Indexing it
would silently answer a question about one model with evidence about another.

## The model digest, and what it can be verified with

Every payload carries `model.digest`, so a committed census is bound to the
exact model it was derived from and a stale citation is detectable rather than
deprecated by convention.

**Stated as the weaker claim it is:** that digest is
`gnd.transition.model_digest`, which is computed over a Python representation of
the loaded model. It is reproducible **by running gnd**, not by an external
client with `sha256sum` over `model.orm.yaml`. Anyone verifying a committed
census today needs gnd. If a consumer outside Python ever needs to verify one, a
canonical-JSON digest with a stated empty case and a shipped producer is what
that costs, and it is owed then rather than now.
