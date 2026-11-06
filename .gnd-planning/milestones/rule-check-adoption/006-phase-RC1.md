---
milestone: rule-check-adoption
station: phase-RC1
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC1
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_rc1_rule_ids.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "360 passed"
  note: >-
    The plan section 9 RC1 row (V2), at 5764ee72. The impact closure (V4,
    1970 passed), lint (V5) and the sharded full default suite against main
    (V1/V3, no new failure) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "the broad lanes read no path RC1 changed except through the guards already in V4 and the full default suite"
evidence:
  - path: src/gnd/address.py
    sha256: 69ad0ae04472b31cb86bf754e94c09b7f55b0a7cdc96da943c2ce30bf44b3390
  - path: src/gnd/checking_service.py
    sha256: 21b2c172c5a501e225699ebcf40ae3f2e64db0119686dd2c948e1e7099efa4f7
  - path: src/gnd/commands/checking.py
    sha256: 0185401c00d703a5cc92367c8aea86e219612f6a385e1842dc14c257207bdc25
  - path: src/gnd/coverage.py
    sha256: 8d24aebbec59c839c663da979a06a1f6325dd4ba595fd5ed517ea338cce8f4e5
  - path: src/gnd/evolve/policy.py
    sha256: 7f9457a3b91bb401cecc43967a60829856e9a9b7965863c71174ee721ff38366
  - path: src/gnd/model_index.py
    sha256: 680a36d84784daa1b63d0a8b6591b6eebf2a05cf10f39525e398ca2fe610a93e
  - path: src/gnd/output.py
    sha256: 2c946769ed304c4793d31446329d02b88513cd46699a2a7a9bbf538b7b53bcc7
  - path: src/gnd/payloads.py
    sha256: 44d0254ea9ded08963a1c6217977d9ea93593563e3ab3ecb699a606033baf327
  - path: src/gnd/report.schema.json
    sha256: 2c1e126f80c3cc3cece5853b01a9f1edb560e2bca08a4ef4fbe73ec68e4e91ac
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: ebbc89f3b33c94918c10d3b8305594a058bbd9f0e0081027f43c64345619879a
  - path: src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json
    sha256: ebbc89f3b33c94918c10d3b8305594a058bbd9f0e0081027f43c64345619879a
  - path: tests/test_rc1_rule_ids.py
    sha256: 63d12ad5ece3944757c6ebc7d8b778cc23a852bf5671c3ae847600ceaf79e8ad
  - path: tests/_tp2_freeze_plugin.py
    sha256: d362c599ec98829d7a1512738cf91135debc4ae4e36eb35137095d6906d52d12
  - path: tests/test_rf1_cli_pins.py
    sha256: 87864e756a2255a5b7de46292027a4f2ffed2d7bca9627a795cbd28e660693fc
  - path: tests/fixtures/rule-ids-cli/expected.json
    sha256: 3e7c7ed462fe1854adbe13f4cacae41fdcdad5bdaee003f3a438e011619dc061
  - path: tests/fixtures/rc1-rule-ids/README.md
    sha256: 46d61234fa20e3aae67c77c95844b5ca3b96d4d02397638d4f7771fc1c709eed
  - path: tests/fixtures/rc1-rule-ids/expected/README.md
    sha256: f68c2f1be25df4890f7d966082c2ceed3bc60508331bbb2c0bec63c74b92d92b
  - path: tests/fixtures/rc1-rule-ids/expected/declared-fail.json
    sha256: 9b783855194b2f618b54e8e1a457732e53578ef705aabed607cc99b697cafcfa
  - path: tests/fixtures/rc1-rule-ids/expected/declared-fail.txt
    sha256: 774ff14cd3e2ba803da33316f9a21b587936f50b4eb819c3855b6f6cdfc37153
  - path: tests/fixtures/rc1-rule-ids/pre-rc1/declared-fail.txt
    sha256: d80299a27437fc74cde97c6feb5fc441c6718e4988ed16894a7da7c3c1eef3ac
  - path: tests/support/pyrel_application_successors.py
    sha256: 77654fca6fcb64722f9380888cf8689885001bc3857631a50709ebefdf05dcae
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 540c4569392c561366d0903959cb49fcd101704d27c347592741530d84f60d1d
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC1/dynamic-query-successor.json
    sha256: c2f734394d2dc3990c2ba6b4d7c9724c636252b063576ff1ef68a1b9d460588d
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC1/full-suite-main-508d6bec.txt
    sha256: 8b0ea796a1a2e2000534558c6193e25809d24ff75d5280206c7301e5345e98ed
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC1/full-suite-rc1-5764ee72.txt
    sha256: 8a0eb0cd78c2da2a1c787af34ea9e1d3485e6d8ff26153dc85fb1b21071392bb
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC1-spec.md
    sha256: 2fde27a63fd1308a956ca6165e71561d01c27bbec8d5567a8b123758e70c6d46
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC1-codex-review.md
    sha256: 35ea9f36db1bc64c7dd589fd5d9374882bb74b24390b0ebce4429df1628774cd
---

# Claim

At 5764ee72 (RC1 merged with main 508d6bec, which carries PR 99),
`gnd check MODEL POP --rule-ids` emits report version 15 as the
owner-approved corpus specifies: the RC1 test file exited 0 (33 passed),
the focused gate V2 exited 0 (360 passed), the impact closure V4 exited 0
(1970 passed), and the sharded full default suite V3 fails exactly the 124
tests main fails at 508d6bec. RC1 adds no failure.

## What shipped

- **M1** `remedy` (string, 1-2000) in `constraint_common` of
  `src/gnd/schema/orm-meta.schema.json` and its sync-pinned skill copy.
- **M2** `src/gnd/report.schema.json`: closed `verdict_v15` (the nine v7
  properties by `$ref`, plus `address`, `addressing`, `remedy`, `novelty`,
  `row_novelty`), `derivation_verdict_v15` (v7 properties and conditional
  rules, `reason_code` widened to every `DerivationReason`), `baseline_v15`,
  and the top-level branch `rule_ids_report`.
- **M3** `address.declared_constraint_address` (the census's helper moved;
  `coverage._constraint_address` kept as an identity alias);
  `ModelIndex.iter_constraints_shared()` (non-copying, must-not-mutate).
- **M4** `payloads.build_check_payload(..., declared=...)`: version 15 =
  version 7 plus identity keys per verdict and `baseline: null`,
  `allow_vacuous: false`; the six version gates name the set
  `ASSURED_PAYLOAD_SCHEMA_VERSIONS = {7, 8, 15}`.
- **M5** `checking_service._run_check_raw(rule_ids=...)`: version 15 for a
  plain version-7 model; temporal, redaction-policy and reference-population
  models refused at exit 3 (`check:rule-ids-unsupported`) on every route
  after model load and before population load, at the version the model gets
  without the flag (D8).
- **M6** `--rule-ids` on `gnd check`; conflicts with the ten other-arm flags
  exit 64 before the model is read; text output names declared ids and
  prints the remedy (`output._identified_verdict_lines`).
- **M7** `gnd coverage` unchanged; refuses a version-15 report.
- **M8** `gnd evolve` admits a `remedy` edit, as it admits `rationale`.
- **M9** amended (corpus finding C1): no new branch row, so no version-7
  assurance block moves.
- CLI help: the approved additive successor for `gnd check` is
  `tests/fixtures/rule-ids-cli/expected.json`; its help and exit-probe text
  differ from the previous successor's by the one added option (diff checked
  2026-11-06); the RF1 historical golden bytes are unchanged.
- Guard bookkeeping (5764ee72): the RF4/RF5 body pins and the RF6
  dynamic-read inventory record RC1's changed bodies and read sites through
  their successor registries (finding I1).

## Gate output (verbatim)

V1, merge base 8bfbe417, focused (local, before any source edit):

    327 passed in 32.11s
    focused exit=0

V2, focused gate (plan §9 row), at 5764ee72:

    uv run pytest -q tests/test_rc1_rule_ids.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py --tb=short -p no:cacheprovider
    360 passed in 37.79s
    exit=0

V4, impact closure, at 5764ee72 (now including the three guard suites the
full suite showed RC1 touches, finding I1):

    uv run pytest -q tests/test_rf1_cli_pins.py tests/test_evolve_additive_policy.py tests/test_rf6_index.py tests/test_public_construction_site_guards.py tests/test_public_branch_runtime.py tests/test_v6_phase2_registry.py tests/test_packaged_skills.py tests/test_v6_phase6_report.py tests/test_tp2_shared_fact_types.py tests/test_v62_phase6_coverage.py tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf6_query_policy.py --tb=short -p no:cacheprovider
    1970 passed in 114.54s (0:01:54)
    exit=0

V5, lint, at 5764ee72:

    uv run ruff check src tests
    Found 11 errors.
    exit=1
    uv run ruff check <the Python files changed since 8bfbe417>
    All checks passed!
    exit=0

The 11 whole-tree errors are a known red: the same command printed
`Found 11 errors.` at the old merge base 8bfbe417 and at main 508d6bec;
none is in a file this phase touched.

V1 (main 508d6bec, after PR 99) and V3 (5764ee72), full default lane, sharded (the same layout for both: test files
sorted and dealt round-robin into 6 shards, each shard in its own clone, run
on beast-3 after `uv sync --locked --group dev` and
`uv run gnd install --symlink --project --force`, with
`uv run pytest -q --tb=line -p no:cacheprovider <files>`):

    V1 main 508d6bec: 17448 passed, 119 failed, 5 errors; shards exit 0,0,1,1,1,0
    V3 rc1 5764ee72:  17481 passed, 119 failed, 5 errors; shards exit 0,0,1,1,1,0
    sorted failing ids: 124 each; comm -13 (only in V3): empty; comm -23: empty
    sha256 of each sorted failing-id list:
      f084798e6cdbd816c24ba71922b4a4d85b445ad870673106ce1c0465f705ca09 (both)

The per-shard summaries and both failing-id lists are retained in
`evidence/RC1/full-suite-main-508d6bec.txt` and
`evidence/RC1/full-suite-rc1-5764ee72.txt`. The 33 extra passes are the RC1
test file. All 124 are environmental on this host and identical on main:
115 in `test_adopt_migration.py` and the `test_ilp_learners.py` wheel check
spawn `uv` by name, which the detached shell's PATH lacked
(`FileNotFoundError: ... 'uv'`); the rest (`test_doctor_uninstall.py`,
`test_generated_project_isolation.py`, `test_public_optional.py`) concern
the clone's install receipts and venv isolation. They are known reds, not
RC1 findings.

The first full run, at dc592a89, found five guard failures RC1 caused
(spec finding I1: RF4/RF5 body pins and the RF6 dynamic-read inventory).
After the merge with main there were nine. 5764ee72 records them through
the guards' own successor registries (three chained `source-successors.json`
rows extended, three added; `evidence/RC1/dynamic-query-successor.json`
appended to `DYNAMIC_SUCCESSORS`); no pinned historical byte was edited.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| RC1-C1 | T1, T2 (`test_t2_*`) | exit 0 / exit 3 as specified |
| RC1-C2 | corpus `declared-fail`, `positional-pass`, `derivation-*`; T4b | byte-equal to the answer key; schema-valid |
| RC1-C3 | V3 against V1; P3 | no failure in V3 that V1 lacks |
| RC1-C4 | T7 (8 conflict sets + `--unredacted` accepted), corpus `conflict-populations` | exit 64, empty stdout |
| RC1-C5 | T6 | v15 valid; v7 + `address` invalid |
| RC1-C6 | corpus `refuse-*`, P1 | exit 3, rule id, versions 9/11/12, `error: null` |
| RC1-C7 | corpus `text-declared-fail`, T10, P3 | byte-equal |
| RC1-C8 | V2 (`test_address.py`, `test_coverage_payload.py`), T12 | unchanged; refused |
| RC1-C9 | T13 (measured below), P2 | under 0.5 s, no copy, no write |

Measured: T13's identity walk over 2,001 constraints (2,000 in one fact
type) ran under its 0.5 s bound in every run of the file (the test asserts
it; elapsed is not printed). Threshold unchanged.

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff 76c5af11 24bb5c9e -- src tests`, disposition `block`, 3 findings,
all reproduced and fixed with regression tests observed red before the fix:
P1 blocking (reference model with unbindable references gave a
schema-invalid wrapped v15 report), P2 and P3 hardening of this phase's own
claims. Retained verbatim with the triage in
[phase-RC1-codex-review.md](notes/phase-RC1-codex-review.md). The fixes
(dc592a89) and the guard rows (5764ee72) were not re-reviewed.

## Refactoring review

Refactors EXECUTED:
- `ASSURED_PAYLOAD_SCHEMA_VERSIONS` in `src/gnd/payloads.py`: the six
  `{7, 8, 15}` literals (formerly `{7, 8}`) name one set. Behaviour-preserving;
  landed in dc592a89 behind V2, V4 and V3.
- The census addressing helper moved to `address.declared_constraint_address`
  (one home for the census and the report), with the old private name kept as
  an identity alias (AGENTS.md shim rule).

Seen, deferred (open questions below): the model digest is `repr()`-based;
text mode prints projected JSON for redaction/temporal models; the two
Tarjan copies (RC2 owns).

## Boundary: what this phase does NOT establish

- One reviewer read the diff; the review fixes were not re-reviewed.
- The full default suite is not clean on beast-3: 124 environmental reds,
  identical on main, mask whatever those tests would say about RC1.
- Version 15 exists only for the plain snapshot arm and plain version-7
  models; novelty, baseline and allow_vacuous are fixed in the shape but
  always empty (RC3, RC4 fill them).
- V3 is the full default lane, sharded; it is not the broad lane. The broad
  lanes (`-m "evidence or census"`) did not run (`slow_cadence`).
- "Version 7 unchanged" rests on the full default suite and the rf1 goldens;
  a version-7 byte no test pins could still have moved.
- The CLI help changed by one option, approved as an additive successor;
  that approval is this record's, not a separate owner ruling.
- No live caller ran: the requester's tool has not been run against this
  build.

## Open questions

- **Size (plan rule 8).** Measured: source +649/-22 lines, of which 431 are
  `report.schema.json` (one JSON value per line under the file's
  `indent=2` formatting) against about 140 estimated for M2, and 213 lines
  of Python against about 100; tests +332/-4 against about 520; fixtures 23
  files, +690. Total source exceeds 1.5 times the 240-line estimate, so
  rule 8's pause applies. **Resolved 2026-11-06, owner ruling: "Accept
  overrun".** The plan is not amended; the estimate stands for later
  phases.
- **Model digest is `repr()`-based** (`values._model_digest`), a
  Python-specific identity a caller cannot reproduce. Pre-existing; RC1's
  corpus relies on it (C4). Target: its own issue.
- **Text mode for redaction/temporal models prints projected JSON**, with or
  without `--rule-ids`. Pre-existing. Target: its own issue.
- **Full-suite environment reds** on beast-3 (124, identical on main):
  the subprocess PATH lacks `uv` in a detached shell. Not RC1's; a host
  setup fix would make V1 clean. Target: maintenance, before RC2's
  full-suite gate.

## Refuted premises

- Spec M9 assumed a new branch row was needed for registry completeness.
  The version-7 assurance block lists applicable `report:check:n-a:*` rows,
  so a new row would have moved frozen bytes (corpus finding C1, probe of
  `tests/fixtures/rc1-rule-ids`, 2026-11-06). M9 was amended before code.
