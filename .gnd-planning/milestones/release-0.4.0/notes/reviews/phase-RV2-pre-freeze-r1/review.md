All three named files match the SHA-256 values in the brief. I only read code; nothing was built or run, because plan mode was on and the brief ruled out building release artifacts.

**Answer:** I found no probe that would pass with the feature absent or broken, and none that would fail on a valid installed candidate. One gap matters for C3, and there are two minor notes.

## Findings

**F1 — the acceptance file doesn't check that the wheel was built from the checkout's commit (C3; this predates the diff and the diff doesn't fix it).**
- **Where:** `tests/test_release_acceptance.py:63-69` and `:127`. The `installed` fixture extracts `git archive HEAD` from wherever pytest is launched. `verify_files` only hashes `release/` and `comparison/`. Nothing compares `candidate/SOURCE_COMMIT` with `HEAD`.
- **Where that check does exist:** only in CI, at `.github/workflows/development.yml:97` (`test "$(cat candidate/SOURCE_COMMIT)" = "$(git rev-parse HEAD)"`). The spec's main beast-3 command (`phase-RV2-spec.md:64`) is just `GND_CANDIDATE_DIR=… uv run pytest …`.
- **Consequence:** suppose a retained 0.4.0 wheel was built from commit A, and pytest runs from a checkout at commit B that also says 0.4.0. Every version check passes. P1 reads the guard fixture from B, the RN2 regressions read their Q4/Q5 inputs from B, and P4 reads its golden from B. P4's harness-SHA comparison is the only part that would catch the mismatch, and only if `assurance_report.py` differs between A and B. So the claim that "all gate evidence can follow the actual owner-merged commit" depends on a manual step, not on the test.
- **To reproduce (by reading):** run the spec's command from a checkout whose HEAD is not `SOURCE_COMMIT`. No assertion in the file looks at `SOURCE_COMMIT`.

**F2 — P2 never reads the generated manifest before mutating it (completeness, low).**
- **Where:** `:593-600`. The spec says "the generated manifest binds a same decision." The test only checks that `resolution.json` holds `same` and that the composition record shows `decisions == [0]`.
- **Consequence:** the manifest's binding is only evidenced indirectly: by the record and by `check --sources` exiting 0. It is first read at `:648`, and that's to mutate it. I couldn't find a broken build that would get past this, because the mutant step would raise a `KeyError` or compose would refuse. So the effect is weaker evidence, not a false pass.

**F3 — style only.** The new top-level import at `:18`, `support.recorded_version`, imports the source-tree `gnd` into the outer pytest process (`tests/support/recorded_version.py:39`). It only supplies the pure `move_version` helper, and no probe result comes from it. Every candidate command still runs through the isolated venv with `-I`, under the sandbox wrapper on macOS. Collection now needs the project environment, which both `uv run pytest` invocations (CI and the spec) provide.

## What I checked and found true

- **C1:**
  - `rv2_installed` builds on the `installed` fixture, which is parametrised over `release` and `comparison`. So all four RV2 tests (P2 and P3 share one test) run against both wheels.
  - `published_0_3_0` checks the wheel against the pinned whole-file SHA-256 `143890ee…`, which matches the spec, and asserts `gnd 0.3.0`.
  - The 0.2.0 hash removed here is still kept in the planning records (RR2 and RN2 evidence).
- **C2:**
  - The probes run through `python -I` from the venv built from a copied wheel, outside the repo, with a filtered environment.
  - The interop and assurance harnesses call `sys.executable -m gnd`, so they also stay in that venv.
  - `test_installed_0_3_0_regressions` keeps every Q1–Q5 assertion. Only the `== '0.3.0'` pin and the retired 0.2.0 negative control are gone, as C4 directs.
- **P1 discriminates:**
  - If `where` were ignored, amount 50 would fail with exit 1 rather than come out vacuous with exit 2.
  - If `in` were broken, the amount-250 case would pass when it should fail.
  - "Vacuous with `binding_count` 0" matches `tests/test_guarded_antecedent_filters.py:64-70`.
- **P2 and P3:**
  - The diagnostic strings exist in the current source: `composition_resolution.py:333,352` and `witness/service.py` (`binding-stale`).
  - The 0.3.0 strings exist at tag `v0.3.0`: `composition.py:93` and `:227`. The reference-populations refusal fires before the manifest is parsed, so the old catalog control can't hit the manifest error by mistake.
  - `A-alias` expects exit 0 according to `cases.json`.
  - `gnd.model.bind_references` and `gnd.errors.ReferenceHashMismatch` exist.
  - The catalog mutation appends a single space, so the JSON stays valid and only the hash pin can catch it.
- **P4:** the golden comparison follows the source test (`tests/test_li1_assurance_report.py:465-470`): harness SHA replaced, version moved, nothing else normalised.
- **P5:**
  - The expected offending rows match `tests/test_expense_receipts_example.py:55-59` exactly.
  - The receipts model has `reference_populations`, so reading `checked['report']['verdicts']` from the wrapped output is correct (`checking_service.py:751`).
  - The 0.3.0 resource-absence controls hold: `v0.3.0` has no `receipts`, `assurance_report.py` or `interop` example.

## What I could not check

- **Actual run results.** I didn't run anything (plan mode; no release builds). I couldn't confirm these on a real wheel:
  - P4's mutant ending with exactly `['identity-decisions','derivation','freshness']` at exit 1. It differs from the source test's M1 case, so only the author's rehearsal supports it.
  - The exact 0.3.0 schema `rule_id` set in P1.
  - The RN2 Q1–Q5 regressions passing on 0.4.0.
- **Retained evidence.** The review folder has no rehearsal logs: `review.log` and `review.md` are empty.

VERDICT: APPROVE
