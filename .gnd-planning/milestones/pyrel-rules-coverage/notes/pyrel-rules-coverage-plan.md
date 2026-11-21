# PyRel rules coverage · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers items 2–4 of [#214](https://github.com/vasiloglou/gnd-public/issues/214).
Item 1 (include roots) belongs to [include-root-routes](../../include-root-routes/README.md)
IR3. Phases are outlines; none has a spec yet. `start-milestone` turns this
outline into the full plan and the RP1 draft spec, and the plan review runs then.

## Goal and completion predicates

A model built with the literature-depth features exports as a PyRel rules
program for RelationalAI. Each construct is either enforced with `require`, or
left out by a recorded projection that the output names. No construct refuses
the whole program unless the owner rules it must.

- **RP1.** External uniqueness compiles to a `require` over the joined roles.
  The packaged `assertions/model.orm.yaml` exports.
- **RP2.** An anchored constraint is not enforced in the program. It is left
  out with a loss report, as `gnd export ossie` does, or carried as
  non-enforced metadata (owner decision D1). The rest of the model exports.
- **RP3.** `primitive: Number` either compiles, or refuses with a message that
  names the supported Integer or scaled-Decimal pattern (owner decision D2).
- **RP4.** The packaged flat literature model, `quantity_fixture/time.orm.yaml`
  and, once IR3 has landed, the interop fixture's non-temporal include root
  (`extraction.orm.json`) export under `--rules lqp`. Each
  program runs on the existing PyRel test harness.

## 0. Binding design rules

- **No silent loss.** Whatever the program does not enforce is listed, by
  constraint id, in a report bound to the model digest.
- **Default export unchanged.** The default (checker) export already exits 0 on
  these models; its bytes stay the same.
- **Families stay registered.** New rule shapes register in
  `gnd.constraint_families.FAMILIES` and keep the common refusal order
  (AGENTS.md, model queries and family dispatch).

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #214 item 2 | `pyrel_rules.py:855` "external uniqueness is a later phase of the rules programs". Confirmed at `0f39c392` on 2026-11-21 | RP1 |
| #214 item 3 | `pyrel_rules.py:864` and `:886` refuse family `'anchored'` | RP2 |
| #214 item 4 and its 6-line model | `pyrel_rules.py:190` "primitive 'Number' is not supported by the rules programs yet" | RP3 |
| #214 reproduction table | The six packaged-model cases are the acceptance cases | RP4 |
| Ossie export loss report (`ossie-loss-report.schema.json`) | The pattern RP2 follows if D1 picks a loss report | RP2 |

Out of scope: external frequency (`:596`, `:860`), exact averages (`:745`) and
temporal models in PyRel export. They keep their named refusals.

## 2–3. Contract sketch and dependencies

All phases adapt `export/pyrel_rules.py` and the PyRel export reference.
RP1–RP3 are independent of one another. RP4 needs RP1–RP3, and IR3 for its
include-root case only. Start condition: none; it can run alongside
include-root-routes, but the two touch `pyrel_rules.py`, so they run one after
the other or on rebased branches, never as two writers at once.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| RP1 | `assertions/model.orm.yaml` exports under `--rules lqp`. A population with a duplicate (work, passage) pair fails the generated `require`; a population without one passes |
| RP2 | The flat literature model exports. Every anchored constraint appears in the report by id, and none appears in the program |
| RP3 | The #214 six-line model exports, or refuses with the D2 message. The quantity fixture's coefficient-and-scale pattern keeps exporting |
| RP4 | Every #214 case reaches exit 0, apart from any construct the owner ruled must refuse, which refuses by name. The temporal `checking.orm.json` case keeps its temporal-model refusal (include-root-routes D3) |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | RP2: skip anchored constraints with a loss report, or carry them as non-enforced metadata in the program | Loss report, the shape `gnd export ossie` already has |
| D2 | RP3: support `Number`, or document Integer / scaled Decimal as the route | Support it if RelationalAI has an exact numeric type; otherwise document |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The PyRel export page and the gnd-export skill list what the
  rules programs enforce and what they report as left out.
- **Risks.** A projected program could be read as full enforcement. Control:
  the loss report is printed and its count is in the exit summary.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_pyrel_rules.py`, `test_pyrel_export.py` and
  `test_pyrel_export_boundaries.py`, plus the structure and inventory guards.
  Live RelationalAI runs are opt-in and named as such.
