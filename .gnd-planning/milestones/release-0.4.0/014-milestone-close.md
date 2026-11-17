---
milestone: release-0.4.0
station: milestone-close
scope: milestone-close
date: 2026-11-17
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
source_base: 9371d8e39e661d4953a228670a36411063f2aa74
gates:
  - command: "bash evidence/close/run-shards.sh via SSH on beast-3 at main 9371d8e39e661d4953a228670a36411063f2aa74"
    exit: "1, 0, 0, 0, 0, 0"
  - command: "python3 .gnd-planning/milestones/release-0.4.0/evidence/close/verify-close.py"
    exit: 0
  - command: "uv run --no-sync python tools/release_text.py check"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_release_version.py tests/test_release_text.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run --no-sync ruff check --output-format json"
    exit: 1
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900 --max-output-bytes 8388608"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.4.0/012-close-candidate.md sha256 f88fb22e234f6f732b2561904229b15275e9116fd116b9fa167e16b952a0d195 with the committed dispositions in .gnd-planning/milestones/release-0.4.0/evidence/close-panel/disposition.md sha256 066a31cfd3fb520f21af31ff551831ef77ca4e98a19897ae345e25cd783ea914"
    exit: "n/a -- ruling"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.4.0/notes/release-0.4.0-plan.md sha256 f5ea73ae1ac3b871185ae2e97facf107e5832bb086db79ef88bfe623f248a075"
    exit: "n/a -- ruling"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner selection"
  reason: "Excluded under RV-D8."
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/001-plan-gate.md
    sha256: 5ff5b7b8c06bf458391a05d9777b8c3ab3106cfd1cfce1e595a4a4aeaa1a64c3
  - path: .gnd-planning/milestones/release-0.4.0/003-RV1-implementation-gate.md
    sha256: cf2ceff6a69ea830b6f510ff3c0a6be73a895fd519fd3c5220d66b61ba6f0463
  - path: .gnd-planning/milestones/release-0.4.0/005-phase-RV1.md
    sha256: 8847be0c29f8c0cc0511b813592ad0fecdccb134c305fabbc84b42243e792bf3
  - path: .gnd-planning/milestones/release-0.4.0/006-RV2-spec-gate.md
    sha256: 21e70701f808f3ef3860e1115d117a32ddd35cda4164d0d177bb1bb8139629f2
  - path: .gnd-planning/milestones/release-0.4.0/008-phase-RV2.md
    sha256: 361ccfce855668c338f667dcf6206a8b9a73b879bf3c1514b77c25ae12a6cc04
  - path: .gnd-planning/milestones/release-0.4.0/009-RV3-spec-gate.md
    sha256: c1282b73e76b1eecefc5df0d70b79235cecf9f0c4462eb1480c4568561cc1f44
  - path: .gnd-planning/milestones/release-0.4.0/010-phase-RV3.md
    sha256: bc31d884b90eb00da31b3682fdb0989eb8ae0605e7b0e2b045d8bf6ffaf7d3d2
  - path: .gnd-planning/milestones/release-0.4.0/011-publication.md
    sha256: 22b3b27c6d870fc82a0eb22a752aeb1fff0b9e94e23c991dadef3c5a44d6eacd
  - path: .gnd-planning/milestones/release-0.4.0/012-close-candidate.md
    sha256: f88fb22e234f6f732b2561904229b15275e9116fd116b9fa167e16b952a0d195
  - path: .gnd-planning/milestones/release-0.4.0/013-close-panel.md
    sha256: 75323160aac0956458c402a9631754c47b8566be3e1c31addf5a22c708f896c0
  - path: .gnd-planning/milestones/release-0.4.0/notes/release-0.4.0-plan.md
    sha256: f5ea73ae1ac3b871185ae2e97facf107e5832bb086db79ef88bfe623f248a075
  - path: .gnd-planning/milestones/release-0.4.0/notes/close-question-sweep.md
    sha256: 58d73903e1680dbefd7cf2511ca0852ef95d90d189c7617c8181bea160ad70d0
  - path: .gnd-planning/milestones/release-0.4.0/evidence/baseline-remote-state.txt
    sha256: 88725f4aee8e25643619e4d5cac97b8d84edcdc0b6fc713193d090951468b94f
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/pre-publication-state.txt
    sha256: 2a6f2e7c7ebf326172948146d7ee4a0625333ccc11afc5de99beddf568b83aae
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/e1-moved-bytes.txt
    sha256: d4641e81af7a1f3590e8e3cd1cc6924c545fa1ad7e74f2dd116cfbf581bafcdf
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/version-inventory.txt
    sha256: e21242785ed8d6f6d2b5f99106fb312c9ae267ee89f40f93422c954083c33651
  - path: .gnd-planning/milestones/release-0.4.0/evidence/plan-r1/PANEL-REVIEW.md
    sha256: cd1afe957dd90d7394b3af2b2c78db2a42de2213750c8b8082e72b9495ca697c
  - path: .gnd-planning/milestones/release-0.4.0/evidence/plan-r1/review-request.json
    sha256: a35dd4124b03830d0af549cb481cb7d7e4f48f1f6b1e94856eb09757bb493d0e
  - path: .gnd-planning/milestones/release-0.4.0/evidence/plan-r1/synthesis.json
    sha256: 36a23d5bc83664679389a4ae1d4761560d15f550e214f4a92bd8d0e7474fa632
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/default-lane.txt
    sha256: 4256f83a7d9410b96ed0acc328d249ae903804b8f085a2099cf6b8e8bdefd78c
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/remote-state.txt
    sha256: 29bc87774878dbd96130b29a385ceaf9f17663dc09bd7b671fb678c4fb6754ec
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/audit-comparison.txt
    sha256: 7b02823e77f20b6cdf81641acd1af246d2ec16c085d270908d12e92b933b2b02
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/command-audit.txt
    sha256: 54035d119d8b5d7e30d2a07f3bee7bcb7bbe995cb8293a8bf444bd01e6675fbc
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/verify-close.py
    sha256: b236a4bd41e18770177a0e7b83c01ebaef7433e74a82a0a8cf395968faac5c56
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/post-panel-focused.txt
    sha256: b4b2de1239ea079f9f1497a3032c4849d44fc429d286bfdb229d4f5d609d763f
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/phase-review-status.txt
    sha256: 965ef38a7063143c6b3d5baf2c18e12a21157f70f65692dcfc35389497907000
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close-panel/PANEL-REVIEW.md
    sha256: e53024915d4e6068f87efa8ad6af22c0cf5d69c529bb072932f365bab10f56f4
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close-panel/disposition.md
    sha256: 066a31cfd3fb520f21af31ff551831ef77ca4e98a19897ae345e25cd783ea914
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close-panel/synthesis.json
    sha256: 6c9d6beb6070f83163df8e872c514c14a7782e3d958eb3c164927ce07f0773a0
---

# Release 0.4.0 closed under delegated approval

All three mandatory phases RV1–RV3 are complete. GND 0.4.0 is published on
[PyPI](https://pypi.org/project/get-nick-done/0.4.0/) and as the
[GitHub release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.4.0).
PR 211 merged the publication pages into main at
`9371d8e39e661d4953a228670a36411063f2aa74`. The owner expressly requested
“merge. and close” on 2026-11-17. The milestone's original auto delegation and
that current close request supply the final ruling below.

## Phase evidence and exit predicates

| Predicate | Established evidence |
|---|---|
| 1 Version consistency | [RV1](005-phase-RV1.md) and the close-focused tests. The source version, lock and .claude-plugin/plugin.json, .codex-plugin/plugin.json and .claude-plugin/marketplace.json declare 0.4.0. Published installation and release pages are on main. |
| 2 E1 and inventory | [Measured gate](003-RV1-implementation-gate.md), [classified inventory](evidence/RV1/version-inventory.txt) and [twelve-output measurement](evidence/RV1/e1-moved-bytes.txt). The committed example bytes are identical across cc4c8bf0..9371d8e3, asserted by [the exact command audit](evidence/close/command-audit.txt). |
| 3 Notes reconciliation | [RV1](005-phase-RV1.md) and its two-tag-range reconciliation. Published notes cover the full literature work and the guarded changes, with the 0.3.1 carryover labelled for PyPI 0.3.0 users. |
| 4 Installed probes | [RV2](008-phase-RV2.md). Both wheel origins were installed outside the source checkout, and all five probes and their candidate and public 0.3.0 controls ran. |
| 5 Installed acceptance | [RV2](008-phase-RV2.md): 23 passed in 920.19s on macOS 27.0.1 arm64/Python 3.11.18/uv 0.10.10. |
| 6 Hand-over | [RV3](010-phase-RV3.md) binds the dossier, scratch helper and supplemental patch. [Publication](011-publication.md) binds the later actual helper use and its docs PR, which merged as PR 211. |
| 7 Separate owner actions | [Publication authority table and receipts](011-publication.md), direct baseline and pre-publication snapshot digests above, [closing remote state](evidence/close/remote-state.txt), [snapshot comparison](evidence/close/audit-comparison.txt) and [exact diff commands](evidence/close/command-audit.txt). The delta contains the authorized tag, release and two matching PyPI files. No .github change, new environment or release workflow run occurred. |
| 8 Publication identity | [Publication](011-publication.md) binds exact PyPI served bytes, downloaded assets, source tag and fresh public-index smoke. The publication pages merged into main through owner-authorized PR 211. |
| 9 Phase and close record | Phase specs and evidence digests revalidated. The [standard close panel](013-close-panel.md) is finalized and every finding has a [disposition](evidence/close-panel/disposition.md). The distinct delegated close ruling follows. |

## Closing verification

The default lane ran on beast-3, macOS 27.0.1 arm64, Python 3.13.18 and
uv 0.13.7. It reported 19,699 passes and 13 skips. Shard 0 exited 1 solely
with the two known optional-wheel setup errors shown below. The other five
shards exited 0. The executable audit verifies that precise attribution
against the retained shard summaries. Runtime source and build inputs match
the accepted candidate `648cc6e0` by exact path-scoped git diff.
Documentation and release-state tests changed through PR 211 and passed the
closing lane.

The post-panel focused command ran on the close branch at head
`5294cef5` with planning-only repairs listed in its retained receipt.
It passed 159 tests with one deselection. The publication-text check exited
0. Full Ruff exited 1 with the exact 188 shared-tool diagnostics reproduced
on the base. Current-byte changes are planning and evidence only.

## Close review and disposition

The standard command attempted six fixed IDs over five executable CLIs.
Claude, Codex, Qwen and GLM returned complete valid responses. Gemini and Kimi
were malformed because their output contained no JSON object and supplied no
opinions. The command and finalization each exited 0. Four valid responses
meet both the runtime quorum and the project's four-reviewer bar.
The finalized advisory report groups two agreed concerns and retains
13 divergent views. Claude had one conservatively unanchored concern.

Codex and GLM approved. Claude and Qwen requested revisions. The agent
reproduced the traceability issues, retained exact audit commands, bound the
baseline snapshot directly, labelled the plan amendment and added stable
carryover destinations. The remaining concerns were either disproved by
retained bytes or accepted as the explicitly bounded residuals below.
There was no second close panel round. The original opinions bind the
candidate digest, while the post-panel audit and focused checks cover the
repaired evidence. The final ruling supplies acceptance independently.

## Open-questions sweep and plan repair

The [complete sweep](notes/close-question-sweep.md) inventories all numbered
records 001–011, plan decisions, the three review ledgers and relevant
predecessor carryovers. The [close review disposition](evidence/close-panel/disposition.md)
accounts for all 17 final-panel concerns. Every row is closed, assigned a
durable RC-01..RC-07 destination, retired or accepted as a residual.

Plan §12 corrects the E1 expectation, incomplete literature outline and
actual installed-probe count. The final plan is labelled r2 plus the close
amendment. Its digest differs from the previously approved r2
`e9828d47fcf6429f85a9869e29972d75e8efb706dd5d2e0d0f0fb6062b3be7ed`.
The amendment retains the previous wording in history and is expressly
approved by the separate ruling below.

## Gate output (verbatim selected lines)

    2489 passed, 125 deselected, 2 errors in 443.65s (0:07:23)
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    3941 passed, 102 deselected in 392.38s (0:06:32)
    2796 passed, 13 skipped, 184 deselected in 491.11s (0:08:11)
    3538 passed, 123 deselected in 624.94s (0:10:24)
    3888 passed, 71 deselected in 711.60s (0:11:51)
    3047 passed, 255 deselected, 1 warning in 757.06s (0:12:37)
    159 passed, 1 deselected in 34.51s
    no page describes the state before 0.4.0 was published
    188 exact baseline diagnostics; comparison exit 0.

Full panel tool receipts are retained in [013](013-close-panel.md).
Exact commands and focused exits are in the digest-bound evidence above.

## Delegated rulings, 2026-11-17

> Delegated approval (auto=true). Authority is the owner's explicit
> process-milestone release-0.4.0 auto instruction, standard GND instrument
> selection and current “merge. and close” request. Accept the three completed
> phases and the publication result described by 012, subject to the exact
> committed close-panel dispositions. Approve the current plan's §12 repairs,
> all sweep dispositions and the bounded residuals below. Review budget was
> one standard six-seat panel round with a 600-second per-seat timeout,
> 900-second overall timeout and 8 MiB per-invocation output ceiling.
> The milestone is closed. This ruling is separate from the command exits
> and advisory reviewer opinions.

The gates above bind the exact accepted candidate, disposition and amended
plan SHA-256 values. The close record and its PR are evidence publication
under the named milestone. Merge remains governed by AGENTS.md.

## Refactoring review

RV1 revised test consumers to reuse recorded-version helpers and a stable
synthetic release page fixture. RV2 reused isolated installed-artifact
helpers and tightened source binding. RV3 reused the canonical release-text
helper. No runtime refactor was deferred. The inherited shared-tool lint
findings and the release checker wording gap have durable named destinations
in the sweep.

## Accepted boundaries and residuals

- The two default-lane setup errors and 188 baseline Ruff findings remain
  visible and assigned to RC-01/RC-02. This close establishes their measured
  equality, along with the selected passing behavior.
- The formal acceptance and fresh-install profiles are exactly those in
  RV2 and publication. Additional platforms, external/native/provider
  historical lanes, certification, announcements, Trusted Publishing and
  TestPyPI were outside the selected milestone.
- Token upload rights were observed. PyPI account ownership and a separate
  human repository content/history audit remain unrecorded, with RC-07
  assigned to the owner. Owner authorizations are retained as dated
  conversation-derived records in 011, while tool receipts establish acts.
- Old-release availability controls depend on the public 0.3.0 wheel and
  index-resolved dependencies. Their observed results and whole-file hash
  are retained without a guarantee of future external availability.
- Each phase and close review binds its own original bytes. Post-review
  repairs have recorded executable checks. Panel results are advisory.
  Raw plan and close panel archives remain local, digest-bound outside Git;
  request, synthesis and finalized reports are committed.
- The GitHub tag and accepted files stay bound to `648cc6e0`. The
  published-state main tree is `9371d8e3`. Later close evidence does not
  rebuild or change the released files.
