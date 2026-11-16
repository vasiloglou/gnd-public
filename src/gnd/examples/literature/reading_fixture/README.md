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
