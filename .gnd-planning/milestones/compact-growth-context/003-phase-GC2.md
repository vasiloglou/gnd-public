---
milestone: compact-growth-context
station: phase-GC2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GC2
date: 2026-11-27
gates:
  - command: "pytest -q tests/test_growth_view.py tests/test_growth_projection.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_model_verbalization.py tests/test_mc2_consumers.py tests/test_include_root_close.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py tests/test_unattended_growth_guidance.py tests/test_atom_bind.py tests/test_rf1_layering.py tests/test_evolve_loading.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py --tb=short"
    exit: 0
  - command: "ruff check"
    exit: 0
  - command: "python scripts/components_index.py --check"
    exit: 0
  - command: "python scripts/components_index.py changed --base 342f953d --strict"
    exit: 0
  - command: "uv build --offline --wheel followed by clean wheel install and seeded example"
    exit: 0
evidence:
  - path: src/gnd/api.py
    sha256: 55da652f4d1f6f61876aecf63b173415c6fb05a6b6ddf3eaedd67f4775d7f86e
  - path: src/gnd/commands/checking.py
    sha256: 7ee7a152a3753cc0c73fddabfd191c66ceede0c245e20dbb6b297d0d193208c5
  - path: src/gnd/documents.py
    sha256: 5c2a674b19dcf9aad323b0819c3ceae7b8a1367e6649aa72f1492de7735ad6cd
  - path: src/gnd/model/__init__.py
    sha256: b126fe5ae74d39ff4a4068026f2285b2ceb073b8f810f5c971bbe5bdc8a1973f
  - path: src/gnd/examples/seeded_growth/README.md
    sha256: f28c46184e7e1b8aab375366e544b68207950ae63ea66ff4722a0811a67df7ec
  - path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md
    sha256: 21136cab354fa38e18f187e17c24b25ac7b5d6093734ed3b6bb0c3c0a29526fe
  - path: tests/test_growth_view.py
    sha256: 7e42b22b3db01f9256bd0bbc3435b925dde9b68779e33965bf1f9c16f1fdb72c
  - path: .gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r4/review.md
    sha256: ef1f1f109fc5c27bae6356c297e89b4c33500a9cd1bab2be6106bbccc39d132e
---

# GC2 acceptance

Delegated coordinator ruling (auto=true), 2026-11-27. The public CLI and Python API, host protocol, packaged example and compatibility guards discharge GC2 on the verified implementation.

## Gate output

    1199 passed, 2 deselected in 142.52s (0:02:22)
    All checks passed!
    0 to fix, 0 warning(s), 10 to reread
    Installed CLI/API parity: 497 bytes. Example: ['work_has_version'] ['reuse', 'defer']
    Packaged validation, preview, apply and judgment commands passed: 8
    Wheel SHA-256: 1f388ac0532a3c192bae867aebd8cf03955748e09cc83862ffa231ae0bc8a9b5
    Valid fixture pairs with byte-identical views: 229

## Review and rulings
One reviewer is one reviewer. Claude identified mutable-model validation and host example coverage gaps. The missing refusal and the stale included-row refusal both reproduced before repair. The model loader now retains a digest for loaded include snapshots; changes to the composed vocabulary require reload before positional origins can be reused. The packaged example runs direct lookup, role-player retry, and ambiguous deferral with a document digest. The regression suite includes both missing refusals, role direction, record membership and installed surfaces. The third review found an existing reference-bearing loader path that accepts nonfinite free-form metadata. A failing regression test reproduced the compatibility problem; extracting the prior vocabulary-digest implementation preserved historical reference digests and fixed the regression. Claude approved the final repair. See the four GC2 rounds and their per-finding decisions.

## Refactoring review
Existing loader validation, model digest and composed-origin metadata supply the structural checks. The API shares the renderer with the CLI and delegates evolution to the existing preview/apply path. No new search or validation framework is necessary.

## Component sweep
Re-read checking, synthesis, codegen, conformance, measurement, evolution and recovery subsystem entries, model.loading, model.document and model.scalar_identity. The internal load-time digest adds no external loader operation; the updated command, API and rendering catalog entries identify the new surface.

## Boundary and open questions
Production ranking, automatic novelty decisions and empirical quality remain outside this milestone. The recorded pytest command is a focused public lane. The two deselected tests and opt-in historical and certification lanes carry no passing claim here.

