# GA2 independent diff review

Codex CLI gpt-6-sol, high effort, read-only, public candidate `8032a346`.
The response below is retained verbatim. One reviewer is one reviewer.

## Findings

| Severity | Finding | Reproduction from the diff |
|---|---|---|
| Medium | **Checker agreement is incomplete.** The new guard compares `binding_count` and a pass/warning verdict, but does not compare the number or IDs of violating bindings. A checker result with 10 bindings and 2 violations passes the guard when discovery counted 10 bindings and 1 violation: both verdicts are `warning`. This does not establish the required support equality. | Supply those two counts to the candidate/checker comparison path in `discover()`. |
| Medium | **The service does not enforce family selection.** `discover()` runs joined generation whenever `joined_settings` is present, even if `guarded-join` is absent from `families`. With `guarded-join` selected and `joined_settings=None`, it runs no joined generation and produces no `joined_rules` report. The CLI prevents these combinations, but the service accepts them. | Call `discover()` with otherwise valid inputs and either mismatched combination. |
| Low | **Declared rule suppression depends on antecedent order.** `guard_key()` preserves antecedent list order. A declared guard with the same relation and classifier atoms in reverse order has a different key, so discovery can propose an already declared conjunction. | Declare the generated guard with its antecedent atoms reversed and a distinct ID, then select `guarded-join`. |

## Confirmed from the supplied diff

Directed pairs have their own cap; relation duplicates retain the first fact ID; endpoint classification checks require exactly one typed class; selected redacted roles are refused before joined row scans; and the CLI keeps `guarded-join` outside default families. The joined work counter charges row scans and generated candidate bindings and clears joined candidates on refusal.

**Verdict:** GA2 needs fixes to checker support comparison and service family admission before acceptance. This was a static review of the supplied diff; I ran no commands or tests.