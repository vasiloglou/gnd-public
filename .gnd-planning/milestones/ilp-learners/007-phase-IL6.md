---
milestone: ilp-learners
station: phase-IL6
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL6
date: 2026-10-28
gate:
  command: "uv run pytest -q -p no:randomly <the IL6 file list, evidence/IL6/gate-files.txt>"
  exit: 0
  output: "1242 passed, 24 deselected in 127.41s (0:02:07)"
  note: >-
    The spec §8 gate: IL4's gate files plus tests/test_il6_walk.py,
    tests/test_il6_skill_census.py and tests/test_ik6_walk.py, with the
    neighbouring census, packaged-skill, tutorial and public API tests (23
    files). T9 ran once on the final docs and package bytes:
    tools/check_installed_docs.py, both wheel origins, 229 tutorial blocks
    each, the learners and induced groups included. Ruff clean on the
    changed Python files.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL6's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL6-spec.md
    sha256: f73fefdd01429f3a6dd25f53f0b32ecb793dc66a8780e68ab66c61065c510499
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL6-agent-review.md
    sha256: 52d027feab2539ddadb3e522b9a0732f85569906360761bf5e58fbdc08b30c2c
  - path: .gnd-planning/milestones/ilp-learners/skill-census.md
    sha256: 5652255373e47c7e8b68e13ee99747e0b94cc0d89c433b1d7c5de253f4158639
  - path: tests/fixtures/ilp_learners/il6/comparison.json
    sha256: 6e32bc0a837846ff80d829f14fa7542c76ce811fd3e666bd9775914c6cc3a45c
  - path: tests/fixtures/ilp_learners/il6/walk-goldens.json
    sha256: 94cb083ed8e5ce0210c4249c405287c56d92265ebe11adc1429bb8e0f573afc9
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL6/final-gate.txt
    sha256: 2bd595168c12f4e4dedaa92a10710810c54fe8990da6d2266756f2617808384e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL6/gate-files.txt
    sha256: 6ace029640daef62e91f4bafe474128a9284de36f4149593619195d55e9365fa
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL6/installed-results.json
    sha256: c7f617c0379e49f6a9053db10f83480f30c3fb337555095c2ba01899564ca777
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL6/installed.txt
    sha256: 18e5fc5eb0778379dcc971d105eeff1941da69f6d87de38cd76704f8da37e41b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL6/r4-red.txt
    sha256: c9ff7f5db574e427db6ae6e5e63a549185ffa3b0a5cf116a4fb74da47e70fc1f
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/facts.tsv
    sha256: fa9abba9fe0e7eb6b6e84e43bf8fab1a5d6b053a29987730322600ebf663b867
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/import-report.json
    sha256: 347e9b6bf0d7c1109882a23120d3fcb27348ffdb4d855269f1bd82779ac96dbc
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/invocation.json
    sha256: e26d362acb4aee9597e2bddc7a88e69b2aec260581c4c3ca2873689986e4378e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/outcome.json
    sha256: 747effc1009be40bd4b36a94360060a9e13769ef2a8c98b8887c7275ba3f25f4
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/proposal.json
    sha256: c5aae4920d8b52c643244d854f5b3608be0a674395a23583b518a4c652232822
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/raw-stderr.txt
    sha256: ec9604f7ffa96e74e683407a1976da127c2f3e0f691eab764af30298588bc4bc
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/raw-stdout.txt
    sha256: 3b58842c69bc7e5e4fcded077d163ea671b716a6fdd92e7b722cdb8f4776adc7
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/reported.json
    sha256: 366cefd20acc5f26bafb2c7582011db31bfa04695da4c69253582e3373128c74
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/rules.txt
    sha256: 4229ea06b20814788e5b28fa5f77368faf599a23abf6623359bc18329dfe762c
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/run_amie.py
    sha256: badbf20dc63405117b88a072f66ef373905fc0fce0da4c65c0db86137a7d4841
---

# Phase IL6 -- the learners compared on real runs

**One reviewer is one reviewer.** The adversarial review of this phase was a
single agent's reading of the diff; it is evidence, not a proof.

## What shipped

- **The comparison table.** `tools/ilp_comparison.py` derives every row from
  the committed live-run evidence (each run's `outcome.json`, its retained
  learner output read by the target's own reader, its import stderr and
  proposal, and GND's own count of which mined rules hold). It equals the
  corpus golden `tests/fixtures/ilp_learners/il6/comparison.json`, committed
  red at `e679e40` before the tool and before AMIE invocation 2, and it writes
  the "Comparing the learners" section of `docs/reference/ilp-bridge.md`.
- **The walk page.** `docs/how-to/compare-ilp-learners.md`: 12 runnable
  blocks replay each adapter's export and its committed learner output
  through the import; two refusals (ILASP, AMIE run 1) are shown with why
  they were refused and how GND caught it. New `learners` group in
  `tools/run_tutorials.py`; nav entry in `zensical.toml`.
- **Shipped learner outputs.** `src/gnd/examples/refunds/learners/` (popper,
  ilasp, llm, rules) and `src/gnd/examples/staffing/` (model, population,
  README, `learners/amie/`, `learners/amie-2/`), byte-equal to evidence.
- **AMIE invocation 2** (IL6-D6 (a), the one authorized run):
  `evidence/IL4/live/invocation-2/`, argv `-maxad 3 -mins 1 -enstd -minc 1`.
  Completed and admitted, 2 rules (5 of 5 and 20 of 20 head pairs), as
  stated before the run; `body_size_agrees` true for both. `run_amie.py`
  takes the invocation number and refuses one with no owner-ruled settings.
- **Docs.** `cli.md` (the amie export, `gnd import mined-rules`, every
  target), `capabilities.md` (every adapter, both imports, the stale Popper
  caveat dropped), the release notes, and the bridge's live-run sentences.
- **Skills.** Pin sites `gnd-export/SKILL.md` and `gnd-model-evolve/SKILL.md`,
  plus `gnd-solve/SKILL.md` Station 6 (review R3); the 65-row census
  `skill-census.md` with `tests/test_il6_skill_census.py`.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL6/gate-files.txt)
1242 passed, 24 deselected in 127.41s (0:02:07)
```

Exit 0. T9, `uv run python tools/check_installed_docs.py --out <scratch>`:
"229 tutorial blocks passed" for each wheel origin, "Both installed wheel
origins passed the documented learning paths." (`evidence/IL6/installed.txt`,
`installed-results.json`). The full `uv run pytest -q` was not run.

## Criteria

| Test | Result |
|---|---|
| T1, T2 the walk under PYTHONHASHSEED 0 and 1 writes the 9 golden files | pass |
| T3 shipped bytes equal evidence; nothing else ships; privacy; refused imports write nothing | pass |
| T4 the tool equals the golden and the bridge section; a changed input changes its row | pass |
| T5 each row agrees with the page and its `outcome.json` | pass |
| T6 the reference pages name every target, import and refusal; no stale Popper caveat | pass |
| T7 the census; seeded faults fail by name | pass |
| T8 RF1 pins, RF5, layering, arch, RF6, built inventory, schema sync, API pins | pass (in the gate) |
| T9 both wheel origins, `learners` and `induced` | pass |
| T10 AMIE invocation 2 replays | pass (`tests/test_ilp_amie.py`) |

## Review

`notes/phase-IL6-agent-review.md`, retained verbatim (scratch paths and
identity tokens scrubbed). No blocking finding.

| Id | Finding | Triage | Disposition |
|---|---|---|---|
| R1 | Pages said each learner ran once; Popper ran 3 times, AMIE under 2 settings | hardening | fixed (`b8839b0`) |
| R2 | The page said AMIE's run of record used defaults; it used `-mins 1` | hardening | fixed |
| R3 | The gnd-solve census row was false; Station 6 lists proposal sources | completeness | fixed: Station 6 names mined-rules, census cell IL6 |
| R4 | T4's mutation test could not fail | hardening | fixed: mutates copied evidence; red against a golden-echoing build, all 5 cases (`evidence/IL6/r4-red.txt`) |
| R5 | The milestone README called the IL6 spec a draft | completeness | fixed in this record's commit |
| R6a | T6 checks refusal names page-wide, not per adapter section | completeness | deferred, IL6-Q1 |
| R6b | Nothing pinned "a refused import writes nothing" | hardening | fixed: T3 asserts it |
| R6c | `hold()` counts an unmappable rule as not holding, silently | completeness | deferred, IL6-Q2; no committed evidence triggers it |

The gate itself found one more: the retained review named home-directory
prefixes literally, which `test_ilp_learners` T8 refuses; reworded.

## Refactoring review

**None executed.** What the phase touched is new: a read-only tool, a page,
tests and copies of evidence. Two structural points are deferred:

- **`tools/ilp_comparison.hold()` imports `ilp_service._mined_inputs`,** a
  private name, to reuse the import's own loading. A public "count mined
  rules on a population" entry would serve both. With IL4-Q3, close.
- **`_learner()` looks for the learner record under four keys,** because each
  phase's `outcome.json` placed it differently. The evidence is immutable;
  a shared outcome schema is for a later milestone (IL6-Q3).

## Boundary -- what this phase does NOT establish

- **Which learner is better.** Each row is one run on one small example.
- **Reproducibility.** Rows record each run's own reproducibility note; no
  repeat runs were made (IL6-D5).
- **Any learner in CI.** The page replays committed outputs; no learner is
  installed or run by the tests.
- **That every packaged skill sentence about the bridge is complete.** The
  census argues each file; it is one author's reading plus one reviewer's.

## Open questions

| Id | Question | Owner | Target |
|---|---|---|---|
| IL6-Q1 | Review R6a: pin each refusal name to its adapter's section in the bridge page? | author | close |
| IL6-Q2 | Review R6c: should `hold()` refuse, rather than count as not holding, a rule GND cannot map? | owner | close |
| IL6-Q3 | One outcome schema across adapters' live-run records, for a later milestone | owner | later milestone |
| IL4-Q4 | Discharged: invocation 2 ran (IL6-D6 (a)) and was admitted. | owner | done |

## Refuted premises

1. **"The T4 mutation cases test the tool"** (spec T4): they compared the
   tool's output with a changed golden, which any tool passes (review R4).
2. **"Two pin sites"** (spec §6): gnd-solve's Station 6 also lists proposal
   sources (review R3).
