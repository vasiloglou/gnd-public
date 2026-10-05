# GND code refactoring — layered core, shared infrastructure, thin CLI

**Status:** candidate r1, 2026-10-05. The owner asked for a milestone built
around code refactoring. This document is that plan. It does not approve the
plan or approve any phase. The owner ruled RF-D1 on 2026-10-05: all work
happens in `gnd-public`. The owner accepted the RF-D2 and RF-D7 proposals
the same day. Nothing in `src/gnd` changes until the plan gate, the RF0
handoff record, and the public-launch sign-offs that RF-D2 names.

**Inspection baseline:** `7e08e1e`. Input:
[architecture audit](../../../../docs/development/architecture-audit.md),
a read-only audit taken at `cf4c1d7` that is explicitly non-authoritative.
For this draft, the audit's scope numbers were re-measured at `7e08e1e`
(148 modules, 104,062 lines excluding skills and examples; `cli.py` 9,088,
`model.py` 5,157, `checker.py` 5,143 lines). No other audit claim was
re-proved. RF0 re-measures all of them with a committed tool.

## Thesis and completion predicates

GND's structure no longer matches its intended layers. The core is a
13-module import cycle once lazy imports are counted. Shared primitives (canonical
JSON, digests, safe filesystem writes, strict loading) are copied, and some
copies have diverged. `cli.py` is where most features end up. We restructure
in small, behavior-preserving steps: pin current behavior first, then move
code, and tighten behavior only through separate, explicitly approved
decisions.

The milestone can close when all of the following hold:

1. **Behavior pinned:** every public CLI command's parser tree, help text and
   exit-code map, every canonical-encoder variant's bytes, every
   `model_digest` meaning, and one golden replay per session-contract version
   are characterization tests that were green before the first move and stay
   green at close, unchanged except through recorded compatibility decisions.
2. **Layering holds:** the committed import-graph measurement reports no
   strongly connected component among the model, population, checking and
   semantics layers (lazy imports counted), and a test fails if a
   lower-layer module imports a higher layer.
3. **One home per primitive:** each identical helper family named in RF2 has one
   definition. Each diverged family has either one implementation behind
   an explicit `strict=`/variant parameter whose variants are pinned
   byte-for-byte, or a recorded decision to keep it separate.
4. **Thin entry points:** `cli.py` is a dispatcher over `commands/<group>.py`
   modules, and no command handler holds domain logic that `api.py` or a lane
   `service.py` cannot also reach.
5. **Honest measurements:** a numerical before/after table (cycle sizes,
   private cross-module imports, duplicate counts, largest-module sizes) is
   committed at close, with every target either met or recorded as missed
   along with its reason.

## 0. Binding design rules

The [phase protocol](../../../../.codex/skills/process-phase/SKILL.md), its
[standing rules](../../../../.codex/skills/process-phase/references/standing-rules.md)
and [verification selection](../../../../.codex/skills/process-phase/references/verification-selection.md)
are the baseline. In addition:

| Rule | Requirement |
|---|---|
| RF-R1 — Behavior-preserving by default | Moves and merges preserve CLI/API names, schemas, exit codes, messages, refusals, deterministic output bytes and digests. Any observable change needs its own decision row and owner ruling. Merely sitting in a refactor phase does not authorize it. |
| RF-R2 — Bytes are contracts | Move canonical encoders and digest helpers verbatim. Never merge variant encoders. A digest helper with a different meaning is renamed, not unified. |
| RF-R3 — Pin before move | No module moves until RF1's characterization tests for the touched surface are green on the pre-move code. A move that needs a characterization pin to change has failed. |
| RF-R4 — Move-only diffs are separate | Every move lands as a move-only commit (re-exports included) before any edit to the moved code, so reviewers can check a move without reading semantics. |
| RF-R5 — Compatibility shims are inventoried | Old import paths stay importable through re-exports listed in one shim inventory, each with its retirement trigger. Re-exports do not carry monkeypatches across: every `monkeypatch` of a moved name is re-pointed at the new location in the same phase. |
| RF-R6 — Source scans must not shrink | Tests that scan source text (`inspect.getsource`, reads of `cli.py`, "module stays unloaded" checks) are widened to cover each new module in the same phase. A test asserts that the scanned set covers every module it is meant to cover. |
| RF-R7 — One authority per unit | All work happens in `gnd-public` (RF-D1). The `runtime` and `test-acceptance` units are still recorded as source-owned (`migration/units.json`), so RF0 records their handoff before any phase edits them, and the source repository stops accepting changes to them from then on. |
| RF-R8 — Release identity changes on every edit | `production_identity` hashes every `src/gnd/**/*.py` by path, and the distribution-lane manifest pins source bytes. Prior release or assurance evidence is never reused over refactored bytes. Unavailable evidence is reported as unavailable. |
| RF-R9 — Measured budgets | Each spec states its before/after import-graph metrics, its touched-file and moved-line budget, and its shim count, all taken from the RF0 tool. A metric that gets worse without a recorded reason is a review finding. |
| RF-R10 — No feature work | No new semantic family, CLI command, flag or schema version. Defects found along the way are recorded as open questions unless a decision row puts the fix in scope. |
| RF-R11 — Focused but honest verification | The reduced v6.3 selection applies. Because model, checker and CLI moves affect almost every consumer, each spec measures its impact closure instead of assuming it is small. Running the whole default lane is a named selection, not something to reach for by habit. |

## 1. Scope

**In scope:** the restructurings in the audit's *Better abstractions* and
*Suggested order of work* sections, the duplicate-helper families, the
wrong-way imports, and the characterization tests and measurement tool they
require.

**Not selected without a further decision:** tightening safe-filesystem path
rules, duplicate-key or non-finite JSON refusal, YAML guards on the two
unguarded loaders, and strict ISO datetime parsing. Each refuses inputs that
are accepted today. RF7 owns them as separately approved sub-parts.

## 2. Artifacts and record homes

Records go in `.gnd-planning/milestones/code-refactoring/`, following the
[record contract](../../../../src/gnd/skills/gnd-orm-core/references/milestone-record-format.md):

- `notes/phase-N-spec.md`: harvested obligations, exact cases, decisions,
  measured budgets and the verification-selection ledger.
- `notes/shim-inventory.md`: each compatibility re-export with its old path,
  new path, introducing phase and retirement trigger.
- `evidence/metrics-<phase>.json`: import-graph and duplication measurements
  bound by digest.
- `NNN-phase-N.md`: append-only completion records.

## 3. Sequence

**RF0 baseline → RF1 characterization → RF2 identical helpers → RF3 core
cycle → RF4 peripheral layering → RF5 CLI command groups → RF6 model query
layer and constraint registry → RF7 approved tightening → RF8 session
profile.** RF0–RF1 do not edit `src/gnd`. RF2–RF6 and RF8 are
behavior-preserving. RF7 is the only phase whose purpose is a behavior change.
RF8 carries the highest risk and comes last so it can rely on everything
before it. RF7 is deferred to a successor milestone (RF-D7) and stays in this
plan only as a description of that later work. Under RF-D2, RF0 and RF1 may
run now. RF2 and later wait until public-launch Phase 3 acceptance and the
Phase 4 candidate sign-off are recorded.

## 4. Phases

### RF0 — Baseline, authority and measurement

**Outcome:** a pinned baseline, a recorded handoff of the `runtime` and
`test-acceptance` units to `gnd-public`, and a measurement tool that every
later phase uses.

Commit an AST import-graph tool under `tools/` that reports module-level and
lazy edges, strongly connected components, imports of another module's private
names, fan-in/fan-out, and duplicate-helper counts by name pattern. Re-measure
every number in the audit summary and record agreements and disagreements.
Inventory the pin sites: tests that monkeypatch `gnd.cli` privates, test
imports of `synth.assemble`/`synth.mutate` privates, source-scan tests, the
`cli.py` path pins and the distribution manifest. Record the unit handoff
in `migration/units.json`, and update the test that currently requires every
unit to be source-owned. Settle RF-D2 to RF-D4.

**Criteria:** RF0-C1 the tool's output is deterministic (two runs produce
identical bytes) and reproduces at least the core 13-module SCC, or the record
explains the difference. RF0-C2 every audit summary row is marked
confirmed or refuted, with measured values. RF0-C3 the pin-site inventory is
counted at execution time, not copied from the audit.

### RF1 — Characterization tests

**Outcome:** current behavior is pinned at every surface later phases touch.

Pin the following: the parser tree, help text and exit-code map for each
command; the exact bytes of every canonical-JSON variant on shared inputs,
including non-ASCII text, NaN, nested ordering and trailing newlines; the three
`model_digest` meanings; the two divergent primitive resolvers
(`inherits_reference` truthy versus `is True`); the ISO-datetime parse sites;
and one golden replay per session-contract version, covering evidence bytes
and resume behavior. Add a layering test in xfail mode that RF3 turns green.

**Criteria:** RF1-C1 every pin fails against a seeded mutation of the code it
pins (no pin that cannot fail). RF1-C2 the diff contains only test,
fixture and tool files. RF1-C3 each diverged helper family has a pin per
variant.

**Shape:** corpus-first by default, because this phase is about serialized
formats and exit codes.

### RF2 — Consolidate the identical helpers

Merge the 11 identical canonical-bytes sites into
`canonical_bytes(v, *, newline, indent)`. Add `sha256_hex`, `Sha256` and
`is_sha256_hex` in `artifacts`. Move all exit codes into `exits.py`. Add
`issues_from_validation_error(err, rule_id)`. Route hand-built constraint refs
through `address.positional_constraint_ref`. Rename the three `model_digest`
functions to names that state what each one means. Leave the variant encoders
alone.

**Criteria:** RF2-C1 all RF1 pins are unchanged. RF2-C2 the duplicate counts
for the merged families reach the spec's target. RF2-C3 the diff contains no
edit to a variant encoder.

### RF3 — Break the core cycle

Add leaf modules `errors.py`, `documents.py`, `values.py` and `universe.py`,
plus one primitive resolver, whose `inherits_reference` behavior is decided
from the RF1 pin under RF-D6. Give the checker a public `effective_view()`
and move `applicable_scope_ids` up a layer. Before splitting anything, rename
the in-place rebinding in `checker.py` (`check`, `_PHASE3_LEGACY_CHECK`,
`_evaluate_derivations`, `_constraint_view`). Keep the derivation-term
ContextVar reachable from both validation and analysis.

**Criteria:** RF3-C1 no SCC among the core modules (lazy edges counted), and
the RF1 layering test passes without xfail. RF3-C2 the private-import count
across the core falls by at least the spec's target. RF3-C3 every
`semantic_registry` `owner=` string resolves to an existing function (new test).

### RF4 — Peripheral layering

Make the safe-filesystem functions public in `safefs.py` (move-only; RF7 owns
any tightening). Split `agent_cli` into `process.py` and `agents.py`. Have
`diff` call checker and admission directly instead of going through `api`.
Make the synth oracle public as `synth/oracle/`. Turn the assurance modules
into a `gnd/assurance/` package ordered `_wire → core → inheritance → claims →
evidence`, with shims under the old names.

**Criteria:** RF4-C1 the `assurance`, `synth` and `api↔diff` SCCs are gone.
RF4-C2 no lane imports `install` for filesystem helpers. RF4-C3 the 47
private imports from `synth.boundary` into `synth.mutate` are replaced by public
oracle imports.

### RF5 — CLI command groups

Add `commands/<group>.py` modules, each with `add_parsers()`,
`set_defaults(handler=)` and an optional `check_args()`. Move the thin groups
first (validate/check/diff, conformance, solve, lifecycle), then the medium
ones (review, exp, evolve), then pull services out of the heavy handlers
(verify, synth, measure, doccheck/fidelity, codegen, recovery inventory) into
lane `service.py` modules. `cli.py` stays as a file. Shared output envelopes
move to `commands/_output.py`.

**Criteria:** RF5-C1 the RF1 parser, help and exit pins are unchanged.
RF5-C2 tests that require `gnd.cli` to stay unloaded also cover
`gnd.commands.*`. RF5-C3 `cli.py` shrinks to at most the line budget the spec
declares. RF5-C4 every monkeypatch of a moved name targets the new location.

**Residual:** splitting the heavy handlers may outgrow one phase. If so, the
spec splits RF5 into numbered parts, each with its own record.

### RF6 — Model query layer and constraint-family registry

Add a read-only `ModelIndex`, cached by model digest, for id lookup,
role → object type, supertype closure, primitive resolution and constraint
iteration with canonical refs. Add one registry entry per constraint family
(adapter, evaluator, witness, message, scope, implemented flag) that replaces
the if/elif chains, following the existing `_SEMANTIC_RULES` pattern. Only
then split `model.py` and `checker.py` into packages along their existing
sections.

**Criteria:** RF6-C1 direct reads of `fact_types` and `.get("roles")` outside
the model package fall to the spec's target. RF6-C2 adding a fake family in a
test requires touching only its registry entry. RF6-C3 a `ModelIndex` built
over a model that is later mutated is never served stale (new test).

### RF7 — Approved tightening (deferred by RF-D7)

Not executed in this milestone. The milestone close carries it as an open
question naming the successor milestone. Each item below would be one
sub-part: the safefs path validator
(`./a`, backslashes, final-directory-only checks), strict JSON loading
(duplicate keys, `1e999`, depth), YAML guards for `evolve/service.py` and
`export/souffle.py`, and strict ISO datetime parsing. Each sub-part lands a
red case for an input accepted today, then the refusal, with an explicit entry
in the release notes.

**Criteria:** RF7-C1 every newly refused input has a case that failed before
the change. RF7-C2 no RF1 pin changes except those the decision names.

### RF8 — Session profile and the v7 merge

Add a `SessionProfile` built once in `DataDrivenContract.model_validate`.
Replace inline version mappings and `in {7, 8}` checks with profile lookups.
Make `session_v7.run` and `reconstruct` strategy hooks. Expose
`SessionStore.best_identity()` instead of `_v7_best`. Name the version-8
literal and fix the stale "unknown version" text only under RF-D8.

**Criteria:** RF8-C1 the RF1 golden replays produce identical evidence bytes
and resume behavior for every contract version. RF8-C2 `session_v7.py`
holds only strategy hooks or is removed behind a shim. RF8-C3 the session SCC
is gone.

## 5. Development skills and documentation surfaces

| Surface | Treatment | Phase |
|---|---|---|
| `docs/development/architecture-audit.md` | Stays a historical input. The RF0 record holds the re-measured successor numbers. | RF0 |
| `CONTRIBUTING.md`, `AGENTS.md` | Describe the layers, the `commands/` pattern, `safefs`, `ModelIndex` and the shim policy once they exist. | RF3–RF6 |
| Packaged skills that cite module paths | Pin sites are counted at each spec gate and updated in the phase that moves the module. | per phase |
| `tests/test_public_distribution.py`, distribution manifest | Update procedure decided in RF-D3. | RF0 |

## 6. Risks and stop conditions

| Risk | Control or stop |
|---|---|
| A move changes digest-bound bytes | RF1 byte pins and RF-R2. A changed pin stops the phase. |
| Monkeypatches silently stop working after a move | RF-R5 inventory. Each moved name gets a test that patches the new location and observes an effect. |
| Source-scan safety tests check less after a split | RF-R6 coverage assertion. |
| Release evidence is invalidated mid-launch | RF-D2 sequencing. No refactor commit lands between a release candidate and its sign-off. |
| Two repositories edit `runtime` | RF-D1: `gnd-public` only. RF0 records the handoff; a later source-side edit to these units is a stop. |
| Merging diverged helpers changes verdicts | Diverged families are pinned per variant. Merging them requires RF-D6 or RF7. |
| Phases grow into rewrites | Moved-line and touched-file budgets per spec. Overruns return to the owner gate. |
| Measurements mislead (fewer cycles, same coupling) | The close table reports private imports and co-change alongside SCCs. |
| Owner strings, docs and skills keep naming old paths | Resolution tests (RF3-C3) and pin-site counts at every gate. |

## 7. Out of scope

New semantics, CLI commands, flags or schema versions. Renaming the
distribution, import or executable. Deleting `cli.py`. Performance work.
Recertification or new assurance claims. Repairing the broad historical suite.
Discharging source-owned open questions without an explicit transfer. The
following carryovers look related but stay with their source owner unless a
ruling transfers them: `OQ-V72-P1-ARTIFACT-COPIES`,
`OQ-V52-CLOSE-CANONJSON-1`, `OQ-V52-P1-IMPORTWALK-1`,
`OQ-V63-CLOSE-HELPER-TAIL-1`.

## 8. Execution and review protocol

This is a milestone plan, not an invocation of `process-phase`. The next step
is plan review and the owner plan gate. The plan bar is at least four complete
reviewer responses. Writing this candidate establishes no panel result.

After the gate, each phase follows `process-phase`: harvest obligations,
write the spec and stop, owner gate, implement and verify, adversarial diff
review, refactoring review, record and commit. Default is `auto=false`.
Delegation granted for public-launch does not carry over to this milestone.

## 9. Verification selection

| Phase | Mandatory focused obligation | Starting points (exact commands belong in the spec) |
|---|---|---|
| RF0 | Deterministic tool output, re-measured audit, pin-site inventory | The tool's own tests. Audit rows. |
| RF1 | Every pin fails under a seeded mutation | New characterization tests. Existing CLI, exit and session tests. |
| RF2 | RF1 pins unchanged; duplicate counts | Byte pins, `tests/test_checker_families.py`, artifact consumers |
| RF3 | Layering test green; RF1 pins; owner-string resolution | Checker, model, population, references and transition controls |
| RF4 | SCCs removed; no `install` imports from lanes | Installer/doctor, assurance, synth, agent-runner controls |
| RF5 | Parser, help and exit pins; unloaded-module tests | CLI tests, the 12 files that patch `gnd.cli` |
| RF6 | Registry extension test; index staleness test | Checker families, verbalize, semantic adapter controls |
| RF7 | Red-before-green per newly refused input | Loaders, safefs, datetime consumers |
| RF8 | Golden replays identical per contract version | `exp` session, store, close and judgments controls |

Each spec records `run`, `inherit` or `cadence` together with its input
boundary and invalidation trigger. A moved file invalidates inherited results
for everything that imports it.

## 10. Owner decisions and open planning questions

These are proposals awaiting the plan gate. None of them is an approval.

| Decision | Proposed default | Resolve by |
|---|---|---|
| RF-D1 — Execution authority | **Ruled by the owner, 2026-10-05: "everything happens on the gnd-public".** RF0 records the handoff of `runtime` and `test-acceptance` in the migration ledger. | Ruled |
| RF-D2 — Sequencing with public-launch | **Accepted by the owner, 2026-10-05.** No `src/gnd` edit until the public-launch Phase 3 acceptance and Phase 4 candidate sign-off are recorded, so that retained release artifacts keep describing their bytes. RF0–RF1 may proceed now. | Ruled |
| RF-D3 — Distribution manifest and release evidence | Each phase updates the curated manifest as a recorded adaptation and reports `production_identity` as changed and unavailable until the next release regenerates it. | RF0 |
| RF-D4 — Milestone name | `code-refactoring`, which uses no semantic version number. | Plan gate |
| RF-D5 — Shim retirement | Shims stay at least until the first public release after RF6. Retiring them is a later, separately approved phase. | RF2 |
| RF-D6 — Divergent primitive resolver | Keep `popvalidate`'s strict `is True` semantics, after RF1 shows which callers depend on the looser one. | RF3 spec |
| RF-D7 — Tightening scope | **Accepted by the owner, 2026-10-05.** RF7 is deferred to a successor milestone in full, including the alias/size guards for the two unguarded YAML loaders (`evolve/service.py:186`, `export/souffle.py:61`). The owner can pull any sub-part forward at a later phase gate. A spot check on 2026-10-05 found that the installer path validator accepts `./a` and `a\b` but refuses `..\x` and `a/../b`. The audit's "looser" claim therefore concerns unusual names, not traversal. | Ruled |
| RF-D8 — Small defects (version-8 constant and message, duplicated `SESSION_CONTRACT_VERSION`, `value_domain._in_range` name) | Fix the constant and the double assignment in RF8. Rename `_in_range` in RF6. Changing the message text needs a ruling. | RF6/RF8 specs |
| RF-D9 — Approval instrument | Corpus-first for RF1 and RF7. Spec prose for the move-only phases. | Each spec gate |
