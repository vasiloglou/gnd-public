# Evolve and the unattended-growth sources, planned 2026-11-21

From [issue #218](https://github.com/vasiloglou/gnd-public/issues/218). A
maintenance pass, not a milestone. Nothing is changed yet. It is independent
of the roadmap milestones: none of them waits for its ruling.

## The disagreement

`src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` (lines 94
and 289) tells a growth host to write a new constraint's source as `sample` for
row evidence and `common-sense` for library evidence, always `proposed` and
`deontic`. `gnd evolve` admits a new constraint as `llm-inferred` /
`proposed` / `deontic`, `user-supplied` / `confirmed`, or `induced` /
`proposed` / `deontic`, and refuses every other source (rule D-12). D-12's one
home is [Evolve admission (D-12)](../../../src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md#evolve-admission-d-12)
in `provenance-and-modality.md` (line 209); `_enforce_d12` in
`src/gnd/evolve/service.py` implements it, and
`src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` (lines
279-280) restates it. A proposal written as the growth document says is
refused at the "new or changed constraints must be" refusal. Confirmed at
`0f39c392` on 2026-11-21.

## Ruling needed before the fix

| Choice | Effect |
|---|---|
| (a) Widen D-12 | `evolve` also admits `sample` and `common-sense` when `proposed` and `deontic`. The evidence basis stays in `source`, where `measure` and the provenance reports read it |
| (b) Change the document | The document says to write `llm-inferred` and keep the basis in `provenance.rationale_world_fact`. No code change |

Proposed: (a). The reporter's workaround is (b), and it hides the basis in
free text.

## Done when

- The chosen side is changed, and a test builds a proposal exactly as the
  growth document describes and runs it through `gnd evolve`.
- For (a): `sample` / `common-sense` with `alethic` or `confirmed` still
  refuses. The D-12 section of `provenance-and-modality.md` lists the new
  combinations, and the restatement in `evolution-contract.md` (lines 279-280)
  says the same.
- The affected lane (`tests/test_evolve_*.py`, `tests/test_unattended_*.py`)
  and the structure and inventory guards pass. The issue gets a reply and is
  closed after the merge.
