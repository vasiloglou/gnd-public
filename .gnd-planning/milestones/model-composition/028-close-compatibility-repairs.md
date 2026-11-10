---
milestone: model-composition
station: "Final compatibility instrument follow-ups"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: close-compatibility-repairs
date: 2026-11-10
gates:
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q --tb=short'
    exit: 1
    result: 'REJECTED8e5ff181:14 failed,18787 passed,801 deselected,1warning in2536.74s'
  - command: 'focused added-failure selection before repair'
    exit: 1
    result: '8 failed,7 passed in1.07s; same eight added identities'
  - command: 'uv run pytest -q tests/test_measure_offline.py tests/test_model_v2.py tests/test_public_api.py tests/test_rf1_pin_harness.py tests/test_rf9_ci_repairs.py tests/test_rf1_cli_pins.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py --tb=short'
    exit: 0
    result: '418 passed in37.61s'
  - command: 'actual guard liveness probes: API exports, source order, inventory membership'
    exit: 0
    result: 'three clean controls pass; six dirty controls reject'
  - command: '.venv/bin/zensical build --strict'
    exit: 0
  - command: '.venv/bin/python tools/check_docs.py site'
    exit: 0
  - command: 'uv run python scripts/components_index.py changed --base 8e5ff181 --strict'
    exit: 0
  - command: 'uv run ruff check src tests --output-format json'
    exit: 1
    result: 'same13 baseline findings, only previously declared five-line checkpoint offset'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/final-repairs/manifest.json
    sha256: c9233f75f47d02b09995d7d185fa13bb50a154a04e172fed31634a297b7130b8
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: ba47d6b0669d2e1150f590531c7fa8cd04b0ba92cf5965a898f1c2084dbf96c5
---

# Claim

The complete8e5ff181 default comparison is rejected, not accepted as a new baseline. Eight added failures reproduce independently and are repaired by one offline-skill prose correction and three exact compatibility-instrument updates. All418 selected affected checks pass afterward. No runtime Python, schema, model, population, CLI grammar, report or digest algorithm changes. The actual final full comparison still requires a new complete run.

## Authority, reproduction and scope

Delegated approval (auto=true),2026-11-10, authority named milestone delegation, gated D1–D5 in the exact approved-spec snapshot before edits; gate.json binds its SHA and red inputs. The current spec appends a pre-execution liveness design; the original prefix was reconstructed and independently matched its gate digest before retention. These are agent rulings, not the owner's personal reading. No new paid phase review is selected; original phase opinions stay bound to their snapshots. Separate close review remains owed.

The offline guard was correctly rejecting the new example URL. Its removal restores the existing policy rather than relaxing HTTP/import/fence checks. The public API guard keeps every original export in order and appends only approved verbalize_model, with its one-model signature. The order guard retains validated-current before traversal/gating and checks both candidate branches and the plain candidate argument without whitespace coupling. RF1 adds only exact remove/metavar mutation-test IDs to the existing meta set; no public surface, historical inventory row or golden is removed or regenerated.

## Guard sensitivity and limits

Actual API guard passes clean and rejects missing, extra and reordered export mutations. Actual ordering guard rejects moving the real operations-gate statement below candidate validation. RF1 inventory passes clean and rejects an invented unknown pin and missing cli_tree. These are instrument liveness probes; runtime semantics remain supplied by the phase gates and upcoming default replay. Selected modules include all RF9 Python/text/container-fence neighbors, so the original URL assertion no longer masks their intended parser branch.

Current attributed budgets: MC2 source106/test565 under375/600; MC3 source1109/test1224 under1400/1400; MC4 production0/test120 under0/120, prose within1050. The actual combined post-MC3 test/support diff is128, reconciled as120MC4 +2late MC2 +6late MC3 obligations. This is not a cap change/transfer or a claim128fits120. All changes were scoped by originating obligations before edits; old phase counts and review limitations remain retained.

## Boundary and next action

The old complete output remains14failed/18787passed and nonzero; its six baseline identities are not rewritten. The earlier6de incomplete run also remains incomplete. Current418pass, strict build/site/components and unchanged13lint do not substitute for the named final full/default comparison. Existing owner authority already selects the corrected beast-3 candidate replay; retain separate source/runtime/status/output and compare exactly the immutable six failure IDs.

PR157c6dad88d and PR155396f86f3 heads remain unchanged with owner merge questions pending. Draft close PR158 contains these follow-ups. No main predicate, independent close opinion, merge, milestone/issue95 closure, certification or publication is established. The final current-source default result and explicit merge prerequisites remain required.

Delegated retention ruling preserves49 E-only trailing-space lines in exactly two rejected pytest output artifacts. whitespace.json enumerates them; every other staged path must pass whitespace checking. Runtime/test/docs authoring remains clean, and rejected outputs remain rejected.
