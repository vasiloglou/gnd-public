# TP0 baseline: issue #24 workload on `2d1ff4d`

Produced by `uv run python tools/measure_transition_cost.py --out <this dir> --repeat 5`
(counters, digests, timings), with `--compare-import SOURCE` for `import.json`. Runtime bytes
are unchanged (`git diff 2d1ff4d -- src/gnd` is empty). Machine: Apple arm64, macOS.

## Counters (gates), reporter replay of 13 calls

| Counter | Baseline | Issue figure | Note |
|---|---|---|---|
| `checker_runs` | 25 | 25 | 7 checks, plus 6 one-step transitions at 3 checks each |
| `model_index_calls` | 540 | 535 | every call runs the key path today |
| `model_index_key_paths` | 540 | — | TP1 target unit |
| `model_dumps_other` | 457 | — | TP1 must not increase it |
| `model_digests` | 212 | — | marker digest re-derivations |
| `deepcopy_calls` | 1,290 | — | top-level, from GND frames |
| `deepcopy_nodes` | 2,760,394 | 2.7 M | TP2 target unit (≥ 50% fewer) |
| `extension_views` | 18 | — | |
| `correspondences` | 25 | — | one per checker run |

`course` control (`attempt-3`, 3 steps, wrapped with `steps_document`): 5 checker runs, 115
model-index calls, 21,492 deep-copied nodes; exits 0. `attempt-1` and `attempt-2` exit 1.

Targets in counter units (TP0-C5; plan D-p1-2):

- **TP1:** `model_index_key_paths` from 540 down to at most one per public call, plus one per
  loaded intermediate and loaded population, measured on the same replay. TP1's spec fixes the
  exact number, and `model_dumps_other` must stay at or below 457.
- **TP2:** `deepcopy_nodes` at most 1,380,197.
- **TP3:** `checker_runs` 25 → 19 when receipts are used, with minting adding none.

Node counts are interpreter-specific: 3.11 measures 2,761,233. Compare like with like.

## Parity

`digests.json` holds the normalized payload digest and the sorted branch-trace digest of every
surface: 7 × three check modes, 6 × transition with and without a declared post, the `course`
surfaces (including admission), CLI runs (reporter check, reporter transition, `course`
pre check), and the batch run (exit 2, 7 projections, 0 violated, with a payload digest; CLI
and batch runs have no trace digests because they run in a subprocess). The CLI and
API digests are equal. `NORMALIZED_FIELDS` is `model` and `population` (input paths only).

`import.json`: the original bundle and the committed fixture agree on every call's exit code,
counts, payload digest, trace digest and counters (`"equal": true`). The fields excluded from
the payload digest are listed in the file: identity fields that echo the renamed `model_id`,
or digests the transform recomputes.

## Timings (evidence only, never a gate)

Separate uninstrumented runs, 5 repetitions of the 13-call replay. The 3.14 row is from the
final run that produced `timings.json`; an earlier 3.14 run the same day measured 5.79 s,
which shows the session-to-session variation.

| Python | Median | Spread (max − min) / median |
|---|---|---|
| 3.14.3 (session default) | 5.09 s | 2.8% |
| 3.13.12 | 4.02 s | 2.0% |
| 3.11.15 | 4.32 s | 0.3% |

The reporter measured 3.96 s on `8a3a98ba`. Planning readers observed about 20% variation
between sessions. Profiling inflates times 2.7–3.2×. The milestone's expected ceiling is
about 44% less GND wall time (plan, Problem section).

## Focused gate

`uv run pytest -q tests/test_transition_cost_workload.py tests/test_rf1_layering.py
tests/test_public_transition_contract.py` on 3.14.3, 3.11.15 and 3.13.12 (`gate-py*.txt`).
The counted replay runs after a one-time warm-up (spec finding 7).
