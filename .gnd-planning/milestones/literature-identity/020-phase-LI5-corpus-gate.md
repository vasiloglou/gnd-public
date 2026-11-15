---
milestone: literature-identity
station: phase-LI5-corpus-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of LI5 development corpus and proof controls"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI5-spec.md
    sha256: 64ecb12ff34f8c7cd68f9e4a26bdb5b3e3f6d10e4035d5fb4508375b92999c6d
  - path: tests/test_li5_lineage.py
    sha256: 8e7476bfc8aadeabd5c04e554b98ef394e84bf82cc8d2158bbc1384c3adc2681
  - path: src/gnd/examples/literature/lineage/README.md
    sha256: 441636cbc30fbb1e43971772ecd9a91bb84d48962b33cc543dcf43927f316135
  - path: src/gnd/examples/literature/lineage/cases.json
    sha256: 0cc4b2764858d0712dbdb2026571cd65ed11bac2213ad67b95282198f4822f2f
  - path: src/gnd/examples/literature/lineage/control-document.txt
    sha256: 87ed667e39088964a7c2d12f01ac88885aa667bf24fa232475b009bf242032b5
  - path: src/gnd/examples/literature/lineage/control-input.json
    sha256: ca0ede0c69e13a8449c0bc9c9b47d5b39d02480a5871aed90bc97579226533a2
  - path: src/gnd/examples/literature/lineage/cycle-document.txt
    sha256: 39644edd5b8c279881087728884784aacb6fa2f57e896d514c3a44d6d15dc131
  - path: src/gnd/examples/literature/lineage/cycle-input.json
    sha256: 66d4a8e2f243cbd8e1a11b4361fca13977cc1ebb12fdd52fadee21b36b9374a5
  - path: src/gnd/examples/literature/lineage/development-input.json
    sha256: cbb2c0eaf19b66afd83a6835f4d878ae734ceb7c9ffa5bbddc317c6405e52b97
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The current milestone chat
delegates the LI5 corpus and amendment rulings. The exact development
annotations, source citations, LI1 identity decisions, adversarial cases
and expected proof exits are approved as the corpus-first instrument.
The fixtures are implementable because they contain distinct positive
and refusing paths, two supported spellings without a join, and two
separate support conditions that can be removed independently.

The red suite reported five setup errors with the example module absent.
The development expected key already pins three supported and five
excluded paths. The earlier reserved split ruling and digest stand.
The model and policy will bind the rule freeze before reserved scoring.

One Claude Code diff reviewer on stdin is authorized. No optional
spec review is budgeted. The model, constructor and scoring record
will be verified after implementation.
