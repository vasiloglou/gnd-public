---
milestone: guarded-rule-authoring
station: phase-GA3
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GA3
date: 2026-11-11
gates:
  - command: "UV_OFFLINE=1 pytest -q tests/test_ilp_amie_constants.py tests/test_ilp_amie.py tests/test_ih1_counting.py tests/test_ih2_ownref.py tests/test_ilp_learners.py tests/test_public_guarded_consequent_matrix.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py -p no:cacheprovider --tb=short"
    exit: 0
    output: "207 passed, 4 deselected in 24.35s"
  - command: "pytest -q tests/test_synth_guarded_cases.py -p no:cacheprovider --tb=short"
    exit: 0
    output: "14 passed in 1.39s"
  - command: "python3 scripts/components_index.py --no-cache changed --base fe22d057 --strict"
    exit: 0
    output: "changed against fe22d057 (fe22d05): 12 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
  - command: "Offline wheel installation with the synth extra, then evidence/GA3/installed-smoke.py"
    exit: 0
    output: "Installed smoke passed: GA1 scoped and isolated cases, GA2 proposal preview, GA3 typed AMIE import and preview."
slow_cadence:
  command: 'uv run pytest -q -m "live or evidence or census"'
  trigger: "explicit owner request or separately selected CI"
  reason: "the installed capture-format fixture covers this phase's authorized miner surface"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA3-spec.md
    sha256: f532d8baf61240f811ad783ee41039f566a7b069693197971c1fc639e4ccfd35
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA3-codex-review.md
    sha256: dbccd13b2298ee1137c6de579162bb97c58bf2701b9abb99e911b3a2d25d8395
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/dynamic-query-successor.json
    sha256: 744b0cb3a2112dff6fc808f77e3c7dffb29d6826237b58864bd29d1a7cf0f9fa
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke.json
    sha256: 6f2ca5564e70a51879d5a8ba079aee4dd1553f08a93c0485c670541c7a630688
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke.py
    sha256: 1642681946ac3e6e481764fbdb3f12cafaa3f8dc7581b912410dd0fbf3863a1a
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke-replay.md
    sha256: c3f080bc1b56f54c713be91ff5294bc36cdf0f18d881ebcf1eef4a8ce0f14755
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA3/rules.tsv
    sha256: 312ba41f4c7dc5457bfb7dc682a28ad52dff29977cf708d0eadbbbefe1f8b58d
  - path: tests/test_ilp_amie_constants.py
    sha256: ee8d673791ef06168329ebbb4b6ea9d36b72d58d032682597165cab052620c6a
---

# GA3 result

The red capture-format fixture at `fe22d057` reached the importer and
received exit 3 with `constant-atom`. The candidate accepts the issue's
`area:cli` rule, a fully ground rule covering all four literal positions,
and a ground Boolean/integer rule. Each produces one of one distinct
head pairs. The architecture rule's two distinct antecedent bindings
project to a single head pair. A wrong-category population produces
two checker witnesses for that one projected pair. The installed import
and both installed proposals passed evolve preview.

Incorrect spellings, reserved dollar strings, variable-only recursion,
repeated exact head atoms, false head pairs and wrong support all leave
the proposal absent. The 20-row per-rule control and 126-unit aggregate
control pass at their injected bounds and refuse one below. The raw
triple export matches its predecessor goldens. The old `m4` evidence
remains unchanged. Its typed literal now reaches the support mismatch
of seven holding pairs out of eight reported.

The [installed receipt](evidence/GA3/installed-smoke.json) binds the
offline wheel and all three workflows to runtime
`618141de9975c4ef30871a979532654267a15de6`.
The first base-wheel smoke exposed an unhandled missing optional Faker
dependency in guarded synth. The public regression reproduced the
traceback. The guarded route now returns exit 5 with the installation
hint. The replay installs the documented synth extra and its isolated
repeated-variable case has no collateral findings.

## Independent review and dispositions

Read-only Codex CLI reviewed the public GA3 runtime at `24851fbb`
and exited 0 with [no reproducible defect](notes/phase-GA3-codex-review.md).
One reviewer is one reviewer. It did not execute tests. It confirmed
one decoder in every slot, exact spelling, reserved-prefix refusal,
variable-only connectivity and recursion, literal-head admission,
distinct pair support and preflight work accounting. Support equality,
checker confirmation and the installed gates were verified locally.
Variable-only inputs retain their mapping and counting semantics within
the new aggregate recount limit.

## Refactoring review

No further refactor needed. One decoder in the existing AMIE adapter
owns the literal inverse. The export spelling remains the round-trip
authority. The import service retains mapping-before-count and proposal
admission. The optional dependency is handled at the guarded command
boundary.

## Boundary and open questions

The fixture uses AMIE's printed row format. Live miner execution remains
outside the selected milestone. Import uses the existing token alphabet
and deliberately bounded exact recount. General recursion, new quoting
syntax and automatic proposal acceptance require a separately approved
scope.
