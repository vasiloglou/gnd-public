# Include-root routes · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers [#217](https://github.com/vasiloglou/gnd-public/issues/217) and
item 1 of [#214](https://github.com/vasiloglou/gnd-public/issues/214). Items
2–4 of #214 belong to [pyrel-rules-coverage](../../pyrel-rules-coverage/README.md).
Phases are outlines; none has a spec yet. `start-milestone` turns this outline
into the full plan and the IR1 draft spec, and the plan review runs then.
Repaired after the PR 219 reviews (`.gnd-planning/reviews/pr-219-r2/` and
`pr-219-panel/`).

## Goal and completion predicates

A version-5 root with includes reaches the routes that refuse it in 0.4.0,
through one recorded composition or flattening, never a silent fallback. Every
combination that stays unsupported refuses with a message naming it.

- **IR1.** `gnd judgments check` accepts an include root, temporal or not, and
  judges the same composed model `gnd check` evaluates. Receipts and the
  report bind the root and every include by digest.
- **IR2.** Any include root, temporal or not, can be written out as a
  `*.flat.orm.json` plus its `gnd-flattening/1` record, outside `gnd extract`
  (owner decision D1). `flatten_model` already flattens the temporal interop
  root in memory (both PR 219 reviews probed it); the gap is that the only
  route that writes the pair is `gnd extract`, which refuses temporal models.
- **IR3.** `gnd export pyrel`, with and without `--rules lqp`, accepts an
  include root by exporting its flattened model. The exported program records
  the flattening record's digest and every include's digest, so an include
  changed and pinned again in the root gives a different recorded digest. An
  include changed without a new pin already refuses at load
  (`include:hash-mismatch`, `model/_includes.py:217`). Detecting a stale
  program after export is out of scope: the default program embeds its model
  text (`export/emit.py:53-55`) and reads no include again.

## 0. Binding design rules

- **Projections are recorded.** As in the literature-interop plan: each
  flattening gets a record bound to the bytes it consumed.
- **Includes stay as they are.** Standalone-valid, no nesting, confined paths.
  This milestone opens routes; it does not relax include rules.
- **Same judgement, either route.** A non-temporal root judged directly (IR1)
  and judged through its flat model must give the same verdicts. A test pins it.
- **The two export modes differ on temporal models, and stay different.** The
  default mode refuses them (`export/emit.py:35-36`). The `--rules lqp` route
  (`render_pyrel_rules`, `emit.py:60-64`) has no temporal refusal: it lowers
  `date_add` / `date_sub` (`pyrel_rules.py:357`, `:409`, `:1654-1668`). Every
  criterion below says which mode it means.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #217, "Problem" | `judgments.py:471` calls `guard_bytes(..., route="judgments")`. The command reaches it through `api.py`, which refuses first (`guard_path` at `:1157`, `guard_bytes` at `:1162`) and loads the model from bytes, without its includes. `require_non_temporal(model, "extract")` at `extract/service.py:191` and `extract/projection.py:319`. Confirmed at `0f39c392` on 2026-11-21 | IR1, IR2 |
| #217, "Request" | Either route. The reporter measured that a non-temporal root with reference populations already judges through the flat model | IR1, IR2 |
| #214, table row 5 and "What would unblock it" item 1 | `pyrel_rules.py:2415` `guard_bytes(..., route='pyrel_rules:2267')`; default export refuses `include:unsupported-route: export.pyrel` | IR3 |
| [literature-interop](../../literature-interop/README.md) LX1–LX2, closed | `gnd-flattening/1`, `model/flattening.py`, `witness/flattening.py` as shipped | IR2, IR3 |

Out of scope: temporal models in the default PyRel export (`emit.py:36`;
owner decision D3), detecting a stale exported program, and anything #214
items 2–4 ask for.

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #217: `judgments check` judges an include root directly | IR1 |
| #217: a flattening route that accepts temporal models | IR2 |
| #214 item 1: export an include root through its flattened model, or document flattening as the route | IR3 |

## 2–3. Contract sketch and dependencies

- **IR1** adapts the judgments entry in `api.py` (`:1157-1163`) and
  `judgments.py:471` to load through the include composition the checker uses
  (`model/_includes.py`), instead of refusing the route. The `gnd exp` session
  judgments keep their own refusal (`exp/session_judgments.py:84`).
- **IR2** adds the writing route for the flat model and its record, reusing
  `model/flattening.py` and the record format of the extract bundle path
  (`extract/service.py:92-112`).
- **IR3** adapts `export/pyrel_rules.py` and `export/emit.py` to flatten the
  root in process with `flatten_model` and export the flat model. That works
  for a temporal root too: probed on 2026-11-21, the flattened
  `checking.orm.json` renders under `--rules lqp` once its anchored constraint
  is removed.

IR1 is independent. IR3 needs no IR2 code. IR2 gives the user the command
that writes the record whose digest an IR3 program carries; for a temporal
root no command writes it today.
Start condition: none; `main` at `0f39c392`.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| IR1 | The #217 temporal root with two includes judges, exit 0. A non-temporal root gives identical verdicts directly and through its flat model. A changed include is refused (`include:hash-mismatch`). Nested includes keep their refusal. The refusals pinned in `tests/test_mc1_guards.py` (`test_R4_judgments`, `test_R5_judgments_api`) change to match; `test_R10_session_judgments` stays |
| IR2 | The interop fixture's temporal `checking.orm.json` (from `python -m gnd.examples.literature.interop run`) is written out as a flat model and record; the record names each element's origin and the temporal rule `publication_not_before_submission` survives. `gnd extract` on a temporal model still refuses, with a message that names the new route |
| IR3, default mode | The fixture's non-temporal include root `extraction.orm.json` (version 5, two includes; today it refuses `include:unsupported-route: export.pyrel`) exports, exit 0. The temporal `checking.orm.json` gets past the include refusal and then reaches the existing temporal-model refusal (`emit.py:36`) |
| IR3, `--rules lqp` | Both roots get past the include refusal. While pyrel-rules-coverage RP2 has not merged, each then stops at the anchored constraint `paper_names_parent_method#0` (`pyrel_rules.py:864`), the only refusal either flat model has, and not at a temporal refusal. If RP2 merged first, both export, exit 0 |
| IR3, both modes | The program records the flattening record's digest and each include's digest; changing one include and its pin in the root changes the recorded digest. The include refusals pinned for these two routes in `tests/test_mc1_guards.py` and `tests/test_mc1_review_regressions.py` change to match |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | IR2: a separate `gnd flatten` command, or extend `gnd extract` | A separate command, so extraction keeps its non-temporal contract |
| D2 | Is IR2 needed once IR1 lands, given #217 asks for one of the two | Yes, though no other phase needs its code. IR3 exports a temporal root under `--rules lqp` and records its flattening record's digest; without IR2 no command writes that record, so the user cannot reproduce the digest or read the flat model that was exported |
| D3 | Temporal models in PyRel export | Default mode: stays out, as `emit.py:36` has it. `--rules lqp`: already accepted today; no new refusal is added, and pyrel-rules-coverage RP5 expects `checking.orm.json` to export in that mode once anchored constraints are handled. The reply to #214 says both |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The representation-format includes section, the judgments
  reference and the PyRel export page each gain one sentence per new route,
  and the PyRel export page says which mode accepts temporal models.
- **Risks.** A direct judgment and a flat-model judgment could drift. Control:
  the parity test in §0.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`. Owner approval of the
  plan precedes IR1 code.
- **Verification.** Each spec names its focused lane from
  `test_public_v71_full_judgments.py`, `test_public_v71_judgment_successor_guards.py`,
  `test_extract_*.py`, `test_lx1_flattening.py`, `test_lx2_witness_flattening.py`,
  `test_pyrel_export*.py`, `test_pyrel_rules.py`, `test_mc1_model_includes.py`,
  `test_mc1_guards.py` and `test_mc1_review_regressions.py`, plus the structure
  and inventory guards.
