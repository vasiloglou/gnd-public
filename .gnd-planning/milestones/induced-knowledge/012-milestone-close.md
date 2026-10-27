---
milestone: induced-knowledge
station: milestone-close
skill: process-milestone
scope: milestone-close
date: 2026-10-27
source_base: b99dfec
gate:
  command: "uv run pytest -q -p no:randomly <the 260 files of every phase gate, listed in evidence/close/final-gate.txt>"
  exit: 0
  output: "8551 passed, 279 deselected, 1 warning in 1074.09s (0:17:54)"
  note: >-
    C-G1, at 5e25dbb. The union of the test files in the gates of records
    002–010 (IK1's 56-file list, the IK2, IK2-repair, IK3, IK4 and IK5
    gate-files lists, and the commands of 008, 009 and 010), plus the close
    regressions and test_atom_bind. tests/test_incremental_performance.py is
    excluded, as in every phase since IK4 (IK4-Q5). The one warning is the
    pre-existing exp-session one. The same run also did
    zensical build --strict (no issues) and tools/check_docs.py site (11416
    local links/assets/anchors checked). After the gate, reader four's two
    page fixes (learn-rules.md, discover.md) and the close records were
    checked by the docs, walk, scaffold, release and close suites (230
    passed), the strict build (no issues) and check_docs (11417 checked).
full_suite:
  command: "uv run pytest -q -p no:randomly"
  exit: 1
  output: "4 failed, 15781 passed, 783 deselected, 1 warning in 2115.40s (0:35:15)"
  note: "At bce65a8. Three of the four are fixed after it (6b2b304, 5e25dbb) and pass in the gate above; the fourth is IK4-Q5, red on main. evidence/close/full-suite.txt"
slow_cadence:
  command: "uv run python tools/check_installed_docs.py --out <scratch>"
  exit: 0
  output: "217 tutorial blocks passed; Both installed wheel origins passed the documented learning paths."
evidence:
  - {path: ".gnd-planning/milestones/induced-knowledge/notes/close-spec.md", sha256: "f5f9a7d5a24a559f3d871eca3e1a9980b0d53be418d17358060cd435aa6a1841"}
  - {path: ".gnd-planning/milestones/induced-knowledge/011-owner-decisions-close.md", sha256: "b7c3db8a4fe61e885d8bfe430d4b062d2bae137a72919e94e9c1307a2976a1de"}
  - {path: ".gnd-planning/milestones/induced-knowledge/notes/close-reading-one.md", sha256: "e01227a11b099c7cef0152d952586ea82b14fc3c4da2aff6732e3783de6b21d7"}
  - {path: ".gnd-planning/milestones/induced-knowledge/notes/close-reading-two.md", sha256: "c5b14fb2b075a29bde6ec2f5c2e051cd8d14d238833d02386cefeb8ab1ecbbcc"}
  - {path: ".gnd-planning/milestones/induced-knowledge/notes/close-reading-three.md", sha256: "90e874ad11ac3ea3dd1eef6515baef34016e03ed990ddfae25a9e3af5c162d7e"}
  - {path: ".gnd-planning/milestones/induced-knowledge/notes/close-reading-four.md", sha256: "8f96df0bc46cac8a3f8b450ec17bfe3967a238d0164fc8c02e14122561c9d7ed"}
  - {path: ".gnd-planning/milestones/induced-knowledge/evidence/close/final-gate.txt", sha256: "e4dcb2519083dc0c60eabc5c36cb26415a6458b7b3b430382f6ab9916e654373"}
  - {path: ".gnd-planning/milestones/induced-knowledge/evidence/close/full-suite.txt", sha256: "15607a7c42f86ae687fd104975c97ca95b945bdc02ad0a9c020d2330fb710002"}
  - {path: ".gnd-planning/milestones/induced-knowledge/evidence/close/installed.txt", sha256: "f0f1af85d0b3dfa61044774a2eea5587cd49ea401940a98a2f391f11d0cdc8d9"}
  - {path: ".gnd-planning/milestones/induced-knowledge/evidence/close/regressions-red.txt", sha256: "e647711ecdfcc708d1b017f1116d122813b99ae7719452be29cbdd3f42f777ba"}
  - {path: ".gnd-planning/milestones/induced-knowledge/evidence/close/dynamic-query-successor.json", sha256: "304db526bf83af3c2d3a2e80818e286699408d7ea348c6e4e2cf078e69e7e710"}
  - {path: "tests/test_ik_close.py", sha256: "a1741b2cefcfbd7ffef2a91b98831bd6c89ac824d6f874dc3e700bd9a5b739ee"}
---
# Milestone close: induced knowledge

**The effective plan:**
- plan r4 (`notes/induced-knowledge-plan.md`), approved 2026-10-24 (record 001).
  The plan's header still says "Draft; awaiting owner approval"; the plan is
  never edited, and record 001 holds the approval;
- amendments 004 (IK1-Q1) and 008 (IK5-Q1);
- the close spec (`notes/close-spec.md`), approved 2026-10-27 with C-D1..C-D4
  and C-G1 (its §8);
- the owner's close decisions CD1..CD5 (record 011).

**Records:**
- the phases: 002 IK1, 003 IK2, 005 IK4, 006 IK3, 007 IK5, 009 IK4-Q2,
  010 IK6;
- the IK2 repair (`evidence/IK2-repair/`);
- the gates and amendments: 001, 004, 008;
- the owner decisions at the close: 011.

## What the milestone shipped

GND can now propose rules from data, and admits none without review. Issue #34's
requests 1, 3, 4, 5 and 6 are discharged here. Request 2 shipped in PR #35.

- **Object-type descriptions (IK1).** A `description` with core keys and
  extras. It is rendered in verbalization, in the extraction vocabulary and in
  generated docstrings; carried by `gnd diff` (`gnd-diff/2`, and since the
  close, in text format too); and shown on evolve's `annotation` surface.
- **Induced provenance (IK2).** The `induced` source and its closed
  `provenance.induction` block. It is admitted only as proposed and deontic,
  and confirmed only by a reviewed status change. `gnd coverage` lists it.
- **Labelled measurement (IK3).** `gnd measure --labels` in two modes.
  Class mode reports agreement cells, each with its numerator and denominator.
- **Discovery (IK4).** `gnd discover` over the checker's own evaluation,
  with suppression, bounds and a work ceiling.
- **The ILP bridge (IK5).** `gnd export ilp`, `gnd import ilp-rules` and a
  Popper adapter. The import re-checks the learner's coverage and refuses any
  difference.
- **`gnd evolve` over reference populations (IK4-Q2).**
- **The end-to-end refunds example (IK6),** with:
  - a business tutorial that shows only skills and plain requests;
  - its runnable commands page;
  - goldens;
  - a 65-file skill census.
- **The close's ten fixes,** for IK1-Q2, IK1-Q5, IK2-Q2, IK3-Q2, IK3-Q4,
  IK5-Q3, IK5-Q4, IK5-Q6, IK4-Q2-Q2 and IK6-R1, plus the readers' fixes
  (below).

## Completion predicates (plan r4)

Verdicts from close reader one, checked against the final bytes.

| # | Verdict | Evidence and residual |
|---|---|---|
| 1 IK1 | MET WITH RESIDUAL | 002. Generated docstrings render `summary` only, not every core key (IK1 spec ruling); the predicate's wording is wider |
| 2 IK2 | MET | 003 and the IK2 repair |
| 3 IK3 | MET WITH RESIDUAL | 006. "Identical" is narrowed by the owner's C-F2 ruling (two report fields excluded from parity) |
| 4 IK4 | MET WITH RESIDUAL | 005, 009. A discover proposal for a model holding a YAML-only value (a date) fails `evolve preview` with exit 70 (IK4-Q3, carried). The exclusion family now has an emitted case and an oracle row (CD4) |
| 5 IK5 | MET WITH RESIDUAL | 007, 008. No real learner ran (D13 (a)); the learner fixtures are hand-written (IK5-Q5) |
| 6 IK6 | MET WITH RESIDUAL | 010. The walk also contains one deliberate exit 3 (the over-claim), beyond the predicate's steps |
| 7 Process | MET WITH RESIDUAL | Every phase has an approved spec, a focused gate, one reviewer, a refactoring review and a record. Residuals: IK4's gate exited 1 on the pre-existing IK4-Q5; IK2's gate missed `test_rf8_structure.py` (repaired) and `test_atom_bind.py` (repaired at this close); amendments 004 and 008 had no reviewer and retain no gate output. Close half: four readers, the sweep below, a PR; **owner acceptance pending** |

## Close review

Four independent local readers (D7), one lens each, with fresh context. All are
the same model family, so no vendor diversity is claimed. Every finding was
reproduced before it was believed. Their reports are retained in
`notes/close-reading-one..four.md`. The quoted regular expression in readings
one and two is split into two code spans, because the docs link check read it as
a link; no other byte of a report was edited.

| Reader | Blocking | Disposition |
|---|---|---|
| One (predicates) | none; IK4-C1 and IK4-C3 had no exclusion case | CD4: a successor test, and a support mutant that fails it |
| Two (ledger and consistency) | none | hardening fixed (YAML refusal labels; the census credits the close); rows corrected under CD3; leftovers carried under CD5 |
| Three (evidence and privacy) | F1: the username in seven retained paths; F2: "no learner ships" | CD1: sanitized, with digests in 011; F2: release notes reworded |
| Four (newcomer, installed wheel) | B1: the tutorial did not warn that the 0.1.0 release lacks the example and `gnd discover`; B2: `discover.md` still said evolve cannot preview a reference-bearing model, which IK4-Q2 lifted | both fixed in the pages; all ten commands-page blocks matched on the installed wheel, and every tutorial number matched the run |

**Fixed during the close, beyond C-D1:**
- the RF5 body pin of `_cmd_diff`, now a counted successor;
- `test_model_v2`'s source pin, which names the new `label=` spelling;
- `test_atom_bind`'s module scope, which had been red since IK2;
- a separator- and case-blind downstream-name check over the milestone's public
  text (reader three, F4);
- evolve's YAML refusals, which now name the model they are about;
- the census pattern;
- the scan-scope rationale;
- two lint errors left by IK6.

All of these are in `tests/test_ik_close.py` or in the tests they touch. Red
evidence is in `evidence/close/regressions-red.txt`.

## Open questions carried forward

Every row from records 002–010, the close readers' leftovers and the close's own
findings. Each has a target; none is closed silently.

| # | Question | Target |
|---|---|---|
| IK4-Q3, IK4-Q2-Q1, IK4-Q2-R1, IK4-Q2 R4 (double wrap), and tags in description extras | evolve and YAML-only values (dates; exit 70 today); strict JSON for `.json` models; one load-then-bind helper; a model with a YAML tag inside a description extra loads but cannot be evolved | one evolve-loading follow-up PR (C-D2, CD3, CD5) |
| IK1-Q4 | The runtime `__doc__` of generated tools can forge a role line through a reading, and since IK1 also through a `summary` (corrected under CD3) | codegen hardening issue |
| IK2-Q3, IK3-Q5 | Typed refusals in place of message-substring exits; merge the two measure `fail()` closures | the refactoring milestone that owns RF5 |
| IK4-Q4, IK3-Q1, plus the `gnd check` FIFO hang and `gnd export pyrel --rules duckdb` exit 70 on `pyrel-oracle/basics` | Checker and export defects, all pre-existing | GND checker/export issues |
| IK4-Q5 | `test_prepared_policy_rechecks_live_hashability` fails on main | separate maintenance |
| IK1-Q3 | Normalize `gnd_version` in T7 row 4 | the next phase that bumps the version |
| IK5-Q5, IK5-Q2, IK4Q2-D3, IK6 join space | A real Popper run, and whether its output fits the IK2 block (corrected under CD3); SWI octal escapes; the reference-bearing ILP export; the learner's join candidates have no case | ILP-bridge follow-up; the owner's call (installing Popper was declined) |
| IK6-Q1 | A packaged skill for the induction loop | its own milestone |
| Sanitization outside this milestone | 65 retained files in five earlier milestones carry the username in paths (record 011) | owner: a separate sanitization PR |
| IK1 known red | `ruff check src`: I001 in `examples/expense/project/cli/expense_cli.py` | separate maintenance |
| IK1 boundary | A description can restate a constraint, and the docs do not warn | the next docs milestone |
| Golden provenance | IK3's RF1 measure goldens captured on Python 3.14 only; IK5's 3.11 goldens derived from a 3.12 capture; IK4 F8's recapture differences not applied | the next RF1 recapture |
| IK6 H4 (minor) | A census reason holding a pipe or a back-ticked path reports `missing:` | accepted residual |
| Reader three F5 | Example ids are checked by shape only, so a value shaped like a personal identifier validates | accepted residual: IK-R11 makes ids opaque by contract, and the host owns their content |
| Reader three F6 | A hand-edited alethic induced proposal only warns at `gnd validate`; `gnd check` then treats it as hard, and evolve refuses it | IK2 follow-up |
| Amendments 004 and 008 | No retained gate output and no reviewer | accepted residual |
| Reader four hardening and completeness | `discover.md` does not name the printed suppression keys or the `ot<k>#<i>` ids; the commands page leaves ILP, deontic, covers and support unglossed; the learned rule's "0 of 4 clean" is not printed directly; `labels.json` refuses re-measurement after apply (the model changed); `gnd measure --labels` prints an empty `REDACTION applied:` header; a rerun in the same folder exits 11; apply rewrites the model as one-line JSON, dropping comments; `gnd --version` reports 0.1.0 for development builds | the next docs milestone; the empty header, the JSON rewrite and the version string as GND issues |

**Accepted residuals (C-D3):**
- IK2-Q5: the pre-existing `orm-meta` patterns accept a trailing newline;
  fixing them would break IK-R3;
- IK3-Q3: a rule-free model cannot be measured in expected-state mode, which
  `measure-labels.md` now says.

**Closed during the milestone:**
- IK1-Q1 (004), IK2-Q1, IK2-Q4, IK4-Q1, IK4-Q2 (009), IK5-Q1 (008), C-F7;
- the IK2-D5 single-token residual (IK2 spec §13);
- the 60–64-level evolve window (IK4 spec §18);
- the IK3 directory-as-manifest case. The IK3 review saw exit 66; since IK3's
  R1 fix it is exit 3, "not a regular file".

**Closed at the close:** the ten C-D1 rows, IK3-Q3's sentence, CD4, and the
reader fixes above.

## Corrections to earlier records

Earlier records are not edited; this record carries the corrections.
- **Record 007:** it calls the IK5 corpus both "43-case" and "40-case". The
  corpus has 40 cases and 43 tests (reader three, F7).
- **Close spec r1:**
  - its header ("Draft … nothing implemented") and §7 ("none yet") describe
    the bytes before the gate. The fixes' findings were logged in an appended
    §9 instead, because §7 and §8 were append-only after the gate;
  - §8's phrase "5283590 plus the IK4Q2-D3 row" names exactly the bytes
    whose SHA-256 it states;
  - §2's binding counts predate the close's own edits;
  - §9's F2 quoted "count the reloads in the work counter" as the ruling. The
    owner's words were "approve … as proposed"; CD2 ratified the bound
    explicitly.
- **IK1-Q4 and IK5-Q5 rows:** worded as CD3 corrected them.

## Refuted premises

- **"The D-03 table has one code home" (IK2-Q2).** Its one home is prose. The
  code is table-driven and pinned to that prose by a test (close spec §9, F1).
- **"Invalid candidate YAML has one parse site" (IK4-Q2-Q2).** There were three
  (F3).
- **"The phase gates covered every affected test."** The full default-lane suite
  found `test_atom_bind.py`, red since IK2, which no phase gate had selected.

## Refactoring review

**Refactors executed at the close, each behaviour-preserving and behind the
gates:**
- the D-03 default in `rai_import` is table-driven (IK2-Q2);
- the RF6 and RF7 scans share one exemption rule for `src/gnd/examples/**`,
  tied to the layer map (`tests/support/scan_scope.py`, IK6-R1). The close RF6
  successor removes 84 example rows and adds 6;
- the runner owns the run-directory normalization (`without_run_dir`), which
  the walk test now uses.

**Seen, deferred:**
- IK2-Q3 and IK3-Q5, with RF5;
- the evolve load helper, with the evolve-loading PR.

## Boundary

- **Owner acceptance is pending.** Neither the readers, the gate nor this record
  is acceptance.
- **No real learner has run.** The stand-in is not Popper.
- **The readers are one model family, run locally;** each is one reading.
- **History.** Main's history keeps the unsanitized bytes of the seven files in
  011.
- **Earlier phase records hash their own phase's bytes.** This record and 011
  describe the merged bytes.
- **No merge, release, publication or certification** is implied.
