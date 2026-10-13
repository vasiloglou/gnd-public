---
name: start-milestone
description: Prepare or resume a GND development milestone plan, turning requirements and carryovers into phased deliverables, measurable gates and the first draft phase spec. Use when asked to start, plan or initialize a repository milestone. Does not execute phases or close a milestone.
---

# Start Milestone

Prepare a milestone for execution under this repository's development protocol.
This skill owns planning; [process-phase](../process-phase/SKILL.md) owns numbered
phase execution and its owner gates.

Adapted from `gnd-apps/.agents/skills/start-milestone` at source commit
`7e20d01024bf62d9c7779f42c43b1ef54a1f5fbd`. The target repository's planning,
approval, review and Git contracts replace the app-specific ones. This is a
source-owned development skill, not an installer-managed packaged skill.

## Resolve the milestone and scope

Accept `start-milestone pyrel-applications` or “plan the next milestone.” This is
a skill invocation, not a shell command. Resolve the named subject from the
request and existing plans. Ask only if ownership or scope remains ambiguous.
Do not infer a framework milestone from an unrelated app's roadmap.

All planning output belongs under `.gnd-planning/milestones/<milestone>/`.
Validate the resolved path stays inside the repository and is not a symlink to
another location. Existing milestones keep their canonical plan path and phase
IDs. A new plan normally lives at `notes/<milestone>-plan.md`, not a competing
`PLAN.md` or an app-style `.<app-directory>/` space.

Read before authoring:

- [AGENTS.md](../../../AGENTS.md) and applicable local instructions.
- [CONTRIBUTING.md](../../../CONTRIBUTING.md), the process-phase protocol and
  its relevant planning/approval/review references.
- `.gnd-planning/PROJECT.md`, the complete effective plan/roadmap if present,
  and the applicable open-question register.
- Prior plans, phase/close records and amendments assigning carryovers; relevant
  source, tests and docs for feasibility. Status summaries alone are insufficient.

If `.gnd-planning` is absent, report that prerequisite and offer the packaged
`gnd-new-project` workflow; do not silently invoke another skill or create an
alternative scaffold. In an existing project, a request to start a milestone
authorizes appending that milestone's planning artifacts. Preserve PROJECT.md,
other milestone records, installer links and unrelated user files.

For a domain-model successor, read the relevant `gnd coverage MODEL` census
before selecting goals, following `gnd-new-project`. For a framework milestone,
explain why an experiment-claim census does not settle runtime feature coverage.
Do not confuse this planning task with authoring or evolving an ORM model.

## Harvest, reconcile and partition

Build an obligations table citing source path and section for each deliverable,
constraint, dependency, cross-cutting gate and carried limitation. Distinguish
observed evidence, inherited claims and proposed targets.

Check readiness from records and evidence. Unresolved prerequisites may leave
dependent phases blocked; name what unblocks them. Inspect a completed milestone
as complete unless the user asks to reopen it. On resumption retain approvals,
phase IDs, records and evidence; amend the canonical plan with clear provenance
instead of resetting history or silently invalidating approvals.

Perform an implementability pass before declaring the plan ready:

- Can each input and upstream capability exist when its phase needs them?
- Can the selected tools meet dependency, isolation and public-interface rules?
- Do evaluation partitions, runtime lanes, tuning rules and budgets agree?
- Are outcomes, thresholds, refusals and comparison denominators measurable?
- Does every promised capability have a falsifiable end-to-end result?

Record conflicting clauses with source locations, a proposed resolution and the
required ruling. Do not rewrite approved gates or treat a proposal as accepted.
Continue unaffected planning while decisions remain pending. Preserve explicit
owner authorization or delegated approval for its named scope; never transfer
another milestone's delegation.

Partition work into stable phase IDs with coherent, testable outcomes. Each
implementation phase owns a spec, approval, implementation, focused tests,
independent review, refactoring review and record. Cross-cutting documentation,
graphics, packaging and integration requirements need named phase owners and
gates. Optional work cannot supply mandatory prerequisites. Milestone closure
has its own gate/record rather than pretending it is a feature phase.

## Write the planning artifacts

Preserve an existing plan's effective structure. For a new plan use the shape
consumed by process-phase, with a goal/status and completion predicates followed
by these sections:

| Section | Content |
|---|---|
| 0 | Binding design rules |
| 1 | Scope, sources and authority |
| 2 | Contract proposal and product behavior |
| 3 | Dependencies and artifact homes |
| 4 | Phases, deliverables, named criteria and inherited residuals |
| 5 | Documentation/skill/compatibility surfaces |
| 6 | Risks and required controls |
| 7 | Out-of-scope work |
| 8 | Execution, approval and review protocol |
| 9 | Per-phase verification story, expected results and affected consumers |
| 10 | Owner decisions and open questions |

Include the harvested obligation-to-phase/gate mapping, baseline, relevant
budgets and closure evidence requirements. Label unresolved exact commands as
unresolved rather than inventing executable gates. Distinguish proposed,
owner-approved and explicitly delegated rulings, with dates/scope/hashes for
actual approval. Planning authorship is not approval or publication authority.

Prepare detailed contracts only for the first ready phase, at
`notes/phase-<ID>-spec.md`, following the
[spec note contract](../process-phase/references/spec-note-contract.md) and
[standing rules](../process-phase/references/standing-rules.md). Authoring this
draft does not run process-phase or record its owner gate. If required decisions
or inputs are absent, retain a clearly blocked draft naming those gaps; do not
claim execution readiness. Later phases remain actionable outlines until their
prerequisites are known. Preserve an existing approved spec rather than replacing
it during planning.

A milestone-local README can link the canonical plan/spec, readiness, pending
decisions and next action. Do not add a global STATE.md, duplicate roadmap, empty
review/evidence records or implementation-started status merely because planning
files exist. Material execution records follow the packaged milestone record
contract when execution is explicitly selected.

## Verify and hand off

Check obligation ownership, acyclic dependencies, mandatory versus optional
prerequisites, phase counts and local links. Review the diff for unrelated edits
or credential/private-data inclusion. Planning uses authorized read-only evidence;
do not run paid tools, reserved test splits or native acceptance lanes merely to
fill a plan. Missing measurements remain missing evidence.

The repository retains its plan/close four-reviewer bar and bounded convergence
rules from
[process-phase review guidance](../process-phase/references/review-convergence.md).
Select a review instrument explicitly; importing this skill does not activate
the maintained panel or authorize reviewer subagents. Never claim a review
opinion over amended bytes that were not reviewed.

Report the canonical plan and first draft spec, phase count, readiness, decisions
and next action. Default `auto=false`; implementation follows the concrete spec's
owner gate. Existing explicit delegation remains effective within its scope.
Hand off to process-phase only when the user selects that execution workflow;
otherwise leave the reviewable planning artifacts. Contributions use a topic
branch and PR; merge, publication and certification retain their separate owner
authorization. This skill does not close milestones or change repository policy.
