---
name: gnd-solve
description: A process guide for the full nine-station GND loop. The `gnd solve` harness owns the ordered validate, synth, codegen, exp-run, and conformance command walk; this skill points to that command's help while retaining the routes and stable station numbers for opening a project, authoring or recovering a model, implementing and shipping a slice, evolving the model, and advisory review. Use when asked to "solve a problem with GND end to end", "walk the GND loop", or "which GND skill comes next". The skill invokes no sibling skill and emits no claim; the harness runs five `gnd` subcommands whose claims remain separate.
---

# GND Solve

## Summary

This is the navigational wrapper around the GND loop. The full spine remains
visible here because committed milestone records resolve their integer
`station:` values through these numbers:

- Station 0 — open the project
- Station 1 — author or recover the model; validation then joins the harness
- Station 2 — ground expectations (`synth` when synthetic grounding applies)
- Station 3 — generate the project (`codegen`)
- Station 3b — implement, test, and ship the slice
- Station 4 — run a data-driven session (`exp-run`)
- Station 5 — check conformance
- Station 6 — evolve an existing model
- Station 7 — request advisory review

The command-owned policy for Stations 1's validation half, 2, 3, 4, and 5 —
their order, argv, accepted exits, timeouts, gating, and logging — has one home
in code. Read it with `gnd solve --help`.

This skill keeps the routing edges, not a second copy of that procedure.

## The two lanes

The normative lane and record rules live in
[`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md).

- **Fast lane — default:** Stations 1 → 2 → 3 → 3b. Model the current slice,
  ground its expectations, generate, then implement, test, smoke, and ship.
  Focused hand-authored fixtures may be enough; routine work needs no station
  record or station commit.
- **Evidence lane — risk-triggered:** Station 4 for convergence or
  agent-behavior uncertainty; Station 5 when model/generated-surface drift is
  plausible; Station 6 when an existing model must change; Station 7 for a
  destructive, ambiguous, security-sensitive, or high-blast-radius decision.
  Material events get milestone records.

At a skill handoff, name the emitted claim and its evidence, name the sibling
that owns the next station, and stop for the user's go-ahead. The `gnd solve`
harness is different: it composes five CLI subcommands, not sibling skills, and
its blocking or `--auto` gates are command behavior documented by `--help`.
The skill auto-invokes no sibling; the harness does not merge their claims.
This skill emits no claim and commits nothing itself.

For ORM YAML, constraint, provenance, or population-format questions, use the
references-only [`../gnd-orm-core/SKILL.md`](../gnd-orm-core/SKILL.md).

## The walk

### Station 0 — open the project

Run only when `.gnd-planning/` is absent. Owner:
[`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md). It scaffolds the
planning directory, its `PROJECT.md`, and the first milestone, then commits that
one-time scaffold. If `.gnd-planning/` exists, skip Station 0.

**Gate:** name the milestone directory opened, then stop before Station 1.

### Station 1 — author or recover the model; validation splits

- **Greenfield:** [`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md)
  owns CSDP authoring and emits `model.orm.yaml` plus its verbalization. Once
  authored, validation is the harness's first station; its procedure is in
  `gnd solve --help`.
- **Brownfield:** [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md)
  owns one-time static recovery and emits the model, verbalization, and
  `model.recovery.json`. Its distinct close gate remains outside the harness:
  `uv run gnd recovery verify BUNDLE_ROOT model.recovery.json`.

The halves part company because recovery verification has a different payload,
while the harness requires a model that is already valid.

**Gate:** for brownfield work, report the recovery verifier's exit and
`ok: true`, then enter the harness only after recovery has closed.

### Station 2 — ground the contract expectations

Owner: the grounding section of
[`../gnd-dev-session/SKILL.md`](../gnd-dev-session/SKILL.md). It decides when a
focused hand-authored fixture is enough and when synthetic grounding is earned.
The harness-owned `synth` command procedure is in `gnd solve --help`.

### Station 3 — generate the agent project

Owner: [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md). The harness-owned
`codegen` command procedure is in `gnd solve --help`; the sibling skill remains
the authority for derived-versus-extension ownership and regeneration limits.

### Station 3b — implement, test, and ship the slice

Owner: you, in the extension half `gnd-codegen` owns and in the consuming
repository's ordinary code. There is no `gnd` entry command.

1. Implement one thin, user-visible slice in extension-owned files.
2. Run the consuming repository's dependency and build checks.
3. Add and run focused tests proportionate to the changed surface.
4. Smoke-test the runnable path end to end.
5. Ship through the ordinary release process and collect user feedback.

Feedback routes an extension defect directly back here. A wrong or incomplete
existing model routes to Station 6. A derived-surface defect routes through
Station 6 when the model must change, then deliberately back through Station 3;
never hand-edit a derived file. A genuinely separate new model routes to
Station 1, not evolution.

**Gate:** name the slice shipped or the failing check verbatim, then stop. The
fast lane normally continues with the next slice; evidence stations run only
when their trigger fires.

### Station 4 — run the data-driven session

Trigger: genuine convergence or agent-behavior uncertainty not answered by the
slice's focused tests and smoke run. Owner:
[`../gnd-dev-session/SKILL.md`](../gnd-dev-session/SKILL.md). The harness-owned
`exp-run` command procedure is in `gnd solve --help`; contract authoring,
outcome interpretation, and experiment closure remain with the sibling skill.

### Station 5 — conformance

Trigger: the model or generated surface may have drifted, or a codegen
experiment needs close evidence. Owner:
[`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md). The harness-owned
command procedure is in `gnd solve --help`. A drift finding is information, not
permission to regenerate; the user chooses Station 6 or deliberate regeneration.

### Station 6 — evolve the model

Trigger: feedback, a session outcome, or a drift finding says an existing model
must change. Owner:
[`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md). Preview the
staged transaction, obtain acceptance, then apply it through that skill. It
emits separate proposal, blast-radius, model-CAS, conformance-envelope, and
immutable change-record claims. After an accepted evolution, deliberately
return to Station 2 or 3. A proposal may also come from `gnd discover`, which
suggests induced, advisory constraints observed in one population, or from
`gnd import ilp-rules`, which brings an ILP learner's rules back as induced,
advisory constraints, or from `gnd import mined-rules`, which brings back a rule
miner's rules that hold on a population; review each here like any other.

Entry commands: `uv run gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json`; after acceptance, `uv run gnd evolve apply model.orm.yaml proposal.json --preview preview.json --workspace . --records records --format json`.

**Gate:** name the records directory and the apply command's aggregate exit
verbatim, then stop.

### Station 7 — review

Trigger: a destructive, ambiguous, security-sensitive, or high-blast-radius
decision needs independent readers. Owner:
[`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md). Require a clean
worktree or disposable clone, then let that skill run and finalize its bounded
panel. It emits an advisory report plus the immutable run directory; failures
and dissent remain, and nothing is edited or fixed.

Entry commands: `uv run gnd review panel review-request.json --out panel-run/`, then `uv run gnd review finalize panel-run/ synthesis.json --out PANEL-REVIEW.md`.

**Gate:** report the panel quorum and band and the finalize exit verbatim. The
user decides whether any recommendation re-enters the loop.

## Limits and report

The skill never auto-invokes a sibling, regenerates, applies a fix, merges claim
families, or turns a completed walk into an acceptance claim. `gnd solve` does
execute five commands, but each station's exit and evidence remain that
station's claim, while the harness exit reports only its own control plane.

Report the station reached and lane used; for each completed non-harness
station, give its gate and evidence pointer. For the command-owned five, cite
the walk log and the exact station exits it recorded. Name the next station and
owner without summarizing the lifecycle as a pass or fail.

For explicitly requested finite derivation proofs or bounded standalone Souffle
program export/native execution or finite Lean definitions with explicit unproved
obligations, the owner may select
[gnd-export](../gnd-export/SKILL.md). This route never runs that sibling;
proof replay stays separate from this workflow's claim.
