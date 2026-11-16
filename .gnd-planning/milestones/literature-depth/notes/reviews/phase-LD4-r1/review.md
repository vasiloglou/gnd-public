# LD4 phase diff review (`0d35a0b0` → `05546dc0`)

All 32 files listed in the brief match their SHA-256 values, and HEAD is `05546dc0c605`. `uv run --no-sync pytest -q tests/test_ld4_revision.py` passed all 9 tests (119 s). For the probes I built one release in `/tmp/ld4probe` and changed only scratch copies of it. Nothing in the repository was touched.

## 1. Findings

**F1 — Two policy edges point the wrong way, so `status` reports derived artifacts as current when their input changed.** `src/gnd/examples/literature/revision_fixture/release-policy.json`, after-snapshot rows for `sources/resolution.json` and `evolution/proposal.json`.
- **Resolution edge:** `revision.py:189` writes `decisions.json` straight from `sources/resolution.json`. The policy has it backwards: `sources/resolution.json` lists `decisions.json` as a requirement.
- **Proposal edge:** `revision.py:249–266` builds `evolution/model.orm.yaml` from `evolution/proposal.json`. The policy has `proposal.json` require `evolution/model.orm.yaml`, and the evolved model lists only `model.orm.yaml`.
- **What a consumer sees:**
  - Append one byte to `after/sources/resolution.json`: `status` puts `decisions.json` under `current`, even though its content equals the resolution file.
  - Edit `after/evolution/proposal.json`: `evolution/model.orm.yaml`, `evolution/definition.json` and `evolution/reviews.json` stay `current`.
  - Edit `decisions.json`: the input `sources/resolution.json` is reported stale.
- **Why it matters:** this breaks C1 ("each changed kind propagates only to its descendants"), because the graph's descendants are not the real ones. The full `replay` would still catch the change, but `status` is the bounded tool the spec gives for reporting dependents.
- **Reproduce:** copy a release, append a byte to the file, run `revision.status(copy/"after")`. I ran this (probes P1, P2, P6).
- **Why the tests miss it:** `test_every_required_kind_and_transitive_staleness` builds its expected answer from the same policy graph, so it can't detect a wrong edge.

**F2 — The corroboration certificate depends on the whale-a source, so removing the other source invalidates both supports (C5, D7).** In `release-policy.json`, `supports/corroboration/review.json` requires `composition.json`, which goes through `sources/manifest.json` to `sources/whale-a/*`. Also, `revision.py:411–415` (`replay_support`) always copies and recomposes `sources/{whale-a,whale-b}/*`, and `_editions` mixes the composed manifest into `resolution_edition`.
- **What a consumer sees:**
  - Delete `after/sources/whale-a/document.txt`: `status` marks `supports/corroboration/witness.json` and `supports/corroboration/support.json` stale, and `replay_support(..., "corroboration")` fails with "support evidence is stale".
  - The other direction works: deleting the corroboration document leaves `supports/whale-a/support.json` current.
- **Why it matters:** the two supports are not independent. If LD5 retracts whale-a, it cannot keep the corroborating certificate, which is the reverse of what D7 says.
- **Why the tests miss it:** the test only deletes the corroboration *witness*, never the other support's *source*.
- **Reproduce:** probe P3 / P3b.

**F3 — Changes to the before snapshot don't show up in after's status, although after artifacts are derived from it.** `revision.py:221–234` builds `after/migration.json` from `before/composition.json` and `before/population.json`. `revision.py:353` builds `release.json` from `before/claims.json`. The policy graph (`revision_manifest.py:83–123`) stays inside one snapshot, and `status` never reads `release.json`.
- **What a consumer sees:**
  - Edit `before/composition.json`, then run `status` on after: it reports `current`, with `migration.json` current.
  - Delete `before/` entirely: after's `status` still reports `current`.
  - Full `replay` does refuse.
- **Why it matters:** for C1/D1, `status` under-reports which artifacts depend on a change. Probes P4 and P5.

**F4 — The rule-only control never checks that its vocabulary is unchanged (C4, D6).** `revision.py:288–296` runs `check --baseline-model` and counts deltas. Nothing compares the fact types or roles of `comparison/base.orm.json` and `comparison/head.orm.json`.
- **What the fixture actually contains:** a different model, `recorded_designation`. The only difference is a narrowed value constraint (`allowed: [stable, candidate]` → `[stable]`). It doesn't touch the `method_has_ancestor_method` derivation rule that `rule_edition` binds, and the policy has no edge between `comparison/*` and `rule.json` or `model.orm.yaml`.
- **Why it matters:** "unchanged vocabulary" is true of the fixture bytes but nothing enforces it. A head with a changed role would still pass if the counts happened to match. I found this by reading and by diffing the two JSON files; I did not mutate and replay.

**F5 — The covered absence becomes stale because of the snapshot name, not the vocabulary change (C3, D5).** `revision.py:202–203` sets `status: "stale"` whenever `snapshot == "after"`. `coverage_key` (`method-family`) is a fixed string in `interpretation.json`; it isn't derived from the resolution renamings or the definition change.
- **What is checked:** the code does confirm that this key selects the related question and leaves the unrelated one alone (`revision.py:166–172`).
- **What isn't:** that the key is the one this revision actually changes. The same release would declare the absence stale for any after snapshot.
- **Found by:** reading only.

**F6 (minor) — The additive-preview control accepts any policy issue.** `revision.py:254` requires exit 3 and a non-empty `policy_issues`. It doesn't check that the issue concerns the `method_builds_on_method` reading edit. Found by reading; no observed consequence with the current fixture.

## 2. Checked and found true

- **Policy before candidate:** a wrong policy pin fails before the candidate is read. Escaping paths, overlong paths and forward dependencies are refused. Empty, duplicated and missing-row rosters are refused, as is a before manifest placed in the after directory. A symlinked artifact counts as changed. Hostile JSON and oversized rosters are refused in under 3 s (all tests).
- **C2 query outcomes:** three paths lost, two preserved. The occurrence map is keyed by source ID, fact type and index, and only the whale-b fact 0 occurrence changes. The WHAM ambiguity carries two candidates. A rehashed forged `migration.json` fails replay.
- **Before-snapshot independence:** `replay --snapshot before` succeeds with `after/` and `release.json` deleted (P7), and the original witness digest is unchanged.
- **C4 evolve and review:**
  - The ordinary preview is pinned to `APPROVED_PREVIEW_SHA256`.
  - Apply binds the old and new model SHA.
  - The old review fails as "stale judgment subject".
  - The renewed review keeps the same `sources` and subject, apart from `model_sha256`.
  - Review inputs are consumer-pinned (`REVIEW_INPUTS_SHA256`) and not taken from the release.
- **C5 distinctness:** the two supports have different review, witness and document digests. The quote spans hash correctly, and each certificate replays on its own, including when the corroboration witness is missing.

## 3. Not checked

- I did not run the structure gates, strict component validation or the standalone installed example (T8).
- I did not build a fully self-consistent forged release from altered fixture inputs (for example a changed `targets.json`), so I can't say whether replay would accept one.
- F4–F6 come from reading the code, not from running it.

VERDICT: CHANGES_REQUESTED
