# Guarded rule authoring · close evidence confirmation

The [initial close outcome](close-outcome.md) remains pinned to round 1.
The standard panel returned five valid reviews and two blocking evidence
findings. This packet verifies their repairs on the same runtime candidate,
`618141de9975c4ef30871a979532654267a15de6`. The close review budget is
two standard rounds. This round checks the two evidence findings and
their named controls. Further runtime changes require a reproduced defect.

## Blocking evidence findings

- **Exact candidate.** The [clean installed receipt](../evidence/close/installed-clean.json)
  identifies the detached clean checkout before and after the run and records
  the wheel SHA-256
  `a04ca98ca3044ee4e870e435d0274c01637ee31c35cecdf7907d3ae434f9dab5`.
  The [replay](../evidence/close/replay.md) verifies the commit and clean status
  before building offline. The wheel ran the installed commands below.
- **Base-only refusal.** The same wheel was installed in a separate base-only
  environment. The receipt's `base_only` entry verifies Faker's absence and an
  installed GND import. It records the guarded-synth invocation, exit 5, the
  verbatim `get-nick-done[synth]` installation hint, both stream hashes and the
  absent output root. The with-extra smoke uses a different environment.

## Public command mapping

The numbering below matches the `commands` array in the clean receipt.
It retains full argument vectors and stream digests.

| Result | Installed operation | Exit and observed assertion |
|---|---|---|
| 1 | GA1 `synth --guarded-cases` on the shipped model | 0, two active pairs and a scoped ordinary corpus |
| 2 | GA1 `measure` with the scoped model | 0, 15 populations and zero checker defects |
| 3 | GA1 `measure` with the full model | 3, wrong-model sidecar digest |
| 4 | GA1 `synth --guarded-cases` on an isolated repeated-variable guard | 0, one matching binding and zero collateral findings in each case |
| 5 | GA2 `discover --families guarded-join` | 0, directed proposal with independently counted support 1/1 |
| 6 | GA2 `evolve preview` | 0, proposal replay accepted |
| 7 | GA3 `export ilp --target amie` | 0, typed facts written and bound into the import run record |
| 8 | GA3 `import mined-rules --target amie` | 0, three supports of 1/1 including the `area:cli` literal head |
| 9 | GA3 `evolve preview` | 0, typed proposal replay accepted |

The `measure_digest_refusals` controls assert the specific `model_digest`
and `a wrong-model sidecar` text at exit 3. The second control changes only
a scoped-model rationale and produces the same refusal. Default discovery,
synthesis and variable-only import compatibility are tested in the source
union, not inferred from the installed opt-in cases.

## Phase review and compatibility evidence

| Review candidate | Reproduced or refuted finding | Current-runtime control |
|---|---|---|
| GA1 `9e2880b9` | Local guards cannot pass model admission. Fresh publication exposed an empty root. Checker work preflight omitted atom and absence witnesses. | `test_fact_type_local_guard_is_invalid_model_input`, `test_fresh_corpus_has_no_visible_empty_root`, `test_fresh_publication_preserves_another_writer`, `test_confirmation_work_accounts_for_atom_and_absence_witnesses` |
| GA2 `8032a346` | Incorrect violating row, mismatched service configuration, and duplicate under reordered renamed atoms. | `test_joined_discovery_rejects_checker_witness_disagreement`, `test_joined_service_rejects_family_and_settings_mismatches`, `test_joined_discovery_declared_rule_is_suppressed` |
| GA3 `24851fbb` | No reproducible AMIE defect found in static review. A later base-wheel smoke exposed the GA1 missing-extra traceback. | `test_amie_literals_in_all_positions_and_shared_head_relation`, `test_guarded_cases_require_synth_extra_with_a_cli_error`, and the base-only installed receipt |

The phase reviewers read those named candidates. The later repairs were
reproduced and checked by the recorded regression tests and the final
union. The independent phase reviews did not read the repair diffs.

GA1's plan gate allowed comparison cases with different values in the same
active antecedent shape. `test_comparison_between_two_integer_variables_can_generate_equality`
and the active cases in result 1 verify it. GA2's plan-review disposition
selected a separate directed cap. `test_joined_discovery_marker_and_separate_directed_cap`
pins the first omitted directed ordinal while the unordered cap is zero.
GA3's aggregate 10,000,000-unit limit can refuse a previously admitted
variable-only input. The original `m4` fixture's valid literal now reaches
support mismatch. The unaffected variable-only observations and export
bytes remain pinned by `test_t3_t5_the_import` and
`test_t1_the_export_is_golden_under_two_hash_seeds`.

## Question sweep

- [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179) closes its
  predecessor deferral under [GA1](../003-phase-GA1.md). The documented
  bounded scalar fragment and scoped ordinary measure contract govern it.
- [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181) closes its
  predecessor deferral under [GA2](../005-phase-GA2.md). Explicit selectors
  and functional endpoint classification govern it.
- [GR-D11](https://github.com/vasiloglou/gnd-public/issues/182) closes its
  predecessor deferral under [GA3](../007-phase-GA3.md). Existing token
  spelling, literal-head scope and exact recount govern it.

The delegated close covers these three delivered requests, the checked
repairs and the evidence record. Merge, live miner execution, certification
and release publication are outside that scope.

## Clean union scope

The clean source checkout uses `uv sync --locked --offline --extra synth`.
The union receipt binds the Python interpreter, lock SHA-256, full
argument vector, stream digests and clean-tree assertions. The default
filter deselects four `live` tests and one `evidence` test.

- `test_live_amie_mines_the_committed_rules` runs a native AMIE learner.
- `test_a1_t2_every_threshold_enumerates_on_an_unbound_argument`,
  `test_a2_t3_clingo_grounds_every_threshold`, and
  `test_a2_t4_no_two_thresholds_are_pointless` run the separate native ILP
  learner or solver controls.
- `test_manifest_bytes_modes_and_sizes` checks the historical scaffold
  evidence lane. The ordinary scaffold tests remain in the union.

The fixture-driven AMIE CLI reader, binding, mapping, count, checker
and preview controls run in the selected union. The native learner and
historical-evidence exercises are outside this closure's claims.

The [clean union receipt](../evidence/close/union-clean.json) records
`1023 passed, 5 deselected in 232.40s (0:03:52)` and exit 0. Both
the union and installed receipts name the same clean source commit.
The [replay](../evidence/close/replay.md) records the Ruff and strict
component check scope and the two catalog reread dispositions.
