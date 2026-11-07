# Plan review over r2 (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner (RF-D0, "Approve all as proposed", 2026-11-07). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, 154,790 tokens, exit 0.
- Reviewed bytes: notes/rule-check-followups-plan.md r2, sha256 6e0d031ae68a7614ed8a5d665abde1b0923a757787c992e57776a269d7ae87b6 (commit 30bfdf26), and notes/phase-FU1-spec.md at that commit.
- The output below is unedited; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU1-spec.md:46
QUOTE: `$defs.derivation_verdict.properties.reason_code.enum` gains the values `derivation_verdict_v15` already lists that it lacks
PROBLEM: The specified edit cannot meet FU1-C1. Unchecked derivations also face a second reason-code enum at `src/gnd/report.schema.json:1108-1113`. In a read-only probe, adding `term:mod-zero` to the property enum left the version-7 report invalid; adding it to both enums made it valid.
FIX: Widen both enums to FD3’s ruled set, preserving the unchecked condition and the existing report bytes. Make T1 fail if either enum remains narrow.

ID: P2
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:108
QUOTE: every schema that references `derivation_verdict` is listed and tested (v7, v9, legacy reference, temporal admission).
PROBLEM: The list is not exhaustive as worded: `derivation_verdict_v15` references six properties of `derivation_verdict` at `src/gnd/report.schema.json:5132-5148`, and `rule_ids_report` uses that v15 definition at `:5399`. FU1’s edit should leave v15 valid.
FIX: Scope C3 to branches whose reason-code enum comes from `derivation_verdict`, and add a v15 non-regression schema case. Use direct schema cases for listed branches even when a CLI route cannot emit the reason.

ID: P3
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:112
QUOTE: `model_copy` (and any other construction route the spec finds) cannot produce a producer without `tool-output`.
PROBLEM: `Population.model_construct(model="m", source="fixture", producer="x")` also creates the forbidden state. It bypasses the validator at `src/gnd/population.py:158-164`; refusing `model_copy` updates alone does not cover C1’s broader wording.
FIX: In the FU2 spec, explicitly decide whether `model_construct` is within C1’s scope. If it is, guard it and add a failing case; otherwise narrow C1 to validated construction and copying.

ID: P4
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:114
QUOTE: `label` survives `_combine_validated_populations` and `bind_population`.
PROBLEM: The criterion does not say whose label wins when candidate and reference populations differ. The binder currently takes the candidate’s `source` and `producer` at `src/gnd/model/__init__.py:699-704`. Carrying its label changes the combined population’s content digest because `src/gnd/values.py:168-173` hashes `label`; the witness candidate digest instead hashes the original candidate at `src/gnd/witness/io.py:280-284`.
FIX: Specify candidate-label precedence and test conflicting labels. Pin the combined digest change and the unchanged witness candidate binding; list any recorded digest affected by a labeled fixture before implementation.

ID: P5
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:186
QUOTE: widen: the scope walk's ratio and ceiling, and the driver test's time margins, to values measured under the six-shard load
PROBLEM: The driver test’s survivor assertion runs `pgrep -f "pathlib.Path"` across the machine (`tests/test_public_session_driver.py:387-390`). It can count an unrelated process. Wider time margins do not address that observer, and the recorded failures do not identify which assertion failed.
FIX: Have the FU4 spec capture the failing assertion under load, scope the survivor check to the spawned process group, then set FD4’s measured margins and show the leader-only mutant still fails.

ID: P6
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:132
QUOTE: per FD5; the guard registries and metrics successors updated.
PROBLEM: FU5-C1 omits specific live guards that retirement must adapt. `tests/test_rf6_packages.py:56-88` requires the historical checker binding count and definition bodies; its RF6b baselines include `_find_cycle`. `tests/support/rf9_ci_sources.py:15-30` requires each frozen compatibility import site, including all three helpers in `compatibility-private-sites.json:209-213,365-369,683-687`. `tests/test_checker_families.py:206-214` imports `_find_cycle`. Simply deleting the helpers fails these guards, while rewriting historical evidence would move recorded bytes.
FIX: Name these guards in the FU5 spec. Keep historical baselines intact, add an explicit retirement successor or exemption for the three names, remove or replace the helper test as FD5 directs, and add a negative test for the retired imports.

The section 1 probes otherwise matched HEAD, including read-only reproductions of issues 113 and 115. The predecessor close’s eight deferred issues are accounted for. There is one tracked `report.schema.json`; `test_schema_sync.py` explicitly excludes it, and its recorded digest is historical RC1 evidence. The v0.1.0 release tag follows RF6, so RF-D5’s release timing does not itself block FU5.
codex exit=0

## Triage (driving agent, 2026-11-07)

P1, P3 and P5 were reproduced: the conditional enum at report.schema.json:1108-1113 lists three values; `Population.model_construct(model='m', source='fixture', producer='x')` succeeds; the survivor check is a machine-wide `pgrep -f "pathlib.Path"`. P2, P4 and P6 were read against the cited files. None relitigates a ruling. All six are applied in r3.

| ID | Disposition |
|---|---|
| P1 | applied: FU1 widens both enums (plan §2, FU1 spec M1, T1) |
| P2 | applied: FU1-C3 scoped to branches whose enum comes from derivation_verdict, direct schema cases, a version-15 non-regression case (T2) |
| P3 | applied: FU2-C1 covers validated construction and model_copy; model_construct is an FU2 spec decision with a case either way |
| P4 | applied: FU2-C2 candidate-label precedence, conflicting-labels case, combined digest change pinned, witness candidate binding pinned unchanged |
| P5 | applied: FU4-C1 captures the failing assertion first and scopes the survivor check to the process group before widening margins |
| P6 | applied: FU5-C1 names the live guards; historical evidence untouched; explicit retirement successor and a negative import test |

r3 is not re-reviewed.
