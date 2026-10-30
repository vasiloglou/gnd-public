# Plan review r1, reader 1

One reader, selected by the owner on 2026-10-29 (o): "One reader" (IH-D5 (b)).
A general-purpose agent reviewed plan r1 (SHA-256 `cbfa12fd…51ce`) and the
IH0 spec r1 (SHA-256 `269663b5…db81`) at `1182f96`. It edited no repository
file, ran no learner, solver or model, and wrote its probes only under the
session scratch directory, written `<scratch>` below. One reviewer is one
reviewer. The report is retained verbatim, except that a private host name is
written `<host>` (close review, 2026-10-30).

---

# Review: ilp-import-hardening plan r1 (cbfa12fd…51ce) + IH0 spec r1 (269663b5…db81) at HEAD 1182f96

**Verdict: request-changes.** The plan is the right size and its harvest is nearly complete, but three findings stop the work as written: IH0's range is not IL's diff, IH1's counting-entry contract cannot serve `hold()` without changing the comparison table, and IH1's one-rendering-pass test already passes at `fb03739`. Each has a small fix. No repository file was edited and no learner, solver or model was run; probes are in `<scratch>/plan-review/` (`probe_hold.py`, `probe_ownref.py`, `probe_render_calls.py`, `il-files.txt`). Working tree verified clean.

## Findings

### 1. Blocking — IH0's range is not "IL's whole diff"; 27 of its 64 files belong to other milestones
**Where:** plan completion predicate 1, §4 IH0, IH-D2, §9 implementability sweep; IH0 spec §Design 1 and 3 (the brief), IH0-D1.
**Evidence:** `git log --first-parent 07f4d45^..fb03739` shows non-IL PRs merged inside the range: #47 IK-evolve (`696b7b6`, `7d7d4bf`), #53 maintenance (`6e762b1`), #52 IKE-Q3 (`de81f34`), #50 IK-close (`33827e2`). Per-merge `git diff --shortstat m^1 m -- src tools`: IL's PRs (#56–58, #60–63) touch 37 files; the others add ~534 lines, and 27 files are touched *only* by non-IL commits — e.g. `evolve/service.py` (+135/−), `codegen/*`, `population.py`, `universe.py`, `semantic_*.py`, `model/_documents.py`, `discover/*`, `recovery/verify.py`. The 64-file/3,628-line figure is accurate for the range (verified; also 104 test files/10,705 lines and 539 files overall) but not for IL. The brief tells readers "the ilp-learners milestone, which added learner adapters…", so they will attribute IK-evolve/maintenance code to IL, and IH0 could "fix" other milestones' reviewed code under this milestone's authority. IH0-D1's sizing is inflated ~17%.
**Fix:** define the subject as the union of IL's first-parent merges (`m^1..m` for #56, #57, #58, #60, #61, #62, #63, #64), or keep the range but list #47/#50/#52/#53 as out of scope in the brief; restate counts (37 files) and add a decision if the owner wants the other PRs included.

### 2. Blocking — `count_mined_rules` as specified cannot be what `hold()` calls without moving the comparison golden
**Where:** plan §2 "The counting entry" ("maps and counts each rule in MAPPING_REFUSALS then COUNT_REFUSALS order, raising IlpError with the name it raises today… `hold()` calls the same two functions"); IH1 criteria; IH-R2.
**Evidence:** `COUNT_REFUSALS = ("too-large", "covers-nothing", "support-mismatch", "does-not-hold")` (`ilp_amie.py:56`). `hold()` (`tools/ilp_comparison.py:123`) must count rules that do *not* hold: `probe_hold.py` over the retained `IL4/live/invocation-1/rules.txt` shows 6 of 8 rules would raise `does-not-hold` under the import's checks (e.g. rule 0: 19/20), while the golden `il6/comparison.json` records amie inv 1 as `rules_mined 8, rules_hold 2`. Raising there turns the tool's row into a `ComparisonError` (exit 2). Also the import maps *all* rules before counting any, while `hold()` maps-then-counts per rule; and `hold()` does not render or check `covers-nothing`/support.
**Fix:** state that `count_mined_rules` raises only mapping refusals and `too-large`; keep `covers-nothing`/`support-mismatch`/`does-not-hold` as admission checks in the import over `MinedCount.counts`; name the order `hold()` adopts on error paths (mapping refusals now precede counting refusals) as an IH1 decision with its cost.

### 3. Blocking (falsifiability) — "calls to `ilp_amie.render` per import: exactly 1" already holds at `fb03739`
**Where:** plan §4 IH1 criterion 2; completion predicate 2.
**Evidence:** `probe_render_calls.py` wraps `ilp_amie` functions during an admitting import of retained invocation 2: `exit 0 {'render': 1, 'relation_table': 2, 'pairs': 2, 'spell': 310}`. IL-close-Q1 as recorded in `008-close-repairs.md` §Refactoring review is that the import "builds the relation table and the spelled pairs again" — the second `relation_table`/`pairs` call (plus the head re-spelling in the provenance loop). The proposed test is green before any change, so it cannot show the obligation discharged.
**Fix:** assert `relation_table` == 1 and `pairs` == 1 per import (both 2 today, red first); optionally that the provenance builder reads the counted pairs rather than calling `spell` again.

### 4. Hardening — IH-D1 (a)'s cost is understated: an adapter bump moves every AMIE export golden
**Where:** plan §10 IH-D1 reading (a) ("export goldens move for models with own-reference subtypes"); §6 last risk row.
**Evidence:** `adapter_version` "2" is inside `tests/fixtures/ilp_learners/il4/expected/staffing/export.json` and `…/north/export.json`; a bump to 3 moves both (and every `export_sha256` shown in docs replays) even though staffing has no subtypes and `facts.tsv` would not change. The §6 risk row ("replays stay on adapter 2 inputs, and the spec names how") is unclear: the import does not select a spelling by version; if tagging is limited to components that hold an own-reference subtype, staffing facts are unchanged and the retained run records' `facts_sha256` stays valid — the plan should say that, not defer it.
**Fix:** restate (a)'s cost as "all AMIE `export.json` goldens and export digests move; `facts.tsv` moves only for models with an own-reference subtype", and repair the risk row.

### 5. Hardening — under IH-D1 (b), R1's asserted name moves, contrary to "no golden moves" + R1 "still refuses"
**Where:** plan §4 IH2 criteria 3–4; IH-D1 (b).
**Evidence:** `tests/test_il_close.py:375` asserts `stderr.startswith("rule 0: support-mismatch:")`. A mapping refusal "before any count" on an own-reference join would refuse R1's rule as `own-reference-join`.
**Fix:** name the R1 assertion change under (b); fix the new name's position (after `type-confused-join`, the last of `MAPPING_REFUSALS`).

### 6. Hardening/completeness — IH-R4's order-pinning test has no owning phase, and nothing pins order today
**Where:** plan §0 IH-R4; no §4 criterion.
**Evidence:** the only docs check is `test_c8c_each_refusal_is_named_in_its_adapter_section` (`tests/test_il_close.py:345`), which checks membership, not order. The ordered tables are at `docs/reference/ilp-bridge.md:514-545`.
**Fix:** give the test to IH1: pin `MAPPING_REFUSALS`/`COUNT_REFUSALS` order against the docs tables, shown red against a swapped tuple.

### 7. Hardening — the order constraint is decided in prose, and its test can only be red against a mutant
**Where:** plan §2 "Order constraint"; `MinedCount.facts_sha256`.
**Evidence:** the plan's own claim checks out (`ilp_service.py:619-640` raises `facts-mismatch` before `mapped`), but the proposed dataclass already carries `facts_sha256`, presupposing the rendering moves inside `count_mined_rules` — the option the constraint argues against. A test pinning `facts-mismatch` ahead of mapping refusals passes at `fb03739`; the closest existing, R6, covers only the earlier input refusals.
**Fix:** make "render in the import and pass it in / return before mapping" an IH1 decision with its cost; require the pin test to be shown red against a reordering mutant (as IL did for R6).

### 8. Hardening — IH-D5/IH-D4 depart from the four-reviewer plan/close bar without stating that cost; close is tied to the wrong decision
**Where:** plan §10 IH-D5 (proposed (b) one reader); §4 Close ("a close review per IH-D4"); §8.
**Evidence:** `start-milestone/SKILL.md` §Verify: "The repository retains its plan/close four-reviewer bar"; `process-phase/SKILL.md`: "the four-reviewer panel remains the bar for plan review and milestone close". IH-D4 is IH0's instrument; reading (c) there is one reader, which would also set close below the bar. Precedent: IL D5, IK D7 and IS D13 each owner-selected four readers.
**Fix:** add a separate close-instrument decision; in IH-D5 state that (a)/(b) are departures from the repository bar needing the owner's explicit ruling (and record it (o) with date if (b) is what this review is).

### 9. Hardening — IH-R3 "full local CI matrix" does not reproduce the CI matrix; its source is not a retained record
**Where:** plan §0 IH-R3; §1 Sources last row; §9.
**Evidence:** `.github/workflows/development.yml` runs regression/installed on ubuntu/3.11 and macOS/3.13 (candidate on ubuntu/3.11). A local run on this Mac is macOS/3.11 + macOS/3.13 only. "this session's local CI on PR #64" is not a committed record (repairs are `a7d6dc0`, `fe80002`).
**Fix:** name the exact local commands (incl. `uv run pytest -q -ra --tb=short` and the candidate build + `test_release_acceptance.py`), state that the Linux leg is not reproduced (or where it runs, e.g. `<host>` is also macOS), name the evidence file (`evidence/close/ci-matrix.txt`), and cite the repair commits.

### 10. Completeness — RF6 successor chain home missing
**Where:** plan §3/§5 ("RF6 census rows regenerated"); IH1 criterion 6.
**Evidence:** RF6 successors are chained in `tests/support/pyrel_application_successors.py:82-87`, listing `ilp-learners/evidence/IL<n>/dynamic-query-successor.json`; the IL-close successor contains 12 `ilp_amie` and 24 `hold` mentions, so moving provenance code moves rows.
**Fix:** add `evidence/IH<n>/dynamic-query-successor.json` + the list entry to artifact homes; name the gate tests (`tests/test_rf6_query_policy.py`, the RF6 successor tests, `tests/test_gnd_arch.py`) in IH1.

### 11. Completeness — IH2 fixture claim inexact
**Where:** plan §9 implementability sweep ("differs from the needed case only in `manager_no`'s primitive").
**Evidence:** the population must change too (`manager: ["1","2"]` and the `manages` rows). `probe_ownref.py` builds it and confirms the plan's central IH2 claim: as shipped the import exits 3 "rule 0: support-mismatch: … GND counts 0 of 2"; with the count forced to agree, the checker passes the rule (exit 0), while with differing primitives (Integer vs String) forcing gives exit 70 (checker 'warning'). So the checker does join equal raw values of one primitive across an own-reference subtype, and today's refusal is false.
**Fix:** say "the model's primitive and the population's manager values".

### 12. Completeness — whole-diff obligation cited to the wrong source
**Where:** plan §1 Harvested obligations row 1; IH0 spec §Provenance.
**Evidence:** `009`'s last "Carried forward" row targets "the owner's call at acceptance", not "the next milestone that changes the mined import"; `010` records the owner declined it first. This milestone's authority for IH0 is the owner's 2026-10-29 answer (quoted in the plan's Goal).
**Fix:** cite that answer as the source in the row.

### 13. Completeness — IH0 spec contract gaps
**Where:** IH0 spec §Obligations / §Goal / §Tests.
**Evidence:** the plan's IH0 **Residual** ("a review is a disagreement locator, not a proof") is not copied forward (spec-note-contract §3 requires it); "commits already reviewed are re-read, not skipped" has no obligation row; "red against `fb03739`" should be "red against the fix's pre-fix parent" (if main moves before IH0, `fb03739` is not the pre-fix code).
**Fix:** add the two rows; reword the red reference.

### 14. Completeness — AGENTS.md shim rule and the provenance home's dependencies not argued
**Where:** plan §3 ("IH1 adds none"); IH1 criteria 1, 3.
**Evidence:** renaming `_mined_inputs` → `load_mined_inputs` triggers AGENTS.md's "retain moved names as explicit identity aliases" rule (argue inapplicable for a private name, or keep an alias). The grep criterion (`_mined_inputs` only in `ilp_service` across `src tools`) holds today for `src` but not `tools`, so it is falsifiable — but doesn't cover `tests/`. The inline provenance builder uses `gnd.discover.support.PopulationView.fact_id`; moved into `ilp_amie`, that adds an export→discover cross-lane edge unless it takes the fact-id function as a parameter.
**Fix:** have the IH1 spec fix `ilp_amie.provenance`'s signature and argue/alias the shim rule.

## What held
- Range counts exact: 64 files, +3,628/−193; 125 commits (103 non-merge); with tests 168 files / ~14,300 lines; 539 files overall. `07f4d45` is IL's first commit.
- Every cited name exists: `_mined_inputs`, `_Mined`, `render`, `mapped`, `count`, `Counts`, `MinedRule`, `MAPPING_REFUSALS`, `COUNT_REFUSALS`; `hold()` at `tools/ilp_comparison.py:123` importing `_mined_inputs` at :129.
- `facts-mismatch`-before-mapping claim matches the code.
- IH2's premise is correct: the checker compares raw values, so an own-reference join of equal same-primitive values is falsely refused `support-mismatch` (reproduced, finding 11).
- Harvest otherwise complete: IL4-Q3 (remainder), IL-close-Q1, the `hold()` import, IL4-Q1 (own-reference) all carried; IL-close-Q2, IL1-Q6, IL2-Q2, IL3-Q3, IL5-Q5, IL5-Q6 rightly excluded; IL6-Q3 offered only as a decision.
- IH-R1/IH-R2 consistent with IL-R7/IL-R11; layer map needs no new home; IL-R10's privacy test (`test_t8`) exists and can be widened.
- IH-D2/IH0-D1 cost arithmetic (~4× with tests) is right for the range as defined.
- IL6 golden records `amie 1: 8 mined, 2 hold`, `amie 2: 2/2/2 admitted` — the evidence finding 2 rests on.
