# Findings ledger: phase-RW3-r2

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
| F1 | the dossier's `scratch=$(mktemp -d) && cd` line: `set -e` does not stop on the left side of `&&`, so a failed `mktemp` was followed by the install in the retained folder | yes | blocking | fixed | 115ae4c1 | the two commands are on two lines. No test is possible; every block passes `bash -n`. The guard is round 1's repair; the `&&` line is older |
| F2 | a wrapped statement was reported twice, once by its line and once by the paragraph pass | yes | hardening | fixed | 115ae4c1 | self-inflicted: the paragraph pass was round 1's repair. The pass is withdrawn, so nothing is reported twice. The check reads lines, as before RW3 |
| F3 | a whitespace-only line did not end a paragraph, so a phrase was found across a paragraph boundary | yes | hardening | fixed | 115ae4c1 | self-inflicted, as F2. Withdrawn with the paragraph pass. `split-phrase-search.py`, which a person reads, splits blocks at blank lines that hold spaces or tabs |
| F4 | a standing sentence reflowed in other ways was reported | yes | hardening | fixed | 115ae4c1 | self-inflicted, as F2. Withdrawn with the paragraph pass: a standing entry is matched against a line, as before RW3. The limit that a phrase split over a line break is not reported is stated in the helper's documentation and the dossier |
