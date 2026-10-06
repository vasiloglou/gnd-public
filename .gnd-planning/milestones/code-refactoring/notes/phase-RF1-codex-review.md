# Phase RF1 — single adversarial review (Codex)

**Edited retained evidence.** The reviewer's output below is verbatim except
for one sanitization: absolute paths to the local checkout were replaced with
`<repo>/`, and the capture's final `exit=0` line was dropped. One reviewer is
one reviewer; this is not a panel.

- Reviewer: `codex exec --ephemeral --ignore-user-config --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0.
- Reviewed: `git diff e834c6e..766d907` over the RF1 tests, fixtures, tools, records and spec.
- Limit stated by the reviewer: the read-only sandbox prevented pytest's temporary files, `tmp_path` fixtures and any mutation replay. It ran collection, the layering file with `-s`, and in-memory reproductions, and read the committed mutation report without rerunning it.

## Dispositions

Every finding was reproduced before disposition. Regression tests written for
the fixes were observed red against the pre-fix code
([evidence](../evidence/phase-RF1/review-regressions-red.txt): 11 failed).
RF1-07 was reproduced with a harness row that survived (`R07-directory-identity`).
Owner ruling 2026-10-05 ("ok do 2"): fix the real holes, record the rest as
owed or deferred.

| Finding | Class | Disposition |
|---|---|---|
| RF1-01 absolute path in `anchored.json` | blocking | Fixed: the repository root is scrubbed; `test_r01_goldens_carry_no_machine_paths` now guards every golden |
| RF1-02 prompt digests and the argv prompt token erased | blocking | Fixed: N7's erasure removed. The session lane supplies the prompts the CLI should build (base, policy-bound controller prompt, and each retry prompt from the run's feedback leaves) as declared inputs, and N5 verifies each digest; an unmatched digest stays literal. Nonce: a 64-hex value is a placeholder, any other shape stays literal (`test_r02_*`) |
| RF1-03 seconds placeholders hide accounting regressions | hardening (own deliverable) | Fixed: `check_timing` refuses negative durations and records that end before they start, before placeholders apply (`test_r03_*`). Budget bounds are not checked |
| RF1-04 N8 erases every `result_sha256` digest | hardening (own deliverable) | Fixed: limited to `.xml` entries (`test_r04_*`) |
| RF1-05 declared-input digests verified against current bytes only | hardening | Not changed. The inputs are test-authored fixtures that no refactor of `src/gnd` can change; a change to how GND computes such a digest leaves a literal hex and reds the pin. Recorded as an open question |
| RF1-06 N4 forbidden list built from staging paths that still exist | hardening (own deliverable) | Fixed: the three staging-name shapes GND generates are refused in published bytes directly (`test_r06_*`) |
| RF1-07 `directory_identity` credited through a fixed-tree digest | blocking (false credit) | Fixed as owed: removed from `PINNED_VIA`, listed in `OWED` and in the inventory as owed by RF4 under RF-R3 |
| RF1-08 three meta nodes exempted from RF1-C1 | completeness (spec departure) | Deferred by owner ruling: recorded as an RF1-C1 narrowing and an open question |
| RF1-09 a setup or teardown failure counted as a kill | blocking (instrument) | Fixed: only a call-phase failure kills; other failures are `error` (`test_r09_*`). The full table still kills 167 of 167 |
| RF1-10 owed inventory rows map to no test | blocking (criterion wording) | Fixed in part: owed rows carry their RF-R3 or D9 anchor and `test_r10_*` refuses an unanchored one. An independent plan-surface list is deferred |

## Reviewer output (verbatim, paths sanitized)

## Findings

- **RF1-01 · high · blocking** — [anchored.json](<repo>/tests/fixtures/rf1-pins/goldens/sem-check/anchored.json:129) contains this reviewer’s absolute worktree path in the unkeyed golden, including the `model` and `population` fields. `rg -n '/Users/' tests/fixtures/rf1-pins/goldens/sem-check/anchored.json` reproduces it. The same `test_check_anchored` observation from another checkout will differ. Normalize the repository root before comparison and recapture this golden.

- **RF1-02 · high · blocking** — [rf1_pins.py](<repo>/tests/support/rf1_pins.py:196) replaces every valid prompt digest and nonce with a placeholder. A direct call to `normalize_text` with `prompt_sha256` values of `"a"*64` and `"d"*64` produces the same result; the `<prompt:sha256=…>` token is also erased. A refactor can change prompt bytes while the session golden stays green if the fake agent responds identically. Pin a digest of the normalized prompt, and check nonce format and relationships separately.

- **RF1-03 · medium · blocking** — [rf1_pins.py](<repo>/tests/support/rf1_pins.py:233) replaces encoded-float `elapsed_seconds` and monotonic values regardless of their magnitude. I passed `{"elapsed_seconds":{"float":"0.1"},"started_monotonic":1000.0}` and `{"elapsed_seconds":{"float":"999.0"},"started_monotonic":-1.0}` to `normalize_text`; both normalized identically. This hides an accounting or ordering regression. Add semantic checks for nonnegative durations, ordering, and budget bounds.

- **RF1-04 · medium · hardening** — [rf1_pins.py](<repo>/tests/support/rf1_pins.py:204) applies the JUnit digest placeholder to *every* digest inside an object named `result_sha256`. The input `{"result_sha256":{"not-junit":"c"*64}}` normalizes identically when `c` becomes `f`. Restrict N8 to the declared tests-mode JUnit path and verify its provenance.

- **RF1-05 · medium · hardening** — [rf1_pins.py](<repo>/tests/support/rf1_pins.py:243) verifies an external input’s digest against its *current* bytes, then replaces that digest without pinning the input bytes. I normalized an index containing the SHA-256 of `{"mode":"allow"}` and then `{"mode":"deny"}`, supplying each as `inputs["policy"]`; the normalized evidence was identical. Bind declared external inputs to expected content or a separately pinned semantic projection.

- **RF1-06 · medium · hardening** — [test_rf1_session_pins.py](<repo>/tests/test_rf1_session_pins.py:254) builds N4’s forbidden staging-name list only from staging paths that still exist after the run. With no such path, `_forbidden(root)` returned `[]`, and `normalize_tree` accepted `{"staging":".staging-deadbeef"}` in a published file. Detect the staging-name pattern in published bytes directly.

- **RF1-07 · medium · blocking** — [test_rf1_helper_pins.py](<repo>/tests/test_rf1_helper_pins.py:72) credits `artifacts.directory_identity` through a fixed-tree digest test. I replaced that local helper *in memory* with `return (0, 0, 0, 0, 0)` and hashed `tests/fixtures/v70-phase1`; the baseline and mutant digests were equal. The fixed tree never exercises the identity-change refusal, so T-HELP-COV credits a safety behavior its routed pin cannot detect. Add a changing-stat case for that branch.

- **RF1-08 · medium · blocking** — [mutations.json](<repo>/tests/fixtures/rf1-pins/mutations.json:12) exempts `test_cli_coverage`, although RF1-C1 and spec §6.9 require every collected RF1 pin node to have a mutation row. [The test](<repo>/tests/test_rf1_cli_pins.py:155) depends on source parser count. Read-only collection found 353 pin-file nodes: 350 named and three exempt. Seed a parser addition or removal for this node, or explicitly narrow RF1-C1.

- **RF1-09 · medium · hardening** — [rf1_pins.py](<repo>/tools/rf1_pins.py:203) marks a node failed if *any* setup, call, or teardown report failed. For events `[(setup,passed),(call,passed),(teardown,failed)]`, the implemented condition returns `failed`, so [the row becomes “killed”](<repo>/tools/rf1_pins.py:258) although the pin assertion passed. Record phases separately and require a call-phase failure for a mutation kill.

- **RF1-10 · medium · blocking** — [inventory.json](<repo>/tests/fixtures/rf1-pins/inventory.json:315) lists RF5 command handlers with neither RF1 nor existing test nodes; the RF2 measure/export refs and RF6 split paths are likewise `owed`. This contradicts RF1-C4’s stated mapping to tests that collect. [T-INV](<repo>/tests/test_rf1_pin_harness.py:109) permits these rows and has no independent plan-surface list: removing the RF2 owed row in memory left its reference set unchanged. Add the mappings before claiming C4, or state the approved `owed` exception in the criterion.

## Checks that held

- **RF1-C2:** `git diff e834c6e..HEAD -- src/gnd` is empty; changed paths fall within tests, tools, and milestone records.
- **Layering:** RF0’s 27 edges form the 23 pairs in `KNOWN_PAIRS`; the scoped 16 cases ran as strict xfails. The focused run returned **4 passed, 16 xfailed**.
- **Alias resolver:** I loaded both revisions of `tools/gnd_arch.py` in memory and compared `measure` over this repository. Every reported section, including edges and layering, was equal.
- The golden manifest check passed, and the helper-site inventory has no missing site IDs. Those checks do not resolve the sensitivity findings above.

The sandbox prevented pytest’s default temporary-file capture and any replay that writes mutation copies or `tmp_path` fixtures. Read-only collection and the focused tests above ran with `-s`; I inspected the committed 167/167 mutation report but could not independently rerun it. No file was modified.
