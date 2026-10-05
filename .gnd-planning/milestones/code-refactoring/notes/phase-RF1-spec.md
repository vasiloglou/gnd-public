# Phase RF1 spec — characterization tests

## 1. Status

**Owner-decided (2026-10-05).** The owner approved this spec at commit
`0d5cead` (sha256 `c502076506e25d093787f672ab082feca225e2567fa51e0c71c695c9b7e86e82`)
with every decision D1–D12 as proposed, gave the RF-R7 attestation, and
ruled that no panel runs over the spec (section 7, *Owner rulings*).
Implementation may begin.

## 2. Provenance

- Plan: [code-refactoring-plan.md](code-refactoring-plan.md), approved r2
  plus gate erratum and text erratum e1, sha256
  `1ffe91ddfd22f9e0fc7102fc6eb27e518d05dad996194e9bab584b58806acac8`
  ([003](../003-plan-gate.md), [005](../005-plan-erratum.md)).
- Prior phase: [004-phase-RF0.md](../004-phase-RF0.md), its open questions
  RF0-OQ2 and RF0-OQ3, and [rf0-baseline.md](rf0-baseline.md),
  [helper-families.md](helper-families.md),
  [metrics-RF0.json](../evidence/metrics-RF0.json).
- Residual concerns routed here by [002-panel.md](../002-panel.md): F2 (B)
  (strict xfail semantics and the clean-layer declaration),
  `claude/late-pins-anchor-drift`, `qwen/qwen-r2-rf1-c1-mutation-evidence`.
- Inspection base: `e834c6e` (`main` after vasiloglou/gnd-public#9).
  `src/gnd` is byte-identical to the RF0 base `19b131b`
  (`git diff --quiet 19b131b e834c6e -- src/gnd` exits 0). Facts below were
  read at `e834c6e` on 2026-10-05 by four parallel readers. Every row I rely
  on was re-checked at its cited line before entering this note.
- No panel has reviewed this spec.

## 3. Obligations — step 0 harvest

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | §4 RF1 pin list | Parser tree, help text and exit-code map of each command | §6.3 lane L-CLI; T-CLI-* |
| O2 | §4 RF1 | Exact bytes of every canonical-JSON variant on shared inputs (non-ASCII, NaN, nested ordering, trailing newline) | §6.4 L-HELP family `canonical_json`; T-HELP |
| O3 | §4 RF1 | The three `model_digest` meanings | L-HELP family `model_digest` (all five sites) |
| O4 | §4 RF1 | Both primitive-resolver semantics (truthy versus `is True`) | §6.5 L-SEM `resolver`; D6 |
| O5 | §4 RF1 | The ISO-datetime parse sites | L-HELP `iso_datetime` plus L-SEM `datetime_sites` |
| O6 | §4 RF1 | Checker verdicts with issue order and text over a fixture corpus | L-SEM `checker` |
| O7 | §4 RF1 | `diff` output | L-SEM `diff` |
| O8 | §4 RF1 | Accept/refuse table of each safe-filesystem helper over a fixed path set | L-HELP `safe_filesystem` |
| O9 | §4 RF1 | Assurance outputs | L-SEM `assurance` |
| O10 | §4 RF1 | Synth-oracle expected states | L-SEM `synth_oracle` |
| O11 | §4 RF1 | `agent_cli` exit codes and stream handling against a fake subprocess | §6.6 L-AGENT |
| O12 | §4 RF1 | One golden session replay per contract version and path (fresh, resume, reconstruct, unknown version); nondeterministic fields normalized by a declared rule or excluded, each named | §6.7 L-SESSION; D7 |
| O13 | §4 RF1 | Layering test as a strict xfail scoped to the model, population, checking and semantics layers | §6.8 L-LAYER; D4 |
| O14 | RF1-C1 | Every pin fails against a seeded mutation of the code it pins | §6.9 mutation harness; D3 |
| O15 | RF1-C2 | The diff contains only test, fixture and tool files | T-SRC |
| O16 | RF1-C3 | Every diverged family in `helper-families.md` has a pin per variant | L-HELP coverage assertion T-HELP-COV |
| O17 | RF1-C4 | Every surface named by a later phase's work is in the pin inventory, and the record maps each to its tests | §6.10 inventory; T-INV; D9 |
| O18 | §4 RF1 shape, RF-D9 | Corpus-first by default (serialized formats, exit codes) | §11; D1 |
| O19 | §9 RF1 row | Every pin fails under a seeded mutation; the pin inventory covers later phases. Starting points: new characterization tests; existing CLI, exit, checker and session tests | §8 ledger rows 1–3 |
| O20 | RF0-OQ2 | Unify the two alias resolvers in `tools/gnd_arch.py` | §6.11; D5 |
| O21 | RF0-OQ3 | The per-edge strict xfail list is the 27 wrong-way edges in `metrics-RF0.json`, with `declared_clean` = entry, infrastructure | §6.8; D4 |
| O22 | e1 RF1 pointer, 002 F4 | The RF1 budget is set at this spec gate | §10; D10 |
| O23 | 002 F2 (B) | Strict xfail semantics and the clean-layer declaration | §6.8 |
| O24 | 002 `claude/late-pins-anchor-drift` | Pins written after drift would anchor drifted behavior | RF1 runs before any `src/gnd` edit; T-SRC; goldens captured at `e834c6e` |
| O25 | 002 `qwen/qwen-r2-rf1-c1-mutation-evidence` | Evidence that each pin can fail must be retained, not asserted | §6.9: harness output retained as evidence and bound by digest |
| O26 | SM1 (later phases) | Later phases must be able to prove "every RF1 pin is unchanged" | §6.2 golden manifest; T-GOLD-MANIFEST |
| O27 | RF-R3 | A later spec that touches an unpinned surface adds pins first | §6.10 `owed` rows name the owing phase |
| O28 | RF-R7, RF-D1 | Owner attestation at this gate that the source repository took no change to handed-off paths; no remote, so the control rests on attestation | §6.12 |
| O29 | RF-R1, RF-R8 | No `src/gnd` change; `production_identity` unchanged | T-SRC |
| O30 | RF-R9, RF-D13 | Measured budgets; overrun stops at the owner gate | §10; D10 |
| O31 | RF-R11, verification-selection | Selection ledger with run, inherit or cadence | §8.2 |
| O32 | §0 standing rules 1–6 and failure classes | Bound by name | §4 |
| O33 | 004 boundary | AST identity is not behavioral identity; RF1 byte pins decide which identical-candidates become identical (RF0 D7) | L-HELP records per-site outputs for every identical-candidate group; §6.4 |
| O34 | 004 RF0-OQ4 (RF2 gate) | Not owned here; RF1 supplies its input (per-variant canonical-JSON bytes) | L-HELP; noted only |
| O35 | §7 out of scope | Carryovers `OQ-V52-CLOSE-CANONJSON-1` and others stay with their source owner | §9 |

## 4. Standing rules bound to RF1

**Process-phase section 0 rules:**

1. **Totality.** RF1 adds two new readers: `tools/rf1_pins.py` reads
   `mutations.json` and `cases.json`, and the evidence normalizer in
   `tests/support/rf1_pins.py` reads session evidence bytes. Both are total:
   the tool exits 3 (never a traceback) on non-object roots, duplicate keys,
   non-finite numbers, wrong types and files over 1 MiB, with the cap applied
   to the read (T-TOOL-3). The normalizer fails its pin with a named
   assertion on undecodable or non-JSON bytes and never raises out of
   pytest's assertion path (T-NORM-4).
2. **Time bound.** The harness is linear in mutation rows, and each row runs
   one subprocess under a 300 s timeout; a timeout is reported as a failed row
   (exit 1), not a hang (T-TOOL-6). The default-lane cost of all new pins is
   bounded by D10 and measured at record time.
3. **Validation order.** `rf1_pins.py mutate`: usage (2), `--out` exists
   (11), table or cases invalid (3), unmutated control red (1), then rows.
   A row whose snippet is absent or not unique is a table error (3), checked
   for every row before any subprocess runs. T-TOOL-2 pins the order when
   two conditions hold at once.
4. **One walk.** One golden-comparison function `assert_golden(lane, key,
   observed)` serves every lane; one normalizer serves every session file.
   No lane carries its own comparison or normalization code.
5. **One home.** Expected values live only in
   `tests/fixtures/rf1-pins/goldens/`. The surface-to-test map lives only in
   `inventory.json`; the RF1 record cites it. Case inputs live only in
   `cases.json`; the README tells the stories and carries no values.
6. **Measurement over argument.** Whether a golden depends on the
   interpreter is settled by capturing under 3.11, 3.13 and 3.14 and
   comparing (D2), not by reasoning about stdlib versions.

**Failure classes:**

- *A declared branch with no case that can fail it.* Every pin is a
  mutation-table target (§6.9), and every branch of the harness and the
  normalizer has a case (§8.3).
- *A class credited when only one half has a case.* The checker corpus
  coverage assertion counts each constraint family per verdict
  (`pass` and `fail` separately), not per family (T-SEM-CHK-COV).
- *A rule unfalsifiable by its fixtures.* The resolver pin uses non-boolean
  truthy values (`1`, `"yes"`), the only inputs that tell truthy from
  `is True` apart (D6).
- *An interchange field defined in Python-only terms.* Goldens are canonical
  JSON (`sort_keys`, `ensure_ascii=False`, `indent=1`, trailing newline);
  bytes are hex strings, exceptions are `{"raises": class, "message": text}`.
- *A single reviewer mistaken for a panel.* The record says one reviewer is
  one reviewer.
- *A guard that goes quiet when it matters.* The mutation harness requires
  the unmutated control to pass before any row counts; a broken control is
  exit 1, not a success (T-TOOL-4).

**Plan rules:**

- **RF-R1:** no `src/gnd` byte changes (T-SRC). Defects and quirks found are
  pinned as they are and recorded as open questions (section *Quirks pinned
  as found*).
- **RF-R2:** every canonical-JSON and digest variant is pinned per variant;
  nothing is merged.
- **RF-R3:** this phase is the pin set. Surfaces it does not pin are
  inventoried as `owed` with the owning phase (§6.10).
- **RF-R4, RF-R6:** not applicable: RF1 moves no code. RF1 does add new
  monkeypatch sites (the session clock injection, §6.7), which the RF0 tool
  inventories like any other; later move units must update them under RF-R5.
- **RF-R5:** not applicable (no shims). `notes/shim-inventory.md` is created
  empty by RF2, not here.
- **RF-R7:** §6.12.
- **RF-R8:** unchanged, because no `src/gnd` byte changes.
- **RF-R9:** RF1 has no metric targets (it moves nothing); its budgets are
  absolute (D10).
- **RF-R10:** no feature work.
- **RF-R11:** §8.2.

## 5. Goal

At base `e834c6e`, with no `src/gnd` change:

- `uv run pytest -q tests/test_rf1_*.py` exits 0, with only the strict-xfail
  layering cases reported as xfailed;
- `uv run python tools/rf1_pins.py mutate --out <dir>` exits 0: the
  unmutated control passes and every mutation row turns each node it names
  red;
- every surface named by RF2–RF8 has a row in `inventory.json` whose test
  node ids all collect.

## 6. Design

### 6.1 Files

| Path | Kind | Estimate (lines) |
|---|---|---|
| `tests/support/rf1_pins.py` | golden comparison, normalizer, observation helpers | 300 |
| `tests/test_rf1_cli_pins.py` | L-CLI | 200 |
| `tests/test_rf1_helper_pins.py` | L-HELP | 350 |
| `tests/test_rf1_semantic_pins.py` | L-SEM | 400 |
| `tests/test_rf1_agent_cli_pins.py` | L-AGENT | 180 |
| `tests/test_rf1_session_pins.py` | L-SESSION | 450 |
| `tests/test_rf1_layering.py` | L-LAYER | 100 |
| `tests/test_rf1_pin_harness.py` | manifest, inventory and harness self-tests | 250 |
| `tools/rf1_pins.py` | `capture` and `mutate` | 350 |
| `tools/gnd_arch.py`, `tests/test_gnd_arch.py` | RF0-OQ2 (§6.11) | +60 / +40 |
| `tests/fixtures/rf1-pins/README.md` | case stories, no values | 120 |
| `tests/fixtures/rf1-pins/cases.json` | case inputs | 400 |
| `tests/fixtures/rf1-pins/mutations.json` | seeded mutations | 700 |
| `tests/fixtures/rf1-pins/inventory.json` | surface → tests | 300 |
| `tests/fixtures/rf1-pins/goldens/**`, `goldens.sha256` | captured, not hand-written | not counted; size bound in D10 |
| `tests/fixtures/rf1-pins/populations/**` | extra checker fixtures, only if T-SEM-CHK-COV needs them | 150 |

### 6.2 Goldens, capture and the manifest

- A golden is one canonical-JSON file per lane and key:
  `goldens/<lane>/<key>.json`. Bytes are recorded as lowercase hex under
  `"hex"`; text as `"text"`; an exception as
  `{"raises": "<module>.<Class>", "message": "<str(exc)>"}`.
- `assert_golden(lane, key, observed)` canonicalizes `observed` and compares
  it with the file's bytes. On mismatch it fails with a unified diff. It never
  writes.
- `uv run python tools/rf1_pins.py capture --out DIR` imports the same
  observation functions the tests use and writes every golden into `DIR`. It
  exits 11 if `DIR` exists and writes nothing. Goldens are captured once, at
  `e834c6e`, into the fixture directory, and are never re-captured in place.
- `goldens.sha256` lists `sha256  relative/path` for every golden, sorted.
  T-GOLD-MANIFEST asserts that the manifest matches the files exactly (no
  missing, extra or changed file) and that the manifest's own sha256 equals
  a constant in `test_rf1_pin_harness.py`. Changing any golden therefore
  edits two files in a visible way. This is the SM1 discharge for every later
  phase, together with
  `git diff --quiet <RF1 record commit> HEAD -- tests/fixtures/rf1-pins/goldens`.
- Interpreter keying (D2): `capture` runs under 3.11, 3.13 and 3.14. A golden
  whose bytes agree under all three is stored once. A golden that differs is
  stored as `<key>.py311.json`, `<key>.py313.json` and `<key>.py314.json`, and
  the record lists every such key with the reason the runtime gave.

### 6.3 L-CLI — parser tree, help text, exit map

Facts (cited): the whole tree is built inside `cli.main` (`src/gnd/cli.py:7456`)
on `_BandSafeParser` (`cli.py:344`), whose `error()` exits 64. It has 27
top-level commands and 24 subcommands (51 parsers plus the root), including
the parsers added by `witness/cli.py:13`, `export/souffle_cli.py:9` and
`export/lean_cli.py:9`. No existing test pins the full tree or exact help
bytes; `tests/test_coverage_cli.py:55` already captures the root parser by
patching `_BandSafeParser.parse_args`.

| Pin | Observation | Golden |
|---|---|---|
| T-CLI-TREE | The root parser is captured the same way as `test_coverage_cli.py:55`. Every parser is serialized as `{prog, description, epilog, formatter_class, actions: [{class, option_strings, dest, nargs, const, default, type, choices, required, help, metavar}], subcommands: {name: …}}`, with `repr()` for `default` and `const` and `__name__` for classes and callables | `cli/tree.json` (one file; interpreter-independent unless D2 says otherwise) |
| T-CLI-HELP[path] | `format_help()` of each of the 52 parsers, with `COLUMNS=80`, `NO_COLOR=1` and `PYTHON_COLORS=0` | `cli/help/<path>.json`, keyed per minor version as D2 measures |
| T-CLI-EXIT[path] | For each of the 52 parser paths: `gnd <path> --help` (exit, stdout bytes) and `gnd <path> --rf1-unknown-flag` (exit, stderr bytes), run in-process through `tests/support/cli_runner.run_main` | `cli/exit-probes.json` |
| T-CLI-MAP | Every module-level exit constant and map: all `EXIT_*` names in `gnd.exits` and `gnd.cli`, `exits.SOLVE_CONTROL_PLANE_EXITS`, `conformance.service._EXIT_*`, `batch.BATCH_EXIT_PRECEDENCE`, `evolve.models._CONFORMANCE_EXIT_PRECEDENCE`, `evolve.service._EXIT_PRECEDENCE`, `exp.session_eval.OUTCOME_BY_EXIT` | `cli/exit-map.json` |
| T-CLI-COV | The set of parser paths in `tree.json` equals the set discovered at run time, has exactly 52 members, and every path has a help and an exit-probe entry | (assertion) |

Behavior of each command's handler is outside L-CLI; see §6.10 (D9).

### 6.4 L-HELP — helper families

Each site is called through its own signature on a shared input set. The
golden records, per site and per input, the output or the exception. Sites
come from `metrics-RF0.json` (`duplicates.families` and the 15
`ast_identical` groups); T-HELP-COV asserts that every family site and every
identical-candidate site has a golden entry or a `pinned_via` entry naming
the test that pins it through a caller.

| Family | Sites | Shared inputs (exact values in `cases.json`) | How |
|---|---|---|---|
| `canonical_json` | 18 name-pattern sites plus `assurance._sorted_set` | `{}`; `{"b":1,"a":{"d":[2,1],"c":"ü"}}`; `"é \U0001F600"`; `float("nan")`; `float("inf")`; `1e16`; `Decimal("1.10")`; `{1: "int key"}`; a two-field pydantic model; `[None, True, 0.0, -0.0]` | Direct call. `cli.canonical` (nested in `_cmd_extract`, `cli.py:1681`) is `pinned_via` the extract CLI pin in L-SEM. The non-encoders `proof_bridge._canonical`, `assurance._sorted_set` (tuple sort) and `transition._canonical` (pre-normalizer) get their own input sets: tuples with duplicates, and dates, datetimes and non-string keys |
| `sha256_hex` | 12 | `b""`, `b"gnd\n"`, 1 MiB of `b"a"`; str and dict inputs where the signature takes them | Direct call. `measure.promote._digest` takes a path: fixture files in `tmp_path`. The two validators (`extract.anchors._digest`, `judgments.digest`) get valid and invalid hex inputs |
| `model_digest` | 5 | Every model in `tests/fixtures/checker`, `tests/fixtures/models/*.orm.yaml`, the example models, and one model with `reference_populations` | `conformance.currency.model_digest` over file paths; the other four over loaded `Model` objects |
| `file_digest` | 5 | A fixed `tmp_path` tree: a regular file, an empty file, a symlink to a file, a symlinked directory, a FIFO where the platform allows it | Direct call, or the documented method on a constructed `EvolutionService` |
| `strict_json` | 6 readers; the 10 nested hooks are `pinned_via` their reader | `b'{"a":1}'`, `b'{"a":1,"a":2}'`, `b'{"a":NaN}'`, `b'{"a":1e999}'`, `b'[1]'`, `b'{"a":1} x'`, `b'\xff'`, a fenced block, 10,000-deep nesting, and, for each site that has a size cap, a payload one byte over it | Direct call; `coverage.read_json_document` through a `tmp_path` file |
| `iso_datetime` | 2 | `2024-01-01T00:00:00Z`, `…z`, `…+00:00`, naive, `T24:00:00`, `2024-01-01 00:00:00`, date-only, fractional seconds, `2024-W01-1`, leading space, `None`, `1` | Direct call |
| `validation_issues` | 6 | One pydantic `ValidationError` from a fixed model with a missing field, a wrong type and a nested error; for the jsonschema sites, a fixed invalid document | Direct call; `session_contract._pydantic_issues` at `schema_version` 1, 3 and 8 |
| `yaml_guard` | 5 | Text and `tmp_path` files: plain mapping, alias, anchor, two documents, a stream over each site's event or token budget, invalid YAML | Direct call |
| `safe_filesystem` | 16, plus the identical-candidates `0f1cc1a7` and `3d106ff9` | Path strings: `a`, `./a`, `a/b`, `a//b`, `a/`, `.`, `..`, `../a`, `a/../b`, `/abs`, `a\b`, `..\x`, `~`, `""`, `"a\x00b"`, `é`. Tree scenarios in `tmp_path`: plain target, existing target, symlinked final component, symlinked parent, missing parent, target is a directory | Path predicates over the string set; descending and writing helpers over the scenarios. A helper whose signature needs state the scenarios cannot supply (for example an open directory descriptor) is called with the descriptor the scenario opens; if that is impossible, it is `pinned_via` its nearest caller and listed in the record |

The identical-candidate groups that are not in these families (`ccbb68bd`
`_rate`, `22614c42` and `c9b00e5d` model traversal, `73ae047d`, `5153de62`,
and the two trivial constructors) are pinned with a small per-group input
set, so that RF2 and RF6 can tell identical-candidates from identical under
RF0 D7. The two trivial constructors are recorded as `not_a_family` with no
pin, as `helper-families.md` already classifies them.

### 6.5 L-SEM — resolver, datetime sites, checker, verbalize, diff, assurance, synth oracle

| Pin | Facts | Observation | Golden |
|---|---|---|---|
| T-SEM-RESOLVER | `is True` at `popvalidate.py:279` (via `resolve_primitive`, `:320`) and `extract/vocabulary.py:89`; truthy at `model.py:730` (`_resolved_primitive`), `model_verbalization.py:59` and `export/pyrel_runtime.py:93,121,1044`. The meta-schema types the field boolean (`orm-meta.schema.json:210`) | Each resolver over an unvalidated object-type mapping with `inherits_reference` in `{True, False, 1, 0, "yes", "", None, absent}`, for a two-level subtype chain (D6) | `sem/resolver.json` |
| T-SEM-DATETIME | Besides the two family sites: `model._temporal_literal_valid` (`model.py:745`), `checker._typed_comparison_values` (`checker.py:2041`), `semantic_adapter.py:132`, `synth/boundary.py:242`, `synth/assemble.py:480`, `export/pyrel_runtime.py:1113` | Each importable function over the `iso_datetime` input set, through the narrowest public or private callable at that line; inline expressions are `pinned_via` their enclosing function | `sem/datetime.json` |
| T-SEM-CHK[case] | `CheckReport` (`checker.py:291`) excludes `scope_id`, `fact_refs` and five report fields from the wire. Verdict order follows `projection.findings` (`checker.py:510`). `test_checker_families.py` pins substrings only | For each case: `checker.check(...)` as `model_dump(mode="json")`, plus the excluded fields `scope_id` and `fact_refs` per verdict, plus `gnd check` (text and JSON) stdout, stderr and exit. Cases: every model and population pair in `tests/fixtures/checker` and the example directories; `--admission` on each JSON case; the transition arm on `examples/approvals` (`--pre`, `--steps`, `--post`); the batch arm (`--populations`) over one directory | `sem/check/<case>.json` |
| T-SEM-CHK-COV | — | The constraint types are every `const` value of a constraint's `type` in `src/gnd/schema/orm-meta.schema.json`. The union over all cases covers each type with a satisfied outcome (`verdict` pass) and a violated outcome (whatever `verdict` the checker reports for a violation of that type and modality, for example a deontic warning). A type the fixtures cannot reach gets a new population under `fixtures/rf1-pins/populations/`; a type the checker does not evaluate is listed with the status it reports | (assertion) |
| T-SEM-VERB[case] | RF6 lists verbalize among its controls | `gnd verbalize MODEL` and `gnd verbalize population MODEL POP` stdout and exit, over the same corpus | `sem/verbalize/<case>.json` |
| T-SEM-EXTRACT | `cli.canonical` is nested in `_cmd_extract` | `gnd extract MODEL --out DIR` over two corpus models: every written file's bytes, plus the exit | `sem/extract/<case>.json` |
| T-SEM-DIFF[pair] | `diff.diff_models` (`diff.py:264`) returns a dict and calls `gnd.api` at `diff.py:227`. An exact pin already exists at `tests/test_v70_phase6_corpus.py:71`, which this phase maps rather than repeats | `gnd diff A B` stdout and exit for three corpus model pairs, one of them with `--populations`-style population comparison through `compare_population` | `sem/diff/<pair>.json` |
| T-SEM-ASSURANCE[case] | Four modules produce in-memory blocks and validators (`assurance.py:207,523,554`, `assurance_claims.py:131`, `assurance_inheritance.py:90,303`, `assurance_evidence.py:603`) | Over the checker corpus: `certify_result` as `AssuranceBlockV1.as_dict()` and `derive_assurance_scope`. `validate_claim_graph`, `compare_observations` and `validate_result` over accept and refuse inputs taken from their existing tests' fixtures. `production_identity`, `runtime_identity` and anything else that hashes `src/gnd` bytes are **excluded**, because RF-R8 makes them change on every edit; the record names each excluded function | `sem/assurance/<case>.json` |
| T-SEM-ORACLE[model] | `mutate.expected_state` (`mutate.py:530`) is the shared oracle; consumers are `predict_violations` (`:667`), `boundary.predict_boundary` (`:392`), `frontier`, and `assemble._build_expectations` (`:1729`) | For each checker-corpus model: `expected_state` for every constraint against the seed-0 conforming population, `predict_violations` for each mutated population that `gnd synth` writes at seed 0 (if it writes none for a model, the golden records that), `predict_boundary`, and `_build_expectations`. Plus `gnd synth` output bytes at seed 0 | `sem/oracle/<model>.json` |

### 6.6 L-AGENT — `agent_cli`

Facts: `agent_cli` defines statuses, not exit constants: `InvocationStatus`
(`agent_cli.py:54`), `BoundedProcessResult.status` (`:102`). Streams are
drained under per-stream and aggregate caps (`:283`, `:299`) and redacted
(`:495`). Existing tests (`tests/test_agent_cli.py`) use real fake
executables.

"Fake subprocess" means a fake executable written into `tmp_path`, as in
`test_agent_cli.py:27`. A monkeypatched `asyncio.create_subprocess_exec`
would bypass the stream-draining code that RF4 moves.

| Pin | Scenario | Observed |
|---|---|---|
| T-AGENT-ARGV | `build_agent_argv` for each adapter and each option combination its tests use | exact argv |
| T-AGENT-RUN[s] | `run_bounded_process`: success with stdout and stderr; nonzero exit; stdout over its limit; stderr over its limit; aggregate over budget; missing executable (spawn failure); timeout (sleep 30 s, timeout 0.5 s); output containing a secret-shaped token | `BoundedProcessResult.model_dump(mode="json")` plus the excluded raw stream bytes, with monotonic fields normalized (D7) |
| T-AGENT-INVOKE[s] | `invoke_agent` with a fake adapter on `PATH`: success; failure; timeout; a version probe that fails | `InvocationResult` wire plus raw streams, normalized |

### 6.7 L-SESSION — golden replays per contract version and path

Facts: contract versions 1–8 are accepted (`session_contract.py:1038`);
dispatch is at `:1073–1088`; an unknown version raises a `literal_error`
whose expected list omits 8 (`:1097–1106`). The CLI never resumes
(`cli.py:5188` always picks a fresh `run-NNNN`); resume is programmatic
through `session.run_session` (`session.py:745`, v1–v6) and
`session_v7.run` (`session_v7.py:537`, v7–v8). `reconstruct` exists only for
v7 and v8 (`session_v7.py:273`; `session_store.py:2731`). No existing test
compares generated evidence bytes with a committed golden.

**Matrix.** `fresh` for v1–v8; `resume` for v1–v8; `reconstruct` for v7 and
v8; `unknown` for `schema_version` 0 and 9. `reconstruct` for v1–v6 is not
applicable, because no such code path exists, and the record says so. That
gives 8 + 8 + 2 + 2 = 20 pins.

| Path | Procedure | Observed |
|---|---|---|
| fresh | `gnd exp run` in-process over a contract of that version, with a fake agent that fails attempt 1 and succeeds on attempt 2 where the version's builder allows two attempts; otherwise one accepted attempt, and the record names the version. Contracts and fake agents come from the existing builders: v1 `test_exp_session_e2e.py:168`; v2 and v3 `tests/fixtures/public-driver-sessions`; v4 and v5 the transition and walk fixtures used by `test_public_agent_failure_transition.py` and `test_public_session_wire_guards.py`; v6 `test_public_local_command_adapter_controls.py`; v7 `tests/support/v71_session_cases.py`; v8 the judgment fixtures of `test_public_v71_judgment_successor_guards.py` | exit, stdout, stderr, and the normalized evidence tree (every file under the run root) |
| resume | From the completed fresh run: delete `result.json` and attempt 2, then call `read_resume_state` and resume through the programmatic entry | the normalized `ResumeState`, whether the agent was invoked again, and the normalized evidence tree after completion |
| reconstruct | `session_v7.reconstruct(store, contract)` on the resume state, and with `allow_terminal=True` on the completed run | the normalized `ResumeState` and the `_v7_best` record identity |
| unknown | `read_session_contract` on a v3 contract relabelled 0 and 9, and `gnd exp run` on each | the `SessionContractError` text, and the CLI exit and stderr |

**Determinism and normalization (D7).** The normalizer runs one declared
rule list, in this order:

| # | Field or token | Rule |
|---|---|---|
| N1 | `started_monotonic`, `ended_monotonic`, `decided_monotonic` | Made deterministic at the source: the session pins inject a counting clock by patching the module-level binding through which each `gnd` module reads the clock (at `e834c6e`: `import time` in `agent_cli`, `exp.session` and `exp.session_v7`; `exp.declared_invocation` is checked at implementation). If a version path reads a clock the injection does not reach, the field is replaced by `"<monotonic>"` and the record names the path |
| N2 | `elapsed_seconds`, `accounted_wall_seconds` | Deterministic under N1. Otherwise `"<seconds>"` |
| N3 | The run's temporary root, `sys.executable`, the fake agent's absolute path | Replaced by `<root>`, `<python>`, `<agent>` wherever they occur in a string |
| N4 | The receipt nonce (`session.py:706`) and staging directory names (`session_store.py:1627,1679,1828`) | Must not appear in any published file: the pin asserts their absence |
| N5 | A 64-hex digest that equals the sha256 of another evidence file's **raw** bytes | Replaced by `<sha256:relpath>`, but only after that equality is checked, so a broken digest chain still fails the pin |
| N6 | Any other remaining difference between two consecutive runs of the same case | Not normalized. T-SESSION-DET runs each fresh case twice and fails on any difference, which surfaces an undeclared nondeterministic field as a finding instead of hiding it |

### 6.8 L-LAYER — strict xfail layering test

Facts: the map has six layers and no `population` layer; `popvalidate` and
`population` are in `model`. `declared_clean` is already
`["entry", "infrastructure"]`. `metrics-RF0.json` lists 27 wrong-way edges in
23 distinct `(from, to)` module pairs: 19 edges in 16 pairs leave the model,
checking or semantics layers, and 8 edges in 7 pairs go from lanes to entry.

- The test runs `gnd_arch.measure` over the repository once per session.
- **T-LAYER-EDGE[pair]**: one case per known wrong-way pair in scope (D4),
  asserting the pair is absent, marked
  `pytest.mark.xfail(strict=True, reason="<from> -> <to>: RF3/RF4 removes")`.
  Cases are keyed by module pair, not by line, so a moved line does not
  XPASS. A pair XPASSes only when every edge between the two modules is gone,
  and strict mode then fails the run until the marker is removed.
- **T-LAYER-RATCHET** (no xfail): the measured wrong-way pairs are a subset of
  the 23 known pairs, and every layer in `declared_clean` has no wrong-way
  outgoing edge. A new wrong-way import anywhere fails the ordinary lane.
- **T-LAYER-SCOPE**: the scope list in the test equals the layers D4 rules,
  and every in-scope pair has exactly one case.

### 6.9 Mutation harness — RF1-C1

```
tools/rf1_pins.py capture --out DIR
tools/rf1_pins.py mutate [--only ID ...] --out DIR [--timeout SECONDS]
```

`mutations.json` (`schema_version: 1`):

```json
{"schema_version": 1,
 "rows": [{"id": "M-HELP-canonical-artifacts-newline",
           "file": "src/gnd/artifacts.py",
           "old": "exact text, occurring exactly once in the file",
           "new": "replacement text",
           "expect_red": ["tests/test_rf1_helper_pins.py::test_canonical_json[gnd.artifacts:canonical_json_bytes]"]}]}
```

- `mutate` copies `src/gnd` into a temporary directory, applies one row,
  and runs `python -m pytest -q -p no:cacheprovider <expect_red nodes>` in a
  subprocess with that directory first on `PYTHONPATH`. The row is **killed**
  when every named node fails, and **survived** otherwise.
- Before any row, the unmutated copy runs every node named by any row. That
  control must pass, or the tool exits 1 (T-TOOL-4). This also proves the
  `PYTHONPATH` copy is the code under test: the control plus one killed row
  prove both ends (T-TOOL-5).
- Coverage: the union of `expect_red` must equal the set of node ids collected
  from `tests/test_rf1_*.py`, excluding `test_rf1_pin_harness.py` and the
  L-LAYER cases (whose subject is tool output, not `src/gnd` behavior).
  A node with no row is a table error (exit 3).
- Output: `DIR/mutation-report.json` (canonical JSON: per row id, killed or
  survived, and the failing node ids) and `DIR/control.txt`. Both are
  retained under `evidence/phase-RF1/` and bound by digest (O25).
- Exits: 0 every row killed and the control green; 1 a row survived, a row
  timed out, or the control was red; 2 usage; 3 invalid table or cases; 11
  `--out` exists.
- Row granularity follows D3: one row may name several nodes when one
  mutation legitimately reds them all (for example a change to
  `_BandSafeParser` reds every help pin), but every L-HELP site, checker case
  and session pin has at least one row of its own that names no other site.

### 6.10 Pin inventory — RF1-C4

`inventory.json` maps every surface named by RF2–RF8 to tests:

```json
{"schema_version": 1,
 "surfaces": [{"surface": "canonical bytes variants", "phase": "RF2",
               "plan_anchor": "RF2 body",
               "status": "pinned",
               "rf1_nodes": ["tests/test_rf1_helper_pins.py::test_canonical_json"],
               "existing_nodes": ["tests/test_artifacts.py::test_canonical_json_bytes_exact"],
               "owed_by": null}]}
```

- `status` is `pinned` (RF1 nodes exist), `existing` (only existing tests,
  named), or `owed` (an unpinned surface whose moving phase must add pins
  first under RF-R3; `owed_by` names that phase).
- The surfaces are taken from the plan's RF2–RF8 bodies. Pre-filled list,
  each to be completed with node ids at implementation:
  - **RF2:** canonical-bytes variants; `sha256_hex`, `Sha256`, `is_sha256_hex`; exit codes moving to `exits.py`; `issues_from_validation_error` sites; constraint refs built by hand (`synth/assemble.py:1206,1532,1669,1672,1724,1726,2099`, `synth/mutate.py:1808`, `measure/report.py:488`, `export/pyrel_runtime.py:891,893`); the five `model_digest` sites.
  - **RF3:** the primitive resolver; checker `effective_view` (today the local at `checker.py:4851`); `applicable_scope_ids` (`semantic_registry.py:1463`); the rebinding at `checker.py:4431,4432,4593,4594,4653`; the derivation-term ContextVar (`model.py:4278`); `semantic_registry` owner strings (existing tests `test_v6_phase2_registry.py`, `test_v62_phase2_registry.py`); the dynamic import at `semantic_spec.py:1613`; the core cycle's modules.
  - **RF4:** the safe-filesystem helpers; `agent_cli`; `diff` → `api`; the synth oracle; the assurance modules; lane imports of `gnd.install`.
  - **RF5:** each of the 51 command parsers (pinned by L-CLI), and each command handler's behavior (D9).
  - **RF6:** `fact_types` and `.get("roles")` read sites (behavior through the checker, verbalize and synth pins); constraint-family dispatch; the `model.py` and `checker.py` package split.
  - **RF8:** each session version and path; `SessionProfile` inputs; `session_v7.run` and `reconstruct`; `_v7_best`; the version-8 literal.
- T-INV asserts: the file is total and canonical; every `rf1_nodes` and
  `existing_nodes` id collects under the default `addopts`; every `owed`
  row names a phase from RF2 to RF8; and every RF1 node id appears in at
  least one row.

### 6.11 RF0-OQ2 — one alias resolver in `tools/gnd_arch.py`

Replace the two resolvers with one `_AliasScopes` class (a scope stack with
`bind`, `lookup` and `push`/`pop`), used by both `_ModuleVisitor` and
`_TestVisitor`. Under D5 (a), the test visitor becomes lexically scoped like
the module visitor, so test-file inventory counts may change. RF1 then
commits `evidence/metrics-RF1-base.json`, measured at `e834c6e` with the
unified tool, and a delta table against `metrics-RF0.json` in the record.
New tool tests: an alias bound inside a test function does not resolve a
patch target outside it, and the module visitor's existing `test_r08_*`
cases still pass.

### 6.12 Authority attestation (RF-R7)

At this gate the owner is asked to attest that the source repository took no
change to the `runtime` and `test-acceptance` paths since the RF0 record. No
source remote is configured, so the control rests on that attestation, as
RF0 D8 ruled. The RF1 record quotes it.

## 7. Decisions

| # | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument (RF-D9 proposes corpus-first for RF1) | (a) **Case-manifest first**: step 3 first commits `README.md`, `cases.json`, `mutations.json` and `inventory.json` with the harness red (no goldens yet); the owner's approval of this spec covers what is pinned; goldens are then captured mechanically from `e834c6e`. (b) Full corpus-first: the owner reads and approves the committed case manifest at a separate station before capture. (c) Prose only. For characterization pins, the expected values *are* the base code's output, so hand-authored answers add nothing; what the owner decides is case selection and the normalization rules, which this spec enumerates. (b) costs one more gate round | (a) |
| D2 | Interpreter-dependent bytes. CI runs 3.11 (ubuntu) and 3.13 (macos); the local toolchain is 3.14; `requires-python` is `>=3.11`. argparse help and some stdlib exception messages differ across minors | (a) Capture under 3.11, 3.13 and 3.14; store one golden where they agree and per-minor goldens where they differ. Under a minor with no golden (3.12, 3.15), the affected pin is skipped with a stated reason, and T-GOLD-VERSIONS asserts every per-minor key has exactly the three variants, so the skip set is closed. (b) The same, but fail instead of skip on uncovered minors, which turns the default lane red for any 3.12 contributor. (c) Pin only interpreter-independent structure (the parser tree, not help bytes) | (a) |
| D3 | Mutation granularity (RF1-C1) | (a) Every pin node is named by at least one row, and every L-HELP site, checker case and session pin also has a row of its own; a shared row may red many nodes. Estimate: about 90 rows. (b) Exactly one row per node, about 200 rows, mostly redundant for aggregate pins such as help. (c) One row per lane: proves the comparisons are live, but not that each site's entry exercises that site | (a) |
| D4 | Layering xfail scope. Plan: "model, population, checking and semantics layers", but the map has no `population` layer. RF0-OQ3: "the 27 wrong-way edges" | (a) Scope = edges *from* the model, checking and semantics layers: 16 pairs, 19 edges as strict xfail cases. The 7 lanes → entry pairs join at RF4 through SM4. T-LAYER-RATCHET still forbids any new wrong-way pair in any layer. (b) All 23 pairs (27 edges) as strict xfail now, which covers lanes earlier than the plan says. The plan's `population` names modules that the map places in `model`; either reading covers them | (a) |
| D5 | RF0-OQ2 alias resolvers | (a) Unify now, with the test visitor lexically scoped; re-measure and report the count delta (§6.11). (b) Unify, but keep file-wide semantics for tests (one class, two modes), with no count change. (c) Defer to RF2, the first phase that consumes the patch inventory | (a) |
| D6 | Resolver pin inputs. The field is schema-typed boolean, so only unvalidated mappings can carry `1` or `"yes"` | (a) Pin over unvalidated mappings (§6.5): the only inputs that tell the semantics apart, matching what RF3's variant parameter must preserve. (b) Pin only through validated models, where both semantics agree, which makes the pin unable to tell them apart | (a) |
| D7 | Session nondeterminism (§6.7) | (a) Rules N1–N6 as listed: inject the clock where reachable, use placeholders otherwise, verify-then-replace digests, and add a determinism double-run that fails on undeclared variation. (b) Pin only per-file key sets and versions, as `v71_session_cases.py` already does, which is not a byte pin | (a) |
| D8 | Session matrix | 20 pins: fresh v1–v8, resume v1–v8, reconstruct v7–v8, unknown 0 and 9. Reconstruct for v1–v6 is recorded as not applicable (no code path) | As stated |
| D9 | Command handlers that RF5 moves but RF1's list does not name (codegen, conformance, solve, evolve, review, measure, doccheck, fidelity, synth CLI beyond seed 0, coverage, recovery, install, doctor, uninstall, judgments, witness, export, import, validate) | (a) Pin them at the parser, help and exit-probe level here; map each handler to its existing tests by name; mark its byte-level behavior `owed` by the RF5 part spec that moves it (RF-R3 already requires those pins before the move). (b) Pin every handler's output now, which roughly doubles RF1 | (a) |
| D10 | RF1 budgets (002 F4; e1) | Hand-written source: estimate 4,350 lines (§6.1, excluding goldens); stop at 1.5× (6,525). Goldens: at most 8 MiB uncompressed on disk, otherwise stored gzipped with a sha-pinned archive as `tests/test_public_coverage_goldens.py:26` does. Default-lane runtime of all `tests/test_rf1_*.py`: at most 180 s on the local machine. Mutation run: at most 45 min. More than 1.5× any estimate, or any ceiling exceeded, stops the phase at the owner gate (RF-D13) | As stated |
| D11 | Quirks the pins capture (section below) | (a) Pin them as they are and record each as an RF7 or successor open question (RF-R1, RF-R10). (b) Fix any of them here, which breaks RF-R1 and RF1-C2 | (a) |
| D12 | Existing exact pins (`test_artifacts.py:688`, `test_v70_phase6_corpus.py:71`, `test_verification_fixes.py:172`) | (a) Map them in `inventory.json` as `existing_nodes`, with no mutation obligation (RF1-C1 binds RF1's own pins). (b) Bring them into the mutation table too | (a) |

### Owner rulings (o)

(o) 2026-10-05, owner reply in chat: "approve D1–D12 as proposed, attested,
no panel". It answered the three gate asks: each row of the table above is
ruled as its *Proposal* column states; the owner attests under RF-R7 that the
source repository took no change to the `runtime` and `test-acceptance`
paths since the RF0 record (no remote configured, so the control rests on
this attestation, §6.12); and no review panel runs over the spec bytes.

## Quirks pinned as found (D11)

Recorded so that no pin is read later as an endorsement:

- Q1: the unknown-version message lists versions 1 to 7 and omits 8
  (`session_contract.py:1097–1106`). Already RF7 work under RF-D8.
- Q2: `cli._canonical_payload` (`cli.py:4293`) is the only canonical-JSON
  site without `allow_nan=False`.
- Q3: `extract.anchors._digest` and `judgments.digest` are hex validators
  matched by the `sha256_hex` pattern; `measure.promote._digest` hashes a
  file, and `evolve.service.final_record_file_sha256` reads no file.
  The family list's labels are kept; the pins record behavior.
- Q4: `session_contract.SESSION_CONTRACT_VERSION` means 3 after line 483,
  while version 8 has no named constant (RF8 names it).

## 8. Tests and verification

### 8.1 Cases (all in the default lane; expected file exit 0)

| Id | File | Case | Expect |
|---|---|---|---|
| T-CLI-TREE, -HELP, -EXIT, -MAP, -COV | `test_rf1_cli_pins.py` | §6.3 | pass at `e834c6e` |
| T-HELP[family, site], T-HELP-COV | `test_rf1_helper_pins.py` | §6.4 | pass |
| T-SEM-* | `test_rf1_semantic_pins.py` | §6.5 | pass |
| T-AGENT-* | `test_rf1_agent_cli_pins.py` | §6.6 | pass |
| T-SESSION[version, path], T-SESSION-DET | `test_rf1_session_pins.py` | §6.7 | pass |
| T-LAYER-EDGE[pair] | `test_rf1_layering.py` | §6.8 | xfailed (strict), 16 cases under D4 (a) |
| T-LAYER-RATCHET, T-LAYER-SCOPE | `test_rf1_layering.py` | §6.8 | pass |
| T-GOLD-MANIFEST | `test_rf1_pin_harness.py` | manifest equals files; manifest digest equals the constant | pass |
| T-GOLD-MANIFEST-NEG | `test_rf1_pin_harness.py` | a temporary copy with one golden byte changed, an extra file, a missing file | each fails the manifest check |
| T-GOLD-VERSIONS | `test_rf1_pin_harness.py` | every per-minor golden key has exactly the variants {py311, py313, py314}, and no key has only some of them | pass |
| T-INV | `test_rf1_pin_harness.py` | §6.10 | pass |
| T-NORM-1..5 | `test_rf1_pin_harness.py` | normalizer over generated inputs: N3 placeholder; N5 replaces a matching digest; N5 leaves a non-matching digest; N4 absence check fails when a nonce appears; non-JSON bytes fail with a named assertion | as stated |
| T-TOOL-1 | `test_rf1_pin_harness.py` | `mutate` over a generated mini package and table: one killing row, exit 0 | exit 0 |
| T-TOOL-2 | same | `--out` exists and the table is invalid | exit 11 (order) |
| T-TOOL-3 | same | hostile tables: non-object, duplicate keys, `NaN`, over 1 MiB, absent snippet, non-unique snippet, node with no row | exit 3, no traceback |
| T-TOOL-4 | same | the unmutated control fails | exit 1 |
| T-TOOL-5 | same | a row whose mutation is a no-op comment | survived, exit 1 |
| T-TOOL-6 | same | a row whose mutation makes the node hang, with `--timeout 2` | exit 1, row reported timed out |
| T-TOOL-7 | same | `capture` into an existing directory | exit 11, nothing written |
| T-ARCH-ALIAS | `test_gnd_arch.py` | §6.11 | pass |
| T-SRC | ledger command | `git diff --quiet e834c6e HEAD -- src/gnd .gnd-planning/milestones/public-launch` | exit 0 |
| T-DIFF-SCOPE | ledger command | `git diff --name-only e834c6e HEAD` lists only `tests/**`, `tools/**` and `.gnd-planning/milestones/code-refactoring/**` (RF1-C2) | exit 0 of the check script quoted in the record |

### 8.2 Selection ledger

| Obligation | Disposition | Command | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| New pins green at base (RF-R3, O1–O13) | run | `uv run pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py` → exit 0 | the new files, `tests/support/rf1_pins.py`, `tests/fixtures/rf1-pins/**`, `src/gnd/**` (read only) | Every RF1 deliverable is in these files | Any change to them or to `src/gnd` |
| Same, under the CI interpreters | run | the same command with `uv run --python 3.11` and `--python 3.13` → exit 0 | as above plus interpreter | D2; CI is unavailable (billing), so the local run is the evidence | Interpreter or lock change |
| RF1-C1 mutations | run | `uv run python tools/rf1_pins.py mutate --out <scratch>` → exit 0; report copied to `evidence/phase-RF1/` | `tools/rf1_pins.py`, `mutations.json`, the pin files, `src/gnd/**` | §6.9 | Any pin, table or `src/gnd` change |
| Tool behavior (RF0-OQ2) | run | `uv run pytest -q tests/test_gnd_arch.py` → exit 0 | `tools/gnd_arch.py`, `tools/gnd_layers.json`, its tests | §6.11 | Tool change |
| Existing consumers of the reused test support | run | `uv run pytest -q tests/test_coverage_cli.py tests/test_exp_session_e2e.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py tests/test_agent_cli.py tests/test_checker_families.py` → exit 0 | `tests/support/**` if any shared helper is touched | RF1 may import, but should not edit, existing support modules; if it edits one, its consumers are added here by name | Edit to any `tests/support` module other than the new one |
| Lint | run | `uv run ruff check tools/rf1_pins.py tools/gnd_arch.py tests/support/rf1_pins.py tests/test_rf1_*.py tests/test_gnd_arch.py` → exit 0 | those files | Repository lint gate | Any change to them |
| Planning links | run | `uv run pytest -q tests/test_development_scaffold.py` → exit 0 | `.gnd-planning/**/*.md` | New notes and record | Planning edits |
| T-SRC, T-DIFF-SCOPE | run | §8.1 | git tree | RF-R1, RF1-C2 | Any commit |
| Full default lane | cadence | not selected | — | RF1 adds tests and changes no imported product code; the pins themselves are the new default-lane load and are run above | Owner or CI selection |
| Distribution lane | cadence | vasiloglou/gnd-public#8 (open) owns the whole-tree retirement | — | RF0 D4 | Its merge |

### 8.3 Branch coverage of the new instruments

- Harness: control green or red (T-TOOL-1, T-TOOL-4); row killed or survived
  (T-TOOL-1, T-TOOL-5); timeout (T-TOOL-6); every table refusal (T-TOOL-3);
  exit order (T-TOOL-2); capture refusal (T-TOOL-7); coverage of nodes by rows
  (T-TOOL-3, "node with no row").
- Normalizer: N1/N2 placeholder and N3 (T-NORM-1), N5 both branches
  (T-NORM-2, T-NORM-3), N4 (T-NORM-4), N6 (T-SESSION-DET), malformed input
  (T-NORM-5).
- Golden manifest: missing, extra and changed file (T-GOLD-MANIFEST-NEG).
- Layering: XPASS fails (strict mode, by construction of `xfail(strict=True)`);
  ratchet with a new pair is shown red in T-LAYER-RATCHET's own negative case
  over a generated map (`gnd_arch` fixture helpers from `test_gnd_arch.py`).

## 9. Out of scope for RF1

Any `src/gnd` edit, including the quirks Q1–Q4. Byte pins of command handlers
marked `owed` (D9). Moving or merging anything. `notes/shim-inventory.md`
(RF2). Retiring or editing existing tests. The RF5-C2 entry-point rule (RF0
D12). Co-change. Repairing the distribution lane. Carryovers
`OQ-V72-P1-ARTIFACT-COPIES`, `OQ-V52-CLOSE-CANONJSON-1`,
`OQ-V52-P1-IMPORTWALK-1`, `OQ-V63-CLOSE-HELPER-TAIL-1`. Linux-only behavior
that cannot be observed on this macOS machine (see the boundary below).

## 10. Size

Estimate 4,350 hand-written lines (§6.1); ceiling and stop rule in D10. The
record reports measured sizes, golden bytes on disk, default-lane runtime
and mutation-run time.

## 11. Approval instrument

Proposed: D1 (a). The approved artifact is this prose, whose case inputs,
normalization rules and mutation granularity are enumerated in §6. The first
implementation commit lands `tests/fixtures/rf1-pins/README.md` (stories
only), `cases.json`, `mutations.json` and `inventory.json`, with the harness
red because no golden exists yet. The goldens are the answer key and live in
a separate directory from the README, so a later blind reading of the README
cannot see them.

## Boundary stated before implementation

- A characterization pin asserts that behavior did not change. It says
  nothing about whether the behavior is correct.
- CI is unavailable (GitHub billing). The 3.11 and 3.13 runs are local and
  macOS-only; ubuntu-specific behavior (for example FIFO or `O_NOFOLLOW`
  details in safe-filesystem pins) is unobserved until CI runs.
- Mutation kills prove that each pin can fail. They do not prove that the
  pinned inputs reach every branch of the code under the pin.

## Implementability sweep (before the gate, 2026-10-05)

Each requirement was checked once for whether some implementation can
satisfy it as written. Seven were repaired in place before this spec was
offered:

- Strict-JSON cap inputs apply only to sites that have a cap
  (`session_store._strict_object_bytes` has none).
- The checker coverage assertion names its source of constraint types (the
  meta-schema's `type` constants) and defines "violated" per modality, since
  a deontic violation is not reported as `fail`.
- The oracle pin no longer assumes `gnd synth` writes mutated populations
  for every model.
- Session fresh runs fall back to one accepted attempt where a version's
  builder supports only one, and the record names that version.
- The clock injection names the bindings the modules actually use
  (`import time`), not an assumed mechanism.
- T-GOLD-VERSIONS no longer requires per-minor goldens to exist when D2's
  capture finds no variance.
- The budget estimate is the sum of §6.1 (4,350), and the stop is 1.5× it.

Confirmed implementable: the mutation harness's `PYTHONPATH` copy takes
precedence, because `tests/conftest.py:35` inserts only the repository root
and `gnd` otherwise resolves through the editable install.

## Implementation findings, recorded as found

Each finding is stated where the run surfaced it. None changes an approved
decision; where one departs from the spec's text, the departure is named.

- **F1 (hardening; open question).** `synth.provenance._sha256_file`,
  `measure.promote._digest` and `transition.population_file_digest` block
  forever when handed a FIFO (the first helper capture hung on it). Only
  `exp.tests_runner._digest_regular_path` opens with `O_NONBLOCK`. A hang
  cannot be pinned, so the FIFO input is offered only to that reader.
- **F2 (refutes spec §6.5 T-SEM-VERB).** There is no `gnd verbalize MODEL`
  command; the only subcommand is `verbalize population`. Model verbalization
  is pinned through `gnd extract`, which writes `<stem>.verbalization.txt`.
- **F3 (new rule N7).** The session prompt embeds the absolute contract path
  (`cli.py:5436`), so every prompt digest varies with the temporary root.
  Prompt-digest fields and the `<prompt:sha256=…>` argv token become
  placeholders.
- **F4 (refutes the N4 premise).** The receipt nonce is published, as
  `attempt.json` `assurance_receipts[].process_receipt.nonce`. N4 is amended:
  a `nonce` field's value is a placeholder; staging names are still checked
  for absence.
- **F5 (new rules N9 and an N5 extension).** v1 and v2 evidence carries
  `production_identity()` and `producer_identity()`, which hash every
  `src/gnd` file (RF-R8) and would break every session pin on the first RF2
  edit. Both are replaced only where they equal the value computed in-process.
  A declared adapter's `executable_sha256` hashes the interpreter's path
  string (`declared_adapter.py:292`), and `policy_sha256` hashes a policy file
  that holds absolute paths; N5 now also accepts these declared inputs, still
  verify-then-replace.
- **F6 (new rule N8).** Tests-mode `result_sha256` digests cover pytest's
  JUnit file, which pytest writes with its own timings; they are placeholders.
- **F7 (harness).** The batch arm of `gnd check` writes to
  `sys.stdout.buffer`; the in-process runner's `StringIO` has no buffer and
  first produced a spurious exit 70. The batch pin runs as a real process.
- **F8 (a vacuous fixture, caught by the harness).** The resolver fixture used
  reference `mode: simple`, which `popvalidate._resolve_reference` and
  `model._resolved_primitive` do not follow, so both returned `None` for every
  flag. The mutation turning `is True` into a truthy test survived. With
  `mode: popular` the two semantics separate (`1` and `"yes"` resolve through
  the truthy sites only) and the row kills.
- **F9 (D2 measured).** 42 golden keys differ by interpreter and are stored per
  minor version. Causes, each seen in a diff: argparse layout (`cli-help`,
  `cli-exit`), stdlib JSON messages (3.14 appends `: nan`), the accepted set of
  `datetime.fromisoformat`, recursion-depth behavior, the `mimetypes` table
  (quirk Q5 below) in v1 session evidence, and pytest's banner retained in
  tests-mode stdout (v3).
- **F10 (size).** A first capture was 11.4 MB, almost all synth corpora. Synth
  output files are pinned by a per-file sha256 and size map, while the oracle's
  expected states stay pinned in full by `test_oracle`; any observed value over
  64 KiB is recorded by digest. Goldens are 2.8 MB of bytes.
- **F11 (N1 fallback everywhere).** No clock is injected. Injecting a counting
  clock into `agent_cli` or the session controller would feed their deadline
  arithmetic, and the number of clock reads varies with scheduling, so N1/N2
  placeholders apply to every monotonic and seconds field.
- **F12 (pinned as found).** After `result.json` is removed from a completed
  run, `read_resume_state` refuses for v1–v6 ("feedback identity does not bind
  the current immutable attempt") and succeeds for v7 and v8. Resuming through
  the CLI (the test patches `cli._next_session_run_root` to return the
  existing run) completes for v1, v4, v5 and v6, refuses for v2 (persisted
  feedback inconsistent) and v7/v8 (controller budget exhausted), and refuses
  for v3 because tests-mode creates its run root exclusively and has no resume.
- **F13 (departure from §6.5).** `validate_claim_graph` and
  `assurance_inheritance.validate_result` are mapped to their existing exact
  refusal tests rather than given new pins; `compare_observations` has a new
  pin. The per-case assurance block is pinned inside every T-SEM-CHK JSON
  report.
- **F14 (D3 measured).** The table has 167 rows against the estimate of about
  90. Helper sites, datetime sites and single functions use a function-entry
  `raise`, which proves the node exercises that exact function. No source
  mutation is specific to one checker case or one session version, so their
  "rows of their own" reuse one mutation per lane, each row naming one node.
  Refusal branches (diff vocabulary mismatch, extract of temporal models,
  version-probe failure, tests-mode resume) have their own rows. Three meta
  nodes are listed in the table's `exempt` list with reasons.
- **F15 (tool).** `mutate --jobs N` runs rows in parallel, each against its own
  source copy and pytest temporary root. `capture` runs the pin files in
  capture mode, which exercises the same observation code as the tests.
- **F16 (D5 measured).** The unified alias resolver changes no count: the
  tool's output at `e834c6e` is byte-identical before and after, and identical
  to `metrics-RF0.json`. The new lexical-scope test was red against the old
  tool.

### Quirk added

- Q5: the media type recorded in a candidate inventory comes from the stdlib
  `mimetypes` table, so a `.yaml` candidate is `application/octet-stream` under
  3.11 and `application/yaml` under 3.13 and later.
