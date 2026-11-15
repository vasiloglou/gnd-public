# LI3 preregistered measurement

Pinned input is diagnostics/measurement.json with 300 occurrences.
Pinned labels are diagnostics/labels.json, assigned by the corpus author
from the scenario's declared semantic relationships. Unlisted pairs have
no expected kind. The measurement compares one emitted kind with that
ledger. A different kind is a false discovery. The denominator is sampled
emissions of each kind. The per-kind ceiling is 1/5 for strata with at
least 20 observations. A stratum with fewer than 20 in its census is
reported as unmeasured. It earns no budget claim. The procedure measures
false discoveries among emitted synthetic candidates, with no sensitivity
or real-world inference from this sample.

Census if total emissions are below 100. Otherwise allocate each stratum
a floor of up to 20 and distribute the remaining slots proportionally
to remaining stratum sizes, using integer largest remainder and sorting
ties lexically by kind. Sample without replacement with Python's
Random(193).sample from pairs sorted by their occurrence IDs. Allocate
and draw in sorted kind order. Report the selected pairs, label
disagreements and numerator and denominator. Score liveness with an
oracle that emits ledger kinds and a control that replaces labels with
null. Both controls use the same sample selection and grading logic.

## Corpus observation and delegated clarification

The spec gives diagnose(data: Any) -> dict. The direct cases use
diagnose(data: Any) -> list[dict] so callers can inspect candidates before
the CLI wraps them with the input digest, threshold and exit. Adopt the
latter signature. The CLI report retains its specified shape.

The size control uses 500 distinct single-token names. A separate dense
control exercises the 8,000-candidate refusal before report construction.
The candidate count cap bounds output allocation. Exact ordered input caps
remain in the spec.

The kept source-evidence coordinates and instance digests can be produced
from the synthetic source construction documented in the corpus README.
The name rule can consume these independently of the label ledger. All
four named candidate classes and exclusions have accepting or refusing
controls. The fixed corpus has both correct and spurious candidate signals.
