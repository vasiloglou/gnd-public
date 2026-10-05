# Architecture audit: dependency map, duplication, abstractions

Read-only audit of `src/gnd` at commit `cf4c1d7` (5 Oct 2026). Non-authoritative
input for planning a refactoring milestone; nothing here is an approved plan.

- Scope: 148 modules, ~105k lines (`src/gnd/skills` and `src/gnd/examples` excluded).
- Import graph: 454 module-level imports plus 185 imports that occur only inside
  functions (lazy imports).
- Change frequency: git history of the private `gnd` repository (2,098 commits
  since 8 Aug 2026).
- Method: AST import graph, strongly connected components, fan-in/fan-out per
  module and per component, co-change pairs from git, and four read-only code
  reviews (infrastructure duplication, core model, CLI/api, exp/synth/assurance).
  The main claims were checked against the source before writing this down.
  Line numbers refer to `cf4c1d7`.

## Summary

| Finding | Evidence |
|---|---|
| The core is one 13-module cycle | Module-level imports are acyclic, but lazy imports close a loop through `model`, `population`, `popvalidate`, `references`, `terms`, `checker`, `transition`, `semantic_registry`, `semantic_adapter`, `correspondence`, `proof_bridge`, `temporal_guarded`, `extraction_scope`. |
| 189 imports of another module's private names | 47 are `synth.boundary` borrowing from `synth.mutate`. Many are helpers that ended up in the wrong module. |
| Infrastructure primitives are copied, and some copies have diverged | ~51 canonical-JSON helpers in 30 files, ~35 digest helpers in 23 files, ~30 safe-filesystem helpers in 20 files. Some copies produce different bytes. |
| `cli.py` is where features accumulate | 9,088 lines, 150 commits (the next file, `checker.py`, has 67). About 20 of ~35 commands carry their own domain logic and bypass `api.py`. |
| No query layer over the model | `model.fact_types` is read 152 times across 42 files and `.get("roles")` 141 times across 31 files. `checker`+`model` changed together in 23 commits. |
| Session versioning is spread across files | Five independent version axes; the mapping from contract version to the other versions is written inline in at least 9 places; `exp/session_v7.py` is a fork of `exp/session.py`. |

## Component map

Intended layering, top to bottom. Each layer should import only from the layers
below it. Sizes are in thousands of lines; commit counts come from the private repo.

| Layer | Components |
|---|---|
| Entry points | **cli.py** (9.1k, 150 commits), api.py (1.5k, 22), solve.py (1.3k), report.py (0.8k, 23), diff.py, coverage, batch, rai_import |
| Lanes | exp/ (15.5k), synth/ (10.0k), review/ (4.4k), export/ (3.9k), evolve/ (3.4k), codegen/ (3.3k), conformance/ (3.0k), recovery/ (2.8k), measure/ (2.2k), extract/ (1.8k), witness/ (1.3k), fidelity/ (1.0k) |
| Semantics and assurance | semantic_spec / semantic_registry / semantic_adapter (5.5k), correspondence, proof_bridge, temporal_guarded, transition.py (2.2k), assurance_* (5 modules, 2.2k), admission, judgments |
| Checking | **checker.py** (5.1k, 67), verbalize.py (1.0k, 28), verbalize_population, model_verbalization |
| Model and population | **model.py** (5.2k, 51), population, popvalidate, references, terms |
| Infrastructure | artifacts.py (1.7k, 41 importers), json_input, exits, address, atoms, install.py (2.2k), agent_cli.py (1.0k), redaction |

Lazy-import cycles (strongly connected components once lazy imports are counted):

- core (13 modules, listed above)
- `assurance`, `assurance_claims`, `assurance_evidence`, `assurance_inheritance`
- `exp.session`, `session_eval`, `session_judgments`, `session_patch`,
  `session_store`, `session_v7`, `tests_runner`
- `synth.assemble` and `synth.mutate`
- `api` and `diff`

## Imports that point the wrong way

| Back-edge | What it actually needs | Fix |
|---|---|---|
| `model → popvalidate` (model.py:2003, 2649, 2794) | primitive and reference-type resolution, which is a pure model lookup. model.py also keeps a diverged copy, `_resolved_primitive` (model.py:711). | Keep one resolver in a model query module. The two copies treat `inherits_reference` differently (model.py accepts any truthy value; popvalidate requires `is True` and parents), so write tests before merging them. |
| `model → population` (model.py:4883) | the strict JSON parser `_parse_document_bytes` | Move it to a leaf `documents` module |
| `model → references` (model.py:4903–4933) | loading lives in the data module, and `references.validate_declarations` then re-runs both validation layers | Separate `model/load.py` from the model types |
| `terms → model` (terms.py:111) | only the error types `ValidationIssue` and `ModelValidationError` | Move them to a leaf `errors.py` |
| `references`, `proof_bridge`, `semantic_adapter → checker` | checker's private value and universe helpers (`_identity_key`, `_literal`, `_INVALID_LITERAL`, `_instances_of`, `_descendant_closure`, `_denoting_types`, …) | Move them to `values.py` and `universe.py` below the checker |
| `semantic_registry → checker, model, popvalidate, proof_bridge, terms` | all used by one 381-line function, `applicable_scope_ids` (semantic_registry.py:1463), which rebuilds the checker's view from checker privates | Give the checker a public `effective_view()` and move the function up a layer |
| `diff → api` (diff.py:227) | a domain module calls the public facade (`api.check(admission=True)`) | Call checker/admission directly |
| `codegen`, `synth`, `extract`, `evolve`, `cli → install` | the skill installer also serves as the safe-filesystem library (`_atomic_write`, `_descend`, `safe_destination`, `_reject_unsafe_relpath`) | Make these public in a `safefs` module |
| `agent_cli ↔ exp` | `agent_cli` is a bounded process runner plus Claude/Codex adapters; 8 of its 10 importers need only the runner | Split it into `process.py` and `agents.py` |
| `session ↔ session_v7 ↔ session_store` | a forked v7 loop and resume path; `close.py` reads `store._v7_best` | Profile-driven loop (see below) |
| `assurance ↔ evidence ↔ claims ↔ inheritance` | only low-level helpers (`_json`, `_read`, `_relative`, `_sha`, `_closed`, `_strings`) | `gnd/assurance/` package with a shared `_wire` module |
| `synth.assemble ↔ synth.mutate` (assemble.py:1764) | one function, `mutate.expected_state`, the shared ground-truth oracle | `synth/oracle/` |

## Duplicated helpers

"Identical" means the copies can be merged now. "Diverged" means merging
would change behavior or digests.

| Family | Copies | State | Proposed home | Risk |
|---|---|---|---|---|
| Canonical JSON bytes | 11 compact sites agree (artifacts.py:189, assurance_inheritance.py:64, model_verbalization.py:33, evolve/models.py:73, exp/session.py:181, exp/session_eval.py:2558/2663, recovery/verify.py:55, review/report.py:153, review/request.py:598, synth/poolfile.py:127); ~10 variants (non-ASCII escaped, default separators, NaN not refused) | The 11 are identical except whether a trailing newline is included in the hashed bytes | `canonical_bytes(v, *, newline, indent)` in artifacts | Low for the identical sites; **high** for the variants (stored digests, `production_identity`) |
| sha256 hex, `Sha256` type | 6 identical `sha256(...).hexdigest()` helpers; `Sha256` declared 5 times; ~15 hand-written hex checks | Identical | `artifacts.sha256_hex`, `Sha256`, `is_sha256_hex` | Low |
| File digests | synth/provenance, conformance/currency, transition, measure/promote, exp/tests_runner, exp/close | Diverged on symlink handling | one bounded file digest that refuses symlinks | Medium |
| `model_digest` | conformance/currency (file bytes), transition.py:185 (`sha256:` + repr), synth/provenance.py:228 (repr, bare hex) | Three different meanings | Rename; never merge | Low (rename only) |
| Safe filesystem (`_descend`, root opening, path validators, create-new-file writers, `_same_inode`) | install, artifacts, recovery/inventory, recovery/report, exp/session_store, exp/tests_runner, exp/junit, evolve/models; five separate publishers in cli | Diverged: install's path validator is looser (accepts `./a`, backslashes); tests_runner checks only the final directory | `safefs.py`: `open_root`, `descend(create=)`, `safe_parts(strict=)`, `atomic_replace`, `write_new`, `same_inode` | Medium-high, security-sensitive |
| Strict JSON loading | ~12 readers | Diverged: about half accept duplicate keys silently; most accept `1e999` as infinity; depth limits differ | `json_input.strict_loads(raw, *, error, max_depth, finite_numbers)` | Medium (would refuse inputs accepted today) |
| YAML alias/size guard | population.py:392, model.py:72/4874, architecture.py:183, rai_import.py:105, exp/frontmatter.py:70 | Diverged; evolve/service.py:186 and export/souffle.py:61 load YAML with no guard | `yaml_input.safe_load(text, *, single_doc, comment_scanner, error)` | Low-medium |
| Model traversal (`_object_types_by_id`, role → object type, descendant closure, constraint iterators, fact type by id) | 4–7 copies each in popvalidate, checker, synth, extract, model, proof_bridge, rai_import, measure/truth | Mostly identical; some differ in None handling | `ModelIndex` (below) | Low-medium |
| Hand-built constraint refs | assemble.py:1206, 1532, 1669, 1724, 2099; mutate.py:1808; measure/report.py:488 | Built by hand | Existing `address.positional_constraint_ref` | Low |
| CLI output envelopes, warning/error text, exit codes | local `fail()`/`emit()` in synth, measure, verify; 49 branches on output format; exit codes split between `exits.py` and cli.py:189–235; bare 3/13/66/74 in conformance and evolve | Same intent | `commands/_output.py`; all codes in `exits.py` | Low |
| ValidationError → issue list | architecture:225, exp/conclusions:212, exp/spec:255, extract/manifest:378, session_contract:1243, cli:4783 | Identical except the rule id | `issues_from_validation_error(err, rule_id)` | Low |
| ISO datetime parsing | popvalidate:184, model:757/864, checker:2064, semantic_adapter:139, synth/values:271 | Diverged; only 2 sites check the format with a regex first, and the result affects checker verdicts | `parse_iso_datetime(strict=)` | Medium |

## Better abstractions

1. **Read-only model query layer (`ModelIndex`).** Lookups by id, role → object type,
   supertype closure, primitive resolution, and constraint iteration with canonical
   refs. Cache it by model digest, because the model's dicts can be mutated. It
   replaces direct reads of the raw dicts and the private imports between checker,
   popvalidate and synth, and is the main way to stop checker and model from
   changing together.
2. **One registry entry per constraint family.** At least seven if/elif chains
   branch on constraint family: checker's `_is_implemented` (1308),
   `_scope_fact_types` (1405), `_vacuity_message` (1450), `_plain_projected_witness`
   (607), the 411-line `_correspondence_message` (612), semantic_adapter's
   `adapt_constraint` (372), and semantic_spec (2360–2420). One registry entry per
   family (adapter, evaluator, witness, message, scope, implemented flag) would
   follow the existing `_SEMANTIC_RULES` pattern in model.py and explains why
   checker and verbalize change together (19 commits).
3. **A `SessionProfile` per contract version.** Build it once in
   `DataDrivenContract.model_validate`. It holds the feedback, evidence, result and
   launch versions plus feature flags. Every `in {7, 8}` check and every inline
   version mapping becomes a profile lookup, and `session_v7.run`/`reconstruct`
   become strategy hooks in the main loop. Expose `SessionStore.best_identity()`
   instead of `_v7_best`.
4. **One module per command group.** `commands/<group>.py` with `add_parsers()`,
   `set_defaults(handler=)` and an optional `check_args()`, the way witness and
   export already work. Domain logic moves into each lane's `service.py`, as
   conformance and evolve already do, and `api.py` becomes a thin public layer
   over those services. Keep `cli.py` as a file (pinned by
   `tests/test_public_distribution.py:116` and `pyproject.toml`).
5. **An explicit synth oracle module.** Its separation from the checker is
   intentional (rule C1). Making it public as `synth/oracle/`
   (`model_index`, `witness`, `expected`), with `mutate.template(name)` as the entry
   point, replaces the 47 private imports with one public one.
6. **A `gnd/assurance/` package.** Order the modules so dependencies run one way:
   `_wire` → `core` → `inheritance` → `claims` → `evidence`. Keep shims under the
   old module names.

## Suggested order of work

Ordered by payoff against risk. Each step should be its own phase with owner
approval first, keeping current names importable through re-exports.

1. **Pin current behavior with characterization tests.** Snapshot the parser
   tree, help text and exit codes per command. Pin the exact bytes of every variant
   canonical encoder and every `model_digest`. Add golden replay tests for each
   session contract version.
2. **Consolidate the identical infrastructure helpers.** Canonical bytes for the
   11 matching sites, `sha256_hex`/`Sha256`, all exit codes in `exits.py`, the
   validation-issue converter, and renaming the three `model_digest`s.
3. **Break the core cycle by moving helpers down into leaf modules.** Add
   `errors.py`, `documents.py`, `values.py` and `universe.py`, plus a single
   primitive resolver. The import graph becomes acyclic without splitting the big
   files yet.
4. **Split the CLI into command groups.** Thin groups first (validate/check/diff,
   conformance, solve, lifecycle), then the medium ones (review, exp, evolve), then
   pull services out of the heavy handlers (verify, synth, measure,
   doccheck/fidelity, codegen, recovery inventory).
5. **Introduce `ModelIndex` and the constraint-family registry,** then split
   `model.py` and `checker.py` into packages along their existing sections.
6. **Unify safefs and strict JSON/YAML loading.** Move first, tighten afterwards.
   Tightening path or duplicate-key rules is a behavior change and needs its own
   approval.
7. **Session profile and merging the v7 loop.** Highest risk: evidence bytes and
   resume behavior must stay identical for every contract version.

## Risks that apply to every step

- **Moving any file changes the release identity.**
  `assurance_evidence.production_roster` (assurance_evidence.py:190) hashes
  every `src/gnd/**/*.py` by path, so any move or edit changes
  `production_identity`, and release evidence must be regenerated.
- **Digests depend on exact bytes.** Committed `steps.json` and evidence bind
  digests of canonical bytes. Move encoders verbatim and never merge the variant
  encoders.
- **checker.py relies on names being rebound in place.** `check` is defined at 434,
  saved as `_PHASE3_LEGACY_CHECK` at 4653 and redefined at 5111;
  `_evaluate_derivations` and `_constraint_view` are rebound at 4593–4594. Rename
  these explicitly before splitting the file.
- **Tests depend on internals.** ~14 test files monkeypatch `gnd.cli` privates,
  and ~60 test imports reach into `synth.assemble`/`synth.mutate` privates.
  Re-exports don't keep monkeypatches working: a patch on the old name doesn't
  affect the moved code, so each patch has to point at the new location.
- **Some tests scan source text.** Some read `cli.py` source or
  `inspect.getsource(gnd.checker)` (the eval/exec safety scan in
  `tests/test_checker_families.py:1741`). After a split they must cover the new
  modules, or they silently check less. Tests that require `gnd.cli` to stay
  unloaded need to cover `gnd.commands.*` too.
- **Owner strings are already out of date.** Some `owner=` paths in
  semantic_registry (e.g. `_check_mandatory` at semantic_registry.py:123) name
  checker functions that no longer exist, and no test resolves them.
- **Shared derivation cache.** The derivation-term ContextVar
  (`_DERIVATION_TERM_CACHE`) must stay reachable from both validation and analysis
  after model.py is split.

## Small defects noticed along the way

- The session contract's "unknown version" error (exp/session_contract.py:1099–1106)
  doesn't list version 8, and version 8 is handled as a bare literal
  (`Literal[8]`, line 1008; `version == 8`, line 1085) with no named constant.
- `SESSION_CONTRACT_VERSION` is assigned 2 at exp/session_contract.py:64 and
  reassigned to 3 at line 483.
- `value_domain._in_range` (synth/value_domain.py:72) still has the pre-F-2
  two-valued semantics that `synth/assemble.py` documents as fixed. It is used
  only for drawing values, but its name suggests it is the oracle version.
