# UG1: drafted issue dispositions (text for the owner to post)

Drafted 2026-11-07 from the UG1 acceptance replay (`tests/test_unattended_model_growth_acceptance.py`,
phase record `002-phase-UG1.md`). **Nothing here has been posted.** UG1 closes and comments on
no issue; whether and when to post, and whether to close, is the owner's. The texts name no
downstream application. Test names are those of the replay file unless another file is named.

## #74 (unattended, source-grounded mode)

> The acceptance replay (three growth rounds over one model, driven through `gnd validate
> --document`, `gnd evolve preview/apply`) confirms on main: every added fact and constraint
> carries a span; `confirmed` and `user-supplied`/`explicit` are refused (`semantic:unattended-u2`,
> `-u3`); the header must name no reviewer and at least one document (`-u1`); a span naming an
> undeclared document is refused (`-u7`); a tampered excerpt is caught when its document is
> supplied (`unattended:excerpt-mismatch`, rounds 1 to 3). Documented deviation, pinned: a
> `common-sense` constraint may cite a library entry instead of a span.
>
> Open, with owners in the milestone plan: a span whose document is not supplied to `validate` is
> not re-hashed (exit 0), and a round cannot declare its own new document through `evolve`
> (exit 3 "declared operations do not equal the canonical candidate model"; declaring it in the
> model first works). Both are pinned by tests as current behavior and are addressed in phase UG3.

## #75 (additions-only policy on `evolve preview`)

> The replay confirms through the CLI that `--policy additive` refuses an object-type rename,
> a fact-type rename (populated and unpopulated), object-type and fact-type deletes, a subtype
> link set on an existing type, and a new constraint on a populated fact type or spanning one,
> each naming its cell (`object_types.rename`, `fact_types.delete`, `object_types.modify`,
> `constraint.populated.add`, ...) and operation index in the preview, which is still written.
> `apply` re-runs the policy and does not publish a refused preview, and refuses mismatched
> `--policy`/`--populated` options (exit 3). Controls show the same changes are admitted without
> the flag or on a fact type the proposal adds. Note for users: a rename or delete preview is
> `breaking`, so `apply` asks for the blast-radius digest on stdin (exit 11 on EOF).
>
> No open item in this issue's scope.

## #76 (duplicate-shape detection)

> The replay confirms the structural report: a fact type added in a later round that restates the
> signature of an existing one is reported with that fact type named (`existing`), a first-round
> fact type has `existing == []`, and a shape match leaves the preview exit at 0 (advice, not a
> refusal) with `apply` rebuilding the report.
>
> Open: what the host does with a match (merge, rename, keep) is the host's, and its documentation
> is phase UG4.

## #104 (document-by-document procedure for CSDP steps 3 to 7)

> Items 1 and 2: met for output shape only. The replay hand-builds the elements, so it shows the
> output is admissible (`proposed`, `deontic`, cited, value type `Date`, uniqueness and mandatory
> constraints, a consolidation round adding a subtype), not that the procedure produces it; the
> procedure's own guard is `tests/test_unattended_growth_guidance.py`. Items 3 and 4 (the checks
> table, the one reply shape) are prose, inspected, with no executable check beyond that guard.
> Item 5, first option (constraints travel with their fact type): met. Item 5, second option
> (admit a clean-population constraint over a populated fact type): open; the replay shows the
> refusal today (`constraint.populated.add`) and is the case phase UG2 must turn into an admission
> for a clean population.
