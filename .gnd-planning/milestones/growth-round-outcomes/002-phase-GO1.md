---
milestone: growth-round-outcomes
station: "phase-GO1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GO1
date: 2026-11-23
gate:
  command: "uv run pytest -q tests/test_go1_evolve_parse_once.py tests/test_evolve_additive_policy.py tests/test_evolve_source_document.py tests/test_evolve_loading.py tests/test_mc3_evolution.py tests/test_unattended_model_growth_acceptance.py tests/test_evolve_population_check.py tests/test_evolve_shape_matches.py --tb=short"
  exit: 0
  output: "443 passed, 1 deselected in 59.72s"
  base: "2814d9be (plan gate; src, tests and docs equal to main 11a7ebf7)"
gates:
  - {name: "structure and inventory guards (project.md block)", command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short", exit: 0, output: "679 passed, 2 deselected in 133.05s (0:02:13)"}
  - {name: "lint, plan form", command: "uv run ruff check src tests tools", exit: 0, output: "All checks passed!"}
  - {name: "lint, whole repository", command: "uv run ruff check", exit: 0, output: "All checks passed!"}
  - {name: "component index", command: "python3 scripts/components_index.py changed --base origin/main --strict", exit: 0, output: "41 file(s) differ; 0 to fix, 0 warning(s), 4 to reread"}
  - {name: "T8, GO1-C5 (slow lane, recorded)", command: "uv run pytest -q -s -m slow tests/test_go1_evolve_parse_once.py -k t8", exit: 0, output: "1 passed, 19 deselected in 27.68s; ratio 0.31"}
selection:
  - {obligation: "GO1-C1..C4, T1-T7", disposition: run, command: "the gate above"}
  - {obligation: "T9 the existing evolve lane, with the write check on", disposition: run, command: "the gate above"}
  - {obligation: "GO1-C5 T8", disposition: run, note: "slow lane, once, on 84c8df0b; ratio 0.31 against the bound 0.6"}
  - {obligation: "GO1-C6 the round sweep", disposition: run, note: "evidence/GO1/round-sweep.json, base main 11a7ebf7 against head 84c8df0b"}
  - {obligation: "broad lanes (evidence, census), report-golden replay, certification", disposition: cadence, note: "not selected: no explicit owner request"}
evidence:
  - {path: src/gnd/model/_parsing.py, sha256: f63f23d77f51534d0def02b92f2b1dd3c7b8f3b9083f9a856176d6300db26a8d}
  - {path: src/gnd/commands/evolve.py, sha256: 106a045fa89a4439e279b166cf197146fa52e9b8b1330b7186045bb4f5e4874d}
  - {path: src/gnd/evolve/cli_service.py, sha256: a1145e7fcee18e93bc59433438117060c4a647eeb00ba1f2f0cb53495cc01835}
  - {path: src/gnd/evolve/service.py, sha256: 8662e9368bfccc009ced7f86b6dfd1096c901bf11b72c589f56061a7975c2873}
  - {path: tests/test_go1_evolve_parse_once.py, sha256: d522720a36411349fec9917148165eeb73055dde95ac66535e4f92b8a9630e81}
  - {path: tests/conftest.py, sha256: f18fedd4c10f45a4717095c353aab3a4529b51b50a0737ac9f635c5817048249}
  - {path: docs/release-notes.md, sha256: fcc11c43e444fbb43c5f5b6f3f1a2687c44bc55f3c6f3cf15e6bbc8d60b5fbe5}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO1-spec.md, sha256: 240ea2136cfee19432566f04c1b14bb25739f6f761cd9fdf60f19976ac37af89}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO1-r1/review.md, sha256: c310a9b4a69e3d6b56231b2a8589213b9b33bc7d44a0f73758c08795e9f76e9f}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO1-r1/FINDINGS.md, sha256: d87e7627ab4354510c293510eeaea8e457dbd5ac941fcad74a3bddfe9e993fe1}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO1/round-sweep.json, sha256: 57ef45c6fb0cc13c14cd6f9606b1b04d6f595e4d77bb4897e072e76888aa6099}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO1/round_sweep.py, sha256: 57b00f7b7f1b1abf2b97141860903ea3ad8cad38736fa221e012d746e97ef88b}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO1/t8-ratio.json, sha256: 2cbccc71258381561ae442900477baa3c912ba13c3234a5e7ee00b831b4f57c6}
---

# Claim

One `gnd evolve preview` or `gnd evolve apply` now parses each model text
once per reader (#228). A parse scope in `gnd.model._parsing` remembers each
parsed document for one command. It is keyed by the sha256 of the bytes and
by whether the source name selects the strict JSON reader, and the document
is shared without a copy. The scope opens on the evolve command dispatcher
(`gnd.commands.evolve.handle`) and on the three service methods. On the
round fixture `apply` parses 2 times, where it parsed 22, and `preview` 2,
where it parsed 6. With the scope switched on and off, every exit, stream
and written file is equal for seven cases. Tests switch on a write check of
every remembered document; the existing evolve lane passes with it.

Authority: plan r4, delegated approval (auto=true) in `001-plan-gate.md`;
spec r3, delegated approval (auto=true), sha256 `601e8f46…ddcb0`, spec §12.
These are agent rulings under the owner's delegation for this milestone,
not the owner's reading. Ordering: the coordinating session answered
"READY GO1" with "GO GO1". Not merged; merge needs the owner.

## Named criteria

| Criterion | Result |
|---|---|
| GO1-C1 parse count | T1: with the scope, `preview` 2 and `apply` 2 at N = 10 and N = 40 (34 and 124 object types); without it 6 and 22. The `.json` workspace stays within 2 and 3, and its scope-off counts are larger. Gate |
| GO1-C2 same bytes | T2 over seven cases (one round, policy refusal, D-12 refusal, include root, `.json` model, YAML date, candidate not YAML) and T4: exits, stdout, stderr and every file of the workspace equal with the scope on and off. Gate |
| GO1-C3 no write | T3: the write check at every scope close over the whole GO1 lane (autouse fixture); liveness cases for a write through a loaded `Model`, `1` to `True`, a tag change and a key-type change; no false positive on dates, NaN, tags, binary, sets, anchors. Gate |
| GO1-C4 stale and fresh | T4 refusal as today; T6 nested and ended scopes; T7 a second command parses again; T6-r1 a copied context after close. Gate |
| GO1-C5 ratio | 0.31 at 604 object types (bound 0.6), recorded; slow lane |
| GO1-C6 sweep | the table below |

## The #228 table at the head (GO1-C6)

CLI wall seconds, one run per cell, one laptop under other load, base `main`
`11a7ebf7` against head `84c8df0b`, the round fixture of T1 (one round that
adds the acceptance replay's round 1). Liveness: at 604 object types base
`apply` is 3.1 times head `apply` (at least 1.5 required).

| Object types | validate base / head | preview base / head | apply base / head |
|---|---|---|---|
| 34 | 1.27 / 0.79 | 1.43 / 0.83 | 1.84 / 1.02 |
| 304 | 3.02 / 1.26 | 3.27 / 0.99 | 8.55 / 2.34 |
| 604 | 3.48 / 2.94 | 5.91 / 3.03 | 15.37 / 4.99 |
| 1,204 | 5.96 / 3.62 | 9.24 / 2.97 | 26.52 / 6.12 |
| 2,404 | 6.68 / 6.17 | 11.37 / 5.75 | 33.68 / 12.80 |

`validate` is outside GO1 (D9) and its code did not change; its differences
are run-to-run noise and warm caches, which is the size of noise in this
table. A round still costs time in proportion to the model.

## Review

Instrument: the review helper, one reviewer in a different tool (Codex,
`codex exec --sandbox read-only`, reasoning high), ruled by the owner (D8,
"Review helper, both"). **One reviewer is one reviewer; this is not a
panel.** Brief `notes/reviews/phase-GO1-r1/BRIEF.md` over `84c8df0b`, with
the GO1 criteria, R0.2 and the pattern-matched-solutions claim.

Verdict CHANGES_REQUESTED with three findings, each reproduced before it was
believed and each hardening: the write check missed tag and key-type changes
(F1) and raised on an unchanged anchored tagged scalar (F2); a context copied
from a closed scope reused it (F3). All fixed in `7e8b29ba`, each with a
regression test that fails at `84c8df0b`. The ledger is `FINDINGS.md`. No
finding was blocking, so the budget (a second round only if the first
blocks) ends here. **The repaired `_parsing.py` and the GO1 test file carry
no review opinion** (`review_tool.py status` lists them unreviewed).
`review.md` and `review.log` were sanitized for local paths by the helper,
which says so at the top of `review.md`.

## Refactoring review

- No existing helper compares parsed documents or remembers a parse; the
  scope follows the house pattern of a module-local `ContextVar` per scope
  (`model_index`, `universe`, `extension_preparation`), not a shared helper,
  because each keys and drops differently.
- The reader test exists once, `_strict_json_source`, called by the parser
  and by the key.
- The write check's snapshot is the round-trip YAML writer, not a second
  equality walk; the first draft's walk (`_same`) was removed with F1/F2.
- The command module reaches `parse_scoped` through its own domain service,
  as the entry-point rule requires; no new layer row.

## Implementation findings and deviations

From spec §13: the NaN false positive of the first write check; the cap
checked before the key is hashed; **the scope opens on
`gnd.commands.evolve.handle`, not on the three `_cmd_evolve_*` handlers**,
because the RF5 relocation guard pins those bodies; "does not cross
threads" restated for copied contexts.

Files outside the plan's §3 GO1 list: `src/gnd/commands/evolve.py` (the
decorator), `tests/conftest.py` (the autouse write check). Both are named in
the pull request for the other lanes.

## Boundary -- what this result did NOT establish

- Speed on another machine or a CI runner, a real vocabulary, memory, or a
  round adding more than one fact type (spec, the experiment's limits).
- `gnd validate` and every other command parse as before (D9: the loader's
  double parse is a maintenance pass offered to the owner, not done here).
- The review repairs are unreviewed bytes.
- No merge, release or publication. GO2–GO5 are not started: GO2 and GO3
  wait for reviewed-vocabulary-growth VG2 and VG4 merged on `main`; GO4 and
  GO5 wait for VG2 and VG5.
