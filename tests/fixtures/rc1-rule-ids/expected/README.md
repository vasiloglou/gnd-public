# RC1 corpus answer key

The expected results for the cases in `../README.md`. Kept apart from
that file so a reader can work out the answers from the stories alone.

## How it was written

- `expected/<case>.json` for cases 1-4: today's version-7 report for the
  same input (with `remedy` lines removed from the model, since today's
  validator refuses them), with the version set to 15, three keys inserted
  after each verdict's `constraint_ref` (`address`, `addressing`,
  `remedy`), two appended to each verdict (`novelty`, `row_novelty`, both
  null), and two appended to the report (`baseline: null`,
  `allow_vacuous: false`). Case 1's model digest is computed for the model
  with its `remedy` text, by the digest function the checker uses, checked
  first against a model whose digest is known.
- `expected/declared-fail.txt`: today's text report with the two verdict
  lines rewritten and a remedy line added after each.
- `expected/refusals.json`: the fields cases 6-8 must have (version, exit,
  issue rule id, no error about the missing population), not whole bytes,
  because the refusal's message wording is not part of the contract.
- `expected/exits.json`: the exit code of every case.
