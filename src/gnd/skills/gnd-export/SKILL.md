---
name: gnd-export
description: Exports and imports pinned Apache Ossie ontologies with loss reports, and exports their semantic model and mapping, optionally over delivered tables. Exports finite Lean models with unproved obligations, finite grounded witnesses, or explicitly selected bounded standalone Souffle derivation programs. Native compilation/execution and positive proof replay are separate optional claims; never source truth, completeness or assurance.
---

# Derivation program and finite witness export

Read the [export boundary](references/export-contract.md) and
[certificate contract](references/witness-contract.md). The closed
[certificate schema](references/witness.schema.json) pins versions 1 and 2.
Version 2 is for a population made by `gnd compose`: add `--composition RECORD`
to both `gnd witness` and `gnd replay`, as the certificate contract describes.

1. Select the model, candidate population, fixed-reference root and a nonempty
   version-1 target request. Preserve exact input bytes.
2. Run `gnd witness MODEL POP --targets REQUEST --reference-root ROOT` for a
   redacted, non-replayable view. Inspect every request's status. For a
   `missing` row, write a one-target request for that row and run
   `gnd why-not MODEL POP --fact-type ID --row ROW_REQUEST --reference-root ROOT`.
   It names the first rule step that left no bindings; it explains, it proves
   nothing. Its atom blockers count rows spelled differently (`near_miss_count`);
   read the pairs with `--raw` before changing a spelling.
3. On explicit raw export selection, run the same command with
   `--raw --out NEW_CERTIFICATE`. The destination is create-once; raw certificates
   contain source values. Never overwrite an existing destination. Under
   `GND_DISCLOSURE=customer` this is refused with exit 3; do not retry it in
   another mode for that reader.
4. Replay separately with `gnd replay MODEL POP CERTIFICATE --reference-root ROOT --json`.
   Exit zero means every requested finite proof replayed against those bound
   inputs. Missing or unknown results establish no absence theorem.

For an explicitly selected standalone Souffle program, follow the export boundary
above: render offline, verify its bound bundle, then select native execution or
positive provenance separately. Raw publication requires explicit `--raw`.

This skill never touches git. It never certifies, starts another skill,
regenerates code, automatically invokes an optional solver, or widens the fragment.
For population input representation, consult
[ORM core](../gnd-orm-core/SKILL.md). Each claim stays separate.

When the owner requests a development record, use the
[milestone record contract](../gnd-orm-core/references/milestone-record-format.md).
The driving agent owns that record and commit; GND never touches git.

`gnd export ilp` is not a derivation export. It is the ILP bridge: it writes
labelled populations for a rule learner with `--target` `popper`, `neutral`,
`ilasp` or `rules`, and `gnd import ilp-rules` brings the learner's rules back
as an evolve proposal (`--target llm` reads an agent's JSON answer). With
`--target` `amie` it writes one unlabelled population for a rule miner, and
`gnd import mined-rules` brings back only rules that hold on it. See
`gnd export ilp --help`; the proposal is reviewed like any other evolution
proposal. To run the whole loop with a learner, use [gnd-induce](../gnd-induce/SKILL.md); its proposals are reviewed through gnd-model-evolve.

For explicitly selected Lean definitions, run `gnd export lean MODEL POP
--toolchain leanprover/lean4:v4.34.0` offline. Publish a raw create-once bundle
only with `--raw --out NEW_DIR`, then run `gnd export lean-verify NEW_DIR --json`.
Compilation is separately selected with `gnd export lean-compile NEW_DIR
--executable LAKE --json`; `--elaborate-stubs` records stub elaboration separately.
Neither operation proves a theorem. The selected positive acyclic finite profile,
refusals, exact propositions and ceilings are in the export boundary above.

## Ossie interchange

Use `gnd export ossie MODEL --out ONTOLOGY.yaml` to create five files: the
ontology, the `ONTOLOGY.yaml.gnd.json` sidecar, the
`ONTOLOGY.yaml.loss.json` loss report (move it with `--loss-report`), and the
relational pair `ONTOLOGY.yaml.semantic_model.yaml` and
`ONTOLOGY.yaml.mapping.yaml`. `--format json` writes JSON instead. Add
`--ontology-only` when the user wants the ontology without tables; the run
then writes the first three files.

Before sharing, inspect two lists. The loss report names refused pointers.
The mapping's `GND` extension lists every fact type and constraint under
`dispositions`, each carried or given a reason, and may hold
`unmapped_links`. Report the entries that carry a reason; never describe
them as mapped. Use `--strict` when a refusal should prevent writing the
bundle.

When the user has delivered tables, pass their binding file with
`--physical-binding FILE`. The semantic model then describes those tables.
A refused binding exits 3 with a `binding:` rule id and writes nothing.
Repair the binding. Never edit the model to make a binding pass, and do not
combine the option with `--ontology-only`.

An export stopped by `ossie:output-size` can be rerun with
`--max-output-bytes N`. Use `--max-input-bytes N` on import for a document
above the default bound. Raise a bound only for a size refusal that names
it, never to get past a different refusal. Outputs are create-once: an
existing file at any output path exits 11.

Keep the ontology, sidecar and loss report together for a GND round trip
with `gnd import ossie ONTOLOGY.yaml --out MODEL.json`. Preserve the
ontology bytes so import can verify the sidecar binding. Import reads the
ontology only, not the relational pair. The import report is written to
`MODEL.json.loss.json` by default, or to the path given by `--loss-report`.

Use the [normative Ossie mapping and file format](../gnd-orm-core/references/representation-format.md#ossie-interchange)
for supported declarations, pins, output formats, the relational files, the
binding rules and import rules.
The ordinary CLI routes run offline. Select any external consumer
verification separately.
