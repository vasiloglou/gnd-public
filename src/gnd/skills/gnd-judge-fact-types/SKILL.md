---
name: gnd-judge-fact-types
description: Judges whether the groups the `gnd discover --families fact-type` family formed duplicate fact types the model already has, from one type-evidence file and the model only, and writes the `duplicates` judgements file `gnd discover --duplicate-judgements` reads back. Use when asked to "judge the induced fact types", "decide the shape matches", "which induced attributes are duplicates", or to hand the fact-type family a semantic duplicate verdict. It never reads the population, never writes a value the disclosure mode hides, and never applies a proposal. Not for multi-valued groups (they need a `shapes` file), for authoring or changing the model (gnd-model-evolve), or for computing the evidence (`gnd discover --type-evidence`).
---

# Judge induced fact types for duplicates

The fact-type family of `gnd discover` groups generic rows ("an item has an
attribute with a value") by attribute and compares each group with the fact
types the model already has only by role players. A signature says two fact
types *could* hold the same facts; it cannot say they *mean* the same thing.
This skill makes that call, group by group, and writes it down for the CLI to
check and render. The CLI never chooses a verdict; you do, and review at
`gnd evolve preview` can still overturn it.

The evidence format and the judgements format have one home each: the
[Type evidence and Type judgements](https://github.com/vasiloglou/gnd-public/blob/main/docs/reference/discover.md#type-judgements)
reference, and the vendored schemas
[`type-evidence.schema.json`](../gnd-orm-core/references/type-evidence.schema.json)
and [`type-judgements.schema.json`](../gnd-orm-core/references/type-judgements.schema.json).
Link them; do not restate their rules.

## Inputs, and the population rule

You need two files: the model (`model.orm.yaml`) and one evidence file that
`gnd discover MODEL POPULATION --families fact-type --type-evidence EVIDENCE`
wrote for it.

**Never open, list, search or ask for the population**, even when it sits in
the same directory. Everything a judgement may use is in the evidence: counts,
opaque row ids, digests, candidate readings and overlaps. If the user offers
attribute names or values, you may weigh them, but never write them into the
judgements file. The CLI refuses (exit 3) a rationale that names a value the
disclosure mode hides, and that check catches exact text only; your own rule
not to quote values is the main control.

## Procedure

1. **Refuse before judging.** Stop, write nothing and tell the user when:
   - the evidence's `format` is not `gnd-type-evidence/1`;
   - its `model_sha256` is not the SHA-256 of the model file you were given
     (compute it with `shasum -a 256` or `sha256sum`);
   - its `truncated_groups` is above 0: the evidence left groups out, and the
     CLI refuses judgements over it.
2. **List the eligible groups:** exactly those with status `proposed`,
   `shape_match` or `over_budget`, in evidence order. If there are none, say
   so and write nothing. Groups with status `multi_valued` are not this
   skill's: they need a `shapes` judgements file from
   [gnd-model-multivalued](../gnd-model-multivalued/SKILL.md). Other
   statuses take no verdict.
3. **Decide each eligible group** by the rules below, in order. A group they
   cannot decide goes to the user as a question that names its id, its counts
   and its candidates' readings. **No file is written until every eligible
   group has a verdict.**
4. **Write the file** where the user says (default
   `duplicates.judgements.json` beside the evidence; never over an existing
   file), with:
   - `format`: `gnd-type-judgements/1`; `kind`: `duplicates`;
   - `evidence_sha256`: the SHA-256 of the evidence file's raw bytes, from
     `shasum -a 256` or `sha256sum`, never of a re-serialized copy;
   - `judge`: `skill` is `gnd-judge-fact-types`, `agent` names you or your
     model, with no value in it;
   - `verdicts`: one per eligible group, in evidence order, each with
     `group`, `generic`, `verdict` (`distinct` or `duplicate`), `of` only on a
     duplicate (a candidate's `fact_type`), and a `rationale` of one or two
     sentences citing group ids, fact type ids, words from the model's
     readings and which rule decided.

   When the evidence's `show_values` is false, write no number standing on
   its own (a count, a percentage, a version) in `agent` or a `rationale`:
   you cannot see the hidden values, a short one can equal a count, and the
   CLI refuses free text that names one. Say "every pair", "half its pairs"
   or "no shared pairs" instead, and name the agent without its version.

5. **Hand off.** Give the user the next commands, with the same model,
   population, `--min-support` and disclosure setting that made the evidence:

```sh
gnd discover MODEL POPULATION --families fact-type --type-evidence-in EVIDENCE --duplicate-judgements JUDGEMENTS --out proposal.json --report report.json --actor ACTOR --requested-at TIMESTAMP
gnd evolve preview MODEL proposal.json --workspace WORKSPACE --records RECORDS --out preview.json --policy additive
```

   Exit 0 renders the verdicts: a `distinct` group is proposed even when its
   signature matches; a `duplicate` is listed under `shape_matches` against
   `of`. Exit 3 means a verdict or the binding was refused; read the message,
   fix the judgements file, and never edit the evidence. A refusal that names
   `judge.agent` or a verdict's rationale means that text equals a hidden
   value: reword it without the word or number that matched. If a refusal
   names `judge.skill`, stop and tell the user: the skill's own name equals a
   population value, and only the CLI's scan can change that. If the data or
   the model changed since the evidence was written, the binding refuses:
   make a new evidence file and judge again.

## Decision rules

For each eligible group, look at its candidates:

- **R1 — same origin.** A candidate whose `origin.generic` is the group's
  `generic` and whose `origin.same_attribute` is true was induced from this
  very attribute: the verdict is `duplicate` of it. The CLI refuses
  `distinct` there. An origin of another generic fact type is not R1.
- **R2 — shared facts.** Otherwise, a candidate whose `overlap.pairs` is at
  least 90% of the group's distinct pairs (`rows` minus `exact_repeats`)
  already holds this attribute's facts: `duplicate` of it. When two qualify,
  take the higher overlap, then the earlier candidate.
- **R3 — no shared facts.** Otherwise, when at least one candidate has a
  non-null `overlap.pairs` and every such candidate has 0: `distinct`. Say in
  the rationale that the verdict rests on the absence of shared facts; a
  synonym attribute recorded for different entities would also pass here, and
  review is where that is caught. When the evidence's `truncated` is above 0,
  R3 does not apply: the last groups may have lost candidates to the size
  cap, so their absence proves nothing; ask instead.
- **R4 — ask.** Anything else (a partial pair overlap, or only `null`
  overlaps so that no candidate is comparable): ask the user, and record the
  answer as the verdict.

An equal role-player signature (`signature_equal`) is evidence neither way.
Every group of one generic fact type has the same role players, so it says
nothing about meaning. Readings may inform a question to the user. When the
evidence's `show_values` is true, the attribute value may inform the judgement,
but it still does not go into the file.

## What this skill never does

It writes only its judgements file. It never edits the model, the evidence or
a proposal, never runs `gnd evolve apply` and never applies a proposal:
admission is the user's reviewed step through
[gnd-model-evolve](../gnd-model-evolve/SKILL.md). The verdicts are inputs; each
rendered constraint stays induced, proposed and deontic (see
[provenance and modality](../gnd-orm-core/references/provenance-and-modality.md)).

A judgement session worth citing is recorded by the driving agent under the
[milestone-record contract](../gnd-orm-core/references/milestone-record-format.md),
staging the judgements file by explicit path, only on the user's go-ahead.
This skill never touches git, and `gnd` never reads or writes `.gnd-planning/`.
