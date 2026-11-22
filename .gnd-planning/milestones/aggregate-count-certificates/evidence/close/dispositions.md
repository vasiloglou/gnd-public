# Close panel dispositions

The reviewed packet remains at `400920e6`. This supplement records the
close ruling's evidence map. Each concern below refers to the finalized panel.

## Review and verification of the repair

The Opus phase review read `c56ce751`. The six files changed in the
[repair at 2f906af0](https://github.com/vasiloglou/gnd-public/commit/2f906af055386ca2e7dc0e83c0be039cdb7b9061)
are the membership module, its normative contract, its test file and
three component documents. The [status ledger](../AC1/independent-review-status.txt)
lists them separately. The local review reproduced the slow path on both
model and population YAML, introduced the existing bounded YAML event
guard at those two entry points, and verified both red-to-green cases.
The repaired candidate also passed the installed check. No second
independent phase review was commissioned. The delegated ruling accepts
the tested repair under the plan's one-review phase budget.

The focused and structural suites in [AC1's gate table](../../003-phase-AC1.md)
ran on the repaired source at `2f906af0`. They returned
`295 passed in 166.71s (0:02:46)` and
`679 passed, 2 deselected in 313.40s (0:05:13)`. The product, test,
tool and public-document files match those bytes at `400920e6`.
The [installed observation](../AC1/installed-observation.json) names the
repair commit and wheel digest directly. The strict component command
`python3 scripts/components_index.py changed --base a7785ffb --strict`
returned zero findings, warnings and rereads. Whole-tree Ruff recorded
188 inherited diagnostics on both base and candidate, with zero added.

| Reviewer concerns | Disposition |
|---|---|
| Claude `repair-bytes-outside-independent-review`, Codex `final-repair-unreviewed`, GLM `ac1-close-repaired-membership-core-unreviewed` | The scope distinction and accepted residual are recorded above. The recommendation for a second phase review is declined. The runtime change reuses the existing guard and has red-to-green, installed and compatibility evidence. |
| GLM `ac1-close-full-suite-gates-unattributed` | Both suite targets are identified above. |
| Qwen `acc-required-structural-and-lint-checks-unevidenced` | The phase record carries the full focused and structural invocations and output. The strict component check and base Ruff comparison are identified above. |
| Qwen `acc-pinned-phase-and-installed-evidence-not-in-panel-packet` | The selected panel request permits exactly the real spec, results and delta inputs. The remaining files are linked evidence. The close sweep verified their actual bytes against the request and record digests. The inline seat's direct coverage was limited to the three named documents. |
| Qwen `acc-close-delta-not-digest-pinned` | The delta's SHA-256 was already in the reviewed request. The delegated close record pins the delta again alongside the candidate and request. |

## Issue controls and proposal

| Part 10 requirement | Verified control |
|---|---|
| Omission | `test_well_formed_membership_forgery_refuses[omitted-and-recounted]` exits 1. |
| Duplication | `test_well_formed_membership_forgery_refuses[duplicated-and-recounted]` exits 1. |
| Empty group | `test_exact_membership_and_public_replay[empty-group.json-empty]` proves a named empty group in the four-row relation containing `flow` and `other`. The installed checker report is byte-identical before and after. `test_empty_covered_relation_and_edited_nonempty_snapshot` also proves an empty covered relation and exercises the refusal after coverage removal. |
| Changed inputs | `test_edited_inputs_precede_forged_membership` varies each of model, candidate population and external request. `test_changed_rule_binding_and_rebound_invalid_proof` varies the rule, then rebinds it to reach proof comparison. |
| Size limits | `test_work_limits_apply_to_empty_scans_both_ways_and_input_intake`, `test_projected_output_has_its_own_byte_limit`, `test_certificate_intake_precedes_model_reads` and `test_deep_yaml_is_refused_before_loading_snapshot` cover distinct limits and precedence. The close control also tests submitted and reconstructed replay result limits. |

The proposal's individual member witness is recorded separately from the five
criteria. The installed fixture and
`test_individual_base_occurrence_still_witnesses_and_replays` match the
ordinary witness position to the first certified member. The frozen roster
and `test_exact_membership_and_public_replay` require representative
positions `[2, 0]`. The alternate index for a repeated contribution is
rejected by `alternate-representative`.

| Reviewer concern | Disposition |
|---|---|
| Qwen `acc-empty-group-populated-covered-relation-not-established` | The covered populated fixture and complementary missing-coverage controls are named above. `test_declared_coverage_is_authenticated_for_both_paths` also checks that changing coverage stales the existing certificate and that a fresh uncovered request refuses at 2. |
| Qwen `acc-plan-mutation-controls-absent-from-exit-predicates` | The parameterized forgery test also exercises `false-empty`, `extra-member` padding, an `unrelated-index` into the other group, a `substituted-of`, `wrong-type`, `swapped-order`, `count-only` and `alternate-representative`. Each exits 1. The exact roster test pins the lowest qualifying position. |
| Qwen `acc-five-criteria-versus-six-evidence-rows` | The five issue bullets are mapped above. The separately listed member evidence fulfills the proposal's optional member-witness path. |

## Replay and interface boundaries

Replay authenticates the caller's inputs and reconstructs the result through
the same bounded membership scan and rule interpretation used by production.
Its validation path consumes the independently supplied model, population and
request and never invokes the producer. The frozen hand-authored roster,
the checker differential and the close control for a two-role typed group
test the shared interpretation. A shared defect outside these controls
remains possible and is accepted within the bounded fragment.

An opaque asserted source value prevents a complete membership result.
Production and replay with a current binding return `2 / opaque-value`
for both a populated selection and an empty selection. The close control
also verifies that the old certificate first returns `3 / binding-stale`
when its snapshot changes. The regular witness and checker compatibility
gates ran alongside the new disclosure controls.

Replay distinguishes submitted inputs from work spent reconstructing
membership. An over-ceiling submitted roster or certificate is
`3 / input-invalid`. A validly framed false-empty certificate can fit that
input budget while reconstruction exceeds its member or output-byte
ceiling, which is `4 / work-limit`. Within budget it returns
`1 / proof-invalid`. The certificate shape gate runs before snapshot
reads. The raw snapshot cap runs before byte authentication, which
precedes model inference and roster comparison. The expected group scan
is driven by source rows and limits. The zero count in the false-empty
control does not stop that scan.

| Reviewer concern | Disposition |
|---|---|
| Claude `replay-shares-membership-semantics` | The shared interpretation boundary is explicit. The committed differential control exercises String/Boolean group roles and ordered String/Integer contributions, comparing all present counts against the existing checker and replaying an absent combination. |
| Claude `replay-member-ceiling-exit-code` | The submitted shape and reconstruction exits above both have executable controls. |
| Qwen `acc-opaque-row-refusal-exit-and-control-unspecified` | The executable opaque control records the refusal for both producer and replay and tests stale precedence. |
| Qwen `acc-refusal-ordering-and-exit-code-mapping-collapsed` | The precedence and exit mapping above are bound to the depth, malformed-certificate and work-limit regressions and to the close control. |
| Qwen `acc-replay-trust-boundary-not-surfaced` | `test_replay_runs_with_producer_and_evaluator_imports_blocked` verifies the separate replay path. The false-empty control proves that submitted count zero does not cap reconstruction. |
| Qwen `acc-plan-documentation-deliverables-unevidenced` | The normative wire lives in `src/gnd/skills/gnd-export/references/count-witness-contract.md`, linked by `docs/reference/cli.md`. The worked example is in `src/gnd/examples/literature/count_fixture/`. Exact component and architecture registration is in `dev/components/COMPONENTS.md`, `tools/gnd_layers.json` and `tools/gnd_entrypoints.json`. |

Run the supplementary controls from the root with
`uv run --no-sync python .gnd-planning/milestones/aggregate-count-certificates/evidence/close/verify-controls.py`.
The [observations](verification.json) record the resulting verdicts.
