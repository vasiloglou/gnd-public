---
milestone: ilp-import-hardening
station: phase-IH1
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IH1
date: 2026-10-30
gate:
  command: "uv run pytest -q -o addopts='' <21 files, evidence/IH1/gate.txt>"
  exit: 0
  output: "1386 passed, 8 skipped in 334.35s (0:05:34)"
  note: >-
    IH1's tests, IH0's, the six ILP adapter suites, test_il_close,
    test_il6_walk, test_il6_skill_census, the five RF6 suites, test_gnd_arch,
    test_development_scaffold, test_rf5_commands, test_rf1_cli_pins and
    test_release_docs. tools/ilp_comparison.py exits 0, and ruff is clean on
    the five changed Python files. One full default suite also ran (below).
slow_gate:
  command: "uv run pytest -q -ra --tb=short"
  exit: 1
  output: "4 failed, 16415 passed, 794 deselected, 1 warning in 7467.50s (2:04:27)"
evidence:
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH1-spec.md
    sha256: 1d3165da4de4685447dbcd34a718963f65b2acf9590d5d5c62b1db06f73c7fbf
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH1-review.md
    sha256: 52f5e376b200d48e61d6eb7247887f8a8ae52538ed4093e0764f62abe3e534c8
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/red.txt
    sha256: 6e8d72406bc8aec4493eaef6e11524a7045a0bf214957b45941aee05abc56557
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/mutant.txt
    sha256: a2f7c9bd557163533f6aa5bf0c728414434e49ec1f53bb48468ce629ec541f36
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/t12-pre-repair.txt
    sha256: c5fd414d6acb9741b7cb292d4135a448e5d16ae607cb73821240362262364b1f
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/gate.txt
    sha256: e52b34fe8bcfe89f29c6b88e02834c8e072b0d54492880d3e48344a03c12fbf2
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/full-suite.txt
    sha256: 4e94f6df80b296919b97d86f688182662dd64e7676dd4011d34670bdad695d5c
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH1/dynamic-query-successor.json
    sha256: 3ffd3a42217459e945e5425301bfda45ff4e12fa3051b72eb4cc4c489fb67575
  - path: tests/test_ih1_counting.py
    sha256: 7352b03203e01eb85c1d6fb87891c695611bcdcae1e5b2b624b3f6f4b425fc0a
---

# Phase IH1: one counting entry for the mined import

**The owner gate.** On 2026-10-30 the owner approved IH1 spec r1 with
IH1-D3, D4 and D5 as proposed (o): "Approve as proposed". The approved bytes
are SHA-256
`1d3165da4de4685447dbcd34a718963f65b2acf9590d5d5c62b1db06f73c7fbf`, unchanged
since. The instrument was the spec's prose. IH1-D1 (a) and IH1-D2 (a) were
already ruled at the plan gate. The owner then delegated the rest of the
milestone (`process-milestone ilp-import-hardening auto`, 2026-10-30) while
IH1's full suite was running. No IH1 decision was taken under that
delegation.

## What shipped

**`gnd.export.ilp_service`**:
- `MinedInputs`, `MinedTables` and `MinedCount` are public, along with
  `load_mined_inputs`, `mined_tables` and `count_mined_rules`;
- `_Mined` and `_mined_inputs` stay as identity aliases. No test or
  evidence script imported them; the only outside caller was the tool;
- `count_mined_rules` maps every rule in `MAPPING_REFUSALS` order, then
  counts every rule. It raises only mapping refusals and `too-large`; with no
  tables passed, building them can also raise the population's own refusals.

**The import:**
- it builds the tables once, renders `amie/facts.tsv` from them with
  `ilp_amie.render_tables`, and compares the facts digest before the entry
  (IH1-D1 (o));
- it then runs the admission checks over the counts;
- it builds provenance with `ilp_amie.provenance` from the counted pairs.

**`gnd.export.ilp_amie`**:
- `render_tables`, with `render` now a wrapper over it, unchanged in bytes
  and refusals (IH1-D3 (o));
- `provenance`, which takes `fact_id` from the caller, so the module imports
  nothing from `gnd.discover`;
- `EXPORT_REFUSALS` adds `opaque` and `too-large` (IH0 finding J).

**`tools/ilp_comparison.hold()`** calls `load_mined_inputs`, `mined_tables`
and `count_mined_rules`, and names refusals with `ilp.refusal_name` (IH0
finding E).

**The two approved behaviour changes:**
- **IH1-D4 (o):** every rule's `too-large` precedes any rule's
  `covers-nothing` or `support-mismatch`. The exit stays 3.
- **IH1-D5 (o):** a population whose bytes are not the bound ones is refused
  `population-mismatch` (exit 3) before it is parsed, so it no longer exits
  5. This is IH0 finding F.

Both are documented in the AMIE section of `docs/reference/ilp-bridge.md`
and in `docs/release-notes.md`. No golden, replay or comparison byte moved,
and `ADAPTER_VERSION` is `"2"`.

**RF6:** an IH1 dynamic-query successor, chained after IH0's; syntax census
only.

## Gate output (verbatim)

From [evidence/IH1/gate.txt](evidence/IH1/gate.txt), on the final bytes:

```
1386 passed, 8 skipped in 334.35s (0:05:34)
exit: 0
$ uv run python tools/ilp_comparison.py
exit: 0
$ uv run ruff check src/gnd/export/ilp_service.py src/gnd/export/ilp_amie.py tools/ilp_comparison.py tests/test_ih1_counting.py tests/support/pyrel_application_successors.py
All checks passed!
exit: 0
```

**Red at the parent `d9b274c`:** 7 failed and 4 passed
([red.txt](evidence/IH1/red.txt)). The 4 that passed are the order pins:
- T4 is red against a mutant with the digest moved after the entry
  ([mutant.txt](evidence/IH1/mutant.txt));
- T5 checks itself against both swapped tuples, in the suite.

The review added two tests:
- **T12** passes at the parent, because its defect came from IH1. It is red
  against IH1's code before the repair
  ([t12-pre-repair.txt](evidence/IH1/t12-pre-repair.txt));
- **T13** is red at the parent: `rule 0: support-mismatch`, not
  `rule 1: too-large`.

**The full default suite** ([full-suite.txt](evidence/IH1/full-suite.txt))
ran on IH1's code before the review repairs, alongside the gate: 4 failed,
16415 passed, exit 1. One failure is the known Python-3.14-only
`test_prepared_policy_rechecks_live_hashability`, outside ILP code, whose fix
is a separate PR. The other three are timing and scaling tests; all three pass
when rerun alone on the final bytes (3 passed, exit 0, in the same file).

## Criteria

| Criterion (plan §4 IH1) | Result |
|---|---|
| `count_mined_rules` and `load_mined_inputs` public; `tools/` names no `_mined_inputs` | T1 |
| One admitting import: `relation_table` once, `pairs` once (was 2 and 2) | T2 |
| `provenance` in `ilp_amie`; no `gnd.discover` import | T6 |
| The entry returns counts for rules that do not hold | T3: 8 counts, 6 not holding |
| `facts-mismatch` precedes mapping refusals; red against a mutant | T4, mutant.txt |
| The refusal order is pinned to the docs; red against a swapped tuple | T5 and its two self-checks |
| IH-R2: goldens, replays and the comparison golden unchanged; adapter version 2 | gate suites; the comparison tool exits 0; the reviewer's differential harness showed identical bytes on all cases but D4 and D5 |
| RF6 successor; RF6, arch and layer tests | gate suites |

**A spec departure:** the spec's T7 planned to lower `MAX_JOIN_ROWS`.
Lowering it cannot be red at the parent, whose `hold()` used the
definition-time default. So T7 uses a staffing population of 1,001 staff
(1,002,001 join rows) instead.

## Review

One reviewer read the diff against `d9b274c`
([review](notes/phase-IH1-review.md)); one reviewer is one reviewer. It ran
a differential harness of old against new code over the cases its report
lists. The bytes were identical except for the D4 and D5 cases. It found no blocking defect,
and:
- **H1, fixed (T12):** `hold()` blamed a population fault on "this rule".
  It now builds the tables outside the rule handler, and the docstring names
  the tables' own refusals. The author reproduced it with the reviewer's
  `hold.py` before repairing.
- **H2, fixed:** `hold()` no longer uses `_REFUSAL`.
- **C1, fixed (T13):** an import test pins IH1-D4.
- **C2, fixed:** the release note and the AMIE section state both changes.
- **C3, fixed:** the RF6 successor's reason text.

**The repairs carry no review opinion.** The full suite ran before them.
They touch `tools/ilp_comparison.py`, a docstring, the docs, the tests and
the successor's reason; the gate above ran after them.

## Refactoring review

**Refactors executed:**
- the import's inline map, count and provenance loops moved into
  `count_mined_rules` and `ilp_amie.provenance`;
- `hold()`'s copy of them is gone (IL-close-Q1, IL4-Q3 remainder);
- `render` is split, so the export and the import share one renderer.

**Seen and deferred:**
- the mined import's learner check still compares one name, while the
  labelled import accepts a tuple. No mined entry uses a tuple, so this is
  carried as IH1-Q1;
- the import counts every rule before any admission check, so a refused set
  takes longer, though bounded per rule. This is accepted under IH1-D4 and
  not measured.

## Boundary -- what this phase does NOT establish

- **One reviewer is one reviewer,** and the repairs are unreviewed.
- **The differential comparison covered the reviewer's cases only;** it is
  not a proof of byte-identity for every input.
- **No timing was measured** for the counting order change.
- **The full suite ran on Python 3.14 on macOS,** not CI's 3.13 and 3.11.
  That run belongs to the close (IH-R3).
- **No learner, solver or model ran** (IH-R1).

## Open questions

| ID | Question | Target |
|---|---|---|
| IH1-Q1 | The mined learner check does not accept a tuple of names | the milestone close, for assignment |
| — | IH0's own-reference suspicions | IH2 |
