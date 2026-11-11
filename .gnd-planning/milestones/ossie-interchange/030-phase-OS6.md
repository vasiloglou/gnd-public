# OS6 upstream converter contribution

The [approved spec](024-OS6-spec-gate.md) and [amendment](027-OS6-spec-amendment.md)
define the supported scopes. Claude Code independently reviewed the public
patch at `0f00f798`. The [publication candidate](029-OS6-publication-candidate.md)
records the findings, fixes and SHA-256 of the retained review.

The upstream RelationalAI suite passed all 40 tests at
`977cbb942c5458374192bb798a8a20320cca06f0` using SDK 1.39.0. The
[offline replay](evidence/OS6/reviewed/consumer-limitations.json) retained
36 matching intact conversions and the same two converter refusals.
Six isolated formulas compiled into scoped metamodel requirements and
the other two warned. The pinned source generator emitted none of those
six value-tuple requirements. Entity-scoped controls and the two Flights
route requirements establish emitted-source behavior for the supported
entity cases. The replay SHA-256 is
`def7d6b48da061def1b816d152b94acf92eabf170725b95694edac9951d3206c`.
The final GND focused gate passed 335 tests with 49 deselections.

## Refactoring review

The patch adds scoped formula compilation within the upstream converter
and uses the existing relation and SDK expression APIs. It preserves the
legacy raw formula path. Tests cover operand roles, typed literals, warnings
at the owning scope and decompiled source. Repeated entity roles warn and
skip after the SDK emitted unbound variables in the corresponding control.

## Publication ruling

On 2026-11-10 the owner approved the fork push and exact PR draft in the
publication candidate. The branch `codex/convert-ontology-requires` was
pushed to `vasiloglou/ossie-converters` at the tested head. GitHub confirmed
[Apache Ossie Converters PR #162](https://github.com/apache/ossie-converters/pull/162)
was open against `main` with that head and the approved title and body.
The title and body digests are recorded in the publication candidate.
This satisfies the upstream publication gate.
