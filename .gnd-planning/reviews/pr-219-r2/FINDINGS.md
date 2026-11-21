# Findings ledger: pr-219-r2

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
| F1 | IR3's acceptance asks the interop `checking.orm.json` to export, but it is temporal and PyRel export refuses temporal models | yes | blocking | fixed | 2d29588c | Reproduced: `require_non_temporal` refuses the loaded root; the reviewer's flattened render raised the `export/emit.py:36` refusal. IR3 now accepts the non-temporal `extraction.orm.json` root (version 5, two includes; today it refuses `include:unsupported-route: export.pyrel`) and expects the temporal root to reach the temporal refusal. New owner decision D3; D2 reworded; RP1 and RP4 aligned. Planning text only, so no regression test |
| F2 | `handoff.py` writes only the first 25 ignored paths into the note, and `takeover` checks only those, so it can report ready with a required path missing | yes | hardening | deferred | | Reproduced by reading `handoff.py:718-720` in both twins; the reviewer's 26-path fixture returned `ready: true`. Dev-tools-owned file, not edited here (`.devtools.toml`). Target: the dev-tools source owner, filed as https://github.com/vasiloglou/dev-tools/issues/28. Until fixed, a receiver runs `handoff.py ignored` when the note says "and N smaller paths" |
| F3 | The maintenance note says D-12 admits only two combinations; `induced` / `proposed` / `deontic` is a third | yes | completeness | fixed | 2d29588c | `_enforce_d12`, `src/gnd/evolve/service.py:445-451`. The note lists all three combinations |
