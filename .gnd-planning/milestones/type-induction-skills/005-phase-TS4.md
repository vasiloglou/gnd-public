---
milestone: type-induction-skills
station: "phase-TS4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-TS4
date: 2026-11-05
gate:
  command: "uv run pytest -q tests/test_packaged_skills.py tests/test_verification_fixes.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_marketplace_plugins.py tests/test_public_agents_skill_table.py tests/test_public_packaged_invocation_guards.py tests/test_public_packaged_command_help.py tests/test_public_workflow_claim_routes.py tests/test_public_packaged_import_skill_routes.py tests/test_skill_prose_sync.py tests/test_solve_successors.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py tests/test_schema_sync.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py"
  exit: 0
  output: "879 passed, 1 deselected in 192.82s (0:03:12)"
  note: >-
    Spec section 8 gate command 1, after the review fixes and both
    recordings. Zensical, check_docs, install, doctor (current=18), the
    distribution-lane inventory and ruff each exit 0; all are in
    evidence/TS4/gate.txt, with local paths redacted.
slow_cadence:
  command: "uv run pytest -q -m distribution tests/test_public_distribution.py tests/test_release_acceptance.py; the full default lane"
  trigger: "the milestone close"
  reason: "spec section 8: the two literals were edited, not run"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS4-spec.md
    sha256: 14a27d9d9e25aa46b7c33b67f99d0edb243ec3f82290dd659919fbd46c24746f
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS4-claude-review.md
    sha256: 1a5ad820aa9aff2f5523fccc3db9a024379ddf473735dd6caad877f5d4258a4d
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS4/gate.txt
    sha256: 5efe54e090b1c72186459d598d4a98282fda3763d06da16bc14db5c8ff06e3b2
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS4/regressions-red.txt
    sha256: 057280595d63b6b5f492065e6ed319e5e6c600912b69d2262ea0d27e2690f483
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS4/recording/results.json
    sha256: e8c8702142467007c4107d1c3f62ca6c7e6d9d1a0a2387ce34ffbe76f3d3c12c
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS4/recording/manifest.json
    sha256: ba372d736526dd282bd8e5ee6b92167cd4792c965c5f13c500daa6309515045f
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/recording-2/results.json
    sha256: b6c2d391d6bbd1cccb2db3e956312be49e9ce766377888251e5a475d63fe18c1
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/recording-2/manifest.json
    sha256: a017c22947f8f18f1e20fe725d44f8f9f43806aebe6762dbb82c100dbbeacc9d
  - path: src/gnd/skills/gnd-model-multivalued/SKILL.md
    sha256: 2a3b486fa2333e4b55d98d4bb7c7ade6bab6519cc6e3e38fe9f95ecc0dd4f1cc
  - path: src/gnd/skills/gnd-judge-fact-types/SKILL.md
    sha256: 610722f8563bdfd9821f1cb84c907c8d17b56edc88c149805c17ac6fecc07aaa
  - path: src/gnd/skills/gnd-orm-core/SKILL.md
    sha256: b7fcf2dba26c638afe301cd11a4ed384a06d6ed419a7301b2a5886ac7dd3dc4b
  - path: tools/record_judge_sessions.py
    sha256: f3f5ab363b34e3bc5ed2f66b435e29415a43eb5c2743d0d3eb4e0bc7877251cf
  - path: tests/test_model_multivalued_skill.py
    sha256: 2235206276f8dbbc5288bd0875468b92bc283a3b54a31c5b466aacaa2898a41b
  - path: tests/test_judge_fact_types_skill.py
    sha256: 88bd61ed3c232b7fecf52a88d0401ea006d3544c2fb2024b65bf07e530fa555f
  - path: tests/fixtures/type-judgements/multi-valued/answer-key.json
    sha256: c829a1cc4de34370087ae16f9816f3245b12c598baf3591c27e41b9b1c63d940
  - path: tests/fixtures/type-judgements/multi-valued/model.orm.yaml
    sha256: d90a666c8a7419b667ede47ee191a2424cc71cc07bdf2e4a145617b01c48629e
  - path: tests/fixtures/type-judgements/multi-valued/items.population.json
    sha256: 66dc3f9a4f2c314b85f770aeff4fab9bdfa5d59c5143e5b75e7a86c9cf06ad57
---

# TS4: the gnd-model-multivalued skill

Spec: [phase-TS4-spec.md](notes/phase-TS4-spec.md) r1, **delegated approval
(auto=true) `(d4)`** under the owner's `process-milestone
type-induction-skills auto`; an agent ruling, not an owner reading. The two
paid runs are the owner's own answer, "TS4 run + TS3 re-run (Recommended)",
quoted in the spec. Base: main `1668a58e`.

## What shipped

- **The skill** `src/gnd/skills/gnd-model-multivalued/SKILL.md`, the
  eighteenth packaged skill. It states the `rai-orm-from-schema` junction
  table convention it borrows and that `gnd import rai-orm` is unchanged,
  and links the spanning uniqueness in `constraint-reference.md` instead of
  copying it. It reads the evidence and the model, never the population;
  refuses as TS3 does; decides every `multi_valued` group by S1 (already
  induced: skip, and route a single-role origin to `gnd-model-evolve`), S2
  (already held: skip), S3 (junction table: many-to-many) and S4 (ask);
  writes the `shapes` file and hands off to `gnd discover
  --shape-judgements` and `gnd evolve preview`. It never applies.
- **Routes:** `gnd-judge-fact-types` links it for `multi_valued` groups (TS3
  D7); `gnd-orm-core` workflow row and both schema rows; AGENTS.md;
  `docs/agents/index.md`; installer links.
- **Pins:** 17 → 18 skills, 68 → 69 files, 218 → 228 links, three
  `ROUTING_MATRIX` rows, `RECORD_ROUTES` and denial entries, snippet map.
- **Fixture** `tests/fixtures/type-judgements/multi-valued/`: five groups,
  g0 S1, g1 S2, g2 S3, g3 S4 (few multi), g4 S4 (partial overlap).
- **Recorder:** one loop, per-skill entries (fixture, canaries, gates, turns).

## Recordings (D1, owner-authorized)

| Run | Model | Turns | Time | Cost | Checks |
|---|---|---|---|---|---|
| TS4 `gnd-model-multivalued` | sonnet (Claude Sonnet 5.5) | 2 | 34.1 s | about $0.27 | 9 of 10 true; `no_population_access` false, a recorder false positive (R1) |
| TS3 re-recording `gnd-judge-fact-types` | sonnet | 2 | 27.4 s | about $0.23 | 10 of 10 true |

TS4: after turn 1 no file existed and the agent asked about g3 and g4; after
turn 2 the shapes file held five verdicts equal to the key; discover exited
0 (one many-to-many proposal, `judged_skip` 4) and preview exited 0. Its
tool calls were `ls`/`shasum`/`cat` and a `grep` in the workspace and one
Write of the judgements file. **R1:** the population check matched the word
"population" in that file's written content (the S4 rationale "the
population is to be corrected", which the skill asks for). The check now
ignores written text; a regression test was red before the fix; the
corrected checks pass over the kept streams. The run is kept as recorded,
with the false check, and was not retried.

TS3 re-recording (closes TS3-Q3): current skill `610722f8…`, recorder
`f3f5ab36…`, fixture unchanged; the four verdicts equal the key; no
rationale carries a count. `tests/test_judge_fact_types_skill.py` now binds
`recording-2` and checks its sources are current; the first recording is
kept intact.

## Measured criteria

| Criterion | Result |
|---|---|
| TS4-C1 ships, installs, every pin | met: 18 skills, 69 files, doctor `current=18` |
| TS4-C2 handoff, never apply | met: T8 |
| TS4-C3 population rule, disclosure | met as prose (T10); the recording read nothing outside its workspace |
| TS4-C4 rai convention stated, uniqueness linked not copied | met: T11 |
| TS4-C5 recorded run yields `many-to-many`, accepted, preview 0 | met for the recorded bytes (skill `2a3b486f…`, current); one recorded check false by recorder defect R1, corrected offline |

## Adversarial review

One reviewer is one reviewer. A subagent reviewed `3fe48d2a` before the
recordings, without paid calls; its report is kept verbatim in
[phase-TS4-claude-review.md](notes/phase-TS4-claude-review.md). I reproduced
F1 (g1 → S3 `many-to-many`, exit 0, with the label role redacted), F2 (skip
exits 0 with no route) and F4 (four missed outside calls); F3 by rerunning
the reviewer's mutation script after the fix (10 caught, 0 survived; 3
patterns no longer present because their clauses were rewritten and pinned).
Regression tests red before the fix: `evidence/TS4/regressions-red.txt`.

| Finding | Class | Fix | Regression test |
|---|---|---|---|
| F1 null overlap with a redacted role | hardening | a `null` overlap on a candidate whose other role is redacted stops S3 | `test_review_each_rule_states_its_key_clause[F1]` |
| F2 single-role origin skipped silently | completeness, fixed (cheap) | S1 reads the uniqueness; routes to `gnd-model-evolve` or a corrected population | `[F2]` |
| F3 clauses unpinned; no partial-overlap group | completeness, fixed (before recording, cheap) | twelve key clauses pinned; fixture g4 | `[F3-*]`, `test_review_f3_*` |
| F4 reads outside the workspace unseen | hardening | `outside_calls`: path arguments outside workspace and plugin, or inputs naming the repository or home | `test_review_f4_*` |
| R1 (from the recording) written text counted as access | hardening | checks skip `content`, `old_string`, `new_string` | `test_r1_*` |

## Refactoring review

**None executed.** One refactor seen and deferred: `record_judge_sessions.py`
now walks stream events for tool calls three times (`forbidden_calls`,
`outside_calls`, `tool_calls`), about ten lines each. One generator would
serve all three. Deferred because both recordings' manifests bind the
recorder's bytes and the tests check those sources are current; a
behaviour-preserving edit now would stale two recordings for no change in
what they show. Open question TS4-Q1. The duplicated turn loop of TS3-Q1
stays at two copies, as TS3 required: TS4 added an entry, not a loop.

## Boundary — what this phase does NOT establish

- **One run per skill, one model.** Evidence for the fixture's branches
  only. S3's `null`-overlap branch, the redacted-role case, truncation and
  the single-role origin of S1 have no recorded run; they are prose with
  pinned clauses.
- **S3's one-in-ten line** is not discriminated by the fixture: g2 (12 of
  24) and g3 (1 of 24) lie on the same sides of any line between 1/24 and
  1/2. Only the clause is pinned.
- **The TS4 recording's `results.json` keeps `no_population_access:
  false`.** The claim that no population was read rests on the corrected
  check over the kept, redacted streams, not on the recorded value.
- **Prose tests check sentences, not behaviour.**
- **Not run:** `test_public_distribution.py`, `test_release_acceptance.py`
  (edited; the close), the full default lane.

## Open questions

- **TS4-Q1 (refactor deferred):** one stream-walk generator for the three
  recorder scans, with a re-recording or a manifest exemption. Target:
  maintenance, together with TS3-Q1.
- **TS3-Q3: resolved** by `recording-2`.
- **Carried:** TS3-Q1, TS3-Q2 (CLI owner); P1–P4 plan repairs and the §2.2
  key at the close; CT4 DateTime, YAML/UTF-16 tracebacks and
  `test_rf7_structure.py` red at base (maintenance).

## Refuted premises

- **P4 (plan §2.3):** "`functional` (only when the user confirms the extra
  values are errors…)". No `functional` verdict exists (TS2 P2); the
  confirmed-errors answer is `skip` plus "correct the population".
