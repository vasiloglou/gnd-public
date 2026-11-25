# Disposition of the r1 plan panel

Each concern in [PANEL-REVIEW.md](PANEL-REVIEW.md) was checked against the
repository at main `f7ee3720` before its fix was written. Plan r2 §11 lists
where each fix landed (rows A1 to A11).

| Group or concern | Seats | Checked how | Result | Disposition |
|---|---|---|---|---|
| `si1-marker-trust` | claude, codex, qwen, glm | `_INCLUDED` is a context variable set only by the include loader (`src/gnd/model/_unattended.py`); the flattening record is written beside the flat model by the same run (`src/gnd/model/flattening.py`), so a host that rewrites one can rewrite the other | reproduced by reading: a marker in the flat bytes, or digests over it, is host-writable | fixed (A1): no marker; exemption only in process from pin-checked includes; forged-list tests on every route |
| `si3-count-by-cause` | claude, codex, qwen, glm | [cause280.py](cause280.py) over every tracked model ([output](cause280.txt)) | 17 = 8 unit-based + 5 multi-supertype + 4 objectification; both `concepts` rows are objectification | fixed (A2): predicate 4 is 17 to 4 and 2 to 2 |
| `d2-readings-costs` | claude, codex, qwen, glm | the D2 row against §2 and C2 | the row was empty | fixed (A3) |
| `si1-route-expectations` | claude, qwen, glm | `_owns_nothing` returns false when the model has no `includes`, so the packaged root's U1 waiver is lost on re-entry too, and origins alone would not restore it; no predicate named the flat file as input | Qwen's premise that U1 belongs to the root is refuted, its conclusion holds: r1's claim that the packaged root is accepted needed the owns-nothing state as well | fixed (A4): the (route, input) table, the §1 correction, SI1-C1's injected test |
| `si1-exemption-band` | codex, qwen | `_rule_unattended`: an included confirmed element skips U8; U6 is skipped for included fact types | reproduced by reading | fixed (A5): predicate 2 rule by rule |
| `si3-disagreeing-supertypes` | claude, qwen | the 7 multi-supertype subtypes and their supertypes' references; `representation-format.md`, the Rmap's identification table | all 7 disagree; GND already identifies an inheriting subtype as its first supertype | fixed (A6): SI3 follows the first-supertype rule |
| `si2-reading-c-vacuous-predicate` | qwen | predicate 3 under reading (c) on the 9 measured entities | an empty change list would pass | fixed (A7): built fixtures that fail first |
| `include-route-list-unhomed` | qwen | §3 artifact table | no row | fixed (A8): home named; E1 lists the routes |
| `si2-si3-corpus-approval-order` | qwen | `src/gnd/export/ossie*.py` does not import `refscheme` or call `reference_identity`; `_add_references` picks the composite itself | the hazard does not arise | fixed (A9) by stating the evidence; the SI3 spec rechecks it |
| `si4-c2-owner-gated-criterion` | qwen | plan rule 0.6 against SI4-C2 | the criterion was the owner's act | fixed (A10) |
| `o4-map-budget-no-predicate` | qwen | O4 against predicate 3 | no predicate | fixed (A11) |

Six groups hold twenty concerns; with the five single-seat concerns, the
table accounts for all twenty-five. None was rejected.

## Seats that did not answer

- Gemini: `malformed`, "output contains no JSON object".
- Kimi: `nonzero`; its CLI reported a provider 429, the account's weekly
  usage limit.

Neither seat was rerun. Quorum is three; four seats answered.
