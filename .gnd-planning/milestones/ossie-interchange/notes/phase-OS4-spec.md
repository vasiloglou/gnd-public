# OS4 — Offline PyRel consumer cross-check

## Gate and provenance

Delegated under the named ossie-interchange milestone's auto run. Plan r3
predicate 6 and OS4 define the claim. OS0 E3 selected `relationalai==1.39.0`;
E3b's 2.0.1 observation stays separate. OS1 provides the 38 eligible census
exports. OS2 adds the current formula projection. Use the pinned
`apache/ossie-converters` commit and the existing isolated OS0 environments.

| Obligation | Measurable result |
|---|---|
| OS4-C1 | Exercise all 38 eligible exports through the pinned converter offline. Compare the emitted PyRel's named concepts, parent edges, owner-qualified relationship declarations and identifiers against the exported ontology. |
| OS4-C2 | Report explicit skipped constructs and failed conversions in a separate, pin-keyed consumer artifact. For the same source, record native GND PyRel rule rendering and its refusal or requirement count. |
| R7–R9 | Verify both Git pins, converter environment and RelationalAI wheel digest. Keep the network guard and all external imports inside the selected oracle subprocess. Leave the normal renderer and loss report free of converter dependencies. |

## Standing rules

Use the existing `tools/ossie_oracle.py` subprocess boundary and
`gnd.export.ossie.render_ossie`. Reuse the repository's AST approach for
counting declaration calls. The GND PyRel comparison uses the existing
rule renderer. Do not add a second translation of GND constraints.
The subprocess runs with a fixed offline config, declared tables and no
network route. Parse the generated source as Python. Never execute it.
Bound process time and artifact size. Unexpected declarations, missing
declared structures and refusal reasons must remain visible in evidence.
The ordinary GND gate may test the comparison instrument with static
inputs. Live converter execution is separately selected.

## Instrument

Compute a canonical structural snapshot from the ontology's actual
declarations. Compare the emitted source's concept literal names and
inheritance edges by resolving AST variables, relationship owner/name
and identifier arguments. Classify converter-induced differences only
when observations demonstrate them. Keep every case result, including
unexpected differences. A synthetic negative AST control must detect a
missing relationship and a mismatched parent or identifier. Exercise
known dropped `requires` and unsupported `OR` and `EXISTS` derivation
body controls separately. The candidate corpus is a positive formula
control, with a check for the chain's emitted definition. The downstream
artifact records pinned identity, per-case comparison and limitations,
plus the separately measured GND rules companion. Use a marked test
entry point and a repeatable output path outside the product.

For OS6, the converter source can be independently selected at a named
local commit in a separate environment. Keep its results separate from
the original pin. OS4 makes no claim about executing PyRel, warehouse
semantics or certification.

## Gate and review

The opt-in converter run requires owner authorization for the exact scope.
The phase also requires an independent diff review and a refactoring
review before closure. Unexpected failures that prevent the plan's
predicate require repair or a documented owner ruling.
