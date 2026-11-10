# OS0 measurement candidate

Date 2026-11-10. GND measurement base `d5156595`. Integration base
`54483d03e1033df49adb993f58a6d1a80f7b35f5`, the merged plan from PR #159.
The approved spec and delegated retention amendment are in
[002](002-OS0-spec-gate.md).

[Evidence manifest](evidence/OS0/manifest.json), SHA-256
`f790b7455080d8f689a69e29d02611aa60f1b34a8b346f2cd0c0b53c6d3f627e`, binds the scratch reproduction scripts,
original approved spec, pins, census, experiment records and checkpoint.
[The experiment summary](evidence/OS0/README.md) records measured dispositions,
limits and the proposed inputs to the dependent phases.

## Local checks

- A scratch rerun of `inventory.py`, `formulas.py` and `oracle.py` exited 0.
  Eleven measured outputs matched the retained bytes. The individual tool
  exits and diagnostics are in E1–E6 and E3b.
- An independent local traversal matched all 2,673 pointers and 14 input
  digests. It checked the four PyRel source identities against the two
  retained output files.
- On the integration base, the inventory, constraint census and E4/E6 output
  match byte for byte. All 14 `python -m gnd validate` observations match,
  including the three baseline exits 3. Exact outputs are in
  [gnd-validation.json](evidence/OS0/gnd-validation.json).
- `git diff --exit-code 54483d03 -- src tests` and
  `git diff --cached --check` exit 0. Ruff over the reproduction scripts exits
  0 with `All checks passed!`. The component-index check against 54483d03
  exits 0 with zero fixes, warnings and rereads.

## Remaining gates

The required single independent phase review is pending. Automatic approval
review refused transmitting the selected artifacts to the authenticated Claude
service before explicit approval of the payload and destination. OS0 completion
still needs that review and its disposition. OS1 also needs explicit owner
confirmation of OD6 under the accepted plan.

The invalid census examples and the 27 absent schema definitions remain
visible in the [evidence](evidence/OS0/README.md). The fixtures establish
pointer coverage for the exact census and parser behavior for the authored
probes. Broader formula equivalence and exporter admission are future gates.
