# GND code refactoring — layered core, shared infrastructure, thin CLI

**Status:** approved r2 with a gate erratum, 2026-10-05. The owner asked
for a milestone built around code refactoring, and this document is that
plan. Candidate r1 (`81f0362`) and candidate r2 (`145ce95`) each received
a six-of-six light panel review ([r1 record](../001-panel.md),
[r2 record](../002-panel.md)). r2 repaired every agreed concern group from
the r1 review and all six of its divergent views (see *r2 changes* at the
end). The owner approved r2 at the plan gate on 2026-10-05, together with
a text-only erratum (RF-R1, predicate 1, the RF5-C2 reference and this
paragraph), rulings RF-D4, RF-D6, RF-D8 and RF-D10 to RF-D13, and the
routing of residual concerns in [002-panel.md](../002-panel.md)
([gate record](../003-plan-gate.md)). The panel opinions cover the r1 and
r2 bytes only; no review covers the erratum.

(e1) **Erratum e1, 2026-10-05** ([record](../005-plan-erratum.md)): a
text-only update after RF0 ([record](../004-phase-RF0.md)). It brings this
plan into line with rulings and measurements already recorded and adds no
new decision. Every changed site is tagged `(e1)`.

Owner rulings so far are listed in section 10. (e1) All three conditions
for editing `src/gnd` now hold: the plan gate passed
([003](../003-plan-gate.md)), the RF0 record states the authority handoff
([004](../004-phase-RF0.md)), and RF-D2 is satisfied (section 10). Code
edits begin at RF2, after RF1 is recorded.

**Inspection baseline:** `7e08e1e` for r1 and r2. (e1) The measured
baseline is now `19b131b` (this branch merged with `main` `cbb9783`): see
[rf0-baseline.md](rf0-baseline.md), which supersedes the audit's numbers.
Input:
[architecture audit](../../../../docs/development/architecture-audit.md),
a read-only audit taken at `cf4c1d7` that is explicitly non-authoritative.
For r1 only the audit's scope numbers were re-measured at `7e08e1e`: 148
modules, 104,062 lines excluding skills and examples; `cli.py` 9,088,
`model.py` 5,157 and `checker.py` 5,143 lines. **Every other number in this
plan is an audit claim that has not been re-proved.** Where such a number
appears it is marked *(audit)*, and no criterion depends on it. Criteria
are stated over the inventory that RF0 measures.

## Thesis and completion predicates

GND's structure no longer matches its intended layers. The audit reports
that the core forms a 13-module import cycle once lazy imports are counted
*(audit)*. It also reports that shared primitives (canonical JSON, digests,
safe filesystem writes, strict loading) are copied, with some copies
diverged, and `cli.py` is where most features end up. We restructure in
small, behavior-preserving steps: pin current behavior first, then move
code. This milestone changes no observable behavior. Every tightening is
deferred (RF-D7).

The milestone can close when all of the following hold:

1. **Behavior pinned:** the RF1 characterization suite (section 4, RF1) was
   green on the pre-move code and is green at close. No pin's expected
   value has changed.
2. **Layering holds:** every module under `src/gnd` (skills and examples
   excluded) has an entry in the committed layer map. The layering test runs
   over every layer of the map with no xfail marker, and fails on any import
   from a lower layer to a higher one (lazy imports included) that is not
   on its allow-list. Each allow-list entry names a reason and the
   successor work that would remove it. The RF0 tool reports no strongly
   connected component that spans more than one module in the model,
   population, checking or semantics layers.
3. **One home per primitive:** every family that the RF0 family list marks
   identical has exactly one definition. Every family marked diverged keeps
   its variants, each pinned byte for byte, as RF-D11 rules.
4. **Thin entry points:** `cli.py` is at most 2,500 lines. The RF0 tool's
   entry-point rule (RF5-C2) reports no violation: each
   `commands/<group>.py` module imports domain behavior only from
   `gnd.api`, a lane `service` module, `gnd.exits`, `commands/_output` or
   the named allow-list.
5. **Honest measurements:** a before/after table (SCCs, private
   cross-module imports, duplicate counts, largest-module sizes) is
   committed at close. (e1) Co-change pairs were removed: they cannot be
   measured in this repository's history (RF0 D3), and the audit's
   private-history figures stay unverifiable. Every target is met against its final
   owner-ruled value (RF-D13). Each original target that was missed and
   re-targeted is listed with its measured value and the ruling that
   changed it.

## 0. Binding design rules

The [phase protocol](../../../../.codex/skills/process-phase/SKILL.md), its
[standing rules](../../../../.codex/skills/process-phase/references/standing-rules.md)
and [verification selection](../../../../.codex/skills/process-phase/references/verification-selection.md)
are the baseline. In addition:

| Rule | Requirement |
|---|---|
| RF-R1 — Behavior-preserving, without exception | Moves and merges preserve CLI and API names, schemas, exit codes, messages, refusals, deterministic output bytes and digests. This milestone hosts no observable change. A change found to be necessary is recorded as an open question for the RF7 successor. Admitting an observable change into this milestone requires a plan revision, not a phase-level exception. |
| RF-R2 — Bytes are contracts | Canonical encoders and digest helpers move verbatim. Variant encoders are never merged. A digest helper with a different meaning is renamed under RF-D10, not unified with the others. |
| RF-R3 — Pin before move | A phase may move or re-route code only on surfaces that RF1 pins. A spec that touches an unpinned surface first adds pins for it, and they must be green on the pre-move code. A move that needs a pin's expected value changed has failed. |
| RF-R4 — Atomic move units | A move unit is one commit containing the move itself, its re-exports, its updates to `monkeypatch` targets and its widened source scans, with no edit to the moved code. Each move unit is green on its own against the phase's verification selection, so no commit leaves a patch or scan test red. Edits to moved code land in later commits. |
| RF-R5 — Compatibility shims are inventoried | Old import paths and old names stay importable through re-exports listed in `notes/shim-inventory.md`, each with its retirement trigger (RF-D5). Re-exports do not carry patches across, so every `monkeypatch` of a moved name is pointed at the new location within the same move unit. |
| RF-R6 — Source scans must not shrink | Tests that scan source text (`inspect.getsource`, reads of `cli.py`, "module stays unloaded" checks) widen to every new module within the same move unit. Each such test asserts that its scanned set covers every module in its declared scope. |
| RF-R7 — One authority per unit | All work happens in `gnd-public` (RF-D1). The handoff is stated in the RF0 record. The public-launch ledger `.gnd-planning/milestones/public-launch/migration/units.json`, and the distribution-lane test `tests/test_public_distribution.py::test_curated_manifest_and_source_owned_ledger` that guards it, are not edited before the public-launch Phase 4 candidate sign-off (RF-D2, RF-D12). At each phase gate the owner attests that the source repository took no change to the handed-off paths. If the source is reachable, the gate also records a high-water-mark comparison; otherwise the record says the control rests on attestation. |
| RF-R8 — Release identity changes on every edit | `production_identity` hashes every `src/gnd/**/*.py` file by path, and the distribution-lane manifest pins the source bytes. Prior release or assurance evidence is never reused over refactored bytes, and unavailable evidence is reported as unavailable. |
| RF-R9 — Measured, non-vacuous budgets | Every numeric target in a spec comes from the RF0 tool's measurement at that phase's base commit and is strictly better than that baseline. The owner approves each target at the spec gate, and a target equal to the baseline is refused. Each spec also states a touched-file and moved-line budget. A target that proves unreachable stops the phase and returns it to the owner gate with the measured value. A metric that gets worse without a recorded reason is a review finding. |
| RF-R10 — No feature work | No new semantic family, CLI command, flag or schema version. Defects found along the way become open questions unless a decision row brings the fix into scope. |
| RF-R11 — Focused but honest verification | The reduced v6.3 selection applies. Model, checker and CLI moves affect almost every consumer, so each spec measures its impact closure instead of assuming it is small. Running the whole default lane is a named selection, made deliberately. |

**Standard move criteria.** Every phase that moves code (RF2, RF3, RF4, RF5,
RF6 and RF8) carries these criteria in addition to its own:

- **SM1** — every RF1 pin is unchanged.
- **SM2** — every name moved in the phase is listed in the shim inventory and
  importable under its old path. For each `monkeypatch` of a moved name, a
  test patches the new location and observes the effect.
- **SM3** — every source-scan and "module stays unloaded" test covers each
  module the phase introduces, as its own coverage assertion checks.
- **SM4** — every new module has an entry in the layer map, and the
  layering test still passes for every layer already declared clean.

## 1. Scope

**In scope:** the restructurings in the audit's *Better abstractions* and
*Suggested order of work* sections, the duplicate-helper families that RF0
confirms, the wrong-way imports that RF0 confirms, and the tool, layer map
and characterization tests they require.

**Deferred to a successor milestone by RF-D7 (not in scope):** tightening
the safe-filesystem path rules, refusing duplicate-key or non-finite JSON,
YAML guards on the two unguarded loaders, strict ISO datetime parsing,
switching the primitive resolver to strict semantics (RF-D6), merging any
diverged helper family (RF-D11), and changing message text (RF-D8). Each of
these changes observable behavior.

## 2. Artifacts and record homes

Records go in `.gnd-planning/milestones/code-refactoring/`, following the
[record contract](../../../../src/gnd/skills/gnd-orm-core/references/milestone-record-format.md):

- `notes/phase-N-spec.md`: harvested obligations, exact cases, decisions,
  measured budgets and the verification-selection ledger.
- `notes/shim-inventory.md`: each compatibility re-export with its old path,
  new path, introducing phase and retirement trigger.
- `notes/helper-families.md`: the RF0 family list, each family marked
  identical or diverged, with its sites.
- `evidence/metrics-<phase>.json`: tool output at the phase's base and head
  commits, bound by digest.
- `NNN-phase-N.md`: append-only completion records.

The layer map and the tool live under `tools/`, outside `src/gnd`.

## 3. Sequence

**RF0 baseline → RF1 characterization → RF2 identical helpers → RF3 core
cycle → RF4 peripheral layering → RF5 CLI command groups → RF6 model query
layer and constraint registry → RF8 session profile.**

RF7 is deferred (RF-D7) and is not part of this chain. RF0 and RF1 do not
edit `src/gnd`. (e1) RF-D2 is satisfied, so RF2 may start as soon as the
RF1 record is committed. Every phase from
RF2 on is behavior-preserving, with no exception (RF-R1). RF8 carries the
highest risk and comes last so that it can rely on everything before it.

## 4. Phases

### RF0 — Baseline, authority and measurement

**Outcome:** a tool and a layer map that every later phase uses, a
re-measured audit, and a recorded authority handoff.

Commit an AST import-graph tool under `tools/`. It reports module-level and
lazy edges, strongly connected components, imports of another module's
private names, fan-in and fan-out, duplicate-helper candidates by name and
body similarity, and the entry-point rule of RF5-C2. Commit a layer map that
assigns every module under `src/gnd` to a layer, using the audit's
component map as its starting point, and to a lane where one applies.
Re-measure every row of the audit's summary and every cycle the audit
names. Commit `notes/helper-families.md`. Inventory the pin sites: tests
that monkeypatch `gnd.cli` privates, test imports of
`synth.assemble`/`synth.mutate` privates, source-scan tests, the `cli.py`
path pins, the distribution manifest, and packaged skills that cite module
paths.

State the handoff of the `runtime` and `test-acceptance` units to
`gnd-public` in the RF0 record (RF-D1). Do not edit the public-launch
ledger or its test (RF-R7). Record RF-D1, RF-D2 and RF-D7 as already ruled,
and bring RF-D3 to its ruling.

**Criteria:**
- RF0-C1 — the tool's output is byte-identical across two runs.
- RF0-C2 — every cycle the audit names (core, assurance, synth
  `assemble`↔`mutate`, `api`↔`diff`, session) and every new SCC the tool
  finds is listed as confirmed, refuted or new. Each difference from the
  audit names the specific edge, confirmed by hand at its source line.
- RF0-C3 — every audit summary row is marked confirmed or refuted, with its
  measured value.
- RF0-C4 — the layer map covers every module, and a test fails on any
  module that has no entry.
- RF0-C5 — the pin-site inventory and the helper-family list are counted at
  execution time, not copied from the audit.
- RF0-C6 — the RF0 record contains the handoff statement and the RF-D3
  ruling.

### RF1 — Characterization tests

**Outcome:** current behavior is pinned on every surface that RF2–RF8 move
or re-route.

(e1) Obligations RF0 routed here (open questions in
[004-phase-RF0.md](../004-phase-RF0.md)): RF0-OQ2 (unify the two
alias resolvers in `tools/gnd_arch.py`), and RF0-OQ3 (the per-edge strict
xfail list is the 27 wrong-way edges in `evidence/metrics-RF0.json`, with
`declared_clean` = entry, infrastructure). The RF1 budget is set at its
spec gate (002-panel routing F4).

Pin the following:
- the parser tree, help text and exit-code map of each command;
- the exact bytes of every canonical-JSON variant on shared inputs
  (non-ASCII text, NaN, nested ordering, trailing newlines);
- the three `model_digest` meanings;
- both primitive-resolver semantics (`inherits_reference` truthy versus
  `is True`);
- the ISO-datetime parse sites;
- over a fixture corpus, checker verdicts together with the order and text
  of their issues;
- `diff` output;
- the accept/refuse table of each safe-filesystem helper over a fixed path
  set;
- assurance outputs;
- synth-oracle expected states;
- `agent_cli` exit codes and stream handling, against a fake subprocess.

For sessions, pin one golden replay per contract version and path (fresh
run, resume, reconstruct, unknown version). Nondeterministic fields in the
evidence bytes are either normalized by a declared rule or excluded, and
each such field is named.

Add the layering test as a strict xfail (`strict=True`) scoped to the model,
population, checking and semantics layers of the map. Its scope widens
through SM4.

**Criteria:**
- RF1-C1 — every pin fails against a seeded mutation of the code it pins.
- RF1-C2 — the diff contains only test, fixture and tool files.
- RF1-C3 — every diverged family in `notes/helper-families.md` has a pin per
  variant.
- RF1-C4 — every surface named by a later phase's work appears in the pin
  inventory, and the RF1 record maps each one to its tests.

**Shape:** corpus-first by default, because this phase is about serialized
formats and exit codes.

### RF2 — Consolidate the identical helpers

Merge every site that the family list marks identical: canonical bytes
(the audit reports 11 sites *(audit)*) into
`canonical_bytes(v, *, newline, indent)`, plus `sha256_hex`, `Sha256` and
`is_sha256_hex` in `artifacts`. Move all exit codes into `exits.py`. Add
`issues_from_validation_error(err, rule_id)`. Route hand-built constraint
refs through `address.positional_constraint_ref`. Rename the three
`model_digest` functions under RF-D10. Variant encoders stay as they are.

**Criteria:** SM1–SM4. RF2-C1 — each family the list marks identical has
exactly one definition. RF2-C2 — the diff contains no edit to a variant
encoder. RF2-C3 — each old `model_digest` name is still importable, listed
in the shim inventory, and absent from every pinned byte stream and digest
input.

### RF3 — Break the core cycle

Add the leaf modules `errors.py`, `documents.py`, `values.py` and
`universe.py`. Add one primitive-resolver entry point that keeps both
semantics behind an explicit, pinned variant parameter, with no caller
changing semantics (RF-D6). Give the checker a public `effective_view()`
and move `applicable_scope_ids` up a layer. Before any split, rename the
in-place rebinding in `checker.py` (`check`, `_PHASE3_LEGACY_CHECK`,
`_evaluate_derivations`, `_constraint_view`). Keep the derivation-term
ContextVar reachable from both validation and analysis.

**Criteria:** SM1–SM4. RF3-C1 — the core layers contain no multi-module SCC,
lazy edges counted, and the layering test passes with its xfail marker
removed. RF3-C2 — the core's private-import count meets the RF-R9 target.
RF3-C3 — every `semantic_registry` `owner=` string resolves to an existing
function (new test).

### RF4 — Peripheral layering

Make the safe-filesystem functions public in `safefs.py` as a move only;
tightening is deferred. Split `agent_cli` into `process.py` and `agents.py`.
Have `diff` call checker and admission directly instead of going through
`api`. Make the synth oracle public as `synth/oracle/`. Turn the assurance
modules into a `gnd/assurance/` package ordered `_wire → core → inheritance
→ claims → evidence`, with shims under the old names.

**Criteria:** SM1–SM4. RF4-C1 — no multi-module SCC remains among the
modules of each cycle that RF0 confirmed for this phase; a refuted cycle is
recorded as already satisfied. RF4-C2 — no module the map assigns to a lane
has an import edge to `gnd.install`, except edges the spec names with a
reason. RF4-C3 — every private-import edge from `synth.boundary` to
`synth.mutate` in the RF0 inventory (the audit reports 47 *(audit)*) is
replaced by a public `synth.oracle` import. RF4-C4 — the layering test's
scope covers every layer of the map, and the test passes. Any remaining
wrong-way edge is on the allow-list of predicate 2, and the spec names it.

### RF5 — CLI command groups

Add `commands/<group>.py` modules, each with `add_parsers()`,
`set_defaults(handler=)` and an optional `check_args()`. Move the thin groups
first (validate/check/diff, conformance, solve, lifecycle), then the medium
ones (review, exp, evolve), then pull services out of the heavy handlers
(verify, synth, measure, doccheck/fidelity, codegen, recovery inventory) into
lane `service.py` modules. `cli.py` stays as a file. Shared output envelopes
move to `commands/_output.py`.

**Criteria:** SM1–SM4. RF5-C1 — `cli.py` is at most 2,500 lines, and at
most the lower ceiling the spec sets under RF-R9. RF5-C2 — the RF0 tool's
entry-point rule reports no violation. That rule permits imports from
`gnd.api`, lane `service` modules, `gnd.exits`, `commands/_output` and an
allow-list that the spec names with a reason for each entry.

**Parts:** RF5 may be split into at most three numbered parts, each with its
own spec gate and record. A fourth part needs a new owner ruling.

### RF6 — Model query layer and constraint-family registry

Add a read-only `ModelIndex`, cached by model digest, for id lookup,
role → object type, supertype closure, primitive resolution and constraint
iteration with canonical refs. Add one registry entry per constraint family
(adapter, evaluator, witness, message, scope, implemented flag) to replace
the if/elif chains, following the existing `_SEMANTIC_RULES` pattern. Only
then split `model.py` and `checker.py` into packages along their existing
sections.

**Criteria:** SM1–SM4. RF6-C1 — outside the model package and `ModelIndex`,
the code makes no direct read of `fact_types` or `.get("roles")`, apart from
sites on a spec allow-list that states a reason for each. RF6-C2 — a test
that adds a fake family touches only its registry entry. RF6-C3 — a
`ModelIndex` built over a model that is later mutated is never served stale
(new test). RF6-C4 — the package split stays within its moved-line and
touched-file budget. Post-split module sizes are recorded in
`evidence/metrics-RF6.json`, and every old import path of `gnd.model` and
`gnd.checker` stays importable.

**Parts:** RF6a covers the index and the registry, and RF6b covers the
package split. Each has its own spec gate and record.

### RF7 — Tightening (deferred by RF-D7; not executed)

Kept only to describe the successor work, and carried as an open question at
milestone close. Its items are the safefs path validator (`./a`,
backslashes, final-directory-only checks), strict JSON loading (duplicate
keys, `1e999`, depth), YAML guards for `evolve/service.py` and
`export/souffle.py`, strict ISO datetime parsing, strict resolver semantics
(RF-D6), merging diverged families (RF-D11), and the stale "unknown version"
message text (RF-D8). This milestone has no RF7 criteria.

### RF8 — Session profile and the v7 merge

Add a `SessionProfile`, built once in `DataDrivenContract.model_validate`.
Replace the inline version mappings and the `in {7, 8}` checks with profile
lookups. Make `session_v7.run` and `reconstruct` strategy hooks. Expose
`SessionStore.best_identity()` in place of `_v7_best`. Name the version-8
literal (non-observable, RF-D8). (e1) The first assignment of
`SESSION_CONTRACT_VERSION` is **not** dead: `exp/session_contract.py:482`
captures it as `V2_SESSION_CONTRACT_VERSION` for the frozen v2 reader
(rf0-baseline A13), so RF8 leaves it in place.

**Criteria:** SM1–SM4. RF8-C1 — every RF1 session replay (version × path)
produces identical normalized evidence bytes and identical resume behavior.
RF8-C2 — `session_v7.py` holds only strategy hooks, or is removed behind a
shim. RF8-C3 — no multi-module SCC remains among the session modules that
RF0 confirmed; a refuted cycle is recorded as already satisfied.

## 5. Development skills and documentation surfaces

| Surface | Treatment | Phase |
|---|---|---|
| `docs/development/architecture-audit.md` | Stays a historical input. The RF0 record holds the re-measured successor numbers. | RF0 |
| `CONTRIBUTING.md`, `AGENTS.md` | Describe the layer map, the `commands/` pattern, `safefs`, `ModelIndex` and the shim policy once they exist. | RF3–RF6 |
| Packaged skills that cite module paths | Pin sites are counted at each spec gate and updated in the move unit that moves the module. | per phase |
| `tests/test_public_distribution.py`, distribution manifest | Update procedure follows RF-D3. The ledger test changes only after the public-launch Phase 4 candidate sign-off (RF-R7). | RF0 ruling; first edit at RF2 |

## 6. Risks and stop conditions

| Risk | Control or stop |
|---|---|
| A move changes digest-bound bytes | RF1 byte pins and RF-R2. A changed pin stops the phase. |
| A move or re-route changes verdicts, issue order or outputs | RF1's behavior pins (RF-R3, SM1). A surface without pins cannot be moved. |
| Monkeypatches silently stop working after a move | RF-R4 atomic move units and SM2's observed-effect test. |
| Source-scan safety tests check less after a split | RF-R6 and SM3 coverage assertions. |
| Release evidence is invalidated mid-launch | (e1) No longer applies: public-launch is closed, and Phase 5 rebuilds its candidate from the then-current commit (RF-D2). Phase 5's history scan covers refactor commits |
| Two repositories edit `runtime` | RF-D1 and RF-R7 attestation at each gate. A source-side edit is a stop. |
| Diverged helpers get merged | RF-D11 keeps them separate. Merging is deferred successor work. |
| Phases grow into rewrites | RF-R9 budgets, the RF5 limit of three parts, the RF6a/RF6b split. An overrun returns to the owner gate. |
| The milestone drifts | If two consecutive phases miss their original RF-R9 target (RF-D13), the owner re-plans before the next phase begins. |
| Measurements mislead (fewer cycles, same coupling) | The close table reports private imports and co-change alongside SCCs. |
| Owner strings, docs and skills keep naming old paths | RF3-C3 resolution test and pin-site counts at every gate. |

## 7. Out of scope

New semantics, CLI commands, flags or schema versions. Renaming the
distribution, import or executable. Deleting `cli.py`. Performance work.
Recertification or new assurance claims. Repairing the broad historical
suite. All RF7 items listed above (RF-D7). Discharging source-owned open
questions without an explicit transfer. The following carryovers look
related but stay with their source owner unless a ruling transfers them:
`OQ-V72-P1-ARTIFACT-COPIES`, `OQ-V52-CLOSE-CANONJSON-1`,
`OQ-V52-P1-IMPORTWALK-1`, `OQ-V63-CLOSE-HELPER-TAIL-1`.

## 8. Execution and review protocol

This is a milestone plan, not an invocation of `process-phase`. r1 was
reviewed by a six-of-six light panel ([record](../001-panel.md)). The bound
on review rounds was declared on 2026-10-05: r2 gets at most one more
round. After that, residual concerns go to the RF0 spec gate as recorded
open questions instead of another plan round. The owner plan gate follows.

After the gate, each phase follows `process-phase`: harvest obligations,
write the spec and stop, owner gate, implement and verify, adversarial diff
review, refactoring review, record and commit. The default is `auto=false`.
Delegation granted for public-launch does not carry over to this milestone.

## 9. Verification selection

| Phase | Mandatory focused obligation | Starting points (exact commands belong in the spec) |
|---|---|---|
| RF0 | Deterministic tool output; cycle and audit-row confirmation; complete layer map | The tool's own tests. Audit rows. |
| RF1 | Every pin fails under a seeded mutation; pin inventory covers later phases | New characterization tests. Existing CLI, exit, checker and session tests. |
| RF2 | SM1–SM4; one definition per identical family | Byte pins, `tests/test_checker_families.py`, artifact consumers |
| RF3 | SM1–SM4; layering test without xfail; owner-string resolution | Checker, model, population, references and transition controls |
| RF4 | SM1–SM4; confirmed SCCs removed; lane-to-`install` edge rule; layering test over every layer | Installer/doctor, assurance, synth, agent-runner controls |
| RF5 | SM1–SM4; `cli.py` ceiling; entry-point rule | CLI tests and the RF0-counted files that patch `gnd.cli` |
| RF6 | SM1–SM4; registry extension test; index staleness test; split budget | Checker families, verbalize, semantic adapter controls |
| RF7 | Not executed (RF-D7) | — |
| RF8 | SM1–SM4; replays identical per version and path | `exp` session, store, close and judgments controls |

Each spec records `run`, `inherit` or `cadence` for every selection, with its
input boundary and invalidation trigger. A moved file invalidates inherited
results for everything that imports it.

## 10. Owner decisions and open planning questions

**Ruled by the owner.** These are not reopened by any phase.

| Decision | Ruling |
|---|---|
| RF-D1 — Execution authority | 2026-10-05: "everything happens on the gnd-public". The handoff of `runtime` and `test-acceptance` is stated in the RF0 record. The public-launch ledger follows RF-R7. |
| RF-D2 — Sequencing with public-launch | (e1) **Satisfied, 2026-10-05**, by owner ruling under RF-D12, recorded in the RF0 spec's owner amendment 2. Public-launch (renamed gnd-public-migration) recorded the Phase 3 acceptance (`004`), the Phase 4 sign-off (`008`) and its close (`009`). The close defers Phase 5, and Phase 5 will rebuild its candidate from the then-current commit, so there is no tag condition. RF2 may start once RF1 is recorded. Original text, superseded: 2026-10-05, amended the same day after the r1 review. RF2 and later phases start only after the public-launch Phase 3 acceptance and the Phase 4 candidate sign-off are recorded, the signed-off commit is tagged, and public-launch records that Phase 5 publishes from that tag, with launch fixes landing on a release branch and merging forward. Recording that is a public-launch act: this plan cannot bind public-launch, so RF2 waits for it. The Phase 5 history inspection also covers refactor commits. RF0 and RF1 may proceed after the plan gate. |
| RF-D7 — Tightening scope | 2026-10-05: RF7 is deferred to a successor milestone in full, including the alias/size guards for the two unguarded YAML loaders (`evolve/service.py:186`, `export/souffle.py:61`). The owner can pull any sub-part forward at a later phase gate. A spot check on 2026-10-05 found that the installer path validator accepts `./a` and `a\b` but refuses `..\x` and `a/../b`, so the audit's "looser" claim concerns unusual names, not traversal. |
| RF-D4 — Milestone name | 2026-10-05, at the plan gate: accepted as proposed. `code-refactoring`, which uses no semantic version number. |
| RF-D6 — Divergent primitive resolver | 2026-10-05, at the plan gate: accepted as proposed. Keep both semantics behind a pinned variant parameter. Switching any caller to strict `is True` is RF7 successor work. |
| RF-D8 — Small defects | 2026-10-05, at the plan gate: accepted as proposed. In RF8, name the version-8 literal (non-observable). (e1) The removal of the first `SESSION_CONTRACT_VERSION` assignment is withdrawn: that assignment is live (rf0-baseline A13). Rename `value_domain._in_range` in RF6 under RF-D10. The "unknown version" message text is RF7 successor work. |
| RF-D10 — Renames and visibility changes | 2026-10-05, at the plan gate: accepted as proposed. Renaming a function or making it public is non-observable when the old name stays importable through a listed shim and appears in no pinned byte stream, digest input or message. Any other rename needs its own ruling. This covers the `model_digest` renames, `safefs`, `synth.oracle`, `SessionStore.best_identity()` and the `checker.py` rebinding renames. |
| RF-D11 — Diverged helper families | 2026-10-05, at the plan gate: accepted as proposed. Every family that RF0 marks diverged keeps its variants, each pinned byte for byte. Merging is RF7 successor work. |
| RF-D12 — Public-launch gate name and stall route | 2026-10-05, at the plan gate. "Phase 4 candidate sign-off" is the single name for the public-launch gate throughout this plan. If public-launch has not recorded the RF-D2 conditions by the time the RF1 record is committed, the owner either re-plans around RF0 and RF1 or rules a revised sequence before any further phase starts. |
| RF-D13 — Missed targets | 2026-10-05, at the plan gate. A missed RF-R9 target or completion ceiling stops the phase at the owner gate. The owner may re-target with a recorded ruling that states the measured value. The milestone closes against the final ruled targets, and the close table lists every original target that was missed. |

**Open.** These are proposals awaiting the named phase gate. None of them
is an approval.

| Decision | Proposed default | Resolve by |
|---|---|---|
| RF-D3 — Distribution manifest and release evidence | Each phase updates the curated manifest as a recorded adaptation and reports `production_identity` as changed and unavailable until the next release regenerates it. | RF0 |
| RF-D5 — Shim retirement | Shims stay at least until the first public release after RF6. Retiring them is a later, separately approved phase. | RF2 |
| RF-D9 — Approval instrument | Corpus-first for RF1. Spec prose for the move phases. | Each spec gate |

## r2 changes

Fix numbers refer to the prioritized fixes in the
[r1 panel report](../evidence/plan-review-r1/PANEL-REVIEW.md).

| r1 concern | r2 change |
|---|---|
| F1 — audit counts used as criteria | Baseline paragraph, *(audit)* markers, criteria stated over the RF0 inventory (RF2, RF4-C3, section 9) |
| F2 — RF0 ledger path, timing and circular gate | Status paragraph, RF-R7, RF0 body, RF-D2, section 5 |
| F3 — RF1 pins miss later surfaces | RF-R3, RF1 pin list, RF1-C4, SM1 in every move phase |
| F4 — vacuous targets | RF-R9, RF5 parts limit, the "milestone drifts" risk row |
| F5 — predicate 4 cannot fail | Predicate 4, RF5-C1 and RF5-C2 |
| F6 — no layer map | RF0 layer map, RF0-C4, predicate 2, RF4-C2, RF4-C4, SM4 |
| F7 — renames versus RF-R1 | RF-D10, RF2-C3 |
| F8 — patch and scan rules enforced only in RF5 | RF-R4 atomic move units, SM2 and SM3 |
| F9 — observable changes inside preserving phases | RF-R1 with no exceptions, RF3 resolver, RF-D6, RF-D8 |
| F10 — RF0-C1 escape hatch and unconfirmed SCCs | RF0-C2, RF4-C1, RF8-C3 |
| F11 — ruled decisions treated as open | Section 10 split into ruled and open; RF0 body; RF0-C6 |
| F12 — RF7 deferral not reflected | Sections 1, 3, 4 (RF7), 7 and 9 |
| Divergent: RF-D2 ends before publication | RF-D2 amended (tagged release commit), owner-accepted 2026-10-05 |
| Divergent: thin session replay | RF1 session replays per version × path; RF8-C1 |
| Divergent: source-side edits undetectable | RF-R7 attestation and high-water mark |
| Divergent: non-strict xfail | RF1 strict xfail |
| Divergent: diverged families not enumerated | `notes/helper-families.md`, RF1-C3, RF-D11, predicate 3 |
| Divergent: RF6 split uncovered | RF6-C4, RF6a/RF6b parts |
