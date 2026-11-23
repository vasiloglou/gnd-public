# LH1 reading fixtures

- `packaged/{full,unavailable,budget-0}/`: the three packaged reading runs,
  written at commit 78934ee3 with gnd 0.4.0 before any LH1 source edit, by
  `python -m gnd.examples.literature.reading run --out DIR` with no option,
  with `--scenario unavailable` and with `--budget-bytes 0`. Their `run.json`
  digests are the LH1 spec's P3. `test_lh1_reading_host.py` (T11) compares
  fresh runs with them through `tests/support/recorded_version.py`.
- `caller/`: a caller root authored for LH1. Two sources (`survey-a`,
  `survey-b`), its own model `survey.orm.json` with its include
  `terms.orm.json` (one uniqueness constraint, on `paper_title`, so exits 2
  and 1 are reachable), `profile.json` with no step declared and
  `profile-declared.json` with every step declared, and the seven step files.
  It shares no section, fact, label or subject name with the packaged
  fixture. The producer's answers live in the test module.
