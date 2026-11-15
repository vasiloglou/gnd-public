---
milestone: literature-identity
station: phase-LI5-independent-reserve-assembly
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-independent-reserve-assembly
date: 2026-11-15
gates:
  - command: "codex exec --ignore-user-config --ephemeral --sandbox read-only --disable shell_tool --disable multi_agent -m gpt-6-astra --output-schema RESPONSE-SCHEMA --output-last-message FIRST-ANNOTATION -"
    exit: 0
  - command: "uv run --no-sync python -m gnd.examples.literature.lineage_run assemble EXAMPLE MODEL FIRST-ANNOTATION FIRST-RUN"
    exit: 3
---

# Claim

Astra submitted a source-only annotation. The frozen LI5 assembler
refused it because a resolution key did not name a participant of an
admitted assertion. No score has run.

## Gate output (verbatim)

    {"exit_code": 3, "reason": "input:unadmitted-resolution-key"}

The exact first annotation, delivered without an answer key or prior
results in the Astra sandbox, has SHA-256
`d1d8c3befba78fd8d75d192e8ecd331440b69d6c9bbf62eb81cd3e3ed01e545b`.
The assembly stdout has SHA-256
`7b8a2ec25397c9b04cf921c1c66b2bf4c30b4a4a1447af887a9d2734361288a7`.
The bytes are retained outside Git. The [corpus gate](028-phase-LI5-independent-reserve-corpus-gate.md)
binds the unchanged source packet and key.

## Boundary

This first submission supplies no composition or independent score.
The annotation handoff omitted the producer's requirement that
decisions address only participants of rows that survive admission.
A source-only recovery may omit invalid references while retaining
all original statements and every valid decision. The annotator will
receive only the producer's general resolution-input rule and its
own first submission. The key and path evidence stay sealed.

## Open questions

- Preserve the refusal and score the first executable blind
  annotation if the procedure-only recovery succeeds.
