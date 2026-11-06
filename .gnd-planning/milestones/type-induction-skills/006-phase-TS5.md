---
milestone: type-induction-skills
station: "phase-TS5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-TS5
date: 2026-11-05
gate:
  command: "bash .gnd-planning/milestones/type-induction-skills/evidence/TS5/gate.sh"
  exit: 0
  output: "16 tutorial blocks passed; strict build, no issues; 14646 links checked; 155 passed, 1 deselected; T4 scan clean; ruff clean"
  note: >-
    Spec section 7 T1 to T4 over the phase tree after the review fixes,
    verbatim in evidence/TS5/gate.txt.
slow_cadence:
  command: "uv run python tools/run_tutorials.py (every group); the full default lane"
  trigger: "the milestone close"
  reason: "the close gate runs the union; TS5 changed docs and package data only"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS5-spec.md
    sha256: 3dc6a16c12e86424b2b071bb07defbf1c6269d4dc7dcd650d7c7f44b85ce4dc7
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS5-claude-review.md
    sha256: 62878a0b2a007ee143c1374a8bcceee356fe116eee4c21c50182279f293a6423
  - path: .gnd-planning/milestones/type-induction-skills/notes/TS5-dispositions.md
    sha256: 53583b7b53c2ff5d2a33edf3195ded7192d1f2dcef89c5384d2b77f4be1ca7f6
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS5/gate.sh
    sha256: a38adacd017b23dfc05d72044158daca013c1cb44cca76b081669fd6ceaf6275
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS5/gate.txt
    sha256: 4d1dc79d2f00731c9687b1c58504eb246db1161b402c0e0c1d8854507d82227c
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS5/regressions-red.txt
    sha256: df7d10ef9320e0792730f1cedaf293a24e95026636f45ab5492d66f73db5d749
  - path: docs/how-to/judge-induced-fact-types.md
    sha256: c571cf11005ec6fefb375ac972a8b730084c28fe3797501aacdab4cf2db99889
  - path: docs/assets/applications/judge-flow.svg
    sha256: 0b87953d61815c5beb9d0c1922ab21180fe8c0471f20dccbfab9fb48fe3c4395
  - path: docs/assets/applications/judge-duplicates.svg
    sha256: 1f505340969c45fc3c52f1e197852b5721d0a6dddeda40bffa005fef58e8d454
  - path: docs/assets/applications/judge-multivalued.svg
    sha256: 11401391e75d372e5e4a37680ffd31848202e8a5bbce8f9dc11ad51968080752
  - path: src/gnd/examples/type_judgements/README.md
    sha256: f26f6061682949d7e2e6bb259f02009259f81caa42936c3cfa74bb8091d332b9
  - path: tests/test_type_judgements_example.py
    sha256: 4e4baccc22b59c07f9e7ec244b692df783a9ff97d1aea36a06de1e7aaf118a5f
  - path: tools/run_tutorials.py
    sha256: f742df0b8267fd633970a9c8c4a0ef2d5840655043deaa7fdfdf61411926b635
  - path: docs/reference/discover.md
    sha256: 7bf56b2d1912fcf15cf311f05506a148ad4049c54f571129aeac0ebe50b5d31e
  - path: docs/release-notes.md
    sha256: c4228756073f7a7a8db375bf18190bb4698880ecfdf0827a79ae2ef387d8186d
---

# TS5: documentation and a how-to

Spec: [phase-TS5-spec.md](notes/phase-TS5-spec.md) r1, **delegated approval
(auto=true) `(d5)`** under the owner's `process-milestone
type-induction-skills auto`; an agent ruling, not an owner reading. No paid
call. Fable wrote the how-to; one reviewer read it.

**Checkpoint DC-TS5.** The rendered how-to was published as a private page
and shown to the owner before this record. Asked "Does the how-to read
right, or should it change before I continue?", the owner answered "Looks
good, continue". That answer accepts the page as shown at `dd0d61ef`; the
review fixes below changed one quote, one paragraph and the test after it.

## What shipped

- `docs/how-to/judge-induced-fact-types.md` (in the `zensical.toml` nav):
  round two of `item_has_attribute` twice. The duplicates round asks
  `/gnd:gnd-judge-fact-types`, the multi-valued round asks
  `/gnd:gnd-model-multivalued`. Each shows the recorded typed turns, the
  recorded questions and answers, the verdicts, `gnd discover` rendering
  them and `gnd evolve preview --policy additive` passing. Three figures
  `docs/assets/applications/judge-*.svg`. 16 `gnd-run` blocks, tutorial
  group `type-judgements` in `tools/run_tutorials.py`.
- `src/gnd/examples/type_judgements/` (package data, no module change,
  TS-R1): `duplicates/` and `multi-valued/`, each a fixture's model and
  population plus its recording's judgements file, and a README.
- `tests/test_type_judgements_example.py`: every example file is its source
  byte for byte; nothing else is in the folder; both recordings asked
  before writing and matched their keys; every typed turn equals its
  recording's user turn, and every quoted line, indented or not, is found
  in its own section's recording in order, with ` ... ` the only elision;
  changed pages are caught (review F1, F2).
- The dispositions in [TS5-dispositions.md](notes/TS5-dispositions.md): 16
  rows, 6 updated (`discover.md` TS5-C3, `release-notes.md`, `cli.md`,
  `capabilities.md`, `compose-documents.md`, `gnd-model-evolve/SKILL.md`),
  9 unchanged, 1 refuted (P6).

## Gate output (verbatim)

```text
$ uv run python tools/run_tutorials.py --group type-judgements
16 tutorial blocks passed
$ uv run --group docs zensical build --strict
No issues found
Build finished in 0.53s
$ uv run python tools/check_docs.py site
14646 local links/assets/anchors checked
$ uv run pytest -q <T3: 6 files>
155 passed, 1 deselected in 15.00s
$ T4: anonymity and absolute-path scan of the new files
no downstream names, no absolute paths
$ uv run ruff check tests/test_type_judgements_example.py
All checks passed!
```

## Measured criteria

| Criterion | Result |
|---|---|
| TS5-C1 dispositions | met: 16 rows; the reviewer's wider grep found no missed page and every "unchanged" row accurate |
| TS5-C2, predicate 6 | met with refuted premise P5: two folders, each round two of one generic fact type after one applied induction; a distinct attribute and a duplicate (duplicates round), a multi-valued attribute (multi-valued round); recorded outputs as fixtures, no live model |
| TS5-C3, O9 | met: both `discover.md` passages say what holds by default and under judgement |
| TS5-C4 docs gates | met: T2 above |
| TS-R5 | met: T4 scan; the reviewer found none of the 298 population strings in the page or figures. No test pins that absence; it rests on the runner and the scan |
| T5 | one reviewer; five findings, all fixed |

## Adversarial review

One reviewer is one reviewer. A subagent reviewed `dd0d61ef` read-only; its
report is kept verbatim in
[phase-TS5-claude-review.md](notes/phase-TS5-claude-review.md). It ran the
docs runner, the six test files and each refusal the page names; it did not
run T2 (it writes `site/`). No blocking findings. I reproduced F1 and F2 by
running the old check over changed pages (`evidence/TS5/regressions-red.txt`:
the old check misses a reworded typed turn, an indented quote, an inserted
fragment and a quote moved between recordings; the new check catches all
four), F3 by reading the TS4 `results.json`, F4 and F5 by reading the lines.

| Finding | Class | Fix | Regression test |
|---|---|---|---|
| F1 the quote check misses typed turns, indented quotes, inserted fragments, cross-recording quotes | hardening | per-section check against its own recording, in order; typed turns pinned to `user_turns` | `test_every_typed_turn_and_quote_is_in_its_own_recording_in_order`, `test_a_changed_replay_is_caught[*]`, `test_a_quote_from_the_other_recording_is_caught` |
| F2 the paraphrase test reads no page | hardening | replaced by the changed-page tests | same |
| F3 "noted in the recording" is false | hardening | the page names the multi-valued recording's kept `no_population_access: false`, why it tripped, how the corrected check caught it, and that the phase record and a test carry it | owner rule: every failure explained; prose |
| F4 `<workspace>/` elided inside a code span | completeness, fixed (cheap) | quoted as recorded | covered by the F1 test |
| F5 dispositions scope counted a file twice | completeness, fixed (cheap) | sentence corrected | none (planning prose) |

## Refactoring review

**None needed.** TS5 added docs, package data, one test file and one
tutorial group entry. The new test's recording reader repeats the shape of
`tests/test_judge_fact_types_skill.py`'s stream walk in about ten lines; a
shared helper would couple a docs test to the recorder tests for no change
in behaviour, and TS4-Q1 already holds the recorder's own walk.

## Boundary — what this phase does NOT establish

- **Two rounds, not one.** Predicate 6 asks for one walk; the page shows two
  folders (P5). One evidence file judged by both skills would need a third
  paid recording.
- **The page replays recordings; it does not run a model.** A live skill
  run may word its questions differently.
- **The owner's checkpoint answer covers the page at `dd0d61ef`.** The F3
  paragraph and the F4 quote changed after it.
- **Not run here:** every other tutorial group and the full default lane
  (the close).

## Open questions

- None new. Carried to the close: P1–P6 plan repairs and the §2.2 key;
  TS3-Q1, TS3-Q2, TS4-Q1; the CT4 DateTime kind, the YAML and UTF-16
  tracebacks and `test_rf7_structure.py` red at base (maintenance).

## Refuted premises

- **P5 (plan predicate 6):** one round with every case. The two recordings
  each bind their own fixture's evidence; D2.
- **P6 (plan §3):** `docs/reference/type-judgements.md`. The contract's one
  home is `discover.md` "Type judgements"; D3.
