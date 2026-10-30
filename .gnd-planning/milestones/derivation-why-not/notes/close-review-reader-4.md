# Close review, reader 4: test design and falsifiability

Retained text of the reader's returned report (one of four local close
readers, WN-D8). Local edits: scratch paths read `<scratch>`.

**Scope.** I ran mutation tests on `src/gnd/witness/why_not.py`, `service.py`, `view.py` and `cli.py`. Each mutant was a copied package placed first on `sys.path` and run in-process through pytest, with no repository edits. Each mutant ran against `tests/test_why_not_kernel.py`, `tests/test_why_not_oracle.py`, `tests/test_public_why_not.py` and `tests/test_why_not_repair_loop.py` (147 tests, all green on baseline). I also probed the generated corpus with a census, and read the anonymity scan. While I worked, the working tree gained an uncommitted aggregate-descent fix (`descent_stopped: "aggregate"`, golden g19). I had reproduced that crash independently (`WhyNotInternalError` when a row-mode descent enters an aggregate predicate). The fix is in place, so I do not report it again.

**Verdict: no blocking findings.** 78 mutants: 64 killed, 14 survived. Of the 14, 9 are equivalent or unreachable. The other 5 survive real behaviour that the spec requires, and the anonymity scan does not cover modified files.

Probes, mutants and the harness are in `<scratch>/close-r4/`. The mutant list is `mutants.py`, the runner is `runmut.py`, the probes are `probe1.py` and `probe2.py`, and the results are `results1.txt` and `results2.txt`.

## Mutant table (all run against the 4 files above)

| Mutant | Result |
|---|---|
| sample cap 4 and 6; samples unsorted or reverse-sorted; declared body order replaced by sorting; candidate dedupe off; sample dedupe off; negation/comparison swapped | killed |
| exit bands: unavailable→0, unsupported→4, work-limit→3 | killed |
| view copies samples, unavailable binding or constants; view drops reads or work; raw/redacted label swapped | killed |
| intake: default limits, no `targets=1`, intake skipped; row fact-type mismatch accepted | killed |
| descent picks the last grounded row; cycle check off; MAX_DESCENT 9 or `>=`; proof_depth check off; descent from an ungrounded sample | killed |
| each budget charge removed (negation per binding and per fact, join probe, candidate probe, joins, cells, pre_joins); cells charged as 1; `>=` breach | killed |
| asserted flag always false or read from extensions; ground ignores constants; head-bind constant or variable checks off; atom sample_count capped; opaque check off or over all facts; closure = target only; no semiderived descent; references ignored; rule-mode `rows` > 1; seed binds computed terms; head not materialized; non-empty rule seed; internal raise removed; `steps_after_blocker` None; unavailable check off; non-atom samples empty or `$`-keyed; reads = all bound | killed |
| **negated-atom constant grounded as None** | **survived (C4-1)** |
| **`_identity_row` uses canonical JSON** | **survived (C4-2)** |
| **cycle path reset to the parent only** | **survived (C4-3)** |
| **`asserted_not_read` checks the first sample only** | **survived (C4-4)** |
| **non-atom `sample_count` capped at 5** | **survived (C4-5)** |
| `_store` dedupe off, reads not intersected, `scalar_bytes` not projected (defaults equal), `atom_blocker` uses `previous[-1]`, descent primitive, compare truthy, work-error alias, negation role-subset filter | survived, equivalent |
| prose blocker treated as derived | survived, unreachable (validation refuses it, WN1 F2) |
| opaque rows outside the closure not stripped | survived, no observable difference found |

## C4-1 — Negated atoms with a constant role are never tested (hardening, high)
**Where:** `why_not.py` `_ground`; no test or generated case has a constant inside `negate`.
**What is wrong:** Grounding a constant as `None` survives every test. On valid input that mutant raises `TypeError`, which the service maps to exit 3 `input-invalid`, where the right answer is `blocked`.
**Reproduction:** Use `s(q)`, `x(q,tag)` and `t(q) :- s(q), not x(q,"k")`, with `s=[a]` and `x=[(a,k)]`. Baseline gives a `negated` blocker with count 0; the mutant gives `TypeError: unsupported identity scalar` (`probe1.py`, case neg-const).
**Fix:** Add this case to the kernel tests, and let the generator place constants in negated atoms.

## C4-2 — Value identity is untested on the row-mode and negation paths (hardening, high)
**Where:** `_identity_row`, used by the row-derived check, `_negate` and `_head`.
**What is wrong:** Replacing identity tokens with canonical JSON survives. Only `_binding_key` dedupe is pinned. The reference says `1` and `1.0` are one value.
**Reproduction:** With `t(v) :- b(v)`, `b=[1]` and the claimed row `Number 1.0`, baseline gives `derived` and the mutant gives `blocked` (head blocker). With `x=[1.0]`, `s=[1]` and the rule `not x(v)`, the mutant raises `WhyNotInternalError` (`probe1.py`).
**Fix:** Pin `1` vs `1.0` in row mode, in negation and in head comparison, and `true` vs `1` in negation.

## C4-3 — Cycle detection is tested only against the immediate parent (hardening, high)
**Where:** `_descend`, where the cycle check uses the whole descent path.
**What is wrong:** Resetting the path to the parent's row only (`path=(key,)`) survives. With that mutant, a two-step cycle (p→q→p) is no longer reported as `cycle`; descent runs to depth 8 and stops with `depth`.
**Reproduction:** `p(v) :- b(v) | q(v)`, `q(v) :- p(v)`, `b=[]`, row `p("a")`. Baseline: the chain is p, q, p, and the third p stops with `cycle`. Mutant: 9 levels, stopping with `depth` (`probe2.py`, case cycle2).
**Fix:** Add a mutual-recursion case to T11.

## C4-4 — `asserted_not_read` is tested only when the first sample is the asserted one (completeness, high)
**Where:** `_atom_blocker`. Spec §6.3 says "some sample's ground row is asserted".
**What is wrong:** Checking only `grounded[0]` survives.
**Reproduction:** Semiderived `s`, `t(v) :- k(v), s(v)`, with `k=[a,b]` and `s` asserted `[b]`. Baseline gives `true`; the mutant gives `false` (`probe2.py`, case semi-2nd).
**Fix:** Add a case where only a non-first sample's row is asserted.

## C4-5 — The oracle comparison ignores non-atom blocker details and descent (hardening, high)
**Where:** `tests/test_why_not_oracle.py::compare`. For `negated`, `comparison` and `head` blockers it checks only kind, index and count. It never compares `sample_count`, `reads`, `samples` or `descent`.
**What is wrong:** Capping non-atom `sample_count` at 5 survives all 200 seeds. Yet my census of the generated corpus shows 10 non-atom blockers with more than 5 bindings, plus 7 descents, none of them compared. The census also found zero `head` and zero `head-bind` blockers; the only floors asserted are `valid >= 150` and `blocked >= 100`.
**Reproduction:** Mutant `nonatom_count_capped`: 147 passed. `census.py` gives `{'kind:negated': 37, 'kind:comparison': 13, 'nonatom_sc>5': 10, 'descent': 7}` and no head kinds. A direct probe with 8 negated bindings: baseline 8, mutant 5.
**Fix:** Compare `sample_count`, `reads` and identity-projected samples for every blocker kind, and compare descent recursively. Add per-kind census floors, including head blockers from a generated computed or constant head.

## C4-6 — The anonymity scan skips modified files (hardening, high)
**Where:** `tests/test_why_not_anonymity.py::_added_files` uses `--diff-filter=A`, plus untracked files only.
**What is wrong:** 47 files the milestone modified are never scanned, among them `docs/release-notes.md`, `docs/reference/cli.md` and `service.py`. Uncommitted edits to tracked files are also missed. A downstream name added to any of them passes the test.
**Reproduction:** `_added_files()` contains `docs/reference/why-not.md` but not `docs/release-notes.md`, `docs/reference/cli.md` or `src/gnd/witness/service.py`.
**Fix:** Use `--diff-filter=AM` against BASE, and add `git diff --name-only` for the working tree, or scan only the added lines of modified files.
