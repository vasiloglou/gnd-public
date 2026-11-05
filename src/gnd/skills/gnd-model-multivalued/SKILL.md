---
name: gnd-model-multivalued
description: Decides how to model the multi-valued groups that the `gnd discover --families fact-type` family counts but does not propose, from one type-evidence file and the model only, and writes the `shapes` judgements file `gnd discover --shape-judgements` reads back. A variant of the `rai-orm-from-schema` dialect's schema-to-ORM conventions, it reads an attribute with several values per entity as a junction table, a many-to-many fact type with a uniqueness spanning both roles. Use when asked to "model the multi-valued attributes", "judge the multi_valued groups", "should this attribute be many-to-many", or to hand the fact-type family a shape verdict. It never reads the population, never writes a value the disclosure mode hides, and never applies a proposal. Not for groups that may duplicate an existing fact type (gnd-judge-fact-types), for authoring or changing the model (gnd-model-evolve), for importing a RAI model (`gnd import rai-orm`), or for computing the evidence (`gnd discover --type-evidence`).
---

# Model multi-valued induced attributes

The fact-type family of `gnd discover` groups generic rows ("an item has an
attribute with a value") by attribute. A group in which some entity has
several distinct values is counted `multi_valued` and not proposed, because
the single-role uniqueness an induced binary sits on would fail. Tags, phone
numbers and authors are such attributes, and they are legitimate. This skill
decides, group by group, whether each one is a many-to-many fact type, and
writes that down for the CLI to check and render. The CLI never chooses a
verdict; you do, and review at `gnd evolve preview` can still overturn it.

The evidence format and the judgements format have one home each: the
[Type evidence and Type judgements](https://github.com/vasiloglou/gnd-public/blob/main/docs/reference/discover.md#type-judgements)
reference, and the vendored schemas
[`type-evidence.schema.json`](../gnd-orm-core/references/type-evidence.schema.json)
and [`type-judgements.schema.json`](../gnd-orm-core/references/type-judgements.schema.json).
Link them; do not restate their rules.

## The convention this skill borrows

The `rai-orm-from-schema` dialect turns a relational schema into ORM. Its
convention for a junction table, whose rows pair two keys and in which
neither key alone is unique, is one many-to-many fact type with a uniqueness
spanning both roles. A generic attribute whose entities hold several values
is the same shape: each row pairs an entity with a value, and only the pair
is unique. This skill applies that convention to the evidence of one
attribute. It imports nothing: `gnd import rai-orm` is unchanged and is not
part of this workflow.

The spanning uniqueness is defined in
[Internal uniqueness](../gnd-orm-core/references/constraint-reference.md#internal-uniqueness-uc),
which you link and do not copy. It says each (entity, value) pair is
recorded once. It states nothing functional: an entity may hold any number
of values.

## Inputs, and the population rule

You need two files: the model (`model.orm.yaml`) and one evidence file that
`gnd discover MODEL POPULATION --families fact-type --type-evidence EVIDENCE`
wrote for it.

**Never open, list, search or ask for the population**, even when it sits in
the same directory. Everything a judgement may use is in the evidence:
counts, opaque row ids, digests, candidate readings and overlaps. If the
user offers attribute names or values, you may weigh them, but never write
them into the judgements file. The CLI refuses (exit 3) free text that names
a value the disclosure mode hides, and that check catches exact text only;
your own rule not to quote values is the main control.

## Procedure

1. **Refuse before judging.** Stop, write nothing and tell the user when:
   - the evidence's `format` is not `gnd-type-evidence/1`;
   - its `model_sha256` is not the SHA-256 of the model file you were given
     (compute it with `shasum -a 256` or `sha256sum`);
   - its `truncated_groups` is above 0: the evidence left groups out, and the
     CLI refuses judgements over it.
2. **List the eligible groups:** exactly those with status `multi_valued`, in
   evidence order. If there are none, say so and write nothing. Groups with
   status `proposed`, `shape_match` or `over_budget` need a `duplicates`
   file from [gnd-judge-fact-types](../gnd-judge-fact-types/SKILL.md).
3. **Decide each multi-valued group** by the rules below, in order. A group
   they cannot decide goes to the user as a question that names its id, its
   counts and its candidates' readings. **Write nothing until every
   multi-valued group has a verdict.**
4. **Write the file** where the user says (default
   `shapes.judgements.json` beside the evidence; never over an existing
   file), with:
   - `format`: `gnd-type-judgements/1`; `kind`: `shapes`;
   - `evidence_sha256`: the SHA-256 of the evidence file's raw bytes, from
     `shasum -a 256` or `sha256sum`, never of a re-serialized copy;
   - `judge`: `skill` is `gnd-model-multivalued`, `agent` names you or your
     model, with no value in it;
   - `verdicts`: one per multi-valued group, in evidence order, each with
     `group`, `generic`, `verdict` (`many-to-many` or `skip`; there is no
     `of`) and a `rationale` of one or two sentences citing group ids, fact
     type ids, words from the model's readings and which rule decided.

   When `show_values` is false, put no number standing on its own (a count,
   a share, a version) in `agent` or a `rationale`: a hidden value can equal
   it, and the CLI refuses free text that names one. Say "every entity",
   "half the items" or "one item" instead, and name the agent without its
   version.

5. **Hand off.** Give the user the next commands, with the same model,
   population, `--min-support` and disclosure setting that made the evidence:

```sh
gnd discover MODEL POPULATION --families fact-type --type-evidence-in EVIDENCE --shape-judgements JUDGEMENTS --out proposal.json --report report.json --actor ACTOR --requested-at TIMESTAMP
gnd evolve preview MODEL proposal.json --workspace WORKSPACE --records RECORDS --out preview.json --policy additive
```

   Exit 0 renders the verdicts: a `many-to-many` group is proposed as a
   binary fact type with a uniqueness over both roles, whose support is
   distinct pairs over rows and whose counterexamples are the rows that
   repeat a pair; a `skip` is counted in `skipped.judged_skip`. If the run
   also has groups for `gnd-judge-fact-types`, pass its `duplicates` file
   with `--duplicate-judgements` in the same command. Exit 3 means a verdict
   or the binding was refused; read the message, fix the judgements file,
   and never edit the evidence. A refusal that names `judge.agent` or a
   verdict's rationale means that text equals a hidden value: reword it
   without the word or number that matched. If a refusal names `judge.skill`,
   stop and tell the user: only the CLI's scan can change that. If the data
   or the model changed since the evidence was written, the binding refuses:
   make a new evidence file and judge again.

## Decision rules

For each multi-valued group, look at its candidates. Its distinct pairs are
`rows` minus `exact_repeats`.

- **S1 — already induced.** A candidate whose `origin.generic` is the
  group's `generic` and whose `origin.same_attribute` is true was induced
  from this very attribute: the verdict is `skip`, naming that fact type.
  The CLI refuses `many-to-many` there. Read that fact type's uniqueness in
  the model. When that fact type's uniqueness covers the entity role alone,
  it was induced as single-valued and the data now breaks it: still `skip`,
  and tell the user the shape changed, so either the population is
  corrected or that uniqueness is changed through
  [gnd-model-evolve](../gnd-model-evolve/SKILL.md).
- **S2 — already held.** Otherwise, a candidate whose `overlap.pairs` is at
  least 90% of the distinct pairs already holds this attribute's facts: the
  verdict is `skip`, naming it. A shapes file has no `duplicate` verdict.
- **S3 — junction table.** Otherwise, when the evidence's `truncated` is 0,
  no candidate's `overlap.pairs` is above 0, no `null` overlap stops S3 (see
  below), and at least one entity in ten
  has several values (`multi.entities` times ten is at least `support`): the
  verdict is `many-to-many`. Rows that repeat a pair become the uniqueness's
  counterexamples; say so in the rationale without counting them.
- **S4 — ask.** Anything else: a partial pair overlap, candidates left out
  by truncation, a `null` overlap that stops S3, or fewer than one entity in ten with several values, which
  may be entry errors rather than a shape. Ask the user, and record the
  answer as the verdict: `many-to-many`, or `skip`. When the user says the
  extra values are errors, the verdict is `skip`, and tell them to correct
  the population and make new evidence: a shapes file cannot declare an
  attribute single-valued.

A `null` pair overlap stops S3 when the candidate's other role is redacted in
the model: redaction hides the pairs, and the candidate may hold them all.
Otherwise a `null` overlap does not stop S3: the candidate is not a binary
whose other role has the value's kind, so it cannot hold these pairs. `signature_equal` is
false for every candidate of a multi-valued group and says nothing. When the
evidence's `show_values` is true, the attribute value may inform the
judgement, but it still does not go into the file.

## What this skill never does

It writes only its judgements file. It never edits the model, the evidence or
a proposal, never runs `gnd evolve apply` and never applies a proposal:
admission is the user's reviewed step through
[gnd-model-evolve](../gnd-model-evolve/SKILL.md). The verdicts are inputs; each
rendered constraint stays induced, proposed and deontic (see
[provenance and modality](../gnd-orm-core/references/provenance-and-modality.md)).

A session worth citing is recorded by the driving agent under the
[milestone-record contract](../gnd-orm-core/references/milestone-record-format.md),
staging the judgements file by explicit path, only on the user's go-ahead.
This skill never touches git, and `gnd` never reads or writes `.gnd-planning/`.
