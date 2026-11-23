# Multipass reading and coverage

Run the packaged workflow offline, then replay its retained outputs.

```sh
python -m gnd.examples.literature.reading run --out ./reading-run
python -m gnd.examples.literature.reading replay ./reading-run
```

The example uses locally authored source notes and saved extractor responses.
A fresh run records actual adapter calls. Replay checks each artifact digest,
validates the stage roster and re-derives the report using its retained
response table and the independent producer pin.
The replay path invokes the local GND verifiers and performs zero producer
calls. It exits 3 with incomplete status if a required artifact is stale,
missing or differs on re-derivation.

## Stage files

The independent input roster names source versions, document digests,
section identifiers and byte spans. Available section, table and equation
entries can be inventoried. The stage files occur in this order.

1. Inventory
2. Broad extraction
3. Targeted selection
4. Targeted extraction
5. Review
6. Affected recheck

Each `stage-N.json` binds the exact input digests, predecessor record and
corresponding `payload-N.json`. The saved attempt rows bind the selected
source range and producer response. The review payload binds its separate
source judgments and the targeted vocabulary proposal that produces a revisit
list of previously inspected sections. The run manifest binds all stage and
companion artifacts. A targeted pass recovers a fact from the methods note.
A separate synthetic source excerpt reports both conflicting labels. The
saved candidate binds those labels to the excerpt and fails public verify
and check.

## Coverage and cost

The report gives each question one disposition. Inspected-but-unfound source
material, unavailable material, inapplicable material and explicit statements
of denial remain distinguishable. Refused and empty extractor responses also
have distinct outcomes. Omitted and unavailable ranges contribute zero
inspected bytes, while attempted empty or refused ranges contribute their
actual length. Repeated attempts each contribute their inspected length.
The report includes the number of scheduled, attempted, omitted and
unavailable reads, plus fact and question gains per byte read. Run with
`--scenario unavailable` to exercise exhausted evidence or
`--budget-bytes 0` to exercise budget exhaustion.

A scoped absence claim binds the closure, its declared scope, typed coverage
rows, and a public fidelity report. The report scores the actual methods
extraction and a separate held-back case against independent gold. The
positive recall floor is two of two. One of two leaves the absence status
unavailable for the same scope.

## Assurance coverage

The assurance scorer can compare a replayed reading run against an independent
expected roster with `score_reading_coverage(run_dir, expected_rows)`. The
existing LI1 assurance entry point uses the same scoring rule. Put the rows
in `coverage.json`, set the run
metadata's `coverage` field to `{"sha256": "<digest>"}`, and supply the
expected rows in the answer key's `coverage` field. Each row has a question
ID, the source ID, the corresponding corpus passage ID in `section`, a state
and an `inspected` boolean. The scorer compares the exact tuples at a
precision and recall floor of one. Both inputs are needed to measure this stage.

## Drive it from your host

This section is the one home of the producer protocol, the profile, the
limits and the caller run's manifest. A host with its own documents and its
own reading model calls `run()` as a library function:

```python
from gnd.examples.literature import reading

report = reading.run(out, fixture=root, producer=my_producer, reviewer=None,
                     document_budget=None, unavailable=None, limits=None)
```

**The root.** A root that holds `profile.json` is a caller root. It holds
`roster.json` in the format above, one `<id>.txt` per source, the reading
model and its includes, and the files of the steps the profile declares. A
root without `profile.json` is the packaged layout; any of the new arguments
over it refuses ("caller arguments need profile.json").

**The profile** (`literature-reading-profile/1`). Every key is required and
no other key is accepted:

| Key | Value |
|---|---|
| `model`, `includes` | file names matching `[a-z][a-z0-9-]{0,63}.orm.json`, distinct, at most 17 together. Artifact names derive from the model name |
| `producer_label` | the extraction sidecars' `executing_model` |
| `base_facts` | fact rows added to every population, by fact type; may be `{}` |
| `review` | `true` needs a reviewer argument or `reviews.json` |
| `calibration` | `null`, or `section` (a targeted section), `section_facts` and `held_back_facts` (disjoint, together the keys of `gold.json`), `renderer_label` and two `case_names`. Needs `gold.json`, `calibration.json` (`high` and `low` candidates) and `calibration.txt` |
| `conflict` | `null`, or `fact_type` and `role`: `conflict.json` must hold exactly two rows of that fact type whose role values occur in `conflict.txt`, and `verify` and `check` must both exit 1 on them |
| `absence` | `true` needs `calibration`, `scope.json` and `closure.json`; the scope's `predicate` must be the fact of every scoped question, and the floor is every gold row recalled |

A step the profile does not declare is recorded `skipped`, never as passed
or as zero: the report's `fidelity` is `null`, `reported-conflict` and both
absence statuses read `"skipped"`.

**The producer.** Any object with `produce(call) -> dict`. A `ProducerCall`
carries the stage, the section and its source, version, kind and span, the
section's bytes and their sha256, and the open questions that point at the
section. The answer is `{"outcome", "facts", "proposal_keys"}`: `outcome` is
`accepted`, `empty` or `refused`; `facts` maps fact types the model covers
to rows of role names and string, integer, finite number or boolean values,
and is non-empty exactly when the outcome is `accepted`; each proposal key is
one of the roster's `revisit_keys`. Anything else, an answer over the
response cap, or a producer that raises, refuses the run with nothing
written. The loop counts the calls; a producer needs no `calls` attribute.
With no producer, the root's `responses.json` and `producer-pin.json` are
used and checked as in the packaged run.

**The reviewer.** Any object with `review(call) -> dict`, called once per
accepted response with a `ReviewCall` (the section, its bytes and digest,
the facts and their digest). It returns `{"decision": "supported", "basis":
TEXT}`. Any other decision refuses the run: the reviewer is a check, not a
filter.

**Budgets.** `budget` bounds the bytes read in all; `document_budget` bounds
the bytes read from each source. A section that does not fit what is left is
omitted and the loop goes on, so a later, smaller section is still read. The
report's `documents` gives each source its bytes, attempts, omissions and a
stop reason by the global rule. A document whose required questions are
answered still gets its other scheduled reads. `unavailable` names sections
not to read; `scenario="unavailable"` is the packaged fixture's and refuses
on a caller root.

**Limits.** `ReadingLimits` holds seven caps. Each default is today's
value; each has a hard ceiling (`LIMIT_CEILINGS`):

| Field | Default | Ceiling |
|---|---|---|
| `roster` (sources, sections, questions, each) | 128 | 4,096 |
| `max_budget` | 1 MiB | 64 MiB |
| `input_bytes` (each input file) | 128 KiB | 8 MiB |
| `response_bytes` (one answer or receipt) | 128 KiB | 1 MiB |
| `route_seconds` (each `gnd` route) | 30 | 600 |
| `route_output_bytes` | 1 MiB | 16 MiB |
| `retained_bytes` (each file of the run) | derived | 10 MiB, the repository's JSON read cap |

Before the first producer call the run computes an upper bound on every file
it will retain from the roster and the limits. With no `retained_bytes` the
cap is that bound, at least 128 KiB; a bound over a given cap, or over the
ceiling, refuses. The retained-file ceiling is the cap every JSON reader in
the repository applies, so every file a run keeps can be read back. The
ceilings cannot all be reached together: at the 1 MiB response cap a run
retains fewer than 10 eligible sections.

**What a caller run writes.** A `literature-reading-run/2` folder. Its
manifest adds `settings` (the document budget, the unavailable sections, the
limits with the retained cap used, `producer` `live` or `saved`, `reviewer`
`live`, `saved` or `none`) and `steps` (`ran` or `skipped` for review,
calibration, conflict and absence). A live run keeps the responses as
`producer-output-table.json` and the receipts as `reviews.json`, both bound by
the manifest. The exits of `verify` and `check` over the broad and targeted
populations are recorded as observed, 0, 1, 2 or 4; any other exit refuses.

**A completed caller run is not a verified extraction.** It means every
call was made and recorded. Whether the populations satisfy the model is in
`public_routes`; the host gates on those exits.

**Replay of a caller run.** `replay(folder, fixture=root)` re-derives a `/2`
run from its folder and the caller root with no producer and no reviewer:
the responses and receipts come from the run's own tables, and every setting
and step status from its manifest. It reads the run's files under the
retained-file cap the run recorded, refuses a file whose bytes differ from
the manifest, a manifest setting above its ceiling, steps that differ from
the profile, and any changed input ("stale reading input"). A `/2` folder
replays only against a caller root, and a `/1` folder only against the
packaged one.

The manifest binds the run to itself, not to anything outside it: a folder
rewritten consistently from end to end replays. Keep the `evidence_sha256`
that `run()` returned and pass it as `replay(folder, fixture=root,
expected_evidence_sha256=...)`; then only that run replays.
`score_reading_coverage(run, rows, fixture=root)` scores a caller run the
same way.
