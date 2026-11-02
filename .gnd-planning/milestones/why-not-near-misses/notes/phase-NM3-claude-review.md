# Phase NM3 -- one-reviewer diff review

Reviewer: a Claude subagent with read-only repository access and test runs,
given the uncommitted NM3 diff and the approved spec, not the implementer's
conclusions. Machine paths are replaced by `<scratch>`. Report as returned,
lightly condensed.

## Verdict

No material defects. Code, schema, goldens and tests agree with the spec
(D1-D5, H1-H3, T1-T15). No redaction leak. No text names a downstream private
application (grep over the diff and every untracked file outside
`.gnd-planning/`).

## Runs (all exit 0)

- NM3 test files plus the gate set (`test_why_not_near_misses_public`,
  `test_public_why_not`, `test_why_not_repair_loop`, `test_why_not_oracle`,
  `test_public_api`, `test_disclosure_mode`, `test_why_not_anonymity`,
  `test_rf5_handler_pins`, `test_rf5_commands`): 615 passed.
- `test_public_built_inventory`, `test_documentation_tutorials`,
  `test_plan_app_docs`, `test_rf1_layering`, `test_rf6_query_policy`,
  `test_gnd_arch`: 231 passed.
- `tools/run_tutorials.py`; the new how-to block re-run by hand matched the
  documented output byte for byte.
- `tools/check_installed_docs.py --out <scratch>`: 239 blocks passed.
- Not run by the reviewer: `zensical build --strict` and `check_docs.py site`
  (they write `site/` into the worktree). The implementer ran both.

## Spot checks

- Under `GND_DISCLOSURE=customer`, `api.why_not` on the spelling gap returns
  `view: redacted` in row and rule mode; none of the population strings
  appears.
- `redacted_clause` pins `near_misses` to `"redacted"` at every descent depth;
  N2 fails on the redaction rule, not the non-atom rule.
- The count-tie clauses are exactly D2 (a). Each T7 negative validates its
  unmutated base first.
- Docs claims checked against `src/gnd/witness/why_not.py`: normalization
  examples, canonical-byte order (`1.0` before `1`), at most 25 pairs per key,
  and the truncation flag false at default limits.

## Findings (all reproduced)

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| R1 | low | T8's last assertion compared `rows` with the same dict objects, so "other rows untouched" could never fail | fixed: snapshot copies before the edit, compare by index |
| R2 | low | The spec's installed-docs command omits the required `--out` | recorded as finding F2; the gate used `--out <scratch>` |
| R3 | low | The release-note migration line paraphrased the spec's mandated words | fixed: the spec's words |
| R4 | low | The milestone README still said the NM3 spec awaits review | fixed in the README update |
| R5 | info | "The Python API returns raw values" in `why-not.md` is false under customer | NM4 by the spec (H1); pre-existing since NM2 |
| R6 | info | T6 does not validate the unset-mode API payload | no change: T5 shows unset equals internal |
