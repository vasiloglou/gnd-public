---
milestone: ossie-interchange
station: merged-main closure
skill: process-milestone
scope: milestone-close
date: 2026-11-10
gates:
  - command: "git diff --exit-code c6fce9c162d943dabc81f8938157f5497e88d93d 85f54b55edd76a3e546e04675ae978b4620a199a"
    exit: 0
  - command: "UV_OFFLINE=1 uv sync --locked --group docs --group dev"
    exit: 0
  - command: "UV_OFFLINE=1 uv run pytest -q tests/test_ossie_consumer.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_ossie_formulas.py tests/test_ossie_import.py tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short"
    exit: 0
  - command: "UV_OFFLINE=1 uv run pytest -q tests/test_plan_app_docs.py -k ossie --tb=short"
    exit: 0
  - command: "UV_OFFLINE=1 uv run --group docs zensical build --strict"
    exit: 0
  - command: "UV_OFFLINE=1 uv run python tools/check_docs.py site"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/ossie-interchange/notes/ossie-interchange-plan.md sha256 bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/ossie-interchange/notes/ossie-interchange-plan.md
    sha256: bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8
  - path: .gnd-planning/milestones/ossie-interchange/notes/close-amendments-r2.md
    sha256: 9fc6b76d028351e4660bdbe5c23c6783aab51ddbe3cf37339bd8aca563d0118b
  - path: .gnd-planning/milestones/ossie-interchange/033-close-readiness.md
    sha256: a1cd3b5db037b7e7f929cb6be366b55f2b9f30b62aa3ed2adf5d7fba0d7402e4
  - path: .gnd-planning/milestones/ossie-interchange/032-panel.md
    sha256: 72cfceb27fb123dfc554fac8a81c1cde8d3bd72c769289fc4d5c2a261db007df
---

# Ossie interchange milestone close

[PR #160](https://github.com/vasiloglou/gnd-public/pull/160) merged the
owner-approved head `c6fce9c162d943dabc81f8938157f5497e88d93d`
into `main` at `85f54b55edd76a3e546e04675ae978b4620a199a`
on 2026-11-10 at 9:50 p.m. Eastern. The merged tree
`072a1fdd9ccd6f1cf5877ac74d944fdd71347c27` is identical to the approved topic tree. The existing
pinned oracle observations still apply to the matching source, fixtures,
and pin evidence.

## Gate output

The post-merge gates ran in a clean checkout of the merge commit with
the locked dependencies. The initial sandboxed setup was refused when
uv tried to open its default cache. The offline run using the existing
cache completed the gate.

```text
352 passed, 88 deselected in 15.25s
6 passed, 86 deselected in 0.07s
Build started
No issues found
Build finished in 0.91s
16448 local links/assets/anchors checked
```

GitHub's rendered normative format reference on main contains
`href="#ossie-interchange"`. The [public anchor](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#ossie-interchange)
therefore resolves to the merged format documentation.

## Independent review and phase records

The [light close panel](032-panel.md) retained five valid opinions,
with a malformed Gemini response. The [close-readiness record](033-close-readiness.md)
links the seven phase records and accounts for the panel findings.
The [effective amendment](notes/close-amendments-r2.md) preserves
the r3 predicates and cites their measured scope.

## Close ruling

**Delegated approval (auto=true), 2026-11-10.** Under the owner's
`gnd:process-milestone ossie-interchange auto` authorization, close
`ossie-interchange` against the amended plan SHA-256
`bb58891507c6b4cd209939a06ae416877ff1b827af35fcde928ec1290a9b13b8`. The owner authorized the exact GND merge in the
same conversation. The merged-main checks satisfy the condition in
record 033. This is the driving agent's milestone ruling. The only paid
close review was the separately owner-authorized high-effort light
panel bound in record 032.

## Open questions and residuals

- [Apache Ossie Converters PR #162](https://github.com/apache/ossie-converters/pull/162)
  carries the upstream contribution at
  `977cbb942c5458374192bb798a8a20320cca06f0`. Upstream review carries
  forward under that PR.
- The pinned RelationalAI SDK omits the compiled value-tuple requirements
  from generated source. The two intact converter refusals remain
  documented in OS4 and OS6.
- The existing paragraph-policy failure on `grow-a-model.md` remains
  with GND documentation maintenance.

## Boundary

Closure covers GND's measured ontology interchange scope and the
recorded pinned observations. The post-merge gates exercise the census,
ordinary importer and exporter behavior, affected docs, and local site
build. The GitHub Pages deployment uses its separate workflow.
