# Why-not near-misses close follow-ups, 2026-11-03

The why-not-near-misses close
(`milestones/why-not-near-misses/005-milestone-close.md`, question sweep)
deferred four items. The owner asked for them to be fixed and the local CI run.
That close record is history and stays as written; this note records what
happened to each item.

## Outcome

| ID | Disposition |
|---|---|
| NM2-Q3 | Closed by design, owner decision 2026-11-03. The goldens are not rebased (see below) |
| NM4-Q1 | Fixed in PR 79: the IK census reads only its own milestone's commits, ending at the last IK-close commit |
| R1-F1 residual | Fixed in PR 79: a near-miss sample shows, per variable, the spelling whose canonical encoding comes first among every row that met the binding, whatever the row order |
| O14 | Open with the reporter: the issue note asks them to re-run their deletion test |

The PR 79 CI run (beast-3, Python 3.11 and 3.13) also found three defects,
fixed in the same PR:

- The RF6 dynamic inventory lacked the kernel change's syntax candidates; they
  are recorded in
  `milestones/why-not-near-misses/evidence/close-followups/dynamic-query-successor.json`.
- A block in `docs/reference/disclosure.md` showed argparse's `choices` list,
  which some Python releases quote and others do not (3.11 quotes; 3.14 does
  not). It passed only on 3.14. The block now cuts the list.
- The NM checkpoint drafts kept their source pages' relative links and failed
  reference closure; they are registered as retained snapshots, pinned by
  digest.

## NM2-Q3: why the RF1 goldens are not rebased

A fresh `tools/rf1_pins.py` capture and merge differs from the committed
goldens in 73 files. That is the RF1 design, not drift:

- RF1 pins are the original capture at `e834c6e` plus declared successors.
  Changed behaviour is pinned by a successor the test states
  (`_assert_successor` in `tests/test_rf1_cli_pins.py`, for example the
  `--compiled-operations` option in the CLI tree and help pins), and the
  original golden stays.
- The v1 and v2 session pins are absent from a fresh capture because they go
  through the RF2 `assert_successor` (`tests/support/rf2_session_pins.py`).
  It binds each answer in `tests/fixtures/rf2-pins/session-successors.json`
  to the digest of the original golden and never writes an RF1 golden. A
  rebase would delete those originals and break that binding.
- Every pin passes on `main`.

A rebase would erase the successor history and the v1/v2 originals and fix
nothing. Rule going forward: when a pin fails, declare a successor for that key;
do not overwrite the original golden.
