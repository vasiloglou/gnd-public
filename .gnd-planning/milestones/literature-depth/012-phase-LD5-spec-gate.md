---
milestone: literature-depth
station: phase-LD5-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LD5-spec-gate
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld5_verdict.py --tb=short"
    exit: 1
    output: "9 errors in 0.15s"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD5-spec.md sha256 44022b8fa8cba692a5fabcad02dbdcc7a854bbb04cba21dbcc1894613db3d83c"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-depth/011-phase-LD4.md
    sha256: e108270204a5e5817e98c14b720f9a9a5aa835816a33e6c365553c6bebe48a75
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD5-spec.md
    sha256: 44022b8fa8cba692a5fabcad02dbdcc7a854bbb04cba21dbcc1894613db3d83c
  - path: tests/test_ld5_verdict.py
    sha256: bf40858311810fb6431fe2af0a6f103bdee805314889013a52d0f527dd208c1d
  - path: tests/fixtures/ld5-verdict/expected.json
    sha256: d7323c9cc5ffcea22768e984e434d683c0b79ab76e7118ce9801549dab8a314a
  - path: src/gnd/examples/literature/verdict_fixture/opinions.json
    sha256: 096613fa54def036cdeb4c85d137ec84fcfa1fae7b500bd080e56b01824276f2
---

# LD5 spec and corpus gate

The owner's `process-milestone literature-depth auto` invocation delegates
approval of the part 8 verdict fixture. The frozen corpus reached the expected
red at the absent example module. The inputs contain separate synthetic
source opinions pinned to observed release and revised-edition evidence.
The answer roster covers two, one, zero and renewed supports and independent
mutations of the shared and source bindings. No optional spec panel is
selected. The later independent diff review retains separate authorization.
