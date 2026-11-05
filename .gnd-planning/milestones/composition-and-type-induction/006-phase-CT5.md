---
milestone: composition-and-type-induction
station: "phase-CT5"
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: phase-CT5
date: 2026-11-04
gate:
  command: "uv run python tools/run_tutorials.py --group compose; uv run pytest -q tests/test_composition_example.py tests/test_development_scaffold.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py; uv run --group docs zensical build --strict; uv run python tools/check_docs.py site"
  exit: 0
  output: "18 tutorial blocks passed; 124 passed, 1 deselected; Build finished; 14288 local links/assets/anchors checked"
  note: >-
    Spec tests T1 to T3, run after the review fixes. The release-note test
    (`-k release_note`) also passes.
slow_cadence:
  command: "uv run python tools/run_tutorials.py"
  trigger: "the close, or an explicit owner request"
  reason: "CT5 adds only the compose group; the other groups' pages are unchanged by CT5"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT5-spec.md
    sha256: 9390e916d39eacc612de7ca9dcae3827958a7f1a9734e5378dedee67a3dab8d7
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/CT5-dispositions.md
    sha256: aa6f3bf70771f0c031c47d9aff0df42ea4d0cc578ae48ad13b9e78557b335a75
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT5-claude-review.md
    sha256: 233711430d2c7b5ed246ea2a7f1e726750db78d26bf107e276bd6dd24287f861
  - path: .gnd-planning/milestones/composition-and-type-induction/checkpoints/DC2/docs/how-to/compose-documents.md
    sha256: 47705a00acc19320e7c91899b8974d2a0c4a4de17ed4f98c42e8d55bfabee448
  - path: docs/how-to/compose-documents.md
    sha256: c82cafca84f7357c51c7d875b938f49c0c863fd63f87e318c660bb3e49013b9d
  - path: docs/assets/applications/compose-composition.svg
    sha256: 589cf12c5a352dab5ac8953d1651c1b8f8ddafd8d6d8d595033aa810830007eb
  - path: docs/assets/applications/compose-documents.svg
    sha256: 25edb7e7689f91f616cdbeba24c4a6ee81074623a6feb40f3a770538d97eb694
  - path: docs/assets/applications/compose-trace.svg
    sha256: 83c0fc8dd4936da163ad586a906d387251475b1ac0e0325541865b1f81772791
  - path: tools/build_composition_example.py
    sha256: 81a5e4451413079de3f7bbb12259d7894667236954938f0498f8e610a79c15b3
  - path: tests/test_composition_example.py
    sha256: 6afa1677addde8acfaee3eb8de2e7e64e9929d9cf4f283bf12aa44087e9cd964
  - path: docs/release-notes.md
    sha256: e0c6c0ab559eed907bc28803139ae27c73a9759cb949ef26b30441ad26237ef4
  - path: docs/reference/anchors.md
    sha256: 399ce6c459734051a9eec30ae25e2dfa2b63c21951159b4999d307bc53faf9a0
  - path: tools/run_tutorials.py
    sha256: 82942094f7440d27bb5c477a548f280c227eb00db184a6b459fedaefcbf2c5a8
---

# Phase CT5: documentation

**Claim.** A how-to, [From several documents to one checked answer](../../../docs/how-to/compose-documents.md),
walks two contracts through extraction with anchors, a manifest renaming,
`gnd compose`, `gnd check --composition --sources` (clean and with a
conflict reported with both sources), `gnd witness --composition` and
`gnd replay --composition`. Every shown output comes from one of its 18
`gnd-run` blocks, which the docs runner executes (group `compose`) over the
packaged example `src/gnd/examples/composition/`. Fifty-one pages and skill
files matching the CT5-C1 terms are dispositioned, 11 updated. The release
note has one Unreleased entry for the milestone. The docs gates exit 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 (digest in the spec); an agent ruling under
the owner's "Yes, run it auto", not the owner's personal reading. The page
was shown to the owner as checkpoint DC2; the owner answered "Yes, finish
it" (2026-11-04).

## What changed

- `docs/how-to/compose-documents.md` (written by Fable, D1) and three
  figures `docs/assets/applications/compose-{documents,composition,trace}.svg`.
- `src/gnd/examples/composition/` (model, targets, a clean and a conflict
  composition directory), built by `tools/build_composition_example.py`,
  which computes every digest and range; `tests/test_composition_example.py`.
- `tools/run_tutorials.py` gains the `compose` group; `zensical.toml` the
  nav entry; the DC2 copy is registered in `tests/test_development_scaffold.py`.
- The 11 updates in [the dispositions](notes/CT5-dispositions.md), plus two
  review corrections outside them: `docs/reference/anchors.md` and the
  release note no longer say `gnd extract` writes anchor sidecars.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| CT5-C1 dispositions | `notes/CT5-dispositions.md`, 51 rows reconciled with the grep | holds after F7 |
| CT5-C2 DC1, DC2 | DC1 missed (D2); DC2 shown and answered; copy retained | holds; DC1 recorded as missed |
| CT5-C3 one how-to | the page; runner group `compose`, 18 blocks | holds |
| CT5-C4 release note, gates, one reviewer | one Unreleased entry; gate above; review below | holds |
| CT-R2, O5 | "What this proves, and what it does not"; anchors bind values to ranges; nothing proves the contracts right | holds; F5 tightened |

**Checkpoint copy.** The DC2 copy keeps the bytes the owner saw. The page
changed after it only by the review fixes below (wording, no new step or
output); the figure edits are F6.

## Review

One local docs reviewer agent, read-only: no blockers, two major findings
([review](notes/phase-CT5-claude-review.md)).

| Finding | Disposition |
|---|---|
| F1 "if any of the three files changes" was false for the model | fixed: the vocabulary digest covers object types, fact types and roles, not constraints, rules or descriptions; the record binds the whole model file |
| F2 the page implied `gnd-extract` writes anchor sidecars | fixed: no `gnd` command writes one; the extractor does, `gnd.anchors.write_anchor_sidecar` publishes one, and the example's builder is linked. The same false sentence was removed from `anchors.md` and the release note |
| F3 "every value is checked" | fixed: "every anchored value" |
| F4 the conflict names only the first missing derived row; "wrong seat in the addendum" took a side | fixed: both missing rows named, the first-row behaviour stated, no side taken |
| F5 closing overclaim | fixed: the person's decisions are stated where anyone can check them |
| F6 figures dropped renaming 1 and merged two manifest entries | fixed in both figures and the alt text; the record box was re-spaced and checked rendered |
| F7 disposition counts | fixed: 51 rows (the schema twin and two word matches added), 11 updated, 40 unchanged |
| F8 `composition.lineage` "keyed by" | fixed: a list, one entry per offending fact |
| F9 unexplained terms | fixed: digest, base node, derived extension and `"replayable": false` explained; the fact-type step says the generic declaration is required |

## Refactoring review

The example is built by one script from declared sources; the test rebuilds
it and compares bytes, so the committed files cannot drift from the
builder. No product code changed in CT5.

## Questions

None opened.

## Boundary

Not merged, released or certified.
