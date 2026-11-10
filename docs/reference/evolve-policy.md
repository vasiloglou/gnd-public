# Additive evolve policy

`gnd evolve preview --policy additive` refuses a proposal that would make
facts already admitted under the current model uninterpretable, among the facts
it can see (see [what the preview carries](#what-the-preview-carries) and
[admitting a constraint on clean data](#admitting-a-constraint-on-clean-data)): a rename,
delete or change of an existing object type, fact type or role; a replaced
reference scheme; a new or stronger constraint on a fact type that has a
population. Without `--policy`, nothing changes: every preview and apply is
byte-identical to what it was before the option existed. For a worked round,
see [Grow a model by additions](../how-to/grow-a-model.md).

```bash
gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json --policy additive --populated orders
```

```bash
gnd evolve apply model.orm.yaml proposal.json --preview preview.json --workspace . --records records --policy additive --populated orders
```

## What the preview carries

Under the option the preview gains four fields: `policy`, `populated_args`
(the `--populated` ids), `populated` (the effective set: those ids plus every
fact type with `sample_population` rows, owned by a declared reference
population, or referenced by a `population` artifact in the proposal) and
`policy_issues`. Each issue names the operation's index and id, its locator
reference, the matrix cell that refused it, and a detail of ids and key names;
no constraint or sample value appears. A preview with issues is still written
to `--out`, so the refusal is reviewable, and the command exits 3.

The matrix, the closed strengthening list and the order of checks are
normative in the
[evolution contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/references/evolution-contract.md)
(section "Additive policy"); this page does not restate them.

## The guarantee's condition

`apply` must repeat the preview's `--policy` and `--populated`, and any
`--check-population` ([below](#admitting-a-constraint-on-clean-data)). It exits 3
when they differ from the reviewed preview's, in either direction, before
the retry branch and before it rebuilds the preview. It then rebuilds the preview with those options, so a
preview whose `policy_issues` were edited exits 11 like any other stale
preview, and the service re-runs the policy on the bytes it publishes rather
than reading the preview's list. A preview stripped of every policy field and
applied without `--policy` publishes as a policy-free preview: the guarantee
is the caller's to repeat.

## Admitting a constraint on clean data

A constraint the text reveals only after its fact type has data is refused by
the policy. With `--check-population FILE` the policy admits it when the
constraint is `proposed` and `deontic` and the population in `FILE` satisfies
it; the preview then records the file's digest and the operations it admitted.

```bash
gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json --policy additive --populated orders --check-population population.json
```

```bash
gnd evolve apply model.orm.yaml proposal.json --preview preview.json --workspace . --records records --policy additive --populated orders --check-population population.json
```

The conditions, the outcome words a refusal carries and the exits are normative
in the evolution contract (section "Additive policy", "Population check").
The admitted constraint stays advisory: the guarantee then holds relative to
the population you supplied. Several population files are composed into one
with `gnd compose` first.

## Source documents

A growth round of an unattended model can declare the document its new spans
cite with a `source-document` operation in a proposal of `schema_version` 3.
The policy admits an `add`; a `modify` (a changed label) is refused as
`source_document.modify` and a `delete` as `source_document.delete`. The
operation's rules are in the evolution contract (sections "Stable locators"
and "EvolutionOperation").

## Subtypes

The policy admits a new object type that declares `subtype_of` in the same
operation, and a new supertype. It does not admit pointing an existing
object type at a supertype: that adds `subtype_of` (and `inherits_reference`)
to an existing element, an `object_types.modify` outside the admitted keys
(`description` and `provenance.rationale`), refused whether or not any fact
type is populated. A consolidation that makes existing entity types kinds of
one another is therefore a reviewed proposal without `--policy additive`. The
[unattended growth procedure](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/references/unattended-growth.md)
describes when to run one.

## Exits

| Exit | When |
|---|---|
| 0 | `--policy additive` and every operation admitted |
| 3 | an operation refused by the policy (the preview is written); `--populated` or `--check-population` without `--policy`; a `--populated` id the model does not declare; a refused population file; apply's options differ from the preview's; the service's re-run at apply finds an issue |
| 11 | the reviewed preview differs from the one apply rebuilds, an edited issue list or a changed population file included |
| 66, 74 | the `--check-population` file is missing (66), or is a symlink, directory or otherwise not a readable regular file (74) |
| 18 | the operations gate, which runs before the policy |

The policy is a gate, not advice: it changes the exit. The same proposal
without `--policy` previews and applies as before.

## Shape report

`gnd evolve preview --shape-report` is advice that sits beside the policy.
The preview's `shape_matches` groups every fact type the proposal adds with
the existing fact types, and the other added ones, played by the same object
types, with their readings and how each entity role player is identified.
A match is a candidate, not a verdict: the report never changes an exit,
`breaking` or the blast radius, and `apply` takes no extra option.

```bash
gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json --shape-report
```

The signature rule and the field layout are normative in the evolution
contract (section "Shape report").
