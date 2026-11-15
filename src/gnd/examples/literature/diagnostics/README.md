# Name diagnostics corpus

`cases.json` preserves the four named spelling pairs and the cross-field
flow matching control. `case-outcomes.json` gives the required kind for each
pair and the malformed-input exit.

`measurement.json` holds 300 synthetic occurrences seeded from public
method names. The occurrence source IDs, contexts and coordinates are
synthetic. Each digest refers to the canonical JSON bytes of a one-row
population with model `literature-names`, that source ID, empty covers
and instances, and a `method_mentioned` fact whose `method` holds the
original spelling. The final newline is included in the digest.

`labels.json` records the authored semantics of pairs within each
scenario. A name collision, a common kind, a spelling variant and a
spurious resemblance all have different stories. Pairs outside the
authored scenarios have no expected kind. The synthetic sample measures
this corpus with the recorded grading policy. Its labeller is the corpus
author.
