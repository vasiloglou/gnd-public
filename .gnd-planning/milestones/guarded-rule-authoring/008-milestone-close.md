---
milestone: guarded-rule-authoring
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true"
scope: milestone-close
date: 2026-11-11
gates:
  - command: "Clean 618141de checkout, uv sync --locked --offline --extra synth, then evidence/close/verify-union.py"
    exit: 0
    output: "1023 passed, 5 deselected in 232.40s (0:03:52)"
  - command: "Clean offline wheel build, base and synth-extra installations, then evidence/close/verify-installed.py"
    exit: 0
    output: "Clean installed wheel passed all three workflows, base-only exit 5, and two exact measure digest refusals."
  - command: "evidence/close/verify-installed-provenance.py against both installs and a second clean wheel build"
    exit: 0
    output: "Both installed payloads match the identical clean rebuild."
  - command: "Standard GND panel, close-outcome.md and close-confirmation.md"
    exit: 0
    output: "5 valid in round 1; 6 valid, 5 approve and 0 blocking in round 2"
  - command: "gnd review finalize for each close-panel run"
    exit: 0
    output: "Round 1: 3 agreed groups and 10 divergent concerns. Round 2: 4 divergent concerns."
  - command: "delegated approval (auto=true)"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/003-phase-GA1.md
    sha256: dd049e0ae2da61e9fbf75c2d2940f96f28b7f290feb633d328abf80b0bd904fe
  - path: .gnd-planning/milestones/guarded-rule-authoring/005-phase-GA2.md
    sha256: 06e0297c7c38a22cccf6c80cff90f6870e498ab2ff9a6418d51ce66ae5348701
  - path: .gnd-planning/milestones/guarded-rule-authoring/007-phase-GA3.md
    sha256: b9e3458b3efe0eae1c72e1462d5b1da87ed6e56646d8c6f4f771007147d0e7a7
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/guarded-rule-authoring-plan.md
    sha256: 0e960702bd212634dac84fb6925638579583ddea5c6bbfa4611e19780affc162
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/close-outcome.md
    sha256: 7295c386e5268b43da364341acd5af76cf15abf742ec25b766fb8268d555799e
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/close-confirmation.md
    sha256: 104e3d400b77187afdbac60d4ce72622d0bcab87e0b679663575ca425de8aee4
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/union-clean.json
    sha256: 62b1e59e4165d62f3eb3ac3ff84bb41404689a22a58381799b2f35270f5eec60
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/installed-clean.json
    sha256: 606eacbd7bb78ebc13da16e7124142832e2867b76a19b4e6e28e7b89ddc0d25d
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/installed-provenance.json
    sha256: 3c5a28776ea832ef0e02221056ab575962eef16832e103bbb0f0b2660434b9b4
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/replay.md
    sha256: 8e22b1d66c9319a76846df1b653501dbb0267e750203c1c8559d3dc000559ba3
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/panel-r1.md
    sha256: fbd693ca606c4dc0927fb36cf54e15edbc4646f40320347f6c3c6e1cefc137e0
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/close/panel-r2.md
    sha256: cc0a15bce9659f674e22a51ab8a1f7f4e6e9ca35acd56fe413596a525a6aecfb
---

# Milestone close

**Delegated close approved (auto=true), 2026-11-11.** All three phase
records and both close-review rounds met the four-reviewer project bar
where applicable. The implementation candidate is
`618141de9975c4ef30871a979532654267a15de6`. The clean test and installed
receipts bind it to the locked environment. The amended plan retains the
approved r2 text and records the comparison and directed-cap rulings.

| Request | Checked outcome |
|---|---|
| [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179) | [GA1](003-phase-GA1.md) provides bounded `gnd synth --guarded-cases` pairs with active bindings, explicit per-rule refusals and ordinary mixed-model cases. Installed scoped measure scored 15 cases and rejected a wrong-model digest. |
| [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181) | [GA2](005-phase-GA2.md) proposes directed forbidden pairs and same-class guards, with optional target markers, distinct support, checker-confirmed counterexample rows and evolve preview. |
| [GR-D11](https://github.com/vasiloglou/gnd-public/issues/182) | [GA3](007-phase-GA3.md) maps typed AMIE literals in all four atom positions. The installed import admitted the issue's `area:cli` rule with support 1/1 and passed evolve preview. |

## Standard close panel

Round 1 reviewed the [initial outcome](notes/close-outcome.md) at
`c63184b9` and returned five valid responses. The
[finalized report](evidence/close/panel-r1.md) binds run SHA-256
`4636f4383f2b8afb502ed7ff469e58f24a9fd52f491d4640c5b25b946350b14c`.
Two findings required stronger evidence of a clean wheel build and the
base-only refusal. The detached clean checkout, separately installed
base environment and [clean receipts](evidence/close/replay.md)
reproduced both observations. The confirmation packet maps the remaining
round-1 concerns to exact commands, phase reviews, tests and decisions.

Round 2 reviewed the [confirmation](notes/close-confirmation.md) at
`66cca318`. Its [finalized report](evidence/close/panel-r2.md) binds run
SHA-256 `ad59c4365198485a9efd2724a2ea771c6e0ba8e6d839e78be72d1bd300849a75`.
All six seats returned valid responses. Codex, Qwen, Gemini, Kimi and GLM
approved. Claude requested four traceability and wording refinements.
There were no blocking findings. The two-round close budget is exhausted.

| Round-2 concern | Disposition |
|---|---|
| Executed smoke script identity | The [provenance receipt](evidence/close/installed-provenance.json) records the SHA-256 of the GA3 script at `618141de`, the close wrapper and the generated isolated input. |
| Link between both installs and the wheel | Both installed environments report the distribution version and match every package and metadata entry in the rebuilt wheel. The receipt records 1145 matched entries per environment. |
| Build invocation and clean source | A second offline build ran from the pinned checkout, with no ignored files under `src`, and reproduced the wheel SHA-256 exactly. Its verification script records the actual command. |
| Attribution of the digest refusal | Installed command 3 establishes exit 3. The specific C6 text was asserted in the separate `measure_digest_refusals[0]` invocation, with a rationale-only scoped-model change as the second control. |

## Boundaries and question sweep

The three predecessor deferrals are resolved by GA1, GA2 and GA3 under
the [reviewed scope](notes/close-confirmation.md#question-sweep).
The five default-lane deselections are named in the clean union receipt.
They concern live learners or historical evidence. The phase reviews read
their named pre-repair candidates. The current-runtime tests and close
receipts verify the later repairs. The phase reviews did not read those
repair diffs. Synthesis uses the optional synth extra. Generated cases
exercise the authored guard, discovery requires complete functional
classification, and the aggregate AMIE recount limit applies to
variable-only imports as well as literal rules.

The implementation and milestone record are attached to
[draft PR #190](https://github.com/vasiloglou/gnd-public/pull/190).
The repository's merge, certification and release gates remain separate.
