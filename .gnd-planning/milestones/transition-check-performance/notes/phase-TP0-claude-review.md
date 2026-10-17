> Retained verbatim except one sanitization: the reviewer's mutant label for mutant 10 is
> written `MU10`, so it cannot be read as a downstream milestone ID.

# TP0 diff review (single independent reviewer)

- Branch: `claude/transition-check-performance-tp0` (uncommitted + untracked), base `15944ee`
- `tools/measure_transition_cost.py` SHA-256 `76c61f7067af26644fbe84f43ab3599625e26335f42cea35af58645da3851b1e`
- `tests/test_transition_cost_workload.py` SHA-256 `4cd69951518831ed26a886c0bab37b11ca1be578c7eac3852fec949ffec73280`
- Contract: phase-TP0-spec.md r5 §1–11 (+ appended findings), plan §4 TP0.
- Interpreter for all runs: 3.14.3 (session default). Baseline: `uv run pytest -q tests/test_transition_cost_workload.py` → 7 passed in 71.6 s.

All scratch scripts are under this directory. Mutants were built by `mk.py` (copies of the
tool and test with one substitution; repo files untouched) and run with
`uv run pytest -q -p no:cacheprovider <scratch>/<mutant>/test_mut.py -k <test>`.

## Mutants and probes

| # | Mutant / probe | Target | Outcome |
|---|---|---|---|
| M1 | Installer patches only the defining home of each counted callable | T4 | **Killed.** `model_digests` 0, `extension_views` 0 → `all(>0)` fails. Note: `checker_runs` still 25 (internal callers resolve `_check_dispatch` as a module global), so T4 kills this via the alias-bound counters, not via `checker_runs`. |
| M2 | Identity-keyed `ModelIndex.for_model` (cache by `id(model)`, conftest monkeypatch) | T5 | **Killed.** `digest != before` fails (same digest after operation mutation). |
| M3 | Probe: does T6's verdict-flip reach the payload? (diff of `pre.check` payloads) | T6 | Reaches payload: sole diff `.verdicts[0].modality 'alethic' -> 'deontic'`; exit and counts unchanged. It flips modality, not the `verdict` field (see F8). |
| M4 | `NORMALIZED_FIELDS = ()` | T3 | **Killed.** CLI vs API digest differ. |
| MU10 | Swap attribution: key-path ↔ other `model_dump` | T4 | **Survived** (1 passed). See F3. |
| M11 | Drop deepcopy depth tracking (count every deepcopy frame whose caller is under `src/gnd`) | T4 | **Survived.** Caller-file filter alone yields 1 for `fact_types`; depth is untested but currently redundant (F7). |
| M12 | `trace_digest` = hash of branch *count* only | T6 | **Survived.** The dropping mutant changes cardinality, so identity is never exercised. See F4. |
| P1 | `counting()` around a replay that raises; then inspect | restore | Profiler restored (`None`); no leaked wrapper in any `gnd.*` module; **`ModelIndex.__dict__['for_model']` becomes a bound `method`, was `classmethod`** (F5). 5 modules first imported inside the block (`gnd.anchor_identity`, `gnd.anchors`, `gnd.compiled_obligations`, `gnd.population_shape`, `gnd.temporal_guarded`); none bind a counted name today. |
| P2 | Raising `__deepcopy__` ×3 inside `counting()`, then one `fact_types` read | depth | `deepcopy_calls == 1`: depth is restored on exception unwinding (profile `return` events). Sound. |
| P3 | Same-process replay counted twice | determinism | Run 0 (cold): `deepcopy_calls` 1291, `deepcopy_nodes` 2,774,153. Run 1 (warm): 1290 / 2,760,394 = evidence. All other counters identical. See F6. |
| P4 | Payload identity fields; `operations` contents | import exclusions | `steps.orm.json` operations contain `user_note`, so `operations_digest` legitimately changes under transform step 2; `model_digest`, `transition.model_digest` echo the model; `computed_post.population.model_id` echoes the id. The four exclusions are necessary; no other id-like field differs. Exact-minimality vs the original bundle cannot be rerun (bytes not committed). |
| P5 | CLI vs API `model`/`population`/`post` on `cli.transition.01`; batch payload | normalization | CLI: `model` = abs path, `population` None, `post` None, `transition.steps` content list; API all None. Batch payload keys `command, issues, model, rows, schema_version, summary, tool`; no temp path found. |

## Other checks

- **Surfaces vs §6:** reporter column complete (7×3 check modes, 6×transition ±post, batch, both CLI arms). Course column missing `pre.check.admission` and the CLI `check MODEL POP` arm on `pre` (F1). Extra `attempt-1/2.transition` surfaces are a harmless superset.
- **Counter owners:** scan of loaded `gnd.*` modules for `is original` covers name-bound aliases (`population._model_digest`, `transition.structured_extension_view`, `checker.__init__` re-exports); function-local imports (`_core.py:364`) read the patched module attribute at call time. Sound for the current import graph.
- **Anonymity:** distinct strings across all 21 JSON files enumerated (901); all are steps-metamodel vocabulary, packaged `expense` example values (`Ari`, `Bea`, `EUR`, categories; present in `src/gnd/examples/expense`), the allowed `urn:gnd-fixture:steps@1` and `Sealed step programs.`. No absolute paths in evidence/fixtures/tool/test; only URL is issue #24 of this repo. `anonymize.py` spells no name. Nothing found.
- **Evidence consistency:** README counter table = `counters.json` reporter replay (25/540/540/457/212/1290/2,760,394/18/25); course line = course replay (5/115/21,492); timings 5.79 s / 4.5% = `timings.json` (3.14.3); TP2 target 1,380,197 = ⌊2,760,394/2⌋; batch summary (exit 2, 7 projections, 0 violated) = `digests.json`; `import.json` `equal: true`, 13 calls. PROVENANCE post-transform hashes verified by T1 (passed); duplicated before/after rows for paired populations are consistent (same bytes).
- `git diff --stat` touches only the spec appendix; no `src/gnd` change.

## Findings

| ID | Class | Severity | Finding | Evidence | Suggested discharge |
|---|---|---|---|---|---|
| F1 | completeness | medium | §6 table's `course` column requires `admission=True` on pre and the CLI `check MODEL POP` arm on pre; the tool emits neither, and T7 asserts no course surface at all, so the gap is undetected. | `digests.json` course keys: `attempt-1..3.transition, pre.check, pre.check.compiled` | Add `pre.check.admission` and a course CLI arm (with T3-style digest equality), and assert course surface names in T7; or record a ruled deviation. |
| F2 | completeness | medium | Batch surface records only exit, row count and summary, no normalized payload digest; CLI and batch have no trace digest. §6 says each surface records all three. The batch payload holds no temp path (P5), so a digest normalizing `model` is feasible; the trace digest for subprocess surfaces is not (needs a recorded deviation). | `cli_surfaces()` / `digests["cli"]["cli.batch"]` | Add `normalized_digest(batch_payload)`; record the subprocess trace-digest deviation in the findings. |
| F3 | hardening | medium | `model_index_key_paths` and `model_dumps_other` (TP1 target units, D4) are only checked `> 0`; an attribution swap survives T4 (MU10). | MU10 survived | Pin `model_index_key_paths == 540` and `model_dumps_other == 457` on the warm replay, or add a delta case (one extra `ModelIndex.for_model` adds exactly 1 key path, 0 other). |
| F4 | hardening | low | T6's branch mutant only removes a branch, so the trace digest is proven sensitive to cardinality, not identity (M12 survived). | M12 survived | Add a substitution mutant (replace one recorded id with another unreached id). |
| F5 | hardening | low | `counting()` saves `getattr(ModelIndex, "for_model")` (a bound method) and restores that, so after the first block the class attribute is no longer a `classmethod`; subclass dispatch would bind to `ModelIndex`. No subclass exists today and counts stay stable, but restoration is not byte-faithful and leaks into later tests in the same process. | P1 | Save/restore `vars(owner)[name]` (descriptor), deleting the attribute when it was inherited. |
| F6 | hardening | low | First counted replay in a process records 1 more `deepcopy_calls` and +13,759 `deepcopy_nodes` than later runs; evidence numbers are warm (surfaces run first). Not documented; a TP2 exact/near gate run cold would mismatch. | P3 | Record in README/findings that node counts are taken warm (after one unrecorded run), or warm up inside `measure()` explicitly. |
| F7 | hardening | low | Deepcopy depth tracking is untested (M11 survived) because the caller-file filter already excludes recursive frames; depth only matters for a GND-defined `__deepcopy__`. Also latent: a module first imported inside `counting()` would bind a wrapper permanently (none does today). | M11, P1 | Optional: one test with a GND-frame nested deepcopy, or drop the redundant depth logic with a comment. |
| F8 | completeness | low | T6's runtime mutant flips `modality`, not the constraint `verdict` the spec names; the T6 stability half compares only `course` surfaces, not the whole `digests.json`. Both still prove liveness. | M3, test source | Flip `verdict` (e.g. pass→fail) or note the substitution; widen stability to reporter or state the scope. |
| F9 | completeness | low | Spec §6 says `NORMALIZED_FIELDS` also blanks the transition's `pre`, `steps`, `post` "when present"; the tool blanks only `model`, `population`. No observable consequence (CLI emits `population`/`post` as None and `steps` as content, P5; T3 equality holds), but the divergence from the append-only spec is unrecorded. | P5 | Add an implementation finding stating why the two fields suffice. |
| F10 | completeness | low | Spec D1 cites "a defining-home-only patch counts 0 of 25 checker runs"; for the chosen target `_check_dispatch` it counts 25 (M1). T4 still kills M1 via alias-bound counters, so the coverage claim holds, but the cited fact is false for this target. | M1 | Note in findings. |

## Verdict

**No blocking finding survived.** Every test T1–T7 has a demonstrated failure path for its
headline property (M1, M2, M4 killed; M3 reaches the payload). Counter restoration is complete
for the profiler and module patches and depth tracking is exception-safe; the import exclusions
are necessary; anonymity and evidence numbers check out. Approve with fixes: F1–F3 (medium)
should be discharged or recorded as ruled deviations before record; F4–F10 are low-severity
hardening/completeness.
