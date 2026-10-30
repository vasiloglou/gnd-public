---
name: gnd-export
description: Exports finite Lean models with unproved obligations, finite grounded witnesses, or explicitly selected bounded standalone Souffle derivation programs. Native compilation/execution and positive proof replay are separate optional claims; never source truth, completeness or assurance.
---

# Derivation program and finite witness export

Read the [export boundary](references/export-contract.md) and
[certificate contract](references/witness-contract.md). The closed
[certificate schema](references/witness.schema.json) pins version 1.

1. Select the model, candidate population, fixed-reference root and a nonempty
   version-1 target request. Preserve exact input bytes.
2. Run `gnd witness MODEL POP --targets REQUEST --reference-root ROOT` for a
   redacted, non-replayable view. Inspect every request's status. For a
   `missing` row, write a one-target request for that row and run
   `gnd why-not MODEL POP --fact-type ID --row ROW_REQUEST --reference-root ROOT`.
   It names the first rule step that left no bindings; it explains, it proves
   nothing.
3. On explicit raw export selection, run the same command with
   `--raw --out NEW_CERTIFICATE`. The destination is create-once; raw certificates
   contain source values. Never overwrite an existing destination.
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
proposal.

For explicitly selected Lean definitions, run `gnd export lean MODEL POP
--toolchain leanprover/lean4:v4.34.0` offline. Publish a raw create-once bundle
only with `--raw --out NEW_DIR`, then run `gnd export lean-verify NEW_DIR --json`.
Compilation is separately selected with `gnd export lean-compile NEW_DIR
--executable LAKE --json`; `--elaborate-stubs` records stub elaboration separately.
Neither operation proves a theorem. The selected positive acyclic finite profile,
refusals, exact propositions and ceilings are in the export boundary above.
