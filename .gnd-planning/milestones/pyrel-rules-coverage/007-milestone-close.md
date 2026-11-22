---
milestone: pyrel-rules-coverage
station: "milestone-close"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "308 passed, 316 deselected in 34.68s"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_plans.py --tb=short"
    exit: 0
    output: "345 passed, 156 deselected in 440.12s (0:07:20)"
    note: "opted in by the owner for this milestone (plan §8)"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 99.93s (0:01:39)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "accepted residual against plan §9: the same 198 errors at base 92cd5c9b (002-phase-RP2.md), all in dev-tools-delivered skill scripts this repository does not edit"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/pyrel-rules-coverage-plan.md
    sha256: 004627d0098184027db692947b4ccb6f2f8cd5c2cc95ad02d3e8a56c142a31af
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/close-results.md
    sha256: 6333b7a6a88cfee7ece325f40fc6941f293400f86e9428838562ebc2e03cc129
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/close-delta.md
    sha256: abbcfdb17438d6c420e09ee8ac9894228ca0721ec786e2c0c647eebfbe6c085f
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/PANEL-REVIEW.md
    sha256: bee00b7c8a7d2e754e83f09f6ff3b97848e37cac584c49b19245edb220cf34ae
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/synthesis.json
    sha256: 992a87c8d4db71290a31f0e1faf61bf5a03a44119d0c6fe942357026435b7a92
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/run.json
    sha256: 4304fd11dbf30f8b1b2a48aaa335b6f8b0d41e02ef9bc8e027dce1063bd53025
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/review-request.json
    sha256: 5c413d01b2ef2b31ea7dfcdde0f626b6ce94853293af2e05e85c47ae8e38ae70
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/disposition.md
    sha256: c1858dbcef31e7dd71a778400a9dccc29f4bad260009511acfac47ff492aab11
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/claude.json
    sha256: 7a311052af276a5aa319c3f464c7e0f7370db2fbaa3a5326d8c7c2f34842e1f6
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/codex.json
    sha256: 0134805d7d2044f1a88c6470d5e7de03a4e0d154b9eb3e2c0e3da53705b55de9
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/qwen.json
    sha256: 2f685c5123192eda470d8bba99a2132d09871760649f089ff8df05cd6ee08bd0
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/gemini.json
    sha256: b02e13684330b50e6f5d5779264808d173c9ed99812872520b3460fcc59fc2a1
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/kimi.json
    sha256: 532bc56f30db5bf3c54252e5303742980d2485ec55586ec00a176d331a30aa49
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/glm.json
    sha256: f221acd030fef42f499e10941240dc986b0ca1487fa41fcce1216971fed9c5ad
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/BRIEF.md
    sha256: e4de13bcc0fd09017ca1b8cadca08be5ba63712e6c4fb69078af3e6818fe6826
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/review.md
    sha256: 3d719fc98e830932bb78c961825d4bda40ee01605d7e751fb177b70d6f271e04
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/FINDINGS.md
    sha256: a5715ddc7deeea8559cc7fe3a01df795d8ad3507fda6339ab329b362424cb65d
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close/dynamic-query-successor.json
    sha256: 316bb84b26b1ce0d0e3458b6754a7bfdb7bd647669ccc5579de8a49ece0a386f
  - path: src/gnd/export/pyrel_rules.py
    sha256: 2140303f9d83b0beeed074b5550e9307df2e0a6c50bde9ad0ed171a9a76d1f45
  - path: src/gnd/export/ossie_formulas.py
    sha256: 9f7c4d6f10a4bcb242709251f5f1da7bd2409878823835cb853622b8b167c93a
  - path: docs/runtimes/pyrel.md
    sha256: c622ee96a74897cec5330b42920b9ee094795584f454c9dc0c5247bdaafe27a8
  - path: .gnd-planning/milestones/pyrel-rules-coverage/001-plan-gate.md
    sha256: 8a6d0fe3763cee8ba5668922e0a9a134c52db59e902d0a2faf2038404226fc79
  - path: .gnd-planning/milestones/pyrel-rules-coverage/002-phase-RP2.md
    sha256: 1218345567781d02ad6cb4d09a2362f6d2436f8e53e6a0946d3bb2b5602847b5
  - path: .gnd-planning/milestones/pyrel-rules-coverage/003-phase-RP1.md
    sha256: 6ae343c76554290e99bbff0a3cbbcd1615c75e7233b72a3e456d4865e7b1618d
  - path: .gnd-planning/milestones/pyrel-rules-coverage/004-phase-RP3.md
    sha256: 9ebf68eb446056e38ed5d4eb0d0ee1cd5c15563269c2eace78358cd9b5507d6c
  - path: .gnd-planning/milestones/pyrel-rules-coverage/005-phase-RP4.md
    sha256: c03a19e798ed63c5fab3df92ce3b3dc762fbd8e7f1a24ca0d0c370287ac95ef7
  - path: .gnd-planning/milestones/pyrel-rules-coverage/006-phase-RP5.md
    sha256: 04fe6f4fc7d1197ad7943e0e333f32ed13ab1675b7c6b59a067915be7f9e36ca
---

# Claim

The pyrel-rules-coverage milestone closes at these bytes. Issue #214 items
2–4 are delivered in `gnd export pyrel --rules duckdb|lqp`:
- external uniqueness;
- anchored constraints listed as not checked;
- `Number`;
- value constraints scoped to a role.

Every packaged literature model of plan §1 exports, and on every listed
population the DuckDB program agrees with `gnd check`. Inputs and models
the programs cannot represent exactly are refused by name with exit 3; the
runtime page states each refusal. The plan's goal predicates hold
(`notes/close-results.md`). Plan r4 is amended in §11 (A1–A13); its
SHA-256 is now `004627d0098184027db692947b4ccb6f2f8cd5c2cc95ad02d3e8a56c142a31af`.

## Phase records

| Phase | Record | Commit |
|---|---|---|
| plan gate | `001-plan-gate.md` | `92cd5c9b` |
| RP2 | `002-phase-RP2.md` | `6e04fe7f` |
| RP1 | `003-phase-RP1.md` | `1350db9a` |
| RP3 | `004-phase-RP3.md` | `33bd03db` |
| RP4 | `005-phase-RP4.md` | `78b9cbb8` |
| RP5 | `006-phase-RP5.md` | `bba37de8` |

## Close review

Instrument: the full GND panel at xhigh, as the owner selected for plan and
close. It ran from a disposable worktree at `e99782fe` over the plan, the
results and the delta (`evidence/close-review/`).
- All six seats returned schema-valid responses; Codex and Gemini blocked,
  the other four asked for revision. The panel is advisory.
- Four seats agreed on one blocking concern: the LQP version's exit on an
  empty disconnected join. Codex raised a second: malformed populations
  escaped exit 3.
- All 17 concerns were checked against the code and dispositioned
  (`disposition.md`): 15 fixed, 2 accepted as residuals.
- The repairs were read by one independent reviewer (Codex through the
  review helper, `notes/reviews/close-repairs-r1/`). It found one more
  rounding route that predates the close (a float literal against an
  Integer value, now refused, A13) and two faults in the close's own text.
  All three are fixed.
- Rounds stop there under the convergence rule (2/3 self-inflicted). The
  final repair bytes have no further independent reader; the lanes above
  ran on them.

## Questions swept

All five open questions of plan §10 are resolved (plan §11, sweep). The
phase records carry no open question. Residuals accepted:
- RP3's r5 repair and RP5's last sentence had no second phase reader (the
  close panel read both).
- Whole-tree ruff stays red with the known 198 errors, recorded above.

## Close ruling

**Delegated approval (auto=true)**, 2026-11-22, under the owner's
`/process-milestone pyrel-rules-coverage auto` (2026-11-21), scope this
milestone's close. The delegation covers plan, spec and close rulings within
this milestone. This ruling is not the owner's reading of the artifacts.
- Ruled: the goal predicates hold on the evidence above. The plan
  amendments A1–A13 are accepted, the plan at SHA-256 `004627d0098184027db692947b4ccb6f2f8cd5c2cc95ad02d3e8a56c142a31af`. The
  residuals listed are accepted.
- Budget used: the selected panel (plan review two rounds, close one
  round), plus Codex phase reviews through the helper; no other paid call.
- Not covered by this ruling: merge, publication and any release, which
  stay with the owner.

## Boundary — what this close does NOT establish

- No RelationalAI engine ran. The LQP programs compile (oracle lane), but
  their enforcement on an engine is unverified.
- Agreement is with `gnd check` without an anchor sidecar.
- The programs are stricter than GND where stated (`close-results.md`,
  Boundaries).
- Nothing is merged or published: the work is on branch
  `claude/pyrel-rules-coverage`, submitted as a pull request for the
  owner's decision.
