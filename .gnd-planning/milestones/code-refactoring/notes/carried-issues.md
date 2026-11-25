# code-refactoring: carried items and their tracking issues

Filed on 2026-11-25 at the owner's request ("file the tracking issues"),
after the close ([019](../019-milestone-close.md)). The close record and the
[question sweep](close-question-sweep.md) are digest-bound and stay as they
were; this file maps their carried rows to issues. Each item was checked on
main `1f13787b` before filing.

| Carried item | Sweep rows | Issue |
|---|---|---|
| Shim retirement (RF-D5; the release trigger has passed) | A5 | [#297](https://github.com/vasiloglou/gnd-public/issues/297) |
| Seven package-initializer import cycles (C-D1) | C63 | [#298](https://github.com/vasiloglou/gnd-public/issues/298) |
| Identical helper copies with no ruling: `_rate`, `_sorted_set`/`_canonical`, two session groups (C-D2) | families | [#299](https://github.com/vasiloglou/gnd-public/issues/299) |
| `load_pool` raises a plain `ValueError` over the byte cap (reproduced on main) | C64 | [#300](https://github.com/vasiloglou/gnd-public/issues/300) |
| `gnd.output._canonical_payload` without `allow_nan=False` (Q2) | C24 | [#301](https://github.com/vasiloglou/gnd-public/issues/301) |
| Input-boundary hardening left after RF7, media types included | B4, C20 | [#302](https://github.com/vasiloglou/gnd-public/issues/302) |
| CLI resume refusal for session versions 2, 3, 7, 8 (RF1-OQ2) | C16 | [#303](https://github.com/vasiloglou/gnd-public/issues/303) |
| Evidence digests depend on the contract's absolute path (RF1-OQ4) | C18 | [#304](https://github.com/vasiloglou/gnd-public/issues/304) |
| Remaining allowed model traversals; RF6a completeness cases | C39, C40 | [#305](https://github.com/vasiloglou/gnd-public/issues/305) |
| Test-support cleanups: RF1-OQ7, RF3-OQ3, plan-surface list, Q3 labels | C21, C23, C24, C32 | [#306](https://github.com/vasiloglou/gnd-public/issues/306) |
| Standalone PyRel positional-reference routing (RF2-OQ2) | C27 | [#307](https://github.com/vasiloglou/gnd-public/issues/307) |
| The four source-owned open questions | C66 | [#308](https://github.com/vasiloglou/gnd-public/issues/308) |

Carried items found settled on main, so no issue was filed:

| Item | Sweep row | Evidence on main |
|---|---|---|
| RF7-R5: `evolve._parse_model_text` leaking ruamel `ParserError` | C47 | it now catches `YAMLError`; four malformed inputs each raise `EvolutionError` |
| Package-wide primitive-ownership guard refusing `safefs.read_regular_file_bytes` | C52 | RF9's CI repair changed the alias to an identity import; `tests/test_artifacts.py::test_no_module_redefines_a_promoted_artifact_primitive` and `::test_consolidated_modules_do_not_reimplement_a_promoted_primitive_body` pass |
| The Souffle setuid test excluded on one machine (4700 became 0700) | C48 | the full default lane on beast-3 at `99cf3df2` had 0 failures with it included |
