# Model-composition execution readiness

Date: 2026-11-09. Checkout: d2d6309b; topic branch:
`codex/model-composition`. This is a preparation note, not a phase-completion
record, spec approval, or close ruling.

## Authority

The current owner request, `process-milestone model-composition auto`,
delegates milestone plan/spec/close rulings under auto=true. It supersedes
historical auto=false defaults for this execution, without rewriting their
history. It does not select paid reviews, reviewer subagents, broad suites,
merge, publication or certification.

The approved plan's MD0 exception selects one Codex reviewer for the plan.
Its section 8 selects Codex for phase diffs. It does not extend MD0 to the
independent milestone close. The close instrument choice is pending with
the owner: one Codex reviewer under an explicit panel override, light panel,
or full panel. No reviewer has been invoked in this execution.

## Artifact verification

All milestone paths were checked: no symlink redirects in the planning
ancestors or milestone tree. Both retained plan/spec review snapshots match
the full SHA-256s stated in the reviewer prompts (r1 and r2).

| Current artifact | SHA-256 |
|---|---|
| notes/model-composition-plan.md | 775b5f16b81283cb5634124254c8ec6df8a53735192af946887db369dda1efe9 |
| notes/phase-MC1-spec.md | e48b12d8e8ede42360ffe21ac19e1eb519db2c52d1c55ca4ef9b402255fc3930 |
| 001-plan.md | 88f6d26287c7ef9ff8664f76c9c90ab837add8764aa018bad26b79edd79fecbb |
| evidence/plan-review-r1/codex-review.md | 9495ea155810bf935e0e121864ff3c85fef91b15974451dde509211811222d70 |
| evidence/plan-review-r2/codex-review.md | a210719fedd9ad241f3f9e8df840fcc6c15bd8dd9e776a1b52f8c91ecd2ad6cb |

The current plan differs from the historical approved digest, as its own
status explains: recorded rulings and amendment a1 followed approval.
The original exact r3 approval bytes are not separately retained here;
the current digest is not substituted for that historical identity.
The two review seats are the same reviewer in two rounds. Neither opinion
covers current r3 bytes. The convergence stop remains in force.

## Phase readiness

| Unit | Prerequisite | Approved spec | Completed criteria / evidence | Next action |
|---|---|---|---|---|
| MC1 | Approved plan, baseline controls | No; draft r3, D1-D8 open | None; no implementation or baseline test results | Finish spec sweep and selection ledger; delegated gate; baseline before production edits |
| MC4-draft | MC1 merged, per plan section 3 | Not prepared | None | Runnable early how-to and rendered owner checkpoint after MC1 |
| MC2 | MC1 loader, provenance, guards | Not prepared | None | Re-read each MC1 guard and rule support/refusal |
| MC3 | MC1 loader, provenance, guards | Not prepared | None | Specify evolve, re-pin and proposal writers |
| MC4 | MC2, MC3, owner reaction to MC4-draft | Not prepared; MD17 open | None | Finish docs/skills after prerequisites |
| Close | All mandatory phase gates, question sweep | Close instrument pending | None | Independent close review, exact-byte delegated ruling; merge remains separate |

## Verification selection requiring the owner

Plan section 9 and MC1 spec sections 6.8 and 8 require the full default
suite and tracked-file compatibility census on beast-3, including a baseline
at 459ca8d2 before MC1 production edits. The process-phase
`references/verification-selection.md` requires explicit current selection
of both broad and full default runs; old plan clauses and auto=true do not
select them. A question is pending to authorize these named baseline and
candidate runs, or select focused checks and amend the compatibility claim.
No full suite or broad lane has run.

A read-only `ssh -o BatchMode=yes -o ConnectTimeout=10 beast-3 'pwd'`
exited 0. Host access is available. The noninteractive checkout/tool location
probe still needs completion; its glob encountered zsh no-match handling.
No remote checkout was modified.

## Implementability sweep findings to settle before the MC1 spec gate

- `parse_model_document` is defined in `gnd.model` at line 298. The new
  `_includes.parse_included` must reuse it, while spec T46 prohibits the
  new leaf modules from importing `gnd.model`. Choose an acyclic shared
  parser home or an explicit injected parser seam, record the signatures,
  retain public identity aliases where moved, and cover source visitation.
- `ReferenceInputError` is defined in `gnd.model` at line 410. Moving
  `_relative` and `retained_root` to a leaf also needs an acyclic home for
  their exception; simply importing it from the initializer recreates a
  runtime cycle. Preserve exception identity, historical module spelling,
  and caller patch seams.
- Spec section 11 chooses prose but gives no reason for departing from the
  corpus-first default for serialized formats and refusal predicates.
  Complete that delegated instrument ruling, including its rationale, or
  author and commit the approved corpus red before implementation.
- Expand section 8 into the required verification-selection ledger, naming
  the precise affected-consumer nodes and architecture gate, input bounds
  and invalidation rules. Current route groups R22, R23, R25, R29 and runtime
  call sites need individual cases for each actual admission point.
- The size stop remains 750 source and 1,425 test lines. Auto does not waive
  this strict limit; measure it during implementation.

The component-index project hook has contradictory historical statements.
Following its later explicit location rule and the approved plan, consult
`dev/components/`. Six searches were run (confined paths, descriptors,
model validation/parsing and identifier collisions) with --no-cache.
The model.loading and model.validation entries were read against loader,
validator, documents, errors, schema and graph controls. No index-wide review
or unrelated index cleanup is selected.

## Boundaries

No production code, fixtures, normative format text, approved plan or spec
was changed. No spec approval, phase completion, test pass, review result,
PR, merge, issue closure, publication or certification is claimed.
Unrelated untracked user files remain untouched. Next work resumes within
the same milestone auto delegation after the missing test-scope selection;
close review selection can be resolved independently before close.

## Owner selections received, 2026-11-09

The owner selected one Codex CLI close reviewer with an explicit panel
override and authorized the named beast-3 baseline/candidate census and full
default suite. Record 002 binds those selections and the delegated MC1 spec
gate. The pending-choice statements above are historical preparation state.
