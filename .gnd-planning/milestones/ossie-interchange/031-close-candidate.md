# Ossie interchange close candidate

The seven phase gates are complete on the GND topic branch in
[draft PR #160](https://github.com/vasiloglou/gnd-public/pull/160).
This candidate asks the independent close panel to review the measured
exit predicates and the [proposed plan amendment](notes/close-amendments.md).
The r3 requirement to verify closure on GND main remains pending.

| Exit predicate | Result and evidence |
|---|---|
| 1. Export census and validation | OS0 fixed a 41-model roster. OS1 exported all 38 eligible standalone models and refused three include routes. The in-process schema and pinned validator and parser gates passed. [OS0](006-phase-OS0.md), [OS1](009-phase-OS1.md). |
| 2–3. Determinism and loss accounting | YAML and JSON replay produced stable bytes. The report and source identity bind to the exact ontology bytes in the sidecar. The census gives one disposition per pointer and never copies refused source values. [OS1](009-phase-OS1.md), [OS2](014-phase-OS2.md). |
| 4. Formula rendering | The pinned parser accepts the emitted formulas. The GND checker agrees with 29 authored semantic controls for the reviewed formula shapes. The oracle supplies syntax and scope checks. The PyRel comparison preserved 162 baseline observations. [OS2](014-phase-OS2.md). |
| 5. Import | 30 exact restorations and eight with precisely the documented population omissions. GND diff checks 34 non-temporal models. Direct authored-document equality checks four temporal models. The pinned Flights example imports with 55 proposed constraints carrying imported provenance. [OS3](020-phase-OS3.md). |
| 6. Offline consumer | The universal conversion premise is refuted. At the pinned converter and SDK 1.39.0, 36 intact outputs match declaration identities and two intact inputs refuse. Separate controls isolate the composition-chain SDK assertion and inherited library-subtype identifier. The reviewed consumer report records both cases. [OS4](021-phase-OS4.md). |
| 7. Include route | Three reproducible `include:unsupported-route` refusals. [OS1](009-phase-OS1.md). |
| 8. Documentation | The explanation and packaged skill point to the normative mapping. The refunds walkthrough verifies the restored digest. The strict site build and 16,448 link checks passed. The full page-policy suite still reports a pre-existing paragraph-length failure in `grow-a-model.md`. [OS5](025-phase-OS5.md). |
| 9. Upstream publication | Owner approved the exact patch and draft. [PR #162](https://github.com/apache/ossie-converters/pull/162) is open at the tested head. All 40 upstream tests passed. The replay adds six metamodel requirements whose source is omitted by the pinned decompiler. The Flights snapshot and entity-scoped controls establish positive source emission. [OS6](030-phase-OS6.md). |

## Verification and scope

Each phase record retains the applicable commands, independent review and
refactoring dispositions. The final combined focused GND gate passed
335 tests with 49 deselections. The OS6 replay artifact has SHA-256
`def7d6b48da061def1b816d152b94acf92eabf170725b95694edac9951d3206c`.
The vendor artifacts are pinned to Apache Ossie
`ee89dbdc2844d8b7d293ed42c8613928bb99505f` and Apache Ossie Converters
`83ddc294c8840f5f497a2bdbec2348a128fc2254`. The OS6 upstream replay
substitutes the published contribution for the converter pin. Ordinary
GND export and import do not require either external consumer or credentials.

The interchange claim covers ontology layer 4 at version `0.3.0.dev0`.
The loss report describes non-native source pointers. `Duration` remains a
documented divergence. The SDK conversion and source-generation limits
remain in the consumer evidence. The close panel and GND merge are pending.

## Open-question sweep

| Source | Question | Disposition |
|---|---|---|
| OS0 | Example-role admission and include route | Closed by OS1's repaired fixture roles and the pinned include refusal. |
| OS0 | Formula expressibility by kind | Closed for the measured shapes by the OS2 authored corpus, parser gate and sidecar fallback. |
| OS0 | Census wording | Close amendment records the 41 inputs and the 38 admitted standalone examples. |
| OS1 | Formula scope, modality and sidecar | Closed by OS2's per-pointer source preservation. |
| OS1 | Restoring GND source safely | Closed by OS3's binding and identity gates. |
| OS1 | Early example and final wording | Closed by the early checkpoint and OS5 docs. |
| OS4 | Universal pinned conversion premise | Refuted. Close amendment records 36 intact matches and the two refusals. |
| OS4 | Upstream requirement conversion | OS6 demonstrates entity-scoped source emission and value-tuple metamodel compilation. |
| OS6 | Emitted source for value-only domains | Carry to the RelationalAI source generator. The two original conversion failures also remain documented consumer limits. |
| OS6 | Upstream publication | Owner approved the tested branch and exact draft. Apache Ossie Converters PR #162 is open. |
