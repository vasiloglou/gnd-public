# Phase LR3 · a labelled reference set and one recorded run · spec r1

## 1. Status

r1, 2026-11-23, written by `process-phase` under `auto=true`. Spec gate in
§12. Started on the coordinator's "GO LR3" (2026-11-23; `main` at
`a0270591` holds PR 241, LH1 and LH2). Built on the LR2 branch (PR 244) with
`origin/main` merged in. Owner rulings that bind it: D3 "sonnet 50$"
([004-ruling-D3.md](../004-ruling-D3.md)) and, asked in this phase, the
credential: "Claude CLI login" (2026-11-23), the producer runs `claude -p`
with the owner's Claude Code login.

## 2. Provenance

[Plan r4](literature-reading-reference-plan.md): Goal (LR3), §0 (R0.2, R0.4,
R0.5), §1 (H12–H18, H24), §2 LR3, §3, §4 (LR3-C1 to C6), §6, §9, D1, D3, D4,
D9. [#226](https://github.com/vasiloglou/gnd-public/issues/226) request 1.
Read at `f1b98682` (LR2 branch with `origin/main` `a0270591` merged):
`src/gnd/examples/literature/reading.py` (caller roots, `run`, `replay`,
`ProducerCall`, `_response`, `_evaluate`), `reading_fixture/README.md`
"Drive it from your host", `corpus/corpus.json`, `answers/answer-key.json`,
`answers/gold/*.population.json`, `model.orm.yaml`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| H12; #226 request 1 | a reference recall and precision on a labelled set, with the stage settings | §6 run and score; T2, T3 |
| H14 | #226's figures as the comparison row | §6 page |
| H15–H17 | drive the stages through LH1's producer protocol; replay as LH2 specifies | §6; T2 |
| H24, D1 (d) | reuse the regression corpus and its answer key with an overlay; `corpus/`, `answers/`, `expected/` keep their bytes | §6 root; T1 |
| D3 | Sonnet, USD 50 ceiling, one recorded run | §6 recorder; the record |
| D4 | participants plus section overlap, predicate agreement beside, section grain stated | §6 scorer; T4 |
| D9 | the record names producer, budget, roster split and stage prompts | §6 run record; T3 |
| R0.2 | a figure names producer, settings and set, and is not a claim about other corpora | §6 page; T5 |
| R0.4 | packaged fixtures unchanged | no existing fixture edited; T1 |
| R0.5 | the gate calls no model | T2 replays; the recorder is a tool outside the gate |
| LR3-C1 | licence per source; gold count per fact type | §6 `labels.json`; T1 |
| LR3-C2 | replay, zero producer calls, figures byte for byte | T2 |
| LR3-C3 | recall and precision per stage with numerator and denominator; producer, budget, roster named | T3 |
| LR3-C4 | a changed gold fact, response or section changes the figure or refuses; one fixture tells found from wrong predicate | T4, T6, T7 |
| LR3-C5 | the page shows figures, rule, R0.2's sentence, #226's figures | T5 |
| LR3-C6 | the reply names what is on `main` and what is not released | `notes/issue-reply.md` |
| coordinator | #245 (empty accepted answers refuse) may land later | §6: the adapter never answers `accepted` with no facts, so the recorded run is the same under either rule |

## 4. Standing rules

- **Totality (1).** The scorer reads a run folder and the root: it reads
  JSON through `gnd.examples.literature.reading`'s bounded readers and
  refuses a row that is not the shape it scores. T8 is the hostile input.
- **Cap (2).** Scoring is linear in rows times gold facts per document (at
  most a few hundred); the recorder is bounded by the roster. No
  time-bound test is owed beyond T8's size cap; argued in the record.
- **Order (3).** Inapplicable: no refusal order is user-visible.
- **N kinds (4).** One scoring walk over all four fact types; no per-type
  branch.
- **One home (5).** The scoring rule's one home is the reference set's
  README; the literature page cites it and shows the figures.
- **Measurement (6).** The figures are a measured run, recorded.
- **General solutions.** Names are compared after one normalization
  (NFC, casefold, whitespace collapsed), applied to every value of every
  type; no name is special-cased. YAML and JSON are read with their loaders.

## 5. Goal

A labelled reference set ships with the literature example, built from the
regression corpus without changing it. One recorded Sonnet run of the
reading stages over it replays with zero producer calls, and its score
gives recall and precision after the broad and the targeted pass. The
literature page shows the figures beside #226's.

## 6. Design

### Reuse

| Capability | Search | Decision |
|---|---|---|
| labelled documents | `components_index.py search "literature corpus"`: `examples.literature_assurance`, the corpus and answer key | reuse the 12 development documents, gold populations and anchored facts |
| run and replay the stages | `reading.run`, `reading.replay` (LH1, LH2) | reuse unchanged |
| bounded JSON reads | `reading._decode`, `read_regular_bounded` | reuse |
| precision and recall counting | `assurance_report.py` reports `(numerator, denominator)` pairs | the same pair shape; the matching rule is LR3's own (D4), because the assurance scorer matches whole claims against passages, not reading attempts |

### The root: `src/gnd/examples/literature/reference_set/`

Built by `reference_set.build_root(out)` from the packaged corpus, committed,
and held equal to a fresh build by T1.

- `<document>.txt`: the 12 development documents, byte-identical to
  `corpus/documents/<document>.md`.
- `corpus.orm.json`: `model.orm.yaml` loaded with the YAML loader and written
  as canonical JSON.
- `roster.json`: one source per document, version `corpus-1`. One section
  per passage, id `<document>-p<n>`: `p1` spans the document's start
  (title and identifier lines) to the end of its first passage and is
  `opening`; every later passage is `targeted`. Spans are UTF-8 byte offsets
  converted from the corpus's code-point spans. One question per targeted
  section (`fact` `method_builds_on_method`, the lineage #226 reads,
  `required: false`), so the targeted pass reads every later passage; no
  question is derived from the gold, so the schedule leaks no answer.
  `revisit_keys: []`.
- `profile.json`: model `corpus.orm.json`, no includes, `producer_label`
  `claude-sonnet-5-5`, `base_facts {}`, review, calibration, conflict and
  absence off.
- `labels.json` (`literature-reference-labels/1`): per gold fact, its
  document, fact type, roles and the sections its anchored roles lie in
  (empty when the answer key anchors none: the seven `work_builds_on_method`
  facts, matched at document grain); the licence note of the corpus (the
  documents are synthetic paraphrases written for the repository); counts per
  fact type.
- `README.md`: the scoring rule's one home, the settings and the figures.

### The scorer: `reference_set.score(run, root)`

Reads the run's `payload-1.json` (broad attempts) and `payload-3.json`
(targeted attempts) and `labels.json`. A produced row is **found** when a
gold fact of its document has the same fact type and the same role values
after normalization, and the section it was read from is one of the gold
fact's sections (or any section of the document when it has none). It is
**wrong predicate** when a gold fact in that scope has the same multiset of
normalized values under another fact type. Each gold fact counts once.
Output `literature-reference-score/1`: for `broad` and `targeted`, the rows
produced, found and wrong-predicate, precision `[found, produced]`; recall
after each pass `[gold facts found so far, gold facts]`; and rows outside
every gold scope.

### The producer and recorder: `tools/record_lr3_reference_run.py`

Outside the package and outside every gate. `ClaudeCliProducer.produce(call)`
runs `claude -p --model claude-sonnet-5-5 --safe-mode --tools ""
--no-session-persistence --output-format json --max-budget-usd 1
--json-schema <schema>`, prompt on stdin, holding the model's fact types and
role names and the section's text. It keeps only rows of covered fact types
with exactly the declared roles and string values; it answers `accepted`
with those rows, else `empty`, never `accepted` with none. It records each
call's `total_cost_usd` and model ids, and refuses a call once the run's
spend would pass USD 50. The run uses `ReadingLimits()` defaults unless the
roster needs more. It writes the run folder to `reference_set/run/` and
`reference_set/run-record.json`: the CLI version, model ids seen, call count,
total cost, the prompt template's SHA-256 and text, the schema, and the
`evidence_sha256` `run()` returned.

### Pages

- `docs/literature/index.md`: a short section "How much does the reading
  find?" with the figures, the scoring rule's link, the set's size, R0.2's
  sentence, and #226's figures (H14) as the comparison row.
- `notes/issue-reply.md`: the final draft (LR3-C6).
- Release-notes bullet.

### Inventories

`tools/gnd_layers.json` gets the new module; the packaged-example and
module inventories the guard block names are updated in the same commit
(said in the PR, as the coordinator asked).

## 7. Decisions, ruled under `auto=true`

| ID | Question | Ruling |
|---|---|---|
| LR3-D1 | D1: (d) or (a) | (d): the corpus's documents read as sectioned sources (§6), with an overlay and no change to its bytes |
| LR3-D2 | the set's size | the 12 development documents, 46 passages, 38 gold facts; the 4 held-out documents stay out (their key is not in the repository) |
| LR3-D3 | precision counts a kept fact outside every gold scope as wrong (plan open question) | yes, as #226 did; reported separately too |
| LR3-D4 | name matching | NFC, casefold, whitespace collapsed; no fuzzy match. A spelling the gold does not use is not found, and the page says so |
| LR3-D5 | the question schedule | one question per targeted section, never from the gold (§6) |

## 8. Tests

`tests/test_lr3_reference_set.py`, default lane.

| # | Case | Expected |
|---|---|---|
| T1 | `build_root` into a temp folder | byte-identical to the committed root's built files; every `<doc>.txt` equals its corpus document; labels count 38 facts by fact type 12/11/8/7 |
| T2 | `reading.replay(run, fixture=root, expected_evidence_sha256=record)` | completes with zero producer calls (no producer is passed); returns the recorded evidence |
| T3 | `score(run, root)` | equals the committed `score.json` byte for byte; names the stages; the run record names producer, model, budget, cost and prompt digest |
| T4 | scorer fixtures | a row with the gold values in the gold section is found; the same values under another fact type is wrong predicate, not found; the same row in another section is not found; a document-grain gold fact is found from any section of its document |
| T5 | the page | shows the figures from `score.json`, links the rule, has R0.2's sentence and #226's figures |
| T6 | a changed gold fact in a copy of `labels.json` | the figure changes |
| T7 | a changed response or a changed source byte in a copy of the run or root | replay refuses |
| T8 | hostile score inputs | a non-JSON or wrong-shape payload refuses with an `ExampleError`, not a traceback |
| T9 | the producer adapter with a fake `claude` | no facts gives `empty`; foreign fact types and roles are dropped; a CLI error or spend past the ceiling raises |

Gate: plan §9's LR3 lane plus this file and `tests/test_documentation_tutorials.py`;
the guard block; `uv run ruff check`; the component-index check.

## 9. Out of scope

Raising the recall; other models; the held-out split; changes to
`reading.py`; a quote concept.

## 10. Size

About 250 source lines (scorer, builder), 200 tool lines, 250 test lines,
40 page lines, and the committed root and run.

## 11. Approval instrument

This prose; the figures are measured, not predicted.

## 12. Spec gate

Delegated approval (`auto=true`), 2026-11-23, under
[001-plan-gate.md](../001-plan-gate.md), with the owner's D3 and credential
rulings above. Budget: one recorded run, USD 50 ceiling; development probes
count against it. No spec review. Compatibility: no existing file's format
changes. The SHA-256 is in the phase record; findings go in §13.
