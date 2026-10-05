# Public launch — r3 planning amendment

**Effective direction: 2026-10-03. Implementation paused.** This amendment
records the owner's corrected scope and requested planning update. Updating these
documents does not restart execution or authorize publication.

## Purpose and precedence

The public repository must support ordinary development with useful regression
tests. The owner states that this repository contains no private data. Earlier
labels such as “retained-private” describe migration bookkeeping, not a finding
of confidentiality and not a reason by themselves to exclude a regression test.

This amendment supersedes conflicting sequencing, exhaustive test-accounting,
and intermediate-evidence preservation requirements in the
[original plan](public-launch-manifesto-and-plan.md),
[r2 amendments](public-launch-plan-r2-amendments.md), and Phase 3 specifications
and continuation notes. Those documents remain historical records. Their prior
“active” or delegated-continuation statements do not authorize resumed work.
Unrelated package, behavior, and publication requirements remain in effect.

## Phase status and remaining order

Original phase numbers are preserved; completed work is not renumbered.

| Phase | Current disposition | Remaining role |
| --- | --- | --- |
| 0 — Scope and provenance | Complete | Revisit only a concrete new gap or changed decision. |
| 1 — Public repository bootstrap | Complete | Keep its completion record; do not repeat bootstrap. |
| 2 — Runtime and package migration | Complete | Keep its completion record; later changes still need focused checks. |
| 3 — Regression coverage and acceptance | Incomplete, paused | Finish after code migration and package preparation. |
| 4 — Release candidate and first-user experience | Preparation next, not started by this amendment | Prepare code, workflows, documentation and packaging before final Phase 3 acceptance; sign off the candidate afterward. |
| 5 — Publish and launch | Pending | Publish only after acceptance and the applicable owner authorization. |
| 6 — Public development transition | Separately activated | Remains outside the launch gate. |
| 7 — Source retirement | Explicit owner trigger required | Remains outside the launch gate. |

The remaining execution order is **Phase 4 preparation → Phase 3 final regression
acceptance → Phase 4 candidate sign-off → Phase 5 publication**. Phase 4
preparation may begin before Phase 3 closes. Candidate sign-off closes Phase 4;
it is not another round of implementation. Phases 6 and 7 retain their separate
activation rules. Ordinary public-repository development need not wait for Phase 6.

Phase 2's completed package migration is not a claim that every later change has
already passed release validation. Preserve its historical results, then check
actual deltas in the final prepared package.

## Prepare the code and package first

Complete remaining runtime or workflow adaptations, packaged resources,
dependencies, examples, documentation, build configuration and release CI.
Remove the temporary source-checkout bootstrap so contributors can work from the
public repository alone. Make the supported release profiles explicit.

During this work, use focused tests for changed behavior and downstream contracts,
plus build/import smoke checks when relevant. Defer comprehensive test selection,
full-suite acceptance and final clean-install/CI validation until the code and
package are ready. Do not schedule certification or recertification without an
explicit owner request for a particular subject and scope.

## Finish the regression suite against the prepared package

Review tests by behavior family and record concise decisions: keep, consolidate,
retire with a reason, or retain as an optional dependency/provider/native test.
Keep unique assertions that protect supported behavior. Consolidation must retain
that protection; retirement needs a concrete reason such as obsolete behavior or
true duplication. Do not weaken assertions, silently skip failures, or change
expected values merely to get a passing run. Explain any changed expectation in
terms of the intended current behavior.

Existing mappings may help locate coverage, but completing a disposition for
every historical definition is no longer a release gate. Old counts measure the
previous bookkeeping process, not passing tests or percentage release completion.
The earlier “retained-private” group needs a coverage-based review before any
useful regression protection is omitted.

Retain useful existing code and test work pending ordinary diff review. This
amendment neither discards it nor declares it accepted. Separate optional tests
from the default contributor suite and report what was actually executed.

Acceptance means a developer can clone the public repository, install it, run
the selected regression suite and continue development without the source
checkout. Verify supported behavior and packaged resources through the final
clean-install and CI checks. Resolve genuine failures or explicitly document
any owner-accepted scope limitation; do not conceal unresolved failures in a
completion claim.

## Proportionate evidence and candidate sign-off

Use ordinary Git history, a concise test-family selection record and normal test
results. Do not require per-batch before/after archives, byte-reconstructible
migration packets, lossless compression, or additional preservation machinery to
finish Phase 3. The source Phase 3 evidence-size cap must not force test retirement
or archival work. This does not waive distinct product, package, or public
repository size constraints; raise a concrete conflict if one remains.

Existing archival files are left in place by this planning update. Any later
cleanup must first check their consumers and preserve needed work through normal
version control or a recovery snapshot. No history rewrite or blanket deletion
is authorized here.

After Phase 3 acceptance, sign off the exact tested candidate. Preserve r2's
build-once/promotion rule and its separate sdist-built-wheel check. A rebuild or
subsequent code/package change requires the affected validation to be repeated.
Then proceed to the separately authorized publication step. No push, visibility
change, release, ownership transfer or source retirement follows from this
planning edit.
