# Literature reading reference · plan r4

**Status: r4, 2026-11-23. Approved under delegation (`auto=true`) in
[001-plan-gate.md](../001-plan-gate.md).** r4 applies the second and final
panel round's five fixes, listed in §12, as amendments ruled at the gate.
r3 was the revision after the first panel round. r2 was the full plan `start-milestone` wrote from outline r1
(2026-11-22, merged in PR 229). The owner delegated `auto=true` for this
milestone on 2026-11-23 and selected the full GND panel for plan and close
review (D6). The first round read r2
([r2 panel](../../../reviews/literature-reading-reference-r2-panel/README.md));
r3 applies its seven fixes, listed in §11. Approval is recorded only in a
plan-gate record, which does not exist yet.

This plan covers one open issue,
[#226](https://github.com/vasiloglou/gnd-public/issues/226): a host reading
scientific papers with GND's literature stages measured about 30 % recall for
every model it tried and has no reference point to tell its own loss from the
method's.

**Provenance.** Phase IDs LR1–LR3 and decisions D1–D5 are the outline's. r2
adds criteria IDs, obligations H1–H22 and decisions D6–D9. The outline left
two rows "not read". Both are read now, and both change the plan `(r2)`:

- **LR1.** `gnd verify --format json` already lists every failing constraint
  with its rows (H2). What is missing is a page that says so, the rows in the
  text output, and the constraint's declared id (H3, H4).
- **LR2.** The reading example has no quote and refuses none (H8). The 44
  claims #226 lost to "quote outside the shown section" were dropped by the
  reporter's own host. GND's one binding of a quote to text is the anchor
  check, against the whole document a sidecar names (H10).

r3 adds H23–H25 and re-ran H2–H4 and H22 at `11a7ebf7` `(r3)`. Code
citations were read at `548b9a1d` (`main`, 2026-11-23). `main` moved to
`78934ee3` the same day (PR 234, PR 236, PR 237) while this plan was written;
those merges changed planning files and six skill scripts that dev-tools
delivers, and nothing under `src`, `tests` or `docs`. H17 and §3 are brought
up to them `(m)`. Rows marked
"agent" were read by the read-only harvest agent of this session and not all
re-read by the author; the rows the plan rests on (H2, H3, H4, H8, H9, H10,
H13) were re-read or run by the author.

## Goal and completion predicates

A host that reads papers with GND's literature stages can tell whether a low
recall is its own loss or the method's, can see why a source fails
verification, and knows where a quote may come from.

- **LR1.** For a source that `gnd verify` fails, a host lists the constraints
  that failed and the rows that violate each, from one documented place. A
  test holds the documented steps on a packaged failing source.
- **LR2.** The pages state one rule for where a quoted span may lie: inside
  the document the anchor sidecar names, by digest. They say what that means
  for a host that shows the model one section at a time, and a test holds
  both sides of the rule.
- **LR3.** A labelled set ships with the literature example. A recorded run
  of the reading stages over it reports recall and precision per stage
  setting, names the producer and settings, and replays with zero producer
  calls.

The milestone is closed when each phase has its record and the close record
cites green focused gates for LR1–LR3, the structure and inventory guards,
`uv run ruff check` `(r3)`, the component-index check, a drafted
reply to #226, and a close review on the instrument D6 selects.

## 0. Binding design rules

- **R0.1 Formats stay.** The anchor sidecar and the default `gnd verify`
  payload and text keep their fields and bytes; #226 says they work as they
  are. Anything LR1 adds is opt-in or a page (D7).
- **R0.2 A reference figure is a measurement of one run.** It names the
  producer, the settings and the labelled set. It is not a claim about other
  corpora or models, and the page says so beside every figure.
- **R0.3 No fidelity rate in the `verify` payload.** `gnd verify` keeps
  saying that checker acceptance is not proof of faithfulness
  (`src/gnd/skills/gnd-extract/references/extraction-contract.md:152`); the reference figures live in the
  example's own record.
- **R0.4 Fixture bytes stay.** The packaged reading run, its pinned producer
  table and its recorded outputs are byte-identical after LR1 and LR2. LR3
  adds a second fixture beside them and changes none.
- **R0.5 The gate calls no model.** A live run happens once, under the
  owner's explicit selection of a producer and a budget (D3). Every gate
  replays recorded responses.
- **R0.6 One home per rule.** How to read a failed verification has one
  home (D8); the quote rule lives in `docs/reference/anchors.md`; the
  literature pages cite both.

The project's six standing rules
(`.codex/skills/process-phase/references/project.md`) and the rule "General
solutions, not pattern-matched ones" (`AGENTS.md`) bind every phase; each
spec discharges them by name.

## 1. Scope, sources and authority

Harvested obligations. "Observed" means read or run by the author at
`548b9a1d` on 2026-11-23; "agent" means read by the harvest agent;
"inherited" means claimed by a source and not re-measured.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | #226 request 3 | "A way to see why `verify` reports `alethic-failure` per source: which constraint, on which rows." The reporter saw it on all 20 sources (3,729 rows, 280 of them unanchored) | inherited | LR1 |
| H2 | probe `(r3)`: run `python -m gnd.examples.literature.reading run --out RUN`, copy `reading_fixture/reading.orm.json` and its include `depth_fixture/vocabulary.orm.json` into `RUN`, then `gnd verify RUN/reading.orm.json RUN/reported-conflict.population.json --no-extraction --format json`. The include resolves beside the model file, so the vocabulary must sit there; `reading_fixture/` alone does not hold it | exit 1, `outcome: "violated"`, `schema_version: 7`, `counts.fail: 1`. The one failing verdict carries `constraint_ref` (`fact_types[subject_label].constraints[0]`), `constraint_type` (`uniqueness`), `modality` (`alethic`), `source`, `status`, a `message` that verbalizes the constraint with the violating value, and `offending_facts`, the two violating rows in full. Each verdict also carries `verdict` (`fail`) and `reason_code`; the report itself carries `outcome` and `counts` `(r3)` | observed (re-run at `11a7ebf7`) | LR1 |
| H3 | the same probe, text output | one line under `BLOCKING (alethic)`: `[fail] <constraint_ref>: <message>`. The rows are not printed; the value appears only inside the message | observed | LR1 |
| H4 | the same probe; `commands/checking.py:904` | the constraint's declared id (`subject_has_one_label`) is not in the payload. `gnd verify --rule-ids` is refused ("unrecognized arguments"); the flag exists on `gnd check` only | observed | LR1 (D7) |
| H5 | `redaction.py:616-633` | when a model's redaction policy selects a verdict's roles, `message` becomes a fixed marker and `offending_facts` one marker row. A host of such a model sees which constraint failed and not the rows | observed by reading | LR1 |
| H6 | `docs/guides/documents.md:62-72`; `src/gnd/skills/gnd-extract/references/extraction-contract.md:136-148` | the pages say "Read the `extraction` block and the semantic verdicts independently" and "REPORT IT" for exit 1. No page shows how to list the failing constraints and their rows from a verify report. `offending_facts` is shown on the expense and book tutorial pages, for the Python `check` call, and on no verify page | observed | LR1 |
| H7 | #226 request 2; "What we measured" | 82 claims dropped host-side: 44 quoted text outside the shown section, 38 used a participant or predicate not in the quote. "Nearly half of our drops were quotes from elsewhere in the paper, and many looked correct" | inherited | LR2 |
| H8 | `src/gnd/examples/literature/reading.py:176-193` | a producer response is `{outcome, facts, proposal_keys}`. There is no quote in it and no check of one. Each attempt records the shown section's span and `excerpt_sha256`, which binds the attempt to the section, not a claim to a quote | observed | LR2 |
| H9 | `src/gnd/examples/literature/reading.py:258-286`, `:390-395` | the example verifies two kinds of document. For the broad and targeted passes it is the attempted sections of one pass joined with newlines, not the declared source and not one shown section; for the reported conflict it is `conflict.txt` `(r4)`. Each verify writes an extraction sidecar that binds its document by digest, and no anchor sidecar, so the example is not a model for anchoring `(r3, r4)` | observed | LR2 |
| H10 | `anchors.py:238-271`; `docs/reference/anchors.md:41-45` | `bind_anchors` requires the sidecar's `document_sha256` to equal the digest of the document bytes, and each anchor's span to lie inside that document with a matching `excerpt_sha256`; otherwise `anchor:binding-mismatch`. `block_id` and `unit_id` are free labels. So a quote is bound to a document version, never to a section | observed | LR2 |
| H11 | `src/gnd/examples/literature/reading.py:93-112` | a roster section is `source`, `kind`, `span` (byte offsets, increasing per source) and `selection` (`opening` or `targeted`); an unavailable section has no span and a reason | observed | LR2, LR3 |
| H12 | #226 request 1 | "A reference recall (and precision) for the literature-reading stages on a labelled set, with the stage settings that produced it" | inherited | LR3 |
| H13 | `src/gnd/examples/literature/reading.py:42`, `:311-341`; `docs/literature/index.md:309-313` | the example's only recall figure is fidelity recall over two fact types (`CALIBRATION_FACTS`), 2 of 2 and 1 of 2, used to qualify one scoped absence. No precision is measured | observed | LR3 |
| H14 | #226 "What we measured" | on 20 papers and about 100 gold claims: broad pass best recall 29 of 101 with precision 15 to 38 %; targeted pass best recall 30 of 100 with precision 10 to 20 %; 233 kept claims outside the gold passages; 3 of 29 aligned claims agree on the predicate | inherited | LR3 (comparison rows) |
| H15 | `src/gnd/examples/literature/reading.py:149-158`, `:562-584` | the producer is duck-typed (`produce(stage, section)`); `run()` wires the saved producer; `replay()` re-derives from the retained table with zero producer calls and requires byte identity, for the packaged fixture only | observed | LR3 |
| H16 | `src/gnd/examples/literature/reading.py:587-596` | a run's settings are `--budget-bytes` and `--scenario`; broad against targeted is fixed per section in the roster. There is no other stage setting to report | observed | LR3 (D9) |
| H17 | [literature-host-interfaces](../../literature-host-interfaces/README.md) plan r6, approved by the owner on 2026-11-23 (PR 237) `(m)` | LH1: a public producer protocol in the reading example, a caller's producer driving the six stages over a caller's root. LH2: `replay()` of a live run from its own folder with zero producer calls, its settings read from the run. LH1 has a draft spec waiting for its owner gate; nothing is implemented | observed by reading | LR3 needs both |
| H18 | literature-depth close, `016-milestone-close.md:162` | "Host-scale reading and extraction: carry to the existing literature-identity follow-up for a separately selected corpus and provider budget" | observed by reading | LR3 (D1) |
| H19 | #226 "Not requested" | "Changes to the anchor or verify formats. Those work for us as they are" | inherited | R0.1 |
| H20 | `tests/test_verify_cli.py:309-336`, `:387` | exit 1 with `outcome: "violated"` and a deontic-only violation at exit 0 are pinned; every verify exit path validates against `report.schema.json`. No test lists failing constraints with their rows for `gnd verify` | agent | LR1 |
| H21 | `docs/literature/index.md`, `docs/literature/commands.md`; `src/gnd/examples/literature/README.md` | the literature pages. `index.md:11` says "GND keeps each claim tied to its passage"; none states where a quote may lie | agent, in part observed | LR2 |
| H22 `(r3)` | `project.md`, "Test and gate commands"; dev-tools re-sync `a29562a` | whole-repository `uv run ruff check` exits 0 at `11a7ebf7` and is the lint gate `project.md` names. r2's wording, retired: "whole-repository `uv run ruff check` exits 1 on files dev-tools delivers; `uv run ruff check src tests tools` exits 0, and is this plan's lint gate" | observed (re-run 2026-11-23 at `11a7ebf7`) | all |
| H23 `(r3)` | `src/gnd/checker/_reports.py:113-116`; `src/gnd/output.py:365` | exit 1 also follows from a failing derivation verdict. Derivation verdicts travel in a separate `derivations` array, rendered under `DERIVATIONS (alethic)` | observed by reading | LR1 |
| H24 `(r3)` | `src/gnd/examples/literature/README.md`; `src/gnd/examples/literature/assurance_report.py:490-531` | the package already ships a labelled literature regression corpus (synthetic paraphrases of public works; answer key `literature-answer-key/1` with passage, participants and predicate) and a staged scorer that reports precision and recall against it per stage (`source-binding`, `semantic-support`, and others) | observed | LR3 (D1, D4) |
| H25 `(r3)` | `tests/test_packaged_skills.py:101-125` | a relative link from a packaged skill file must resolve inside the packaged skills tree, so a skill page cites a `docs/` page by absolute URL | observed by reading | LR1 (D8) |

Component index (`dev/components/`), searched 2026-11-23:

| Capability | Search | Found |
|---|---|---|
| verify a population | `search "verify population"` | `cli.verify_command`, `export.verification` |
| the reading example | `search "literature reading"` | `examples.literature_reading` (`reading.py`), `examples.literature_assurance` |
| bind a quote to text | `search "anchor quote"` | no component of its own; `src/gnd/anchors.py` is found by `git grep bind_anchors` |
| score a reading against labels | `search "literature reading"` | `assurance_report.py`: `score_reading_coverage` scores coverage; `_semantic` and `_source_binding` score precision and recall against the regression corpus's answer key (H24). r2's "scores coverage, not recall against gold" was wrong `(r3)` |

`components_index.py review` lists 276 leads in 10 groups; an index review
is offered to the owner and is not a prerequisite.

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #226: a way to see why `verify` fails a source, by constraint and row | LR1 |
| #226: guidance on whether a claim's quote must lie inside the shown section | LR2 |
| #226: a reference recall and precision on a labelled set, with the settings | LR3 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it does not measure a reader's recall or
say what a report page explains, so none is read here. The baseline is rows
H2, H3, H13 and H14.

## 2. Contract proposal and product behavior

### LR1 — why a source fails verification

- One page section, "Reading a failed verification" (home: D8), gives the
  steps: run `gnd verify … --format json` with the model's includes beside
  it (H2), and with `--unredacted` or `GND_DISCLOSURE=internal` where the
  disclosure policy allows the rows, citing `docs/reference/disclosure.md`
  for that rule `(r4)`; the failing constraints are the `verdicts` with
  `verdict: "fail"` and `modality: "alethic"`, and the failing derivations
  are the `derivations` with `verdict: "fail"` (H23) `(r3)`; each names its
  constraint by `constraint_ref` and `constraint_type`, says what it
  requires in `message`, and lists the violating rows in
  `offending_facts`. A failing derivation names itself by `derivation_ref`
  and lists its `findings` `(r3)`. It says what a deontic violation is (a
  `warning`, exit unchanged) and what a redacting model hides (H5).
- A test runs those steps on the reading example's reported conflict, on a
  passing source, on a deontic-only violation, on a redacting model and on
  a derivation failure, and fails if the page names a field the report does
  not carry. The last three fixtures are authored in the test `(r3)`.
- Proposed under D7 (a): nothing in `gnd verify` changes. The alternatives,
  printing the rows in text and accepting `--rule-ids`, are the owner's.
- Details are in the [LR1 draft spec](phase-LR1-spec.md).

### LR2 — where a quote may lie

Proposed under D2 (b):

- `docs/reference/anchors.md` states the rule in one sentence: a span is
  bound to the document whose digest the sidecar names, and may lie anywhere
  in it. GND has no notion of the section a model was shown.
- The literature pages say what follows for a host. If the host verifies
  against the whole source version, a correct quote from another section
  binds, and the section it was shown in can be recorded in `block_id`. If
  the host verifies against the shown section only, a quote from elsewhere
  cannot bind. Which document a host names is the host's choice, and the
  pages recommend the whole source version.
- The packaged reading example is neither case: it verifies the attempted
  sections of one pass joined with newlines, or `conflict.txt` for the
  reported conflict, and writes no anchor sidecar (H9) `(r4)`. Its README says so and says it is not a model for anchoring `(r3)`.
  r2 said the example verifies "against the shown section only", which was
  wrong.
- `docs/literature/index.md:11` ("GND keeps each claim tied to its
  passage") is rewritten to cite the anchor rule `(r3)`.
- A test pins both sides with one source and one quote from its second
  section: bound when the sidecar and the document are the whole source;
  refused with `anchor:binding-mismatch: source span or excerpt differs`
  when the sidecar's `document_sha256` names the first section and the
  document is that section, so the span rule refuses and not the digest
  check `(r3)`. The same test reads the pages for the rule's one statement
  and the citations.
- The reading example's code and fixture do not change (R0.4).

### LR3 — a labelled reference set and one recorded run

- A labelled set the example reads: either the packaged regression corpus
  and its answer key (H24), with an overlay beside it where the reading
  stages need sections and no change to its bytes, or a second fixture
  beside `reading_fixture/` (D1) `(r3, r4)`.
- One live run over it through the producer protocol of LH1, recorded and
  replayed as LH2 specifies (D3). The record gives recall and precision per
  stage (broad, targeted) under the scoring rule of D4, and names the
  producer, the budget and the roster.
- The literature page shows the figures beside the scoring rule, the set's
  size and the sentence of R0.2, with #226's own figures (H14) as the row a
  host compares against.

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| LR1 | D7 and D8 ruled, or the plan gate accepting their proposals | the home D8 names (proposed `docs/guides/documents.md`), `src/gnd/skills/gnd-extract/references/extraction-contract.md` (one citing line, absolute URL, H25), `docs/literature/commands.md` (one citing line), a new `tests/test_lr1_verify_failure_listing.py`, `docs/release-notes.md` |
| LR2 | D2 ruled | `docs/reference/anchors.md`, `docs/literature/index.md`, `docs/literature/commands.md`, `src/gnd/examples/literature/README.md`, a new `tests/test_lr2_quote_scope.py`, `docs/release-notes.md`, the interim draft in `notes/issue-reply.md` `(r4)` |
| LR3 | LH1 and LH2 of literature-host-interfaces implemented and merged; D1, D3, D4 and D9 ruled | a new fixture folder under `src/gnd/examples/literature/` or the regression corpus (D1), `reading.py` only if LH1 leaves a scoring hook or a settings field to add (D9) `(r3)`, the literature pages, a new `tests/test_lr3_reference_set.py`, the packaged-example inventories the guards name, `notes/issue-reply.md` |

Order: LR1 and LR2 in either order, LR3 last. The graph is acyclic. LR1 is
the first ready phase: it needs no other milestone. LR3 is an outline until
the code of LH1 and LH2 is on `main` and its rulings exist.

Other writers. literature-host-interfaces changes
`src/gnd/examples/literature/reading.py` and the literature pages. One
writer at a time on `reading.py`: LR1 and LR2 do not touch it, and LR3
starts after LH2 merges. LR1 and LR2 change `docs/literature/commands.md`,
and LR2 `index.md`, by a few lines `(r3)`; the second branch to merge rebases. Start
condition: `main` at `78934ee3` or later.

Fixtures. LR1 uses the packaged reading run's reported conflict
(`reported-conflict.population.json`, which the example already verifies at
exit 1) and its broad population (exit 0), staged with the model and its
included vocabulary as H2 says. It authors in the test a deontic-only
violation (the case of `tests/test_verify_cli.py:309`), a redacting copy of
the included vocabulary with `redact: true` on `subject_label` and the
include re-pinned, and a derivation failure `(r3)`. The test runs with
`GND_DISCLOSURE` unset, and the redacting case once under `internal`
`(r4)`. LR2 authors one two-section
source and its sidecars in the test. LR3's fixture is its own deliverable.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| LR1 | **LR1-C1** on the reported conflict, the documented steps give exactly one failing constraint, `fact_types[subject_label].constraints[0]`, kind `uniqueness`, with its two rows. **LR1-C2** on the broad population they give none, exit 0. **LR1-C3** every field name the page's section uses, at report, constraint-verdict or derivation-verdict level, is a property of that level's definition in `report.schema.json` and a key of the live report at that level (derivation names from the derivation fixture); the names are a listed set in the test, each checked to occur in the section `(r4)`. **LR1-C4** a deontic-only violation is listed as a warning and not as a failure; a redacting model gives the marker and the page says so. **LR1-C5** the default `gnd verify` text and JSON for both sources are byte-identical before and after the phase (R0.1). **LR1-C6** `(r3)` every exit-1 fixture gives a non-empty listing, including a derivation failure | none |
| LR2 | **LR2-C1** the rule is stated once, in `anchors.md`, and the literature pages cite it. **LR2-C2** a quote from a source's second section binds when the sidecar names the whole source. **LR2-C3** the same quote is refused with `anchor:binding-mismatch: source span or excerpt differs` when the sidecar's document is the first section alone `(r3)`. **LR2-C4** the packaged reading run replays byte-identical (R0.4). **LR2-C5** `(r3, r4)` the example's README says its verify documents are the joined attempted sections and, for the reported conflict, `conflict.txt`, each bound by an extraction sidecar and none by an anchor sidecar, and `index.md:11` cites the rule; the test reads both | none |
| LR3 | **LR3-C1** the labelled set ships with a licence per source and a count of gold facts per fact type. **LR3-C2** replay of the recorded run makes zero producer calls and reproduces the figures byte for byte. **LR3-C3** the record gives recall and precision per stage, with numerator and denominator, and names the producer, budget and roster. **LR3-C4** a changed gold fact, a changed response and a changed section each change the figure or refuse; the scoring rule has one fixture that tells "found" from "found with the wrong predicate". **LR3-C5** the page shows the figures, the scoring rule and R0.2's sentence, beside #226's figures. **LR3-C6** the reply to #226 is drafted and names what is on `main` and what is not released | H18 |

Each phase also runs the structure and inventory guards,
`uv run ruff check` `(r3)`, an independent review of its diff that
carries the pattern-matched-solutions claim of `project.md`, a refactoring
review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each (R0.6).** The verification steps live in the home D8
  names; `extraction-contract.md` §5 and the literature commands page cite
  it. The quote rule lives in `docs/reference/anchors.md`.
- **Packaged skills.** `gnd-extract`'s `extraction-contract.md` gains one
  citing line, an absolute URL to the docs home (H25) `(r3)`; its manifest is held by `tests/test_packaged_skills.py`, in
  the guard block.
- **Release notes.** One entry per phase under the unreleased heading.
- **Compatibility.** LR1 and LR2 change pages and tests only, under D7 (a)
  and D2 (b). D7 (c) would add an opt-in flag and keeps the default bytes.
  D7 (b) as written changes the default text, so ruling it would amend R0.1
  and LR1-C5 at the same gate `(r3)`. r2 said "the default bytes stay either
  way", which was wrong for (b). LR3 adds a
  fixture and changes none.
- **Issue reply.** `(r4)` An interim draft covering requests 3 and 2 is
  written in LR2 and updated when LR2 merges; the close writes the final
  draft with LR3's figures. The owner posts both.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| The page describes fields the report does not carry, or stops matching it | LR1-C3: the test reads the page's field names and checks each against the schema and a live report |
| The documented steps are fitted to one fixture | LR1-C1, C2 and C4 cover a failure, a pass, a deontic warning and a redacted verdict; the diff review's pattern-matched claim |
| A host reads "anywhere in the document" as "any text is evidence" | LR2 states the two things an anchor does prove (the span is in that document version and the excerpt matches) and that neither proves the claim is supported |
| A reference figure is read as a product claim | R0.2, with the set, producer and settings beside every figure (LR3-C5) |
| The labelled set carries text that cannot be redistributed | D1 (a), with the licence of each source recorded in the set (LR3-C1) |
| A live run needs a provider credential | R0.5: made once under the owner's explicit selection; the gate replays it. No repository `.env` is read |
| The scoring rule cannot tell a right claim from a near miss | LR3-C4's discriminating fixture; D4 reports predicate agreement beside span overlap |
| LR3 starts before the producer protocol is settled and is rewritten | LR3 waits for LH1 and LH2 on `main` (§3) |

## 7. Out of scope

- Raising the recall itself. LR3 gives the figure a host compares against;
  a method change follows from what it shows.
- A change to the anchor format or to the default verify payload and text
  (R0.1).
- A quote or claim concept in the reading example. It has none today (H8)
  and LR2 documents the anchor rule without adding one.
- The 38 claims #226 dropped for a participant or predicate not in the
  quote: that is the reporter's host rule. LR2's page says which of the two
  drop reasons GND's anchor check corresponds to.
- A summary of failures across many sources in one command; a host loops
  over its sources with the steps of LR1.
- The run over a separately selected corpus that literature-depth carried
  (H18), unless D1 is ruled (b).
- The producer protocol and live-run replay themselves
  (literature-host-interfaces, #215 and #216).
- Release, tag and publication.

## 8. Execution, approval and review protocol

- `auto=true` `(r3)`: the owner delegated approval for this milestone on
  2026-11-23 ("they should both start with /process-milestone auto"). The
  plan gate, each spec gate and the close are ruled under that delegation
  and recorded as delegated rulings. It authorizes no paid producer call,
  no credential, no publication and no merge.
- Plan review and close review: the full GND panel (D6, the owner's ruling).
  Round one read r2 and blocked (Codex). The budget is two rounds; round two
  reads r3. Stop criterion, declared here before round two: after round two
  the plan is ruled on its findings with no third round; a blocking finding
  that survives reproduction is fixed and recorded at the gate.
- Phase-diff review: one independent reviewer in a different tool per phase
  (the owner's ruling, "Review helper, both") `(r3)`.
- The plan gate is recorded in `001-plan-gate.md` `(r4)`: it rules D1, D2,
  D4, D5, D7, D8 and D9 under the delegation, records D6 as the owner's
  ruling, and leaves D3 to the owner at LR3's spec gate (R0.5).
- Each phase: spec, owner gate, change, focused gates, one independent
  reviewer over the diff, refactoring review, record, commit.
- LR3's live run is an owner-selected step inside its phase, with the
  producer and budget named in its spec (D3). Nothing in this plan
  authorizes it.
- One pull request from the topic branch to `main`, or two if LR1 and LR2
  merge ahead of LR3 (D5). Merge stays with the owner. Before the pull
  request, `python3 scripts/components_index.py changed --base origin/main --strict`
  exits 0.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| LR1 | `uv run pytest -q tests/test_lr1_verify_failure_listing.py tests/test_verify_cli.py tests/test_ld3_reading_workflow.py tests/test_documentation_tutorials.py --tb=short` | exit 0 |
| LR2 | `uv run pytest -q tests/test_lr2_quote_scope.py tests/test_anchor_sidecar_v2.py tests/test_ld3_reading_workflow.py --tb=short` | exit 0 |
| LR3 | `uv run pytest -q tests/test_lr3_reference_set.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py --tb=short` `(r4)` | exit 0 |
| all | the structure and inventory guard block of `project.md`, `uv run ruff check` `(r3)`, and `python3 scripts/components_index.py changed --base origin/main --strict` | exit 0 |

The lanes name files that exist at `548b9a1d`, plus one new file per phase.
Affected consumers are read again at each spec and may be widened there. No
broad lane (`-m "evidence or census"`) is selected.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them.

| ID | Question | Proposed |
|---|---|---|
| D1 | LR3: the labelled set. (a) A small set written for the example from openly licensed papers. (b) The corpus run the literature-depth close carried (H18). (c) Ask the reporter for a redistributable slice of theirs. (d) `(r3, r4)` Reuse the packaged regression corpus and its answer key (H24), with any sections the reading stages need added as an overlay beside it; `corpus/`, `answers/` and `expected/` keep their bytes (R0.4). r3's "or extend", retired | (d) if LR3's spec shows the reading stages can read its documents as sources with sections; else (a). (b) stays carried `(r3)` |
| D2 | LR2: the rule. (a) A quote must lie inside the section the model was shown. (b) A quote may lie anywhere in the document the sidecar names, and the pages recommend naming the whole source version and recording the section | (b). It is what `bind_anchors` enforces today (H10); (a) would need a new check and a section concept GND does not have `(r2)` |
| D3 | LR3: the producer and its budget for the recorded run | Owner names one model and a ceiling; the run is recorded once and replayed after |
| D4 | LR3: the scoring rule for "a gold fact is found" | Participant names plus the section the fact was read from overlapping the gold passage, with predicate agreement reported beside it; the scorer reuses `assurance_report.py`'s precision and recall counting (H24). A produced fact has no span of its own (H8), only its section's, so the figures are comparable to #226's only at section grain, and the page says so. If LH1 adds a per-fact span, LR3's spec may score by it `(r3)` |
| D5 | Whether LR1 and LR2 ship ahead of LR3, by their own pull request | Yes `(r2)`. They need no other milestone, and LR3 waits for literature-host-interfaces. The outline proposed holding them so the three replies go out together; LR3 now waits for two phases of another milestone. `(r3)` An interim reply to #226 covering requests 3 and 2 is drafted when LR2 merges (`notes/issue-reply.md`); the owner posts it. If LH1 or LH2 is not on `main` when LR1 and LR2 close, LR3 waits and the milestone stays open; carrying LR3 is the owner's decision |
| D6 | Plan review and close review instrument | **Ruled by the owner, 2026-11-23: "Full panel, both"** `(o)`. The full GND panel for plan and close review. r2's proposal, superseded: "the GND panel light for both" |
| D7 `(r2)` | LR1: does `gnd verify` change. (a) No: the JSON report already answers the request and the phase is a page and a test. (b) (a), and the text output prints each failing verdict's rows under its line. (c) (a), and `gnd verify` accepts `--rule-ids` as `gnd check` does, so a verdict carries the constraint's declared id | (a). #226 asks for no format change (H19). (c) is the one that would let a host name a constraint by its id and not by position; it is offered, not proposed |
| D8 `(r2)` | LR1: the one home of "Reading a failed verification". (a) `docs/guides/documents.md`, after the verify command. (b) `extraction-contract.md` §5, in the packaged skill. (c) `docs/reference/cli.md` | (a); the other two cite it |
| D9 `(r2)` | LR3: what "stage settings" means, given that a run has only a budget and a scenario (H16) | The record names the producer, the budget and the roster's split into opening and targeted sections, read from the settings LH2 writes into a run, and the prompt of each stage if LH2 records it. If LH2 does not, LR3's spec either records the prompts in LR3's own record or asks for a `reading.py` settings field after LH2 merges, one writer at a time (§3) `(r3)` |

Open questions carried into the specs: LR1, whether the page's steps are
shown as a short Python snippet the documentation tests run or as prose with
field names; LR2, whether `block_id` is the recommended place for the shown
section or a new documented convention; LR3, the size of the set, and
whether precision counts a kept fact outside the gold passages as wrong, as
#226 did.

## 11. r3: the first panel round's fixes

The first round ([r2 panel](../../../reviews/literature-reading-reference-r2-panel/README.md))
read r2 at SHA-256
`4960c18dfcf59c7b15b0ca0da1964ae5a4bf6c5034d43455dfb21c8cac97dee2`. Five of
six seats succeeded; Codex blocked. Its seven prioritized fixes and their
sites in r3:

| Fix | What r3 changes | Sites |
|---|---|---|
| fix-lr2-document-scope | the example verifies the joined attempted sections with no sidecar; LR2-C3 pins the span branch | H9, §2 LR2, LR2-C3, LR2-C5 |
| fix-gates | whole-repository `uv run ruff check` is the lint gate; the component-index check stays | Goal, H22, §4, §9 |
| fix-d7b-opt-in | D7 (b) changes default text and would amend R0.1 and LR1-C5 | §5 |
| fix-paths | `src/gnd/` prefixes | H8, H9, H11, H13, H15, H16, H21 |
| fix-lr3-existing-corpus | the regression corpus and scorer are in D1 and D4; D4's section grain; D9's prompts; interim reply and LR3 wait | component row, H24, §2 LR3, §3, D1, D4, D5, D9 |
| fix-lr1-steps | derivation failures, staging, authored fixtures, report-level field names, absolute URL from the skill, `index.md` not an LR1 home | H2, H23, H25, §2 LR1, §3, LR1-C3, LR1-C6, §5 |
| fix-lr2-pages | `index.md:11` rewritten; the LR2 test reads the pages | §2 LR2, LR2-C5 |

Refuted on reproduction, no change: Qwen's claim that a verdict carries no
`verdict` field (the live report carries `"verdict": "fail"`; H2 now lists
it); Kimi's claim that an include resolves against the working directory (a
run from the parent folder exits 1; what is true, that the vocabulary must be
staged beside the model, is in H2). Codex's note that `project.md` says
"There is no component index in this repository" is a stale line in
`project.md` itself, which its later "Component index" section, `AGENTS.md`
and the sibling plans contradict; the check stays, and the stale line is
reported as a follow-up, not edited here.

## 12. r4: the second panel round's fixes

The second and final round
([r3 panel](../../../reviews/literature-reading-reference-r3-panel/README.md))
read r3 at SHA-256
`a1ab8a9c87e7b733eea0b42a5306173385e4c9c44319b96767af82ac0172a299`. Three of
six seats succeeded (quorum); none raised a blocking concern. Under the stop
rule of §8 there is no third round: the five fixes are applied here and
ruled at the plan gate.

| Fix | What r4 changes | Sites |
|---|---|---|
| fix-interim-reply | the interim reply is an LR2 deliverable; §5 names both drafts | §3 LR2 row, §5 |
| fix-example-verify-paths | both verify paths; "no anchor sidecar" | H9, §2 LR2, LR2-C5 |
| fix-corpus-reuse-only | D1 (d) reuses the corpus with an overlay and changes none of its bytes; the LR3 lane names its tests | §2 LR3, D1, §9 |
| fix-lr1-disclosure-and-levels | LR1 cites the disclosure home; the redacting fixture edits the vocabulary; `GND_DISCLOSURE` pinned; three-level field check | §2 LR1, §3 Fixtures, LR1-C3 |
| fix-plan-gate-wording | the gate rules under delegation; full skill path | §8, R0.3, H6 |
