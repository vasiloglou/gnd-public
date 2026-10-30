# Phase WN3 -- the repair loop, end to end

## 1. Status

**Draft r1.** Prepared under `/process-milestone derivation-why-not auto`. The
gate is a delegated approval (auto=true), recorded in the appended section
below. Implementable once WN2 is committed, because it uses `gnd why-not` and
`api.why_not`.

## 2. Provenance

- Derived from the approved [plan r3](derivation-why-not-plan.md) §4 WN3
  (C1-C4), §3 (the example home is named here), §5 and §9, and the WN2 record.
- Issue #66's motivating loop: a host asks why a claimed row is not derived,
  adds the missing fact, and asks again until the row derives and a witness
  proves it.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| WN3-C1 | a packaged example with a claim rule over quoted facts and two missing base facts; in the installed-docs example list | §6.1; T1 |
| WN3-C2, O7 | a committed test walks the loop in row mode, with negative controls | §6.2; T2 |
| WN3-C3, O13 | a how-to page | §6.3; T3 |
| WN3-C4 | a route sentence in one packaged skill | §6.4; T4 |

## 4. Rules bound to WN3

- **WN-R1.** No change to `check`, `witness` or the why-not contract. The
  example is data, and the test drives only the public API.
- **WN-R8.** T17 covers every added file.
- **Standing rule 6 (measure).** Every claim in the how-to is a `gnd-run` block
  whose output is asserted.

## 5. Goal

A host that holds only a model, a population and one claimed row can reach a
witnessed derivation using nothing but why-not's payload, plus a table of the
values a document would supply for roles no binding reaches.

## 6. Design

### 6.1 The example (`src/gnd/examples/quoted_claims/`)

A certified-answer model. An answer claims that a person said a quotation, and
the claim is certified when the record backs it.

- `quote(quote, work)`: the quotation appears in the work. Base.
- `authored(work, person)`: the person wrote the work. Base.
- `reviewed(work, reviewer)`: an editor reviewed the work. Base.
- `certified(quote, person)`: derived, `body: [quote(q, w), authored(w, p),
  reviewed(w, r)]`, `head: {quote: q, person: p}`.

Files: `model.orm.json`, `gap.pop.json` (quotes for two works, no
`authored` and no `reviewed` rows), `claim.json` (the witness request for
`certified(q-17, Ada Byrne)`), `extracted.json` (the reviewer a source
document names, keyed by role), and `README.md`.

Gap 1 is `authored` at body index 1. Its `work` role is bound from the sample
and its `person` role from the claimed row, so it is ground. Gap 2 is
`reviewed` at body index 2. Its `work` role is bound from the sample, and its
`reviewer` role is free, so the extracted table supplies it.

`tools/check_installed_docs.py` adds `quoted_claims` to the example domains.

### 6.2 The loop test (`tests/test_why_not_repair_loop.py`)

1. Before repair, `api.check` over `gap.pop.json` reports `certified` with
   verdict `pass` and no rows. The population covers `certified` and asserts
   none, so the computed extension equals the asserted (empty) one. This is
   the exact variant WN3-C2 asks the spec to name.
2. `api.why_not(..., row_path=claim.json)` exits 0, `blocked`, and the blocker
   is `(atom, 1, authored)`. The test builds the fact from the payload alone:
   `fact_type`, the role map, and the raw sample. For each role it uses the
   sample's value when the role is bound, else the extracted table's value. It
   asserts the extracted table's roles and the blocker's bound roles are
   disjoint.
3. Negative controls, each from the gap population:
   - the same values written onto the previous step's predicate (`quote`,
     positionally);
   - the right predicate with a wrong bound value (`authored(w-other, …)`).

   Both leave `certified(q-17, Ada Byrne)` underived, and the blocker's
   `(kind, index, fact_type)` unchanged.
4. After repair 1, why-not names `(atom, 2, reviewed)`, with `reviewer` free.
   The reviewer comes from the extracted table.
5. After repair 2, why-not exits 0 `derived`.
6. `api.witness` then exits 0 for the row, and `api.replay` replays it.

### 6.3 How-to (`docs/how-to/repair-a-missing-claim.md`)

The page follows the existing how-to shape: a "Files on GitHub" box, a setup
block that copies the example, then `gnd why-not` runs with their redacted and
`--raw` outputs. It shows the two repairs and closes with `gnd witness`. Every
command is a `gnd-run sh` block with asserted output. It is listed under
How-to guides in `zensical.toml`. A test adds the page to the tutorial runner's
groups, as the other how-to pages are, if the runner needs a group.

### 6.4 Skill route (WN3-C4)

`gnd-export` owns the witness workflow, so it gets one route sentence after its
witness step: when a request's status is `missing`, `gnd why-not MODEL POP
--fact-type ID --row REQUEST` names the first step that left no bindings. The
sentence names the command only and links nothing outside the skill, because
packaged skills ship without the docs tree. `gnd-dev-session` is unchanged. No
packaged `gnd-induce` skill exists at this baseline.

## 7. Decisions

| ID | Question | Proposal |
|---|---|---|
| WN3-D1 | Example name | `quoted_claims` |
| WN3-D2 | Which skill routes | `gnd-export`, one sentence |

## 8. Tests

| ID | Check |
|---|---|
| T1 | the example validates; `tools/check_installed_docs.py` lists it (the existing installed-docs unit test exercises the list) |
| T2 | §6.2 in full |
| T3 | `tools/run_tutorials.py` runs the how-to's blocks; the docs site builds and `tools/check_docs.py` finds no broken link |
| T4 | the skill sentence is present; the skill-sync and packaged-skill tests pass |

Focused gate: the WN2 gate, plus `tests/test_why_not_repair_loop.py`, the
how-to's tutorial group, the skill tests, and the docs build with
`tools/check_docs.py`.

## 9. Out of scope

Any change to why-not's semantics or payload, and a business-facing tutorial.

## 10. Size

An example of about five small files, one test of about 150 lines, a how-to
page, and one skill sentence.

## 11. Approval instrument

Delegated approval (auto=true). One local reviewer over the phase diff
(WN-D8).

## WN3 gate -- delegated approval (auto=true), 2026-10-30

- **Authority:** the owner's `/process-milestone derivation-why-not auto`
  request in this session; a delegated approval, not the owner's own reading.
- **Bytes approved:** spec r1 above this section, SHA-256 `df9e334204d778f0ebcdeec555298474a38be78eeb5ca25de4cb678e7c33ede5`.
- **Base:** WN2 commit `b1d017d`.
- **Decisions:** WN3-D1 (`quoted_claims`) and WN3-D2 (`gnd-export`) as
  proposed.
- **Instrument:** one local reviewer over the phase diff (WN-D8). No paid calls.

Implementability sweep, against the example written by
`evidence/WN3/build_example.py`:

- **S1.** The model validates. A population `source` must be `agent-output`,
  `synthetic` or `fixture`; the example uses `fixture`.
- **S2.** `gnd why-not ... --row claim.json --raw` exits 0 `blocked` at
  `(atom, 1, authored)`, ground, `descent_stopped: not-derived`. Its sample is
  `{work: Field Notes, person: Ada Byrne}`: `work` comes from the sample, so
  gap 1 meets WN3-C2's bound-from-sample condition.
- **S3.** `check` exits 0 over `gap.pop.json` and reports `certified` with a
  `pass` verdict; `witness` reports the row `missing`. That is the
  "pass with the row absent" variant §6.2 step 1 names.
