# Phase OS0 — Pin, measure and decide

## 1. Status

Awaiting owner review (draft r3, 2026-11-10). Implementable once the plan
and this spec are approved. OS0 writes no product code.

## 2. Provenance

- Plan: [ossie-interchange-plan.md](ossie-interchange-plan.md) r2, §4 OS0,
  §0, §2.1 and §10. Unreviewed.
- r2 applies the owner's rulings of 2026-11-10 (`(o)`): OD8 adds E3b on
  relationalai 2.0.1 and answers D1, OD4 makes E4 count exceptions, and OD2
  is decided by E1.
- r3 follows plan r3, which applies the light-panel fixes over plan r2
  (`(p2 Fn)`). Here that means the JSON-pointer disposition unit (F3), the
  `refused` populations (F1) and the new E6 (F19). The panel reviewed the
  plan, not this spec.
- Upstream bytes read on 2026-11-10: apache/ossie
  `ee89dbdc2844d8b7d293ed42c8613928bb99505f`, apache/ossie-converters
  `83ddc294c8840f5f497a2bdbec2348a128fc2254`.
- No review has run over this spec.

## 3. Obligations

| Row | Source | Discharged in |
|---|---|---|
| OS0-C1 every JSON pointer of every census model has a measured disposition (p2 F3) | plan §4 | §6 step 3, evidence `inventory.json` |
| OS0-C2 E1–E6 and E3b recorded with limits | plan §4 | §6 step 4 |
| OS0-C3 measurement-dependent rulings settled (OD2 by E1, OD4 exceptions by E4, OneToOne and modality by E6, relationalai target by E3/E3b) | plan §4, §10 (o) | §6 step 5 |
| R7 pin | plan §0 | §6 step 1 |
| R9 credential-free | plan §0, AGENTS.md | §6 step 2: oracle environments live outside the repository; no `.env` read |
| checkpoint before completion | owner feedback 2026-10-14 | §6 step 6 |

## 4. Standing rules

1. Totality: inapplicable. OS0 adds no consumer of untrusted input to
   `src/gnd`. Measurement scripts live in scratch, not in the package.
2. Cap bounds the algorithm: inapplicable, for the same reason.
3. Validation order: recorded as an observation. E5 notes the order in which
   upstream `validate.py` reports faults, as input to OS3's order.
4. One walk: the inventory is produced by one walk over every JSON pointer of
   each census model (p2 F3), checked against every `$defs` element
   kind of `orm-meta.schema.json`, with a coverage assertion that every kind
   was visited.
5. One home: the measured mapping table goes in the plan's §2.1 (amended with
   provenance). No second copy.
6. Measure: this phase is the measurement.

## 5. Goal

Each of E1–E6 and E3b has a recorded result. The inventory covers 100% of
the JSON pointers of the census models, each with exactly one disposition. OD2, OD4's exceptions
and the `relationalai` target version are settled from recorded results. Nothing under `src/` or `tests/` changes (`git diff --stat
main -- src tests` is empty).

## 6. Design (steps)

1. **Pin.** Record both commits and the sha256 of `ontology/ontology.json`,
   `ontology/mapping.json`, `validation/validate.py`, `ontology/ontology.md`
   and `examples/flights.ontology.yaml` in `evidence/OS0/pins.json`.
2. **Oracle environments**, under the session scratchpad, never the
   repository:
   - env A: Python 3.11 with `apache/ossie` at the pin, which runs
     `validate.py`;
   - env B: `ossie-converters/ontology` at the pin, which runs `OssieParser`;
   - env C: `ossie-converters/relationalai` at the pin with
     `relationalai==1.39.0` and the upstream test `raiconfig.yaml`;
   - env D (o, OD8): the same with `relationalai==2.0.1`, overriding the
     converter's pin.
   Both install a proprietary package. The owner allowed this in scratch
   environments on 2026-11-10 (D1). The wheel digests are recorded in
   `pins.json`.
3. **Census and inventory.** Census: `src/gnd/examples/*/model.orm.yaml`
   (and the other `*.orm.yaml` in those directories) and
   `src/gnd/skills/gnd-model-from-text/examples/*.orm.yaml`. The exact list
   is written to `evidence/OS0/census.txt`. For each JSON pointer, the
   inventory records its element kind, id and one proposed disposition (plan
   §2.1; p2 F3). Population pointers are `refused` with reason
   `population:out-of-scope` (p2 F1).
4. **Experiments** (designed here, before they run):
   - **E1** Validate a minimal ontology with `custom_extensions` on a concept
     and on a relationship against `ontology.json` (env A). Liveness: the
     same document without the field must pass. Limits: this shows schema
     admission only, not that consumers keep the field.
   - **E2** For each constraint kind present in the census, hand-write one
     `requires` formula and parse it with `OssieParser` (env B). A kind
     scores `parses` or `fails: <message>`. Liveness: a malformed formula
     must fail. Limits: parsing is not meaning. Meaning is OS2's differential
     test.
   - **E3** Run `OssieToRelationalAIConverter.convert(...,
     table_provider=declared_table)` on `flights.ontology.yaml` and on one
     hand-translated census model (env C), offline (network guard as in
     upstream `tests/conftest.py`). Record success or failure, output
     concepts and properties, and the count of `require`. Limits: no
     execution of the output.
   - **E3b** (o, OD8) E3 again in env D. Also record any import or API errors
     verbatim, and whether the output differs from env C's (a textual diff of
     the generated PyRel). Limits: as E3. A failure on 2.0.1 is a finding
     about the converter's pin, not about GND.
   - **E4** Count the census fact types whose internal uniqueness is not on
     the first n−1 roles, and check whether reordering their roles changes
     their readings. A script over the inventory gives the count, plus a
     list. OD4 is ruled "reorder" (o), so E4's output is the list of
     exceptions (fact types where no role order states the uniqueness without
     changing the reading), each with its reason.
   - **E6** (p2 F19) Inventory checks, run in the same script. First,
     OneToOne: list the census binaries with a uniqueness on each role, and
     confirm that `multiplicity: OneToOne` states both, with no residue.
     Second, modality: count the census constraints by `modality`, and confirm
     that each alethic/deontic mark has an `extension` pointer. Liveness: a
     binary with uniqueness on one role only must not be classified
     `OneToOne`. Limits: inventory only, with nothing exported.
   - **E5** Run `validate.py` on `examples/flights.ontology.yaml` (expect
     pass) and on a copy with an undeclared concept reference (expect fail).
     If either end does not score, the oracle is not live and OS1's oracle
     lane is redesigned.
5. **Settle the conditional rulings.** Record which branch of OD2 E1
   selects, OD4's exception count from E4, E6's OneToOne and modality counts,
   and the `relationalai` version for
   OS4 and OS6 from E3/E3b. Each is stated in counts or exit codes.
6. **Checkpoint for the owner.** One short page shows a census model, its
   hand-written Ossie document, the validator verdict and the converter's
   PyRel. It goes to the owner before OS1's spec is written.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | May OS0 install the proprietary `relationalai==1.39.0` in a scratch environment for E3? | yes: E3 runs. No: E3 is skipped, and OS4 stays blocked until it runs. **Ruling (o, 2026-11-10):** yes, and also 2.0.1 ("you can also try relationalai 2.0"; plan OD8) |
| D2 | Evidence retention | commit the inventory, pins and results under `evidence/OS0/` (proposed); upstream source is never copied in |

## 8. Tests

None in the repository. Evidence files with expected outcomes:

| Evidence | Expected |
|---|---|
| `pins.json` | two commits, five digests |
| `census.txt`, `inventory.json` | every JSON pointer listed with exactly one disposition; coverage of all `$defs` kinds asserted |
| `E1.json`–`E6.json`, `E3b.json` | each with a result, a liveness pair and limits |

## 9. Out of scope

Any change under `src/` or `tests/`; vendoring schemas (OS1); publishing
anything; running on Snowflake.

## 10. Size

Scripts in scratch, about 300 lines. Evidence of about 1–2 k lines of JSON.
No product lines.

## 11. Approval instrument

This prose.
