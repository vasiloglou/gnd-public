Retained first independent Codex CLI close opinion; operator/repository paths sanitized; trailing Markdown spaces removed. Other wording unchanged.

**REVISE — candidate local close readiness at `b89747d6`.** One blocking compatibility defect and one hardening finding.

1. **Blocking — composed witness adapters change include-free refusals.**
   [service.py:162](<REPO>/src/gnd/witness/service.py:162) and [service.py:182](<REPO>/src/gnd/witness/service.py:182) expose every `ModelValidationError`’s first rule.

   Reproduced both adapters using committed `public-launch-phase-2/invalid.orm.yaml`, the anchored composed population, and a canonical composition record rebound to their actual hashes. Only the record read was supplied in memory; model, population, certificate and binding checks were real. Executing the baseline adapter bodies versus HEAD produced:

   ```text
   composed_witness_result: baseline 3/input-invalid → HEAD 3/semantic:cross-ref
   composed_replay_result:  baseline 3/input-invalid → HEAD 3/semantic:cross-ref
   ```

   This violates the frozen include-free refusal contract. Preserve include-specific reasons while retaining `input-invalid` for other validation errors, as the neighboring adapters do. Add discriminating include-free controls.

2. **Hardening — D3’s repaired guard no longer binds the candidate argument.**
   [test_model_v2.py:344](<REPO>/tests/test_model_v2.py:344) searches beyond the call. Changing only `_validated_candidate`’s argument from `proposal.candidate_model` to `before_loaded_model` still passes: it finds the later payload field at [service.py:1682](<REPO>/src/gnd/evolve/service.py:1682).

   Reproduced by substituting that argument in `inspect.getsource(EvolutionService.preview)` and invoking the actual guard with the substituted source. Bind the assertion to the call’s first argument and reject this mutation. Current runtime argument binding is correct.

I verified:

- The required contracts, full canonical plan including amendments 13–18, close notes, phase specs/corpora, approval records, reviews and completion records. All **1,524 entries across 11 historical manifests** matched their original commits. Current metadata has **118 citations**, including the two unchanged `001` path-only entries.
- All **4,698 nonplanning paths/modes** at HEAD equal `1ca2379f`. Actual `origin/main` at `a9b67d8b` equals the complete approved MC4 tree. The retained patch exactly matches the five pending files; the close branch adds no runtime Python change.
- Retained final default evidence is **exit 1: 6 failed, 18,795 passed, 801 deselected**, with exactly the six `459ca8d2` failure IDs. Retained census has **2 passes**, all 400 original observations unchanged and 23 dispositioned additions. The rejected 14-failure run remains separate. The 13 lint findings match after the declared offset.
- Size accounting: MC2 tests **565/600**; MC3 source/tests **1109/1224**, each below 1400; MC4 tests **120/120**; combined support **128 = 120 + 2 + 6**.
- Fresh execution: **26 targeted pytest cases passed**, 13 population checks matched, both component/expense combined previews and analysis-only previews behaved as claimed, and flattened/stale-pin inputs refused. API/inventory dirty controls rejected their mutations. Tracked reference and twin checks passed; tracked files remain unchanged.

I did not rerun full/default/census/native/external suites, real filesystem publication/finalization, or race/cap fixtures. Those claims rely on retained evidence. Main’s valid **229-pass** smoke remains distinct from its invalid initial attempt and from candidate full results. No network, credentials, agents, edits or merges were used.

PR158 still requires separate fixed-head owner merge approval, final on-main equality, and the final close ruling/record. **Issue95 closure remains pending.**
