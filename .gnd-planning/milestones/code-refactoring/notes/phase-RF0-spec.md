# Phase RF0 spec — baseline, authority and measurement

## 1. Status

**Awaiting owner review.** No implementation file exists. Under
`auto=false`, nothing in this spec is implemented before the owner rules the
decisions in section 7.

## 2. Provenance

- Plan: [code-refactoring-plan.md](code-refactoring-plan.md), approved r2
  plus the gate erratum, sha256
  `ca55aac340d2263429d77bad1a30f3def8a914c88fd71870a7e408bf8e4daebd`
  ([gate record](../003-plan-gate.md), commit `1cf27fb`).
- Residual review concerns routed to this gate:
  [002-panel.md](../002-panel.md), open questions F2, F4, F5, F6, F7 and
  F8, plus qwen's two divergent views on RF0-C4 and RF-R7.
- Inspection base for this spec: `1cf27fb`. Facts were measured at that
  commit on 2026-10-05 unless they are marked *(audit)*.
- No panel has reviewed this spec. The plan's panels covered the plan
  bytes only.

## 3. Obligations — step 0 harvest

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | §4 RF0 body | AST import-graph tool under `tools/` reporting module-level and lazy edges, SCCs, private-name imports, fan-in and fan-out, duplicate-helper candidates by name and body, and the RF5-C2 entry-point rule | §6.1; RF5-C2 rule deferred, D12 |
| O2 | §4 RF0 body | Layer map assigning every module to a layer, and to a lane where one applies | §6.2 |
| O3 | §4 RF0 body | Re-measure every audit summary row and every cycle the audit names | §6.4 `rf0-baseline.md`; D2 |
| O4 | §4 RF0 body | `notes/helper-families.md` | §6.4; D7 |
| O5 | §4 RF0 body | Pin-site inventory: patches of `gnd.cli`, private imports from synth, source scans, `cli.py` path pins, the distribution manifest, skill citations | §6.1 `tests` section; §6.4 |
| O6 | §4 RF0 body, RF-R7, RF-D1 | Handoff statement in the RF0 record; public-launch ledger and its test untouched | §6.5; T-SRC |
| O7 | §4 RF0 body, RF-D3 | Rule RF-D3 | D4 |
| O8 | RF0-C1 | Output byte-identical across two runs | T1 |
| O9 | RF0-C2 | Every named cycle and every new SCC confirmed, refuted or new; each difference names its edge, confirmed by hand at the source line | §6.4; T-REC |
| O10 | RF0-C3 | Every audit summary row confirmed or refuted, with its measured value | §6.4; D2 |
| O11 | RF0-C4 | Layer-map coverage test fails on any module without an entry | T7d, T7e |
| O12 | RF0-C5 | Pin-site inventory and family list counted at execution, not copied | §6.4; T-REC |
| O13 | RF0-C6 | RF0 record holds the handoff statement and the RF-D3 ruling | §6.5 |
| O14 | §9 RF0 row | Deterministic output; cycle and audit-row confirmation; complete layer map | §8 ledger |
| O15 | RF-R9 | Measured budgets; a target that proves unreachable stops the phase | D9; §10 |
| O16 | RF-R11, verification-selection reference | A selection ledger with run, inherit or cadence per gate | §8 |
| O17 | §5 audit row | The audit stays historical input; RF0 holds the successor numbers | §6.4 |
| O18 | §5 manifest row | Manifest procedure ruled at RF0 | D4 |
| O19 | 002-panel F2 (B) | Inputs for RF1's per-edge xfail: the confirmed wrong-way edges, and which layers are declared clean | §6.1 `layering`; §6.2 `declared_clean` |
| O20 | 002-panel F4 (I) | The tool measures module line counts and moved lines; co-change pairs; budgets for RF0 and RF1 | §6.1 `modules`, `--compare`; D3 (co-change); D9; RF1 budget at the RF1 gate |
| O21 | 002-panel F5 (G) | Inventory every monkeypatch target, not only `gnd.cli` | §6.1 `tests.patches` |
| O22 | 002-panel F6 (K) | Every duplicate candidate classified with a reason; a definition of "identical" | D7; §6.4 |
| O23 | 002-panel F7 (L) | Each confirmed SCC assigned to a phase or a bounded allow-list entry; allow-list count tracked | D10; §6.4 |
| O24 | 002-panel F8 (E) | Confirm the audit claims the plan acts on before acting | §6.4 claims register; D2 |
| O25 | qwen/rf0-c4-skills-exclusion | Excluded set declared in the map and asserted by the coverage test | §6.2 `excluded`; T7f |
| O26 | qwen/rf-r7-reachability-hatch | Define reachability as a recorded attempt | D8 |
| O27 | Predicates 2, 3 and 5 | The tool supplies their inputs | §6.1 |
| O28 | Standing rules 1–6 and failure classes | Bound by name | §4 |

## 4. Standing rules bound to RF0

**Process-phase section 0 rules:**

1. **Totality.** The layer-map loader in `tools/gnd_arch.py` is total over
   arbitrary JSON: wrong types, duplicate keys and non-finite numbers exit 3
   and never raise a traceback. The map read is capped at 1 MiB, applied to
   the read itself. Source parsing is total too: `SyntaxError`,
   `RecursionError`, `ValueError` and `UnicodeDecodeError` from any source
   file exit 3 and name the file (T11, T13).
2. **Time bound.** Measurement is linear in edges, apart from the SCC pass
   (Tarjan, linear) and duplicate grouping (hashing, linear). T12 bounds a
   full repository run at 30 s.
3. **Validation order.** Usage (2), then `--out` exists (11), then map load
   and validation (3), then source parse (3), then write. T10b pins the
   order when two conditions hold at once.
4. **One walk.** A single `ast.NodeVisitor` per module classifies every
   import kind (module, lazy, type-only, dynamic). There are no per-kind
   passes.
5. **One home.** `tools/gnd_layers.json` is the only home of layer and lane
   assignment, and the plan's prose vocabulary yields to it. For numbers,
   `notes/rf0-baseline.md` supersedes the audit.
6. **Measurement over argument.** Every claim in the audit-claims register
   is settled by tool output or a cited command, never by prose.

**Failure classes:** every branch in §6.1 has a case in §8 (branch table
§8.3). The output is canonical JSON. The AST hashes are Python-specific
(`ast.dump`), so the output records the interpreter version, and hashes are
compared only under the same minor version (D7). This addresses the
"interchange field defined in Python-only terms" class.

**Plan rules:**

- **RF-R1:** no `src/gnd` change. T-SRC asserts
  `git diff --quiet 1cf27fb HEAD -- src/gnd`.
- **RF-R2 to RF-R6:** not applicable, because RF0 moves no code. RF0
  supplies the inventories that RF-R5 and RF-R6 consume.
- **RF-R7:** §6.5 and D8.
- **RF-R8:** `production_identity` is unchanged because no `src/gnd` bytes
  change (T-SRC).
- **RF-R9:** RF0 has no prior measurement, so its budgets are absolute (D9).
- **RF-R10:** no feature work.
- **RF-R11:** §8.

## 5. Goal

`uv run python tools/gnd_arch.py measure --out PATH` exits 0. It writes
byte-identical canonical JSON on repeated runs of the same tree and
interpreter, and the map covers every non-excluded module under `src/gnd`.
`uv run pytest -q tests/test_gnd_arch.py` exits 0. The RF0 notes record
every audit claim and every named cycle as confirmed, refuted, new or
unverifiable, each with a measured value or a cited reason. `src/gnd` is
byte-unchanged from `1cf27fb`.

## 6. Design

### 6.1 `tools/gnd_arch.py` (estimate 750 lines, stdlib only)

```
gnd_arch.py measure [--root DIR] [--layers PATH] --out PATH
gnd_arch.py compare BASE_REV HEAD_REV [--root DIR] --out PATH
```

- `--root` defaults to the repository root (the parent of `tools/`).
- `--layers` defaults to `tools/gnd_layers.json`.
- Exit codes: `0` written; `2` usage (argparse); `3` invalid map,
  unparsable source, or a `git` failure in `compare` (unknown revision, not
  a repository); `11` `--out` already exists, nothing written. No other exit
  codes.

**Output** (`measure`, `schema_version: 1`): canonical JSON with
`sort_keys=True`, `ensure_ascii=True`, `indent=1` and a trailing newline.
There are no timestamps and no absolute paths. Every list is sorted by its
listed key.

```json
{"schema_version": 1,
 "scope": {"package": "src/gnd", "excluded": ["src/gnd/examples/**", "src/gnd/skills/**"],
           "python": "3.14", "module_count": 0, "line_count": 0},
 "modules": [{"module": "gnd.cli", "path": "src/gnd/cli.py", "lines": 0,
              "layer": "entry", "lane": null}],
 "edges": [{"from": "gnd.model", "to": "gnd.popvalidate", "kind": "lazy", "line": 2003}],
 "unresolved_dynamic": [{"from": "...", "line": 0}],
 "sccs": {"runtime": [["gnd.a", "gnd.b"]], "module_only": []},
 "private_imports": [{"from": "...", "to": "...", "name": "_x", "line": 0,
                      "kind": "from_import"}],
 "fan": [{"module": "...", "fan_in": 0, "fan_out": 0}],
 "layering": {"wrong_way": [{"from": "...", "to": "...", "kind": "...", "line": 0,
                             "from_layer": "...", "to_layer": "..."}],
              "cross_lane": [],
              "clean_layers": ["infrastructure"]},
 "duplicates": {"ast_identical": [{"hash": "<sha256>", "sites": ["gnd.a:f:12"]}],
                "families": [{"family": "canonical_json",
                              "sites": [{"site": "gnd.a:_canonical:40", "hash": "<sha256>"}],
                              "distinct_hashes": 1}]},
 "tests": {"patches": [{"file": "tests/x.py", "line": 0, "api": "setattr",
                        "target": "gnd.cli._x", "resolved": true}],
           "source_scans": [{"file": "tests/x.py", "line": 0, "kind": "getsource"}],
           "private_imports": [{"file": "...", "line": 0, "target": "gnd.synth.mutate._x"}]},
 "skills": {"module_citations": [{"file": "src/gnd/skills/.../SKILL.md", "line": 0,
                                  "cites": "src/gnd/cli.py"}]},
 "query_sites": {"fact_types_reads": [{"module": "...", "line": 0}],
                 "get_roles_calls": [{"module": "...", "line": 0}]}}
```

**Branch table**

| Area | Branch | Rule |
|---|---|---|
| edge kind | `module` | Import at module top level, including inside top-level `if`/`try`/`with` and class bodies |
| | `lazy` | Import inside any function or lambda body |
| | `type_only` | Import inside `if TYPE_CHECKING:` or `if typing.TYPE_CHECKING:` |
| | `dynamic` | `importlib.import_module("gnd...")` or `__import__("gnd...")` with a literal string argument |
| | unresolved dynamic | The same calls with a non-literal argument go to `unresolved_dynamic`, not to `edges` |
| target resolution | `from gnd.x import y` | Points at `gnd.x.y` if that module exists, otherwise at `gnd.x` |
| | relative import | Resolved against the importer's package. One that climbs above `gnd` exits 3 |
| | external | Imports outside `gnd` are dropped |
| SCC | runtime | Over `module`, `lazy` and `dynamic` edges. `type_only` is excluded |
| | module_only | Over `module` edges only |
| | reporting | Only components with two or more modules are reported |
| private import | `from_import` | `from gnd.x import _y`, where `_y` does not start with `__` and `gnd.x` is not the importer |
| | `attribute` | `alias._y`, where `alias` is bound in that module to a `gnd` module |
| layering | wrong-way | `rank(from_layer) < rank(to_layer)` |
| | same layer | Allowed |
| | cross-lane | Both modules are in the lanes layer with different lanes. Reported in `cross_lane`; not a violation |
| | clean layer | A layer none of whose modules has a wrong-way outgoing edge |
| duplicates | `ast_identical` | Functions in two or more modules whose `ast.dump` is equal after removing the docstring and the function name. Argument names are kept |
| | families | Sites whose function names match a pattern in the map's `helper_patterns` |
| tests | patches | `monkeypatch.setattr` and `monkeypatch.delattr`, both string and object forms, and `unittest.mock.patch`/`patch.object`. Object targets resolve through the test file's imports; anything else gets `resolved: false` |
| | source_scans | `inspect.getsource` calls, reads of a path ending in `cli.py`, and `sys.modules` lookups |
| skills | module_citations | Mentions of `src/gnd/....py` or `gnd.<module>` in the packaged `SKILL.md` and reference files |
| query sites | reads | `.fact_types` attribute reads, and `.get("roles")` calls |
| compare | output | Runs `git diff -U0 --no-color BASE_REV HEAD_REV -- src/gnd`. Reports per-file added and removed lines, plus *moved lines*: removed lines whose whitespace-stripped content was added in a different file, matched as a multiset; blank lines are ignored. This is RF-R9's moved-line input. Metric deltas are a plain diff of two `measure` outputs and need no subcommand |
| | git failure | Unknown revision or not a repository → exit 3 |

### 6.2 `tools/gnd_layers.json` (estimate 200 lines)

```json
{"schema_version": 1,
 "excluded": ["src/gnd/examples/**", "src/gnd/skills/**"],
 "layers": [{"name": "infrastructure", "rank": 0}, {"name": "model", "rank": 1},
            {"name": "checking", "rank": 2}, {"name": "semantics", "rank": 3},
            {"name": "lanes", "rank": 4}, {"name": "entry", "rank": 5}],
 "lanes": ["codegen", "conformance", "evolve", "exp", "export", "extract", "fidelity",
           "measure", "recovery", "review", "synth", "witness"],
 "modules": {"gnd.cli": {"layer": "entry"}, "gnd.exp.session": {"layer": "lanes", "lane": "exp"}},
 "declared_clean": [],
 "allow_list": [],
 "helper_patterns": {"canonical_json": "^_?canonical(_json)?(_bytes)?$|^_?json_bytes$"}}
```

- Starting assignments come from the audit's component map. Every
  remaining module is assigned in RF0 and justified in `rf0-baseline.md`.
- `declared_clean` and `allow_list` start empty. RF0 fills
  `declared_clean` from the measurement, and each `allow_list` entry
  (`from`, `to`, `reason`, `successor`) comes from D10.
- Every regular expression in `helper_patterns` is listed in
  `helper-families.md`.

### 6.3 `tests/test_gnd_arch.py` (estimate 500 lines)

Fixture packages are generated inside `tmp_path` from dictionaries in the
test file, never committed. That keeps unparsable and hostile sources out of
the lint and manifest surfaces.

### 6.4 RF0 notes (written at execution, measured, never copied)

- `evidence/metrics-RF0.json`: tool output at the RF0 base.
- `notes/rf0-baseline.md` contains:
  - the audit-claims register (each audit summary row, plus every audit
    number or claim the plan acts on: 11 sites, 47 imports, the three
    `model_digest` meanings, the dead assignment, 12 patch files), each
    marked confirmed, refuted or unverifiable with its measured value or
    the reason it cannot be measured (D2);
  - the cycle register (every named cycle plus any new SCC: confirmed,
    refuted or new, with each differing edge checked at its source line,
    then assigned to RF3, RF4, RF8 or the allow-list, as D10 rules);
  - the pin-site inventory (counts and per-module tables from `tests`,
    `skills`, `cli.py` path pins and the distribution manifest);
  - the layer-assignment justification.
- `notes/helper-families.md`: every `ast_identical` group and every family,
  each classified identical-candidate or diverged with a reason (D7).

### 6.5 Authority handoff (RF0 record text)

The RF0 record states: *the `runtime` and `test-acceptance` units are
developed in `gnd-public` from this record's commit forward, by owner
ruling RF-D1; the public-launch ledger records the transfer after the Phase
4 candidate sign-off (RF-R7).* No edit is made to
`.gnd-planning/milestones/public-launch/**`. T-SRC asserts this.

## 7. Decisions (open)

| # | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument for RF0 (RF-D9) | (a) prose plus the generated-fixture test list; (b) a committed corpus first. RF0's output is an internal measurement format with no external consumer, so (b) adds a gate without protecting a contract | (a) |
| D2 | RF0-C3 says "confirmed or refuted", but some audit claims rest on the private repository's history (commit counts, co-change) and cannot be measured here | (a) add a third status, `unverifiable`, which needs a reason; (b) force a refuted status, which would misstate claims that may be true | (a) |
| D3 | Predicate 5 lists co-change pairs, but this repository has 22 commits of fresh history and the audit's co-change came from private history | (a) drop co-change from the close table and report the audit figures as unverifiable; (b) measure co-change over this milestone's own commits, which mostly measures the refactor itself; (c) the owner supplies private-history counts at close. Changing predicate 5's text needs a plan revision under the erratum rule, so (a) and (c) are recorded as an owner amendment at this gate | (a), recorded as an amendment |
| D4 | RF-D3: distribution manifest and release evidence | (a) each phase adds adaptation rows to public-launch's `b3-files.json`, which edits a public-launch migration artifact; (b) refactor phases never edit public-launch migration artifacts. The distribution tests are a public-launch cadence lane, already red at `7e08e1e`. Each phase records their failing set at base and head, and reports `production_identity` as changed and unavailable. Once public-launch establishes a successor manifest procedure, phases follow it | (b) |
| D5 | Layer ranks and rules | The order infrastructure < model < checking < semantics < lanes < entry; same-layer edges allowed; cross-lane edges reported, not violations; `agent_cli` and `install` in infrastructure (so `agent_cli → exp` is wrong-way) | As stated |
| D6 | Edge-kind semantics | `type_only` excluded from runtime SCCs; class-body imports count as module-level; literal dynamic imports count as runtime edges. The other reading (type-only edges count) would report cycles that never execute | As stated |
| D7 | What "identical" means (F6) | RF0 marks AST-identical groups (docstring and name removed) as identical-candidates. A family is *identical* only when RF1's byte pins also agree on every pinned input. Anything else is *diverged*. Hashes are compared only under one interpreter minor version | As stated |
| D8 | RF-R7 reachability (qwen) | The private source remote isn't configured here. (a) attestation only, unless the owner supplies a remote URL; then each gate records `git ls-remote URL` and its output or failure; (b) require a remote now | (a) |
| D9 | RF0 budgets | Tool at most 900 lines; map at most 250; tests at most 650; notes at most 600. More than 1.5 times any estimate stops the phase (RF-D13). There are no prior baselines, so these are absolute | As stated |
| D10 | Cycle assignment and allow-list (F7) | Core → RF3; `assurance`, synth `assemble`/`mutate` and `api`↔`diff` → RF4; session → RF8. Any new SCC is assigned at this gate's record or allow-listed with a reason and successor. The allow-list count is an RF-R9 metric that may not grow in any later phase | As stated |
| D11 | Pre-existing red controls | At `7e08e1e` and `1cf27fb`, `tests/test_development_scaffold.py` fails two tests: `test_reference_closure_and_declared_bootstrap` (public-launch `phase-4-spec.md` links to an absent `public-launch-plan-r3-amendments.md`) and `test_manifest_bytes_modes_and_sizes` (unattributed paths). RF0 doesn't repair them, because they're public-launch's. Its gate requires the failing set to be exactly these two | As stated |
| D12 | RF5-C2's entry-point rule in the RF0 tool | (a) build it in RF0, where nothing exists to check yet and the rule's allow-list belongs to the RF5 spec; (b) defer the rule to RF5 as a tool extension | (b) |

## 8. Tests and verification

### 8.1 `tests/test_gnd_arch.py` (all expected to pass, exit 0 as a file)

| Id | Case | Expect |
|---|---|---|
| T1 | `measure` on the repository twice into two paths | Identical bytes; exit 0 both times |
| T2a–T2g | Generated package: module, lazy, class-body, `try`-wrapped, `TYPE_CHECKING`, relative (`from . import x`, `from ..y import z`), literal `__import__` and `import_module` | Each edge has the stated `kind`, `to` and `line` |
| T2h | Non-literal `import_module(name)` | Appears in `unresolved_dynamic`, not in `edges` |
| T2i | Relative import above the package root | Exit 3, naming the file |
| T2j | `from gnd.x import y`, where `y` is a submodule and where it is a function | Points at `gnd.x.y` and at `gnd.x` respectively |
| T3a | Cycle closed only by a lazy import | Present in `sccs.runtime`, absent from `module_only` |
| T3b | Cycle closed only by a `type_only` import | Absent from both |
| T3c | Two-module module-level cycle | Present in both |
| T4a–T4d | Private from-import counted; dunder not counted; same-module not counted; `alias._x` counted as `attribute` | As stated |
| T5a | Two functions differing only by name and docstring | Same `ast_identical` group |
| T5b | Functions differing by one constant | Different groups |
| T5c | Family pattern matches three sites with two distinct bodies | `distinct_hashes == 2` |
| T6a | Edge from rank 0 to rank 2 | In `wrong_way` |
| T6b | Same-layer edge | Not in `wrong_way` |
| T6c | Cross-lane edge | In `cross_lane`, not in `wrong_way` |
| T6d | `clean_layers` | Equals the layers with no wrong-way outgoing edge |
| T7a | Map missing a module | Exit 3, naming the module |
| T7b | Map naming a module that does not exist | Exit 3 |
| T7c | Unknown layer, a lane outside `lanes`, or a lane on a non-lanes module | Exit 3 |
| T7d | Real repository: every non-excluded module has a map entry (RF0-C4) | Pass |
| T7e | Real map with one entry deleted, in a temporary copy | Exit 3 (proves T7d can fail) |
| T7f | The `excluded` set equals `["src/gnd/examples/**", "src/gnd/skills/**"]`, and no excluded file appears in `modules` | Pass |
| T7g | Hostile maps: non-object, duplicate keys, `NaN`, a 2 MiB file | Exit 3, no traceback |
| T8a–T8d | Patches: string target; object target through `import gnd.x as m`; target through `from gnd.x import C`; unresolvable target | Resolved targets; `resolved: false` for the last |
| T9 | Source scans: `getsource`, `read_text` on a `cli.py` path, `sys.modules["gnd.cli"]` | One entry each |
| T10a | `--out` exists | Exit 11; the existing file is byte-unchanged |
| T10b | `--out` exists and the map is invalid | Exit 11 (pins the order) |
| T11 | Generated source with a syntax error | Exit 3, naming the file |
| T12 | Full repository `measure` | Completes in 30 s or less |
| T13 | Generated source nested deeply enough to raise `RecursionError` | Exit 3, no traceback |
| T14a | `compare` over a temporary git repository where one function moves between files and one line is edited | That function's lines are counted as moved; the edit counts as added and removed, not moved |
| T14b | `compare` with an unknown revision | Exit 3 |
| T-SRC | `git diff --quiet 1cf27fb HEAD -- src/gnd .gnd-planning/milestones/public-launch` | Exit 0 (run as a ledger command, not a pytest case) |

### 8.2 Selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Direct tool behavior (O1, O8, O11, O19–O21, O25) | run | `uv run pytest -q tests/test_gnd_arch.py` → exit 0 | `tools/gnd_arch.py`, `tools/gnd_layers.json`, `tests/test_gnd_arch.py`, `src/gnd/**` (read only) | Every branch in §6.1 has a case (§8.3) | Any change to those files |
| Lint | run | `uv run ruff check tools/gnd_arch.py tests/test_gnd_arch.py` → exit 0 | The same two files, ruff 0.16.2 | The repository lint gate for touched Python | Any change to them or to the ruff config |
| Unchanged product and launch bytes (RF-R1, O6) | run | T-SRC → exit 0 | `src/gnd`, `.gnd-planning/milestones/public-launch` | RF0 must not edit either | Any commit touching them |
| Planning links and pre-existing reds (D11) | run | `uv run pytest -q tests/test_development_scaffold.py` → exit 1, failing exactly the two tests named in D11 | `.gnd-planning/**/*.md` links, the public-launch manifest | This check scans markdown links, so it covers the new notes | Repair of either pre-existing red: then expect exit 0 |
| Distribution lane | cadence | Public-launch owned; red at `7e08e1e` | — | Outside RF0 acceptance (D4) | Public-launch repair |
| Full default lane | cadence | Not selected; RF0 changes no imported code | — | Impact closure is the new files only | Any `src/gnd` or `conftest` change |

### 8.3 Branch coverage

Every row of the §6.1 branch table maps to at least one case: edge kinds
T2a–T2h; resolution T2i–T2j; SCC T3a–T3c; private imports T4a–T4d; layering
T6a–T6d; duplicates T5a–T5c; tests T8a–T8d and T9; skills and query sites
T1 (asserted non-empty against the repository, plus one generated case each
inside T2); compare T14a–T14b. The map loader's branches are T7a–T7g, and the
exits T10a, T10b, T11 and T13.

## 9. Out of scope for RF0

Any `src/gnd` edit; RF1 pins and the layering test (RF0 supplies only its
inputs); the RF5-C2 entry-point rule (D12); repairing public-launch reds;
editing `units.json` or any public-launch artifact; co-change measurement
(D3); CI wiring for the tool; the curated-manifest repair (separate task).

## 10. Size

Estimate: `tools/gnd_arch.py` 750 lines, `tools/gnd_layers.json` 200,
`tests/test_gnd_arch.py` 500, notes 450, metrics JSON (generated) not
counted. The ceilings are in D9. The RF0 record reports the measured sizes.

## 11. Approval instrument

This prose plus the test table in §8.1, per D1. The fixtures are generated
inside the tests, so there is no separate answer key to split out; the
expected outcomes are the "Expect" column above.
