# Local milestone-close review three

2026-10-13. One authorized local same-model reader. Runtime candidate
`6cff353e7bc25a8e5bab3952cfb9d137611ced45`; documentation candidate `47e9071`.
Opinion below is retained verbatim and bounded to the inspected artifacts.

## Opinion

One medium evidence finding remains before the current claim of complete CS2
closure is justified. I found no additional blocking problem with the opt-in
contract, dated delegated amendment, question sweep, portable corpus baseline
or app-adoption boundary.

**Medium — CS2-C3 lacks a demonstrated compiled-snapshot/walk contrast.** The
plan requires retained transition-only, intermediate-state and frame
counterexamples demonstrating why passing compiled snapshots cannot establish
full-walk correctness. `notes/phase-CS2-spec.md` retains this obligation. The new
`tests/test_compiled_snapshot_obligations.py::test_transition_only_literal_is_not_a_snapshot_obligation`
asserts snapshot exit 0 and no compiled rows, but never runs a walk with that
literal precondition. Selected historical frame/intermediate controls test those
walk mechanisms, but do not pair them with passing activated snapshots.
`003-phase-CS2.md` and `004-milestone-close.md` declare completion without naming
such contrasts. Add bounded public-interface examples pairing a passing
activated snapshot with retained-precondition, intermediate-state and frame
failures, and retain exact test/evidence identities; alternatively explicitly
amend that remaining demonstration scope before declaring it discharged.

## Checks and other conclusions

- Read all three phase records, close record, original plan and its dated close
  amendment, CS2 spec, app regression recipe, corpus narrative/answer key,
  baseline/red log, focused gate summaries and agreement artifact. Inspected
  relevant public regression and historical transition controls statically.
- Verified every SHA-256 entry in `002-phase-CS1.md`, `003-phase-CS2.md` and
  `004-milestone-close.md` against current disk bytes: zero mismatches.
- The baseline/red distinction is honest: the portable red log demonstrates
  missing activation through `TypeError`; default and walk controls pass. The
  external temporary baseline declares its reproducibility limit rather than
  claiming all diagnostic bytes are retained in history.
- The observable-field amendment is a reasonable delegated repair: public
  batch rows expose counts, exits and failing references. The 2/2 artifact
  scopes its claim to those fields and does not imply agreement for every
  passing/warning row. Excluded-entry inventory should remain explicitly tied
  to the corpus and trace when close evidence is finalized.
- The recipe names runtime/docs candidates, expected nonnumeric/numeric exits,
  the qualified missing failure and app-owner adoption at the eventual merged
  identity. It does not assert external M3 acceptance or merge authority.

## Scope limits

No production writes, paid/provider calls or test execution. Hash checks and
static inspection do not establish a fresh runtime gate. I did not inspect all
historical carryover artifacts or certify their original claims. This opinion
does not establish full repository, distribution, Ubuntu, downstream M3 or
full-walk acceptance. Four same-model readings are not independent proof.

## Final follow-up — finding discharged

2026-10-13. Inspected `tests/test_compiled_snapshot_boundaries.py` and the
supplementary completion section of the updated close record. Its three public
API cases now assert activated snapshot band 0 against walk band 1 and inspect
the specific retained-precondition, touched-relation frame or intermediate
failure family. The frame case checks both pre/post snapshots; the intermediate
case uses the same passing endpoint before and after the two-step walk. These
are discriminating contrasts matching the original medium finding, which is
discharged.

Inspected retained final gate streams: 218 passed in 26.96s on Python 3.11 and
218 passed in 25.89s on Python 3.13. I did not rerun them. The retained full trace
names 23 compiled entries and the excluded `start.pre_concept_exists` entry with
its multiple-asserter reason. Verified all 10 updated close artifact SHA-256
entries against disk: zero mismatches.

No remaining blocking or medium finding within this reader's bounded closure
scope. Original opinion remains above as history. No production write,
provider run, broader gate or claim of external acceptance accompanies this
follow-up.
