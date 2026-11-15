---
milestone: literature-identity
station: phase-LI5-independent-reserve-freeze
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-independent-reserve-freeze
date: 2026-11-15
gates:
  - command: "codex exec --ignore-user-config --ephemeral --sandbox read-only --disable shell_tool --disable multi_agent -m gpt-6-astra --output-schema RESPONSE-SCHEMA --output-last-message RECOVERED-ANNOTATION -"
    exit: 0
  - command: "uv run --no-sync python -m gnd.examples.literature.lineage_run assemble EXAMPLE MODEL RECOVERED-ANNOTATION BLIND-RUN"
    exit: 0
---

# Claim

The format-only recovery resolved the [first assembly refusal](029-phase-LI5-independent-reserve-assembly.md).
The executable blind annotation and its composition are bound before
the first scorer invocation.

## Gate output (verbatim)

    All statements unchanged; exactly one invalid resolution reference omitted.
    {"exit_code": 0}

Astra received the general admissibility rule and its first submission.
The key, labels, proposed paths and score were absent from the session.
The driver independently ran the existing admission route on the first
submission and computed its valid decision subset. The second response
kept all original source and statement values and exactly that subset
in its original order. The original source and key hashes in
[028](028-phase-LI5-independent-reserve-corpus-gate.md) are unchanged.

| Frozen artifact | SHA-256 |
|---|---|
| Executable annotation | `22890d0a785b9c3073249e2355280589561b2a394edeb93f81ca53e91924f030` |
| Assembly stdout | `e89df0eae5ec7db81135aed16463968955c578bcc4f2ec43172eff351f080c17` |
| Composition | `dc9fc6fbb33261ebc891397a0937142a365ea817b17f9cc259b1112291229896` |
| Composed population | `c7eb5b87ae50ad509209034ccc702fa842fc629fc7f26b790dd9517a36a7377e` |

## Boundary

These digests bind local artifacts outside Git. Assembly verifies the
admission and composition input. The lineage score has not run at
this freeze.

## Open questions

- Run the frozen score once against the owner-approved key.
