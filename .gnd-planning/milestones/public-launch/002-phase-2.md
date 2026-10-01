---
milestone: public-launch
station: "phase-2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-2
date: 2026-10-01
gate:
  command: "uv run pytest -q tests/test_development_scaffold.py tests/test_review_credential_launcher.py"
  exit: 0
  output: "43 passed in 0.56s"
slow_gate:
  command: "uv run pytest -q -o addopts='' tests/test_public_runtime.py tests/test_public_distribution.py tests/test_development_scaffold.py tests/test_review_credential_launcher.py"
  exit: 0
  output: "75 passed in 8.71s"
  note: "Explicit bounded P2 distribution selection; no broad historical replay. Exact profile guard follow-up also exited 0."
evidence:
  - path: migration/b2-files.json
    sha256: 9d19ae337c5b75e5ae4d615674a3685f1301b124a25a5d573ee25cb34319efe0
  - path: ../../../tests/fixtures/public-launch-phase-2/identities.json
    sha256: 26aa74fe55cffe4440e8bec9070e57fd9451af0f6c3e89da1ae90a507633aaa7
---

# Claim

The coherent target package built and ran outside both checkouts with the selected
CLI/API/resource/assurance checks exiting as declared. Local combined gate exits
0 (75 cases); hosted Ubuntu Python 3.11.16 gate exits 0 (43 default + 32 package).
All units remain source-owned; this is a private non-releaseable migration stage.

## What shipped

230 source-identical runtime paths, including all 53 early B1 files; 150 Python
files and 80 resources. Package names, metadata version 0.1.0, base-three and
optional synth dependency policy preserved. Public test configuration has no
private Git/history hooks; current successors are mapped in
[migration/b2-test-successors.md](migration/b2-test-successors.md).
Own installer generated 16 links per discovery root. Both unmanaged skills are
real identical twins; machine receipts remain ignored. Contributor docs now state
current staging honestly. P2 build profile uses uv 0.10.10; P4 decides release tooling.

## Gate output (verbatim summaries)

```text
uv run pytest -q tests/test_development_scaffold.py tests/test_review_credential_launcher.py
43 passed in 0.56s
exit 0

uv run pytest -q -o addopts='' tests/test_public_runtime.py tests/test_public_distribution.py tests/test_development_scaffold.py tests/test_review_credential_launcher.py
75 passed in 8.71s
exit 0

uv run pytest -q -o addopts='' tests/test_public_distribution.py::test_artifact_and_installed_resource_sets
1 passed in 1.12s
exit 0

uv run ruff check tests/conftest.py tests/test_public_runtime.py tests/test_public_distribution.py tests/support/public_probe.py tests/support/public_release_fixture.py
All checks passed!
exit 0

git diff --cached --check
exit 0 (empty output)
```

[Hosted gate](https://github.com/vasiloglou/gnd-public/actions/runs/36929617118)
at `3da7be7f76049a723303589f6de0f5d3658c5b87`: `43 passed in 0.53s`,
`32 passed in 16.84s`. Actual Linux link identity is included; no certification.

## Verification selection and measurements

RUN: exact curated path/byte attribution; sdist-to-wheel rebuild, base-only venv
outside checkouts, exact package and whole-archive member sets, CLI/API cases,
missing/stale/corrupt reader controls, own install/doctor, contributor/credential
checks, whitespace and staged-content audit. Source-private observer separately
verified 232 Git/working/target identities and empty affected committed/working/
untracked deltas through source high-water d8ac975e080a428fd7e32aea493cad722e54f7d1.
Five semantic source/wheel payloads agree, excluding only assurance projection.
Two false-source-claim controls exit 1 after the accepting source observer exit 0.
INHERIT: immutable P0/P1 historical inventory/routing/receipts only, not current
behavior on changed bytes. NOT SELECTED: full advertised suite, broad historical
replay, native/oracle/provider/proof/certification. Their future selection needs
explicit scope. P3 and P4 gates remain pending, not inherited as green.

Measured wheel uncompressed 5,558,612 bytes, 65 skill files, 211 relative-link
occurrences / 167 unique edges. All within 12 MiB package, 64 MiB target,
1 MiB ordinary blob and 2 MiB authored public planning limits. Build artifacts
remain in selected private local storage by digest, not public Git. P4 emits its
own candidate; these are not promoted release bytes.

## Review and refactoring review

One reviewer is one reviewer. Full read-only review found link-mode portability,
named-cause oracle, and source-reconciliation evidence gaps; each reproduced.
Six regressions failed pre-fix, then green. Additional whole-archive hardening
rejects duplicates/extra members; malformed kind and stale README gaps repaired.
Narrow repair review found no remaining blocker in scope. Hosted first checkpoint
081e3a8 failed (3 failed, 29 passed) because latest uv 0.12.21 generated different
sdist metadata; a pin regression failed pre-fix, then the reviewed uv 0.10.10
profile passed actual hosted CI. Failures remain evidence, not silently discarded.
Two implementation passes; pass 2 included hosted integration verification.
No reviewer rebuilt artifacts or established a certification claim.

**None needed:** runtime/installer/schema/skill bytes moved unchanged; small
current harness and docs did not justify runtime refactoring. Existing source
artifact helper refactor remains OQ-V72-P1-ARTIFACT-COPIES with its original trigger.

## Boundary — what this does NOT establish

No full framework parity/coverage or optional-native/provider execution. No current
assurance certificate: omitted historical evidence is unavailable; synthetic
reader bundles have zero proved/covered rows and never ship. No authority
transfer, publisher, public visibility, upload, announcement or source retirement.
No P3 full acceptance or final P4-C5 contributor/release readiness. Source migration
originals remain canonical; source-private observations are not prerequisites for
running the bounded public target checks. Reviewer opinion is advisory reading.

## Open questions

- Original 218 source IDs/states, including 119 live potential overlaps, retained;
  original mints/owners/triggers remain. Reassess actual triggers before adaptations
  and any P3 handoff; no original question closed by packaging success.
- OQ-V72-P1-ARTIFACT-COPIES: source-owned v7.3 routing, named digest/CLI caller or
  v7.3-gate trigger, not discharged by move-only copying.
- OQ-V70-CLOSE-BROAD-REDS: unscheduled historical test hygiene, not closed.
- OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE: owner public-launch P4, before release gate;
  decide final supported build tools. Current P2 pins uv 0.10.10, no general claim.

## Refuted premises

Platform symlink permission bits are not a portable Git identity; pin link type,
value and target instead, keeping regular modes exact. Latest CI uv was not the
measured build profile; strict archive audit exposed this actual difference.
Neither premise changes the approved corpus answers or runtime contracts.
