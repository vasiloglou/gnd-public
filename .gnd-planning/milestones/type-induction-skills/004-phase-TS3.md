---
milestone: type-induction-skills
station: "phase-TS3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-TS3
date: 2026-11-05
gate:
  command: "uv run pytest -q tests/test_packaged_skills.py tests/test_verification_fixes.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_marketplace_plugins.py tests/test_public_agents_skill_table.py tests/test_public_packaged_invocation_guards.py tests/test_public_packaged_command_help.py tests/test_public_workflow_claim_routes.py tests/test_public_packaged_import_skill_routes.py tests/test_skill_prose_sync.py tests/test_solve_successors.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py tests/test_schema_sync.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py"
  exit: 0
  output: "791 passed, 1 deselected in 91.27s (0:01:31)"
  note: >-
    Spec section 8 gate command 1, after the review fixes. Commands 2-5
    (zensical, check_docs, install, doctor), the distribution-lane
    inventory and ruff each exit 0; all are in evidence/TS3/gate.txt,
    with local paths redacted to <repo>.
slow_cadence:
  command: "uv run pytest -q -m distribution tests/test_public_distribution.py tests/test_release_acceptance.py; the full default lane"
  trigger: "the milestone close or an explicit owner request"
  reason: "spec section 8 ledger: the two literals were edited, not run"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS3-spec.md
    sha256: b52456feea54a1f328de2705d9816e040af96031628c13e7e99eea5b598e3969
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS3-claude-review.md
    sha256: a55d213bf7cbae335101be98cbe0a60cce15aef4d9620ed03a15947386bc50f9
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/gate.txt
    sha256: 1c6d57ba9ce3b588f3cf24490bf33c999a05769e81f96c7ddaca77556449e6fb
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/regressions-red.txt
    sha256: eab667a406cecfa7894b5f085ef2b206ee7d9c418897ef218f1fe2cec79c7298
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/recording/results.json
    sha256: 34fa2ba4f97e87d057cc9bfc378efc2c2585058e65ebeec196febb68b7453ca0
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS3/recording/manifest.json
    sha256: 1344d3e06a0a6401b7a1be5f02c1ccc72782d4eef3678701f634fb85cc5a1937
  - path: src/gnd/skills/gnd-judge-fact-types/SKILL.md
    sha256: 0a166a7b3897115ed6290e5e563e76afd930dad20a196c721630f155e13668d4
  - path: tools/record_judge_sessions.py
    sha256: d3ad657a0b713f4c35398bd6446caa71e17d2e970857b92e1f53c9ef85fd7439
  - path: tests/test_judge_fact_types_skill.py
    sha256: 05310125472bc1d6b7dc994652e0eee0ddeefcaa1fbbc9a47e2b7dd5bb4a43e4
  - path: tests/fixtures/type-judgements/round-two/answer-key.json
    sha256: 19a21e96ed519a61ff8b9467040f498457d2230c1101ea8807f5ea9e76497a9f
  - path: tests/fixtures/type-judgements/round-two/model.orm.yaml
    sha256: adb36c4fde0a7e74b67384195f756fb60e3f7fe5cefaa57d47f81dc839d10ebd
  - path: tests/fixtures/type-judgements/round-two/items.population.json
    sha256: ad0c9da0c4854872c3bf431810eefdd57f1f16f15b38494887bb13cd1a6c37fe
  - path: tests/test_il6_skill_census.py
    sha256: 49fe879e7573e514ea514006fa66ffded8996013baa8f722191e91df7ac32b74
  - path: tests/test_schema_sync.py
    sha256: 99b08ce4caf7cf8cb73ee34f77f1ac6bd607236f8881e8d1421da5426b34cf19
  - path: src/gnd/skills/gnd-orm-core/SKILL.md
    sha256: e8e11e051640821b37ea5638fe72f28410a772a1cd878976543ceee6e7e5c2c8
---

# TS3: the gnd-judge-fact-types skill

Spec: [phase-TS3-spec.md](notes/phase-TS3-spec.md) r1, approved by the
owner `(a3)` 2026-11-05 (prose, D1–D9 as proposed). Implementation began
on the owner's "Go ahead" in this session. Base: main `b4ef8cbf`.

## What shipped

- **The skill** `src/gnd/skills/gnd-judge-fact-types/SKILL.md`, the
  seventeenth packaged skill. It reads one type-evidence file and the
  model, never the population. It refuses evidence with the wrong format,
  a model digest that does not match, or groups left out. It decides every
  `proposed`, `shape_match` and `over_budget` group by R1–R4: same
  origin, shared facts, no shared facts, ask. It writes no file until
  every group has a verdict, then writes the `duplicates` judgements
  file and hands off to `gnd discover --duplicate-judgements` and
  `gnd evolve preview`. It never applies a proposal and never touches
  git.
- **Vendored schemas (D5):** `type-evidence.schema.json` and
  `type-judgements.schema.json` in `gnd-orm-core/references`. The runtime
  files are canonical. A separate case in `test_schema_sync.py` checks
  them, and the "Canonical schemas" paragraph is reworded to match.
- **Routes (D7):** a `gnd-orm-core` workflow-index row and two reference
  rows, a row in AGENTS.md, a row in `docs/agents/index.md`, and the
  installer's links in `.claude/skills` and `.codex/skills`.
- **Pins:** 16 → 17 skills and 65 → 68 files in every inventory. Links go
  212 → 218 with six named edges. There are two new `ROUTING_MATRIX` rows,
  a `RECORD_ROUTES` and a denial entry, and `'gnd-judge-fact-types': 2`
  in the snippet map. The distribution-lane literals are moved too.
- **IL6 census (D4):** pinned to the ilp-learners close merge `7818be1`,
  with no credit for uncommitted edits.
- **Fixture and key (D2):** `tests/fixtures/type-judgements/round-two/`
  has four groups, one per rule: g0 R1, g1 R2, g2 R3, g3 R4.
- **Recorder (D8):** `tools/record_judge_sessions.py`. It imports the
  redaction helpers from `record_skill_sessions.py`.
- **The recorded run (D1, D6):** one session with Sonnet 5.5 in Claude
  Code 2.1.300, two turns, 36.6 s, about $0.46. Disclosure was unset and
  `--show-values` was off. Every one of the ten checks holds:
  - after turn 1, no file existed; the agent asked about g3;
  - after turn 2, the file was written and is schema-valid;
  - `gnd discover` exited 0 and `gnd evolve preview` exited 0;
  - the verdicts equal the key;
  - only the judgements file is new;
  - there was no apply call, no access to the population, and no canary.

## Gate output (verbatim)

See `evidence/TS3/gate.txt` (paths redacted to `<repo>`). Gate command 1:
`791 passed, 1 deselected in 91.27s`, exit 0. Zensical: "No issues found",
exit 0. check_docs: "14307 local links/assets/anchors checked", exit 0.
Install: "already current (0 writes)", exit 0. Doctor: `current=17`, exit
0. Distribution inventory: "16 passed", exit 0. Ruff: "All checks passed!",
exit 0.

## Measured criteria

| Criterion | Result |
|---|---|
| TS3-C1 ships, installs, every pin | met: T1–T7, T12; 17 skills, 68 files, doctor `current=17` |
| TS3-C2 handoff, never apply | met: T8, plus the review F7 sentence check |
| TS3-C3 population rule, disclosure | met as prose: T10, review F1 clauses; the recording read nothing outside its workspace |
| TS3-C4 recorded run accepted, key matched | met for the skill bytes the recording binds (`067b1818…`); **those bytes are now superseded** (boundary) |

## Adversarial review

One reviewer is one reviewer. A subagent reviewed `51ec0a3a` without paid
calls; the report is kept verbatim (with paths replaced) in
[phase-TS3-claude-review.md](notes/phase-TS3-claude-review.md). It made
eight findings. I reproduced F1 (the value `24` collides with the
recorded "24 rows", exit 3) and F8 (three `/Users/` lines). F2–F7 were
confirmed by reading the cited lines and the reviewer's repros. Each fix
carries a regression test, and those tests were red before the fix
(`evidence/TS3/regressions-red.txt`: 9 failed, 40 passed):

| Finding | Class | Fix | Regression test |
|---|---|---|---|
| F1 numbers and model versions in scanned free text | hardening | step 4: no number standing alone when values are hidden; step 5: reword on refusal, stop on `judge.skill` | `test_review_each_rule_states_its_key_clause[F1-*]` |
| F2 all-null overlaps fell into R3 | hardening | R3 needs one comparable candidate | `[F2]` |
| F3 candidate truncation ignored | hardening | `truncated > 0` disables R3 (ask) | `[F3]` |
| F4 R1 ignored `origin.generic` | hardening | R1 requires the same generic | `[F4]` |
| F5 population check bypassable after redaction | hardening | the evidence directory keeps no population; raw streams scanned for population, answer key, fixture, evidence directory and `tests/` | `test_review_f5_*` |
| F6 edited inputs unseen | completeness, fixed (cheap) | per-file SHA-256 before and after | `test_review_f6_*` |
| F7 rule bodies unpinned | completeness, fixed | key clauses and eligible statuses pinned; every sentence naming apply must deny it | `[F7-*]`, `test_review_f7_*` |
| F8 local paths in gate.txt | hygiene | gate regenerated with `<repo>` | `test_review_f8_*` |

The reviewer also ran all 51 test files that read the skill tree: 2203
passed and 2 failed. Both failures are in `test_rf7_structure.py`, and
they also fail at base `b4ef8cbf`, so they are not TS3's.

## Refactoring review

**None executed.** One refactor was seen and deferred.
`record_judge_sessions.py` repeats the turn loop of
`record_skill_sessions.py`, about 30 lines (start, resume, timeout,
result event). Merging them means editing the PL18-pinned recorder, which
D8 declined. When TS4 adds its `shapes` entry it reuses this recorder's
loop, not a third copy, so the duplication stays at two. Open question
TS3-Q1 below. Nothing else that TS3 touched has a second home: the decision
rules have one home (T9), and the schemas are held by the sync test.

## Boundary — what this phase does NOT establish

- **The recording binds superseded bytes.** It ran on skill
  `067b1818…` and recorder `2a7008a8…`; the review fixes changed both
  (now `0a166a7b…`, `d3ad657a…`). The fixture and key are unchanged. Its
  rationales quote counts ("24 rows"), which the fixed skill now tells an
  agent not to do. A second paid run over the current bytes needs a new
  owner authorization; D1 allowed one.
- **One run, one model, four groups.** It is evidence for those branches
  only. R3's truncation branch, R1's other-generic case and the customer
  mode have no recorded run.
- **Prose tests check sentences, not behaviour.** An agent can ignore a
  sentence and every prose test still passes.
- **Not run:** `test_public_distribution.py` and
  `test_release_acceptance.py`, whose literals were edited but which run
  at the close; and the full default lane.

## Open questions

- **TS3-Q1 (refactor deferred):** one shared turn loop for the two
  recorders. Target: TS4, or maintenance if PL18's pin is lifted.
- **TS3-Q2 (review F1, CLI half):** the TS2 free-text scan matches
  `judge.skill`, a fixed name, token by token. A population value equal to
  "gnd", "judge", "fact" or "types" refuses every file, and no skill
  wording can avoid it. Target: the CLI owner (maintenance); a
  fixed-vocabulary check would close it.
- **TS3-Q3:** whether to authorize a second recorded run over the
  current bytes (owner).
- **Carried:** P1, P2 and P3 plan repairs and the §2.2 key at the close; the
  CT4 DateTime kind and the YAML and UTF-16 tracebacks to maintenance;
  `test_rf7_structure.py` red at base (maintenance).

## Refuted premises

- **P3 (plan TS3-C4):** "over the TS5 fixture". TS5 comes after TS3, so
  TS3 authored the fixture (D2).
- **Spec §6.5 / sweep (I1):** groups B and D are `proposed`. Wrong: every
  group is a `shape_match` against the applied induced fact type.
