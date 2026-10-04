# Turn requirements into a model

A GND model makes domain rules explicit enough for a person to review and for
the runtime to check. Start with a concrete decision your application makes:
“May this reader receive this recommendation?” is a better first slice than
“Model everything about a library.”

The [BookRec tutorial](../bookrec/01-model.md) builds a complete example.
This guide explains the modeling choices you will make in another domain.

## Write facts before rules

Write five or ten specific facts in ordinary language. For example:

> Alice is 17 years old. Alice has read *The River*. *The Mountain* requires a
> reader age of 18. Alice is recommended *The Mountain*.

Separate independently changeable facts. A reader's age, a book's age limit,
reading history, and a recommendation are four fact types. Give each role a
type and a name. Decide how entities are identified: a stable reader ID can
identify a reader even when the display name changes.

Then ask what makes this particular recommendation unacceptable. A guarded
rule can join a reader's age, the book's age limit, and the recommendation and
require the age comparison to hold. A different rule can require the absence
of the same pair from reading history.

## Choose the smallest rule that says what you mean

| Requirement | Useful construct | Question to settle |
|---|---|---|
| A reader has at most one age | Uniqueness over the reader role | Which roles determine which other roles? |
| Every known reader has an age | Mandatory role | What is the explicit set of known readers? |
| A status is one of draft/approved/paid | Value enumeration | Is this a closed vocabulary? |
| Every recommended pair is eligible | Subset | Is eligibility already represented by a relation? |
| Eligible and blocked pairs cannot overlap | Exclusion | Which role sequence identifies the same pair? |
| Every eligible pair must be returned | Equality or the reverse subset too | Are you requiring completeness or only validity? |
| A recommendation implies an age condition | Guarded constraint | Which facts bind every variable? |
| A dependency graph must be acyclic | Appropriate ring constraint | Is the fact type the edge relation or its closure? |

Model each requirement once at the clearest level. A checker can reject an
ineligible recommendation without enforcing that *all* eligible books were
returned; that second obligation must be stated separately. Likewise, at most
one age does not imply that an age exists. Uniqueness and mandatory answer
different questions.

## Distinguish hard rules from preferences

Every constraint carries `source`, `status`, `modality`, and provenance.
`alethic` means a violated constraint produces a hard `fail`. `deontic` means
the violation produces advisory `warning` feedback. A genre preference may be
advisory while an age restriction is hard. A warning is still useful to show
in the application even when its final exit band is zero.

In guided authoring, unconfirmed inferred proposals remain proposals. Review
them with the domain owner before making them hard requirements. Record why a
rule exists and the wording that justified it; this makes a later change
reviewable. When evolving a model, unchanged constraints retain their original
provenance.

## Validate, then check contrasting populations

Contextual commands below assume you have authored the named model and two
population files using the [format reference](../reference/formats.md):

```sh
gnd validate model.orm.yaml --format json
gnd check model.orm.yaml valid.pop.json --format json
gnd check model.orm.yaml invalid.pop.json --format json
```

Validation checks the model itself. Population checking asks whether the
provided facts satisfy its rules. For each important rule, construct one
population that exercises and satisfies it, and another that fails for the
reason you intend. Read `constraint_ref` and the finding, not just the exit.
An empty population is often vacuous rather than a useful passing example.

## Review what remains uncheckable

A free-text requirement can be preserved as a textual constraint, but the
deterministic checker reports it `unchecked`; it does not interpret arbitrary
prose. Subtype partitions need observable membership evidence. Current-time
operands are not a clock service. These limits should influence how you write
the model and the application, rather than being discovered at deployment.

For exact syntax, examples, and family-specific limits, use the
[constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md)
and [provenance and modality policy](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md).
For agent assistance, follow [explicit skill handoffs](agent-skills.md).
