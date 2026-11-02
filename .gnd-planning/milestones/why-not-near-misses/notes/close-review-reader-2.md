# Close reader 2 -- the disclosure mode as a security control

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`. The reader compared against
`git archive 33c260e src` in scratch and left the repository unchanged.

**Verdict: approve.** Nothing blocking. No population value came out under
`GND_DISCLOSURE=customer` through any CLI leaf or public API function tried.

## Findings

**F1 (completeness, documentation; reproduced). The threat model understates
what a customer-mode why-not reveals.** NM-R6 and `disclosure.md` said "One
signal remains by design" (the near-miss count). The redacted view also
carries per-step `count`s, `status` and `sample_count`, which confirm whether a
guessed `--row` matches exactly. Against `spelling-gap.pop.json`:

| Guessed row | Step counts | Blocked at |
|---|---|---|
| `q-18, Ada Byrne` | [1, 1, 0] | `reviewed` |
| `q-18, Bo Lin` | [1, 0] | `authored` |
| `q-99, any person` | [0] | `quote` |

`gnd witness --targets` exit codes (0 proved, 2 otherwise) and `gnd replay` on
a crafted certificate give the same yes/no. Not new (the default view already
carried these counts, and disclosure is decided after the verdict), but the
sentence should name exact-match confirmation.

**F2 (hardening; reproduced, no leaking path found). A nested in-process call
can clear an outer `customer`.** `cli._disclosed` wraps every leaf in
`disclosure.invocation(mode)`; for value-free leaves `mode` is `None`, which
replaced an enclosing `customer`. Inside `invocation("customer")`,
`cli.main(["doctor"])` saw `resolve() is None` and `forward() == {}`. No
value-free leaf reaches a governed call today. In the same nesting the
refusal text says "when GND_DISCLOSURE=customer" though the mode came from the
context (cosmetic).

**F3 (hardening, documentation; read only). The threat model does not name
the arguments a wrapper must never forward:** `--executable` on
`export souffle-run`, `souffle-witness` and `lean-compile`; `--test-argv` and
`--adapter-policy` on `exp run` and `solve`. Forwarding them hands over code
execution. Pre-existing, not a regression.

## Attacked and found sound

- Check family under `customer` (`check` json/text/`--admission`,
  `validate`, `verbalize population`, `verify --no-extraction`, `measure`,
  `diff --populations`): no value; `--unredacted` exit 3 with empty stdout;
  `--disclosure internal` exit 3.
- Witness lane: `why-not` with and without `--row`, `witness`,
  `witness-view` on an earlier raw certificate (plain, `--expand`,
  `--expand --json`), `replay`, `replay --json`: no values; `--raw` exit 3
  everywhere.
- Soufflé lane on the dispatch fixture: `export souffle`, `souffle-run`
  (extensions null, tool path and digest blanked), `souffle-verify`,
  `souffle-witness` (certificate null).
- `export ilp --target amie` refuses the redacted role.
- Python API: every governed function, including `unredacted=1` and `"yes"`,
  refused; the export wrappers refuse `raw=True`; `api.witness`, `replay`,
  `why_not` return views; `EvaluationSession.check`, `check_with_receipt`,
  `transition` refused and the session still works after.
- A malformed variable (`Customer`, empty, trailing space): every governed API
  call raises `DisclosureRefused`.
- `SURFACES` covers all 48 CLI leaves and every public `gnd.api` name except
  the constants `EXIT_INTERNAL` and `annotations`; rows checked are live.
- With the handler patched out, every mode-bearing leaf exits 3 without
  running its handler under four malformed or loosening cases; value-free
  leaves never exit 3; the context variable is `None` after every call,
  including when the handler raises.
- `forward()` returns `customer` only when customer wins, `{}` otherwise; with
  the mode unset the spawners in `solve`, `declared_adapter`, review
  `adapters` and `exp/session` build the same environment as at 33c260e
  (read); verifier and sealed-test children use the fixed allowlist.
- Unset equals 33c260e: 24 CLI commands byte-identical in output and exit,
  elapsed time ignored.
- `tests/test_disclosure_mode.py`: 66 passed.

Not exercised: Lean export and compile (no toolchain; read only); real agents
for `exp run`, `solve` and review.

## Dispositions (author, at close)

- F1: fixed in `docs/reference/disclosure.md` "Who customer mode protects":
  status, exit code and per-step counts confirm an exact match; the near-miss
  counters add the spelling signal. The plan's NM-R6 wording ("one signal")
  is noted as superseded in the plan's close note.
- F2: fixed in `gnd.disclosure.invocation`: an enclosing `customer` holds, so
  a nested invocation never loosens it. Regression
  `test_close_r2_a_nested_value_free_invocation_keeps_an_enclosing_customer`
  fails on the old line and passes on the fix. The cosmetic refusal text is
  left as is.
- F3: fixed in the same section: the program-running arguments are named.
