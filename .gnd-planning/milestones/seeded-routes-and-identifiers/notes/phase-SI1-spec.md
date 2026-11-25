# Phase SI1: seeded roots through flatten, extract and PyRel export (#292)

## 1. Status

**r1, draft. No ruling and no implementation.** Written on 2026-11-25 against
main `f7ee3720` with the [plan](seeded-routes-and-identifiers-plan.md) r1,
which has no ruling either. No review has read this spec. D1 is the owner's;
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
| SI1-C1 | `gnd flatten` exits 3 with a named rule id for every model it cannot flatten, never a traceback | #292; plan rule 2 | M1, T1 |
| SI1-C2 | D1's outcome for `flatten`, `extract`, `export pyrel` and both `--rules` modes, on the packaged and on the grown `seeded_growth` root | #292; plan predicate 1 | M2, M3, T2, T3 |
| SI1-C3 | an element the root owns keeps every unattended rule on those routes | plan predicate 2 | T4 |
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

### E1 (before the ruling): where flat bytes are loaded again

The SI1 spec's one measurement: every place that loads a flat model, in
process or from a written file, and what the normative text promises for it
("The flat model is canonical JSON accepted by unrooted model-byte intake").
For each: whether it has the root's pins at hand. The result decides D1's
sub-question D1b.

### D1: what a seeded root's flat form does

| Reading | What it does | Cost |
|---|---|---|
| (a) **in-process exemption** (proposed) | `flatten_model` re-enters the flat bytes with the root's origins, so the re-entry check uses the same `included_rows` the root's validation used. `flatten`, `extract` and the PyRel exports accept the seeded root. The written flat file, loaded later on its own, has no pins: it is refused, under D1b | one parameter through the re-entry; the flat file of a seeded root is not standalone-loadable, which the normative text must say |
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
| M2 | `src/gnd/model/flattening.py`, `src/gnd/model/__init__.py` | the re-entry validates with the root's origins; the loader's existing `_INCLUDED` context is set from `model._provenance`, through `included_rows` |
| M3 | `src/gnd/model/_unattended.py` | D1b's named refusal for an unrooted load of a flat model whose record says it had reviewed includes, if E1 shows the flat file carries enough to know that; otherwise D1b is the normative sentence only |
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
| T1 | `gnd flatten` on the packaged seeded root on main | today: exit 1 and a traceback (the regression is shown first); after M1: never a traceback for any model that fails re-entry |
| T2 | the packaged seeded root: `flatten`, `extract`, `export pyrel`, `--rules duckdb`, `--rules lqp` | exit 0 each under (a) |
| T3 | a second seeded root built in the test: a different reviewed include, two includes, and an owned element with spans | exit 0 on each route |
| T4 | that root with an owned element missing its spans | each route refuses it with the owned element's U4 or U5 id, and names no seed element |
| T5 | the written flat file of the packaged seeded root, loaded on its own with `gnd validate` and `gnd check`; and a flat file edited to claim the exemption for an owned element | D1b's result; the edited file is never exempted |
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
