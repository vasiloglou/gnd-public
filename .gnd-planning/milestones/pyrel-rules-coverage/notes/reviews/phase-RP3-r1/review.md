<!-- Edited by review_tool.py sanitize: 6 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 26 supplied SHA-256 hashes match. Four findings remain.

**F1 — Integer arithmetic now crashes export (high).** [pyrel_rules.py:1384](<repo>/src/gnd/export/pyrel_rules.py:1384) calls `types.get(t)` when `t` can be a dictionary.

Reproduce by changing `arithmetic.orm.json`’s `score` primitive to `Integer`. The validated model exports under both targets at `6b9dc077`; current code raises `TypeError: cannot use 'dict' as a dict key`. Restrict the lookup to variable terms. Reproduced in memory against both versions.

**F2 — Some model constants bypass D6 (medium).** [pyrel_rules.py:334](<repo>/src/gnd/export/pyrel_rules.py:334) checks only the outer comparison operand.

In `compare-beyond.orm.json`, replace the right operand with:

```json
{"fn": "add", "args": [9007199254740993, 0]}
```

Both targets export successfully, emitting the oversized integer instead of refusing it by name. GND passes the resulting comparison for `score: 9007199254740992`.

Derived-head constants also escape: [pyrel_rules.py:1374](<repo>/src/gnd/export/pyrel_rules.py:1374) skips scalar head terms. Adding a Number `score` role to `arithmetic.orm.json`’s derived fact, updating its reading, removing `where`, and setting its head’s score to `9007199254740993` produces a valid model that both targets export. Both bypasses were reproduced in memory.

**F3 — Embedded reference populations bypass cell validation (high).** [pyrel_rules.py:2691](<repo>/src/gnd/export/pyrel_rules.py:2691) merges reference facts after the validation loop.

Reproduce by declaring `anchor-beyond.population.json` as a pinned reference population owning `holds` and `visits` in `numeric-anchor.orm.json`, then supplying an empty candidate. Both generated readers admit the two oversized Float anchors; GND returns **1**. Thus C6’s refusal does not cover reference-backed inputs. I exercised the real reference binder with in-memory file bytes and a matching SHA-256.

**F4 — Two existing refusal tests fail (medium).** The changed message at [pyrel_rules.py:1379](<repo>/src/gnd/export/pyrel_rules.py:1379) no longer matches the `fl` and `num` expectations in [test_pyrel_rules_derivations.py:221](<repo>/tests/test_pyrel_rules_derivations.py:221).

Running `test_inexact_arithmetic_is_refused_by_name` reproduces both assertion failures; its `misc` case additionally fails through F1. The claimed cumulative passing verification is therefore not true for these bytes.

**Checked and found true:** Both Number models render and compile as Python under both targets. Supplied boolean, oversized Number/Float, and deferred-anchor populations return **3** with named refusals. Candidate rosters and plan bindings enforce the bound; ±2**53 is admitted. Supplied allowed-value, range, and direct-comparison constants are refused. Both Ossie hash triples match. Numeric canonicalisation matches GND identity, including boolean separation, across 169 boundary comparisons.

**Limits:** Full PyRel execution and LQP compilation require prohibited build files and were not rerun; native agreement in C2 remains unverified. The focused read-only pytest run produced **3 passed, 3 failed**. Historical logs were hash-verified and their conclusions inspected, but their complete nested transcripts exceeded output limits. No files were changed.

VERDICT: CHANGES_REQUESTED