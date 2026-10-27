# Differential report contract (`gnd-diff/1`, `gnd-diff/2`)

`diff.schema.json` is the closed output shape. This file defines the meaning of its
rows. A diff compares two validated models only when their vocabulary projections
have the same digest. The full model digests remain separate because constraints
and derivation rules can differ while the vocabulary is shared.

An `entailment` row reads from `from_model` to `to_model`. `implies` means the
left constraint syntactically entails the right under one of the bounded
catalogue rules. It is not a proof that one entire model is stronger. The
catalogue covers uniqueness role sets, mandatory identity, exact
subset/exclusion structure, typed value allowed sets and intervals, and guarded
rules with identical alpha-normalized antecedents and comparable consequents.
Any other pair is `undecided`, never a counterexample. Pairs are formed within
one family and compatible subject and sorted by family, direction and references.

Every `population` row names exact bytes by SHA-256 and labels their origin.
Both models load those bytes independently. A `checked` side carries the actual
version-10 check band, constraint verdicts and derivation verdicts; a
`not_comparable` side carries a refusal rule without a fabricated band. The
`a_to_b` and `b_to_a` arrays are separate because a population may distinguish
the models in one direction only. A gap names a target failing or unresolved
obligation and retains the checker's offending value where one exists. A
complete fact binding may have a sentence rendered by the existing inert
witness renderer; partial bindings have a null sentence.

`derivations` lists concrete witnessed tuples whose memberships differ. Each
side has status `in`, `out` or `unknown`; an opaque or unavailable extension is
never treated as `out`. The relative outcome is `unresolved` if either side is
unknown, `unsound` when an out-side claimed the tuple, and `incomplete` when an
unclaimed tuple is present only in the other model's computed extension.
Possible patterns are tested only against concrete witnessed tuples, not
expanded into invented facts.

Synthesis attempts a conforming population from each source model and
constraint-derived boundary cases from both models. A boundary is retained as
a separator only after independent checks show source band 0 and target band 1
or 4. Unsupported synthesis or an unreachable boundary is recorded in
`not_derivable`. No model, population or existing check report is rewritten.

API and CLI reports project sensitive witnesses after evaluation. Applied
projection removes role-bearing offending facts, derived tuples and witness
sentences when either model declares an effective redacted role; explicit
`--unredacted` permits the original values. Neither projection changes row
membership, direction, verdict, band or the literal `assurance: none`.
Invalid models, vocabularies and population documents are refusals rather than
gap evidence. Reports are observations over listed populations and syntactic
rules, not certification or recertification of either model.

## Description annotations (`gnd-diff/2`)

Object-type descriptions are excluded from the vocabulary digest, so two models
that differ only in a description are compared. Such a diff exits as it would
for identical models. When at least one object type's `description` differs
under canonical JSON equality, extras included, the report uses
`schema_version: "gnd-diff/2"` and adds `annotations`. That is one entry per such
object type, in model order, with `object_type` and the whole `before` and
`after` objects, `null` where absent. Annotations carry no population data, and
redaction passes them through unchanged. A report without annotations is
byte-identical to `gnd-diff/1`. The schema requires `annotations`, with at least
one entry, exactly when the version is `gnd-diff/2`.

The text format ends with one block per annotation: `ANNOTATION <object type>
description`, then `before` and `after` lines holding each object as compact,
ASCII-escaped canonical JSON, so description text cannot start a line of its
own. A diff without annotations prints the same text as before.
