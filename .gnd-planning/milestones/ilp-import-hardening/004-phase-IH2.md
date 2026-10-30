---
milestone: ilp-import-hardening
station: phase-IH2
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IH2
date: 2026-10-30
gate:
  command: "uv run pytest -q -o addopts='' <22 files, evidence/IH2/gate.txt>"
  exit: 0
  output: "1398 passed, 8 skipped in 71.72s (0:01:11)"
  note: >-
    IH1's gate list plus tests/test_ih2_ownref.py. tools/ilp_comparison.py
    exits 0, and ruff is clean on the four changed Python files. One full
    default suite also ran (below).
slow_gate:
  command: "uv run pytest -q -ra --tb=short"
  exit: 1
  output: "16425 passed, 794 deselected, 1 warning, 2 errors in 2043.21s (0:34:03)"
evidence:
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH2-spec.md
    sha256: 897c5ae6bc675e6daf40fecd1c634b1e23d68eb3b978923d744efb03b30a091b
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH2-review.md
    sha256: e89acebe30660b400a53b2a0e7ac56998580722949b732d41d1253588f17ad25
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/red.txt
    sha256: 18ec463b286580e370a34d406c6937a42665f6192dc7f1a6d9bd7f7df537284e
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/repair-red.txt
    sha256: 0cd8f75e21065be5215b8581720d7a98f5edec42ded9bc75d97128711ce33126
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/gate.txt
    sha256: 9af0c4dd9f0403ed8ad5efcb107df40559604ac83105fa99b449fbc6cee58251
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/full-suite.txt
    sha256: cef86d91269c04cd1787248d59217a8cf40a038a6859d0370fdae0033c673d0e
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/dynamic-query-successor.json
    sha256: 7ab59670e22d7b2f2c8066865506c9d81bdee787bdabababcda007c4a0267edc
  - path: tests/test_ih2_ownref.py
    sha256: ef62754be5a415afa642d807cab9dfffba2b0bad29e78cb7b5e762fdc80371df
---

# Phase IH2: own-reference subtype joins

**The gate: a delegated approval (auto=true).**
- **Authorization:** the owner's `process-milestone ilp-import-hardening auto`
  (2026-10-30), which covers spec, plan and close rulings within this
  milestone. This is the agent's ruling under that delegation, not the
  owner's reading of the spec.
- **Artifact:** spec r1, `notes/phase-IH2-spec.md`, SHA-256
  `897c5ae6bc675e6daf40fecd1c634b1e23d68eb3b978923d744efb03b30a091b`,
  unchanged since.
- **Rulings:** IH2-D1 (a): a variable spanning more than one family. IH-D1
  was already ruled (b) by the owner on 2026-10-29: refuse by a new name.
- **Instrument:** the spec's prose plus its T1 fixture, which is the plan's
  reproduction. No spec panel ran.
- **Budget and compatibility:** no paid call; no learner, solver or model
  run (IH-R1); no wire, golden or adapter-version move (IL-R7 under (b)).
- **Implementability sweep:** before the ruling, the author read
  `ilp_amie.mapped`, `family`, `Relation`, R1 and IL-close's fixtures. The
  check can sit after `check_join_types` with each atom position's family.
  IH1's T5 and `test_ilp_amie` T13 pin the tuple to the docs table.

**A delegated amendment, after the review.** The review's F1 refuted the
spec's claim that a cross-family span catches every own-reference join (see
"Refuted premise"). Under the same delegation, the check gained a second
condition:
- a variable is also refused `own-reference-join` when its types'
  references, taken together, resolve to more than one kind of value: text,
  number (Integer and Number together) or boolean. This takes in a variable
  over one such type alone, which may hold both `1` and `"1"`. The rule was
  settled by the close review: reader 4's H1 and reader 1's findings 1 to 3
  (see "Review");
- the name, its place in the tuple and the exit are unchanged, so IH-D1 (b)
  still holds;
- IH2-D1 (a) is retained, with this condition added.

The amended design is in this record and the code. The spec's bytes are not
edited.

## What shipped

**`gnd.export.ilp_amie`**:
- `MAPPING_REFUSALS` ends with `own-reference-join`, after
  `type-confused-join` (IH-R4).
- `mapped`, after the join check, refuses `rule K: own-reference-join` for
  the first variable, in atom order (body, then head), that either:
  - spans two families: "variable ?a joins the families manager and staff,
    which the count spells apart"; or
  - spans references of more than one kind of value: "variable ?a joins
    references of Integer and String in one family, which the count spells
    alike". Kinds come from `_kind`, which counts `gnd.terms.NUMERIC_PRIMITIVES`
    as one number kind, so an Integer and Number diamond is admitted.
- `reference_primitives(model)` resolves each type to its reference
  primitives. A subtype that inherits its reference takes the union of its
  supertypes', so the diamond's `director` resolves to both.
- `Relation` carries those primitives in a new defaulted field.
  `relations.json` writes its fields explicitly, so no export byte moves.

**Other surfaces:**
- **Docs:** the AMIE section's mapping table gains the row, and the family
  prose states both cases.
- **Release notes:** one bullet.
- **R1** in `tests/test_il_close.py` now asserts `rule 0: own-reference-join:`,
  the owner-recorded name change under IH-D1 (b) (o). It still exits 3.
- **RF6:** an IH2 dynamic-query successor, chained after IH1's; syntax census
  only.
- **Unchanged:** no golden, replay or fixture outside `ih2/` moved, and
  `ADAPTER_VERSION` is `"2"`.

## Gate output (verbatim)

From [evidence/IH2/gate.txt](evidence/IH2/gate.txt), on the final bytes:

```
$ uv run pytest -q -o addopts='' <the 22 files>
1398 passed, 8 skipped in 71.72s (0:01:11)
exit: 0
$ uv run python tools/ilp_comparison.py
exit: 0
$ uv run ruff check src/gnd/export/ilp_amie.py tests/test_ih2_ownref.py tests/test_il_close.py tests/support/pyrel_application_successors.py
All checks passed!
exit: 0
```

**Red at IH1's head `4389b61`:** 3 failed, 3 passed ([red.txt](evidence/IH2/red.txt)).
- T1: `rule 0: support-mismatch: amie reports Support 2, GND counts 0 of 2
  head pairs`. This is the plan's false refusal, reproduced.
- T5 reached the count.
- T3: the tuple had no new name.
- The T4 cases pass at both heads, as the spec expects.

**The review's successors** ([repair-red.txt](evidence/IH2/repair-red.txt)):
- **At IH1's head:** T6 fails with exit 70 (`internal: constraints[0] holds by
  GND's count but the checker says 'warning'`), and T8 fails with
  `support-mismatch`.
- **Against IH2's check before the repair:** T6 still fails with exit 70.
- **Against the reviewer's subject-only mutant:** T8 fails.
- **T7,** the diamond's one-primitive control, passes in all three.
- **T9 to T11** (the close review), in the same file:
  - **At IH1's head:** T9's mixed population and T11 exit 70.
  - **Against the per-type check of reader 4's H1:** T9 and T11 exit 70, and
    T10 is refused.
  - **Against the union of primitive names, before kinds:** T10 is refused.

**The full default suite** ([full-suite.txt](evidence/IH2/full-suite.txt))
ran on IH2's code before the review repairs: 16425 passed, no failure,
and 2 errors, so exit 1. Both errors are setup failures in
`tests/test_public_optional.py`: its build profile pins uv 0.10.10, and that
host has uv 0.13.6. The development host has the pinned uv, and the close's
CI runs the profile with it.

## Criteria

| Criterion (plan §4 IH2, spec) | Result |
|---|---|
| A fixture reproduces today's false `support-mismatch`, red at IH1's head | T1, red.txt |
| IH-D1 (b): refused by a new name before any count | T1, T5 (the count replaced by one that raises), T6, T8 |
| The name after `type-confused-join`, with the docs table | T3; IH1's T5; `test_ilp_amie` T13 |
| R1 refuses with exit 3, never 70; its name moves | T2 = R1 |
| No fixture golden moves; `adapter_version` 2 | T4; the gate suites; the comparison tool exits 0 |
| Release notes: one bullet | `docs/release-notes.md` |
| IH0's suspicions: own-reference exit 70; `spell` writing `1` and `"1"` alike | T6 and T1. Within one family, one reference primitive now means one primitive's raw values; this is argued, and pinned by T7 and C1a to C1e |

## Review

One reviewer read the diff against `4389b61`
([review](notes/phase-IH2-review.md)); one reviewer is one reviewer. It ran
the import over its own models and four mutants. Every finding was
reproduced by the author before repair; F1 was reproduced with the
reviewer's `diamond` model, which exits 70.

| Finding | Class | Disposition |
|---|---|---|
| F1: a diamond (`director` under `manager` and `staff`) unites an own-reference subtype with its supertype's family, so the join reaches the count and exits 70 | blocking | fixed by the amendment; T6 red at IH1's head and against the pre-repair check; T7 shows the one-primitive diamond still admitted |
| F2: no own-reference join in the object position; a subject-only mutant survived | hardening | fixed: T8, red against that mutant |
| F3: the docs and release note claimed more than the code did | completeness | fixed with F1: the table row, the family prose and the bullet name both cases |
| Close review reader 4, H1: the F1 repair refuses a variable over `director` alone, which IH1's head admitted with the checker agreeing | hardening | **overruled** by reader 1's finding 1: briefly repaired per type, then reverted. `director` may hold `1` and `"1"`, and with such a population IH1's head exits 70 (T9's mixed case). The refusal is disclosed in the docs and the release note |
| Close review reader 1, finding 1: with the per-type repair, a variable over `director` holding `1` and `"1"` exits 70 | blocking | fixed: the union again, by kind of value; T9 |
| Close review reader 1, finding 2: a type under two unrelated references, String and Integer, with no own-reference subtype, exits 70 (at `fb03739` too) | hardening | fixed by the same rule: T11. The name says own-reference, though no subtype here has its own scheme; the docs row describes the case |
| Close review reader 1, finding 3: the union of primitive names refused an Integer and Number diamond that `fb03739` admitted with the checker agreeing | hardening | fixed: kinds of value, not primitive names; T10 |
| Close review reader 1, finding 4: siblings and value-type subtypes declared `inherits_reference: false` are refused by this name too | completeness | the docs row now says "a subtype that does not inherit its supertype's reference starts" a family |
| Close review reader 4, C2 and C3: the release note called every old `support-mismatch` false, and the table row named only a subtype with its supertype | completeness | fixed: both now state the cases the code refuses |

**The repairs carry no review opinion.** The close review's repairs were
read by no one after them. The repairs touch `ilp_amie.py`, the docs, the release note, the
tests, seven fixture models and their populations, and the RF6 successor. The
gate above ran after them; the full suite ran before them.

## Refuted premise

Spec r1, Design 1 and 3: "Two related types fall in different families only
when one of them has its own reference scheme", so a cross-family check
"catches exactly the joins the count cannot meet", and "exit 70 is
unreachable through such a join". The first half is true. The conclusion is
false: a type that is a subtype of both an own-reference subtype and its
supertype unites them in one family (review F1). The amendment above
repairs the check. `family` itself is unchanged, so the export bytes do not
move.

## Refactoring review

**None executed.** The phase added one check and one resolver, and it
touched no shared structure that needs moving.

**Seen and deferred:**
- **The diamond's family spelling.** `family` still spells an own-reference
  subtype and its supertype alike when a third type unites them. The
  mapping now refuses every join that spelling could miscount. Changing the
  spelling would move the export (IL-R7) and needs IH-D1 (a)'s adapter
  version 3. Carried as IH2-Q1.
- **The resolver's cost.** `reference_primitives` walks each type's
  inheriting ancestors without sharing partial results across a cycle. This
  is linear in practice and exponential only in pathological diamond
  lattices; it was not measured.

## Boundary -- what this phase does NOT establish

- **One reviewer is one reviewer,** and the repairs are unreviewed.
- **The checker's value equality across primitives** was observed, not
  proved: Integer `1` and String `"1"` differ, and String and String agree.
  The refusal is conservative: a variable whose types' references span two
  kinds is refused even where its population holds values of one kind only
  (T9's `alone` case, admitted at IH1's head).
- **Only `bool`, `int` and `str` are exported** (`ilp.export_value`), so the
  kinds are argued complete for what the count spells. Integer and Number
  are one kind because their exported values are ints; their equality in
  the checker was observed for T10, not proved.
- **No other path** by which a family mixes reference primitives, such as
  cycles with own-reference edges, was constructed. The resolver covers the
  union in principle.
- **The full suite ran before the repairs,** on Python 3.13 on a second
  macOS host (a clean clone of `4389b61` with the working-tree
  changes laid over it). The close runs CI on both Pythons (IH-R3).
- **No learner, solver or model ran** (IH-R1).

## Open questions

| ID | Question | Target |
|---|---|---|
| IH2-Q1 | Spell a diamond's own-reference subtype apart from its supertype (IH-D1 (a), adapter version 3) instead of refusing the join | the milestone close, for assignment |
