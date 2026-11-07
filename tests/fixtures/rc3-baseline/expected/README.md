# RC3 corpus answer key

## How it was written

- `<case>.json` for cases 1-5: the head's `--rule-ids --format json` report
  at eac81cf8 (before any RC3 change), with `novelty`, `row_novelty`,
  `baseline`, `exit_code`, `outcome`, `acceptance_ready` and `assurance`
  filled by an oracle script that applies the spec's rules directly to the
  head and base reports: a key is the rule's address plus the canonical JSON
  of the row (or the address alone for a failing rule with no rows); keys in
  both are standing, head-only are new, base-only are resolved; the band is 1
  for a new must-hold failure, else 4 if a must-hold rule is unchecked in
  either run, else 2 if head is vacuous, else 0; the assurance block is the
  uncertified block for that band (spec D5).
- `mixed.txt`: the head's text report at eac81cf8 with each failing line
  marked new or standing and the `BASELINE` block appended (spec D6).
- `refusals.json`: the fields cases 7-9 must have, not whole bytes.
- `exits.json`: the exit code of every case.
