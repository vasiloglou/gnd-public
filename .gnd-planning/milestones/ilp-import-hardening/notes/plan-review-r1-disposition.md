# Plan review r1: disposition

Reader 1's report is in [plan-review-r1-reader-1.md](plan-review-r1-reader-1.md).
It covers plan r1 (`cbfa12fd…51ce`) and IH0 spec r1 (`269663b5…db81`) at
`1182f96`. One reader is one reader.

**Reproduction (the author, before any repair):**
- **Finding 1:** `git log --first-parent 07f4d45^..fb03739` lists the merges.
  - `#47`, `#50`, `#52` and `#53` change 16, 1, 3 and 11 `src`/`tools` files.
  - IL's merges (#56 to #64, with #59) change 37 files, +3,187/−161.
- **Finding 2:** the reader's `probe_hold.py` shows that rules 4 to 7 of
  AMIE invocation 1 count 19/20, 20/36, 5/6 and 19/35. Each would be refused
  `does-not-hold` by an entry that raises it.
- **Finding 3:** `probe_render_calls.py` over AMIE invocation 2 exits 0 and
  counts `{'render': 1, 'relation_table': 2, 'pairs': 2, 'spell': 310}`.
- **Finding 11:** `probe_ownref.py` gives:
  - with String codes, exit 3 "GND counts 0 of 2" as shipped, and exit 0
    with the count forced;
  - with Integer and String codes, exit 70 with the count forced.

| # | Class | Disposition in r2 |
|---|---|---|
| 1 | blocking | **applied:** IH0's subject is IL's nine merges (37 files). The other milestones' merges are out of scope; IH-D2 restated |
| 2 | blocking | **applied:** `count_mined_rules` raises only mapping refusals and `too-large`; the admission checks stay in the import; `hold()`'s error order is IH1-D2 |
| 3 | blocking | **applied:** the IH1 criterion counts `relation_table` and `pairs` (2 each today, so red first) |
| 4 | hardening | **applied:** IH-D1 (a) states that every AMIE `export.json` golden and digest moves. The risk row says tagging is confined to components with an own-reference subtype, so `facts.tsv` and the retained `facts_sha256` hold |
| 5 | hardening | **applied:** under (b), R1's asserted name change is named, and the new refusal's position is fixed after `type-confused-join` |
| 6 | hardening | **applied:** the refusal-order test is an IH1 criterion, red against a swapped tuple |
| 7 | hardening | **applied:** the facts digest stays in the import (IH1-D1); the pin test is red against a reordering mutant |
| 8 | hardening | **applied:** IH-D5 is recorded as ruled (b) (o) and as a departure from the bar; the close instrument is IH-D6 |
| 9 | hardening | **applied:** IH-R3 names the steps, says the Linux leg is not reproduced, names `evidence/close/ci-run.txt` and cites `a7d6dc0` and `fe80002` |
| 10 | completeness | **applied:** the RF6 successor home and the gate tests are named |
| 11 | completeness | **applied:** the fixture change includes the population |
| 12 | completeness | **applied:** IH0's source is the owner's 2026-10-29 answer |
| 13 | completeness | **applied** in IH0 spec r2: the residual, the re-read row, and "red against the fix's parent" |
| 14 | completeness | **applied:** the shim argument with an identity alias, and `provenance` taking `fact_id`, so no export → discover edge |

Every finding was applied; none was deferred. Completeness findings are
deferred by default, but each of these was a wording or citation repair to
the plan itself.
