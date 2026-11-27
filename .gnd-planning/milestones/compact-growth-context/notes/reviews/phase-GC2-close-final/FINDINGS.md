| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Out-of-occurrence citations can validate another binding | yes | blocking | fixed | 066d2f3d | The worked example runs the second pair of IDs as a negative control; test_example_search_miss_retry_and_defer checks span containment and exact role coverage. |
| F2 | Receipt implies independent direction inference | yes | completeness | fixed | 066d2f3d | The receipt now states the agent attributes meaning and the executable check compares values to those citations. |
| F3 | Test opens text in locale/default newline mode | yes | hardening | fixed | 066d2f3d | The test decodes raw UTF-8 and applies NFC normalization for span coordinates. |
