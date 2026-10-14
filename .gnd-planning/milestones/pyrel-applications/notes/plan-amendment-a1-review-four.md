# Amendment A1 review — reviewer four

Reviewed 2026-10-13 through the owner-selected local review instrument. Subject:
entire `notes/plan-amendment-a1.md`, against the original plan r1.

Amendment SHA-256:
`f1f79833476921fdbfd4a04e6360739b6f67d733f7cf2dcac4e9cf488245f698`.

Original plan SHA-256:
`a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`.

Scope: honest agreement denominator, product/tutorial claims, independently
computed completeness, limits on equivalence claims and governance. No other
seat's outputs were read. No paid calls.

## Verdict and findings

**Approve amendment A1 within this scope. No actionable amendment findings.**
This opinion does not itself enact the delegated amendment gate or approve PA0
completion, production implementation, merge, release or certification.

The amendment repairs an incompatible comparison predicate without relaxing
the application contract. Original plan `notes/pyrel-applications-plan.md:197-204`
requires computed eligibility and independent claim checking. Unconditional
rule-row agreement would instead require copying the current GND use of supplied
eligible claims. A1 `:9-17` identifies that conflict precisely; `:24-30` retains
all native checking and demands separately authored expected native results.

The denominator is auditable: A1 `:31-36` requires comparable rows, compared rows
and matches, separately lists excluded disagreements, and prohibits exclusion
of an unlisted mismatch. A1 `:37-44` limits the initial exclusions to two named
`constraints[3]` outcomes and requires another explicit amendment for further
runtime-measured disagreements. Thus 100% can only describe the named comparable
denominator. It cannot describe all emitted rows or universal ORM equivalence.
The separate native answer-key requirement applies even to excluded comparison
rows, so exclusion cannot make a wrong native result pass.

The two disagreement inputs remain refusals through independent derivation
checking (`:39-41`). No successful business acceptance exception is introduced.
The amendment preserves all product/evolution paths, six graphics, executed docs
and installed-wheel gates (`:53-55`), and explicitly preserves GND's public
behavior and historical evidence (`:45-46`). Tutorials must continue to describe
computed versus claimed sources accurately; the unchanged source-grounded
graphic and result-mapping requirements already cover that obligation.

## Independent reproduction

Ran the current local `.venv/bin/python` against the public `gnd.api.check`
interface and `src/gnd/examples/bookrec/complete.orm.yaml`. This is GND checking,
not a PyRel/native successor execution.

| Input | GND `constraints[3]` | GND eligible derivation | Overall result |
|---|---|---|---|
| `tests/fixtures/pyrel_applications/cases/m2-book_is_eligible-extra.population.json` | fail, witness Ada/night | fail, `derived-extension-unsound`, Ada/night | exit 1; acceptance false |
| Temporary copy of shipped complete population with Ada/river removed from both `recommendation` and `book_is_eligible` | pass, four bindings | fail, `derived-extension-incomplete`, Ada/river | exit 1; acceptance false |

These observations support A1 `:9-17` and `:37-41`. The native dispositions remain
future expectations, not observations. They follow the retained requirement to
evaluate `all_eligible` against independently computed pairs. The model's
eligible derivation joins preferred genres and excludes blocked/rated pairs
(`src/gnd/examples/bookrec/complete.orm.yaml:199-235`); `all_eligible` requires
recommendations for its antecedent pairs (`:337-363`).

## Governance and limits

A1 remains proposed until four reviews and the delegated gate (`:3`), sets a
bounded initial/repair review budget, and prohibits production edits or PA0
completion before that gate (`:57-61`). The named auto delegation is recorded
in `001-plan-gate.md:10-16` and the PA0 spec provenance; the parent task explicitly
selected this continuing local review. No inherited delegation from a different
milestone is used. Original plan bytes and original review opinions remain
separate from this amendment opinion.

PA0 must still freeze the joint-omission fixture identity/digest and separate
native expectations as required by A1 `:50-52`. No full corpus census,
implementation review, PyRel execution, rendered tutorial/graphics inspection,
wheel verification or independent authorization-history audit was performed.
The local reproduction does not establish any future native implementation's
correctness or the final denominator. Materially amended bytes need re-review.
