---
milestone: derivation-why-not
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: WN-close
date: 2026-10-30
source_base: fb03739
gate:
  command: "see evidence/WN-close/close-gate.txt (the cumulative WN3 gate plus the IK6 skill census)"
  exit: 0
  output: "2484 passed, 33 deselected in 368.06s (0:06:08)"
  note: >-
    Run over the closing tree, after every close-review fix. The evidence file
    holds the exact command, the interpreter, ruff, and the why-not and api
    tutorial groups. The IK6 skill census (C3-2) is part of this run, on the
    committed gnd-export edit.
slow_cadence:
  command: "uv run pytest -q; uv run python tools/check_installed_docs.py; uv run pytest -q tests/test_public_built_inventory.py tests/test_public_runtime.py"
  trigger: "explicit owner selection"
  reason: "the broad suite, the wheel-building installed-docs check and the distribution lanes are owner-selected (plan §9)"
evidence:
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN-close/close-gate.txt
    sha256: 714e35f85a0806c70c8da295c00a88ad0a517a87d5592b5f9b83be9455531144
  - path: .gnd-planning/milestones/derivation-why-not/notes/close-review-reader-1.md
    sha256: 6b5dd329778d8cf59f931c86c7bc5359bfa34afa9d31b19cc88eab51ec552445
  - path: .gnd-planning/milestones/derivation-why-not/notes/close-review-reader-2.md
    sha256: 2d1cb157bf1eca7c229b37bde073f9c4d0cde1191920ef4bac125c0033efed07
  - path: .gnd-planning/milestones/derivation-why-not/notes/close-review-reader-3.md
    sha256: 52425497733f572c30b02a3f3ab4655618542fd5dc9ead13457ac8fca66a6e88
  - path: .gnd-planning/milestones/derivation-why-not/notes/close-review-reader-4.md
    sha256: a813934315dd4ef2e7b4c5d3a7c9d1ccc104597c294f2be866ddfbbbdf385c61
  - path: src/gnd/witness/why_not.py
    sha256: 825443b065e46b525eb1be1022452d27f8931dc5307b177db66c348ea6157d22
  - path: src/gnd/witness/service.py
    sha256: efd0362f38a19d23427aa8c90ae7315a0d18a64db6001b5a7631d0b29822f82e
  - path: src/gnd/witness/view.py
    sha256: 24be1af6695ad3624dcaa852d7bec102259f0ef4d69b90b0279f645d35c41ec5
  - path: src/gnd/witness/cli.py
    sha256: 5ebd0512260a83d8b71b42b50020a2bb8295c9c3a3af2964d9d06ea852269033
  - path: src/gnd/commands/witness.py
    sha256: a21133b72aab3cf6509bfc3f28f0d48dd4349e8002963270a375f32ed10b6f5f
  - path: src/gnd/api.py
    sha256: 0585e55fee9032e5bcfd36e03727765d62c3cdf2812828f6722de53d920bd21b
  - path: src/gnd/why-not.schema.json
    sha256: bb7409464493a0eb7f4ae7f16f194607bb9aea91b58e96a0ee5769ed5eaee743
  - path: docs/reference/why-not.md
    sha256: 7fc7bb78e0c6a51552dbcd43c05be58044be04f2dde2bb026b2e349cdc8d866f
  - path: tests/test_why_not_kernel.py
    sha256: 0caaa54026428fddd671b9bc29988a7cd01abae226a903ee1295868a9d273d36
  - path: tests/test_why_not_oracle.py
    sha256: 9147f97f3e57ae2073afdb818641c27f4d522f29224adf9b9f6a39d4ec186b5f
  - path: tests/test_why_not_anonymity.py
    sha256: 33d12db551dd601a6c9efc7186909ee3663ed6b522cca065fd9a608154acff53
  - path: tests/fixtures/why_not/cases.json
    sha256: 38c53580a72c23dcca75a35d03604f12476a5f2ce5e1d3c1d5b06b09a1e24b41
---

# Derivation why-not -- milestone close

**Status: closed under delegated approval (auto=true), and accepted by the
owner on 2026-10-30 with the merge authorized (see Owner acceptance at the
end).** The owner's `/process-milestone derivation-why-not auto`
request in this session delegates the close ruling. This record states that
ruling. It is not the owner's own reading, and it neither merges PR #67 nor
publishes anything.

## What the milestone shipped

Issue #66 asked, for a rule or a claimed row that does not derive, for the
first body atom at which the conjunction becomes empty, its predicate, the
values bound by earlier atoms, and the row counts.

- **`gnd why-not`** and **`gnd.api.why_not`** ([reference](../../../docs/reference/why-not.md)).
  GND's evaluator decides first (derived, unavailable). Otherwise each clause
  is walked in declared order, with the binding count after every step, the
  first step that left none, its predicate and role map, up to five samples
  of the bindings that reached it, and descent into a derived blocker's row.
- **Output:** schema `gnd-why-not/1`, a closed redacted CLI view unless
  `--raw`, and exits 0 (blocked or derived), 2 (unsupported), 3 (invalid
  input) and 4 (unavailable or work limit).
- **The repair loop:** the `quoted_claims` example, a test that repairs a
  claim from the payload alone, and a how-to.

Records: [WN1](002-phase-WN1.md), [WN2](003-phase-WN2.md),
[WN3](004-phase-WN3.md). Commits `26e36c8` (WN1), `f456930` (WN2 corpus,
red), `b1d017d` (WN2), `ae08200` (WN3), and this close.

The issue's phrase "constants bound by earlier atoms" is delivered as samples
projected onto the blocker's bound roles (O3, approved at the plan stage).
Variables bound earlier but not read by the blocker are not shown.

## Completion predicates

| # | Predicate | Result |
|---|---|---|
| 1 | status agrees with check and the oracle on every corpus case | holds. After C2-1, the T9 corpus (200 seeds, rule and row mode, and the named discriminators) asserts `check` agreement in `compare()`, beside the T8 cases. Reader 1's differential fuzz (about 4,800 calls) found no disagreement |
| 2 | prefix counts and blocker match the oracle | holds for atom blockers; non-atom `reads`/`samples` are not compared by the oracle (residual WN1-Q1). The kernel pins them by named cases, including C4-5 |
| 3 | both budgets charged, literal counters on both sides | holds (T12, T13) |
| 4 | command, API, ceilings, closed view, exits, schema, pins, corpus first | holds. `f456930` precedes every WN2 code line. The distribution-lane pin edits were not executed (slow_cadence) |
| 5 | two-gap loop from payload fields, negative controls, witness exit 0 | holds |
| 6 | gates, reviews, sweep, PR | holds: three phase gates and this close gate, three phase reviews, four close readers, the sweep below, and [PR #67](https://github.com/vasiloglou/gnd-public/pull/67). Owner acceptance is separate |

## Close review (four local readers, WN-D8)

Reports are kept as [reader 1](notes/close-review-reader-1.md) (correctness),
[reader 2](notes/close-review-reader-2.md) (implementability),
[reader 3](notes/close-review-reader-3.md) (protocol and anonymity) and
[reader 4](notes/close-review-reader-4.md) (test design). Verdicts:
request-changes (1), approve-with-fixes (2), no blocking finding (3, 4).

| Finding | Severity | Disposition |
|---|---|---|
| C1-1 descent into an aggregate-ruled blocker raises `WhyNotInternalError` (CLI traceback) | blocking | fixed: descent stops with `descent_stopped: "aggregate"`. Kernel regression red first (`WhyNotInternalError`), green after; golden G19 in both views; schema enum and reference page updated |
| C1-2 the reference called `binding_cells` a held limit | hardening | fixed: "may store 400,000 binding cells in total" |
| C2-1 check agreement was asserted on fewer cases than claimed | completeness | fixed: `compare()` asserts `check_status` on every T9 case |
| C2-2 `asserted_not_read` is false for a derived (not semiderived) blocker with asserted rows; record 002 says "derived" | hardening | accepted as specified: the flag is semiderived-only by spec §6.3 and the reference page. Record 002's wording is corrected here (it should read "semiderived") |
| C2-3 / C3-4 no record pins the shipped `why_not.py` bytes | completeness | fixed: this record's evidence pins every shipped source file at the closing bytes. 002's digest is the WN1 bytes; WN2 (`b1d017d`) changed one docstring line, and this close adds the aggregate stop |
| C2-4 `cli.md` showed only the row form | completeness | fixed: a rule-mode row added |
| C2-5 gate evidence held a summary line only | completeness | fixed for the close gate: command, interpreter and tail. Earlier phase evidence is left as committed |
| C3-1 phase commits lack the record path; two subjects exceed 65 characters | hardening | accepted; history is not rewritten. The record paths are listed above and in the PR body, and the close commit follows the grammar |
| C3-2 the WN3 record pointed "below" to an unrecorded census run | completeness | fixed: the close gate includes both skill census files |
| C3-3 for WN1 and WN3, history cannot show the gate preceded the code | completeness | accepted and stated: those gates and implementations share commits (`26e36c8`, `ae08200`), so the order rests on the records' prose. WN3's sweep ran on the example files under `src/`. Only WN2 committed its gate first |
| C3-5 / C4-6 the anonymity scan skipped modified files and commit messages | hardening | fixed: added lines of modified files (working tree against the base) and every milestone commit message are scanned. This cannot be shown red against a real name without writing one; the planted control exercises the mechanism |
| C3-6 the forbidden-token list was chosen at a delegated gate | hardening | open for the owner (WN-Q-close-1) |
| C4-1 negated atom with a constant untested | hardening | fixed; the mutant now fails |
| C4-2 identity untested on row, negation and head paths | hardening | fixed; the mutant now fails |
| C4-3 cycle tested only against the parent | hardening | fixed (p, q, p, q); the mutant now fails |
| C4-4 `asserted_not_read` tested only on the first sample | completeness | fixed; the mutant now fails |
| C4-5 non-atom `sample_count` uncompared | hardening | fixed by a kernel case (8 bindings, 5 samples); the mutant now fails. The oracle-side comparison stays residual WN1-Q1 |

The five surviving mutants were rerun with reader 4's harness against the
four why-not test files: each now fails (1 failed each).

## Question sweep

| ID | Question | Disposition |
|---|---|---|
| WN1-Q1 | Oracle comparison of non-atom `reads`/`samples` and `head` steps | accepted residual; kernel named cases pin them |
| WN1-Q2 | The declared-order discriminator restates the evaluator's order | accepted residual (§6.6 allows it) |
| WN1-Q3 | A references case | resolved: G9 (dispatch, reference-owned legs) and the python-api block |
| WN2-Q1 | Spec §4 rule 3 lists the row file after the model; the service reads it first | accepted residual: the exits are the same |
| WN3-Q1 | Unrendered fence in `docs/reference/ilp-bridge.md` (pre-existing) | deferred to the owner: a separate fix outside this milestone |
| C2-2 | Should `asserted_not_read` also cover derived types with asserted rows? | deferred to the owner: a contract change (schema and reference) |
| O15 | The related direct-derivation request (GR-T5) | deferred to the owner: file it as its own issue if wanted |
| O16 | Reporter acceptance in their loop | deferred to the reporter, after merge |
| WN-Q-close-1 | Does the anonymity test's digest set (four names, three stripped forms) cover every name the owner protects? | open for the owner (C3-6) |

## Boundary -- what the milestone does NOT establish

- **Owner acceptance** is recorded separately below; the delegated ruling
  above does not establish it.
- **Distribution lanes, the installed-docs wheel check and the broad suite did
  not run** (owner-selected).
- **Each review is one reader**; the four close readers are four readers over
  the pre-fix close tree. The close fixes carry no review opinion.
- **Declared order, not evaluator order.** Counts describe the rule as
  written; they are not the evaluator's work.
- **The repair loop is one synthetic example**; free roles need a value from
  outside the payload.
- **A pre-existing docs defect** (`ilp-bridge`) remains.

## Merge with main

Before the merge, main gained the ilp-import-hardening milestone (PR #65).
Both milestones chained their RF6 dynamic-query successors from IL-close. The
merge keeps main's IH0-IH2 chain and adds
[evidence/WN-merge/dynamic-query-successor.json](evidence/WN-merge/dynamic-query-successor.json),
which rebases the 41 WN1 and 2 WN2 rows onto IH2 unchanged. The WN1 and WN2
successor files stay as committed history. The release notes keep both
milestones' entries. The merged tree's focused checks are in the merge commit.

## Owner acceptance

2026-10-30, by the owner, in the session that ran this close: "Accept and
merge", in answer to "Do you accept the milestone and want PR #67 merged, or
should I run the broad suite and distribution lanes on the branch first?". This
acceptance is the owner's own, distinct from the delegated close ruling above,
and covers the bytes of this record's commit and the PR head that carries it.
It authorizes merging vasiloglou/gnd-public#67; it does not run the broad
suite or distribution lanes, start a successor milestone, publish, or certify
anything. The four open owner questions in the sweep stay open.
