# Phase TS5 spec: documentation and a how-to

## 1. Status

**r1, delegated approval (auto=true) `(d5)` 2026-11-05** (SHA-256 of the r1
bytes before this mark:
`fdc7cb9ed1d9f9dea3069bc9124c08f4341ba8793eec1812a685df49ee340fad`), under the
owner's `process-milestone type-induction-skills auto`; an agent ruling after
the §7 sweep, not an owner reading. D1–D4 ruled as proposed; instrument: this
prose; no spec panel. Budget: no
paid model call; Fable and one reviewer run as local subagents. The how-to is
shown to the owner at a checkpoint (DC-TS5) before the phase is recorded, as
the owner's standing preference asks.

## 2. Provenance

- Plan r1 `(a1)`: completion predicate 6; §3 docs homes; §4 TS5-C1..C4; §5;
  §9 TS5 row; O9.
- Inputs: TS1–TS4 records (`002`–`005`); the two current recordings
  (`evidence/TS3/recording-2/`, `evidence/TS4/recording/`); the fixtures
  `round-two/` and `multi-valued/`.
- Pattern: the accepted CT5 how-to (`docs/how-to/compose-documents.md`),
  its example folder under `src/gnd/examples/`, its tutorial group and its
  dispositions note; the accepted grow-a-model page.
- Owner preferences on file: how-to and business pages are written by
  Fable, are pedagogical and graphical, show `/gnd:` skill prompts and
  recorded replays rather than code where a skill acts, never fabricate a
  replay, explain every failure a replay shows, and are shown at a checkpoint
  before the work is complete.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| TS5-C1 | dispositions over every page and skill naming the fact-type family, shape matches or `multi_valued`, including the CT how-to | `notes/TS5-dispositions.md` and its edits |
| TS5-C2, predicate 6 | a how-to walks one generic fact type through a round after one applied induction, with a distinct attribute, a duplicate and a multi-valued attribute, using both skills; it runs end to end in the tutorial runner with the recorded skill outputs as fixtures, no live model | §5.1; T1 |
| TS5-C3, O9 | `discover.md`'s once-per-generic paragraph and its D5 sentence say what holds by default and what changes under judgement | §5.3; T3 |
| TS5-C4 | docs gates exit 0 | T2 |
| Plan §3 | `docs/reference/type-judgements.md` (new) | refuted premise P6: TS2 put the contract in `discover.md` "Type judgements" (one home, standing rule 5); a second page would copy it. Disposition: no new reference page |
| Plan §3 | release notes, capabilities | dispositions rows |
| §0 TS-R5 | the page shows no value the recorded mode hid | T4 |

## 4. Standing rules

TS-R1: no `src/gnd` module changes (the example is package data). TS-R5:
the how-to runs in unset mode without `--show-values`; any value it shows
comes from a `cat` of the example population the reader holds anyway, never
from the evidence. TS-R6/R4: the page's commands end at `gnd evolve preview`;
applying is named as the reader's reviewed step. TS-R7: no downstream names.
Standing rule 5: the how-to links the `discover.md` contract and the skills,
copying neither the formats nor the decision rules.

## 5. Design

### 5.1 The how-to (Fable)

`docs/how-to/judge-induced-fact-types.md`, in the CT5 and grow-a-model
shape: a short story, then rounds. The example folder
`src/gnd/examples/type_judgements/` holds two rounds of one generic fact
type `item_has_attribute`:

- `duplicates/`: the `round-two` fixture's model and population and the
  TS3 `recording-2` judgements file;
- `multi-valued/`: the `multi-valued` fixture's model and population and
  the TS4 recording's judgements file;
- `README.md`.

The page: copy the example; `gnd discover --type-evidence` (counts shown);
the reader asks Claude Code `/gnd:gnd-judge-fact-types model.orm.yaml
evidence.json`; the recorded question about g3 and the answer, quoted from
`results.json`; the verdict table from the recorded file; `gnd discover
--type-evidence-in --duplicate-judgements` and `gnd evolve preview --policy
additive`, both run; then the same for `/gnd:gnd-model-multivalued` with
its two questions. A section names what the run proves and what it does
not (verdicts are proposals; the free-text check is exact text only; one
recorded model). Figures under `docs/assets/applications/judge-*.svg`.

Why two folders, not one evidence file (refuted premise P5): a single
round with every case would need one evidence file judged by both skills,
which the two recordings do not cover (each binds its own fixture's
evidence), and a third paid run is not authorized. Both folders are round
two of the same generic fact type after one applied induction; the page
says so.

Tutorial group `type-judgements` in `tools/run_tutorials.py`.

### 5.2 Example test

`tests/test_type_judgements_example.py`: each example file is
byte-identical to its fixture or recording source; the page's quoted
replay lines appear in the recording's `results.json`.

### 5.3 `discover.md`

The once-per-generic paragraph: by default, every later group is a shape
match; under a `duplicates` file, a `distinct` group is proposed; the two
skills and the how-to are linked. The D5 sentence: counted and not
proposed by default; proposed as many-to-many under a `shapes` verdict.

### 5.4 Release notes

One entry for the two skills under the existing Unreleased heading.

## 6. Decisions

| ID | Question | Proposal |
|---|---|---|
| D1 | Writer | Fable (owner preference on file) |
| D2 | One or two example rounds (P5) | two folders, both round two of `item_has_attribute`, each with its own recorded file |
| D3 | `type-judgements.md` (P6) | not written; `discover.md` stays the one home |
| D4 | Checkpoint | the rendered how-to published as a private artifact and shown to the owner before the record |

## 7. Tests

| # | Case | Expected |
|---|---|---|
| T1 | `uv run python tools/run_tutorials.py --group type-judgements` | exit 0 |
| T2 | `uv run zensical build --strict`; `uv run python tools/check_docs.py site` | exit 0 |
| T3 | `tests/test_type_judgements_example.py`; `tests/test_packaged_skills.py`, `tests/test_skill_prose_sync.py`, `tests/test_development_scaffold.py`, `tests/test_disclosure_docs.py`, `tests/test_tutorial_output_blocks.py` | exit 0 |
| T4 | no canary of the evidence-hidden kind is printed by an evidence or report block; anonymity and absolute-path scan of the new files | pass |
| T5 | one independent docs reviewer over the page, the example and the dispositions | findings dispositioned |

### Implementability sweep

| Requirement | Met as written? |
|---|---|
| Recorded files bind evidence the page recomputes | Yes: evidence does not depend on `--actor`; the TS3 and TS4 tests recompute it with another actor and match. |
| The runner unsets the disclosure mode | Yes: `run_pages` pops `GND_DISCLOSURE`. |
| Package data reaches the page | Yes: as CT5, `importlib`/`gnd.__file__` copy of `examples/type_judgements`. |
| Predicate 6 as one evidence | Not as written (P5); D2. |
| `type-judgements.md` | Refuted (P6); D3. |

## 8. Out of scope

CLI changes; new recordings; release or publication.
