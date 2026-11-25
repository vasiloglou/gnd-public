# OB5 quoting gate

**Owner ruling, 2026-11-25.** `auto=false`.

The owner was shown the [oracle-lane run](notes/OB5-oracle-lane-run.md)
(commit `404f9b4c`) and asked "Do you approve fixing the quoting rule and
changing V2's expected mapping, or do you want it explained further first?"
The owner answered:

> approved

## Rulings

| Item | Ruling |
|---|---|
| The quoting rule (amends OB3 E5) | **Approved.** A regular identifier is written quoted and upper-cased, as before. Any other name is written quoted exactly as given. |
| Approved corpus answer | **Approved to change:** `tests/fixtures/physical_binding/V2/expected.mapping.yaml`, its six expressions over the `uni.` tables. No other approved file changes. The OB4 corpus digest `d8377d48…54ed` is superseded by the one in the OB5 record. |
| Scope | The repair lands in OB5, which the approved H7 text provides for ("that is repaired first"). The export, relational and binding suites are selected again. |
