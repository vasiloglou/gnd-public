# Round 2 — Reader 1: semantics and admission safety

**Digests:** both match.
- plan r2 = `e0668e30…0ce3bb9`
- IL1 spec r2 = `4a06f583…cff5af8`

**Verdict: approve-with-fixes.** All four of my round-1 blockers are resolved. r2 introduces four non-blocking defects, listed below.

**Scope.**
- **Read:** the r1 and r2 diffs, the disposition and my round-1 note.
- **Checked against source:** `src/gnd/export/ilp_rewrite.py`, `ilp_popper.py` (`_TOKEN`, `_unquote`) and `ilp.py` (`Column`, neutral `types`); `src/gnd/model_index.py:264-274`; `src/gnd/model/_validation.py:981-991,1785-1811`; `src/gnd/model_queries.py:21-30`.
- **Probes:** read-only `uv run` scripts under `<scratchpad>/review2/reader-1/`. No repository file was touched.

## Round-1 blockers

| Finding | Status | Evidence |
|---|---|---|
| R1-F1 (IL4 support over head pairs) | **resolved** | **Definitions:** plan r2:312-322 fixes the numerator \|{(x,y): ∃z body ∧ head}\|, the denominator \|{(x,y): ∃z body}\|, `confidence.value` = numerator / denominator with formula `std-confidence-head-pairs`, the miner count compared with the numerator (`support-mismatch`), PCA kept verbatim and not compared, "only counts are compared, weaker than IK5", and zero body pairs refused as `covers-nothing`. **Oracle:** IL4-C3 checks numerator, denominator and confidence against a brute-force oracle over distinct head pairs. **Admission:** D11 admits a rule only when numerator = denominator (plan:324-328). That is exactly ∀z(body→head) per pair, which is GND's own guarded atom-consequent semantics. So the admission bar and the re-check now agree. The carried-limitations row (plan:499) records "counts only". |
| R1-F2 (type-confused join) | **resolved** (design); see R1-2-F1 to F3 for gaps in how it is specified | **Plan:** plan:216-229 places check D12 in the shared rewriter for every target, `neutral` included. Completion item 1 (plan:56-59) and IL1-C2 (plan:386-389). **Spec:** spec:170-197 makes it check 9b. A variable's join sites are mapped through the neutral `predicates[].types` and `types[].object_type`; the clause is compatible iff the closures of each pair intersect; the closure is `{t} \| ModelIndex.supertype_closure(t)`. Tested by T5/T5b (spec:318-319). **Closure equivalence verified:** `supertype_closure` (`model_index.py:264-274`) walks the same `subtype_of` field as `_supertype_parents` (`model_queries.py:21-30`), and it excludes `t` itself. Adding `t` gives exactly `_ancestor_closure` (`_validation.py:981-991`). The validator's predicate is the same non-empty intersection (`_validation.py:1798-1801`). **Probe:** the clause `wrong(A):- f_order_amount(A,B,C), f_order_by(A,C,D), f_customer_blocked(A,D).` (C is both an amount and an order) rewrites to `guarded` today. So the gap is real at HEAD, and 9b as described would refuse it. |
| R1-F3 (IL3 unthresholded features) | **resolved** | Plan:72-73 and 267-270 export only thresholded features ("Unthresholded features are not exported"). The schema declares each column's predicate, role, operator and threshold (plan:273-274). A thresholded feature becomes `wrong(X):- f(X,_,A), gt_t(A,t)`. My round-1 probe showed that rewrites to a `guarded` comparison. IL3-C2 (plan:432-433) now holds for every exported feature kind. |
| R1-F11 (T4 beyond-Unicode octal) | **resolved** | T4 accepts `'\4177777\'` (U+10FFFF) (spec:316). T4b refuses `'\4200000\'` (0x110000) and `'\154000\'` (0xD800) (spec:317). The plan carries the same boundaries (plan:396-397). `_unquote` reuses the hex scalar check (spec:205-208; `ilp_popper.py:255`). A token-boundary case is added. With r2's tokenizer alternative simulated, `'\4177777\'` and `'a\1\'` both lex as intended. |

## Self-inflicted findings (r2-introduced only)

- **R1-2-F1** (hardening, medium): check 9b, as written, would falsely refuse valid clauses that contain anonymous variables.
  - **Claim:** spec:174-183 says "For each variable other than X: collect its join sites". The parser returns every `_` occurrence as the same term, `{'var': '_'}`. The rewriter treats each `_` as fresh (`ilp_rewrite.py:55-61`; it emits `$anon1`, `$anon2`). The existing check-5 map (`ilp_rewrite.py:128-133`) already groups `_` under one key, so an implementation that follows that precedent groups unrelated `_` sites.
  - **Effect:** a clause with `_` at two different object types is admitted today but would be refused `type-confused-join`. That changes shipped behaviour beyond D12's scope. No IK5 corpus clause uses `_`, so the "goldens byte-identical" check would not catch it.
  - **Reproduce:** `wrong(A):- f_order_by(A,B,_), f_order_amount(A,_,C), f_order_amount(A,B,C), gt_t_amount(C,100).` over `tests/fixtures/induced_knowledge/ik5-corpus/expected-export/neutral/neutral.json` rewrites to `guarded` at HEAD. Its `_` sites are `t_customer` and `t_order`.
  - **Repair:** state in 9b that `_` is excluded, since each occurrence is its own variable. Add a T5b case with `_` at two incompatible types that stays exit 0.

- **R1-2-F2** (hardening, low): the carve-out for comparison operands rests on a false premise.
  - **Claim:** spec:187 says "Comparison operands are already typed by check 5 and are not re-checked." Check 5 (`ilp_rewrite.py:139-144`) only requires every type involved to have an `integer` primitive. It does not check object-type compatibility between the comparison predicate's declared type (`gt_t_quantity`) and the variable's role type (`t_amount`).
  - **Effect:** a learner's mistyped threshold is admitted silently. That is the same class of confusion D12 is meant to close, for any model with two integer value types.
  - **Repair:** treat the comparison predicate's declared type as one more join site in 9b. Otherwise, correct the sentence and record the gap as accepted.

- **R1-2-F3** (completeness, low): IL4 relies on a type check that it cannot reach.
  - **Claim:** plan:306-310 says IL4's mapping is "not its `wrong/1` rewriting", yet "the shared type check and validation apply". The spec places 9b inside `rewrite()`, which is the `wrong/1` path (spec:172-173), so IL4 never passes through it.
  - **Mitigation:** IL4's typed-prefix export (plan:301-302) narrows the risk.
  - **Repair:** specify 9b as a separate function over (atoms, columns, closure) that both the `wrong/1` rewriter and IL4's Horn-rule mapping call. Give IL4 one test of its own.

- **R1-2-F4** (hardening, low): T4b's octal-specific message for the 8-digit case cannot be produced by §6's tokenizer.
  - **Claim:** r2 newly requires T4b's `'\12345670\'` to refuse "with the octal-specific message" (spec:317; r1 asked only for a generic `unparsable`). With the specified alternative `\\[0-7]{1,7}\\` placed before `\\.` (spec:200-203), eight digits fall through to `\\.`. That catch-all consumes the closing `\'`, so the token never reaches `_unquote`.
  - **Effect:** alone on a line, the tokenizer fails with a generic error. With a later quote on the same line, the token swallows `'\12345670\'),g(A,B,'` and then fails elsewhere.
  - **Reproduce:** `<scratchpad>/review2/reader-1/tok.py` patches `_TOKEN` with r2's alternative.
  - **Repair:** either lex `\\[0-7]+\\` and enforce the digit bound and the message in `_unquote`, or let T4b accept the generic `unparsable` (line and column) for the 8-digit case.
