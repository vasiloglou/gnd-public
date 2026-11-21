# include-root-routes · close delta

What the milestone delivered differently from plan r4 as approved
(`001-plan-gate.md`), 2026-11-21. Read with `notes/include-root-routes-plan.md`
r5 and `notes/close-results.md`.

## Plan amendments at the close (plan §11, `(c1)`)

1. IR2's focused lane adds `tests/test_rf1_cli_pins.py`: a new top-level
   command changes the frozen CLI pins, which the r4 lane did not name.
2. IR2's homes add seven command inventories (RF5 command groups, parser
   and scope counts, the disclosure table and its counts, the CLI successor).
3. The PyRel page that states the exporter's limits is
   `docs/runtimes/pyrel.md`, not `docs/agents/export-and-review.md`.
4. IR3's homes add `src/gnd/export/include_roots.py`: `pyrel_runtime.py` is
   embedded in every default program and `emit.py` would close an import
   cycle with `pyrel_rules.py`.
5. §8 adds the component-index check before the PR.

## Spec-level changes recorded in the phases

- IR1: T9 was corrected to time the composition layer IR1 adds; the first
  version timed the whole route and measured the checker's pre-existing
  superlinear cost (IR1 spec i1). `bytes_declare_includes` was factored out
  of `guard_bytes` (i2).
- IR2: IR2-D4 was amended twice: the extract hint moved into
  `require_non_temporal`, then was scoped to `extract` after the review
  (F2).
- IR3: IR3-D2 was amended twice (i1, i3); the corpus's two imports moved
  with it, and no expected value changed.

## Behaviour that changed for existing inputs

- `gnd judgments check` on an include root: was exit 3 with
  `reason: "include:unsupported-route"` (outside the schema enum); now
  judged. Include refusals now use `reason: "binding"`.
- A version-5 document with `fact_type_constraints` and no `includes`: on
  the three opened routes the refusal is now `include:declaration`, where
  0.4.0 said `include:unsupported-route`.
- `gnd extract` on a temporal include root: same exit 3, the message adds
  that `gnd flatten` writes the flat model.
- `gnd export pyrel` on an include root: was exit 3
  (`include:unsupported-route`), now exported or refused for the reason its
  flat model gives.
- No output changed for a model without includes or attachments: IR1 T11
  and IR3 T6 compare whole bytes with the base.
- Added after the close review: an include path that cannot be encoded is
  refused `include:path` on every route (`compose`), where 0.4.0 reported
  the codec error (exit 3) and the PyRel export exited 70.

## Not delivered or not established

- No exported PyRel program was run; the `pyrel_oracle` lane did not run.
- The phase-review fixes were not re-reviewed.
- Open questions carried out of the milestone are listed in
  `notes/close-results.md`.
