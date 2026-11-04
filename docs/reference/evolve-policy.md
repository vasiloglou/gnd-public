# Additive evolve policy

`gnd evolve preview --policy additive` refuses a proposal that would make
facts already admitted under the current model uninterpretable: a rename,
delete or change of an existing object type, fact type or role; a replaced
reference scheme; a new or stronger constraint on a fact type that has a
population. Without `--policy`, nothing changes: every preview and apply is
byte-identical to what it was before the option existed.

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

`apply` must repeat the preview's `--policy` and `--populated`. It exits 3
when they differ from the reviewed preview's, in either direction, before
the retry branch and before it rebuilds the preview. It then rebuilds the preview with those options, so a
preview whose `policy_issues` were edited exits 11 like any other stale
preview, and the service re-runs the policy on the bytes it publishes rather
than reading the preview's list. A preview stripped of every policy field and
applied without `--policy` publishes as a policy-free preview: the guarantee
is the caller's to repeat.

## Exits

| Exit | When |
|---|---|
| 0 | `--policy additive` and every operation admitted |
| 3 | an operation refused by the policy (the preview is written); `--populated` without `--policy`; a `--populated` id the model does not declare; apply's options differ from the preview's; the service's re-run at apply finds an issue |
| 11 | the reviewed preview differs from the one apply rebuilds, an edited issue list included |
| 18 | the operations gate, which runs before the policy |

The policy is a gate, not advice: it changes the exit. The same proposal
without `--policy` previews and applies as before.
