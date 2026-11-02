<!-- Retained review of the NM2 diff, 2026-11-01: one reviewer (a Claude subagent,
general-purpose, run from this session), full repository read access plus the
ability to run tests. EDITED: absolute machine paths were replaced with
<scratch>/ and <worktree>/; the body is otherwise verbatim. The disposition
follows the review. -->

# NM2 (disclosure mode) adversarial diff review

Subject: `git diff acfb9ae -- src tests tools` plus the two evidence files, in the
worktree `intelligent-pasteur-df4027`. The scripts are in this directory and are
run from the worktree root with `uv run python <script>`. No repository file was
edited.

Baseline: `uv run pytest -q tests/test_disclosure_mode.py` gives 59 passed. The
gate subset (rf1_layering, rf6_query_policy, public_api, rf1_cli_pins,
rf1_pin_harness, rf5_commands, rf5_handler_pins, rf4_peripheral,
rf1_agent_cli_pins, agent_cli, solve) gives 1624 passed.

S = `<scratch>/nm2-review`

---

## R1 — blocking — `gnd doccheck` is classed value-free but prints declared-redact population values in every mode, including customer

- **Where:** `src/gnd/disclosure.py:101-106`, where `"doccheck"` is in the
  value-free `_rows`. The emitting code is
  `src/gnd/fidelity/doccheck_service.py:229-249`.
- **Claim:** The rendering obligation prints each missing filler as
  `{value!r}`, for example `VIOLATION rendering: has_email.email reference value
  'bo@example.com' is not mentioned in the document`. This is a value of a
  `redact: true` role.
  - Under `GND_DISCLOSURE=customer` the output is the same. The leaf is not
    disclosure-bearing, so the mode is ignored, and `gnd --disclosure customer
    doccheck …` is silently accepted.
  - The table is NM2-C2's normative deliverable, and NM4 generates the public
    docs table from it. The table would tell a customer-mode operator that
    doccheck emits no values. That is a false statement about a value-emitting
    surface.
  - T13 checks only the table's keys, never their classes, so nothing catches it.
- **Reproduction:** `S/r_doccheck.py`
  ```
  mode=None exit=3 leaks_bo@example.com=True
     ["VIOLATION rendering: has_email.email reference value 'bo@example.com' is not mentioned in the document", ...]
  mode=customer exit=3 leaks_bo@example.com=True
  SURFACES['gnd doccheck'] = Surface(kind='value-free', convention=None, spawns=False, note='')
  ```
- **Fix:** Reclassify `gnd doccheck` as `every-mode` with a note ("quotes source
  population fillers the document does not mention"), and record the finding as
  the spec requires for a class move. Alternatively, make it a site that prints
  role and fact type without the value under customer. Add it to T26.
- **Other leaves checked:** I audited the remaining value-free leaves for similar
  emitters: `extract`, `synth`, `coverage`, `exp author-expectation` (it is
  answer-free by design), `export pyrel` (it takes no population), `measure` and
  `verify --out` (both governed by `--unredacted`), and the import leaves.
  `import mined-rules` and `import ilp-rules` build their schema from
  `RedactionPolicy.effective_roles`. I did not prove they are value-free:
  UNREPRODUCED either way.

## R2 — hardening — the RF4 body pin no longer covers the witness and replay algorithms

- **Where:** `src/gnd/witness/service.py:42, 71, 186-194` and the two
  `source-successors.json` rows for `witness` and `replay`.
- **Claim:**
  - `test_moved_algorithm_preserves_base_body` pins, by digest, the body of each
    `moves.json` name. The moves.json names homed in `gnd.witness.service` are
    only `_witness_inputs`, `replay` and `witness`.
  - After D1 (b), the new successor rows bind `witness` and `replay` to their
    two-line mode wrappers. The actual algorithm moved to `witness_result` and
    `replay_result`, which no row or pin covers.
  - So an unrecorded future change to the raw algorithm passes the RF4 body test.
    The successor reasons say "the unchanged raw body moved to witness_result",
    but nothing checks that. I checked by hand that it is true today: the only
    change is the renamed `def` line.
- **Reproduction:** `S/r_pin_drift.py` (output in `r_pin_drift.out`)
  ```
  moves.json names homed in gnd.witness.service: ['_witness_inputs', 'replay', 'witness']
  witness: pinned digest unchanged under a witness_result edit: True
  replay: pinned digest unchanged under a witness_result edit: True
  ```
- **Fix:** Add a test, or a successor-style row keyed by the new name, asserting
  that the `_algorithm` digest of `witness_result` and `replay_result` (renamed
  to the old name) equals the RF4 base digest of `witness` and `replay`.

## R3 — hardening — `invoke_agent(extra_environment=…)` treats every supplied name as disclosed, so a secret routed through it is unmasked

- **Where:** `src/gnd/agents.py:276-282, 385, 426`
  (`disclosed_names=frozenset(extra)`).
- **Claim:**
  - The new keyword is public, and its comment calls it "non-secret". But
    masking is turned off for every name it carries. A caller that passes, or
    overrides, a credential name has that value written verbatim into the
    retained stdout and stderr, and into session evidence.
  - The fact list then records the name twice (`inherited` and `supplied`).
  - Only `GND_DISCLOSURE` needs to be disclosed. The runner's guarantee
    ("every supplied environment value is masked") is now one keyword away from
    being broken.
- **Reproduction:** `S/r_unmask.py` (output in `r_unmask.out`). A fake `codex`
  prints its key.
  ```
  None -> b'key=*** mode=' [('ANTHROPIC_API_KEY', 'inherited')]
  {'GND_DISCLOSURE': 'customer'} -> b'key=*** mode=customer' [...('GND_DISCLOSURE', 'supplied')]
  {'ANTHROPIC_API_KEY': 'sk-override-secret-2222'} -> b'key=sk-override-secret-2222 mode=' [('ANTHROPIC_API_KEY', 'inherited'), ('ANTHROPIC_API_KEY', 'supplied')]
  ```
- **Fix:** Take `disclosed_names` from the caller explicitly. For example,
  `invoke_agent(..., extra_environment, disclosed_names=frozenset({"GND_DISCLOSURE"}))`,
  where session.py passes `frozenset(forwarded)`. Alternatively, refuse
  `extra_environment` keys that collide with the inherited names. Either way,
  `agents` stays parameter-only (NM-R7).

## R4 — hardening — the CLI walk ignores, and then overwrites, an enclosing customer context

- **Where:** `src/gnd/cli.py:712-727` (`mode = option or env`) and
  `_disclosed` → `disclosure.invocation(mode)`.
- **Claim:**
  - `disclosure.resolve()` combines the context variable with the environment.
    The CLI walk uses only the option and the environment, then *sets* the
    context variable to the result, or to None on non-bearing leaves.
  - An in-process embedder that runs `cli.main` inside
    `disclosure.invocation("customer")` therefore has `--unredacted` honoured.
    Meanwhile `gnd.api` refuses the same request in the same context.
  - Two sites resolve the mode differently. `invocation` is a public name in
    `gnd.disclosure`.
- **Reproduction:** `S/r_outer_ctx.py` (output in `r_outer_ctx.out`)
  ```
  api: refused: unredacted=True is refused in customer disclosure mode
  cli: exit 1 leaks ann@example.com: True
  ```
- **Fix:** In `_disclosure`, include the current context value as a tightening
  source (`"customer" if "customer" in (_MODE.get(), env, option) else option or env`).
  Alternatively, make `invocation` private and document it as CLI-only.

## R5 — completeness (test weakness) — D3/H3 is unguarded: T27 does not test `judgments`, and the H3 regression survives the whole suite

- **Where:** `tests/test_disclosure_mode.py:352-370` (T27).
- **Claim:**
  - Spec T27 is "`api.judgments(unredacted=False)` under customer returns (not
    refused); `judgment_policy` redacted". The test never calls `judgments`.
    It checks only that `check_with_feedback` hands `unredacted=False` to a
    *stubbed* `_check_unresolved`.
  - Because it monkeypatches `_check_unresolved`, it also cannot see a
    regression in which the private check resolves the mode.
  - Mutant `internal-callers-resolve` reintroduces exactly H3: `_check_unresolved`
    resolves like the public function. Under that mutant, `judgments` under
    customer silently returns a `binding` error (outcome 3). Its internal raw
    check raises `DisclosureRefused`, a `ValueError`, which `judgments`' broad
    `except` converts. Session feedback becomes unredacted under internal.
    All 59 tests still pass.
- **Reproduction:**
  - `S/mut/nm2_mutants.py` is a pytest plugin. It is run as
    `NM2_MUTANT=<m> PYTHONPATH=S/mut uv run pytest -q -p nm2_mutants tests/test_disclosure_mode.py`,
    and the results are in `S/mutants.out`.
  - `S/r_judgments_mutant.py` shows the behaviour:
    ```
    real  : outcome 0 error None
    mutant: outcome 3 error {'reason': 'binding', 'message': 'invalid bound judgment input'}
    ```
  - mutants.out: `internal-callers-resolve: 59 passed`.
- **Fix:** Make T27 call the real `api.judgments` (unstubbed check) under
  customer. Assert that outcome is not 3, that there is no error, and that
  `judgment_policy` equals the unset result. Add an unstubbed
  `check_with_feedback` run under internal and assert its payload equals unset.

## R6 — completeness (test weakness) — internal-mode behaviour of `validate`, `diff`, `transition` and `judgments` (API) is untested

- **Where:** `tests/test_disclosure_mode.py:314-349`. F8 records the gap; this
  finding measures it.
- **Claim:** Mutants that keep the customer refusal but never act as internal
  survive for all four functions. Matching controls for `check` and `verbalize`
  are killed, which proves the plugin is active.
- **Reproduction:** `S/mutants.out`
  ```
  validate-ignores-internal: 59 passed
  diff-ignores-internal: 59 passed
  transition-ignores-internal: 59 passed
  judgments-ignores-internal: 59 passed
  judgments-refuses-under-customer: 59 passed
  check-ignores-internal (control): 1 failed, 58 passed
  verbalize-ignores-internal (control): 1 failed, 58 passed
  ```
- **Fix:** Extend the T16 and T17 API loop to `validate(MODEL)`,
  `diff(MODEL, MODEL, populations=[POP])`, a `transition` on a small walk
  fixture, and `judgments`. The fixture from `r_judgments_mutant.py`, with
  stubbed policy and receipts, is enough. Assert that internal equals
  `unredacted=True` and that customer equals unset.

## R7 — completeness (test weakness) — T26 cannot detect an every-mode leaf that starts following the mode, and T15 cannot fail

- **T26** (`tests/test_disclosure_mode.py:478-506`)
  - **Claim:** Spec T26 requires identical *bytes* from `discover`,
    `export ilp`, `fidelity` and `check_with_feedback` in all three states. The
    test patches `_run_handler`, so no handler ever runs. It compares only
    parsed namespaces, which the walk never touches on non-bearing leaves.
  - Mutants that make the `discover` or `fidelity` handler withhold output when
    `resolve()` is not None survive. `resolve()` still reads the environment on
    non-bearing leaves.
  - **Reproduction:** `S/mutants.out` shows `discover-follows-mode: 59 passed`
    and `fidelity-follows-mode: 59 passed`.
  - **Fix:** Run each every-mode leaf for real on a fixture under unset,
    `GND_DISCLOSURE=internal`, `GND_DISCLOSURE=customer` and
    `--disclosure internal`, and compare the bytes.
- **T15** (`tests/test_disclosure_mode.py:246-275`)
  - **Claim:** `group` is computed so that it is always one of the `CASES`
    keys, so `assert group in CASES` is a tautology. Injected site and
    every-mode rows that no test exercises pass.
  - **Reproduction:** `S/mutants.out` shows
    `t15-undischarged-rows (T15 only): 1 passed`.
  - **Fix:** Have each discharging test record the keys it actually exercised,
    for example in a module-level set filled by the tests or by an explicit
    key-to-test map. Assert that every non-value-free key is in that set.
- **T4:** The spec names `gnd discover` as well as `gnd coverage`. The test runs
  only `coverage`. I did not reproduce any failure here; this is a gap only.

## R8 — completeness — the public `witness`, `replay` and `why_not` lost their docstrings

- **Where:** `src/gnd/witness/service.py:186-200`.
- **Claim:** The wrappers have no docstring, so `help(gnd.api.witness)` and the
  others now show nothing. This is an unset-visible change to the public API
  that is not listed in the spec. The docstrings stayed on the `*_result`
  functions. In the same hunk, the comment "Historical qualifications are
  serialized by existing callers." is now separated from the `__module__`
  assignments it describes.
- **Reproduction:** `S/r_docstrings.py` (output in `r_docstrings.out`)
  ```
  witness: acfb9ae='Produce finite witnesses; exit zero requires every requested tuple proved.'  now=None
  ```
- **Fix:** Copy the docstrings onto the wrappers. Optionally, add one sentence
  on the customer projection. Move the comment back above the `__module__`
  lines.

## R9 — hardening — conftest isolation does not reach module-scoped or session-scoped fixtures

- **Where:** `tests/conftest.py:16-19`.
- **Claim:** The autouse fixture is function-scoped. Pytest sets up broader
  fixtures first, so a module or session fixture still sees an ambient
  `GND_DISCLOSURE`. NM2-C6 promises that "an operator's GND_DISCLOSURE never
  reaches a test". T38's negative control covers only `test_rf1_cli_pins` and
  two NM2 tests.
  - The mechanism is reproduced. I found no current module fixture that runs a
    bearing leaf; the ones that run `synth` or `_cmd_measure` do not reach a
    resolving site. A concrete suite failure is UNREPRODUCED.
- **Reproduction:** `S/iso/test_r_isolation.py` with `S/iso/conftest.py`
  (which loads the repo's fixture), run as
  `GND_DISCLOSURE=customer uv run pytest -q -s --rootdir=S/iso S/iso/test_r_isolation.py`:
  ```
  module fixture saw: ('customer', 'customer') | test body sees: None
  ```
- **Fix:** Scrub the variable in a `pytest_configure` or `pytest_sessionstart`
  in conftest. Hooks are forbidden by `test_public_collection`, so the
  alternative is a session-scoped autouse fixture using `MonkeyPatch.context()`.
  Then widen T38 to a broader selection.

---

## Categories with nothing found: what was checked

1. **Leaks under customer.**
   - Every guarded API callable was checked: the seven check-family functions,
     the three delegating `EvaluationSession` methods (which go through the
     public functions, `api.py:1045-1083`), the four export-service functions,
     and the three witness-lane public functions. Their error envelopes under
     customer are projections, not exceptions (`r_errors.py`).
   - Customer is refused or redacted on every declared CLI site. Covered:
     check (snapshot and batch), verify, verbalize, diff and validate, in text
     and JSON (`r_cli_leaks.py`).
   - The `--out` paths stay closed under customer without raw: witness
     ("--out requires --raw"), export souffle and lean (`souffle_io:105`,
     `lean_io:28`), and souffle-witness.
   - `witness-view --expand` without raw keeps only ids.
   - `why-not --row` only reads the caller's row and is projected.
   - The `CheckReceipt` path holds an internal `CheckReport`; redaction is
     applied at transition build.
   - The witness-service `*_result` functions are unguarded public raw
     functions by design (D1 b). Note that `gnd.witness.service` is not in
     `SURFACES`, while `gnd.export.service` is.
2. **Unset parity.**
   - `process._result` with an empty `disclosed_names` gives the same mapping.
   - solve gets no `env` keyword unless customer, and the session passes no
     `extra_environment` unless customer.
   - No public signature change, other than the new optional
     `invoke_agent`/`run_bounded_process` keywords.
   - The `*_result` bodies differ from the acfb9ae bodies only in the `def`
     name. The exception is the docstrings (R8).
   - The goldens diff is only the root usage and help line plus tree.json.
3. **Resolution order.**
   - All subparser groups are `required`, so `_leaf` never sees None (every
     group without a leaf exits 64).
   - Repeated or trailing `--disclosure` gives 64 (T5 and T6 pass).
   - The token is reset in `finally`. Contexts are copied into asyncio tasks
     (`asyncio.run`).
   - No threads are used in any forwarding path. The only `threading` use in
     src is in `archsmoke`.
   - No `cli.main` re-entry exists in src.
   - Under internal, `--out` without `--raw` works on witness, souffle and lean.
     T24 specifies this, so it is intended.
   - No check arm refuses `--unredacted`, so internal cannot turn a valid call
     into a usage error.
4. **Forwarding.**
   - The legacy `invoke_agent` is forwarded (the injected-invoker branch is
     test-only).
   - `_invoke_command` covers v6 to v8.
   - Reviewer seats use an allowlist environment plus the forward.
   - solve uses `{**os.environ, **forward()}`.
   - The verifier and tests runner are scrubbed (T34).
   - HTTP adapters do not spawn.
   - The masking fix keeps every other value masked (T34b), apart from R3.
   - An ambient `GND_DISCLOSURE=internal` is still inherited by solve stations
     through `os.environ`. This is "as today" per spec row 13; I note it as
     intended, not as a defect.
5. **Table.** All 48 leaves were enumerated together with their options
   (`dests.py`). Only `doccheck` is misclassified (R1).
6. **Tests.** See R5, R6 and R7. T12 runs in-process (`run_main`), so it can
   fail. T11's handler counter and the T16 walk are sound.
7. **Successor rows.**
   - All nine rows use `base` 387aada.
   - The before and after algorithm and import digests are verified by
     `test_rf4_peripheral` (it passes).
   - The reasons describe the edits correctly.
   - Each row binds the exact current body, so it cannot mask a later edit of
     that same function. The pin coverage lost by the move is R2.
   - The dynamic-query successor is a syntax census only and is chained from the
     NM1 file.

## Disposition (phase author, 2026-11-01)

Each finding was reproduced in this session before disposition: the
reviewer's `r_doccheck.py`, `r_outer_ctx.py`, `r_judgments_mutant.py` and its
mutation plugin `mut/nm2_mutants.py` were rerun. Every fix has a regression
test that was observed red against the pre-fix code, by a temporary revert or
by the reviewer's mutant.

| Finding | Triage | Disposition | Regression test, observed red pre-fix |
|---|---|---|---|
| R1 | blocking | fixed: `gnd doccheck` reclassified **every-mode**; it quotes the population values a rendered document misses, like `fidelity`. Not a site, because NM-D13 keeps the fidelity family unchanged in every mode. Recorded as F10 and named for the owner. | `test_review_r1_doccheck_emits_values_in_every_mode` (red under the value-free row) |
| R2 | hardening | fixed (test): the raw bodies are pinned to the RF4 base algorithm | `test_review_r2_raw_bodies_keep_the_rf4_base_algorithm` (red when `witness_result` gains a statement) |
| R3 | hardening | fixed: `invoke_agent` gains `disclosed_names`. Only caller-named values are unmasked, and an overridden inherited name is recorded once, as supplied. | `test_review_r3_only_named_values_are_unmasked` (red under the pre-fix `frozenset(extra)`) |
| R4 | hardening | fixed: the CLI walk treats an enclosing customer context like `GND_DISCLOSURE=customer` | `test_review_r4_an_enclosing_customer_context_holds_in_process` (red under the pre-fix `mode = option or env`) |
| R5 | completeness | fixed (test): `api.judgments` under all three modes and `check_with_feedback` under internal, end to end | `test_review_r5_judgments_and_feedback_bypass_the_mode` (red under `internal-callers-resolve` and `judgments-refuses-under-customer`) |
| R6 | completeness | fixed (test): internal reaches `validate`, `transition` and `diff` (over a model without the constraint, so the diff shows values) | `test_review_r6_internal_reaches_every_api_check_function` (red under `validate-`, `transition-` and `diff-ignores-internal`). `judgments-ignores-internal` is caught by R5. |
| R7 | completeness | partly fixed: `discover` runs end to end in all three modes. A `fidelity` end-to-end run is deferred, because it needs a committed extraction case. The T15 weakness is accepted as is: T15 checks the group map, and T13 and the per-group tests carry the coverage. | `test_review_r7_discover_output_is_the_same_in_every_mode` (red under `discover-follows-mode`). `fidelity-follows-mode` still survives (open question NM2-Q2). |
| R8 | completeness | fixed: the public `witness`, `replay` and `why_not` docstrings restored, each with the mode sentence. The two successor rows were recomputed. | none needed (no behaviour) |
| R9 | hardening | fixed: `tests/conftest.py` pops `GND_DISCLOSURE` at import, so fixtures of every scope see no ambient mode. The function fixture is gone. | T38 (ambient customer subprocess run) still exits 0 |
| Arguable: `gnd.witness.service.*_result` not in `SURFACES` | n/a | not changed: they are the raw internal path of D1 (b), not `gnd.api` callables. The table covers `gnd.api` and `gnd.export.service` as plan NM2-C2 says. Recorded in the boundary. | n/a |

One reviewer is one reviewer.
