# PyRel applications plan review — reviewer four

Reviewed: 2026-10-13. Instrument: independently delegated local reviewer;
no paid calls. Subject: `pyrel-applications-plan.md`, entire draft r1.

Reviewed SHA-256:
`a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`.

Scope: product/tutorial completeness, the six graphics and their source grounding,
documentation rendering and installed resources, governance consistency and
implementation feasibility. No other reviewer's notes were read.

## Verdict and findings

**Approve for the plan gate within this review scope. No actionable plan findings.**
This is an advisory planning opinion, not owner acceptance, implementation
authorization, a native-runtime result or a milestone close.

The plan defines both functioning applications, all named model variants,
independent publication checking, repair and evolution as mandatory outcomes
(`pyrel-applications-plan.md:38-59`, `:98-127`, `:131-134`). It explicitly assigns
the missing interfaces, grammar, coverage and runtime measurements to the
owner-gated PA0 spec (`:156-173`). Their absence from this draft is therefore
not an unowned implementation gap.

## Evidence checked

- Inspected all five shipped model variants as data, including fact-local
  constraints and derivation bodies. The baseline/strict BookRec modality change
  and the complete model's preferred-genre eligibility derivation support the
  planned distinction between legal advisory recommendations and the complete
  eligible set. In particular, `src/gnd/examples/bookrec/complete.orm.yaml:199-235`
  joins matching genres and excludes blocked/rated pairs; `:301-363` includes
  hard genre fit and `all_eligible`. The plan's before/after graphic requirement
  at `:267` preserves that distinction instead of presenting one universal set.
- BookRec's existing tutorial already has a concrete warning-bearing candidate:
  Ada receives `cosmos` and `map`, with a visible advisory warning
  (`docs/bookrec/04-application.md:25-48`). Its shipped seed contains two readers,
  five catalogue books, rated pairs and the adult/minor facts. These are adequate
  source material for the three specified BookRec graphics; new native outcome
  receipts remain required, rather than borrowing these GND outcomes as PyRel
  evidence.
- Expenses have three synthetic submissions of 60, 800 and 1,400 EUR
  (`docs/expense/01-model.md:61-67`), category caps and chain limits in the
  baseline/currency models, and invalid meal/chain and missing-currency fixtures.
  The existing evolution tutorial explicitly keeps EUR-only semantics and
  distinguishes missing coverage from missing values
  (`docs/expense/03-evolution.md:3-7`, `:114-149`). The three planned expense
  graphics at plan `:268-270` use those same mechanisms and prohibit invented
  currency conversion.
- Every graphic has a named teaching question, source-to-figure mapping,
  model-rule/outcome verification, editable sources, accessible equivalent and
  visual acceptance requirements (plan `:263-301`). Desktop/mobile and supported
  theme review are explicit; a successful build cannot substitute for them.
  The site currently configures both default and slate palettes in
  `zensical.toml`; choosing SVG or Mermaid according to actual rendering is a
  reasonable PA5 spec decision, not a rendering assumption.
- Existing application boundaries inspect staged files before publication
  (`src/gnd/examples/bookrec/extension/bookrec/cli.py:23-35`;
  `src/gnd/examples/expense/extension.py:64-83`). The plan requires equivalent
  independent native checking and refusal preservation, rather than treating
  correct filtering or report arithmetic as acceptance.
- The isolated runtime pins are real (`tutorials/runtimes/pyproject.toml:4-8`),
  and installed readers already have a packaged-runtime setup precedent
  (`docs/runtimes/scenario.md:45`). Plan `:142-147`, `:284-287` and `:305-319`
  assign runtime copies, runner support and installed-path verification.
- Governance remains consistent with the supplied AGENTS agreements: topic branch
  and PR, separate merge authority, no paid review implied, no inherited
  delegation, separate phase owner gates and no certification/release claim
  (plan `:86-94`, `:354-376`). The plan's statement that it does not itself invoke
  delegation does not contradict the owner's separate selection of this local
  review. The seven-phase sequence is acyclic and each mandated product outcome
  has a phase and acceptance owner.

## Phase-spec follow-through, already covered by the plan

These are implementation watchpoints, not additional findings or conditions on
this plan verdict:

- `tools/check_installed_docs.py:48-51` currently copies docs/tools from the
  checkout, and `:66-67` invokes the default offline lane. Reusing that command
  unchanged would not prove PA6 native execution or wheel-sourced graphic
  inclusion. PA6 must implement the selected native lane and artifact-origin
  checks demanded by `PA6-C1`/`PA6-C3`.
- The current expense resource-copy snippet copies files only
  (`docs/expense/01-model.md:48-54`). If PA5 chooses nested graphic or runtime
  resources, update that copy flow and test the actual installed reader path.
  PA0's resource-consumer inventory and PA5/PA6 installed-asset criteria already
  own this work; flat resource placement is also possible.
- Capture actual native accepted/warning/refusal outputs before authoring the
  source mappings. The existing synthetic facts are usable teaching sources,
  but they do not demonstrate the future PyRel acceptance contract.

## Scope limits

Read-only inspection and model-data inventory only; no application changes,
plan edits, native execution, site build, screenshots, wheel build, external API
calls or runtime compatibility verification. Existing documentation assertions
are cited as inspected source, not independently passed controls. This review
does not establish the guarded compiler's semantic correctness, security against
all inputs, universal ORM equivalence or implementation performance. Re-review
is needed for material amended plan bytes.
