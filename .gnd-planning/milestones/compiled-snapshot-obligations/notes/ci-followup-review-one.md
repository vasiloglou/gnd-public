# Bounded local CI follow-up review one

Inspected the four-file CI follow-up diff and new deterministic timing test.
No production edits or broad suite run. Opinion: **no blocking finding** within
the preservation, denominator and timing-accounting scope requested.

## Preservation and denominator

`src/gnd/synth/frontier.py:114` excludes only the new `compiled-subset` family
from the predecessor snapshot mutation frontier. Measurement and synthesis
call sites still use ordinary `check(model, population)` without the new
activation keyword. The excluded rows are therefore unreachable obligations
for that default measurement contract, rather than omitted existing supported
refusals. The change does not widen the measured denominator or enable a new
checker route. Existing exclusions and admitted families remain intact.

The signature pins explicitly admit the approved keyword-only option with its
False default; they retain the other public signatures and bypass checks.
This updates the expected public surface rather than weakening the prohibition
on substituting another checker.

## Timing accounting

The new wrapper targets `gnd.model.validate_declarations`, which is the actual
runtime global lookup used by bind/resolve paths. Its compatibility aliases in
references/witness remain separately wrapped. The shared `depths['intake']`
guard counts only the outer intake interval, so adding the defining lookup does
not double count nested intake calls or include fixture time twice.

The gate in `tests/test_public_v71_witness_corpus.py:107` retains the exact
10-second threshold. No threshold, selected modes, answer expectations or
measured result assertions were altered. The repair correctly classifies
inherited validation as inherited intake under the pre-existing added-layer
measurement contract.

Ran only the deterministic regression:

```text
UV_CACHE_DIR=/tmp/gnd-review-one-uv UV_PROJECT_ENVIRONMENT=/private/tmp/gnd-issue16-audit/venv uv run --no-sync --python 3.11 pytest -q tests/test_witness_timing_measurement.py --tb=short
```

Result: **1 passed in 0.20s**, exit 0. Its fake monotonic clock advances only in
the defining validation lookup and requires total ticks to equal the sum of
measured buckets, making both escaped and double-counted validation observable.

## Small documentation hardening

`_scan_reason_codes`'s docstring still names only the earlier guarded-exists
exception. Consider updating that sentence to also name the new explicit
compiled-subset boundary. The filter's adjacent comment already explains it;
this is a low-severity documentation suggestion, not a correctness blocker.

## Limits

This is one same-model advisory reader. Root-reported 264 witness and 93 affected
control passes on both interpreters were not rerun by this reader. The narrow
deterministic test and source inspection support the bounded accounting repair,
not full repository CI, platform equivalence, new assurance or certification.
