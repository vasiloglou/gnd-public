# RF0 baseline — measured architecture of `src/gnd`

Measured on 2026-10-05 at base `19b131b` (this branch merged with `main`
`cbb9783`; `src/gnd` is byte-identical to `main`). Every number below comes
from [`metrics-RF0.json`](../evidence/metrics-RF0.json), which
`uv run python tools/gnd_arch.py measure` produced under Python 3.14, or
from a command quoted where it is used. This file supersedes the
[architecture audit](../../../../docs/development/architecture-audit.md)'s
numbers. The audit stays as historical input.

Statuses follow RF0 decision D2: **confirmed** means the measured value
equals the audit's; **refuted** means the measurement contradicts it;
**unverifiable** means it can't be measured in this repository, for the
reason given.

## Scope

148 modules and 104,062 lines, with `src/gnd/examples/**` and
`src/gnd/skills/**` excluded. The largest modules are `cli.py` (9,088),
`model.py` (5,157), `checker.py` (5,143), `exp/session_store.py` (3,018)
and `exp/session_eval.py` (2,697). The tool records 842 import edges: 478
module-level, 358 lazy, 5 type-only and 1 dynamic.

## Audit-claims register

| # | Audit claim | Measured | Status |
|---|---|---|---|
| A1 | 454 module-level imports | 454 distinct module-level module pairs | confirmed |
| A2 | 185 imports that occur only inside functions | 184 lazy-only pairs, plus 1 dynamic pair (`semantic_spec.py:1613`, `__import__("gnd.terms")`) = 185 | confirmed (the audit counted the dynamic import as lazy) |
| A3 | The core is one 13-module cycle | The runtime SCC has **14** modules: the audit's 13 plus `gnd.semantic_spec`, which joins only through the dynamic edge `semantic_spec.py:1613 → gnd.terms` (checked by hand). Without dynamic edges the SCC is the audit's 13 | refuted (one more module) |
| A4 | 189 imports of another module's private names; 47 are `synth.boundary` → `synth.mutate` | 189 private from-imports; 47 from `synth.boundary` to `synth.mutate`. The tool also finds 53 private attribute accesses through module aliases | confirmed |
| A5 | ~51 canonical-JSON helpers in 30 files, ~35 digest helpers in 23 files, ~30 safe-filesystem helpers in 20 files | Name-pattern families ([helper-families.md](helper-families.md)): canonical JSON 18 sites; sha256-hex 12; file digest 5; safe filesystem 16. The audit's counting method isn't recorded | unverifiable (method); measured counts given |
| A6 | 11 canonical-bytes sites are identical apart from the trailing newline | None of the audit's named sites is AST-identical to another. They differ in type annotations, docstrings, `try` wrappers and model-dump preprocessing. Only three `canonical`-named functions share one AST (`conformance.report`, `coverage`, `fidelity.report`) | refuted under the D7 definition (finding F2) |
| A7 | `cli.py` 9,088 lines, 150 commits; `checker.py` 67 commits | 9,088 lines. Commit counts come from the private repository's history | lines confirmed; commits unverifiable (D3) |
| A8 | About 20 of ~35 commands carry their own domain logic | Needs a reading of each handler, not an import measurement | unverifiable by the tool; owned by the RF5 spec |
| A9 | `model.fact_types` read 152 times in 42 files; `.get("roles")` 141 times in 31 files | `.fact_types` attribute reads: 179 in 45 modules. `.get("roles")` calls: 145 in 31 modules | refuted (counts differ; the tool counts every attribute load) |
| A10 | `checker` and `model` changed together in 23 commits | Private history | unverifiable (D3) |
| A11 | Five session version axes; the version mapping written inline in at least 9 places; `session_v7` is a fork of `session` | Needs reading, not import measurement | unverifiable by the tool; owned by the RF8 spec |
| A12 | Three `model_digest` meanings (`conformance/currency`, `transition.py:185`, `synth/provenance.py:228`) | All three exist. Two more sites match the family: `population._model_digest` (line 262) and `references.reference_model_digest` (line 157). All five AST hashes differ | refuted ("three"); the RF2 spec must cover five |
| A13 | `SESSION_CONTRACT_VERSION` is assigned 2 at line 64 and reassigned at 483 (the plan called the first assignment dead) | Both assignments exist. Line 482 captures the first as `V2_SESSION_CONTRACT_VERSION` for the frozen v2 reader, so it is **not dead** | refuted (finding F1) |
| A14 | ~14 test files monkeypatch `gnd.cli` privates (the plan's r1 said 12) | 12 test files patch a `gnd.cli` target (17 patch sites) | refuted for ~14; matches the plan's 12 |
| A15 | ~60 test imports reach into `synth.assemble`/`synth.mutate` privates | 54 sites in 12 test files | refuted (count) |
| A16 | `agent_cli ↔ exp`; 8 of `agent_cli`'s 10 importers need only the runner | `agent_cli` imports no `gnd` module, so there is no cycle. It has 10 importers. Which parts each importer needs requires reading | importer count confirmed; cycle refuted; the rest is owned by the RF4 spec |
| A17 | Wrong-way imports `model → popvalidate` (2003, 2649, 2794), `model → population` (4883), `model → references` (4903–4933), `terms → model` (111), `diff → api` (227), `assemble → mutate` (1764) | All present at the stated lines, as lazy edges | confirmed |
| A18 | `references`, `proof_bridge`, `semantic_adapter → checker`; `semantic_registry` → checker, model, popvalidate, proof_bridge, terms | All present (`semantic_adapter → checker` is module-level at lines 16 and 19; the others are lazy) | confirmed |
| A19 | `codegen`, `synth`, `extract`, `evolve`, `cli → install` | Importers of `gnd.install`: `cli`, `codegen.emit`, `codegen.manifest`, `codegen.plan`, `evolve.service`, `extract.manifest`, `synth.paths` | confirmed |

## Cycle register (RF0-C2, D10)

Runtime SCCs are computed over module-level, lazy and dynamic edges.
Module-level edges alone form no cycle.

| Cycle | Audit | Measured | Assigned to |
|---|---|---|---|
| Core | 13 modules | 14 (A3). `semantic_spec` joins only through `semantic_spec.py:1613` | RF3 |
| Assurance | `assurance`, `assurance_claims`, `assurance_evidence`, `assurance_inheritance` | Same four modules | RF4 |
| Session | 7 `exp` modules | Same seven: `session`, `session_eval`, `session_judgments`, `session_patch`, `session_store`, `session_v7`, `tests_runner` | RF8 |
| Synth | `assemble` ↔ `mutate` | Confirmed (`mutate.py:74` module-level, `assemble.py:1764` lazy) | RF4 |
| `api` ↔ `diff` | named | Confirmed (`diff.py:227` lazy) | RF4 |
| `agent_cli` ↔ `exp` | named as a back-edge | Refuted: no edge from `agent_cli` | none |
| New SCCs | — | None | — |

The allow-list is empty (count 0). Under D10 that count may not grow in any
later phase.

## Layering

The six layers follow RF0 decision D5. All 148 modules are assigned in
[`tools/gnd_layers.json`](../../../../tools/gnd_layers.json). Measured:
27 wrong-way runtime edges, 54 cross-lane edges, and two clean layers
(`entry` and `infrastructure`, recorded as `declared_clean`).

| From → to layer | Edges | Examples |
|---|---|---|
| checking → semantics | 8 | `checker → correspondence` (lazy ×4), `checker → proof_bridge`, `proof_kernel`, `semantic_registry` (module-level, lines 53–61) |
| lanes → entry | 8 | `exp.session*` → `report` (5); `export.lean_cli`, `export.souffle_cli`, `witness.cli` → `api` |
| checking → lanes | 5 | `checker → extract.anchors`, `extract.identity`; `model_verbalization → extract.refscheme`, `extract.vocabulary`; `verbalize_population → extract.anchors` |
| model → checking | 3 | `model → verbalize`, `popvalidate → verbalize`, `references → checker` |
| model → semantics | 1 | `references → transition` (lazy, line 159) |
| semantics → entry | 1 | `admission_validation → report` |
| semantics → lanes | 1 | `judgments → extract.manifest` |

These edges are the input to RF1's per-edge strict xfail markers (routed
concern F2(B)).

### Layer assignments that depart from or extend the audit's component map

- `redaction`: audit said infrastructure; assigned **semantics**, because
  it imports `model`, `semantic_registry` and `terms`. As infrastructure it
  would contribute three wrong-way edges for a module whose role is
  report-level redaction.
- Not in the audit's map:
  - `gnd` (package init, imports only `importlib.metadata`),
    `architecture` (declaration loader; imports only `artifacts`) and
    `yaml_comments` → infrastructure;
  - `extraction_scope`, `model_identity` and `patterns` → model;
  - `semantic_ir`, `proof_currency`, `proof_kernel`, `transition_kernel`,
    `admission_validation` and `assurance_transport` → semantics;
  - `declared_adapter` → lanes/exp (it imports `exp.adapter_policy` and
    `exp.declared_invocation`);
  - `__main__` and `archsmoke` → entry.

## Pin-site inventory (RF0-C5)

| Pin site | Measured |
|---|---|
| Monkeypatch and `mock.patch` sites targeting `gnd` | 460 sites; 389 resolved across 85 target modules; 71 unresolved (targets bound at run time, mostly tool scripts loaded through `importlib`). Most patched: `assurance_evidence` 27, `checker` 26, `install` 19, `synth.assemble` 19, `cli` 17, `codegen.emit` 15, `artifacts` 14 |
| Files patching `gnd.cli` | 12 |
| Test private imports of `synth.assemble`/`synth.mutate` | 54 sites in 12 files |
| Source-scan sites | 85 in 55 files: `getsource` 35, "module stays unloaded" (`sys.modules`, mostly inside subprocess code strings) 33, `cli.py` path literals 17 |
| Packaged skill citations of module paths | 9: `gnd.archsmoke` (2), `gnd.conformance`, `src/gnd/model.py`, `gnd.extract.vocabulary`, `gnd.model_verbalization`, `src/gnd/review/adapters.py` (3) |
| `cli.py` path pins | Included in the 17 `cli_path` literals above, among them `tests/test_public_distribution.py` |
| Distribution manifest | `b3-files.json`, a historical B3 snapshot. The whole-tree check is being retired in vasiloglou/gnd-public#8 |

## Findings

- **F1 (refuted premise).** RF-D8 and the plan's RF8 text call the first
  `SESSION_CONTRACT_VERSION` assignment dead. It isn't: line 482 captures it
  as `V2_SESSION_CONTRACT_VERSION`. RF8 must not remove it. Routed to the
  RF8 spec gate; the plan text is repaired at milestone close.
- **F2.** Under D7, "identical" requires an equal AST with argument names
  kept. The canonical-JSON helpers the audit grouped as identical differ in
  annotations and docstrings, so D7 classifies them all as diverged and
  RF2's canonical-bytes merge has no candidates as written. Routed to the
  RF2 spec gate as a decision: accept that result, or add a normalization
  (annotations removed, arguments alpha-renamed) as a second, owner-ruled
  view, still subject to RF1 byte pins.
- **F3.** The audit missed dynamic imports. The single literal
  `__import__` at `semantic_spec.py:1613` is what puts `semantic_spec` in
  the core cycle, so RF3 has to deal with it explicitly.
- **F4 (refuted premise).** Plan predicate 5's co-change column cannot be
  measured here (D3). Repaired at milestone close.
