# Phase CT5: documentation

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.**

`(d1)` **Delegated approval (auto=true)**, 2026-11-04, under the owner's
"Yes, run it auto"; an agent ruling, not the owner's personal reading.
Approved bytes: SHA-256 `f7e93cf13b9894852c39d7212046befd1387d2963cbb58d4801c5fcc6378ba68` (before this tag), after the sweep at
`077a611`: the docs runner takes named groups (`tools/run_tutorials.py`
`groups()`), the grow-a-model page and its figures exist as the pattern, and
48 pages or skill references match the CT5-C1 terms. Rulings: D1, D2 as
proposed. Budget: no paid calls; Fable and one reviewer as local agents.

## Provenance

- Plan: [composition-and-type-induction-plan.md](composition-and-type-induction-plan.md)
  r3, approved `(a1)`: §4 CT5, §5, §9 CT5 row; obligations O5, O12, O14.
- Inputs: the CT1 to CT4 records (`002` to `005`) and their reference pages
  (`anchors.md`, `composition.md`, the discover section, the witness contract).
- Owner preferences on file: business pages are pedagogical and graphical,
  written by Fable, shown at a checkpoint before the work is complete; the
  model-growth DC2 page was rejected as too dry and its Fable rewrite was
  accepted ("Yes, commit it", 2026-11-04).
- Authority: the owner's "Yes, run it auto" (2026-11-04). **This spec's
  bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| CT5-C1 | Dispositions over every page and skill reference naming anchors, sidecars, composition, witnesses, replay or discover, including the witness contract and the `python-api.md` count | `notes/CT5-dispositions.md`; the edits it lists |
| CT5-C2 | Checkpoints DC1 (after plan approval) and DC2 (real runs after CT3 and CT4) | DC1 recorded as missed (the plan gate preceded this session's work); DC2 is the how-to below, shown to the owner before the close |
| CT5-C3 | One how-to: from several documents to one checked answer traced back to each source | `docs/how-to/compose-documents.md` with a runnable example in `src/gnd/examples/composition/` |
| CT5-C4 | One Unreleased release-note entry; docs gates exit 0; one independent docs reviewer | the CT1 to CT4 entries under one heading; gates; reviewer |
| CT-R2, O5 | Anchors bind values to ranges; composition and lineage prove nothing | wording on every new page |

## Design

- **How-to (Fable).** A story in the shape of the accepted grow-a-model page:
  two contracts arrive as two documents; each is extracted with anchors; the
  manifest says that "ACME CORP." in one is "Acme Corp." in the other;
  `gnd compose` builds one population; `gnd check --composition` answers a
  question whose premises come from both (a derived fact type), and a
  conflict between the two contracts is reported with both sources; `gnd
  witness --composition` traces the answer back to a span in each document.
  Figures (SVG, `docs/assets/applications/compose-*.svg`) show the two
  documents, the composition and the trace. Every shown output comes from a
  `gnd-run` block that the docs runner executes (group `compose`). A short
  closing section points to the fact-type family for generic rows.
- **Dispositions.** One table: page, what it says about the changed
  surfaces, disposition (updated, with the edit; or unchanged, with the
  reason).
- **Checkpoint DC2.** The how-to, rendered, is shown to the owner; the copy
  shown is retained under `checkpoints/DC2/`.

## Decisions

| ID | Question | Proposal |
|---|---|---|
| D1 | Who writes the how-to | Fable (owner preference on file) |
| D2 | DC1 | recorded as missed, not back-filled: a plan-time mock-up after the phases are built would be a reconstruction |

## Tests

| # | Case | Expected |
|---|---|---|
| T1 | `uv run python tools/run_tutorials.py --group compose` | exit 0 |
| T2 | `uv run --group docs zensical build --strict`; `uv run python tools/check_docs.py site` | exit 0 |
| T3 | `tests/test_packaged_skills.py`, `tests/test_skill_prose_sync.py`, `tests/test_disclosure_docs.py`, `tests/test_development_scaffold.py`, the example's own test | exit 0 |
| T4 | One independent docs reviewer over the new pages and the dispositions | findings dispositioned |

## Size

One how-to, three figures, one example folder and its test, the dispositions.
