# Findings ledger: CG2-r1

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Malformed input escaped the CLI | yes | blocking | fixed | 5c8f9a86 | Invalid YAML exercises the public error band and diagnostic. |
| F2 | An isolated row digest discloses low-entropy values | yes | blocking | fixed | 25efdbd3 | No row-value digest appears. An injective substitution of every value preserving singleton membership leaves the full report identical. |
| F3 | Multiple shared trigrams consumed the unique-pair budget | yes | blocking | fixed | 25efdbd3 | Posting visits consume the item budget. Each distinct comparison consumes one pair. Two long similar names finish with one pair. |
| F4 | Explicit unit-based entity references absent | yes | blocking | fixed | 25efdbd3 | Distinct units on the same measure are grouped for entities and value types, independently of labels. |
| F5 | Equivalent Unicode readings differed | yes | blocking | fixed | 25efdbd3 | NFC and decomposed readings produce one shape. |
| F6 | Acronyms and digits hid units; ambiguous one-letter suffixes were accepted | yes | hardening | fixed | 25efdbd3 | Multi-letter lexical units work after acronyms and digits. Single-letter units need explicit unit metadata. |
| F7 | Included fact samples absent from singleton indexing | no | hardening | fixed | 25efdbd3 | The sample walk now precedes ownership filtering. An included model produces no targets. Independent validation of each include restricts which cross-boundary samples a fixture can declare. |

One reviewer is one reviewer. The direct stdin invocation returned the review verbatim in independent-review.md. Its claims apply to the supplied hashes. Repairs are exercised by regressions and have no separate reviewer verdict.
