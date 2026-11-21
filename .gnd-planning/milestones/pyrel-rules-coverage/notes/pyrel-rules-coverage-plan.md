# PyRel rules coverage · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers items 2–4 of [#214](https://github.com/vasiloglou/gnd-public/issues/214)
and the value constraints that stop its quantity-fixture case. Item 1 (include
roots) belongs to [include-root-routes](../../include-root-routes/README.md)
IR3. Phases are outlines; none has a spec yet. `start-milestone` turns this
outline into the full plan and the RP1 draft spec, and the plan review runs
then. Repaired after the PR 219 reviews (`.gnd-planning/reviews/pr-219-r2/`
and `pr-219-panel/`).

## Goal and completion predicates

A model built with the literature-depth features exports as a PyRel rules
program (`gnd export pyrel --rules`) for RelationalAI. Each construct is
either enforced with `require`, or left out by a recorded projection that the
output names. No construct refuses the whole program unless the owner rules it
must. Every criterion below is about the rules programs; the default (checker)
export is unchanged.

- **RP1.** External uniqueness compiles to a requirement over the joined
  roles, on both the fact-scoped and the top-level branch. The packaged
  `assertions/model.orm.yaml` exports.
- **RP2.** An anchored constraint is not enforced in the program. It is left
  out with a loss report, as `gnd export ossie` does, or carried as
  non-enforced metadata (owner decision D1). The rest of the model exports.
- **RP3.** `primitive: Number` either compiles, or refuses with a message that
  names the supported Integer or scaled-Decimal pattern (owner decision D2).
- **RP4.** Value constraints scoped to a role (`role_ref`) compile, in both the
  fact-scoped and the top-level branch (owner decision D3).
- **RP5.** The packaged flat literature model, `quantity_fixture/time.orm.yaml`,
  `assertions/model.orm.yaml` and, once IR3 has merged, the interop fixture's
  `extraction.orm.json` and temporal `checking.orm.json` export under
  `--rules lqp`. The rules route already lowers date arithmetic, so the
  temporal root is expected to export once RP2 handles its anchored constraint
  (include-root-routes D3).

## 0. Binding design rules

- **No silent loss.** Whatever the program does not enforce is listed, by
  constraint id, in a report bound to the model digest.
- **Default export unchanged.** The default (checker) export already exits 0 on
  these models; its bytes stay the same.
- **Families stay registered.** New rule shapes register in
  `gnd.constraint_families.FAMILIES` and keep the common refusal order
  (AGENTS.md, model queries and family dispatch).
- **Say what each test proves.** Offline, the `lqp` program is compile-only
  and DuckDB does not enforce `require` (`tests/test_pyrel_rules.py:292-293`,
  `:351`; `pyrel_rules.py:2455-2460`). Enforcement is shown by the DuckDB
  program's denial rows in the opt-in `pyrel_oracle` lane
  (`test_duckdb_program_agrees_with_gnd`, `tests/test_pyrel_rules.py:108`),
  and by RelationalAI itself only in a named opt-in live run.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #214 item 2 | `pyrel_rules.py:855` (fact-scoped) and `:882` (top-level; the packaged assertions model is refused here) "external uniqueness is a later phase of the rules programs". Confirmed at `0f39c392` on 2026-11-21 | RP1 |
| #214 item 3 | `pyrel_rules.py:864` and `:886` refuse family `'anchored'` | RP2 |
| #214 item 4 and its 6-line model | `pyrel_rules.py:190` "primitive 'Number' is not supported by the rules programs yet" | RP3 |
| #214 reproduction table, `quantity_fixture/time.orm.yaml` row | Its two fact-scoped `type: value` constraints with `role_ref` (lines 22-37) are refused at `:864` (fact-scoped) and would be at `:473` (top-level, "role-scoped value constraints are a later phase") once the anchored refusal is gone | RP4 |
| #214 reproduction table | The packaged-model cases are the acceptance cases | RP5 |
| Ossie export loss report (`ossie-loss-report.schema.json`) | The pattern RP2 follows if D1 picks a loss report | RP2 |

Out of scope: external frequency (`:596`, `:860`, `:882`), exact averages
(`:745`), and temporal models in the default export.

### Issue requests and the phases that discharge them

#214's "What would unblock it" lists four items. Item 1 is include-root-routes
IR3.

| Request | Phase |
|---|---|
| #214 item 2: external uniqueness in the rules programs | RP1 |
| #214 item 3: an explicit, recorded projection for anchored constraints | RP2 |
| #214 item 4: `Number`, or a documented Integer / Decimal route | RP3 |
| #214 reproduction table: every packaged literature case exports | RP4, RP5 |

## 2–3. Contract sketch and dependencies

All phases adapt `export/pyrel_rules.py` and the PyRel export reference.
RP1–RP4 are independent of one another. RP5 needs RP1–RP4, and IR3 merged for
its two include-root cases. RP5 exports packaged models only and uses no
literature-host-interfaces deliverable.

Start condition: none for RP1–RP4. This milestone and include-root-routes both
edit `pyrel_rules.py`, so they never have two writers at once: one works while
the other waits, or the second rebases on the first's merged change.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| RP1 | `assertions/model.orm.yaml` renders under `--rules lqp` and `--rules duckdb`; the default lane checks that both programs carry the (work, passage) requirement. In the `pyrel_oracle` lane, the DuckDB program's denial rows flag a population with a duplicate (work, passage) pair and not one without. A fact-scoped external uniqueness gets the same pair of tests |
| RP2 | The flat literature model renders. Every anchored constraint appears in the report by id, and none appears in the program |
| RP3 | The #214 six-line model renders, or refuses with the D2 message. The quantity fixture's coefficient-and-scale pattern renders once RP2 and RP4 have landed |
| RP4 | A role-scoped value constraint renders, in both branches; in the `pyrel_oracle` lane a population with a disallowed value is denied and one without is not |
| RP5 | Every case in the RP5 goal renders under `--rules lqp`, exit 0, apart from any construct the owner ruled must refuse, which refuses by name. Live RelationalAI enforcement is a named opt-in run |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | RP2: skip anchored constraints with a loss report, or carry them as non-enforced metadata in the program | Loss report, the shape `gnd export ossie` already has |
| D2 | RP3: support `Number`, or document Integer / scaled Decimal as the route | Support it if RelationalAI has an exact numeric type; otherwise document |
| D3 | RP4: role-scoped value constraints are not among #214's four items. Take them in, or drop the quantity fixture from RP5 and name the refusal it keeps | Take them in: without them the fixture #214 lists cannot export |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The PyRel export page and the gnd-export skill list what the
  rules programs enforce and what they report as left out.
- **Risks.** A projected program could be read as full enforcement. Control:
  the loss report is printed and its count is in the exit summary.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_pyrel_rules.py`, `test_pyrel_export.py` and
  `test_pyrel_export_boundaries.py`, plus the structure and inventory guards,
  and names its `pyrel_oracle` and live runs as opt-in.
