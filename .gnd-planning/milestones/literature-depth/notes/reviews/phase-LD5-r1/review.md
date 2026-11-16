<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
The LD5 diff should not be approved yet. Each support is checked on its own only when the candidate release contradicts itself, and some broken or shared-changed evidence is reported as "no support" instead of being refused or flagged for revalidation. All 20 files matched the brief's SHA-256s. The 10 tests in `tests/test_ld5_verdict.py` pass (99 s), and I reproduced F1 and F2 by building a release in a temporary directory.

## Findings

**F1 — Binding the shared claim to `claims.json` breaks per-support independence, so C2 fails on a consistent release.** `verdict.py:22` binds the shared `claim` to `claims.json`. But `revision.py:383` writes both support records into `claims.json`, and `release-policy.json:619-630` makes that file depend on both `support.json` files.
- In a real re-release where only whale-a's support changes, `claims.json` changes too. The result is `revalidation-required` with stale binding `claim` and no effective supports, so the still-valid corroboration support is lost.
- `test_rehashed_one_support_keeps_the_other_certificate` (`tests/test_ld5_verdict.py:83`) passes only because it leaves `claims.json` listing the old whale-a support. The verifier accepts that self-contradictory candidate as `supported`.
- Repro: I changed whale-a's `support.json` `resolution_edition` and rebound the manifest.
  - With `claims.json` left alone: `supported`, effective `["corroboration"]`, while `claims.json` still lists the old value (114bcb3b).
  - With the same change also written into `claims.json` (manifest status `current`): `revalidation-required`, stale `["claim"]`, effective `[]`.

**F2 — Evidence that can't be checked, or a shared model change, comes back as "unsupported" (exit 2) instead of exit 3.** `verdict.py:30-31` and `:115-116` turn every evidence error into a per-support `stale` with reason `evidence`. That includes KeyError, TypeError, AttributeError and StopIteration, so coding bugs are hidden as staleness. `model.orm.yaml` is also missing from `SHARED` (`verdict.py:21-28`), even though every review and witness depends on it. This contradicts the spec ("malformed inputs refuse at exit 3", and zero support must be distinguishable from revalidation) and the fixture README.
- Repro: deleting `after/manifest.json` gives `unsupported`, both supports `evidence`, CLI exit 2.
- Repro: adding a comment to `after/model.orm.yaml` and rebinding the manifest gives `unsupported`, CLI exit 2. A shared change is reported as "the claim has no support".

**F3 — Test gaps (style; no observed defect).**
- C2 names witness and rule-edition changes, but the per-support tests (`tests/test_ld5_verdict.py:78-82`) cover only occurrence, resolution edition and review.
- The interpretation change from C1 is not in the shared-binding tests (`:58-63`).
- The spec's untrusted-path and installed-example checks are not tested.
- The shared `resolution_edition` and `decision` bindings both hash `decisions.json` (`verdict.py:23,25`), so they are the same binding twice.

**F4 — Asymmetry (style).** The renewed-support replay copies `rule.json` as-is (`revision.py:465`), while the ordinary replay recomputes it from the model (`revision.py:446-447`). The opinion still pins it, so I saw no observable effect.

## Checked and found true
- **C1 (mostly):** the saved opinions are read under the 128 KiB bound and digest-checked before decoding, before any release read. The case and source list is exact and ordered. Oversized, deeply nested, NaN, empty and duplicate documents are refused. A candidate cannot re-pin its own opinions. Rehashed claims, decisions, rule or definition each give `revalidation-required`. Interpretation was not exercised.
- **C3:** the expected results match all five cases: two approvals; one after a rejection; zero; old opinions stale in the revised edition; and a renewed whale-a support with the same occurrence digest (48a6…).
- **C4 (partly):** the renewed replay re-runs the LD4 transition against the pinned preview and review inputs and compares the observed evolution bytes. Replay writes nothing into the release.
- The test added after the spec gate (bf40… → c309…) only adds a test; nothing frozen was changed.

## Not checked
- Whether the pinned evolution preview digest independently covers the old model's digest.
- The installed-package example, the wider literature and structural test selections, and strict component validation.
- The scratch release I built is still at `/var/folders/nb/…/T/ld5rev-bpf150sw`.

The full review is also saved at `<home>/.claude/plans/read-users-nikolaosvasiloglou-codex-work-toasty-dragonfly.md`.

VERDICT: CHANGES_REQUESTED
