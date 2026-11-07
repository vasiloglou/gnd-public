# RC4 corpus answer key

- `vacuous-only-plain.json`: the `--rule-ids --format json` report at
  4713fc8a, unchanged.
- The other `.json` answers: the `--rule-ids` report (cases 1, 3, 4) or the
  `--baseline` report (cases 5, 6) at 4713fc8a, with `allow_vacuous: true`
  and, where the band was 2, `exit_code` 0, `outcome` `accepted`,
  `acceptance_ready` true and the uncertified `accept` assurance block (spec
  D2). Where the band was not 2, nothing else changes.
- `vacuous-only.txt`: the `--rule-ids` text report at 4713fc8a plus the
  closing line of spec D3.
- `exits.json`: the exit code of every case.
