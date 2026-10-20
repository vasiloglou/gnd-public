---
milestone: incremental-evaluation
station: phase-IE0
skill: n/a -- repository development via process-phase
scope: phase-IE0
date: 2026-10-19
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline pytest -q tests/test_incremental_baseline.py tests/test_incremental_baseline_review.py tests/test_transition_cost_workload.py"
  exit: 0
  output: "49 passed in 149.41s (Python 3.11.15)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately selected CI
  reason: new diagnostic tool/test/fixture scope; no runtime changes
---

# IE0 — accepted under delegated approval

The owner selected milestone-wide `auto=true` in 002. The initial spec was
approved and committed in 94f4113 before implementation; instrument repair
and matched-course amendments were recorded in a0fbcd5 and 6f9fdf7. No
claim that the owner personally read those delegated rulings is made.

## Criteria and evidence

| Criterion | Evidence / result |
|---|---|
| C1 fresh baseline/identities | environment.json, work.json and public fixture hashes; final validator true on current identities |
| C2 real counters and timing | code-event body/evaluator/partial/join/fingerprint/public-call counters; zero/multiple/constant negatives; separate serial uninstrumented ABC/BCA/CAB samples |
| C3 oracle and discriminator coverage | independent full calculations, complete relation/lineage/unavailable/possible traces; seven control groups plus live references/options; reusable receipt mutation changes a consumed transition |
| C4 target/feasibility freeze | targets.json: reporter 13 calls, 19 receipt checker runs and 4,878 executed bodies; incremental body target strictly less than 4,878 with parity; localized unrelated/no-op body/evaluator targets zero; dependency census and effort limits in README |

Final reporter: full 25 vs receipt 19 checker runs, **4,878 body executions in
both**, evaluator work events 1,796 vs 1,365, fingerprint nodes 1,438,732 vs
1,119,220. Counter events are executed primitives/guarded binding work, not
unique findings. All reporter exits are 2. Course expected exits are 1/1/0,
three walk results with six public API calls per arm; checks 18 vs 15. Localized
has six checks, all exit 1 due intentionally incomplete derivation claims; its
receipt arm mints only and claims no receipt reuse saving.

The exact baseline command was:

`UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python tools/measure_incremental_evaluation.py --workload all --repeat 3 --out .gnd-planning/milestones/incremental-evaluation/evidence/IE0`

Exit 0. Lint command names the tool and both new test files; exit 0.
The selected pytest command and its result are in frontmatter/gate.txt. No
broad, provider/native, reserved or certification lane was run.

## Independent review and refactoring

One independent Codex CLI reader (read-only, stdin, xhigh) plus one bounded
confirmation; one reviewer is one reviewer, not a panel. Provider transfer was
explicitly authorized after the first auto-review rejection; no bypass was used.
The reader ran no tests. Both substantive responses, reproduced findings, red
regressions and fixes are retained in the notes and evidence. Initial review
found 13 instrument defects/gaps, confirmation found 3 acceptance gaps; all
were dispositioned with regression controls. No third round. Amended bytes
carry no new reviewer opinion; final acceptance is delegated disposition based
on the actual focused gates, not an invented reviewer approve verdict.

Refactors EXECUTED within the tool: shared semantic-envelope projection,
scoped code-event observer, per-call/timing observer and reuse of existing
loaders/driver helpers. Runtime/old fixture bytes are unchanged; no layer,
ModelIndex or shim changes. The duplicated driver logic is limited to adding
matched receipt/public-check paths and explicit observation, rather than
altering the old evidence tool's contract.

## Refuted premises and boundaries

- Matching internal-error results are not parity. Shallow-shared synthetic model
  data caused equal 70s; detached controls and exact expected exits now reject it.
- Finding labels were not evaluator counts. The corrected counter observes
  actual primitive returns/binding work, with live negative controls.
- Course receipt and full drivers initially had different public calls, so raw
  branch equality could not hold. The refused run is retained; a2 makes public
  prechecks match instead of filtering branch IDs.
- Evidence saved while the tool was changing was exploratory and invalidated.
  Only final serial evidence with matching identities supports this acceptance.
- Timing remains informational and machine-specific, not a promised speedup.
- New reporter workload is absent; no 547-program acceptance or data-size claim.
- All family reuse eligibility remains unproved until IE1/IE2/IE3; this phase
  changes no runtime behavior and demonstrates no incremental performance gain.
- The initial estimate was smaller than the eventual instrument/regressions;
  actual source/test sizes below replace the planning estimate, not history.

Next: IE1 corpus, final spec and delegated gate. The mutable receipt report fix
remains IE3-owned; source evidence is not a certification or publication.

## Artifact identities

[
  {
    "path": "tools/measure_incremental_evaluation.py",
    "sha256": "4c40938bd663a6a83f05daa6cee2c18d39b1725f1e6da93954b1a50fedb330e4"
  },
  {
    "path": "tests/test_incremental_baseline.py",
    "sha256": "821a0ce6965c045f3cfb0462038121b95378d3f1b82ae51e2b5967489d214e1b"
  },
  {
    "path": "tests/test_incremental_baseline_review.py",
    "sha256": "9b92fa07b0ccf635dfeb2ab8251f8b67bfc04fe691ee272f7a44254f8c7477a9"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/notes/phase-IE0-spec.md",
    "sha256": "cb909a0aab7bb96818b1e92503028e4decb092e1baefd5928edb42f510be8056"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/work.json",
    "sha256": "ea13001e8964c57b47fefd06ca4916f8fbf31edc2977136cdb1430a5a3acff71"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/parity.json",
    "sha256": "6faef50f3db903c202a5e2b8a9e59a07cb463cbef763b746017f758794dc59cd"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/timings.json",
    "sha256": "1f1923a582d0e1010ba010bd33a3711432b501071644982c900574a758e744e2"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/environment.json",
    "sha256": "5f06c4c356fa3fdcd05a552742b5724bef9503d9be417369f4a3d1cd82ab42c9"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/targets.json",
    "sha256": "4ad01e5af5936a286a604467108fd4cb6e9081ae0923e7c5540792ff506814d8"
  },
  {
    "path": ".gnd-planning/milestones/incremental-evaluation/evidence/IE0/reporter-dependencies.json",
    "sha256": "aae65031fc2af4493052156c6905af38015b9e84e047c5562e045ffe0836e99f"
  }
]

## Size

- `tools/measure_incremental_evaluation.py`: 524 lines
- `tests/test_incremental_baseline.py`: 168 lines
- `tests/test_incremental_baseline_review.py`: 222 lines
