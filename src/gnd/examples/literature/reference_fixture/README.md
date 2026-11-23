# Reading reference set

A labelled set for the [multipass reading stages](../reading_fixture/README.md),
and one recorded run over it, so a host can compare its own recall and
precision with a measured reference. It is an overlay on the
[regression corpus](../README.md): the corpus, its answer key and its
expected outcomes are not changed.

**A figure here is a measurement of one run.** It names its producer, its
settings and this set, and says nothing about other papers, other models or
other settings.

## What is here

| File | What it is |
|---|---|
| `<document>.txt` | The corpus's 12 development documents, byte for byte. They are synthetic paraphrases of public works, written for regression tests; no document is the text of its work |
| `corpus.orm.json` | The corpus's flat model, as JSON |
| `roster.json` | One source per document; one section per corpus passage, `<document>-p<n>`. Section `p1` runs from the start of the document (its title and identifier lines) to the end of the first passage and is read by the broad pass; every later passage is read by the targeted pass. Each later section has one question, so the targeted pass reads them all. No question is derived from the labels |
| `profile.json` | A caller root's profile; review, calibration, conflict and absence are off |
| `labels.json` | The gold facts of the answer key, each with its scope (below); a licence per source (Apache-2.0, the repository's, with the work it paraphrases); 31 facts: 11 `work_introduces_method`, 8 `method_builds_on_method`, 12 `method_is_used_in_field`. `work_builds_on_method` is derived by the model, not read, and is left out |
| `run/` | The recorded run, a `literature-reading-run/2` folder |
| `run-record.json` | Who produced it and how: model, CLI version, flags, the prompt template and its SHA-256, the output schema, the spend and the `evidence_sha256` |
| `score.json` | The score of `run/` |

`reference_set.build()` builds every file but the run, the record and the
score from the packaged corpus; a test holds the committed files equal to
it.

## The scoring rule

This section is the rule's one home.

- A gold fact's **scope** is the sections of its document that the answer
  key anchors it in, together with every section of its document whose
  text holds one of its role values. So a fact whose work identifier is in
  the opening section and whose method is in a later one can be found from
  either.
- A produced row is **found** when a gold fact of the same document has the
  same fact type and the same role values, and the row was read from a
  section in that fact's scope. Values are compared after Unicode NFC, case
  folding and collapsing whitespace, and nothing else: a spelling the gold
  does not use is not found.
- A row is **wrong predicate** when a gold fact whose scope holds that
  section has the same multiset of values under another fact type. Role
  names are not compared, so two values that happen to match names in
  another fact count too.
- Each gold fact is found at most once. Every produced row counts in
  precision, including rows outside every gold fact's sections.
- **Precision** per pass is found rows over produced rows. **Recall after a
  pass** is the gold facts found so far over all gold facts.

The grain is the section: a produced fact has no span of its own, only its
section's. Scores taken at a finer grain, a quote's span, are not directly
comparable.

## The recorded run

Producer: Claude Sonnet, `claude-sonnet-5-5`, through the `claude` CLI with
the owner's login, one call per section, with structured output, tools
disabled and no session kept (`run-record.json` has the flags and the
prompt). **Both passes use the same prompt**, which names the section and
its source and asks no question; the passes differ only in which sections
they read, so the targeted row measures the later sections, not a
question-led reading. Byte budget: 7,708, the size of the documents; the 46
sections hold 7,662 of those bytes and were all read, 12 broad and 34
targeted. The owner set a USD 50 ceiling; the run spent USD 0.29.

| Pass | Produced | Found | Wrong predicate | Precision | Recall after the pass |
|---|---|---|---|---|---|
| broad (opening sections) | 10 | 9 | 0 | 9 / 10 | 9 / 31 |
| targeted (later sections) | 23 | 18 | 2 | 18 / 23 | 27 / 31 |

Of the four gold facts not found: one was never produced (`wham-pose`, WHAM
builds on SLAM); one was produced as the right pair of names under another
fact type (`pinn-failure-modes`, curriculum regularization and PINNs); and
two `work_introduces_method` facts were produced with the source's id as the
work in place of the paper's identifier, which the prompt's "source" line
offered (`pinn-failure-modes`, `boltz-1`).

Replay re-derives the run with no producer call:

```python
from gnd.examples.literature import reading, reference_set
import json

record = json.loads((reference_set.ROOT / "run-record.json").read_bytes())
reading.replay(reference_set.ROOT / "run", fixture=reference_set.ROOT,
               expected_evidence_sha256=record["evidence_sha256"])
print(reference_set.score(reference_set.ROOT / "run"))
```

These documents are short paraphrases with one claim per passage, written
so that the claims are stated plainly. The run measures the stages on this
set only; it predicts nothing about longer or denser papers. To score your
own run over this set, run the stages on this root with your producer and
call `reference_set.score(your_run)`.
