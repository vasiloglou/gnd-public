I'm requesting changes. All 14 file hashes match the brief, so the review covers the bytes it names. The accessor crashes in customer mode on most plain snapshot reports, and Python accepts a vacuity combination the CLI refuses. Read-only throughout. The only file I wrote was the plan-mode file, and my probe scripts went to `/tmp`.

## 1. Findings

**F1 (high): `snapshot_verdict` crashes in customer mode and returns `derivations: None` in internal mode, for any model without derived fact types.** `src/gnd/api.py:800-801` and `:803`
- **What's wrong:** Plain reports carry the key `"derivations": null` when the model has no derived fact types. `body.get("derivations", [])` only helps when the key is missing, so it returns `None`.
  - In customer mode the list comprehension then raises `TypeError: 'NoneType' object is not iterable`.
  - In internal mode the result's `derivations` is `None`, not the list the docs and the customer branch imply.
- **What a user sees:** A customer-mode caller cannot read the verdict of an ordinary plain check. That includes the #331 vacuity case this phase exists for.
- **Fitted to fixtures:** The customer-mode test uses only `dispatch`, which has a derivations list, so this case is never exercised.
- **Reproduced:** I ran it.
  ```python
  raw = api.check("src/gnd/examples/approvals/model.orm.yaml", "src/gnd/examples/approvals/state.pop.yaml")
  api.snapshot_verdict(raw)["derivations"]   # None
  os.environ["GND_DISCLOSURE"] = "customer"
  api.snapshot_verdict(raw)                  # TypeError at api.py:801
  ```
- **Same crash in customer mode on:**
  - every `tests/fixtures/rc4-allow-vacuous` population (`vacuous-only`, `fail-and-vacuous`, `unchecked-and-vacuous`), with and without `allow_vacuous=True`;
  - the approvals example on schemas 7, 10 (admission) and 16 (guarded diagnostics).
- **Should return:** a list, `[]` for these reports, in both modes.

**F2 (medium): Python accepts `allow_vacuous=True` together with anchors/document; the CLI refuses that combination.** `src/gnd/api.py:722-723`
- **What's wrong:** The new guard rejects only admission, compiled_operations and composition. The CLI's `--allow-vacuous` also excludes `--anchors` and `--document` (`commands/checking.py:1199-1221`).
- **Reproduced:** I ran both sides on `tests/fixtures/v70-phase1`.
  - CLI: `gnd check model.orm.yaml population.pop.json --anchors population.pop.json.anchors.json --document document.txt --allow-vacuous` exits **64** with a usage error.
  - Python: `api.check(..., anchors=..., document=..., allow_vacuous=True)` returns a **schema-15** report with an extraction block and exit 0. Without the option the same call gives schema 7.
- **What a user sees:** the opt-in policy does not match the CLI, and Python emits a report shape the CLI never produces. The spec asked to "reject incompatible modes before evaluation".

**F3 (low): the refusal names a CLI flag the Python caller never used.**
- `api.check(dispatch model, seed.pop.json, allow_vacuous=True)` exits 3 with the diagnostic "`--rule-ids` supports models whose check report is plain version 7…".
- The exit code matches the CLI's `--allow-vacuous` result (3 on both sides), so there is no behavioural difference. The wording comes from code this phase did not change.
- `python-api.md` says only "applies to plain snapshots". It does not say that reference, temporal or redaction-policy models become invalid-input under the option.

## 2. What I checked and found true

- **Focused suite:** the spec's selection plus `test_v61_phase2_api.py` passes (46 tests). The disclosure table and surface tests pass (5).
- **Envelope sweep, internal mode:** I ran every bundled example with plain, admission and guarded-diagnostics checks. Versions 7, 10, 12 wrapping 11, 14 wrapping 13, and 16 all map to the right status. Exit 3 maps to invalid-input, including the missing population with zero fail counts.
- **Wrapper consistency:**
  - An outer 3 or 70 over an inner success returns the failure status with empty constraints.
  - An outer/inner exit mismatch otherwise returns invalid-report.
  - Unknown versions return unsupported-schema.
  - Version 8, the transition successor, is excluded as documented.
- **Vacuity parity on the rc4 corpus:** Python and CLI agree on exits 0, 1 and 4 and on the counts. The default stays exit 2, and the accessor reports `vacuous`.
- **Default path unchanged:** `allow_vacuous=False` produces a report equal to the old call. The keyword is added only when it is true.
- **Grounded-inventory example:** an empty outcome relation gives violated, a missing one gives unchecked, a matching outcome gives accepted.
- **Fitted-code check:** the change adds no regular expression, string split or slice over structured text. The version tuple and the status map are closed literal sets, which is fine. The one input class the fixtures miss is the null `derivations` value in F1.

## 3. What I could not check

- I did not test hand-tampered but schema-valid plain reports, such as exit 0 with a failing alethic verdict. The accessor trusts `exit_code` for plain reports.
- I did not run the full test lane.
- I did not test the doc claim that "a role-local mandatory constraint on outcomes alone can be vacuous".

VERDICT: CHANGES_REQUESTED
