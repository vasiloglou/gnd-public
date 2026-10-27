---
milestone: induced-knowledge
station: followup-ike-q3
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: IKE-Q3
date: 2026-10-27
gate:
  command: "uv run pytest -q -p no:randomly <every tests/test_rf*.py, every test file naming discover, judgments, reference_homes or gnd.api, and tests/test_evolve_references.py: 163 files>"
  exit: 0
  output: "5962 passed, 351 deselected in 1239.49s (0:20:39)"
  note: >-
    The gate on the final bytes; the file list is
    evidence/ike-q3/gate-files.txt. An earlier run over the same 163 files,
    before the review notes N1, N4 and N5 were applied, also exited 0
    (5962 passed, 351 deselected).
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside this follow-up's impact closure; the focused selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/ike-q3/tests-red.txt
    sha256: 0f0d0cbc82da2244f6be240fb14279b6a2499ea4298efe58928b76b7e822839b
  - path: .gnd-planning/milestones/induced-knowledge/evidence/ike-q3/gate-files.txt
    sha256: 365f7463ac2be06fd257f1285bfeab8a96bf36b683b45813b216fd2c8a333f0d
  - path: .gnd-planning/milestones/induced-knowledge/evidence/ike-q3/final-gate.txt
    sha256: e23a4d04c020d7f9d270d7ccd06f171705fdaed2f1413e4e7c92089b757edacc
  - path: .gnd-planning/milestones/induced-knowledge/notes/followup-ike-q3-agent-review.md
    sha256: ae369465d488e20299b7e41cf89aded0246b4b6339b7154930f19574a4f828e3
---

# Follow-up — IKE-Q3: an unbindable reference in discover and judgments

**Claim.** `gnd discover` refuses a reference population file by name when it
is missing (66), or linked or otherwise unreadable (74). The `judgments` API,
and `gnd judgments check`, return outcome 3 with reason "binding" for those
files. Neither lets a raw `ArtifactError` escape. Every other outcome is
unchanged.

**Authority:**
- spec [followup-ike-q3-spec.md](notes/followup-ike-q3-spec.md), approved
  2026-10-27 by the owner directly in the session: "Approve D1 to D3 as
  proposed (D1-A, D2-A, D3-A)."
- carried from [014-followup-evolve-loading.md](014-followup-evolve-loading.md),
  open question IKE-Q3 (spec F12 there).
- base: main at `077f46e`.

## What shipped

- **discover** (`src/gnd/discover/service.py`, `_cmd_discover`): one
  `except ArtifactError` arm after the ill-formed arm.
  - It writes `reference population: <the binder's message>` to stderr.
  - It exits 66 when the cause chain holds a `FileNotFoundError`, else 74.
    This is the cause walk evolve uses (D1-A).
  - The reference binder is the only artifact read in `discover()`. The
    reviewer confirmed this, so the label cannot mislabel another input.
- **discover help and docs:** the help's exit sentence and
  `docs/reference/discover.md`'s exit table name reference files.
- **judgments** (`src/gnd/api.py`, `judgments`): `ArtifactError` joins the
  final `except` tuple. That gives outcome 3, reason "binding", message
  "invalid bound judgment input". No new reason, message or outcome (D2-A).
- **H3** (`tests/test_evolve_loading.py`): the before-r2 fixture bytes are
  kept. `IKE_Q3_RULED` overrides the four ruled rows, and the other 24 rows
  are still compared (D3-A).
- **Tests:** `tests/test_ike_q3.py`, Q1..Q5.

## Exits, base → now

| Case | discover | judgments API / `gnd judgments check` |
|---|---|---|
| missing | 1, traceback → **66** | raises → **outcome 3 "binding"** / traceback → **3** |
| linked | 1, traceback → **74** | raises → **outcome 3 "binding"** / traceback → **3** |
| digest changed | 3 → 3 | 3 → 3 |
| intact | 0 → 0 | unchanged |

`gnd check`, `gnd validate` and `gnd evolve` are not touched.

## Red first

`evidence/ike-q3/tests-red.txt`: 11 failed, 29 passed, on the base source.
The failures are Q1..Q5 (7 cases) and the four ruled H3 rows. Each fails on
the escaping `ArtifactError`, as the reviewer reproduced independently.

## RF controls

- **RF1 goldens:** the help sentence changed, so the discover CLI goldens
  (`cli/tree.json`, `cli-help/gnd_discover.json`, `cli-exit/gnd_discover.json`)
  were refreshed. So were the manifest and its digest constant, as IK4 did in
  `bae3526`. In `tree.json`, only discover's description string was edited:
  a recapture would also have folded in the `check` successor that RF1 applies
  in the test.
- **RF5/RF6:** neither changed body is pinned, so no successor was needed.
  Every `tests/test_rf*.py` passes in the gate.

## Review

One independent agent reviewer: no blocking defect, five notes
([disposition](notes/followup-ike-q3-agent-review.md)).
- **Fixed:** N1 (walk the cause chain), N4 (the doc's 74 row) and N5 (Q5
  asserts reason "binding").
- **Recorded:** N2 and N3, below.

## Findings, recorded as found

- **F1 (refutes the task premise).** `gnd check` and `gnd validate` exit 3 for
  a missing, changed or linked reference. Only `gnd evolve` splits them
  66 / 74 / 3, so "the exits evolve and check give" was two targets (spec §2.1).
- **F2 (review N3, pre-existing).** A model whose directory has a symlinked
  ancestor (macOS `/tmp`) makes discover exit 74 "could not read input", even
  with an intact reference. The base does the same.

## Boundary — what this does NOT establish

- **witness and session replay** still let an `ArtifactError` out of their
  internal functions. H3 pins them, and `session_replay._model` is RF8-frozen.
- **An over-cap reference in judgments** is outcome 3 "binding". Its own
  over-cap inputs are outcome 4 "limit" (review N2).
- **`gnd check` / `gnd validate`** keep 3 for every damage.

## Open questions

| ID | Question | Proposed | Owner |
|---|---|---|---|
| IKE-Q5 | Should an over-cap reference file in judgments be outcome 4 "limit", like judgments' own over-cap inputs, instead of 3 "binding"? | a small judgments follow-up if wanted; it changes an outcome | owner |
| IKE-Q6 | Should witness and session replay refuse an unbindable reference by name? | witness with its command's exits; replay needs an RF8 successor control | owner |
