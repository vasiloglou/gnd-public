# Include-root routes · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers [#217](https://github.com/vasiloglou/gnd-public/issues/217) and
item 1 of [#214](https://github.com/vasiloglou/gnd-public/issues/214). Items
2–4 of #214 belong to [pyrel-rules-coverage](../../pyrel-rules-coverage/README.md).
Phases are outlines; none has a spec yet. `start-milestone` turns this outline
into the full plan and the IR1 draft spec, and the plan review runs then.

## Goal and completion predicates

A version-5 root with includes reaches the routes that refuse it in 0.4.0,
through one recorded composition or flattening, never a silent fallback. Every
combination that stays unsupported refuses with a message naming it.

- **IR1.** `gnd judgments check` accepts an include root, temporal or not, and
  judges the same composed model `gnd check` evaluates. Receipts and the
  report bind the root and every include by digest.
- **IR2.** A temporal include root can be flattened into a
  `*.flat.orm.json` plus its `gnd-flattening/1` record, by `gnd extract` or a
  separate route (owner decision D1). Extraction itself may stay non-temporal;
  the refusal then names that.
- **IR3.** `gnd export pyrel`, with and without `--rules lqp`, accepts an
  include root by exporting its flattened model, and the output names the
  flattening record's digest. A changed include makes the export stale.

## 0. Binding design rules

- **Projections are recorded.** As in the literature-interop plan: each
  flattening gets a record bound to the bytes it consumed.
- **Includes stay as they are.** Standalone-valid, no nesting, confined paths.
  This milestone opens routes; it does not relax include rules.
- **Same judgement, either route.** A non-temporal root judged directly (IR1)
  and judged through its flat model must give the same verdicts. A test pins it.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #217, "Problem" | `judgments.py:471` calls `guard_bytes(..., route="judgments")`. `require_non_temporal(model, "extract")` at `extract/service.py:191` and `extract/projection.py:319`. Confirmed at `0f39c392` on 2026-11-21 | IR1, IR2 |
| #217, "Request" | Either route. The reporter measured that a non-temporal root with reference populations already judges through the flat model | IR1, IR2 |
| #214, table row 5 and "What would unblock it" item 1 | `pyrel_rules.py:2415` `guard_bytes(..., route='pyrel_rules:2267')`; default export refuses `include:unsupported-route: export.pyrel` | IR3 |
| [literature-interop](../../literature-interop/README.md) LX1–LX2, closed | `gnd-flattening/1`, `model/flattening.py`, `witness/flattening.py` as shipped | IR2, IR3 |

Out of scope: temporal models in PyRel export (`export/emit.py:36` refuses
them) and anything #214 items 2–4 ask for.

## 2–3. Contract sketch and dependencies

- **IR1** adapts `judgments.py` to load through the include composition the
  checker uses (`model/_includes.py`), instead of refusing the route.
- **IR2** adapts `model/flattening.py` and the extract bundle path
  (`extract/service.py:92-112`). Whether `flatten_model` already handles
  temporal rules is the first thing the spec confirms.
- **IR3** adapts `export/pyrel_rules.py` and `export/emit.py` to take the flat
  model and its record. It depends on IR2 only if D1 puts the flattening behind
  a new route.

IR1 and IR3 are independent. Start condition: none; `main` at `0f39c392`.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| IR1 | The #217 temporal root with two includes judges, exit 0. A non-temporal root gives identical verdicts directly and through its flat model. A changed include is refused as stale. Nested includes keep their refusal |
| IR2 | A temporal include root flattens; the record names each element's origin and the temporal rule survives. Extraction of a temporal model still refuses, with a message that names flattening as the route |
| IR3 | The interop fixture root (`python -m gnd.examples.literature.interop run`) exports in both modes, exit 0 in default mode. Under `--rules lqp` it gets past the include refusal and stops only at a #214 item 2–4 construct, named |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | IR2: flattening through `gnd extract`, or a separate `gnd flatten` command | A separate command, so extraction keeps its non-temporal contract |
| D2 | Is IR2 needed once IR1 lands, given #217 asks for one of the two | Keep it: IR3 and PyRel users need a flat model of a temporal root too |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The representation-format includes section, the judgments
  reference and the PyRel export page each gain one sentence per new route.
- **Risks.** A direct judgment and a flat-model judgment could drift. Control:
  the parity test in §0.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`. Owner approval of the
  plan precedes IR1 code.
- **Verification.** Each spec names its focused lane from
  `test_public_v71_full_judgments.py`, `test_public_v71_judgment_successor_guards.py`,
  `test_extract_*.py`, `test_lx1_flattening.py`, `test_lx2_witness_flattening.py`,
  `test_pyrel_export*.py`, `test_pyrel_rules.py` and `test_mc1_model_includes.py`,
  plus the structure and inventory guards.
