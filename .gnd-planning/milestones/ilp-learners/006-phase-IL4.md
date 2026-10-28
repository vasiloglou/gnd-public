---
milestone: ilp-learners
station: phase-IL4
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL4
date: 2026-10-28
gate:
  command: "uv run pytest -q -p no:randomly <the IL4 file list, evidence/IL4/gate-files.txt>"
  exit: 0
  output: "1038 passed, 24 deselected in 174.87s (0:02:54)"
  note: >-
    The literal gate of spec §8: IL3's gate files plus tests/test_ilp_amie.py
    (T1 to T13, T9, the oracle, the step 4 regressions). The live lane ran
    separately against the scratch jar: 1 passed (before the step 4 fixes;
    the later change to its comparison is a refactor onto ilp_amie.canonical,
    not re-run, since each run starts AMIE). The RF1 pins ran under Python
    3.11.15, 3.13.12 and 3.14.3: 154 passed each, before the step 4 fixes,
    which changed no CLI surface. Ruff clean on the changed files.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL4's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL4-spec.md
    sha256: d0533394dbd3838527dc669e7dd87a0ba580523ffccafcd6f49c2965129b0d51
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL4-agent-review.md
    sha256: 5810dc10f66b667f629687a0f4648eccc034a040fe42970a5fbcbd9d958ad080
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/gate-files.txt
    sha256: 6e58be18a7f01a067aaf07b068719d536012fd7b1c294968fd7b5b32f22a0204
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/final-gate.txt
    sha256: 0fca1cf55d74733f562e4e829a3e57334064235cada69f1dfa1369089c9166b2
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/review-brief.md
    sha256: 8c910898212c76d5e845758da66753fd171f181dac525784695e6ecbee23497c
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/run_amie.py
    sha256: 5475fc7a08f1edb416b4a79aad868ed2086d61b53b1255fac26c52d23e32097e
  - path: .gnd-planning/milestones/ilp-learners/evidence/live_common.py
    sha256: f4f403020a5b1832222e3f172f05877684d0438383891a54a93b6d7f303ca84c
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/downloads.json
    sha256: 0c01c595abdc4949ddcca59e8b6dbf76f752c710bb06918679bc619ca871edf4
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/dynamic-query-successor.json
    sha256: e00c868a957ee39b93fd08ae08b92a728b4e675e844fbd4e860a3102b9c01bac
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/help.txt
    sha256: 768d8247063a5cb05b2efeea8a9bd4255b7ee4f90f281835561c2c7bfbb1933b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/invocation.json
    sha256: 5c84e3016d9620eb386186bd18cfbea4e5b5bb9f6b6ce95f0e8226fbf6ca9dfc
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/probe.json
    sha256: eff07a1a20b51098802510d499db119ba290e77b33b9f6c599d6635e42a9ae9e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/raw-stderr.txt
    sha256: b21485308e3b8807beefa9c69570e15989467845678009609e4d6be079245613
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/raw-stdout.txt
    sha256: 2eb98773d81b9dca2d3060a9ee733f30d1716e6154bc0aa2f7a84b30bc934cc2
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/probe/toy.tsv
    sha256: 54867501618678176d777d859d1d41c073ad02c551ca3aabc1600bc5a223d663
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/facts.tsv
    sha256: fa9abba9fe0e7eb6b6e84e43bf8fab1a5d6b053a29987730322600ebf663b867
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/import-stderr.txt
    sha256: 480817fc248897597e398a3de08e25e46252f627c179dcda40f60472cec74a86
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/invocation.json
    sha256: d0b00a54789d53cefc8537dc63c9b9b08a1733eda5d44ef0ce6855b5e1900cc1
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/outcome.json
    sha256: a329207c360a398956eb1602e41e3b9ea4a5b601a09bbf8c6de5f1d940e59c09
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/raw-stderr.txt
    sha256: b87c23fb66669e382b3b35f6a55c25454e71d900da56fba9c9e8880536d2ecd9
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/raw-stdout.txt
    sha256: 6c83b9edc8a5377f490b515a270f1ca72bb82b7be52c048915bf71d9db5e8a12
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/reported.json
    sha256: 365eda612c7b62ce1e579c21533fb4793ad93ea2c9d35a2bb5d8497a94eca8c3
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/rules.txt
    sha256: cbe40fe6018aad4f79d240994b67d86dac5f9f0ca62b9cd391d0253bbbab7f59
  - path: tests/fixtures/ilp_learners/il4/model.orm.yaml
    sha256: fe3857c96fc16d01d38526a4aedc89de52158f3b1a01e305ffbc6f201a2770aa
  - path: tests/fixtures/ilp_learners/il4/population.yaml
    sha256: dfbfee12d84a102392b44cb7f8f25e8cd67a6afab417dbd3b5a0a636bbe11e9a
  - path: tests/fixtures/ilp_learners/il4/rules.json
    sha256: 71c442ce16f9ba9f9291ce1e81182799ca402f31958ab945bf2723fe6ba747fe
  - path: tests/fixtures/ilp_learners/il4/expected/north/export.json
    sha256: 1ad8d2aa8c9c748dd7859c41747251dc60c9d587eee2f3f09951c3c273aa15c6
  - path: tests/fixtures/ilp_learners/il4/expected/north/facts.tsv
    sha256: feafc61d604deb9b159fcdca58219008b8abcaf00778a603f0e3beb98c47d935
  - path: tests/fixtures/ilp_learners/il4/expected/north/relations.json
    sha256: 7033307136fddd759edf90be16d3d029e984af6218ef017d4ab443fa0c7aa65b
  - path: tests/fixtures/ilp_learners/il4/expected/staffing/export.json
    sha256: d7756509f96fd4b9e4449b53a004fb77d5f1a831378a958c5e1122958ca435f3
  - path: tests/fixtures/ilp_learners/il4/expected/staffing/facts.tsv
    sha256: fa9abba9fe0e7eb6b6e84e43bf8fab1a5d6b053a29987730322600ebf663b867
  - path: tests/fixtures/ilp_learners/il4/expected/staffing/relations.json
    sha256: 8b156b92f3f04d6301ceb668bb4003ac3328ea44bcbb2899b2330e44e762f236
---

# Phase IL4 — AMIE-style miner: typed triples out, mined Horn rules back, one AMIE run

Spec r1, approved by the owner 2026-10-28 ("go with your recs", §13):
AMIE 4.0.0, its CC-BY licences accepted, the synthetic staffing fixture as the
run's input. PR #60 merged at `70266b5` before any code.

## What shipped

- **`gnd export ilp --target amie MODEL --population POP --out DIR`**
  (`src/gnd/export/ilp_amie.py`): one relation `f_<fact type>` per binary
  asserted fact type the population covers, values spelled
  `<object type>:<value>`, sorted and deduplicated into `amie/facts.tsv`;
  `amie/relations.json` holds the population digest, the relations and every
  skipped fact type with its reason (IL4-F3). The target decides which input
  is required, in a post-parse check that exits 64 (IL4-C5).
- **`gnd import mined-rules MODEL RULES --population POP --reported RUN
  --target amie --out PROPOSAL`**: a closed, capped reader of AMIE 4.0.0's
  rule lines; a mapping to `guarded` constraints with an `atom` consequent,
  refusing eight shapes by name in a fixed order; GND's own count over
  distinct head pairs; holds-only, all-or-nothing admission; a checker
  cross-check; the proposal through `discover.output`, with `gnd discover`'s
  provenance and opaque fact ids. The run record is `gnd-mined-run/1`
  (IL4-F2), the report `gnd-mined-import/1`, both in
  `src/gnd/mined-import.schema.json`.
- **Registry:** `amie` (`unlabelled-horn`), `MINED_TARGETS`; the export
  enum; the layer map; the inventories; the RF6 delta.
- **Shared code:** `ilp.index_tree` split from `export_tree`;
  `ilp.refusal_name` reads `rule K:` (IL4-F9); `live_common.run_import`
  takes a phase's own fixture.
- **RF1:** `gnd export ilp`'s help and exit back to one golden per lane,
  `gnd import`'s moved, `gnd import mined-rules`'s new, `cli/tree.json`, the
  manifest and its digest (IL4-F7).
- **Docs:** `ilp-bridge.md` "AMIE-style miner": the commands, the export,
  the reader, the run record, the mapping table, the counting, every
  refusal, the bounds.
- **Corpus and tests:** the staffing fixture and `rules.json` (20 reader and
  15 import cases, committed red at `29e850b`), `tests/test_ilp_amie.py`.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL4/gate-files.txt)
1038 passed, 24 deselected in 174.87s (0:02:54)
```

Exit 0. Also run: the live lane (1 passed), the RF1 pins under 3.11, 3.13
and 3.14 (154 passed each), ruff on the changed files (clean). The full
`uv run pytest -q` was not run.

## The run of record

Invocation 1, `evidence/IL4/live/invocation-1/`, replayed by T9:
`termination: completed`, `import: refused:does-not-hold`, exactly as
stated before the run (IL4-F8). AMIE 4.0.0 (the verified asset; AMIE prints
no version), OpenJDK 21.0.10, argv `java -Xmx2G -jar amie4.0.0.jar -maxad 3
-mins 1 amie/facts.tsv`, 18 threads, 0.044 s of mining. It printed 8 rules;
every Support equals GND's numerator; two hold (the planted
`works_in, team_site => based_at`, 20/20, and
`based_at, works_in => team_site`, 5/5); six do not, among them the
near-miss (19/20) and two rules AMIE's PCA confidence passed at 0.54 and
0.56 that hold on 19 of 35 and 20 of 36 head pairs. The import refused the
whole set at rule 0, as all-or-nothing is ruled. Per-rule counts in the
spec, §14. The outcome's `import` field was re-derived once from the
retained stderr (IL4-F9); AMIE was not run again for it.

Before the run: the probe on the toy TSV (by hand three times, then once
by the script, IL4-D10). After it: T-live ran AMIE 5 times over the
committed facts while IL4-F10 was diagnosed; none is an invocation.
"Single run, reproducibility not measured."

## Criteria

| Criterion | Holds | By |
|---|---|---|
| IL4-C1: the typed triple export equals a committed golden across two hash seeds | yes | T1 (staffing and a refunds batch, two seeds), T1 skipped, schema, spelling and no-relations cases |
| IL4-C2: a mined rule maps to a schema-valid guarded constraint with an atom consequent; constants, recursion and the other shapes refused per the table, each with a test | yes | T3 corpus a1, a2, m1–m8; R1 (`disconnected-body`); T6 (`gnd evolve preview` exit 0) |
| IL4-C3: GND's numerator, denominator and confidence match a brute-force oracle; `support-mismatch`, `covers-nothing`, `open-world-head`, `type-confused-join` and `does-not-hold` each tested | yes | T4 (fixture and 300 random populations), T5 c1–c5, m1, m8, T6b |
| IL4-C4: one live run under IL-R9, JVM and miner versions recorded, replayed | yes | invocation 1; T9; T-live |
| IL4-C5: the post-parse check exits 64; popper and neutral without `--labels` give the same stderr as before | yes, for `--labels` alone missing | T7; review 6 (several missing arguments) in the boundary |

## Review

One reviewer is one reviewer: one local agent read `git diff 70266b5
f6ded68`. Its report is retained in `notes/phase-IL4-agent-review.md` with
the reproduction and triage. All 7 findings were reproduced:
- **1 blocking, fixed:** a holding rule whose body falls apart reached the
  exit-70 checker disagreement; now refused `disconnected-body`.
- **3 hardening:** duplicates up to renaming, fixed; subtype joins
  (IL4-Q1) and the unbound model (IL4-Q2) deferred and documented.
- **3 completeness:** the non-printable message, fixed; the multi-missing
  CLI messages, accepted; test gaps, closed.

Each fix has a regression, red before it (`test_r1`, `test_r3`, `test_r5`;
`test_r7` and T9's learner check close gaps and could not be red). The
reviewer did not run AMIE, the script or the full suite.

**Coverage audit against the declared branches:**
- **reader:** every refusal by a corpus case (u1–u16) and T10's caps at and
  one over the bound; R3 for duplicates.
- **mapping:** each of the eight rows by a case (m1–m8, R1), in order.
- **counting and admission:** each of the four refusals (T5, `test_t5_the_join_bound…`).
- **inputs:** `learner-mismatch`, `rules-mismatch`, `population-mismatch` (T5).
- **export:** `no-relations` and `unrepresentable` (T1).
- **termination:** `completed` by the run, the rest by the shared helper's
  IL3 tests; `learner-timeout` unreachable (no AMIE timeout, IL4-F4).
- **import:** `refused:<name>` by the run and T5; `admitted` by T6 and the
  admitted corpus cases (not by the run); `none` by the extractor's empty
  case. The checker-disagreement exit 70 is now unreachable from input.

## Refactoring review

**Refactors executed:**
- **`ilp.index_tree`** split from `export_tree`, so the AMIE tree reuses the
  one index builder; every other target's goldens are unchanged.
- **`ilp_amie.canonical`** is the one definition of rule equivalence, used by
  the reader's duplicate check and by T-live (review 3).
- **`live_common.run_import`** takes a fixture directory, so IL4 reuses the
  ruled import step; IL3's calls are unchanged.

**Seen and deferred:**
- **`ilp_amie` uses `ilp._value`,** a private name, as IL3 uses
  `ilp_popper._threshold_rows`. Grouped with IL3-Q2 (IL4-Q3, close).
- **`_cmd_import_mined_rules` is about 150 lines** in `ilp_service`. Moving
  the per-rule provenance into `ilp_amie` would shorten it, but would move
  this phase's RF6 rows again. IL4-Q3, close.

## Boundary — what this phase does NOT establish

- **An admitted live result.** The ruled argv filters on PCA confidence
  only, so AMIE prints rules that do not hold and the set is refused.
  Admission is shown by the corpus (T6), not by the run (IL4-F8).
- **Subtype joins.** A join through a subtype is spelled with two prefixes,
  so GND counts it as never holding while the checker passes it: a false
  refusal, never a false admission (IL4-Q1).
- **Binding to the model.** The run record binds the rules and the
  population, not the model (IL4-Q2).
- **The CLI message when several arguments are missing.** Exit 64 is
  unchanged; argparse's combined list no longer names `--labels` (review 6).
- **Body-size comparison.** AMIE 4 computes it only with `-enstd`, which the
  ruled argv does not set, so it is never reported in the run (IL4-F4).
- **AMIE's determinism.** Rule order and variable names vary by run
  (IL4-F4, IL4-F10); the rules and figures matched once.
- **`learner-timeout`** is unreachable: AMIE has no timeout option.

## Open questions

| Id | Question | Owner | Target |
|---|---|---|---|
| IL4-Q1 | Review 2: spell entities by a shared root type so a subtype join counts as the checker does, or refuse subtype joins by name? Needs a rule for multiple supertypes. | owner | close |
| IL4-Q2 | Review 4: bind the export digest in `gnd-mined-run/1`? It changes the run record after the run of record, whose retained `reported.json` would then need re-deriving. | owner | close |
| IL4-Q3 | Make `ilp._value` public and move the per-rule provenance into `ilp_amie` (with IL3-Q2). | author | close |
| IL4-Q4 | A second invocation with `-enstd -minc 1` (filter on standard confidence 1) would show an admitted live result. Run it? | owner | IL6 |
| IL4-Q5 | The plan's "refunds through every adapter" (IL6) and §6's "positive examples" wording: repair at close (IL4-D4 (o), IL4-F4). | owner | close |
| IL1-Q1 | Re-targeted to close (IL4-D9 (o)): AMIE rules carry no comparisons. | owner | close |

## Refuted premises

1. **"AMIE prints positive examples and a body size"** (spec §6). It prints
   `Support`, and a body size only with `-enstd` (IL4-F4).
2. **"`export.json` can carry the population digest"** (spec §6); it is
   closed (IL4-F3).
3. **"The mapping table covers every shape the checker evaluates"**: a
   disconnected body passed it (review 1).
4. **"The shared outcome mapping reads every import's refusal"**: it did
   not read `rule K:` (IL4-F9).
5. **"On the fixture, the planted rule should be mined and admitted"** (spec
   §6, expected result): mined, but refused with the set, because AMIE's
   default filters let non-holding rules through (IL4-F8).
