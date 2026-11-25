# Release notes and milestones

Version 0.4.0, published on 2026-11-17, is the latest release; 0.3.0, 0.2.0 and
0.1.0 came before it. Version 0.5.0 is prepared for PyPI. Releases follow the
[release procedure](releasing.md). Changes on `main` after a release are listed
in an `Unreleased:` section until the next one.

## 0.5.0 (prepared, not published)

### Ossie relational files

- **Tables beside the ontology.** `gnd export ossie` now writes five files.
  The two new ones are `OUT.semantic_model.<fmt>`, the tables that hold the
  model's facts, and `OUT.mapping.<fmt>`, which says where each concept and
  relationship is stored. The ontology, sidecar and loss report keep their
  bytes. A file already at either new path stops the run with exit
  11 (`EXIT_COLLISION`) and nothing is written. `--ontology-only` keeps the
  three-file run. The size bound covers the two new files as well, so a
  large model whose three files fitted can now stop with `ossie:output-size`;
  add `--ontology-only` or raise `--max-output-bytes`. A model that yields no
  table writes three files and prints a note.
- **Your own tables.** `--physical-binding FILE` describes delivered tables
  in place of the generated ones. The file follows the packaged schema
  `gnd-physical-binding/1`. A binding the model contradicts is refused with
  a `binding:` rule id and exit 3. Together with `--ontology-only` it is a
  usage error, exit 64 (`EXIT_USAGE`). A fact that a table holds only
  through a surrogate key cannot be bound; it is listed as `unbound`.
- **Larger files.** `--max-output-bytes N` on `gnd export ossie` and
  `--max-input-bytes N` on `gnd import ossie` replace the 10 MiB bound for
  one run. N is a whole number of bytes, from 1 byte to 256 MiB. Any other
  value is a usage error, exit 64 (`EXIT_USAGE`). The model file itself
  stays capped at 10 MiB.
- **The relational mapping as a library.** `gnd.rmap.map_model(model)`
  returns the tables the export generates, by Halpin's relational mapping
  procedure, with a list of what it could not place and the reason for each.
  `gnd.rmap.dispositions(model, schema)` gives one row for every fact type
  and constraint. The
  [mapping rules](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#relational-mapping-rmap)
  are in the representation reference.
- **What the new files disclose.** The semantic model and the mapping carry
  the model's object-type, fact-type and role ids as table and column
  names, or the names your binding file gives. The
  [disclosure page](reference/disclosure.md) lists them.
- **Where to read more.** [Ossie interchange in GND](explanation/ossie.md)
  and [Describe your delivered tables](how-to/describe-delivered-tables-for-ossie.md).

### PyRel rules programs for literature-style models

`gnd export pyrel --rules duckdb` and `--rules lqp` now export models that
use external uniqueness, anchored rules, `Number` values or value
constraints scoped to a role. 0.4.0 refused the first three by name, as "a
later phase of the rules programs" or "not supported by the rules programs
yet" ([#214](https://github.com/vasiloglou/gnd-public/issues/214)). The
[PyRel runtime page](runtimes/pyrel.md) is the reference for what the
programs check, what they list as not checked and what they refuse.

- **External uniqueness.** The programs check it over GND's shared-entity
  join: two join rows with the same referenced values break the rule. A join
  whose fact types share no object type is listed as not checked, and
  reported vacuous when all its fact lists are empty, as GND does.
- **Anchored rules are listed, not refused.** A rule that ties a value to a
  span of a source document is printed with its id and the reason it is not
  checked; `gnd check --anchors SIDECAR --document DOC` still decides it. A
  must-rule listed this way gives exit 4 when the program checks a population
  and no rule is violated. A violation gives exit 1.
- **`Number`.** A `Number` value is held as a binary float, like `Float`.
- **Value constraints scoped to a role.** A value constraint with `role_ref`
  checks only the values in that role, as GND does.
- **Inputs the programs now refuse, and two results that change.** A program
  refuses, with exit 3, a population it cannot hold exactly: an integer
  beyond 2**53 in a `Float` or `Number` cell, a number that is not finite,
  or two rows that differ only as `1` and `1.0`. On a `Float` model, 0.4.0's
  DuckDB program accepted the first and the last and reported a uniqueness
  rule satisfied where `gnd check` reports a failure. A model is refused
  when you export it if it holds such an integer among its allowed values,
  range bounds or comparison literals, puts arithmetic or a sum next to a
  `Float` or `Number` value, or compares a float literal with an `Integer`
  value. A script that ran 0.4.0's programs on such inputs now gets exit 3.
- **What is not verified.** The DuckDB programs are compared with
  `gnd check` on the packaged literature models. The `--rules lqp` programs
  are verified to compile; no RelationalAI engine has run them, so
  enforcement by `require` on an engine is not shown in this release.

### Include roots on more routes

- **Judgments on include roots.** `gnd judgments check` accepts a version-5
  root with includes, temporal or not, and judges the model `gnd check`
  composes. Receipts bind the root file's sha256, which commits to every
  include's pin; `--reference-root` applies to include roots too. Include
  refusals now report `reason: "binding"` with the include code in
  `message`, which `judgment.schema.json` allows; 0.4.0 wrote the include
  code as the reason ([#217](https://github.com/vasiloglou/gnd-public/issues/217)).
- **`gnd flatten`.** A new command writes an include root's
  `<stem>.flat.orm.json` and its `gnd-flattening/1` record, for temporal
  roots too, which `gnd extract` refuses; extract's refusal for a temporal
  include root now names it ([#217](https://github.com/vasiloglou/gnd-public/issues/217)).
- **PyRel export of include roots.** `gnd export pyrel`, in the default mode
  and with `--rules duckdb` or `--rules lqp`, exports an include root through
  its flat model and records `FLATTENING_RECORD_SHA256` and `MODEL_INCLUDES`
  in the program. The default mode still refuses temporal models; the
  `--rules` programs accept them ([#214](https://github.com/vasiloglou/gnd-public/issues/214)).
- **Unencodable include paths.** An include path that cannot be encoded as
  UTF-8 is refused `include:path` on every route; 0.4.0 reported the codec
  error itself, and the PyRel export exited 70.

### Unattended growth from a reviewed vocabulary

[Unattended growth](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/references/unattended-growth.md)
is the guide these changes follow.

- **Unattended growth from a reviewed vocabulary.** A version-5 root with
  `source.mode: unattended` may include an owner-reviewed model: the included
  elements keep their own source, status and modality and are exempt from the
  unattended rules U2 to U6, while an unconfirmed inferred `alethic` claim in
  an include is still refused (U8). `gnd validate` prints one `INCLUDE` line
  per include in its text output, and span diagnostics on included elements
  now carry the `includes[ID]:` prefix
  ([#222](https://github.com/vasiloglou/gnd-public/issues/222)).
- **`gnd evolve` admits sample and common-sense constraints.** A new
  constraint may now carry `source: sample` (row evidence) or
  `source: common-sense` (library evidence) when it is `proposed` and
  `deontic`, as the unattended-growth guide tells a host to write them; with
  `confirmed` or `alethic` it is refused by name. 0.4.0 refused both sources
  in every form ([#218](https://github.com/vasiloglou/gnd-public/issues/218)).
- **Growth rounds on a seeded root.** An unattended root that includes a
  reviewed model and holds nothing of its own may start without a source
  document; its first `gnd evolve` round declares one. `gnd evolve` refuses
  `repin-include` on an unattended root under every policy
  (`evolve:unattended-repin`), where 0.4.0 refused it only under
  `--policy additive` ([#222](https://github.com/vasiloglou/gnd-public/issues/222)).
- **A seeded growth example.** `src/gnd/examples/seeded_growth/` grows an
  unattended root from a reviewed seed in two rounds, then validates, checks
  and judges it; `unattended-growth.md` gains "Starting from a reviewed
  vocabulary", and the include route list names `gnd coverage`,
  `gnd evolve` and `gnd discover`.
- **`gnd evolve` parses each model text once.** One `gnd evolve preview` or
  `gnd evolve apply` now parses each model text once per reader. Before, an
  `apply` parsed the same two texts 22 times. Every preview, record, message
  and exit is unchanged ([#228](https://github.com/vasiloglou/gnd-public/issues/228)).
- **An outcome for every operation.** `gnd evolve preview --operation-outcomes`
  names each operation `admitted`, refused by the policy, validation or D-12,
  `dropped-with` a refused one, or `unassessed`. When a gate refuses the
  proposal, `--outcome-report FILE` receives the same rows; the refusal and
  its exit are unchanged. Without the option nothing changes
  ([#227](https://github.com/vasiloglou/gnd-public/issues/227)).
- **What a reply carries for an element the model has.** "The reply
  shape" in `unattended-growth.md` now says a reply names an element the
  model already has, its own or included, by id only, and routes rows for an
  existing fact type to `open_questions`, since the additive policy refuses
  a changed sample row ([#227](https://github.com/vasiloglou/gnd-public/issues/227)).
- **The admitted part of a round.** `gnd.discover.narrow.narrow_proposal`
  turns a proposal and its operation outcomes into a new proposal of the
  operations no gate refused, which is previewed and applied like any other;
  `apply` stays whole ([#227](https://github.com/vasiloglou/gnd-public/issues/227)).
- **One summary per round.** `gnd evolve summary ROUND_FILE` prints what a
  round reused, what the host dropped, what it proposed, each verdict's count
  and what the applied record added
  ([#227](https://github.com/vasiloglou/gnd-public/issues/227)).

### The literature examples from a host

- **Your own assertion entity.** The literature admission example's
  `admit()` takes a shape naming the assertion entity in your model and the
  entity types to follow from it. An assertion is identified by its own
  handle; every fact attached to an admitted assertion is kept, the facts of
  the followed entities with them, and an include root is admitted with its
  includes. `max_rows` bounds the rows read
  ([#215](https://github.com/vasiloglou/gnd-public/issues/215)).
- **Admission rules as data.** `rules` lists the requirements a reviewed
  assertion must meet, in order, with a reason for each refused value. A
  supported assertion that fails one is `policy-refused`; the packaged
  comparison is now the default rules. `max_targets` (up to 1,024, the cap
  of `gnd judgments check`) lowers the target cap. Such a call writes
  `literature-assertion-admission/2`; the packaged call keeps its bytes
  ([#215](https://github.com/vasiloglou/gnd-public/issues/215)).
- **A live producer over your own documents.** The literature reading
  example's `run()` takes a producer object over a root that holds
  `profile.json`: your documents, your reading model and its includes, and
  the optional review, calibration, conflict and absence steps, each
  recorded `skipped` when undeclared. The run has a byte budget per document
  as well as in all, seven limits with ceilings, and records the exits of
  `verify` and `check`, 0, 1, 2 or 4. It writes
  `literature-reading-run/2`; the packaged run keeps its bytes
  ([#216](https://github.com/vasiloglou/gnd-public/issues/216)).
- **Replay of a host run.** `replay(folder, fixture=root)` re-derives such a
  run with no producer call, from its settings and retained tables;
  `expected_evidence_sha256` ties it to the run that returned that digest
  ([#216](https://github.com/vasiloglou/gnd-public/issues/216)).
- **Reading a failed verification.** The documents guide shows how to list
  the constraints and derivations a `gnd verify` exit 1 failed, with the
  violating rows, from the JSON report, with a runnable example on the
  literature reading example's conflicting labels. `gnd verify` itself is
  unchanged ([#226](https://github.com/vasiloglou/gnd-public/issues/226)).
- **Where a quote may lie.** The anchor reference states the rule: a span
  may lie anywhere in the document the sidecar names, and GND has no notion
  of a section. The literature pages say what that means for a host that
  shows its model one section at a time. No format changes
  ([#226](https://github.com/vasiloglou/gnd-public/issues/226)).
- **A reference recall and precision for the reading stages.** The
  literature example ships a labelled reference set, built over the
  regression corpus without changing it, and one recorded Claude Sonnet run
  over it that replays with no producer calls: recall 27 of 31 after the
  targeted pass. The literature page shows it beside the figures #226
  reported ([#226](https://github.com/vasiloglou/gnd-public/issues/226)).

### Aggregate COUNT certificates

- **`gnd witness-count` and `gnd replay-count`.** `gnd witness-count MODEL
  POPULATION --request REQUEST --raw --out CERTIFICATE` writes a certificate
  for one named group of a derived COUNT rule: its members, their count and
  the row each one comes from. `gnd replay-count` rebuilds the roster from
  the model, the request and the population and compares. A group with no
  members in a covered relation gets a certificate with an empty roster and
  count zero, which replays too. The
  [COUNT membership contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/count-witness-contract.md)
  says which rules and inputs qualify
  ([#193](https://github.com/vasiloglou/gnd-public/issues/193)).
- **A packaged example.** `src/gnd/examples/literature/count_fixture/` holds
  a model, a population and the requests for a group with two members and an
  empty group; its README lists the commands.

### Other changes

- **`gnd check` on large vocabularies.** The checker no longer rebuilds its
  type maps once per object type: on the interop example with 1,000 extra
  object types `gnd check` takes about half a second where 0.4.0 took over
  two minutes, and `gnd judgments check` and `gnd verify` gain the same.
  Reports are unchanged. A subtype chain hundreds of types deep is still
  slow ([#221](https://github.com/vasiloglou/gnd-public/issues/221)).
- **An indented `---` is content.** The frontmatter reader behind experiment
  specs, conclusions and generated `SKILL.md` files takes a fence only at
  column 0, with nothing after it but spaces or tabs. An indented `---` in a
  block scalar or a multi-line value no longer ends the block early and drops
  the keys after it; a document whose only closing dashes are indented is
  refused as unterminated.
- **One parse per load and per witness command.** A model without includes
  is parsed once when it is loaded, where 0.4.0 parsed it twice, and
  `gnd witness`, `gnd replay` and `gnd why-not` parse each model text once
  per command, where they parsed it up to five times with `--composition`.
  Reports, certificates and exits are unchanged
  ([#228](https://github.com/vasiloglou/gnd-public/issues/228)).
- **CRLF models that end in a block scalar.** A YAML model saved with CRLF
  line endings keeps the final newline of a closing `|` or `>` block scalar,
  as it does with LF; 0.4.0 dropped it. A plain scalar or a comment that
  ends in `>` or `|` no longer keeps trailing blank lines.
- **Rule text for models that differ only in key order.** Within one
  process, two models equal up to the order of their keys no longer share a
  cached index, so the rule verbalization of the second prints its bindings
  in its own order.
- **Literature pages.** The literature section opens with an overview and
  gains a [command page](literature/commands.md).

## 0.4.0 (2026-11-17)

If you're upgrading from PyPI version 0.3.0, the [0.3.1 notes](#031-tagged-2026-11-11-not-published-on-pypi)
also describe changes in this release. The 0.3.1 tag also adds an explicit
diagnostic when guarded-case synthesis needs the optional `synth` extra.

### Literature: identity, composition and depth

The [literature lineage walkthrough](literature/01-lineage.md) follows reviewed
claims back to their sources and checks which lineage paths those claims support.

- **Identity and lineage.** Witness and why-not commands accept version 1 models
  and models without an explicit identifier. The packaged literature corpus
  includes a staged assurance report. Composition binds reviewed identity
  decisions to its record. Name diagnostics suggest unresolved candidates for
  review. Saved judgments support contextual assertions and checked lineage paths.
- **Model includes and reference catalogs.** Extract and check with separately
  rooted models, and verify witness and replay against the flattened model.
  A [fixed reference catalog](reference/composition.md) can participate in
  composition, checking, witness and replay. Replay refuses a catalog whose
  bytes differ from the recorded input.
- **Scientific evidence and revisions.** The packaged examples cover
  source-scoped claims, time dimensions, exact decimal replay and multipass
  reading with explicit coverage. Semantic migration records bind a revision
  to its inputs and support replay of earlier snapshots. Support-scoped
  verdicts show which derived claims survive a revision.

### Guarded-rule clauses

Guarded and derivation comparisons support typed literal lists with `in`.
Guarded antecedents support `negate` and `where` filters, with coverage-aware
verdicts. Guarded consequents support `any_of`, with diagnostics for failed
alternatives. Supported clause shapes lower into exporters, with installed
retail examples exercising the behavior. See the
[rule-check report reference](reference/rule-check-report.md).

### Other changes

- The [expense receipts walkthrough](expense/05-receipts.md) combines three
  documents using reviewed vendor identities. It shows how an omitted
  decision stops composition and how different decisions change findings.
- BookRec now has runnable chapters for
  [guarded rules](bookrec/08-guarded-rules.md),
  [suggested rules](bookrec/09-suggested-rules.md) and
  [claims from reviews](bookrec/10-what-reviews-say.md).
- The representation format names five additional rule IDs. Synthesis and
  assurance preserve the scope of their existing bounded coverage measures
  as the new guarded clauses become available.

## 0.3.1 (tagged 2026-11-11, not published on PyPI)

Version 0.3.1 is the GitHub tag `v0.3.1`. It is not on the package index;
install it from the tag:

```sh
uv tool install "git+https://github.com/vasiloglou/gnd-public@v0.3.1"
```

Everything in this section is new since 0.3.0.

### Guarded rules

- **Antecedent diagnostics**: `gnd check --guarded-diagnostics` reports, per
  guarded rule, how many bindings its antecedent has and the first atom that
  matched nothing. See [rule-check reports](reference/rule-check-report.md).
- **Comparing rule editions**: `gnd check HEAD POPULATION --baseline-model
  BASE` compares offending findings by rule ID across two editions of a model.
- **Guarded-case synthesis**: `gnd synth --guarded-cases` builds an active
  failing and an active passing population for each supported guarded rule,
  confirmed by the checker. See
  [synthetic data](guides/synthetic-data.md#generate-examples-for-guarded-rules).
- **Guarded-join discovery**: the opt-in `guarded-join` family of `gnd
  discover` proposes forbidden-pair and same-class rules from a binary relation
  and a classifier. See [discover](reference/discover.md#discover-guarded-joins).
- **Typed AMIE constants**: the ILP bridge imports rules with literal
  constants in body and head atoms, with bounded recount work. See the
  [ILP bridge](reference/ilp-bridge.md).

### Other changes

- **Ossie export and `redact`** (issue 169): `gnd export ossie` prints a note
  with the number of fact types that declare `redact`. The exported files do
  not change. `redact` withholds population values from reports, and an export
  carries the model's own text and no population, so a redacted fact type's
  reading, constraints and provenance text are exported in every
  [disclosure mode](reference/disclosure.md), as
  [Ossie interchange](explanation/ossie.md) explains.
- **Ossie import reference** (issue 173): the
  [representation format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md)
  defines the import report, `gnd-ossie-import-loss/1`, and names all 29
  `ossie-import:<rule>` refusals, so a caller can branch on them.
- **Package description** (issue 175): the package declares a long description.
  The PyPI page of the next release will show it.
- **Reply shape for unattended growth** (issue 104): the reply a host asks a
  model for now gives the entry shape of a derived fact type, with its quote.
- **Release procedure** (issues 174 and 176): the
  [release procedure](releasing.md) names the command that moves the pages
  after a publication, and says that every release through 0.3.0 was published
  by a token upload.

## 0.3.0 (2026-11-11)

Everything in this section is new since 0.2.0. The first block is Apache Ossie
interchange; the blocks after it are the other changes.

### Apache Ossie interchange

GND can share a model as an [Apache Ossie](explanation/ossie.md) ontology and
start a model from one.

- **Export.** `gnd export ossie MODEL --out ONTOLOGY.yaml` writes three files:
  the ontology, a sidecar (`ONTOLOGY.yaml.gnd.json`) that keeps the GND details
  Ossie has no place for, and a loss report (`ONTOLOGY.yaml.loss.json`) that
  lists each source field and how it was handled. `--format json` writes JSON,
  and `--loss-report PATH` puts the report elsewhere (import takes it too).
  Example populations are omitted and listed in the report; `--strict` stops
  the export when any field would be refused.
- **Import.** `gnd import ossie ONTOLOGY.yaml --out MODEL.json` writes a GND
  model and its own loss report. With the sidecar beside an unchanged ontology,
  the model content the export kept is restored, and the report says whether
  the restored model's identity matched the source's. What the export omitted
  stays omitted: a model with sample or reference populations comes back
  without them, and its identity does not match. An ontology from another tool
  imports through the supported projection. Import opens no network connection.
- **Scope.** The ontology layer of Ossie `0.3.0.dev0`, pinned to Apache Ossie
  commit `ee89dbdc`: concepts, relationships and a documented subset of
  constraint formulas. Ossie's semantic models, mappings and query interfaces
  are outside it.
- **Disclosure.** Both commands behave the same in every
  [disclosure mode](reference/disclosure.md). An export writes the model's
  constraint literals and description text, also for a fact type marked
  `redact`. Read the loss report before you share an export.

Start with [sharing the refunds example](how-to/share-an-ossie-ontology.md).
The mapping is in the `gnd-orm-core` representation format, "Ossie
interchange"; see [formats](reference/formats.md).

### Shared definitions, project-owned policies (issue 95)

A project can pin a local shared vocabulary while keeping its own rules.
Validation, checking and model verbalization use the composed model; evolution
can review a vocabulary update and repair project rules in one accepted change.
The [two-team expense tutorial](tutorials/shared-expense-policies.md) shows
Engineering and Sales using different policies, then Sales moving to a new
Finance edition while Engineering stays on the old one. The
[command walkthrough](how-to/shared-expense-policies-commands.md) runs every step.
Generated-app and linked-project conformance routes for these models remain
unsupported.

- **New model format, version 5.** A model that includes a vocabulary declares
  `version: 5` and uses two new fields, `includes` and `fact_type_constraints`
  ([formats](reference/formats.md)). **GND 0.2.0 cannot read a version 5
  model**: its schema refuses the version and both fields. Models at earlier
  versions are unchanged. A command that does not support such a model yet
  refuses it with `include:unsupported-route` before it loads anything;
  `gnd export ossie` and `gnd export pyrel` are among them.
- **Evolving an included vocabulary.** A proposal can re-pin an include
  (`repin-include`), and a preview of such a model carries `before_includes`
  and `candidate_includes`. `gnd evolve preview --previous-include ID=PATH`
  supplies the old bytes of a re-pinned include. GND 0.2.0 refuses these
  proposals and previews.
- **Model review.** `gnd verbalize model MODEL` and `gnd.api.verbalize_model`
  print a review of the complete model. They print the same text in every
  [disclosure mode](reference/disclosure.md), authored sample populations
  included.

### Model identity a caller can recompute (issue 111)

The `model_digest` that steps documents, sidecars and certificates pin is a
digest of a Python representation, which a caller outside Python cannot
reproduce. A second identity can now be used in its place.

- **Canonical model identity**: `gnd validate MODEL --identity` prints the
  model's canonical identity and, on the second line, the canonical JSON
  document it is the sha256 of, so a caller can recompute it. A model that has
  no canonical form exits 3 with `model:identity-unrepresentable`. The flag is
  text only and is refused (exit 64) with `--trace`, `--document` or
  `--format json`. The bytes are defined in the `gnd-orm-core` representation
  format, "Model identity (canonical, versions 1 and 2)"; see
  [formats](reference/formats.md).
- **Either identity is accepted** wherever GND matches a `model_digest` you
  supply: a walk's steps document (`gnd check --steps`), a report read back by
  session replay, a coverage source, a measure sidecar and corpus, and a
  witness certificate. Refusal messages are unchanged, and GND's own reports
  still write the legacy value. A Pyrel rules program generated from a model
  checks the legacy value only, so pin plans meant for it with the legacy
  `model_digest`. See [data and transitions](guides/data-and-transitions.md).

### Plain text for redaction and temporal models (issue 112)

On a model with an active redaction policy or temporal terms, the text output
of `gnd validate`, `gnd check`, a walk (`gnd check --steps`),
`gnd check --admission` and `gnd verify` printed the projected JSON report.
They now print their usual plain layouts, rendered from the projected payload
only, so nothing the projection hides reaches the text. A projected error line
does not name the error's type; `--format json` still reports it. JSON output,
the report schema and digests are unchanged.

### Constraints admitted on clean data (issue 104)

`gnd evolve preview --policy additive --check-population FILE` admits a new or
strengthened `proposed` + `deontic` constraint on a fact type that already has
data, when the population in `FILE` covers every populated fact type the
constraint ranges over and satisfies the constraint. This closes the route the
0.2.0 notes list as open. `apply` repeats the option, and a changed file stops
it (exit 11). The preview records the file's digest and the operations it
admitted, never a path or a value. A preview that carries the new
`population_check` field is refused by older GND readers. Rules and exits:
[admitting a constraint on clean data](reference/evolve-policy.md#admitting-a-constraint-on-clean-data).

One rule is stricter, with or without the option. A constraint written inside
a fact type now counts every fact type it reaches, not only the one that holds
it. Under `--policy additive`, a new constraint on an empty fact type that also
ranges over a populated one is refused (`constraint.populated.add`), where
0.2.0 admitted it.

### Unchecked source spans are counted (issue 74)

`gnd validate MODEL --document DOC` on an unattended model now says how many
source spans it did not re-hash because their document was not supplied: one
`unattended:spans-unchecked` warning, `N of M source spans were not re-hashed`.
The exit is unchanged. The new `--require-documents` flag turns the same entry
into an error and exits 3, also when no `--document` is given. A run in which
every span is re-hashed, a run without `--document`, and a model without the
unattended mode are unchanged. See "Unattended source" in the `gnd-orm-core`
representation format.

A correction rides along: a `--document` refusal (exit 3) on a model with a
redaction policy or reference populations now prints the same projected report
as that model's other validate results, in JSON and text. Before, it printed a
report without the projection, which failed the report schema.

### A growth round can declare its source document (issues 74 and 104)

An unattended model's growth round can now declare the document its new spans
cite, inside the round: a `source-document` operation in `gnd evolve`
addresses one `source.documents` entry by its digest. `add` appends it;
`modify` changes its label; `delete` removes it; `rename` is refused. Under
`--policy additive` the add is admitted, and a modify or delete is refused
(`source_document.modify`, `source_document.delete`, exit 3). The operation
exists in proposal `schema_version` 3 only. **GND 0.2.0 cannot read a proposal
that declares a source document**: it refuses it (exit 3). Proposals without
the operation are unchanged. See [the additive
policy](reference/evolve-policy.md#source-documents).

The packaged unattended growth procedure of `gnd-model-from-text` also says
what to do when a round's report names an existing fact type with the same
shape as an added one. The host reuses the existing fact type, or keeps both
and writes the reason in `provenance.rationale`, or keeps both with an open
question, and logs which it did.

### Fixes and internal changes

- **Discover on an unattended model** (issue 148): `gnd discover` no longer
  exits 70 with `semantic:unattended-u5` on a model with `source.mode:
  unattended`. Rule U5 now accepts an `induced` constraint without a span: its
  required `provenance.induction` block cites the population it was found in.
  Spans it does carry are still checked, and U8 still keeps it `deontic`.
- **Text walk on a reference model**: `gnd check MODEL --pre PRE --steps STEPS`
  in text format, without `--post`, no longer fails with `KeyError:
  'transition'` on a model with reference populations. It prints the same
  layout as on a plain model.
- **Retired private helpers**: `_find_cycle`, `_dfs_cycle` and
  `_ring_component_violations` are removed from `gnd.checker` (issue 114). They
  were private and had no remaining caller.
- **Test timing** (tests only, issue 117): two timing-sensitive tests no longer
  fail under load.
- **Prepared-policy reuse on Python 3.14**: incremental evaluation rechecks
  each non-primitive part of a prepared policy's key before reusing it. On
  Python 3.14, which caches a tuple's hash, a key part that had become
  unhashable was served from the cache; it now takes the unprepared path, as
  on 3.13.
- **A null `derivations` is read as absent**: a report, a session snapshot or
  a diff row with `"derivations": null`, which the report schema allows, no
  longer stops `gnd coverage --check` with a traceback, is no longer reported
  by a session as an invalid verifier payload, and no longer fails the
  redaction projection of a diff.
- **Packaged modeling examples**: four role names in three
  `gnd-model-from-text` examples are now snake case (`issue_number`,
  `occurred_on`, `start_date`, `full_name`), like every other role name in the
  examples. A copy of an example made before this release keeps the old names.
- **Disclosure reference**: the [disclosure reference](reference/disclosure.md)
  lists `gnd export ossie` and `gnd import ossie` among the outputs that are
  the same in every mode.

## 0.2.0 (2026-11-08)

Everything in this section is on `main` after 0.1.0. The first block is the
rule-check work; the blocks after it are the earlier changes that were waiting
for a release, newest first.

### Rule checks for projects that already break their rules

`gnd check` can now say which rule each verdict belongs to, judge a change
against a baseline, and tell a rule that had nothing to judge from one that
held. Without the new flags nothing changes: the check writes the report
version its model gets today.

- **`--rule-ids`**: report version 15, with the rule's own identity in every
  verdict (`address`, `addressing`), the rule's `remedy` text, and for an
  `acyclic` rule one row for every loop edge instead of a single cycle. See the
  [rule-check report](reference/rule-check-report.md).
- **`--baseline BASE`**: judges the base population under the same model and
  marks each violation `new` or `standing`, so a change is judged by what it
  adds. See [Adopt rules on a project that already breaks
  them](how-to/adopt-rules-with-a-baseline.md).
- **`--allow-vacuous`**: exits 0 when rules with nothing to judge are the only
  shortfall.
- **`source: tool-output` and `producer`**: population header fields that label
  facts a deterministic program produced and name the program and revision. They
  are labels the writer states; GND does not run or verify the program.
- **Population headers stay valid when copied**: `Population.model_copy(update=…)`
  re-checks that a `producer` comes only with `source: tool-output` and is a 1
  to 200 character string, and a population combined with its reference
  populations keeps its own `label` (issues 115, 116).
- **Refusals**: models version 15 does not describe (temporal terms, an active
  redaction policy, reference populations) are refused before either population
  is read.

### Unattended growth procedure (2026-11-06)

The `gnd-model-from-text` skill's Unattended mode used to say how to record
evidence and stop there; a host that followed it produced elementary fact types
and nothing else ([issue #104](https://github.com/vasiloglou/gnd-public/issues/104)).
It now covers Steps 3 to 7. Skill prose only: no command, option, exit or schema
changes.

- **Steps 3 to 7 without a user**. A new reference,
  `references/unattended-growth.md`, gives for each step the text that licenses a
  proposal, with a cited span and `proposed` + `deontic`.
- **Rounds and consolidation**. One document is one round; a periodic
  consolidation round runs over the whole model. `--policy additive` admits a
  new supertype but refuses pointing an existing object type at it, so
  consolidation is a reviewed non-additive proposal; see
  [subtypes under the policy](reference/evolve-policy.md#subtypes).
- **Checks for many documents** and **one reply shape** for a host's model,
  covering fact types, subtype links, constraints and derived fact types.
- **Constraints with their fact type**. A fact type's constraints are proposed in
  the round that adds it, since the additive policy refuses them afterwards.
  There is no policy that admits a `proposed` + `deontic` constraint over a
  populated fact type when `gnd check` is clean; that remains open.

### Report schema correction for exact-arithmetic reasons

`gnd check --format json` has always written a `term:*` reason, such as
`term:mod-zero`, on a derivation it could not evaluate because exact
arithmetic failed. The report schema did not admit those reasons on report
versions 7, 9 and 11, or on the version 4 and 6 projections of those
reports, so such a report failed validation against
`src/gnd/report.schema.json`. The schema now admits the seven `term:*`
reasons on those versions. This is a correction, not a new version: the
reports `gnd` writes are unchanged, no report that validated before is now
refused, and `derived-unknown` stays on the admission versions (10 and 13),
whose derivation rows carry the finding it needs.

### Type judgements by skill

The `fact-type` discover family can now take a skill's verdicts: whether an
induced group duplicates a fact type the model has, and whether a
multi-valued attribute is a many-to-many fact type. The CLI still decides
nothing semantic; it writes evidence, checks the verdicts against it and
renders the proposals.

- **Type evidence**. `gnd discover --families
  fact-type --type-evidence EVIDENCE` also writes each group's counts and the
  fact types its entity type already plays, for a judgement skill to read;
  the other outputs are unchanged. See
  [type evidence](reference/discover.md#type-evidence).
- **Type judgements**. `gnd discover
  --type-evidence-in EVIDENCE --duplicate-judgements J --shape-judgements S`
  reads verdicts bound to one evidence file: a group judged `distinct` is
  proposed even when its signature matches, one judged `duplicate` is
  reported against the named fact type, and a multi-valued group judged
  `many-to-many` is proposed with a uniqueness spanning both roles. Stale,
  incomplete or contradicted verdicts exit 3. See
  [type judgements](reference/discover.md#type-judgements).
- **Two judgement skills**. The packaged
  skills `gnd-judge-fact-types` and `gnd-model-multivalued` read one
  evidence file and the model, never the population, and write the
  `duplicates` and `shapes` judgements files: an induced group is judged a
  duplicate of a fact type the model has, or distinct; a multi-valued
  attribute is judged a many-to-many fact type with a uniqueness spanning
  both roles, the junction-table convention of the `rai-orm-from-schema`
  dialect, or skipped. When the evidence cannot decide, they ask. Neither
  applies anything. Walk through both in
  [Judge induced fact types with two skills](how-to/judge-induced-fact-types.md).

### Composition and type induction

One checked answer from several documents, traced back to a passage in each.
Walk through it in [From several documents to one checked answer](how-to/compose-documents.md).

- **Several anchors per fact role** ([#73](https://github.com/vasiloglou/gnd-public/issues/73)).
  An anchor sidecar at `schema_version: 2` may hold several anchors for one
  fact role, and the role passes only when every one binds. A repeated
  anchor (same fact, role, span and occurrence) is refused. Version-1
  sidecars check as before. The format is in the new
  [anchor sidecar reference](reference/anchors.md), with a published
  `anchor-sidecar.schema.json`.
- **Composition** ([#73](https://github.com/vasiloglou/gnd-public/issues/73)).
  `gnd compose MODEL DIR --out COMPOSED --record RECORD` and
  `gnd.api.compose` build one population from several anchored sources under
  a manifest of renamings, identical-row deduplication and scope tags, and
  write a value-free record of each composed fact's source facts.
  `gnd check --composition RECORD --sources DIR` re-derives the composition,
  checks each anchored value against its own source, and names the sources
  of every offending fact. `gnd.api.__all__` gains `compose`; see the
  [composition reference](reference/composition.md).
- **Witness lineage** ([#73](https://github.com/vasiloglou/gnd-public/issues/73)).
  `gnd witness --composition RECORD` writes a version-2 witness whose base
  facts name their source facts, and so, through each source's sidecar,
  their spans in each document. `gnd replay --composition` checks that
  lineage against the record. Version-1 witnesses are unchanged.
- **Fact-type proposals** ([#77](https://github.com/vasiloglou/gnd-public/issues/77)).
  `gnd discover --families fact-type` proposes a binary fact type for each
  attribute of a declared generic fact type that reaches `--min-support`
  distinct entities with one value type, as an additive evolve proposal.
  The report lists the rows that would migrate by opaque id and the
  attribute by digest; `--show-values` follows the disclosure mode. The
  default seven families are unchanged; see
  [constraint discovery](reference/discover.md#proposing-fact-types-from-generic-rows).
### Model growth guardrails (2026-11-04)

For a model that a program grows round by round, without a person in the
loop, GND now owns five things the program used to keep for itself: four
checks and a rule read-back. Walk
through them in [Grow a model by additions](how-to/grow-a-model.md).

- **Rule read-back** ([#72](https://github.com/vasiloglou/gnd-public/issues/72)).
  `gnd.api.verbalize_rules` renders a model's derivation rules in GND's
  controlled language and reports a prose rule as `unsupported`; see the
  [rule verbalization reference](reference/rule-verbalization.md).
  `gnd.api.__all__` gains `verbalize_rules`. Fix: the full verbalization of a
  model given as a path no longer raises on a structured aggregate rule; its
  output now equals the output for the loaded model.
- **Additive policy** ([#75](https://github.com/vasiloglou/gnd-public/issues/75)).
  `gnd evolve preview --policy additive [--populated FT ...]` refuses, with
  exit 3 and the preview still written, a rename, delete or change of an
  existing element, a replaced reference scheme, or a new or stronger
  constraint on a populated fact type. The preview gains `policy`,
  `populated_args`, `populated` and `policy_issues`, omitted without the
  option. `apply` must repeat the options, exits 3 when they differ from the
  preview's, and re-runs the policy; see the
  [additive evolve policy](reference/evolve-policy.md).
- **Duplicate-shape report** ([#76](https://github.com/vasiloglou/gnd-public/issues/76)).
  `gnd evolve preview --shape-report` adds `shape_matches`, grouping each
  added fact type with the fact types that have the same role players, with
  their readings. Advice only; `apply` needs no new option and rebuilds the
  report. See the [shape report](reference/evolve-policy.md#shape-report).
- **Extraction guidelines** ([#78](https://github.com/vasiloglou/gnd-public/issues/78)).
  `gnd extract --guidelines` adds a constraint-blind per-fact-type guide,
  digest-recorded in `<stem>.artifacts.json`. No constraint is stated (an
  identifying external uniqueness shows only as identification); value
  constraints are left out;
  a description can restate a rule and is repeated as written.
- **Unattended model-from-text** ([#74](https://github.com/vasiloglou/gnd-public/issues/74)).
  With `source.mode: unattended`, `gnd validate` requires `reviewer: none`,
  declared source documents, nothing `confirmed`, no `explicit` or
  `user-supplied` source, a cited span for every element, sample row and
  constraint except `common-sense` ones, and `deontic` for unreviewed
  constraints. `gnd validate --document DOC` re-hashes the spans.
  The `gnd-model-from-text` skill gains an Unattended mode.

Without the new options, and for models without `source.mode: unattended`,
previews, applies, extract bundles and validation results are
byte-identical to before. One exception: the verbalization fix above, for
inputs that used to raise. An `induced` constraint carrying
`provenance.spans` outside unattended mode is still refused (exit 3), now by
`semantic:unattended-u7` rather than the schema. The schema gains
`$defs.source_span`.

### Disclosure mode (2026-11-01)

One GND installation can now serve readers behind your interface and
customers ([issue #70](https://github.com/vasiloglou/gnd-public/issues/70)).
Set `GND_DISCLOSURE` or the root option `--disclosure` to `internal` or
`customer`; unset changes nothing.

- `internal` acts as if every value option were passed.
- `customer` withholds declared roles and every witness, replay, why-not, Lean
  and Soufflé value, in the CLI and the Python API. A request for values exits
  3 or raises `gnd.api.DisclosureRefused`.
- Contract change under `customer` only: `api.why_not` returns the redacted
  view, and `api.witness` and `api.replay` return the default view without a
  certificate.
- Under `customer`, child processes receive `GND_DISCLOSURE=customer`. In any other
  mode GND adds nothing to a child's environment, so a child inherits whatever
  `GND_DISCLOSURE` the caller's environment already holds.

See [disclosure](reference/disclosure.md).

### Near-miss values in why-not (2026-11-01)

`gnd why-not` and `gnd.api.why_not` now tell a missing fact from one spelled
differently ([issue #70](https://github.com/vasiloglou/gnd-public/issues/70)).
Every atom blocker reports near-misses: rows of its fact type that would have
joined if bound strings were compared after case folding, Unicode
normalization and removing punctuation and extra spaces. Matching stays exact:
status, blockers, counts, `work` counters and exit codes are unchanged.

- Three new fields on every atom blocker: `near_miss_count`,
  `near_miss_truncated` and `near_misses` (up to five pairs).
- The redacted view shows the two counters; `near_misses` reads `"redacted"`.
- The search has its own ceiling of 200,000 inspections and never refuses a
  request.
- Migration for `gnd-why-not/1` consumers: the schema is closed, so read
  `schema_version` and accept `/2`. Atom blockers carry three new required
  fields; nothing else changes.

See [values spelled differently](reference/why-not.md#values-spelled-differently).

### Why a derived fact is missing (2026-10-30)

`gnd why-not` and `gnd.api.why_not` explain a derivation that produced nothing,
or not the row you expected ([issue #66](https://github.com/vasiloglou/gnd-public/issues/66)).
GND's evaluator decides first whether the row is derived. If it is not, the
answer walks each clause in declared order. It gives the binding count after
each step and the first step that left none, with up to five of the bindings
that reached it, and explains a derived blocker's row in turn.

- New surface: one command, one API function (`why_not`, appended to
  `gnd.api.__all__`), and one output schema, `why-not.schema.json`.
- The CLI redacts population values unless `--raw` is passed; the API returns
  them, like `api.witness`.
- Exit bands: `0` blocked or derived, `2` unsupported (aggregates, prose rules,
  opaque values), `3` invalid input, `4` an unavailable term or a work limit.
- `check`, `witness` and `replay` are unchanged.

See [Why a derived fact is missing](reference/why-not.md).

### ILP import hardening (2026-10-30)

- The rules and Popper imports refuse a threshold their export never offered
  as `off-threshold`: a rules column the export could write but did not, and a
  Popper `ge_` or `le_` threshold name that `bias.pl` does not declare.
- An ILASP `#sum+` aggregate, or one with more than 16 terms and conditions,
  is refused `aggregate` by clause, not by a schema error.
- `tools/ilp_comparison.py` names a refusal that cites no clause, counts every
  clause as not evaluated after a refusal before the first clause, reports
  output the import refused at its reader, and exits 2 on other learner output
  it cannot read.
- `gnd import mined-rules` refuses a population whose bytes are not the run
  record's as `population-mismatch` (exit 3) before loading it, so a broken
  population that is not the bound one no longer exits 5. It counts every rule
  before any admission check, so a later rule's `too-large` is reported before
  an earlier rule's `covers-nothing` or `support-mismatch`; the exit is still 3.
- `gnd import mined-rules` refuses as `own-reference-join`, before any
  count, a mined rule with a variable whose types span two subtype families,
  or whose types' references resolve to more than one kind of value (text,
  number or boolean). The count spells such values apart or alike where the
  checker does not. The first was refused `support-mismatch`, falsely when
  the references share a kind; the second, a type under two references, could
  exit 70. Both now exit 3 by the new name. A rule over such a type whose
  values happen to be of one kind is refused too.

### More rule learners (2026-10-28)

The ILP bridge now has an adapter for each of five learners, and each was run
against a real learner version: once, or once per setting the owner approved. The committed outputs replay in the
documentation, so the comparison is reproducible without installing a learner.

- `gnd export ilp --target ilasp` writes an answer-set-programming task for
  ILASP, and `--target rules` a feature table for a rule-set learner such as
  RIPPER. `gnd import ilp-rules` reads both back, plus a language model's
  answer with `--target llm`.
- `gnd export ilp --target amie --population POPULATION` writes one unlabelled
  population as typed triples for the AMIE rule miner, and
  `gnd import mined-rules` brings its rules back. GND counts each rule on the
  population itself and admits the set only when every rule holds.
- The Popper adapter ran against Popper 5.0.1; its rendering now writes each
  threshold as a predicate of its own.
- Fixes at the milestone's close (2026-10-29):
  - A mined rule that joins a subtype with its supertype now counts as the
    checker does. The AMIE export spells such values by their subtype family,
    and its adapter version is now 2.
  - A mined run record must name the facts the miner read (`facts_sha256`).
    Facts the model renders differently are refused `facts-mismatch`.
  - An infix comparison of two variables, such as `C > D`, is type-checked as a
    join.
  - An ILASP constant that is not one of the export's thresholds is refused
    `off-threshold`.
  - The Popper reader keeps every rule in the solution block, and reads a bare
    `true` or `false` as a boolean.
  - A Popper threshold that the export never rendered is refused
    `off-threshold`, and the Popper export refuses an integer outside clingo's
    32-bit range as `unrepresentable`, as the ILASP export does.
  - The ILASP extractor reads every non-blank line after the timing block, so
    no learned rule after a blank line is dropped.

[Compare the rule learners on real runs](how-to/compare-ilp-learners.md)
replays every run, and the [comparison table](reference/ilp-bridge.md#comparing-the-learners)
summarizes them. Each row is a single run on a small example, not a ranking.

### Induced knowledge (2026-10-26)

GND can now propose rules from data, and never adopts one without review.
Object types take an optional `description` that verbalization and generated
docstrings carry. A description is never checked, so it must not restate a
constraint: state the rule as a constraint instead (see the
[representation format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md)).
A seventh provenance source, `induced`, records a rule found
from data, with its inducer, support and evidence digests; it
enters a model only as `proposed` and advisory, through `gnd evolve`.

- `gnd measure --labels` scores each rule against populations you labelled.
- `gnd discover` suggests constraints that hold in one population.
- `gnd export ilp` writes labelled populations for a rule learner, and
  `gnd import ilp-rules` brings its rules back after re-checking every claimed
  coverage itself; a claim it cannot reproduce is refused.
- `gnd evolve` binds a model's reference populations as `gnd validate` does.

The tutorial [Find the rule your auditors are really using](tutorials/learn-rules.md)
walks the loop on a synthetic refunds example. GND has no rule learner of its
own: the example carries a small stand-in learner script, and no real learner
has been run in its tests.

### Opt-in incremental evaluation (2026-10-20)

`api.EvaluationSession` reuses eligible extension components and constraint findings
across loaded snapshots while keeping the normal public report semantics. Host
observations pass through normal population validation; separate bounded version-1
counts feedback supports ordered attempts. Persistent experiment wires and existing
stateless defaults keep their contracts. Receipts now consume a private report copy,
so changing their public report cannot alter a later transition. Failed receipt
minting also avoids a repeated checker invocation.

The frozen public reporter replay executes 4,878 rule bodies with receipts and 179
with sessions plus receipts. Complete reports, branches and ordered logical
calculation results match. Initial IE5 wall time regressed on the measured small public
fixtures: reporter medians 5.83 s versus 6.79 s in one balanced shared-host run.
IE6 then reduced repeated policy accounting, preserving live hashing, mutation
guards, cloning and limits. In a new balanced comparison, session medians improved
9.59→9.03 s on the reporter, 2.41→1.99 s on course and 0.574→0.541 s on localized
controls against the archived pre-IE6 session. Full evaluation with receipts was
still faster in each comparison (8.50 s, 0.86 s and 0.423 s). Small shared-host
samples establish no general speedup; remaining bookkeeping stays an explicit
performance follow-up. Do not compare elapsed values across these separate runs.

The session is in-process and bounded to one generation, 100,000 retained rows and
32 MiB projected cache content by default. Unknown/reference/observer modes and
oversized units compute fresh. Current witness/lineage/unavailable state remains
part of parity checks. Profiling and balanced measurements are recorded with the
incremental-evaluation milestone; timing is workload-specific and is not a claim
about the offered 547-program workload, which has not been supplied. No production
publication or fresh certification is implied.

## Earlier transition-check work

Checks and transitions do less internal work. Each public call now computes the model's index key once, and the checker reads fact types without copying them. Results are unchanged. On a 13-call plan workload, GND time per call fell by about a third.

`api.check_with_receipt` now allows receipt-bound reuse of a transition pre-state check. On the same workload, it cuts checker runs from 25 to 19.

## Documentation for agentic data apps

The documentation is reorganized around agents: GND as skills plus Python, an executable
ORM ontology with ORM 2 diagrams, a "Work with an agent" section covering every skill,
a capabilities tour, a runnable plan-checking example (`approvals`) and an offline,
runnable development-session loop, plus recorded Claude Code, Codex and hosted-model sessions on one task. GND's lineage from GSD is documented, with a guide
for adopting a GSD project.

## Phase 4.1 documentation and applications

A navigable documentation site introduces GND, its supported capabilities and
stable Python API. BookRec teaches application development, hard rules, advisory
warnings and model evolution. Expense approval teaches policy checks and a
currency evolution. Both include synthetic inputs, runnable checkpoints and
instructions tested directly from Markdown. Dispatch remains the short first check.

## Acceptance status

Phase 3 accepted its recorded candidate on macOS/Python 3.13 and Ubuntu/Python
3.11. Phase 4.1 changes documentation and packaged tutorial resources; prior
artifact hashes do not describe these changes. Focused tutorial/build validation
and the final Phase 4 candidate sign-off are distinct. Phase 5 owns publication.

Independent external-user trials and the publishing service rehearsal remain
unmeasured. Optional provider/native profiles have separate prerequisites. No
fresh certification was requested; unavailable assurance is not inferred from
passing application checks.

## Development milestones

GND was built in a series of development milestones before its first public release.
Milestone numbers are not package versions; 0.1.0 is the first public release and
contains the public parts of all of them.

| Milestone | Date | What it added |
|---|---|---|
| v1.0 Core framework | 2026-08-17 | The ORM YAML format and `validate`; the population checker with alethic and deontic modality and verdict bands; `synth` and `measure`; the document round trip; code generation and conformance; data-driven sessions with closed feedback; model evolution and recovery; the review panel; packaging with `gnd install` |
| v1.1 Dogfooding repairs | 2026-08-18 | Acceptance by constraint satisfaction with coverage floors; digest-only expected answers, so no answer key sits on disk |
| v1.2 Milestone records | 2026-08-19 | Append-only planning records written by the skills; `gnd-new-project` |
| v2.0 Operations | 2026-08-25 | Operations with preconditions, effects and frames; transition checks with the frame check; sealed-test sessions; `gnd solve`; `gnd coverage`; `gnd-adopt` for GSD projects |
| v3.0 Guarded rules | 2026-08-28 | Guarded constraints; promoting advice to a hard rule through evolution; the BookRec application |
| v4.0 Architecture contracts | 2026-08-30 | Declared architecture contracts, a static architecture conformance check and smoke runs |
| v5.0 Derived fact types | 2026-09-01 | Structured derivations with stratified negation; incomplete and unsound derived-claim verdicts |
| v5.1 First outside user | 2026-09-04 | Generated projects that run outside the repository; evidence bound to the model's digest; the sixth review seat |
| v5.2 PyRel | 2026-09-05 | `gnd export pyrel`, a standalone program that runs locally on DuckDB |
| v6.0 Verified kernel | 2026-09-17 | A checker kernel verified with Nagini and the `proof-backed` assurance label; the evidence bundle is development-only, so public builds report `unavailable` |
| v6.1 Outside consumers | 2026-09-25 | `gnd.api`; batch checks; plan mode; witness redaction; walk floors; declared command and OpenAI-compatible adapters; `gnd import rai-orm` |
| v6.2 Composed semantics | 2026-09-25 | Operations and derivations in one model; exact integer arithmetic; aggregates; floats with explicit undefined cases |
| v6.3 Test lanes | 2026-09-28 | Faster evidence loading and separated test lanes (maintainer-facing) |
| v7.0 Theory core | 2026-09-29 | Source anchoring; recursion; opaque values and per-fact admission; three-valued derivations; `gnd verbalize population`; `gnd diff` |
| v7.1 Portable evidence | 2026-09-30 | Calendar dates and durations; immutable reference populations; witnesses and replay; patch and ranking sessions; saved-judgment gates; Soufflé and Lean exports |
| v7.2 Reliability | 2026-10-01 | Stricter session and admission consistency; one shared evaluator path |
| Public launch | 2026-10 | The public repository, packaged examples, this documentation site with executable tutorials, and the external-runtimes path |
