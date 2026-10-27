# Follow-up spec — IKE-Q3 (unbindable reference in discover and judgments)

**Status:** owner-decided (2026-10-27): D1..D3 approved as proposed (§6.1).

## 1. Provenance

- **Carried by:** [014-followup-evolve-loading.md](../014-followup-evolve-loading.md),
  open question IKE-Q3, and finding F12 of
  [followup-evolve-loading-spec.md](followup-evolve-loading-spec.md) (r2.6).
  D6-A forbade exit changes there, so test H3 pins the leak as it is.
- **Exit precedent:** [009-phase-IK4-Q2.md](../009-phase-IK4-Q2.md), the owner's
  I-F2 ruling for evolve: a missing reference file exits 66, a linked one 74, a
  digest mismatch 3.
- **Base:** main at `077f46e`.
- **Protocol:** process-phase, `auto=false`. No panel has read these bytes.

## 2. Reproduction on the base (author's runs, 2026-10-27)

The fixture is a scratch copy of `tests/fixtures/reference-corpus/dispatch/`,
with `references/catalog.pop.json` deleted (missing), given one extra newline
(changed), or replaced by a link to an identical file outside (linked).
"API" is `gnd.api.judgments` as H3 calls it (policy and receipts readers
patched so the run reaches the bind).

| Case | `gnd discover` | `judgments` API | `gnd evolve preview` | `gnd check` / `gnd validate` |
|---|---|---|---|---|
| intact | 0 | 3 "shape" (the probe policy) | 0 | 0 / 0 |
| missing | **1**, traceback: `ArtifactError … could not be inspected: [Errno 2]` | **raises** `ArtifactError` | 66 | 3 / 3 |
| changed | 3 "reference raw hash does not match declared sha256" | 3 "binding" | 3 | 3 / 3 |
| linked | **1**, traceback: `ArtifactError … is a symlink` | **raises** `ArtifactError` | 74 | 3 / 3 |

`gnd judgments check` returns the API's `outcome` as its exit, so the same leak
reaches the CLI as a traceback.

### 2.1 Refuted premise

- **"`gnd evolve` and `gnd check` give the same exits for these cases."** They do
  not. `gnd check` and `gnd validate` exit 3, with a named message, for all
  three damages; only evolve splits them 66 / 74 / 3 (record 009, I-F2). So
  "the exits evolve and check give" is two different targets, and the owner
  picks one per home (D1, D2).

## 3. Where the leak is

- **discover:** `_bind_references` (`src/gnd/discover/service.py:129`) calls
  `bind_declared_references`, which passes the binder's `ArtifactError`
  through unwrapped by design (IK4-Q2-R1). `_cmd_discover` catches
  `ReferenceInputError` and `OSError`, not `ArtifactError`. The binder is the
  only artifact read in `discover()`, so a catch there names exactly the
  reference case. The missing case's `ArtifactError` has a `FileNotFoundError`
  cause; the linked case has none.
- **judgments:** `api.judgments` (`src/gnd/api.py:897`) calls
  `bind_declared_references` after the population load. Its handler catches
  `ValueError`, `TypeError`, `OSError` and the load errors, not
  `ArtifactError` (a plain `Exception`). The changed case is a
  `ReferenceInputError`, a `ValueError`, so it is already outcome 3.

## 4. Proposed exits

| Home / case | Base | Proposed |
|---|---|---|
| discover missing | 1 (traceback) | **66**, stderr `reference population: artifact … could not be inspected: …`, nothing written |
| discover linked | 1 (traceback) | **74**, stderr `reference population: artifact … is a symlink`, nothing written |
| discover changed | 3 | 3 (unchanged) |
| judgments API missing | raises | **outcome 3**, error `{"reason": "binding", "message": "invalid bound judgment input"}` |
| judgments API linked | raises | **outcome 3**, same error |
| judgments API changed | outcome 3, same error | unchanged |
| `gnd judgments check` missing / linked | 1 (traceback) | **3** (its exit is the outcome) |

Any other `ArtifactError` from the discover bind (a directory at the reference
path, an over-cap file) falls in the same catch: 66 only when the cause is
`FileNotFoundError`, otherwise 74, matching evolve's markers (" is not a
regular file", "could not be read" → 74).

**Why judgments is not 66/74.** The judgments contract
(`gnd-dev-session/references/judgment-contract.md`) is a closed vocabulary:
"0 satisfied, 1 valid unsatisfied, 3 invalid, 4 unavailable or
resource-limited", with bounded messages that omit input values. Its own
missing or linked model, population, policy or receipts file is already
outcome 3 "binding" (`api.judgments`'s `read`). 66 and 74 would be new
outcomes in that contract.

## 5. Implementation (after approval)

- `src/gnd/discover/service.py`, `_cmd_discover`: one `except ArtifactError`
  arm after the `ReferenceInputError` arm, writing the prefixed message and
  returning `EXIT_NO_INPUT` when `error.__cause__` is a `FileNotFoundError`,
  else `EXIT_IO`. `discover --help`'s exit sentence gains "66 on a missing input
  or reference file, 74 on a refused output or reference path".
- `src/gnd/api.py`, `judgments`: add `ArtifactError` (already imported there)
  to the final `except` tuple. No new message, reason or outcome.
- **RF controls:** if an RF5/RF6 (or RF4 body) control pins either changed
  body, register a successor by a script under
  `.gnd-planning/milestones/induced-knowledge/evidence/ike-q3/`, as
  `evidence/close/` and `evidence/evolve-loading/` did. Measured during
  implementation, recorded as a finding.
- About 10 lines of src; about 80 of tests.

## 6. Decisions for the owner

| # | Question | Options | Proposed |
|---|---|---|---|
| D1 | discover's exits for missing / linked | **A:** evolve's 66 / 74 (discover already uses 66 for a missing input and 74 for a refused path). **B:** check's 3 for both, as an invalid model. | **A** |
| D2 | the judgments API's outcome for missing / linked | **A:** outcome 3 "binding", as its own unreadable inputs and the changed case. **B:** missing → outcome 4 "unavailable", linked → 3. **C:** 66 / 74 (extends the closed contract). | **A** |
| D3 | H3's pinned rows | **A:** keep the before-r2 fixture bytes (a historical measurement) and have H3 apply an explicit four-row `IKE_Q3_RULED` override naming this spec. **B:** rewrite the four fixture rows. | **A** |

### 6.1 Owner rulings

2026-10-27, the owner directly in this session: "Approve D1 to D3 as proposed
(D1-A, D2-A, D3-A)." (o)

| # | Ruling |
|---|---|
| D1 | **A**: discover exits 66 on a missing reference file, 74 on a linked one (o) |
| D2 | **A**: the judgments API returns outcome 3, reason "binding" (o) |
| D3 | **A**: H3 keeps the before-r2 fixture bytes and applies a four-row override (o) |

Approved bytes: r1 as committed with this ruling. No panel ran.

## 7. Tests (each fails first on the base)

New file `tests/test_ike_q3.py`, using `tests/support/reference_homes.py`:

| ID | Case | Asserts |
|---|---|---|
| Q1 | discover, missing | exit 66; stderr names `references/catalog.pop.json`; no `Traceback`; `--out` and `--report` not written |
| Q2 | discover, linked | exit 74; same |
| Q3 | discover, a directory at the reference path | exit 74; no traceback |
| Q4 | judgments API, missing and linked (parametrized) | returns, outcome 3, reason "binding" |
| Q5 | `gnd judgments check` in process, missing and linked | exit 3; no traceback |
| H3 | `test_h3_every_homes_outcome_is_unchanged` | the four discover/judgments missing/linked rows now expect the ruled outcome; every other row unchanged (the five other homes, both intact and changed rows) |

Discover changed (3) and judgments changed (3) stay pinned by H3.

## 8. Verification

- Red: Q1..Q5 and the four H3 rows on the base, saved verbatim to
  `evidence/ike-q3/tests-red.txt`.
- Focused gate: `tests/test_ike_q3.py`, `tests/test_evolve_loading.py`,
  `tests/test_evolve_references.py`, every `tests/test_*discover*.py`, every
  test file naming `judgments`, and every `tests/test_rf*.py`; saved to
  `evidence/ike-q3/final-gate.txt`.
- One independent reviewer agent over the diff; outputs only in the session
  scratchpad, then dispositioned in
  `notes/followup-ike-q3-agent-review.md`.
- Record 015 in the milestone directory.

## 9. Boundary

- **witness and session replay** also let an `ArtifactError` out of their
  internal functions (H3 rows `witness/*`, `replay/*`). They are not public
  command outcomes measured here, `session_replay._model` is RF8-frozen (F11),
  and the task names only discover and judgments. H3 keeps pinning them.
- `gnd check` / `gnd validate` keep 3 for every damage.
- No exit is renumbered; no new exit is allocated.
