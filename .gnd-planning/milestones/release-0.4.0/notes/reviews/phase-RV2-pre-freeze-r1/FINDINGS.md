# RV2 pre-freeze review findings

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Retained source receipt was independent of the checkout SHA | yes | hardening | fixed | 9ae859222288c62a9da229442140ba83fd4a771e | The verifier accepted synthetic files with valid digests and the wrong source receipt before the fix. The wrong-source control now refuses it. The archive uses the same verified ref. |
| F2 | Resolution manifest digest was checked indirectly | yes | completeness | fixed | 9ae859222288c62a9da229442140ba83fd4a771e | The approved P2 probe explicitly calls for the binding. The probe now compares path and raw-byte digest before reading the decision and repeats the re-pinned mutant. The revised rehearsal passed. |
| F3 | Recorded-version helper imports the driver environment | yes | completeness | rejected | | The helper translates report bytes in the driver. Candidate invocations keep the isolated installed interpreter in both wheel cases. |
