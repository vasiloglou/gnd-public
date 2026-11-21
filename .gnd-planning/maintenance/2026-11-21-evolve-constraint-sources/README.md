# Evolve and the unattended-growth sources, planned 2026-11-21

From [issue #218](https://github.com/vasiloglou/gnd-public/issues/218). A
maintenance pass, not a milestone. Nothing is changed yet.

## The disagreement

`src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` (lines 94
and 289) tells a growth host to write a new constraint's source as `sample` for
row evidence and `common-sense` for library evidence, always `proposed` and
`deontic`. `gnd evolve` admits a new constraint only as `llm-inferred` /
`proposed` / `deontic` or `user-supplied` / `confirmed` (rule D-12,
`src/gnd/evolve/service.py`, the branch ending at the "new or changed
constraints must be" refusal). A proposal written as the document says is
refused. Confirmed at `0f39c392` on 2026-11-21.

## Ruling needed before the fix

| Choice | Effect |
|---|---|
| (a) Widen D-12 | `evolve` also admits `sample` and `common-sense` when `proposed` and `deontic`. The evidence basis stays in `source`, where `measure` and the provenance reports read it |
| (b) Change the document | The document says to write `llm-inferred` and keep the basis in `provenance.rationale_world_fact`. No code change |

Proposed: (a). The reporter's workaround is (b), and it hides the basis in
free text.

## Done when

- The chosen side is changed, and a test builds a proposal exactly as the
  document describes and runs it through `gnd evolve`.
- For (a): `sample` / `common-sense` with `alethic` or `confirmed` still
  refuses, and the D-12 statement in the evolve reference is updated.
- The affected lane (`tests/test_evolve_*.py`, `tests/test_unattended_*.py`)
  and the structure and inventory guards pass. The issue gets a reply and is closed after the merge.
