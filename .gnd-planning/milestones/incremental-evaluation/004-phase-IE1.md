---
milestone: incremental-evaluation
station: phase-IE1
skill: n/a -- repository development via process-phase
scope: phase-IE1
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline pytest -q tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_rf6_index.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_popvalidate.py tests/test_rf4_peripheral.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_rf9_ci_repairs.py"
  exit: 0
  output: "1419 passed in 34.20s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately selected CI
  reason: focused current state/query/layer consumers cover IE1; historical broad/native lanes unselected
---

# IE1 — accepted under delegated approval

The corpus and delegated approval were committed in 8cf018b before runtime.
Owner milestone auto delegation in 002 covers the documented corpus correction
and review repairs; this is delegated approval, not owner personal inspection.

## What shipped and criteria

- C1: existing positive/negative/aggregate classifications and dependency graph
  drive the reverse closure; unknown change identifiers invalidate all heads,
  incomplete classification refuses. Constraint scopes conservatively invalidate;
  no constraint evaluator consumes a negative selection here.
- C2: independently seeded ModelIndex includes operations and restores an outer
  scope. Typed ordered fingerprints include unit inputs and option binding.
  Corpus covers edits, reordering, marker loss, rosters/references and code changes.
- C3: detached private entries, one committed generation plus one staging map;
  both generations, option binding, signatures, dataclass dictionaries and proxy
  backing tables charged to caps. Oversize or unsupported state computes fresh.
  Exceptions including cancellation roll back; overlapping same-session work
  refuses, independent sessions work. A live capability binds thread/task/nonce.
- C4: IE0 targets and corpus branches were frozen before extension skipping;
  IE1 changes no production evaluation path or public API.

## Independent review

One CLI reader plus bounded confirmation, not a panel. The user explicitly
selected CLI provider transfer. Five initial findings and three confirmation findings reproduced RED, followed
by ten passing direct review controls (including extra expired index and live
cross-thread controls). Retained output declares root-path sanitation. The
reader used static inspection and did not execute verification.

## Refactoring review

Executed: a single fresh-scope helper in ModelIndex avoids copying its content
key policy into session state; existing ordinary public scopes remain intact.
The existing dependency classifiers remain the completeness authority. No
parallel evaluator or family registry introduced. Affected source/query scans
remain enforced; the authenticated syntax successor adds counted sites without
raw model-query waivers. Layer map adds checking home with zero allowances.

## Boundaries and open questions

No extension/constraint skipping, public session, observation adapter, reporter
speedup or benchmark acceptance established here. IE2 owns extension envelopes;
IE3 owns constraint reuse, public API and mutable receipt repair; IE4 feedback;
IE5 complete differential performance and installation. Retained byte projection
is Python-object accounting, not an operating-system RSS guarantee; borrowed
module/code handles are counted shallowly, without retaining copied globals.
A failed transaction retains its prior committed generation. New 547 workload
remains absent. No broad/native, live provider test, certification or merge.

## Refuted premises

A context variable alone does not grant a bounded transaction lifetime: copied
contexts survive reset. Wrapper sizes alone do not account for owned storage.
Per-level policy width/depth caps do not imply a cumulative work cap. The five
pre-fix failures are retained as evidence of these refutations.

Final confirmation disposition: all three findings reproduced (3 failed, 7 passed), then repaired. Ten review controls now pass. Confirmation self-inflicted ratio 3/3=1.0; stop after the declared two-round budget. Repaired bytes carry no further reviewer opinion. The measured gate plus corpus supports delegated acceptance, not an invented review verdict. Source totals: 415 runtime state lines, 290 corpus test lines and 125 review test lines; this exceeds the initial 200–300 runtime estimate because explicit bounded ownership and regressions required more work.

Gate output (verbatim): **1419 passed in 34.20s**. Lint: **All checks passed!**. The earlier pre-repair green outputs remain historical; the current output is evidence/IE1/gate.txt.

## Artifact identities

```json
[
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/approval-amendment.json",
    "sha256": "d0d55f90600a594c1a3670a194b892bff3a6bf9b5d652193a414fffb28ebba5f"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/approval.json",
    "sha256": "13ebc12c68fedff535ed3b3c532ca6ddebef54061835440eaa2953316e3ecd46"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/confirmation-red.txt",
    "sha256": "f2fac4c7eddfb2cd6b435e6008d9874aa6a3d3720303458d5cbc3b3cc62670ec"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/corpus-red.txt",
    "sha256": "6a596e06c2b1dcaabe10d60e77c6e2110a9df8c5ece44fc8678d133061e655a9"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/dynamic-query-successor.json",
    "sha256": "61b223e728cb0444efeedcc2ded5ce9b501246cf1df66aa5b37aac3f0e422bb2"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/gate.txt",
    "sha256": "dbeca465d560c7d55bfb2101871079f11e312f3bae00799a4f7b53b300b2a5e4"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE1/review-red.txt",
    "sha256": "302ffd54b7e6a543a271c26299f06d42c11f2772c076a56c4e4622b67d18b2a7"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/notes/phase-IE1-codex-confirmation.md",
    "sha256": "43ea3b45f013b8b29442c287ed81ac1356f30720fc8de3f622b673117bcb8fb0"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/notes/phase-IE1-codex-review.md",
    "sha256": "baa93baa16f4a1c655e9aa1e97690bac114458e87de3804d441c018f39fb29a2"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/notes/phase-IE1-spec.md",
    "sha256": "295dcb0d64d89c00cbd0a912ec97ab7ae0c6d2d85e7552ce324361a137fde55b"
  },
  {
    "path": "src/gnd/incremental_state.py",
    "sha256": "9d0902ec417f95e77165683304dd80dca43ee06e7f47fd4561e31d126057b0a4"
  },
  {
    "path": "src/gnd/model_index.py",
    "sha256": "a342040b95d33182da92ff265be5be4e1d9ef4d1d2b98ca887abf20c7a5b06a8"
  },
  {
    "path": "tests/support/pyrel_application_successors.py",
    "sha256": "4249acfb4af8974ddc035dccd2f9dc7d44226142ca10fad3ec384ac627dec730"
  },
  {
    "path": "tests/test_incremental_state.py",
    "sha256": "009ccde0371d0c60a425e61dffb46f082cde62ba253afdaf836dff334f063aea"
  },
  {
    "path": "tests/test_incremental_state_review.py",
    "sha256": "1f6f0c74d3eda0b442a710eea1b06efe76de9f1b4068520e25f6c9a97978c2aa"
  },
  {
    "path": "tools/gnd_layers.json",
    "sha256": "f553f9dd9a8f81b8caee782ae0adf67996d653ae0ea4bddfacd02638ef0e4af1"
  }
]
```
