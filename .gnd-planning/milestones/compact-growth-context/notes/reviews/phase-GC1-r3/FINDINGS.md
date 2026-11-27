| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Optional default spelling can change bytes | yes | completeness | rejected | — | Preserve authored optional fields. The documented exception is fact derivation, whose effective default is asserted. Semantic equivalence across differently authored models is outside the byte contract. |
| F2 | Fact-field coverage relies on digest | yes | completeness | deferred | — | Claude exercised the legal objectification fixture and observed the correct field; carry targeted fact-field coverage into the GC2 API tests. |
