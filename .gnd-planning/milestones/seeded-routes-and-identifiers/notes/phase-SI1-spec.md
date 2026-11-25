# Phase SI1: seeded roots through flatten, extract and PyRel export (#292)

## 1. Status

**r2, draft. No ruling and no implementation.** Written on 2026-11-25 against
main `f7ee3720`; r2 follows the [plan](seeded-routes-and-identifiers-plan.md)
r2 (its §11, A1, A4, A5, A8). No review has read this spec. D1 is the owner's;
the rest is approved by delegated ruling once the plan gate is recorded.

## 2. Provenance

[#292](https://github.com/vasiloglou/gnd-public/issues/292), reproduced on
main (plan §1, "Measured before writing"); the normative section "An
unattended root that includes a reviewed model" and "Extraction flattening
record" of `src/gnd/skills/gnd-orm-core/references/representation-format.md`;
the reviewed-vocabulary-growth milestone, which made the exemption (VG3);
the include-root-routes milestone, which made the flat routes (IR2, IR3).

## 3. Obligations

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| SI1-C0 | E1's list of every route that loads an include root or flat bytes again | plan SI1-C0 | E1 |
| SI1-C1 | `gnd flatten` exits 3 with a named rule id for a model its re-entry refuses, never a traceback | #292; plan rule 2 | M1, T1 |
| SI1-C2 | plan predicate 1's (route, input) table, every cell tested | #292; plan predicate 1 | M2, M3, T2, T3, T5, T6 |
| SI1-C3 | plan predicate 2, rule by rule: the included element's exemptions (U8 when confirmed included), every rule for an owned element, and no exemption from input bytes | plan predicate 2 | T4, T5 |
| SI1-C4 | the guide and the normative text say what each route does with a seeded root | #292 "Expected"; plan §5 | M4 |
| SI1-C5 | a notes bullet under `Unreleased:` | plan §5 | M5 |
| R1 | a flat file must not let a host exempt its own elements | plan §6 | D1, T5 |
| R5 | not fitted to the packaged example | plan §6 | T3 |

## 4. Standing rules, bound to this phase

- The exemption has one home, `gnd.model._unattended`, keyed by
  `gnd.model._includes.included_rows` over the loader's origins. No second
  origin test is written.
- Its safety rests on the root's pin (normative text, last paragraph of the
  seeded-root section): GND checks the bytes against the pin. Anything that
  carries the exemption past the root must carry that binding with it.
- No regular expression over model text; documents are read as documents.

## 5. Goal

On the packaged `seeded_growth` root and on that root after its two rounds:
`gnd flatten` writes the flat model and its record (exit 0); `gnd extract`
and the three PyRel modes behave as they do for any include root; every
element the root owns is still checked by U1 to U8; and no route ends in a
traceback.

## 6. Design

### What happens today

`flatten_model` (`src/gnd/model/flattening.py`) serializes the composed model
without `includes` and re-loads those bytes to prove they reproduce it. The
re-entry is an unrooted load: it has no includes, so `included_rows` is empty
and U2 to U6 apply to the seed's elements. `extract`, `export pyrel` and
`flatten` all call `flatten_model`. `export.include_roots` and the extract
service catch the error and exit 3; `extract.flatten_service` catches only
`FlatteningError`, so `gnd flatten` lets `ModelValidationError` escape.

### E1 (before the ruling): where include roots and flat bytes are loaded

The SI1 spec's one measurement: every route that loads an include root, and
every place that loads a flat model again, in process or from a written file
(the CLI routes of the include route list, verbalization, evolve and shapes,
import, the export variants and both `--rules` modes), with what each does
today with a seeded root and what the normative text promises for it ("The
flat model is canonical JSON accepted by unrooted model-byte intake"). For
each: whether it has the root's resolved, pin-checked includes at hand. The
list is the row set of plan predicate 1's table and decides D1b's
detection.

### D1: what a seeded root's flat form does

| Reading | What it does | Cost |
|---|---|---|
| (a) **in-process exemption** (proposed) | `flatten_model` re-enters the flat bytes with the root's origins and its owns-nothing state, so the re-entry check uses the same `included_rows` and the same U1 waiver the root's validation used (`_owns_nothing` answers false for a model without `includes`, so origins alone would leave U1 on the packaged root). `flatten`, `extract` and the PyRel exports accept the seeded root. The written flat file, loaded later on its own, has no pins: it is refused, under D1b | one parameter through the re-entry; the flat file of a seeded root is not standalone-loadable, which the normative text must say |
| (b) marker in the flat file | the flat model lists the addresses of included elements, and the unattended rules read it | an unrooted file then exempts whatever it lists: a host could exempt its own claims by writing the list (R1). Binding the list to the record's digests needs the record at load time, which is (a) with more format |
| (c) refuse by name | the three routes refuse a seeded unattended root with one named rule and the guide says so | keeps the 0.4.0 workaround (copy the seed into the root) for every host that grows from a seed |

**D1b, under (a): the written flat file of a seeded unattended root, loaded
on its own.** Proposed: one named refusal in place of today's U2 to U5 list,
for example `unattended:flat-without-root`, at `$.source`, saying the file is
the flat form of a root with reviewed includes and that the root is the file
to load. The normative text's "accepted by unrooted model-byte intake" gains
that exception. The alternative is to leave today's U2 to U5 list, which
names the seed's elements and reads like the host's error.

### Modules (under (a) and D1b as proposed)

| ID | Path | Change |
|---|---|---|
| M1 | `src/gnd/extract/flatten_service.py`, `src/gnd/commands/flatten.py` | a model `flatten_model` cannot re-enter is a refusal with exit 3 and the validation issues, as the other two routes already report it |
| M2 | `src/gnd/model/flattening.py`, `src/gnd/model/__init__.py`, `src/gnd/model/_unattended.py` | the re-entry validates with the root's origins and owns-nothing state; the loader's existing `_INCLUDED` context is set from `model._provenance`, through `included_rows`; nothing is read from the flat bytes to grant it |
| M3 | `src/gnd/model/_unattended.py` | D1b's named refusal for an unrooted load of a flat model whose record says it had reviewed includes, if E1 shows the flat file carries enough to know that; otherwise D1b is the normative sentence only. Whatever it reads can only turn today's U-rule list into this one refusal, never grant an exemption, so a forged signal costs the host nothing it could gain |
| M4 | `representation-format.md` (the two sections), `unattended-growth.md` (the include route list) | what each route does with a seeded root |
| M5 | `docs/release-notes.md` | a bullet under `Unreleased:` |

## 7. Decisions

| ID | Question | Readings | Ruling |
|---|---|---|---|
| D1 | a seeded root's flat form | (a), (b), (c) above | **the owner's**; proposed: (a) |
| D1b | the written flat file loaded on its own, under (a) | a named refusal, or today's U2 to U5 list | open; proposed: a named refusal, if E1 shows it can be detected |
| D2 | the round budget for the review | one round, a second only over a repair, then stop | open; proposed: yes |

Rulings are appended below this line, each with its date, source and the
SHA-256 of the spec bytes it covers.

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `gnd flatten` on the packaged seeded root on main; then, after M1, a re-entry refusal injected at `flatten_model`'s re-entry seam | today: exit 1 and a traceback (the regression is shown first); after M1: exit 3 and the named rule id for the injected refusal |
| T2 | the packaged seeded root: `flatten`, `extract`, `export pyrel`, `--rules duckdb`, `--rules lqp` | exit 0 each under (a) |
| T3 | a second seeded root built in the test: a different reviewed include, two includes, and an owned element with spans | exit 0 on each route |
| T4 | that root with an owned element missing its spans; and a reviewed include holding a confirmed alethic element from an otherwise restricted source | the first: each route refuses it with the owned element's U4 or U5 id, naming no seed element; the second: accepted on each route (U8 exemption kept) |
| T5 | the written flat file of the packaged and of the grown seeded root, given on its own to `gnd validate`, `gnd check`, `gnd extract` and the three PyRel modes; a flat file and a root edited to list an owned element as included | the flat file: D1b's named refusal on each route; the edited files: the owned element's U-rule ids on each route, never exempted |
| T6 | the grown root after both rounds | as T2 |
| T7 | every existing include-root and flattening test | unchanged: `tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_lx1_flattening.py tests/test_vg3_unattended_includes.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py` |

### Verification selection

Focused: T1 to T7 and the structure guards of `project.md`. Impact closure:
every test file that loads an include root or a flat model. Broad: the full
default lane on beast-3 before the pull request. No opt-in lane.

### Implementability

- Every test has a command that can fail; T1 fails on main today.
- T5's edited-file case is the control for R1.
- E1 runs before the ruling; if it finds a route that loads the written flat
  file of a seeded root with no record at hand and must accept it, (a) needs
  a second look and the spec says so before any code.

## 9. Out of scope

- Unattended roots whose includes are themselves unattended (VG3 refuses
  them today).
- Temporal include roots: the existing route rules apply unchanged.

## 10. Size

About 40 production lines, 120 test lines and 20 lines of normative text and
guide. Past twice that, the phase pauses.

## 11. Approval instrument

This prose, E1's result and D1's ruling. Corpus-first is not used: no
exported format changes under (a); D1b adds one rule id, which the normative
text lists.
