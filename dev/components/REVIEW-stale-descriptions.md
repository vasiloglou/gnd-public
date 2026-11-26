# Component index review of stale descriptions, 2026-11-26

Scope: the 103 components whose modules had commits after their `does` and `verbs`
were last edited (the first group of `components_index.py review`). The other 163
components and the 11 subsystems were not reread, and `REVIEW.md` is left as it was.
Code read at commit a223ac7. 266 components and 11 subsystems before and after; no
entry was added, split, merged or removed.

How each entry was read: the entry beside `git diff <commit>..HEAD` of its modules,
from the commit the lead named. That is the check the lead calls for, not a reading of
every module. Five modules were read in full (`evolve/outcomes.py`,
`evolve/__init__.py`, `synth/guarded_service.py`, `examples/literature/revision.py`,
`examples/literature/revision_manifest.py`); the rest through their diffs. The seven
largest diffs were read by two readers whose proposals were sample-checked in the code
before they were applied. The 60 `checked: partial` lines stay: no entry was read in
whole.

## What was repaired in the index

74 entries read and found still accurate; each has a `reread:` line dated 2026-11-26
naming the commit it was read from. 29 entries edited:

- semantics.temporal_guards: `does` now covers date memberships and supplied filtered bindings; verbs for `evaluate_filtered_temporal_guard` and `term_syntax`.
- model.relational_mapping: the note said refscheme takes the first external uniqueness whatever its status. It now prefers the confirmed alethic preferred one, through this module's helpers. Verbs for `external_uniqueness_order`.
- model.reference_schemes: verbs for the preferred, reviewed composite key and its fallback.
- evolve.operation_outcomes: the note said nothing that decides a refusal reads the outcomes. `discover.narrow` now reads them to choose what a narrowed proposal keeps. Entry otherwise still accurate.
- export.pyrel_rules: the note said every unsupported semantic is refused. Anchored rules and disconnected joins are now listed as not checked. Verbs for `render_report`, external uniqueness, role-scoped value rules and float exactness.
- Guarded disjunction (`any_of`), antecedent filters and membership, which arrived in ten components without their verbs: check.snapshot_decision, semantics.snapshot_spec, semantics.snapshot_adapter, semantics.snapshot_ir, semantics.extensions, checker.evaluate, synth.guarded, model.verbalization, export.lean_lowering, export.souffle_lowering (the last two as named refusals).
- Include roots and flat models: witness.command (`--flat-model`, `--flattening-record`), witness.replay (flattening binding, model origins, catalog certificates), export.include_roots (`model_validation_message`), export.pyrel_emit (`render_pyrel_rules_report`), model.validation (`flat_without_root_issue`, first document pending).
- evolve.service: verbs for `read_evolution_outcome_report`, `OutcomeRefusalPending` and the unattended re-pin refusal.
- synth.service: verbs for `run_guarded_cases` and the guarded-cases manifest (its second module, `guarded_service.py`, had no verb).
- evolve.population_check: verbs for `workspace_relative`, the stale-population refusal and YAML populations.
- discover.joined: verbs for `matches_counterexamples`, `require_family` and `guard_key`.
- export.ossie, export.physical_binding: verbs for unit-based references and the identifier depth limit.
- infra.errors (`ReferenceHashMismatch`), examples.literature_lineage (admission binding), examples.literature_assurance (`score_reading_coverage`), examples.literature_revision (`replay_renewed_support`): verbs for new public names.
- model.scalar_terms: its `reread:` line updated, since `description` and `sample_population` are no longer walked as syntax.

## Suggested code changes

| # | Kind | What | Where | Size | Checked how |
|---|---|---|---|---|---|
| 1 | Undescribed | Ten include-guard route labels carry a source line number that no longer matches | see below | small | `grep` of `route='<name>:<digits>'` under `src/gnd`, each compared with its own line |
| 2 | Duplicate | The preferred external uniqueness of an entity is selected in two places with different conditions | src/gnd/refscheme.py:70, src/gnd/rmap.py:226 | medium | read both selections |
| 3 | Undescribed | Two docstrings in `evolve/outcomes.py` describe the dependents drop as it was before it became transitive and order-independent | src/gnd/evolve/outcomes.py:3, :141 | small | reader read the module in full; I read the module docstring |
| 4 | Undescribed | A D-12 refusal message lists the admitted sources without `sample` and `common-sense` | src/gnd/evolve/service.py:584 | small | read lines 566-587 |

### 1. Route labels that name a line
`guard_bytes(..., route=...)` passes the label to the refusal as its detail
(`src/gnd/model/_includes.py:328`). Ten callers label themselves by file and line, and
every line is now wrong: `api:980` at api.py:991, `service:29` at witness/service.py:42,
`service:231` at evolve/service.py:269, `lean_io:39` at export/lean_io.py:42,
`pyrel_rules:2267` at export/pyrel_rules.py:2701, `applications:220` and
`applications:295` at export/applications.py:227 and :304, `souffle_io:115` at
export/souffle_io.py:117, `session_contract:1677` at exp/session_contract.py:1687,
`session_replay:68` at exp/session_replay.py:67. Two are both `service:`. Suggest a
capability name, as the other callers use (`export.lean.raw`, `batch`,
`exp.session-contract`). A test that pins a label would need the same edit.

### 2. Two selections of the identifying external uniqueness
`refscheme._select_role_refs` picks the preferred, confirmed alethic external
uniqueness anchored on an entity and falls back to the first anchored one.
`rmap._Mapper` builds the same choice once per model, and also requires that no
component is derived and that each is functional on the entity. Both order ties with
`rmap.external_uniqueness_order`. The two can therefore name different identifiers for
one entity. If that is intended, `distinct_from` and a note would record it; if not,
refscheme could read the Rmap's indexed choice. Callers of refscheme: discover,
evolve.shape_matches, extract and verbalization.

### 3. Docstrings in evolve/outcomes.py
The module docstring says a refusal drops "every later operation that depends on an
element it adds"; `outcomes()` now drops dependents wherever they stand and follows
dropped operations transitively. The `locate_validation_issues` docstring omits
constraints embedded in a fact type's `after` and the role step.

### 4. D-12 refusal message
The final `else` message says new or changed constraints "must be
llm-inferred/proposed/deontic or user-supplied/confirmed"; the branch above it also
admits `sample` and `common-sense` sources. Not checked: whether a test or the
evolution contract pins the text.

## Not confirmed

- src/gnd/semantic_spec.py:5-7 says its interfaces "are not production correspondence", while `correspondence._indexed_guarded_disjunction` now uses this module's budget and state helpers (imports verified). Whether that breaks the docstring's intent is the owner's call.
- src/gnd/export/pyrel_rules.py:1169 resolves an unknown relation ending in `_any` by suffix, beside a comment at :197 saying a fact type that only happens to end in `_any` is never taken for one. No failing input was built; fact types are matched earlier at :1160.
- src/gnd/correspondence.py:943 imports `evaluate_temporal_guard` inside a function beside the module-level `temporal_guarded` import. Reported by a reader, not checked by me.
- No user was asked for searches known to have missed.

## Searches tried

- "prefer reviewed composite reference key" -> model.reference_schemes
- "witness an include root with a flat model" -> witness.command
- "guarded rule with alternatives any_of disjunction" -> synth.guarded
- "guarded cases manifest" -> synth.service
- "renewed review support" -> examples.literature_revision
- "check value is one of a list membership" -> model.validation (model.scalar_terms, where membership is compiled, is not first)
- "refuse stale population before apply" -> the module src/gnd/evolve/population_check.py, not its component
- "operation outcomes report" -> cli.evolve_command (evolve.operation_outcomes is not first)

## Second pass, after main moved to c304885

Main was merged into this branch at c304885, and 16 components had commits to their
modules after their `does`, `verbs` or `reread` line (the first group of `review`).
Each was read the same way: the entry beside `git diff <commit>..HEAD` of its modules,
from the commit the lead named (1519ecb, 08fcfd0 or bedba9a). The source tree at HEAD
is that of c304885.

9 entries read and found still accurate; each has a `reread:` line dated 2026-11-26
naming the commit it was read from (code at c304885): model.reference_schemes,
check.admission, semantics.extensions, semantics.snapshot_adapter,
semantics.transitions, model.population_sentences (each only reads fact rows through
`ModelIndex.fact_map`, the same last-wins map it built before), exp.schema (its verbs
already name `read_session_contract_with_digest` and the portable prompt),
exp.session_evidence (its readers now share `SessionEvidenceJson`; same behaviour) and
synth.pool (its `out` already names the pool byte limit). 7 entries edited:

- model.query_index: `does` now says the cache is keyed on content and key order and the universe tables are built from the canonical document; verbs for `fact_map` and the last-wins fact map.
- model.diff: verbs for the absent synth extra, recorded as not-derivable synthesis (issue 323).
- model.validation: verbs for the YAML depth cap the model parser now enforces.
- model.population_loading: verbs for the YAML depth cap the population parser now enforces.
- cli.exp_command: verbs for the portable prompt, which names the contract by digest, and for reading the contract once.
- exp.acceptance: verbs for `SessionEvidenceJson`, the bounded JSON decode in front of each version dispatcher.
- infra.text_output: verbs for the canonical payload refusing non-finite numbers.

### Suggested code changes

| # | Kind | What | Where | Size | Checked how |
|---|---|---|---|---|---|
| 5 | Duplicate | Two `model_validate_json` overrides still repeat the body `SessionEvidenceJson` now holds | src/gnd/exp/session_contract.py:1138, src/gnd/exp/session_records.py:409 | small | read both overrides and the mixin at src/gnd/exp/session_eval.py:1185 |

`SessionEvidenceJson` decodes through the shared bounded reader and hands the document
to `model_validate`. `DataDrivenContract` and `DeclaredLaunchIntent` do the same in
their own overrides. The contract module cannot import the mixin from `session_eval.py`,
which imports it, so sharing it means moving the mixin lower (beside the contract or
into the input policy). The overrides in `evolve/models.py` use their own decoder and
were not compared.

### Searches tried

- "yaml depth cap" -> infra.input_policy, then model.population_loading and model.validation
- "portable prompt contract digest" -> cli.exp_command, then exp.schema
- "diff without synth extra" -> model.diff
- "bounded json decode version dispatch" -> exp.acceptance
