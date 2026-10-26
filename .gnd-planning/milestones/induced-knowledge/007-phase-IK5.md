---
milestone: induced-knowledge
station: phase-IK5
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK5
date: 2026-10-26
gate:
  command: "uv run pytest -q -p no:randomly <the IK5 file list, evidence/IK5/gate-files.txt>"
  exit: 0
  output: "4473 passed, 105 deselected in 585.85s (0:09:45)"
  note: >-
    Direct IK5 tests (tests/test_ilp_bridge.py: the approved 43-case corpus,
    the implementation tests T3, T5, T9, T10, T12 and C-F1, and the review
    regressions) plus the impact closure: every tests/test_rf*.py,
    test_gnd_arch.py, test_measure_labels.py, every discover test, every test
    naming the export or import commands, rai-orm, the schema inventories, the
    docs pages and nav, and the skill files. 94 files, each checked to exist.
    test_incremental_performance.py is excluded (IK4-Q5, red on main).
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK5's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/gate-files.txt
    sha256: 29495291441e144b8d487eff7f43e31a16e2eef184a7342f76965576f887ef71
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/final-gate.txt
    sha256: aca200eee2b04b000e2e80c006fee3233f815e3a4fd3442d4141e96b68154bba
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/corpus-red.txt
    sha256: c03e1db05d1555072d9db04c095918f8faa42ebb19e460d7ad9c74717b85d52b
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/regressions-red.txt
    sha256: 9934be82998d22823e12d1957784465f0652c4bfaa6103111adf3fdd49aa2056
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/mutants.txt
    sha256: 933491d072025fe039623b15ec59e0d6cbe8d7672e320b5bea12512a6b1f7d0f
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/review-brief.md
    sha256: 4cc1de38f9f3a8a56018efc2ea1237d325415f2e5e84dfd49ac471bc7595ad30
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/build_ik5_corpus.py
    sha256: 310433f8537ac133d3075831e09605407482739e576efbe3d82c7e6722c00e4b
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/build_dynamic_successor.py
    sha256: ed644942c01dcde93eb2391a2aeda37dddc8d3ddaadd714dd39a29c8cd6ed402
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK5/dynamic-query-successor.json
    sha256: f23a2c5af224dc37f4838ff63bcd5963a306328f482362f9780205678cca424d
  - path: tests/fixtures/induced_knowledge/ik5-corpus/cases.json
    sha256: 2f2278c95cbdc5b9120953d824741855b95159653155d4040afca529f12b4b2f
  - path: tests/fixtures/induced_knowledge/ik5-corpus/expected.json
    sha256: 663207ed6249a8a47a486a69d2a8111998acf81071db9c4670dce91d55fe92ca
  - path: tests/fixtures/induced_knowledge/ik5-corpus/README.md
    sha256: ea041ea2f555c1f7f71b398ae0f6d13f86898fd44f9aaf29ed78ff39850b8143
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK5-agent-review.md
    sha256: da104e4bef2e381fbf55030a72daba3833dc45332758bafbf4aa624134e7d144
---

# Phase IK5 — the ILP bridge

**Claim.** IK5-C1 to C4 hold on the evidence below, under:
- the owner rulings in spec §13 (IK5-D1..D15, with D13 option (a));
- the corpus approval in spec §15 (C-F1..C-F6).

The bridge has two commands:
- **`gnd export ilp`** writes the learner-neutral form and its Popper rendering,
  reproducible as one export digest;
- **`gnd import ilp-rules`** admits learned clauses only as induced, proposed,
  deontic `guarded` constraints, and only when GND's covered example-id set
  equals the learner's for every clause.

**No learner ran.** The learner fixtures are hand-authored in Popper's printed
syntax (D13 (a)).

## What shipped

- **Export:** `gnd.export.ilp`, the neutral form `gnd-ilp/1`.
  - Modes come from fact-type roles, through `ModelIndex`. Examples are the
    populations of a class-mode IK3 manifest, and `wrong/1` covers `negative`.
  - Refusals by name: `expected-state`, `opaque`, `unrepresentable`,
    `redacted`, `primitive`, `name`, `too-large`, `references`.
  - `export.json` indexes every file, and its SHA-256 is the export digest E.
    `--target neutral` writes the neutral form alone (C-F2).
- **Popper adapter:** `gnd.export.ilp_popper`.
  - The rendering is `bk.pl`, `exs.pl` and `bias.pl`.
  - A closed, bounded tokenizer and parser reads Popper's printed program into
    `gnd-ilp-clauses/1`. Negation, disjunction and aggregates are parsed so that
    they are refused by name.
- **Rewriter:** `gnd.export.ilp_rewrite` runs fragment checks 1–9 in the
  contract's order, with 16 refusal names, then body rewriting into one
  top-level `guarded`.
- **Service:** `gnd.export.ilp_service` runs both commands.
  - The import checks bindings first: clause digest, then E recomputed from the
    same inputs, then learner, then coverage shape.
  - Check 10 is the model validator.
  - Re-evaluation runs one checker pass per distinct population. `warning` is
    covered; `pass`, `vacuous` and `unchecked` are not, and the last two are
    listed.
  - It then compares sets per clause, refuses `covers-nothing`, and computes the
    IK2 block: precision-shaped support, examples and counterexamples, and three
    evidence digests.
  - Admission is all-or-nothing, and the proposal is written with an exclusive
    create.
- **Shared code:**
  - IK3's per-population read is now `labels.read_population`;
  - IK4's proposal builder gained `add_operations` and keyword `origin`, `prefix`
    and `rationale`.
- **Wire formats:** four closed schemas, `ilp`, `ilp-clauses`, `ilp-run` and
  `ilp-import`.
- **Registration:**
  - the CLI: the `export ilp` target and the `import ilp-rules` subcommand;
  - layer map entries and the RF5 service binding for both command modules;
  - RF1 goldens for the export and import subtrees, keyed by Python minor where
    argparse wraps differently (I-F7);
  - the RF6 census delta and both schema inventories;
  - the contract page `docs/reference/ilp-bridge.md`, which is the fragment
    table's one home, plus CLI and capability rows, a nav entry and two skill
    lines.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly <IK5 file list; evidence/IK5/gate-files.txt>
4473 passed, 105 deselected in 585.85s (0:09:45)
$ uv run ruff check <changed .py files>
All checks passed!
```

Also run during the phase:
- **Corpus:** committed red at `d0cb831` (41 failed, 2 passed by design). All 43
  corpus tests pass on the implementation, unchanged.
- **Review regressions:** all eleven fail on a copy of `abc872a`'s `src` and pass
  after the fixes. The R5 and R6-import tests are coverage: they pass on both.
- **Mutation:** the reviewer's 17 meaning and format mutants all survived
  coverage before the R5 tests. All 17 are now killed.
- **RF1 goldens:** captured on Python 3.12, 3.13 and 3.14. The 3.11 keys are the
  3.12 capture, because 3.11 is not installed (I-F7).

## Criteria

| Criterion | Result | Tests |
|---|---|---|
| C1 | met | X1 and X2 against hand-written expected files; D1 under `PYTHONHASHSEED` 0 and 1; T5 schema validity of every written file; modes from roles; examples from the IK3 manifest |
| C2 | met | F01–F20 (every refusal name, with the four plan constructs in both forms), I1, I2, T5, T8, R5 (each operator and spelling), R8; I3 previews at exit 0; no `derivation_rule` |
| C3 | met | I1 and I2 admitted; M1 (equal counts, different sets) and M2 (a vacuous-only difference) refused as `coverage-mismatch`; M3 and M4 |
| C4 | met | B1–B5 (export, clauses, learner and shape bindings); the live learner is not a lane (D12). Fixtures are hand-authored (D13 (a)) |

No bound was moved after implementation. The inconsistency the review found in
the bounds is recorded as IK5-Q1, unchanged.

## Adversarial review

One local reviewer agent read `git diff d0cb831 abc872a`. **One reviewer is one
reviewer.**

**On meaning preservation:** it compared 40 learned clauses with an independent
Prolog-semantics oracle. Every admitted clause matched, and every disagreement
was a refusal.

**What it found:**
- **Blocking, fixed:** three tracebacks.
  - R1: nested aggregates;
  - R2: an integer over 4,300 digits;
  - R3: a lone surrogate.
- **Hardening, fixed:** R4, a constant such as NEL that the import admitted but
  evolve's YAML reader reads differently.
- **Partly fixed:** R6, the work counters. Real reads are now counted and the
  export prints its work. The bound inconsistency is IK5-Q1.
- **Completeness:**
  - R5: mutants survived. Fixed with tests.
  - R7: hex escapes did not read back. Fixed; octal escapes are IK5-Q2.
  - R8: `_` was treated as ground. Fixed.
  - R9: aggregate naming. Deferred as IK5-Q3.

The report is retained, with its disposition, in
[phase-IK5-agent-review.md](notes/phase-IK5-agent-review.md). It is set as
markdown and is not a byte copy, as the note says.

## Refactoring review

**Refactors EXECUTED:**
- **One population reader.** `labels.read_population` is IK3's read, extracted
  and now shared by `score_populations` and the export. IK3's 76 tests pass
  unchanged.
- **One proposal builder.** IK4's `operations` and `proposal` are generalized by
  keyword, not copied, so discover and the import both go through evolve's one
  replay. IK4's 65 tests pass unchanged.
- **One predicate table.** `ilp.schema` returns the neutral predicates and the
  `Column` table from one walk. The rewriter reads the columns, so it never
  re-reads model roles or neutral dicts (I-F3).
- **One verdict index per report.** This replaced a scan per (population,
  clause) (review R6).

**Seen but deferred:**
- **IK5-Q4:** `discover.output.candidate_text` writes characters that YAML does
  not keep. IK5 refuses them at its own boundary; discover's own path is
  unchanged.
- **IK5-Q6:** check 10 reloads the candidate model once per clause. The cost is
  bounded by K ≤ 32, but no counter records it.
- **IK3-Q5,** carried.

## Boundary — what this phase does NOT establish

- One reviewer is one reviewer; the broad lanes were not run (`slow_cadence`).
- **No real learner ran (D13 (a)).** Whether a real Popper accepts the rendering
  is untested; the reviewer named `type(wrong,(ex,))` and the missing
  `direction` declarations as places to check first. Whether real Popper output
  fits the IK2 block is also untested. The IK2 residual is discharged only for
  blocks GND computes itself.
- **Coverage agreement is necessary, not sufficient.** Rules that agree on the
  labelled examples can disagree on unseen populations. Owner review through
  evolve decides.
- **The export writes raw population values** for non-redacted roles into the
  learner's input. That is a host-side file, not induction evidence (IK-R11).
- **What the export and import refuse:**
  - Integer comparisons only.
  - Value types other than Integer, String and Boolean are refused, as are
    models with reference populations.
  - String constants holding non-printable characters are refused
    (`constant-spelling`).
  - Octal-escaped Popper output is unparsable (IK5-Q2).
- **The RF1 3.11 goldens** were derived from a 3.12 capture, not run on 3.11.
- **Inherited:**
  - IK3-Q2 (case-insensitive file systems);
  - IK4-Q2 (evolve cannot preview reference-bearing models);
  - IK4-Q5 (a pre-existing red test).

## Open questions

| ID | Question | Target |
|---|---|---|
| IK5-Q1 | The IK5-D14 bounds disagree. 1,000,000 facts cannot fit under the 64 MiB per-file cap (the smallest fact entry is 97 bytes), so the facts bound is unreachable and the file cap refuses first at about 690,000 facts. Lower the facts bound or raise the file cap | owner ruling (IK-R12), before IK6 |
| IK5-Q2 | Read SWI's octal escapes (`\001\`) in Popper text | milestone close |
| IK5-Q3 | Aggregates whose goal is a conjunction, a negation or a comparison are named `unparsable`, not `aggregate` (still exit 3) | milestone close |
| IK5-Q4 | `discover.output.candidate_text` writes YAML-unkept characters verbatim (pre-existing IK4 code) | milestone close |
| IK5-Q5 | A real Popper run, to test the rendering and the IK2 block's fit (D13 (b)) | owner's call; IK6 or later |
| IK5-Q6 | Count check 10's candidate reloads in the work counter | milestone close |

## Refuted premises

- **"The tests pin the rewrite" (spec §8 branch walk).** As first written, 13 of
  17 meaning and format mutants survived. They are all killed now (R5).
- **"The bounds are consistent" (IK5-D14).** The facts bound is unreachable
  under the file cap (IK5-Q1).
- **"Fact type ids need an ILP-safe name check" (spec §6).** The model schema
  already restricts them; only length remains (I-F2).

## Size

The spec estimated about 1,100 source lines, 250 schema lines and 900 test
lines. Measured at record time:
- 1,177 source lines in `src/gnd/export/ilp*.py`, plus 359 lines across the
  touched commands, the shared modules, the docs and the skills;
- 841 lines of schemas (written expanded, so above the estimate);
- 640 test lines, plus the 40-case corpus.
