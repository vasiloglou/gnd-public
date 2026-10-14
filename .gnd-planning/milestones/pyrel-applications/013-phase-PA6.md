---
milestone: pyrel-applications
station: phase-PA6
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA6
date: 2026-10-13
source_base: c0039e4
gate:
  command: ".venv/bin/python tools/accept_pyrel_applications_install.py --out /private/tmp/pyrel-applications-pa6-20261013-e"
  exit: 0
  output: "fresh wheel target-only application acceptance complete"
slow_cadence:
  command: uv run pytest -q
  trigger: local CI mirror on the merged commit before push
  reason: full repository suite
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/install-regate-e.txt", "sha256": "762cb436eb6e600fa9ac253de6610909f14131a28b0b4e3a29c258a3a46807cf"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/regate-red.txt", "sha256": "7805b03fd8ef247be9209605af97764649aad996412abd4450a23ad5b4145101"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/regate-green.txt", "sha256": "0efee2f7497f3175194f5e7bf96f692bf01ac35bbc805180682921c8dcfbb250"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/regate-controls.txt", "sha256": "69dab4b22a706c49224746c107867394b5fcecefcaff2b453dd889666f46bb03"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/regate-controls-red.txt", "sha256": "cd533642dffb2e5327555b2ca15668fcd2728a078ff6bb5db1d2cf0bb8f2c776"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/claude-regate-review-raw.md", "sha256": "4118743e505fe80b558c6478e44c668c14233318795baa31a091cef2997fb0e5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-bookrec-offline-steps.json", "sha256": "ff55d3a18c13df1d3d21f124b1ce0e0c123bd65abf48e57b87249bccab525d1f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-bookrec-pyrel-steps.json", "sha256": "83a02648bafb29aceced122c4a6861c90408fb20db646ea08258fd1f23d56935"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-expense-isolation.json", "sha256": "0593f4610ac8141b839fb4d4de90a64b63ed7648e4696c3125839154d64863ca"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-expense-offline-steps.json", "sha256": "2b2201b1a0b2d0837097b77f66d704f72a444430b9788b01b57b66722b5600ae"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-expense-pyrel-steps.json", "sha256": "3ff767bde08d447ed6a4baf80a725107602d1d9beacf1b4d69f9181ba32b762f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-gnd-corpus.json", "sha256": "45c355f07e1f0b764c81779d5d7a212c94547538b7ebb4d23c7b5890dc7759fe"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-isolation.json", "sha256": "a5df5817274e9241ff070230b6f0965d57523358b2633c227ac472e7035c25e5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-native-corpus.json", "sha256": "6623b00b16c01e5290e7cd32cca0da4a9dd1a09c801b4cf7025e63cd1660afa4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA6/e-receipt.json", "sha256": "bd5da83348765fafc1741dc8eea8f112b519cf4d0183f827dbfcd1325f0894d3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA6-spec.md", "sha256": "e87675fcbc972d24306097f3b3c69a89235ec9989397f455d60b8d32de1533bd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA6-regate-review-prompt.md", "sha256": "387e0a1d4346b1ae23a3d6bbf33cf37882d8ae43b576b4f73cd0d4d53003acfa"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA6-claude-regate-review.md", "sha256": "7400af50da3c75de6729084ce8caec4f1ac8e2c10708122eb109fdac3cd87c9e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA6-repair-review-prompt.md", "sha256": "54ace84412ebb8e8f8e3e542511461657ba6154101d3a5cc7aaaa58913bda2b6"}
---
# PA6 -- Fresh-wheel and target-only acceptance

Spec notes/phase-PA6-spec.md with its delegated re-gate after A2/PA5R/012. Run E
used the harness committed in c0039e4 on a fresh target outside the checkout.

## Gates (verbatim, run E)

- Harness exit 0, "fresh wheel target-only application acceptance complete".
- Learning paths from the installed wheel: BookRec 59/59 pyrel, 51 passed with 8
  explicitly skipped offline; Expense 45/45 pyrel, 35 passed with 10 skipped offline.
- Installed GND137 verdict/witness/exit controls passed; native 137/137 with 2321 of
  2321 comparable rows matching and exactly the two A1 differences.
- Generated native import isolation passed for BookRec and Expense.
- Installed-site strict build exit 0; "7561 local links/assets/anchors checked"; six
  SVG twins and graphic URLs bound.
- Receipt binds commit c0039e4, harness, 550 source hashes, tools, site config, lock,
  wheel and 565 artifacts (evidence/PA6/e-receipt.json).
- Install controls: "17 passed" (evidence/PA6/regate-controls.txt).

## Reviews

Initial Claude PA6 review (notes/phase-PA6-claude-review.md) plus one repair reading
after the re-gate (notes/phase-PA6-claude-regate-review.md): credit run E, no blocking
finding. Dispositions: provenance of PA5R evidence corrected in 011/012 addenda;
offline-skip and count-drift controls added -- the count control is red when its
check is disabled; the offline-skip check is redundant with the count check, which
still refuses the mutation (evidence/PA6/regate-controls-red.txt), recorded as
defense in depth rather than a red control.

## Refactoring review

None needed in PA6's own bytes beyond the constant update: the harness was already
reviewed and committed; the shared corpus-key refactor stays owned by
native-install-harness-maintenance as the spec recorded.

## Boundary

Finite installed acceptance candidate; no release, certificate, merge or universal
equivalence. Base install and zensical transitive dependencies resolve without a
lock (versions recorded). Runs A-D superseded and retained.

## Open questions

| Question | Owner / target |
|---|---|
| Source identity omits wheel build inputs (pyproject.toml, uv.lock, README) and tests/fixtures/pyrel_applications/approval.json | Milestone close |
| Isolation probe misses a bare tests module; AST check is a substring match | native-install-harness-maintenance |
| Split PA5R and ci-repair successor links | Milestone close |
