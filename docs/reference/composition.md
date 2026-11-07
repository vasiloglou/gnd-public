# Composition

A program that extracts facts document by document often needs one
population built from many documents, for example to evaluate a rule whose
premises come from two contracts. `gnd compose` builds that population from
anchored sources and writes a record of where every composed fact came from.
`gnd check --composition` re-derives the composition from its inputs before
it checks anything, and checks each anchored value against its own source.

Composition changes only what its manifest lists. GND never guesses that two
values mean the same thing. An anchor binds a value to a range of text, and a
composed fact's anchors are its source facts' anchors; composing adds no
proof that a fact is true.

## The composition directory

```
DIR/
  manifest.json
  <id>/population.json
  <id>/population.json.anchors.json
  <id>/document.txt
```

Each source id names a folder holding one population, its anchor sidecar
(version 1 or 2, see [anchor sidecars](anchors.md)) and the document the
sidecar binds. An id is 1 to 64 letters, digits, `.`, `_` or `-`, starting
with a letter or digit. Other entries in `DIR` are ignored. No file may be a
symbolic link, and no directory on the way to it either: every path is
resolved step by step from the current directory (or from `/` for an
absolute path), so `..` and a symlinked folder such as macOS `/tmp` are
refused ("could not be read safely", exit 3). Work from a real directory
with relative paths below it.

## The manifest

```json
{
  "schema": "gnd-composition-manifest/1",
  "sources": ["contract-a", "contract-b"],
  "renamings": [{"source": "contract-b", "fact_type": "contract_has_party", "role": "party",
                  "from": "ACME CORP.", "to": "Acme Corp."}],
  "deduplications": "identical-rows",
  "scope_tags": [{"source": "contract-a", "tag": "2024-agreement"}]
}
```

- `sources` lists every source once, in the order composition reads them.
  Two ids that differ only in case are refused, so a case-insensitive
  filesystem cannot open one folder twice.
- A renaming rewrites one role's value in one source's facts, by exact match
  of value and JSON type. `from` and `to` have the same JSON type. A renaming
  that matches no row, names a fact type or role the model does not declare,
  or repeats another is refused; a match among instances alone does not count
  as a row. The same value listed among that source's instances of the role's
  object type is renamed too, but only when it stays one entity: two renamings
  that give one source value of one object type different new values are
  refused. One value of one object type is one entity in its source, so a
  renaming must cover every role of that object type where the value appears:
  renaming it in one fact type and keeping it in another is refused with the
  fact type and role that still use the old value, whether or not the value is
  listed as an instance. Renaming is the only way composition changes a value.
- `deduplications: "identical-rows"` collapses rows that are equal after
  renaming into one composed fact, whose lineage lists every source fact.
- A scope tag (1 to 128 characters) is attached to a source in the record
  only; it does not change the composed population.

[`composition-manifest.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/composition-manifest.schema.json)
describes the manifest; the parser is the authority.

## Compose

```sh
gnd compose model.orm.yaml DIR --out composed.population.json --record composition.json
```

For each source, in manifest order, GND validates the population against the
model, binds the sidecar to the population and the document, and applies the
renamings. Rows are then appended per fact type in source order, then row
order; a row identical to an earlier one becomes part of that fact's lineage
instead. Instances and `covers` are unioned. The composed population takes
its header (`model`, `model_id`, `source`, and `producer` when the first source has one) from the first source and is written as canonical JSON, so
composing the same inputs twice gives the same bytes.

`--out` and `--record` must be two different files outside `DIR`, and neither
may be the model (64). Files are compared by identity, so a case variant of
the model's name, or of `DIR` on a case-insensitive filesystem, is refused too. An output that is an existing directory is refused (74)
before anything is written. Both are written to temporary files first, with the
ordinary umask mode, and then renamed into place. The exits are
0, 3 (a refused input, `composition:invalid`, or an anchor binding message),
64 (usage) and 74 (an output could not be written). On a refusal nothing is
written. A refusal names sources and indexes, never a
value. Composition with reference populations is refused.

`gnd.api.compose(model, directory)` returns
`{"schema": "gnd-compose/1", "exit_code": 0, "population": ..., "record": ...}`
and writes nothing; a refusal returns `exit_code: 3` with an `error` object.

## The record

```json
{
  "schema": "gnd-composition/1",
  "model_sha256": "...",
  "manifest_sha256": "...",
  "population_sha256": "...",
  "sources": [{"id": "contract-a", "population_sha256": "...", "sidecar_sha256": "...", "document_sha256": "..."}],
  "scope_tags": [{"source": "contract-a", "tag": "2024-agreement"}],
  "facts": [{"fact_type": "contract_has_party", "index": 0,
             "sources": [{"source": "contract-a", "fact_type": "contract_has_party", "fact_index": 0}],
             "renamings": []}]
}
```

Every digest is the SHA-256 of a file's raw bytes. `facts` lists every
composed fact, by fact type and then index, with its source facts and the
manifest indexes of the renamings applied to them. No role value appears in
the record. The record is written as canonical JSON, and its identity
(`record_sha256` in a check report) is the SHA-256 of those bytes. A record
file in any other form, re-indented for example, is refused (exit 3), so the
check and a witness's `composition_sha256` always name the same bytes.
[`composition.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/composition.schema.json)
describes it.

## Check a composed population

```sh
gnd check model.orm.yaml composed.population.json --composition composition.json --sources DIR --format json
```

In order, GND:

1. checks the model's and the composed population's digests against the
   record;
2. composes again from `DIR` (binding every sidecar again) and compares the
   composed bytes, the manifest digest, every source digest, the scope tags
   and the lineage with the record;
3. checks the composed population.

A mismatch in steps 1 or 2 exits 3 and names the first field that differs.
`--composition` needs `--sources`, and excludes `--anchors`, `--document`,
`--compiled-operations`, `--admission`, `--populations` and the transition
arm (64). The checker runs over exactly the composed bytes it verified.

An `anchored` constraint is evaluated per source: each source's values, as
they were before renaming, are matched against that source's own sidecar and
document, with the [every-anchor rule](anchors.md#when-a-role-with-several-anchors-passes).
A composed fact fails when any of its source facts fails.

Composition does not check constraints. When two sources give different
values where a uniqueness allows one, both compose, and the check reports the
violation. The report's `composition` block then names, for every composed
fact in any verdict's offending facts, its source facts. An offending row of
a fact type's own constraint is matched within that fact type; a
model-level constraint's row is matched in every fact type holding it. A
verdict whose offending facts are values rather than rows (a mandatory
role's missing players, for example) names no lineage.



```json
"composition": {
  "record_sha256": "...",
  "lineage": [{"fact_type": "party_is_based_in_city", "index": 1,
               "sources": [{"source": "contract-b", "fact_type": "party_is_based_in_city", "fact_index": 0}]}]
}
```

Text output adds one line per such fact, `lineage
party_is_based_in_city#1: contract-b:party_is_based_in_city#0`.
`gnd.api.check(model, population, composition=RECORD, sources=DIR)` does the
same; `composition` may be a path or a parsed record.

## Trace a derived fact back to its sources

```sh
gnd witness model.orm.yaml composed.population.json --targets targets.json --composition composition.json --raw --out witness.json
gnd replay model.orm.yaml composed.population.json witness.json --composition composition.json
```

With `--composition`, `gnd witness` writes a version-2 witness. Its binding
adds `composition_sha256`, the SHA-256 of the record file, and every base
node adds `sources`, the record's source facts for that composed fact. Each
source fact's anchors, in its own source's sidecar, locate spans in its own
document, so a derived fact traces to the passages of every document it
drew on. The record must bind the model and the composed population, or the
witness is refused (3).

`gnd replay --composition` replays a version-2 witness: a base node whose
`sources` differ from the record is `proof-invalid` (1), and a different
record is `binding-stale` (3). A version-2 witness without `--composition`
is refused with `composition-required` (3). Replay checks the witness
against the record; only `gnd check --composition --sources` re-derives the
record from the sources, so run it before trusting a record. `gnd.api.witness` and
`gnd.api.replay` take the same `composition=` keyword. The format is in the
`gnd-export` skill's witness contract.

## Disclosure

`gnd compose` and `gnd.api.compose` return your own composed population in
every mode. The record and the `composition` block carry ids and indexes
only, and the check's offending facts follow `gnd check`'s usual redaction.
See [disclosure mode](disclosure.md).
