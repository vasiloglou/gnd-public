# Close reading two: A1 obligations and open-questions sweep (HEAD 1c30525)

M = `.gnd-planning/milestones/pyrel-agent-loop/`, A1 = `M/notes/plan-amendment-a1.md`.

## Blocking

None that falsifies a shipped verdict. Repo checks matched the records: the PL17 digests equal 020:25-26, there are 125 runs, and the course replay is `llama-3.2-3b/course/run-2`.

## Hardening

H1. **The open-questions register drops rows without a disposition.** Six rows have no target after the record that last carries them (sweep below). PL19 must give each one a disposition or carry it over.

H2. **PL12-Q1 was narrowed without being recorded.** The original question (016:172, 013:136) asks for one lowering for the checker runtime (`pyrel_runtime.py`/`applications.py`). The PL16 spec rewrote it as "apps call the generated program" (`notes/phase-PL16-spec.md:35`). Only `src/gnd/examples/plan_apps/core.py`, `commands/export.py` and `export/emit.py` import `pyrel_rules`, so `ApplicationOracle` still has its own lowering. Record 017 neither closes nor carries PL12-Q1. The two term renderers `_expr`/`_operand` (016:154) were also deferred with no question ID.

H3. **The A1 work limits were substituted silently.** A1:410-412 requires a fixpoint row limit, an aggregate group limit and a plan length limit, each with a named refusal. Only `STEPS_LIMIT = 500` exists (`src/gnd/export/pyrel_rules.py:1589`). PL13b replaced the other two with a 1 MiB input cap plus a finiteness argument (`notes/phase-PL13b-spec.md:39-43`). Record 014 does not list this under its refuted premises.

H4. **The GitHub render check was never run.** A1:189-191 and the PL10 gate (A1:200) ask for `gh api markdown` on one page. No record or test does it. `tests/test_figures_render.py` covers only the `<div>`+`![` pattern. The new pages use 23 `--8<--` replay includes, which GitHub prints as literal text: the same class of defect as owner complaint 1 (A1:10).

H5. **The PL7 obligations were never mapped.** PL18-spec:20 maps only PL7-PL11's *page* obligations. The PL7 model obligations were dropped without an open question:
- `recommend_book`/`approve_expense` (A1:101-108); BookRec has no operation (git grep).
- generalising `tools/openrouter_gateway.py` (A1:133-137); the file is still there, superseded by `tools/plan_app_bot.py`.
- retiring the hand-written `rules_in_pyrel.py` files (A1:400); both are still tracked.

H6. **The A1 capability matrix (A1:273-293) was narrowed silently.** The matrix obligation was claimed discharged (PL16-spec:33). In the shipped models:
- Course has no ring, cardinality, value range or uniqueness by room/timeslot.
- Clinic has no exclusive-or, inclusive-or, equality, dose range or reference catalogue.
- No example uses v4 reference populations. PL16-spec D3 dropped them because of PL15-Q1.

Record 017 lists none of this under its refuted premises.

H7. **"Recording order" was redefined after the protocol was declared.** A1:153 says recording order. 020:97 redefines it as `results.json` order, which is (model, example, run) because the lanes ran in parallel. Two discarded PL17 launches (86 + 49 runs) are not in `results.json`, which goes against A1:152 "every run is listed". They are disclosed in `recordings/README.md:47-53`, and their evidence for the skill and evolve recordings lives only in the session scratchpad (021:195, 019:39).

H8. **Record 021's evidence digests describe pre-feedback bytes.** For example, `course-planner.md` is now `49c345…`, not `eca70a…` (021:27), and the `replays.json` digest has changed too. The `skill-sessions-evolve/manifest.json` is not listed. Fresh-wheel acceptance ran before the review fixes (021:22).

## Completeness

C1. **A1-D5** (keep or retire the old chapters, A1:228) and **A1-D4** were never explicitly ruled. Record 012 rules only D1, D2, D3 and PL12-Q2, and the D5 work is deferred as PL18-Q1.

C2. **The milestone `M/README.md` is stale.** It stops at the "Resume status, 2026-10-14" section (README:27-43) and mentions neither A1 nor PL12-PL18.

C3. **The A1 Quickstart "one prompt" (A1:49) was withdrawn under auto=true** (PL18-spec A3). This changes an owner-adopted amendment by delegated ruling and should be put to the owner at close.

## (1) A1 deliverables (A1:417-430, 012:26-33)

| Item | Status | Evidence |
|---|---|---|
| PL12 requirement object, denial lowering, single-source test | DISCHARGED | 011:29-49; test_pyrel_rules.py:259 |
| PL12 `--explain` plus execution test | DISCHARGED WITH RESIDUAL: replaced by `--rules lqp|duckdb` and `app.py rules` (PL18-spec D5); `rules_in_pyrel.py` not retired | H5 |
| PL12b logic-reasoner lane | NOT DISCHARGED (owner accepted compile-only, 012:18) | 021:170 |
| PL13a L1 families | DISCHARGED WITH RESIDUAL: external uniqueness and frequency, and multi-role exclusive-or, refused | 013:52-53 |
| PL13b L2 derivations | DISCHARGED WITH RESIDUAL: work limits substituted (H3); refusing negation through a cycle is left to the validator | 014; PL13b-spec:27 |
| PL14 L3 calendar, L4 references, tamper control | DISCHARGED | 015:56-60, 72-76 |
| PL15 L5 plans, agreement | DISCHARGED WITH RESIDUAL: `--post` (frame) refused | 016:63-64 |
| PL16 five models, apps, both runtimes | DISCHARGED WITH RESIDUAL: models hand-written "as the skill would" (PL16-spec:114); matrix narrowed (H6) | 017:63-69 |
| PL17 A1 protocol recordings | DISCHARGED WITH RESIDUAL (H7) | 020:67-82 |
| PL18 Course and Clinic tutorials, three How-to pages, Explanation | DISCHARGED | docs/tutorials, docs/how-to, docs/explanation |
| PL18 replays, re-render byte test, reduced motion, transcript | DISCHARGED (no Codex `--json` input) | tests/test_replays.py:19-60 |
| A1 page gates: no python fence, strict build | DISCHARGED | 0 python fences; 021:17 |
| GitHub render check | NOT DISCHARGED | H4 |
| IA move: per-skill How-to pages, ch7/ch4 to Reference | NOT DISCHARGED (PL18-Q1) | 021:119-126 |
| PL19 close | in progress | — |

## (2) Open-questions sweep

| Row | Status |
|---|---|
| PL12-Q1 | partly closed for the apps; checker-runtime residual **orphaned** (H2) |
| PL12-Q2 | closed by owner ruling 012:18 (compile-only); dropped from register after 016:173; page states it (021:170) |
| PL13a-Q1 | closed, 014:63-66; test_pyrel_rules_derivations.py:181 |
| PL13a-Q2 | **orphaned**: last at 014:171, absent from 015/017:142 |
| PL13b-Q1 | **orphaned**: targeted "PL16 if needed" (015:161); 017 is silent; test docstring still calls it open (test_pyrel_rules_derivations.py:143) |
| PL13b-Q2 | carried: checker, 017:142 |
| PL13b-Q3 | parked "after PL19" (015:162); dropped after 015; **no carrier** |
| PL14-Q1 | carried: checker, 017:142 |
| PL15-Q1 | carried: checker, 017:142 |
| PL15-Q2 | closed for the apps (PL16-spec:93) but not recorded in 017; GND side text-only (PL16 review:121) |
| PL15-Q3 | **orphaned**: "after PL19" (016:176), dropped in 017 |
| PL16-Q1 | carried "after PL19"; PL18-Q2 joins it (021:127) |
| PL16-Q2, PL17-Q1 | parked "after PL19", no carrier |
| PL17-Q2 | **orphaned**: owner "if the docs need it"; PL18 shipped the docs without a ruling |
| PL18-Q1 | parked "after PL19" |
| PL18-Q2 | with PL16-Q1 |
| PL18-Q3, Q5, Q6 | "outside this milestone", no issue filed |
| PL18-Q4 | closed by 6dcc4d9 (021:245-248; A1:10 now prose); 021:129 still says target PL19; worktree part environmental |

## (3) Rulings and refuted premises not honoured

- **A1-D1 "real operation plans"** is honoured for the five apps, not for BookRec/Expense, its literal subject (H5).
- **012:36 "every run reported"**: two discarded PL17 launches and the first skill and evolve launches are reported only in prose (H7).
- **The PL16 spec premise "PL17 recordings show the skill doing it live"** (PL16-spec:114-115) is false. PL17 ran tool-less bots, and the skill was recorded in PL18, for Course only. Neither record lists it under refuted premises.
