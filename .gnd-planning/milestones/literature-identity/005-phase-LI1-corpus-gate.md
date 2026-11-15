---
milestone: literature-identity
station: phase-LI1-corpus-gate
skill: "n/a -- repository development under process-phase, not a gnd-solve station over a domain model"
scope: phase-LI1-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved the LI1 corpus at commit cd30649b, tree src/gnd/examples/literature 65782aac2bf0544e562404753d1db68ef77d34d6"
  exit: "n/a -- ruling"
evidence:
  - path: src/gnd/examples/literature/corpus/corpus.json
    sha256: 9b572f981660f273a6db95ec248f106db0e618fecea7de8dda934c329fdcd5f1
  - path: src/gnd/examples/literature/answers/answer-key.json
    sha256: e183f2cf840b176925da2bbcf4d3cd207fb116933ebbd732301f96a385058944
  - path: src/gnd/examples/literature/answers/README.md
    sha256: 0fb1a56ca7f1bf8bc997ce1674248177602985b8f1f15a60cbca3f245b94cf43
  - path: src/gnd/examples/literature/answers/heldout.sha256
    sha256: 00453b06687807e81048144e56608208dc2c28f1f7856ed4604c8406ce9f6af7
  - path: src/gnd/examples/literature/expected/M1-drop-all.expected.json
    sha256: f9608c5aa9d06fc7eae863b4befcfccbce33ca0bb8e32a445866b9b56f5ecf43
  - path: src/gnd/examples/literature/expected/M2-drop-one.expected.json
    sha256: 2cb849f5a91f847130b2e052a8fb20264bc6b35b38d2d26fc16a54657ca2357f
  - path: src/gnd/examples/literature/expected/M3-stale.expected.json
    sha256: e5cd2b8ac86b8e6bfe45ac12a99c39f3736316e2e988a6d53af1faa336746f5a
  - path: src/gnd/examples/literature/expected/M4-false-derived.expected.json
    sha256: 8428b0a295a78d2830f244c77f640b10ff50841cf757fc319d40b0ae53ffc17f
  - path: src/gnd/examples/literature/expected/M5-invalid-population.expected.json
    sha256: 856b5fa3cdaa4948b203046c2e4367a22140f919cb54b8a732602913a9d5e3f3
  - path: src/gnd/examples/literature/expected/M6-shifted-span.expected.json
    sha256: 37e82f41b68fd2c313d5349201272896d47c6c7d51219a2895b391e4515a856a
  - path: src/gnd/examples/literature/expected/X1-abstain-6.expected.json
    sha256: ecbd2e34dd9ec4766a44f39499cb775373fff9078d8766aa5bb76ef6a8c4dc37
  - path: src/gnd/examples/literature/expected/X2-consistent-shift.expected.json
    sha256: 774c1cffdf62b173e9cac1324f5a164cc2831ecebfb3378aab2971f945155e46
  - path: src/gnd/examples/literature/expected/reference.expected.json
    sha256: 98f123a9d7c58c240c4d24ac12b1bcf6cce7e8076c59c13e0fef40834d311e64
  - path: tests/test_li1_assurance_report.py
    sha256: c7be6c3b3cfe64b1be1b425add18231401b8be18caf74de0875b613ed8f5a734
  - path: tests/test_li1_literature_corpus.py
    sha256: 870b39283485440c9a2449cb6b542694fbc1171542ad9fdd7a39d62805334f01
  - path: tools/build_literature_example.py
    sha256: edbb57f554586a3dddc98a474c5d4167b05dd0d427dc41d005cde8b547b381b3
---

# Claim

The owner approved the LI1 corpus as committed in `cd30649b`: the 16
paraphrased documents, the answer key and its stories, the reference run, and
the nine expected outcomes in `expected/`. The owner ruled amendments A1–A5
(spec §13) as proposed, with A4 counting a missing composition record as an
absent freshness unit. The owner asked for the gate to be recorded, and
implementation waits for a separate go-ahead.

## Gate output (verbatim)

    Owner answers, 2026-11-15, in chat:
      Corpus gate:      "Approve the corpus (Recommended)"
      A1, A2, A3, A5:   "Accept all four (Recommended)"
      A4:               "Count it as absent (Recommended)"
      Go-ahead:         "Record and stop (Recommended)"

## Rulings `(o)`, 2026-11-15

| ID | Ruling |
|---|---|
| Corpus | Approved as committed. A later change to any expected outcome returns that outcome to the owner |
| A1 | `model-population-validity` is an agreement stage. A unit agrees when its R1 exit equals `expected_check_exit` (4 for every source here). The floor is 12/12 |
| A2 | For source binding, freshness and derivation, units are the gold items together with the run's items. "Both" means run-positive and in agreement. Derivation abstention counts derived fact types whose R4 verdict is unchecked or vacuous. A source binding is accepted when R2 does not refuse it |
| A3 | A stage with any refused unit is `fail`, and its report names `refused_units` |
| A4 | A missing composition record is an `absent` freshness unit. Freshness therefore fails in M5 and M6 (recall 24/25), as the expected files say |
| A5 | The approved outcomes are the `literature-assurance-expectation/1` files. Full report goldens are generated once the harness exists, and they must agree with every value given |

## Boundary -- what this result did NOT establish

- **No harness.** No harness code exists. The 47 harness tests are red because
  the module is missing, which is what this gate approves.
- **The expected outcomes are measured, but no harness has scored them.**
  They were built from route outputs measured on 2026-11-15 by scratch
  probes, not by a harness.
- **The labels.** One author wrote them, and they are not independent expert
  ground truth. The held-out separation is procedural, not blind.
- **Four body-level passages** (sbi-frontier.p2, roberta.p3, roberta.p4,
  segment-anything.p2) paraphrase claims from the body of their papers, and
  were not checked against their bodies.
- **Further authority.** No merge, publication or push is authorized. The
  `literature-heldout` branch stays local.

## Open questions

- None surfaced by this gate.
