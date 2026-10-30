# Close review, reader 2: implementability and completion predicates

Retained text of the reader's returned report (one of four local close
readers, WN-D8). Local edits: scratch paths read `<scratch>`.

**Scope.** I read the whole plan r3, the README, `001-plan-gate.md`, records 002–004, and the WN2/WN3 specs and reviews where they bear on criteria. I read the kernel, service, view, CLI and API diff and the repair-loop test.
- **Digests:** I checked every frontmatter SHA-256 in 002–004 against the working tree and HEAD (35 paths), and the approved plan and WN1 spec digests at `f2f83de`.
- **Tests:** `test_public_why_not`, `test_why_not_repair_loop` and `test_why_not_anonymity` gave 81 passed. Kernel, oracle, rf6 and rf1-layering gave 111 passed.
- **Host check:** I ran the CLI as a host would on `src/gnd/examples/quoted_claims`.
- **Probes:** two, under `<scratch>/close-r2/`.
- **Not done:** I wrote nothing in the repository. I did not run the v71 corpus, the distribution lanes or a docs build.

**Verdict: approve-with-fixes.** None of the findings blocks the close. The issue's ask is delivered: `--raw` in row mode on the example gives `steps` `[quote:1, authored:0]`, blocker `(atom, 1, authored)` with its predicate and role map, and samples `{"work":"Field Notes","person":"Ada Byrne"}`. Rule mode gives per-clause counts. One narrowing was approved at the plan stage (O3): "constants bound by earlier atoms" is delivered only as samples projected onto the blocker's bound roles. Earlier-bound variables that are not in the blocker (such as `$q`) are never shown.

| ID | Status | Evidence |
|---|---|---|
| P1 status agrees with check and oracle | **partial** (evidence) | The committed check comparison covers only the about 16 cases in `AGREEMENT` and `_more_agreement`, not the T9 corpus or T2–T7 (C2-1). My probe found 0 mismatches over 400 generated cases. |
| P2 prefix counts and blocker match the oracle | discharged, with residuals | `test_why_not_oracle.py::compare`. Non-atom `reads`/`samples` are not compared (WN1-Q1, Q2). |
| P3 two budgets with literal counters | discharged | T12 (limit+1), T13 (a)–(e). |
| P4 command, API, schema, view, exits, pins, corpus first | discharged | `f456930` changes no code (spec, schema, corpus and tests only). `corpus-red.txt` reads 43 failed, 1 passed. The distribution-lane pin edits were not executed (slow_cadence). |
| P5 two-gap loop | discharged | `test_two_gap_repair_loop` and its negative controls pass. |
| P6 gates, reviews, sweep, PR | **not yet** | The close is pending. Phase gates and reviews are recorded. |
| WN1-C1 status first | partial (evidence) | The code is correct (closure, opaque scan, strip, exact pre-evaluation). The test claim is overstated (C2-1). |
| WN1-C2 prefix counts and blocker | discharged | T2–T7, both head-bind sub-branches. |
| WN1-C3 independent oracle | partial | Atom blockers only; recorded residual. |
| WN1-C4 descent | discharged | T10, T11. The string-rule stop cannot be built (F2, a refuted premise). |
| WN1-C5 budgets | discharged | T12, T13. |
| WN1-C6 branch walk | discharged | T1(c) and T11 case 4 cannot be built (F2, F3). |
| WN1-C7 layering and isolation | discharged, premise refuted | 41 + 2 dynamic RF6 rows via authenticated successors; T15b. |
| WN2-C1 command and API, hostile inputs | discharged | G10–G13, T3 projection. WN-D14 order checked in code: row validation runs before `rule-opaque`. |
| WN2-C2 schema, closed view, leak test | discharged | T2, T4, T8. |
| WN2-C3 pins | discharged statically | `api.__all__` literals, `EXPECTED_PARSERS`, rf1 goldens, rf5 case, `VENDORED_SCHEMAS`, runtime tuple. The last two were not run. |
| WN2-C4 docs | discharged, one defect | `cli.md` row (C2-4). |
| WN2-C5 check and witness unchanged | discharged (indirect) | The witness and check-contract files pass. |
| WN2-C6 counted bounds | discharged | T8. |
| WN3-C1 example | discharged | The installed-docs check itself was not run. |
| WN3-C2 loop | discharged | The bound and extracted roles are asserted disjoint; both controls present. |
| WN3-C3 how-to | discharged per the record | I did not build the docs. |
| WN3-C4 skill route | discharged | One route sentence in `gnd-export`; discovery links are symlinks. |
| Rulings WN-D1–D14 and spec D6 | honored | D3 depth 8 and cycle key; D5 exit map `_WHY_NOT_EXITS`; D6 `WhyNotLimits`; D9 `[:5]`; D11 single target and mismatch give exit 3; D12 schema path; D13 tuple; D14 order. |

**Digests:** every frontmatter SHA-256 matches HEAD, except `src/gnd/witness/why_not.py` in 002 (C2-3).

## C2-1: "check agreement over every T1–T7, T9, T10 and T14 case" is not what the tests assert (completeness, high)
- **Where:** `tests/test_why_not_kernel.py:176-245, 621-645`, `tests/test_why_not_oracle.py::compare` and `test_generated_corpus_agrees_with_the_oracle`. The claim appears in record 002 (WN1-C1 row) and in WN1 spec §8 T8.
- **What is wrong:** `check_status` is only called for `AGREEMENT`, `_more_agreement` and the semiderived case. The T9 named discriminators, the 200-seed corpus and the T2–T7 cases are compared with the oracle only. P1 asks for check agreement "on every corpus case". The 1,894-case probe was the reviewer's and is not committed.
- **Reproduction:** `probe_t9_check.py` in the scratch directory runs `check_status` over the generated corpus (rule and row mode) and prints `cases 400 no-verdict 0 mismatch 0`. The code is right; the evidence is narrower than claimed.
- **Fix:** assert `check_status` inside `compare()`, or in the generated-corpus loop. Otherwise reword record 002 and the close.

## C2-2: `asserted_not_read` is false for a `derived` blocker whose row is asserted, and record 002 says otherwise (hardening, medium)
- **Where:** `why_not.py` `_atom_blocker` (`if derivation == "semiderived" and grounded`). Record 002 says "`asserted_not_read` for a derived predicate with asserted rows".
- **What is wrong:** `_base_relations` drops the asserted rows of every structured-rule type, not only semiderived ones. So a host that asserted `p(z)` with `p` derived is told the step is blocked at `p` with `asserted_not_read: false`. The spec scopes the flag to semiderived types, so the code matches the spec. The record overstates it, and the host gets a misleading signal.
- **Reproduction:** `probe_derived_asserted.py` prints `semiderived blocked p ... asserted_not_read= True` and `derived blocked p ... asserted_not_read= False`.
- **Fix:** either set the flag for any structured-rule predicate and update the schema, reference doc and tests, or correct record 002's sentence and say in `why-not.md` that it covers semiderived types only.

## C2-3: No record pins the shipped bytes of `why_not.py` (completeness, high)
- **Where:** record 002 pins `src/gnd/witness/why_not.py` at `5f9b6a07…2f13`, which is the bytes at `26e36c8`. WN2 changed its docstring; HEAD is `cf406b40…`. Record 003 does not list `why_not.py`, `api.py` or `commands/witness.py`.
- **Reproduction:** `shasum -a 256 src/gnd/witness/why_not.py` does not match 002. `git show 26e36c8:src/gnd/witness/why_not.py | shasum -a 256` gives `5f9b6a07…`.
- **Fix:** the close record pins the HEAD digests of every shipped src file, and notes that 002 describes WN1 bytes.

## C2-4: `cli.md` shows `--row` as required and omits rule mode (completeness, medium)
- **Where:** `docs/reference/cli.md:88`. The row reads `gnd why-not MODEL POPULATION --fact-type ID --row REQUEST` and calls it "for one claimed row". The parser (`witness/cli.py`) and `why-not.md` make `--row` optional.
- **Fix:** write `[--row REQUEST]` and say "the rule, or one claimed row".

## C2-5: The gate evidence files hold only a summary line (completeness, low)
- **Where:** `evidence/WN{1,2,3}/final-gate.txt`.
- **What is wrong:** none of the files records the command or the pytest header. The WN3 gate is a superset of WN2's (it includes the v71 corpus), yet records 2465 passed in 337 s against WN2's 2379 in 952 s. That cannot be checked from the bytes; machine load may explain it.
- **Fix:** store the command, interpreter and full tail in the close gate evidence, or rerun the focused gate over the final HEAD at close.
