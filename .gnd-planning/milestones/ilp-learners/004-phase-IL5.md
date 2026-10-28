---
milestone: ilp-learners
station: phase-IL5
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL5
date: 2026-10-28
gate:
  command: "uv run pytest -q -p no:randomly <the IL5 file list, evidence/IL5/gate-files.txt>"
  exit: 0
  output: "842 passed, 22 deselected in 56.18s"
  note: >-
    The literal gate of spec §8: the direct IL5 tests (tests/test_ilp_llm.py)
    and the plan §9 impact closure (the IL1, IL2 and IK5 bridge tests, the IK6
    walk, the IK close test, the RF1 CLI goldens, RF5 commands, the layer map,
    the architecture test, the RF6 census, the built inventory and schema
    sync). The live lane ran separately with the IL1 scratch SWI-Prolog:
    2 passed. The RF1 CLI pins also ran under Python 3.11.15: 113 passed.
    Ruff clean on the export package, the IL5 tests and the run script.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL5's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL5-spec.md
    sha256: 4c1897edd36c4a186b100cf12edd47f3c2dc486f978c366550d12fc8911964bf
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL5-agent-review.md
    sha256: ffa2f7e4180b998be246ac7bd035f175423de341b4e7162f71f9df1131f79d20
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/gate-files.txt
    sha256: 86e4052fa6b6e1934171a5afa04ab3a3d5f3a36341b4c8959b489f5076f08746
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/final-gate.txt
    sha256: b4604c9883492bc41092aa17afd9e5a5310f79511ed2344fe9673f4385f791b7
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/review-brief.md
    sha256: 5508c5d53c289e6cad061ff6caaccc858a5bbcf86b1fe9913c1bd1e58fbd541b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/run_llm.py
    sha256: 996ccff9d26d99d9149ec8c52ace873cebc328ab5fabf5e7da009b79ac365466
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/dynamic-query-successor.json
    sha256: c30801e409783b16c56447ddf7f173f49ea4785bc587ad8ecc7b12b28663ee74
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/provider-terms.md
    sha256: dc5046680c0d895d83d3795cfe352e50346f658950062941b260c161c353dcc2
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/provider-terms-confirmed.json
    sha256: 8b4b598a11573c284a2ccc996681270c5f1109ae4623454164e1fadd7a044189
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/answer.json
    sha256: 98db66d2a20c0c5637172649b1d66ff4291967d916d74cb8f38e184f2a4a83a1
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/import-report.json
    sha256: f48aa9ba67ad511f3f5deac9cb2d1b89c83cdd364701a6c29e153b5349bdd0d2
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/invocation.json
    sha256: 2711d12cfe53cba7777939d67f51bb8a500a010876f15094359665130fb617af
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/outcome.json
    sha256: 591f6469a64de6444dbc7bc19d0cd0a930f78f09543b1a0c8894a9a3062213f9
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/proposal.json
    sha256: e21739ceeb6dfef4a2999ef563db039eb4070b5730ea3c4523340eae8f70a4ea
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/run-meta.json
    sha256: 7be88f5dc9d9e41d2103fbcbf85b7203f1b745fec0e1cfa50bc0c8cdc5344c2e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL5/live/invocation-1/run.json
    sha256: 6a9ca0f04263262957f75ea0a85666c35b11f1c98d2b8a1f52ae4c240015759e
  - path: tests/fixtures/ilp_learners/il5/answers.json
    sha256: a1a4fcff8ba242848807843fbc6006c3ab024244f86ca4c2ce84faa068911629
  - path: tests/fixtures/ilp_learners/il5/expected/refunds/prompt.txt
    sha256: e1d9746eece7b291859ac6af74e28daca517b782877e0fe26741bc8f227b8c73
  - path: tests/fixtures/ilp_learners/il5/expected/orders/prompt.txt
    sha256: 3a8323277764d85109405012790621e7f87b63f42164727d49c0045bbb18427e
---

# Phase IL5 — the LLM proposer, its prompt builder, and one claude run

**Claim.** IL5-C1 to C3 hold on the evidence below, under:
- the owner's gate rulings of 2026-10-27 (spec §12);
- the owner's confirmation of the provider terms, "approved", for invocation 1
  (`evidence/IL5/provider-terms-confirmed.json`);
- one reviewer's adversarial read, whose findings were reproduced, and six of
  eight fixed at first. The other two were fixed after the owner's rulings
  IL5-Q1 (o) and IL5-Q2 (o) of 2026-10-28.

## What shipped

- **`src/gnd/export/ilp_prompt.py` (new):**
  - `build_prompt(neutral, model)` writes a fixed HEADER, one DATA section and
    a fixed TRAILER. The DATA section holds the model's verbalization from
    `=== Object Types ===` on, then one ASCII-only, sorted-key JSON line per
    predicate, comparison (with its thresholds), example and fact.
  - A prompt over 256 KiB is refused `too-large`.
  - Step 4 added the `forged-line` refusal: a verbalization line that, trimmed,
    repeats one of the prompt's own structural lines, opens a code fence, or
    reads `model: ID`. Benign prompts are byte-identical, so
    `PROMPT_VERSION` is still 1.
  - `extract_answer` returns the one complete json block, else `""` (IL5-D3).
    `extract_model` returns the first full `model: ID` line, an unverified claim
    (IL5-D4).
- **The registry:** `llm` accepts a `claude` or `codex` run record
  (IL5-D2), exports nothing, and binds the neutral export through the new
  `binds` field (IL5-D1). `ilp_service` resolves the bound target before export
  binding and accepts a tuple of learner names.
- **Surfaces:** the import CLI choices, `ilp-import.schema.json`'s `target`
  enum and the layer map add `llm`/`gnd.export.ilp_prompt`. The docs gain the
  "LLM proposer" section. Seven RF1 goldens moved (help and exit for three
  Pythons, and `cli/tree.json`); the two py311 ones were recaptured under
  Python 3.11.15 in step 4.
- **RF6:** `evidence/IL5/dynamic-query-successor.json` chains to IL2's delta.
- **The run script:** `evidence/IL5/run_llm.py`. It refuses to start without
  the owner's terms confirmation. It never overwrites an invocation, writes the
  raw streams first, evaluates coverage with SWI-Prolog over `popper/bk.pl`
  plus an arithmetic `cmp.pl` (IL5-D6), then runs the fixed import. Step 4 made
  its evaluator admit only `wrong/1` over the export's own predicates, spell
  `compare` literals, record an SWI failure instead of exiting, and withhold an
  answer that holds a private string.

## Gate output (verbatim)

From `evidence/IL5/final-gate.txt`:

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL5/gate-files.txt)
824 passed, 22 deselected in 47.27s
$ GND_IL5_SWIPL=<scratch>/il1-live/SWI-Prolog.app/Contents/MacOS/swipl uv run pytest -q -p no:randomly -m live tests/test_ilp_llm.py
2 passed, 58 deselected in 0.95s
$ uv run ruff check src/gnd/export tests/test_ilp_llm.py .gnd-planning/milestones/ilp-learners/evidence/IL5/run_llm.py
All checks passed!
$ <scratch>/venv311/bin/python -m pytest -q -p no:randomly tests/test_rf1_cli_pins.py   # Python 3.11.15
113 passed in 0.68s
```

**A known red outside the gate:**
`tests/test_rf1_pin_harness.py::test_golden_manifest` fails, because
`goldens.sha256` lists stale digests for nine goldens moved by IL1, IL2 and
IL5. It fails with the same nine names at `426bd80`, which was checked in a
throwaway worktree. It is not in any IL phase's gate files (IL5-Q3).

## The run of record

- **The terms:** recorded before the run in `evidence/IL5/provider-terms.md`.
  The `claude` CLI was signed in through claude.ai on a Max plan, with no
  credential variable set, so the Consumer Terms apply. The owner confirmed
  the four points with "approved" on 2026-10-27, including the §3 reading,
  which is the owner's.
- **Invocation 1** (`evidence/IL5/live/invocation-1/`):
  - termination `completed`, import `admitted`;
  - the agent reported `model: claude-opus-5-5`, which nothing checks;
  - the agent wrote no files;
  - the one clause is
    `wrong(X) :- f_refund_amount(X, R, A), ge_t_amount(A, 640)`;
  - SWI covers harbor, market, airport and station, and GND's import agrees
    (support 4 of 4).
- **T9** replays it from the committed bytes. Since step 4 it checks every
  evidence file, and five tampered copies each fail it.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| IL5-C1: deterministic prompt; host strings cannot change the instructions | T1 (golden under two hash seeds), T1b, T2, T2b, R2 (forged lines refused) | holds, after the step 4 fix to R2's case |
| IL5-C2: a malformed answer exits 3 at the reader; a wrong claimed coverage exits 3 `coverage-mismatch` | T5–T8b over the approved corpus | holds |
| IL5-C3: one live run under IL-R9, with a replay test, only after D8 | D8 (a) ruled; terms confirmed; invocation 1; T9 | holds |

## Review

One reviewer is one reviewer: one local agent read `git diff 426bd80
93216bc`. Its report is retained, edited only to replace paths, in
`notes/phase-IL5-agent-review.md`, with the disposition. Of 8 findings, all
were reproduced:

- 6 are fixed, each with a regression test run red first. Before the fixes, 12
  tests failed and 8 passed; the 8 that passed pin branches that were already
  right.
- 2 waited for the owner, and were fixed after the rulings IL5-Q1 (o) and
  IL5-Q2 (o) of 2026-10-28. Their 18 tests (`test_q1_*`, `test_q2_*`) ran red
  first: 17 failed and 1 control passed.

The reviewer did not invoke an agent, run the run script, or run the full
suite.

**Coverage audit against the declared branches:**
- **termination:** every value has a unit case (R8) except `learner-timeout`,
  which is unreachable by IL5-D7.
- **import:**
  - `none`: T9's branch and R5;
  - `refused:unparsable`: R4;
  - a named refusal: R4;
  - `admitted`: T9.
- **The prompt's refusals:** `too-large` (T2b) and `forged-line` (R2).
- **The evaluator's refusals:** R1.

## Refactoring review

**Executed:**
1. **One termination and import mapping.** T9 had re-implemented
   `run_llm.termination` and the refusal mapping, so the test and the script
   agreed by construction. T9 now calls the script's own functions (step 4,
   review 8). The behaviour is unchanged, behind the same gate.

**Seen, deferred:**
- **Evidence-script scaffolding has three copies.** `run_popper.py`,
  `run_ilasp.py` and `run_llm.py` each carry their own sanitizer, sandboxed
  environment and outcome writer. The first two are retained evidence, cited
  by digest in their records, so they are not edited. A shared helper for the
  next live scripts (IL3, IL4) is IL5-Q4, targeted at IL3.
- **The forged-line rule lives in the prompt builder.** The verbalization's
  neutralizers keep text on one line but do not reserve any line. Any other
  prompt that embeds the verbalization would need the same check. No other
  caller in `src/gnd` embeds it in a prompt today, so the question is carried
  to close (IL5-Q5), not refactored now.
- **Considered and not done:** normalising `Learner.learner` to always be a
  tuple. The `str | tuple` union is read in one place, `ilp_service`, and the
  tuples are pinned by IL1's T2. Changing it would move pinned values for no
  behaviour change.

## Boundary — what this phase does NOT establish

- **One run is one sample.** Invocation 1 says nothing about how often the
  agent proposes an admissible rule, or the same rule. It is a single run, and
  it cannot be repeated.
- **The model id is the agent's claim.** `claude-opus-5-5` is not verified,
  since `gnd.agents` has no model flag (IL5-D4).
- **The CLI version is recorded only as a hash.** `learner.version` is
  `unreported` (IL5-F7), and the proposal's provenance says "claude
  unreported". The hash matches `2.1.300 (Claude Code)` on this machine,
  checked after the run.
- **The prompt's meaning is not protected, only its structure.** An injected
  sentence inside a value is still text the model reads. GND's re-check of
  every clause is the control (IL-R6 residual).
- **The provider terms are a paraphrase,** made on 2026-10-27. Whether they
  permit this use is the owner's ruling, not GND's.
- **SWI's agreement is independence of evaluator, not of data.** SWI reads
  GND's Popper rendering of the same export.
- **The step 4 review is one reviewer's reading.** It did not run the full
  suite or an agent.
- **The full default lane and the broad historical lane did not run** (slow
  cadence above). py313 goldens were edited, not captured, and were not run
  under 3.13.
- **`learner-timeout` is unreachable,** as it was for IL2 (IL2-Q4).

## Open questions

| Id | Question | Owner | Target |
|---|---|---|---|
| IL5-Q1 | Review 3: should a truncated run's answer still be imported? **Ruled 2026-10-28: no;** a cut-off run gives no answer (spec §12). | owner | closed |
| IL5-Q2 | Review 6: should any other code-fence line outside the one json block make the answer `""`? **Ruled 2026-10-28: yes** (spec §12); no approved corpus answer changed. | owner | closed |
| IL5-Q3 | `goldens.sha256` is stale for nine goldens moved by IL1, IL2 and IL5; `test_golden_manifest` fails at `426bd80` too. **Ruled 2026-10-28: refresh it.** Fresh captures under Python 3.11.15, 3.13.12 and 3.14.3 match eight of the nine goldens byte for byte; `cli/tree.json` differs only by the CS1 flag the test admits as a successor. Only the nine manifest lines and the pinned manifest digest moved. | owner | closed |
| IL5-Q4 | A shared helper for live-run scripts (sanitizer, environment, outcome writer), used from IL3 on. | author | IL3 |
| IL5-Q5 | Should the verbalization itself reserve structural lines for every prompt that embeds it? | owner | close |
| IL5-Q6 | IL5-F7: read the agent's version before `gnd.agents` redacts it, or add the version to its result. That changes a shared module. | owner | close |
| IL2-Q4 | Carried: no agent has a timeout of its own, so `learner-timeout` stays unreachable. | owner | close |

## Refuted premises

- **"No host string can add, end or forge a line of the prompt"** (the docs,
  and IL-R6 in the spec). This was false for verbalization lines: a reading or
  an object-type name is a whole line, and the neutralizers leave `=`, backticks
  and spaces alone. It is refuted by review 2's reproduction and corrected in
  place in both documents. The `forged-line` refusal now makes it true for the
  structural lines.
- **IL5-D4's "`learner.version` is the CLI version's first token".** It is
  refuted by invocation 1: `gnd.agents` returns the version already redacted
  (IL5-F7, IL5-Q6).
- **IL5-F4's "74 columns" for the edited usage line** holds for 3.13 and 3.14
  only. 3.11 wraps differently, as review 7 showed, and the py311 goldens were
  recaptured.
