---
milestone: ossie-interchange
station: phase-OS0
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OS0
date: 2026-11-10
gates:
  - command: "PYTHONPATH=src .venv/bin/python $REVISED/admission.py $CENSUS $REVISED/gnd-validation.json"
    exit: 0
  - command: "$ENV_A/bin/python $REVISED/inventory.py $REPO $REVISED"
    exit: 0
  - command: "cd $REVISED && $ENV_A/bin/python formulas.py"
    exit: 0
  - command: "$ENV_B/bin/python $REVISED/controls.py $REPO $REVISED $ORIGINAL"
    exit: 0
  - command: "cmp eight replayed outputs with retained evidence"
    exit: 0
  - command: ".venv/bin/ruff check .gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/reproduce"
    exit: 0
  - command: "git diff --exit-code 54483d03 -- src tests"
    exit: 0
  - command: "git diff --cached --check"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base 54483d03 --strict"
    exit: 0
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or separately scoped CI selection
  reason: OS0 changes milestone evidence and reproduction scripts.
evidence:
  - path: .gnd-planning/milestones/ossie-interchange/004-owner-OD6.md
    sha256: 9ecdf4d644426ecdb114441ed91880620687c0c74730c254c0694dadc7522246
  - path: .gnd-planning/milestones/ossie-interchange/005-OS0-spec-amendment.md
    sha256: 679c2cd5fb2e6b8a2364a4a47911c436f0e6ed1b153dd56efc84bca5eb7cc71e
  - path: .gnd-planning/milestones/ossie-interchange/notes/phase-OS0-spec.md
    sha256: b145083fc5d2872ba55a0e893f18640d4637aee46f4d4b4dcc63d293665c3055
  - path: .gnd-planning/milestones/ossie-interchange/notes/phase-OS0-claude-review.md
    sha256: 8fe787d1ce9841c4ec7fabdb9152d823f1bd25c20596f527cca3a04fa29f7026
  - path: .gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/manifest.json
    sha256: a0e4ccc3b61b5d9b02a517b6975d9726a5c499292d577c83b93075ab16ff79ef
  - path: .gnd-planning/milestones/ossie-interchange/evidence/OS0/manifest.json
    sha256: f790b7455080d8f689a69e29d02611aa60f1b34a8b346f2cd0c0b53c6d3f627e
---

# OS0 phase record

OS0 measured the pinned validator, parser and converter, classified the full
tracked model census and established the inputs for OS1–OS4. The
[integration base](003-OS0-candidate.md) is `54483d03`. The approved
[005 amendment](005-OS0-spec-amendment.md) supersedes the earlier census
scope and preserves the original candidate.

## Criteria and evidence

- **OS0-C1.** The pointer audit exits 0 on 41 models and 11,442 unique
  pointers, with 45 observed and 17 absent metaschema definitions. Rows
  distinguish input-model refusals, population refusals and candidate native
  or extension projections. [Revised measurements](evidence/OS0/revised/README.md)
- **OS0-C2.** E1, E3/E3b and E5 on unchanged pinned inputs carry the original
  exits. The broadened E2, E4 and E6, individual parser exits and the
  liveness controls replay on the revised inputs. [Original measurements](evidence/OS0/README.md)
- **OS0-C3.** OD2 selects the document-digest-bound sidecar. OD4 has eight
  reordered facts, all preserving the reading, and zero reading-binding
  exceptions. Three explicit binaries support OneToOne, 54 direct
  references are candidates for generated OneToOne identifiers, and all
  237 projectable modality marks select the sidecar. Both tested
  RelationalAI versions produce identical source on Flights and refunds.
  OS4 and OS6 select 1.39.0, the converter's pin.

## Gate output

The exact oracle arguments and individual outputs are in the JSON reports.
Scratch paths in the reproduction commands are represented by the variables
defined in the reproduction instructions.

```text
Measured GND admission for 41 models, including 3 include guards.
41 models, 11442 unique pointers, 45/62 observed schema definitions
E2 controls 0/1; uniqueness-internal: 0, uniqueness-external: 1, mandatory: 0, guarded: 0, ring: 0, subtype-partition: 1, value: 0, textual: 1, anchored: 1, subset: 0, exclusion: 1, frequency: 0
Parser verified 418 reading orders, including 8 changed declaration orders.
OneToOne, ManyToOne, repeated-role refusal and require counter controls passed.
Eight revised outputs match the retained bytes.
All checks passed!
changed against 54483d03 (54483d0): 49 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
```

## Independent review and disposition

Claude Code Sonnet, high effort, exit 0, reviewed the original candidate via
read-only file tools, on the owner's scoped authorization in [004](004-owner-OD6.md).
[Verbatim review](notes/phase-OS0-claude-review.md). It could read the topic
checkout and could not run or independently reproduce the gates.

| Finding | Triage and disposition |
|---|---|
| F1 | Blocking. Git reproduced 41 matching files against the initial 14. The revised roster includes JSON and nested documents, and guard probes cover three include roots. |
| F2 | Blocking. The old runner bound zero census readings because its reorder list was empty. Both orders now run through the pinned parser for all 209 projectable facts. The repeated-role negative exercises a refusal. |
| F3 | Hardening. The old count omitted generated direct references. E6 now records their candidate projection separately from the three explicit bidirectional facts and states the converter limit. |
| F4 | Blocking. The old assertion never consumed mutated disposition rows. The revised control refuses both the missing row and the incorrectly native row. |
| F5 | Hardening. The record calls the classification a candidate projection. The independent pointer verifier resolves all emitted paths, and duplicate YAML keys refuse. |
| F6 | Blocking. The standard loader reproduced the four invalid role names. Whole-model refusals account for every source pointer. OS1 owns the four fixture corrections. |
| F7 | Hardening. E2 reports syntax probes by expression and scope. OS2 owns the independently reviewed expected-verdict corpus and semantic claims. |
| F8 | Hardening. The new counter distinguishes actual calls from a string and bare member. It observes zero calls in the two retained source files. |
| F9 | Hardening. The revised measurements and no-product-diff gate use the merged-plan integration base. Prior measurements retain their original base and the earlier matched PyRel source digests. |

## Refactoring review

None needed. OS0 contains local observation code and artifacts only. OS1
can use the existing model guard, canonical identity and artifact
publication primitives through their public seams.

## Boundary

One reviewer is one reviewer. The review opinion binds the original
candidate. The repaired measurements are backed by the local replay and
controls. Formula parsing supplies scope and syntax observations. The
exporter's product behavior, formula equivalence and generated PyRel
execution belong to later gates. No product source or tests changed.

## Open questions and refuted premises

- **OS1, example admission.** Four camel-case roles in three skill examples
  produce exit 3. Repair the shipped fixture names and retain the old
  observation. The existing include guard refuses the three include roots
  as permitted by predicate 7. Carry the distinction into the OS1 gate.
- **OS2, constraints and derivations.** Formula probe failures cannot settle
  kind-level expressibility. Evaluate semantics on the prior-authored case
  corpus before committing the renderer.
- **Close, census plan text.** Reconcile predicate 1 with the original
  depth-one YAML spec, the broadened Git roster and the explicit include
  route. Preserve the original findings and amendment provenance.
