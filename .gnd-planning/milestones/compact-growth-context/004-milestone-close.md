---
milestone: compact-growth-context
station: milestone-close
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-27
gates:
  - command: "gnd review panel notes/close-request.json (six seats attempted)"
    exit: 0
  - command: "gnd review finalize evidence/close-panel-r1 notes/close-synthesis-r1.json"
    exit: 0
  - command: "pytest -q tests/test_growth_view.py tests/test_growth_projection.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_model_verbalization.py tests/test_mc2_consumers.py tests/test_include_root_close.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py tests/test_unattended_growth_guidance.py tests/test_atom_bind.py tests/test_rf1_layering.py tests/test_evolve_loading.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py --tb=short tests/test_rf1_cli_pins.py"
    exit: 0
  - command: "ruff check"
    exit: 0
  - command: "python scripts/components_index.py --check"
    exit: 0
  - command: "Installed wheel interpreter runs evidence/verify_install.py from the source checkout"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/compact-growth-context/001-plan-gate.md
    sha256: 5ed6327c042704120ba840754d8034a2954f33058e3cade37459c6d7b9e77c03
  - path: .gnd-planning/milestones/compact-growth-context/002-phase-GC1.md
    sha256: 656fdd81c3da03e19d7957c8c9ad1d63daeb9063df8280738333d0b29c138cea
  - path: .gnd-planning/milestones/compact-growth-context/003-phase-GC2.md
    sha256: 6e0b9de7bb73176e9c04a09c3a6ad25fd574f453b4bb426e0570e7b018d5d2c3
  - path: .gnd-planning/milestones/compact-growth-context/notes/compact-growth-context-plan.md
    sha256: a4560bef76726de7d77933996fba7017f02f60dbc80bcd81218f3ce8cbe3571e
  - path: .gnd-planning/milestones/compact-growth-context/notes/close-delta.md
    sha256: fb12f51741ee7c814beb62dd16144af939065dde2b823d74fd1446bd5fd270ac
  - path: .gnd-planning/milestones/compact-growth-context/notes/close-panel-r1.md
    sha256: ae9666e541fb45d46dc8690792b908be6b7ea0acb76ab6df3f5592ac1ed38975
  - path: .gnd-planning/milestones/compact-growth-context/notes/close-replay.md
    sha256: da5117cf6d187492d26a7aef4bcdeef995e374865563df4753864d6886e07830
  - path: .gnd-planning/milestones/compact-growth-context/evidence/verify_install.py
    sha256: 27c06dd92e8d0e559cc728b6fceb5587d72138c521982ff143a003f28ddabe65
  - path: .gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-occurrence/review.md
    sha256: d3b354b7c704c16351c50bf96b42071138ed2406ed40a47a97f0f96f8f125702
---

# Compact growth context for issue 295

## Ruling
Delegated coordinator decision (auto=true), 2026-11-27. Accept GC1, GC2 and the close-review repairs for the owner-selected two-phase product milestone. The two numbered phase records establish their own gates. The final shipped example and public behavior are bound to commit 066d2f3d. The later records retain independent findings and measurements. PR 341 carries these changes to main for the owner's merge decision.

## Gate output

    1334 passed, 2 deselected in 144.75s (0:02:24)
    All checks passed!
    Path and loaded-model pairs with identical bytes: 229
    Installed CLI/API bytes: 497. SHA-256: b3be4910c0e937e8db09eba4d7f1f5727b1439e957930e3ac3b57da23fbf6b23
    Packaged commands passed: 8. Direct, retry, defer and reversal verified.
    Final wheel SHA-256: 159165900c599d0d19db2f9325ae0ce9d24e8c9f2eedb727ebaad5ea8ae6da3c

The fixture contains 16,927 source bytes. The ordinary rendering uses 31,742 bytes and the complete growth inventory uses 8,864 bytes. The host controls prompts, search and evidence interpretation.

## Close review and dispositions
The full panel attempted all six seats on the plan, GC2 record and close delta. Claude, Codex, Qwen, Kimi and GLM returned valid responses. Gemini returned malformed output and contributed no opinion. Five exceeds the project's four-reviewer bar. Finalization validated two agreed concerns and ten divergent concerns. The panel assessed the pre-repair close candidate. The replay note dispositions the concerns and gives exact commands for the final artifact. Independent Claude diff review then assessed the repaired example and receipt. Historical phase wheel hashes belong to their respective builds.

## Refactoring review
The source-span example verifies named assignments directly. No schema placeholder parser or retrieval policy is needed in the host. The model vocabulary digest reuses the previous positional digest calculation. Reference identity and the existing evolution CAS are separate.

## Open questions and boundaries
The register contains no outstanding issue-295 rows. Optional full-rule inspection remains necessary for semantic equivalence, and an inconclusive search may end in deferral. The narrower rule signature, host-owned ranking, absence of end-to-end recall or cost claims, and explicit merge and release boundary are accepted residuals. The project guard lane deselected two tests. No opt-in historical certification or paid grower evaluation was part of this close.

The first GC1 review launch produced a CLI usage error. It is retained as failed evidence and never counted. The review helper marks the changed product bytes as reviewed. Review and tests establish the recorded artifact properties; the owner retains publication authority.


The final independent diff verdict was APPROVE. The scope of the span check is textual consistency within the selected occurrence. The coding agent must still judge whether the cited text establishes the fact and its direction. The worked source file is ASCII; full Unicode occurrence-coverage expansion is deferred.
