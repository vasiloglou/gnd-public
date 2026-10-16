# Plan review: reader 2 of 4

- **Lens:** whether the plan can be implemented against the actual code and the repository rules
- **Repository:** `.claude/worktrees/github-issue-24-milestone-55853e`, HEAD `2d1ff4d`. `git diff 73ea302 HEAD -- src/gnd` is empty, so the inspection baseline still holds.
- **Artifacts reviewed (shasum -a 256):**
  - `e691348d8f2cfa6656c8eb8ca305fc91605a87ce3ae5b332d531942e086392ab`  `notes/transition-check-performance-plan.md` (draft r3)
  - `f0073202b77a6b75a8aaaae59db6a1eba858a7afc2beeee6189647c5e068dd7b`  `notes/phase-TP0-spec.md`
- **Interpreter used for experiments:** `uv run python -I`, CPython 3.14.3. The scratch anonymized bundle was used. No repository file was edited.

## Runtime facts established (reproduced, not inferred)

Measured on the 13-call scratch bundle:

| Quantity | Per `api.check` | Per `api.transition` (1 step, no post) | 13-call total |
|---|---|---|---|
| `ModelIndex.for_model` calls inside the api call | 13 | 64 | 475 |
| `for_model` calls inside `load_population` (outside any api call) | 5 per load (popvalidate rules) | n/a | 65 |
| **All `for_model` calls** | | | **540** (issue: 535) |
| Full checker runs (`_core._check_dispatch`) | 1 | 3 | **25** (issue: 25) |
| `correspond_snapshot` | 1 | 3 | 25 |
| `gnd.model_index.deepcopy` (top-level calls) | 48 | 144 | 1201 |
| `copy.deepcopy` (top-level, caller frame under src/gnd) | 0 | 12–16 | 90 |
| `population._model_digest` / `transition._model_digest` | 5 / 2 | 22 / 3 | 180 / 32 |
| `structured_extension_view` via `gnd.extensions` / via `gnd.transition` | 0 / 0 | 0 / 3 | 0 / 18 |

Other facts:
- Every step document has exactly 1 step. Each transition's pre population is byte-identical to the check population just before it (for example `00-check` and `01-transition`, `10` and `11`). The fixture has **no** 5-step transition, no post documents and no reference populations. It has 2 dynamic derivation heads.
- Batch `gnd check --populations` over the 7 check populations exits **2**. The same holds for `--compiled-operations`, `--admission`, and `--pre/--steps/--post` using `02-check` as post.
- CR-01 behaves as stated. After nested mutation, `matches_validation_marker` is False, `for_model` returns a new index, `api.check` exits 70 (`UnvalidatedPopulationError`), and `checker.check` raises.

## Answers to the five questions

**Q1. How TP1 can thread one key per call.**
- `for_model` has 13 production call sites: `checker/_core.py:357,437,1668,1690,1704,1795,1902`, `compiled_obligations.py:116`, `popvalidate.py:98`, `universe.py:335`, `synth/poolfile.py:184`, `synth/value_domain.py:25`, and `examples/plan_apps/core.py:151`. Most sit deep in helper call trees: 9 per check come through `semantic_adapter.universe_of` and 25 per transition through popvalidate rules.
- **An explicit parameter is not practical.** It would have to pass through many private signatures in the checking, model and semantics layers.
- **The existing `extension_preparation.calculation_scope` (`extension_preparation.py:146-166`) cannot be consulted.** It lives in the `checking` layer (rank 2), and `gnd.model_index` is `model` (rank 1). A read from `model_index` would be an upward edge, and `test_layer_ratchet` would fail.
- **The layer-legal option is a new ContextVar scope owned by `gnd.model_index` itself**, for example a context manager that computes the key once and pins `(model, key, index)`. These modules would enter it: `api` (entry), `checking_service` and `transition` (semantics), `checker._core.check` (checking), and optionally `population.load_population` (model). Every one of those edges already exists and points downward, so no new allowances are needed. Inside the scope, `for_model(m)` returns the pinned index when `m is scope.model`. Outside the scope it keeps today's behaviour, so the RF6 tests stay green.
- **Callers outside any public api call:** `load_population` → popvalidate (5 per load, 65 of the 540 on this workload), synth and pool tooling, and `universe.py:335` when called directly. The plan's open question (§10, line 380) is therefore partly answered already. The issue's 535 matches the GND-side total including loads (540), not the api-only count (475).

**Q2. Can the TP0 counters be collected at the defining homes?** Not as the spec's table is written. The lookup owners that must be patched:
- `checker_runs`: `gnd.checker._core.check` alone records **0**. Callers bind `check` elsewhere: `gnd.checker.check` (used through `checker_module.check` at `checking_service.py:309`), `gnd.transition.check` (`transition.py:57`), and `gnd.batch.check` (`batch.py:13`). `check_with_anchors` (`_core.py:2034-2041`) does not go through `check` at all. Wrapping `gnd.checker._core._check_dispatch` covers every variant with one patch, because it is reached only through `_core` globals (`:2041`, `:2067`). Verified: 25.
- `model_digests`: patching `gnd.population._model_digest` misses `gnd.transition._model_digest` (`transition.py:74,120`, 32 calls). Patching `gnd.values.model_digest` sees 0.
- `deepcopies_gnd`: patching `copy.deepcopy` misses `gnd.model_index.deepcopy` (`model_index.py:10`, `from copy import deepcopy`). That binding accounts for 1201 of 1291 top-level copies (93%). Other bindings: `evolve/service.py:9` and `witness/view.py:3`.
- `extension_views`: patching `gnd.extensions.structured_extension_view` sees 0, because transition binds the name at `transition.py:65`. Checks never call it.
- `correspond_snapshot` is imported lazily at call time (`_core.py:364`), so patching `gnd.correspondence` works. Verified: 25.
- `model_index_keys`: wrapping `artifacts.canonical_json_bytes` with a re-entrancy flag set by a `for_model` wrapper works. Measured 540, equal to the call count.
- **Frame-filtered deepcopy counting is cheap.** One `sys._getframe(1)` per top-level call; the instrumented run took 7.6 s against about 6.4 s plain. It counts **top-level calls only**: `copy._deepcopy_dict(x, memo, deepcopy=deepcopy)` binds the original as a default argument, so recursion bypasses any patch. The issue's 2.7 M is a cProfile count that includes recursion, so it is not like-for-like. The size of the `memo` dict is a cheap volume proxy (688,352 entries for the model_index copies).

**Q3. TP3's new keyword and minting function.**
- **Feasible.** The new keyword plus a separate minting function can be built.
- **Pins that must change:**
  - The `transition` parameter tuples at `tests/test_public_api.py:20` and `tests/test_v61_phase2_api.py:47`.
  - If the minter joins `api.__all__`: `tests/test_public_api.py:16`, `tests/test_v61_phase2_api.py:37`, `tests/test_public_runtime.py:52` (subprocess literal), and the `# noqa: RUF022 - approved stable order` comment at `src/gnd/api.py:114`.
- **Pins that are unaffected:** `test_public_reference_signatures.py` (it only checks `references`) and `test_public_emitter_trust_controls.py:152` (it only checks `unredacted`).
- **Docs:** `docs/reference/python-api.md`, `docs/reference/capabilities.md`, the release note, and any new public exception types.

**Q4 and Q5.** See the findings below. In short: TP0-C2 as specified, TP3-C2's "compiled_operations / reference populations" transition cases, and TP0 T3 and T4 cannot be satisfied as written. T8 cannot fail.

## Findings

| ID | Class | Severity | Claim | Evidence | Proposed fix |
|---|---|---|---|---|---|
| R2-1 | blocking | high | The TP0 counter table patches lookup owners that miss most of the work. `checker_runs` reads 0, `deepcopies_gnd` misses 93%, `model_digests` misses the transition binding, and `extension_views` reads 0. TP0-C2 ("deterministic counters") is not met by the spec as written. T4 would catch only the counters that read zero; the deepcopy and digest undercounts pass T4 silently. | Experiment E1 and the Q2 rows: `transition.py:57,65,74`, `batch.py:13`, `checking_service.py:309`, `_core.py:2034-2041`, `model_index.py:10` | Replace the table with actual lookup owners: `checker_runs` ← `gnd.checker._core._check_dispatch`; `model_digests` ← `gnd.population._model_digest` + `gnd.transition._model_digest`; `deepcopies_gnd` ← `copy.deepcopy` + `gnd.model_index.deepcopy` (+ `evolve.service`, `witness.view`); `extension_views` ← `gnd.transition.structured_extension_view` (+ `gnd.checker`, `gnd.diff`, `gnd.synth.assemble` bindings). Add a T4 sub-case that cross-checks totals against a site-attributed count. |
| R2-2 | blocking | medium | T3 expects batch check to exit **0**. On the baseline it exits **2**: every fixture population is vacuous, and T2 itself pins "all exit 2". The test as specified fails on the baseline. | E3: `gnd check steps.orm.json --populations <7 check pops>` → exit 2 | Expect exit 2 with zero failures, pinned per population. |
| R2-3 | blocking | medium | T4 measures "the 5-step transition" and the illustrative `fixture-5` / `checker_runs: 7` suggests one exists. The fixture has six 1-step transitions and no 5-step walk. The surface list also includes `api.transition(..., post)`, but the fixture has no post documents and the spec does not say where posts come from. | All `NN-transition-steps.json` have `len(steps)==1`; bundle file list | Define the transition surfaces by fixture file. For "with post", name the post as the next check population (it runs: E3 exit 2) or drop it. Restate T4 on a named call. |
| R2-4 | blocking | medium | TP3-C2 requires parity "on every TP0 transition case, including `compiled_operations`, reference populations and dynamic heads". `api.transition` has no `compiled_operations` mode (`api.py:735-741`; `transition.py` never references it). The TP0 fixture has no reference populations. Dynamic heads exist (2). The criterion is unsatisfiable or vacuous as written. | `api.transition` signature; E4 `reference_populations` False, dynamic 2 | Limit TP3-C2 to the fixture transitions plus named existing reference-population and dynamic-head transition fixtures (for example `plan_apps/course`, or an existing reference-population corpus case). Move `compiled_operations` to the check-surface parity (TP1/TP2, O12). |
| R2-5 | hardening | medium | T1's "no file contains a downstream name (literal scan)" requires committing the forbidden literal into the test, which defeats the anonymization. This is a guard that must contain the content it forbids. | spec §8 T1 | Scan positively instead: every `model_id` equals `urn:gnd-fixture:steps@1`, every provenance `user_note` comes from an allowlist, and paths are relative. Alternatively compare SHA-256 digests of tokens against a committed digest list. |
| R2-6 | hardening | medium | The plan says TP1 can reuse "`_model_digest(model)` computed at check entry" as the per-call key (plan lines 163-166). That digest uses `repr`, excludes `operations`, and replaces content when reference populations are present (`values.py:176-191`). The ModelIndex key hashes canonical JSON over everything except `warnings` (`model_index.py:56,74`). Reusing the marker digest would fail `tests/test_rf6_index.py::test_all_query_inputs_mutated_never_serve_stale[operations]` (it asserts `current.digest != old.digest`). Also, the marker digest is recomputed 5 times per check, not once. | `values.py:176-191`, `model_index.py:56-74`, `test_rf6_index.py:64-80`, E1 (`model_digest_population` 5 per check) | TP1 computes its own `for_model` key once per scope. Delete the "reuse the marker digest" sentence, or record its incompatibility with RF6. |
| R2-7 | hardening | medium | The threading mechanism and the meaning of "public call" are not stated. `calculation_scope` cannot be reused under the layer map (`model_index` is model, rank 1; `extension_preparation` is checking, rank 2). `load_population` makes 5 `for_model` calls outside any api call. The issue's 535 matches the total including loads, not the api-only 475. | Q1; `gnd_layers.json` modules; E2 call-site attribution | Name the design in the plan or TP1 spec: a ContextVar scope owned by `gnd.model_index`, entered by `api`, `checking_service`, `transition`, `checker._core.check` and (decision) `load_population`. List the public calls covered by TP1-C1. Answer the §10 open question with this measurement. |
| R2-8 | hardening | medium | The TP1-C2 test can be fooled. After nested mutation the population marker already refuses the check (exit 70), so a stale-index mutant gives the same api result. A test asserting only "fails `matches_validation_marker`" cannot detect a scope that leaks across calls. | E5: marker False, `api.check` exit 70 regardless of the index | Require (a) a direct `for_model` freshness assertion after mutation, and (b) a case that mutates the model, **re-loads** the population against the mutated model (so the marker passes), checks, and compares against a fresh process. Only (b) exposes a stale index that changes a verdict. |
| R2-9 | hardening | medium | The `model_index_keys` counter is defined as hashing "made from inside `for_model`". After TP1 moves key computation to scope entry, the counter drops to 0 by construction, so TP1-C1 would pass trivially. | spec §6 counter table | Count model-key hashes wherever they occur (wrap `canonical_json_bytes` and count calls whose argument is a model dump, or wrap the new key function), fixed in TP0 so TP1 cannot move it. |
| R2-10 | hardening | medium | The deep-copy metric is not like-for-like with the issue, and its gate is ambiguous. Mock wrappers count top-level calls only (recursion is bound as a default argument in `copy._deepcopy_dict`). The issue's 2.7 M includes recursion. TP2's "≥ 50% fewer" could be met or missed purely by changing the copy granularity, for example replacing one whole-list copy with per-row copies. | E1/E6: 1291 top-level calls; memo-entry volume 688,352 | Record both top-level count and volume (summed `len(memo)`) in TP0. Bind TP-D6's TP2 target to volume, or to both. |
| R2-11 | hardening | medium | The TP3 minting function must also produce the check payload, or the workload gets no net saving. The workload calls `api.check(pop_i)` and then `api.transition(pop_i)`. If the minter is a separate full check, a caller does 2 checks to save 1. In addition, `api.check` goes through `checking_service` (anchors, compiled ops, admission, reference binding), while the transition pre-check is plain `check(model, pre)` inside `calculation_scope` (`transition.py:1920-1923`). The receipt must hold exactly the report the transition would compute. | `checking_service.py:289-312`, `transition.py:1920-1928` | The TP3 spec should state: the minter returns the byte-identical `api.check` payload plus a receipt. The receipt stores (a deep copy of) the default-mode `check(model, pre)` report. When the two differ (anchored constraints, compiled or admission options), the minter returns no reusable receipt or one refused for "check options". |
| R2-12 | hardening | low | The TP3 receipt binds the model **object**, so path inputs (`api.transition(path, …)`) always produce a fresh `Model` and are always refused. A "forged" receipt (a receipt-class instance not minted by GND) and a "foreign object" need separate detection. This is feasible with a module-private weak registry of minted receipts. | `api.py:214-222` (path or Model inputs) | The TP3 spec states that receipts require loaded `Model` and `Population` objects. It names the registry mechanism and the error class hierarchy (relation to the existing `TypeError` refusals in `test_public_api.py:41-46`). |
| R2-13 | hardening | low | T8 cannot fail for TP0. `tools/gnd_arch.py` scans only `src/gnd` (`PACKAGE_DIR = "src/gnd"`, `:45,195`), so the "tools excluded" condition holds automatically, and T8 is just the existing test. | `tools/gnd_arch.py:45,195` | Replace T8 with a check that can fail: assert `git diff 73ea302 -- src/gnd` is empty, or that the tool imports only the public loaders and `gnd.api` plus its declared patch targets. Otherwise relabel T8 as a regression run, not a test. |
| R2-14 | hardening | low | "Failing pre-check" (TP-D5 (ii)) is undefined. Every fixture check exits 2 (vacuous). If "failing" means nonzero exit, no receipt is ever reusable on the TP0 workload, and TP3-C2 cannot be met. | `checker/_reports.py:141-166` (band 2 = vacuous) | Define failing as band 1 (and decide band 4). State that band 2 is reusable. |
| R2-15 | completeness | low | Stale text. Plan line 257 says "TP-D5 open" and line 268 "TP-D5 decides", but §10 records TP-D5 as ruled. Plan §5 and §9 list only `test_public_api` / `test_public_reference_signatures` as pins (see Q3 for the full list). Spec §2 cites "plan draft r1". Spec D6 asks for 3.11 and 3.13, but the default `uv run` interpreter is 3.14.3 and no selection command is given. | plan :257, :268, :308-310, :359; spec :12, :159 | Update the text; list the real pins; give `uv run --python 3.11/3.13` commands. |
| R2-16 | completeness | low | The fixture has 145 fact types (steps model load). The plan's "65 derived fact types" agrees with 63 static + 2 dynamic classifications, but nothing states the total. The admission surface is "when the fixture supports admission", which is not decidable. `--admission` runs and exits 2 on the fixture. | E4; E3 admission exit 2 | State that admission is exercised (it runs), and record the fact-type total. |

Criteria that some implementation can satisfy as written: TP0-C1, C3, C4, C5; TP1-C1 (with R2-7 and R2-9), C2 (with R2-8), C3, C4; TP2-C1, C2, C3, C4 (with R2-10); TP3-C1, C3 (with R2-12 and R2-14), C4. Not satisfiable as written: TP0-C2 under the spec's table (R2-1), and TP3-C2 (R2-4).

Falsifiability of T1–T8:

| Test | Can it fail? |
|---|---|
| T1 | Yes (digests). The literal-scan half is problematic (R2-5). |
| T2 | Yes |
| T3 | Yes, and it currently would fail (R2-2) |
| T4 | Yes, but its subject does not exist (R2-3) |
| T5 | Yes |
| T6 | Yes (perturbation) |
| T7 | Yes, weakly (schema tags only) |
| T8 | No (R2-13) |

## Experiment commands and outputs

E1, counting with mock.patch (script `scratchpad/plan-review/r2exp/count.py`):
```
uv run python -I .../r2exp/count.py .../scratchpad/bundle core
# defining homes only:
TOTAL {'for_model': 540, 'for_model_keys': 540, 'model_digest_population': 180, 'model_digest_transition': 32,
       'correspond_snapshot': 25, 'sev_transition': 18}        # checker_runs absent (=0), sev_home 0, values.model_digest 0
uv run python -I .../r2exp/count.py .../scratchpad/bundle all
# plus check owners gnd.checker/transition/batch, copy.deepcopy, model_index.deepcopy:
TOTAL {'for_model': 540, 'for_model_keys': 540, 'deepcopy_model_index_binding': 1201, 'model_digest_population': 180,
       'model_digest_transition': 32, 'checker_runs': 25, 'correspond_snapshot': 25, 'deepcopy_all': 90,
       'deepcopy_gnd_frame': 90, 'sev_transition': 18}
# per call: check = 13 for_model / 1 checker run / 48 mi deepcopies; transition = 64 / 3 / 144 (+12..16 copy.deepcopy)
```
E2, `for_model` attribution: load = 5 (popvalidate `_rule_*`). Check = `_check_dispatch`×3, `universe_of`×9, `check`×1. Transition = 3×check share + popvalidate 25.

E3, CLI surfaces on the fixture: `--populations` (7 check pops) exit 2; `--compiled-operations` exit 2; `--admission` exit 2; `--pre 01 --steps 01 --post 02` exit 2.

E4: `reference_populations` False, operations 6, fact_types 145, stability `{'static': 63, 'dynamic': 2}`. All step documents have 1 step.

E5, CR-01: marker True→False after `m.fact_types[0][...]` mutation, new index True, `api.check` exit 70 `UnvalidatedPopulationError`, `checker.check` raises.

E6 (`r2exp/dispatch.py`): `{'dispatch': 25, 'mi_top': 1201, 'mi_memo_entries': 688352}`. Python 3.14.3: `copy._deepcopy_dict(x, memo, deepcopy=deepcopy)` binds recursion as a default argument.

## Verdict

**revise**. The design is implementable and layer-legal (a ContextVar scope owned by `gnd.model_index`; a receipt with a private registry). But 4 blocking items (R2-1 to R2-4) make the TP0 spec and TP3-C2 unsatisfiable or wrong as written. All of them are text fixes; none needs a re-design.
