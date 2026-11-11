---
milestone: ossie-interchange
station: pre-merge close readiness
skill: process-milestone
scope: close-readiness
date: 2026-11-10
gates:
  - command: "ruling: delegated (auto=true) amended .gnd-planning/milestones/ossie-interchange/notes/ossie-interchange-plan.md sha256 bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8"
    exit: "n/a -- ruling"
  - command: ".venv/bin/pytest -q tests/test_ossie_consumer.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_ossie_formulas.py tests/test_ossie_import.py tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short"
    exit: 0
  - command: ".venv/bin/pytest -q tests/test_plan_app_docs.py -k ossie --tb=short"
    exit: 0
  - command: ".venv/bin/zensical build --strict"
    exit: 0
  - command: ".venv/bin/python tools/check_docs.py site"
    exit: 0
  - command: "pytest -q 'tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[grow-a-model.md]' --tb=short (main baseline 54483d03)"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/ossie-interchange/notes/ossie-interchange-plan.md
    sha256: bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8
  - path: .gnd-planning/milestones/ossie-interchange/notes/close-amendments-r2.md
    sha256: 9fc6b76d028351e4660bdbe5c23c6783aab51ddbe3cf37339bd8aca563d0118b
  - path: .gnd-planning/milestones/ossie-interchange/032-panel.md
    sha256: 72cfceb27fb123dfc554fac8a81c1cde8d3bd72c769289fc4d5c2a261db007df
  - path: .gnd-planning/milestones/ossie-interchange/evidence/OS4/reviewed/consumer-limitations.json
    sha256: b5a0981e8c925d4ddd0725a47ff2fd240499429e9b22f2fc108c5d20edad0116
  - path: .gnd-planning/milestones/ossie-interchange/evidence/OS6/reviewed/consumer-limitations.json
    sha256: def7d6b48da061def1b816d152b94acf92eabf170725b95694edac9951d3206c
---

# Ossie interchange close readiness

All seven phase records are complete. The
[independent close panel](032-panel.md) exited 0 with five of six valid
responses and requested revisions. The
[effective amendment](notes/close-amendments-r2.md) addresses those
findings and preserves the r3 wording. The milestone remains open
until the owner's GND merge decision and verification on merged main.

## Delegated amendment ruling

**Delegated amendment (auto=true), 2026-11-10.** The owner's
`gnd:process-milestone ossie-interchange auto` invocation authorizes
amendments for this milestone. Adopt the measured scope for predicates
1–6 and 9 and OS6-C2 in `notes/close-amendments-r2.md`,
SHA-256 `9fc6b76d028351e4660bdbe5c23c6783aab51ddbe3cf37339bd8aca563d0118b`. The amended canonical plan
SHA-256 is `bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8`. This is the driving agent's
amendment ruling. The owner separately selected one high-effort light
panel run. The ruling preserves the on-main condition, and GND merge
authority remains with the owner.

## Phase records and verification

| Phase | Evidence |
|---|---|
| OS0 | [Pin and census](006-phase-OS0.md) |
| OS1 | [Exporter and validator/parser gate](009-phase-OS1.md) |
| OS2 | [Renderer, authored corpus and parity](014-phase-OS2.md) |
| OS3 | [Importer, refusal controls and census round trips](020-phase-OS3.md) |
| OS4 | [Pinned offline consumer comparison](021-phase-OS4.md) |
| OS5 | [Documentation and refunds replay](025-phase-OS5.md) |
| OS6 | [Upstream suite, replay and approved PR publication](030-phase-OS6.md) |

The updated focused topic-branch selection exited 0 with
`352 passed, 88 deselected in 14.86s`. It exercises the full census
export and import, formula and consumer controls, existing PyRel rules,
CLI and layering. The documentation update at `6547f97b` uses prose
from Claude Fable 5.2 with light editing. The final Ossie documentation
gate exited 0 with `6 passed, 86 deselected in 0.06s`. The strict
site build reported `No issues found` and the link checker reported
`16448 local links/assets/anchors checked`.

The paragraph-policy test exited 1 on an isolated archive of baseline
main `54483d03e1033df49adb993f58a6d1a80f7b35f5` with
`assert 141 <= 90`. The page and test are unchanged from that baseline.
This is a documentation maintenance carryover outside the affected Ossie
pages.

## Merged-main condition

After the owner authorizes GND PR #160's merge, the driving agent will
check out the resulting main commit in an isolated checkout and record
its SHA-256-bound evidence in the next milestone record. Run these
checks from that checkout.

```sh
uv run pytest -q tests/test_ossie_consumer.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_ossie_formulas.py tests/test_ossie_import.py tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short
uv run pytest -q tests/test_plan_app_docs.py -k ossie --tb=short
uv run zensical build --strict
uv run python tools/check_docs.py site
```

The test selections include the census export and round trips.
Confirm the public GitHub link reaches the Ossie interchange anchor in
the merged normative format reference. Compare merged product source,
fixtures, and pin evidence with the tested topic branch. The existing
opt-in evidence applies to matching bytes and inputs. A change in that
scope requires reevaluating the affected gate before ruling on closure.
Record the final milestone ruling only after the merged-main evidence.

## Refuted premises and carryovers

- The [effective amendment](notes/close-amendments-r2.md) accounts for
  the 41-input denominator, three whole-input include refusals,
  unavailable embedded extension route, bounded formula shapes,
  temporal GND diff limit, two intact converter refusals, and absent
  generated source for the replayed GND requirements.
- The RelationalAI SDK source generator still omits compiled value-tuple
  requirements. The composition-chain and inherited-identifier
  converter refusals remain pinned consumer limits. The OS4 and OS6
  consumer reports retain those outcomes.
- [Apache Ossie Converters PR #162](https://github.com/apache/ossie-converters/pull/162)
  was open at the verified head `977cbb942c5458374192bb798a8a20320cca06f0`.
  Its upstream review carries forward under the published PR.
- The GND documentation maintenance carryover is the existing
  `grow-a-model.md` paragraph-policy failure.

## Boundary

The readiness checks apply to the topic branch. GND main verification
and the final milestone ruling remain pending. The scoped claim covers
Apache Ossie ontology interchange and the recorded offline observations.
