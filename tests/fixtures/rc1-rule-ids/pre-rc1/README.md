# Pre-RC1 text output

`declared-fail.txt` is the text `gnd check` printed on 2026-11-06, at
commit 8bfbe417 (before RC1), for `models/components.orm.yaml` with its two
`remedy` lines removed (that build refused `remedy`) and
`populations/graph-fail.pop.yaml`. Without `--rule-ids` the RC1 build must
print these bytes for the model with its `remedy` lines: a remedy is never
printed unless the flag is given. Added after the corpus was approved, for
review finding P3; it is not part of the approved answer key.
