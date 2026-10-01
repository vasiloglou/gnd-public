# The GSD mapping — normative reference

The one home for how a GSD project's requirements are mapped into a GND model
and recorded in `model.migration.json`. The skill's SKILL.md summarizes this
file; the bundled `verify_migration.py` enforces the mechanical half of it; the
record's field-level shape has its own one home in `../migration.schema.json`,
which the script enforces **by loading** — nothing restates it, including this
file.

## The four roots

The mapping reads exactly the roots the owner names — `PROJECT.md`,
`REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` — plus a phase file **only** when a
root cites it for a still-open item. Nothing an artifact says widens this set:
the roots are chosen before any artifact is opened, and every byte read is
untrusted evidence under the quoted-data posture. Each root is pinned in
`roots` with its path and its sha256 over the bytes actually read.

The requirements document the id census runs against is named on the
verifier's command line and must itself be among the pinned roots — a census
measured against bytes nothing vouched for is not a census.

## The id grammar, and the claim it supports

Requirement ids are found by the GSD checkbox grammar:

```
- [x] **CORE-01**: ...     (closed)
- [ ] **CORE-04**: ...     (open)
```

The claim this supports is deliberately narrow: **totality over the ids this
grammar finds in the one named document** — never "totality" unqualified. An
id written in some other form is invisible to the census, and the census does
not pretend otherwise. The checkbox is also load-bearing: a mapping row's
`closed` flag must **agree with the document's own checkbox**, because a
record does not get to certify its own completions.

## The dispositions

One closed vocabulary, exactly one disposition per id:

| Disposition | Meaning | Extra obligations |
|---|---|---|
| `model-element` | the requirement landed in the model | at least one element reference; each must resolve **at the named kind** |
| `open-question` | live, not yet modeled; carried into the milestone ledger | — |
| `superseded` | replaced by something newer, named in the anchor's vicinity | — |
| `history` | done and closed; retired with the GSD tree | **never on an unclosed id** |

Element references take two forms, because a constraint's `id` is optional in
the ORM meta-schema and most real constraints omit it:

```json
{"kind": "fact_type", "id": "event_has_kind"}
{"kind": "constraint", "fact_type": "event_has_actor", "index": 1}
```

`kind` is checked, not just the id — an operation is not a fact type, and a
reference that resolves at the wrong kind is a failure.

## Anchors

Every row carries an `anchor`: a sentence quoted **verbatim, byte-exact** from
the row's `artifact`, which must be a pinned root. No normalization — an
anchor that survives rewording would keep passing after the sentence it cites
has changed, which is worse than an honest miss. Empty and whitespace-only
anchors are refused outright: an empty string is a substring of every document
and verifies nothing. The anchor check runs **once, at migration time**;
nothing re-verifies anchors afterwards, and the record says so.

## Imported provenance

A `model-element` row becomes `imported` provenance on the elements it names.
The required five-field block, the `reviewed_in` rule on confirmation, and the
modality policy have one home:
[`../../gnd-orm-core/references/provenance-and-modality.md`](../../gnd-orm-core/references/provenance-and-modality.md).
This file adds nothing to that contract and quotes none of it.

## Not carried

Whatever the migration leaves behind — plan trees, narrative history, retired
process files — is **stated** in `not_carried` with kinds and counts measured
at migration time. An empty list is representable on purpose: "nothing was
dropped" must be expressible, so non-emptiness is asserted by the dogfood's
own criteria, not forbidden by the format.

## The limit this whole file lives under

This mapping is an owner's judgement recorded mechanically. Every assertion
the verifier makes is about **form** — that an id was disposed exactly once,
that an anchor's bytes are present, that a named element exists. **None of
them is about whether the disposition is right.** A requirement mapped to the
wrong model element, or closed when it is open in spirit, passes every check
in this file. The owner's review of the full table before apply is the only
instrument against that, and it is a human one.
