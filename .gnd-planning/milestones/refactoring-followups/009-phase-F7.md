---
milestone: refactoring-followups
station: phase-F7
scope: phase-F7
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_rf4_peripheral.py tests/test_rf6_packages.py tests/test_fu5_retired_helpers.py tests/test_rf8_structure.py tests/test_rf6_moves.py --tb=short
    exit: 0
  - command: python -m pytest -q .gnd-planning/milestones/refactoring-followups/evidence/F7/test_audit.py
    exit: 0
  - command: zensical build --strict
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F7-Claude-review.md
    sha256: fbef29352b1037f3895a7bcc5421c7f0a5c4a9e1903c774a60d7a22099a16585
  - path: docs/assets/refactoring-import-migration.tsv
    sha256: d6e91df7e2fbf6749060d21a495b3f65748af400d2083edc6686b0319e601589
---
Delegated acceptance with #297 open. The first public release carrying the notice keeps the live shims. Later removal requires the release owner's named phase and release. 847 literal rows, 479 RF4 moves and 47 RF8 imports give 1,373 historical rows and 1,252 distinct import spellings. Each spelling has one current migration target, with its intermediate targets recorded. Of the rows, 1,368 are object-identical, two wrappers bind different validation rules, and three helpers were retired earlier in FU5 under #114. Twenty-six current defining-home rows require no migration. Static scanning found uses on 458 rows, old-name patches on 20, and migration-target patches on 59. Dynamic and third-party usage remains unknown.

    1182 passed in 93.50s (0:01:33)
    4 passed in 0.23s
    strict site build exit 0
    Migration page and downloadable inventory verified

Claude requested changes. F1–F3: canonicalize through live module bindings, deduplicate the recommended target per spelling, distinguish the defining home. F4: test the actual rule-specific wrappers, pin live identity and reject a wrong-rule mutation. F5: recognize keyword targets and patch.multiple, including the real transition patch. F6: read Markdown cells and section names, bind the literal row count and consult the FU5 retirement registry; unexpected missing/changed bindings now fail. F7: serve the TSV from docs assets, add navigation, correct the release heading placement, validate the built page and asset. This review covered the original guide and table. Repairs received focused checks.

The first compatibility suite found an F5 oversight: RF8's class body pins caught the intentional extraction of the JSON dispatcher from AttemptRecord and SessionResult (1 failed, 1181 passed). The new two-row successor checks both exact predecessor hashes against the pre-F5 source, and pins the changed class bodies alongside F5's direct behavioral tests. The full affected suite then passed. Original RF8 records and aliases remain intact. Slow cadence: uv run pytest -q -m "evidence or census".
