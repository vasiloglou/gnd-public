# ORM: the executable ontology

GND starts from one artifact: a conceptual model of your domain, written in
**Object-Role Modeling (ORM 2)**. It is an ontology in the practical sense: the
things your application talks about, the facts that relate them, and the rules
those facts must or should obey. It is also *executable*. GND checks agent output
against it, generates synthetic data and code from it, and exports it to other
engines.

ORM is Terry Halpin's fact-based conceptual modeling method. (It has nothing to do
with object-relational mappers.) GND uses it because it suits checking agent output:

- **Everything is an elementary fact.** There are no attributes, only roles that
  objects play in fact types. That makes every rule about a *combination* of facts
  explicit and checkable.
- **Every element reads back as a sentence.** A domain expert can confirm "Each Book
  has exactly one primary genre" without reading YAML.
- **Constraints have a modality.** *Alethic* rules (must) decide acceptance; *deontic*
  rules (should) produce warnings.
- **It is a small, well-studied notation** with decades of tooling and literature,
  so the model is a reviewable artifact rather than a prompt.

## From sentences to facts

Suppose an application recommends books. You want to ask: **does this output include
a book the reader already read?** That question needs a rule and facts, and GND keeps
both explicit.

| Term | Meaning | BookRec example | In `model.orm.yaml` |
|---|---|---|---|
| Object type | A kind of thing (entity) or value | User, Book, Genre | `object_types` |
| Fact type | A relationship with named roles | User rated Book | `fact_types` |
| Population | The facts being checked | ada rated `read` | a population file's `facts` |
| Constraint | A condition the facts must or should satisfy | Recommended and rated pairs must not overlap | `constraints` |
| Derivation | A rule defining additional facts | A book is eligible when preferred, unread and allowed | `derivation_rule` |
| Provenance | Why a rule is present | The requirement sentence that motivated it | `provenance.user_quote` |

You do not need a database: models and populations are ordinary YAML and JSON files.
Halpin's design procedure is to verbalize example facts first, then group them into
fact types, then add constraints by asking questions about populations. The
`gnd-model-from-text` skill walks you through exactly that dialogue
([model a domain by dialogue](agents/model-from-text.md)).

## The model is an ORM 2 model

Each diagram below uses standard ORM 2 notation. Beside it is the corresponding part
of the BookRec model you open in [chapter 1](bookrec/01-model.md).

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d1-fact-type.svg"
</div>
<div markdown>

```yaml
object_types:
  - {id: user, kind: entity,
     reference: {mode: popular, value_type: user_id}}
  - {id: book, kind: entity,
     reference: {mode: popular, value_type: book_id}}
fact_types:
  - id: user_rated_book
    reading: "{User} rated {Book}"
    roles: [{object_type: user, role_name: user},
            {object_type: book, role_name: book}]
```

<p class="caption"><strong>Object types and a fact type.</strong> User and Book are entity types (soft rectangles) identified by an id. "User rated Book" is a binary fact type with one role box per participant.</p>
</div>
</div>

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d3-uniqueness-mandatory.svg"
</div>
<div markdown>

```yaml
- id: book_has_genre
  reading: "{Book} has primary genre {Genre}"
  constraints:
    - {type: uniqueness, roles: [book],
       modality: alethic}
    - {type: mandatory, role: book,
       modality: alethic}
```

<p class="caption"><strong>Uniqueness and mandatory.</strong> Genre is a value type (dashed). The bar over the Book role means at most one primary genre; the dot where the line meets Book means at least one. Together: exactly one.</p>
</div>
</div>

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d2-exclusion.svg"
</div>
<div markdown>

```yaml
id: unread_only
type: guarded
modality: alethic
antecedent:
  - fact_type: recommendation
    bind: {user: "$u", book: "$b"}
consequent:
  absence:
    fact_type: user_rated_book
    bind: {user: "$u", book: "$b"}
```

<p class="caption"><strong>Exclusion.</strong> The circled cross says no (user, book) pair is both recommended and rated. BookRec writes the same rule as a guarded constraint, which lets a rule join several facts; a violation names the offending binding, for example <code>{$u: ada, $b: read}</code>.</p>
</div>
</div>

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d4-modality.svg"
</div>
<div markdown>

```yaml
- id: age_appropriate      # alethic: must
  type: guarded
  modality: alethic
- id: preferred_genre      # deontic: should
  type: guarded
  modality: deontic
```

<p class="caption"><strong>Must versus should.</strong> The same kind of rule with a different modality. A violated alethic constraint fails the check; a violated deontic constraint produces a warning and the output can still be accepted.</p>
</div>
</div>

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d5-derived.svg"
</div>
<div markdown>

```yaml
- id: book_is_eligible
  reading: "{Book} is eligible for {User}"
  derivation: derived
  derivation_rule:
    body:   [user_prefers_genre($u, $g),
             book_has_genre($b, $g)]
    negate: [book_is_blocked_for($b, $u),
             user_rated_book($u, $b)]
```

<p class="caption"><strong>Derived fact type.</strong> The asterisk marks a fact type computed by a rule rather than supplied (shown here in shorthand). Negation is stratified, and an unknown input yields <em>cannot decide</em>, never a guess. GND compares any supplied claims with the derived result (<a href="bookrec/06-evolution.md">chapter 6</a>).</p>
</div>
</div>

<div class="orm-pair" markdown>
<div class="orm-pair__figure">
--8<-- "docs/assets/orm-d6-operation.svg"
</div>
<div markdown>

```yaml
operations:
  - id: approve_expense
    parameters: [expense, approver]
    preconditions:
      - id: pre_draft    # only a draft
        require: [expense_has_status($expense, "draft")]
    effects:
      - retract: expense_has_status($expense, _)
      - assert:  expense_has_status($expense, "approved")
      - assert:  expense_approved_by($expense, $approver)
    frame: {modality: alethic}
```

<p class="caption"><strong>Operations (a GND extension to ORM 2).</strong> An operation declares preconditions and effects; the frame says nothing else may change. GND can then check a plan, meaning a walk of operations, and not only a state (shown in shorthand; see <a href="agents/plans.md">checking an agent's plan</a>).</p>
</div>
</div>

## Hard rules and advice answer different questions

A hard, **alethic** constraint decides whether an output conforms. A violated hard
constraint makes an otherwise well-formed check fail. A **deontic** constraint records
advice or a policy warning: the output can still be accepted with a warning. This is
the difference between "never recommend an already-read book" and "prefer the reader's
favorite genre."

Choose that interpretation explicitly during modeling. The words "must" and "should"
in a prompt do not remove the need to review the generated model.
[BookRec chapter 2](bookrec/02-facts.md) makes the distinction concrete.

## Validate, check, and walk

`gnd validate` asks whether the model itself is well-formed and supported. `gnd check`
asks whether supplied facts satisfy the model. With `--pre` and `--steps` it checks a
plan: each operation's preconditions, every intermediate state, and the frame. A check
reports one of five bands:

| Band | Meaning |
|---|---|
| 0 | pass |
| 1 | an alethic constraint is violated |
| 2 | vacuous: the population is inadequate rather than violating |
| 3 | ill-formed input: the check never ran |
| 4 | indeterminate: GND could not decide, and says so instead of guessing |

An invalid input or an unsupported case is different from a genuine rule violation.
Read the report and the [command-specific exit meanings](reference/formats.md) rather
than treating every nonzero status as a failed business rule.

A checker needs a declared scope. A complete list of submitted expenses and a partial
excerpt from a receipt are different inputs. Admission, source anchors, reference
populations and unresolved facts help represent particular boundaries; they are not an
automatic guarantee that every real-world fact was supplied.

## ORM is the intermediate representation

<figure class="wide-figure">
--8<-- "docs/assets/orm-d7-intermediate-representation.svg"
</figure>

Requirements text, an existing codebase, a reviewed change or an imported ORM model all
become one `model.orm.yaml`. Every other artifact is derived from it or checked against
it:

- **the verifier:** `gnd check`, `gnd verify` and transition walks evaluate the model's
  constraints directly;
- **synthetic data:** `gnd synth` generates conforming, boundary and violating
  populations, and `gnd measure` scores the checker against them;
- **code:** `gnd codegen` emits the model-derived half of a Python project and
  `gnd conformance` detects drift;
- **plain language:** `gnd verbalize` turns models and populations into sentences;
- **change:** `gnd diff` and `gnd evolve` compare and publish model versions;
- **other engines:** `gnd export` writes Soufflé, Lean and PyRel artifacts and
  replayable witnesses.

## Where the developer and agent fit

![Generated tools and authored application logic have distinct owners.](assets/project-boundary.svg){ .mechanism }

1. Describe the requirements and review an agent-authored model.
2. Validate it and inspect small populations, including intentional mistakes.
3. Generate a Python project and write the application logic in its extension files.
4. Check the produced facts or plans before deciding to publish or act on them.
5. Change the model explicitly when requirements change, then check conformance.

GND supplies the model, the checker and structured workflows. A developer or coding
agent supplies domain understanding and application behavior. Generated scaffolding
does not invent a recommender, storage backend or user interface.

An output can be legal yet incomplete: "every recommended book is eligible" does not
say "every eligible book is recommended." BookRec's final chapter adds a derivation and
a completeness rule to illustrate the difference. Likewise, a valid expense state does
not by itself prove the operation that produced it was authorized; that is what
[transition checks](guides/data-and-transitions.md) are for.

## Read more

- [ORM Foundation](https://www.orm.net/): Terry Halpin's ORM resources
- [ORM 2 graphical notation](https://www.orm.net/pdf/ORM2.pdf) and the
  [ORM white paper](https://www.orm.net/pdf/ORMwhitePaper.pdf)
- [Object-role modeling](https://en.wikipedia.org/wiki/Object-role_modeling) on Wikipedia
- [NORMA](https://github.com/ormsolutions/NORMA), the reference ORM 2 diagramming tool
  for Visual Studio
- GND's own ORM reference library:
  [the Halpin posture](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/halpin-posture.md),
  [constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md),
  and [verbalization patterns](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md)

<p class="caption">Credits: GND's ORM modeling skills are adapted from RelationalAI's open-source <a href="https://github.com/RelationalAI/rai-agent-skills">rai-agent-skills</a> (Apache-2.0).</p>
