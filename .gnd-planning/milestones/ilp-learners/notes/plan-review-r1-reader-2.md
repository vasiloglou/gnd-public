# Reader 2 — implementability, homes and layers

Both digests match the expected values:
- `ilp-learners-plan.md`: `6cb10d97…8e463`
- `phase-IL1-spec.md`: `59629173…6b027`

**Verdict: request-changes.** Five of the IL1 spec's surfaces cannot be built as written:
- `EXPORT_TARGETS` leaves out `neutral`;
- the `choices=` wiring breaks the RF5 entry-point policy;
- the "sorted" registry order changes the RF1 goldens;
- the octal fix names the wrong function;
- one T4 expectation is arithmetically wrong.

The plan also misses the existing schema `target` enums and the label-free CLI shape that IL4 needs.

Scope: the plan and IL1 spec at HEAD `63f7f1f`, checked against `src/gnd/export/ilp*.py`, `src/gnd/commands/{export,checking}.py`, `tools/gnd_layers.json`, `tools/gnd_arch.py`, `tools/gnd_entrypoints.json`, `src/gnd/{process,agents}.py`, the schemas, the RF1/RF5/RF6 tests and `pyproject.toml`. Probes were read-only. I wrote one scratch export of the refunds example under the session scratchpad (`…/scratchpad/review/reader-2/ilp`). I changed no repository file.

## Findings

- **R2-F1** (blocking, high): `EXPORT_TARGETS` as specified drops `neutral` from `gnd export ilp`.
  - Spec line 74 defines it as "targets with render is not None". Spec line 67 sets `render` to `None` for `neutral`. Spec lines 85–87 say export `choices=` come from `EXPORT_TARGETS` "because the sets are unchanged".
  - Today export accepts `choices=("popper","neutral")` (`src/gnd/commands/export.py:108`). `export_tree` handles `neutral` with an empty rendering (`src/gnd/export/ilp.py:211`, `ilp_service.py:161`).
  - The IK6 walk exports with `--target neutral` (`tests/test_ik6_walk.py:118,138,158`). `docs/reference/ilp-bridge.md:54` documents it.
  - So IL1-C1 (byte-identical IK6 and RF1 goldens) would fail.
  - Reproduce: `uv run gnd export ilp --help` shows `{popper,neutral}`.
  - Repair: define `EXPORT_TARGETS` as every target (`neutral` exports `neutral.json` only), or give `neutral` an explicit empty-render entry. Keep `IMPORT_TARGETS` as every target.

- **R2-F2** (blocking, high): taking `choices=` straight from the registry breaks the RF5 entry-point policy.
  - Spec lines 85–86 have both command modules read `EXPORT_TARGETS`/`IMPORT_TARGETS` from `gnd.export.ilp_learners`. Spec line 88 registers that module only in the layer map.
  - `tools/gnd_entrypoints.json` binds `gnd.commands.export` and `gnd.commands.checking` to `["gnd.export.ilp_service"]` only.
  - `tools/gnd_arch.py:825–861` rejects any service target whose name does not end in `.service`/`_service`, and flags every other import from an entry module (lazy ones included) as "entry-point imports a non-service module", unless an exception row says why.
  - A new `commands → ilp_learners` edge is therefore an RF5 violation. Neither the plan (§3 lines 206–218, §9 line 357) nor the spec names `gnd_entrypoints.json`.
  - It would also move the `ilp_service`/registry import from dispatch time (`commands/export.py:130`, `checking.py:668`) to parser-construction time, so `jsonschema`, `measure.labels` and `ilp_popper` load on every `gnd` invocation.
  - Repair, either of:
    - (a) `ilp_service` re-exports the target tuples, and the commands read them through the already-bound service with a parser-time import. State the startup-import consequence.
    - (b) Keep literal `choices=` in the commands, and add a T2 test that they equal the registry.
  - Name `tools/gnd_entrypoints.json` and `tests/test_rf5_commands.py` in the IL1 gate.

- **R2-F3** (blocking, medium): "sorted by target" changes the RF1 help and exit goldens.
  - Spec line 73 says `LEARNERS` is "sorted by target", which gives `("neutral","popper")`.
  - Both parsers spell `{popper,neutral}` today (`commands/export.py:108`, `checking.py:452`). The goldens pin that order and the matching argparse error text: `tests/fixtures/rf1-pins/goldens/cli-help/gnd_export_ilp.json`, `cli-exit/gnd_export_ilp.json`, and `gnd_import_ilp-rules.py31{1,3,4}.json`.
  - Reproduce: `uv run gnd export ilp m --labels l --target bogus --out o` prints "choose from popper, neutral" and exits 64.
  - Repair: the tuples keep declaration order, not sorted order (popper, neutral, then each later adapter appended). T2 should pin that order.

- **R2-F4** (blocking, high): the octal fix must change the tokenizer `_TOKEN`, not only `_unquote`.
  - Spec line 21 and spec §6 lines 90–95 ("`ilp_popper._unquote`, ~10 lines"), plus §4 rule 1 ("the changed loader is … the quoted-atom reader"), place the whole change in `_unquote`.
  - But the quoted-atom alternative at `src/gnd/export/ilp_popper.py:34` is `'(?:[^'\\\n]|\\x[0-9a-fA-F]{1,6}\\|\\.)*'`. In `'\001\'` the closing `\'` is eaten as an escaped quote, so the token never matches. The parser fails at line 92 with `unexpected "'"` before `_unquote` runs.
  - Reproduce: `_TOKEN.match(r"'\001\'")`, `r"'\101\'"` and `r"'\7\'"` all return `None`.
  - So T4's first three cases (spec line 138: "the first three parse") cannot pass with a `_unquote`-only change.
  - Repair: add `\\[0-7]{1,N}\\` to `_TOKEN` before `\\.`, as the hex form already is, and say so in spec §2, §4 and §6. Add a T4 case where the octal reading and the escaped-quote reading compete, such as `'a\1\'b'`.

- **R2-F5** (blocking, medium): one T4 "beyond Unicode" case is a valid code point.
  - Spec line 138 expects `'\4000000\'` to exit 3 as "beyond Unicode".
  - Octal 4000000 is 1048576 (0x100000), which is below 0x10FFFF. That is a valid Unicode scalar, so the spec's own check (line 93) accepts it and the test expectation is wrong.
  - `'\154000\'` is 0xD800, so the surrogate case is correct.
  - Repair: use `'\4200000\'` (0x110000) for "beyond Unicode".

- **R2-F6** (blocking, medium; plan level): adding a new `--target` changes two existing wire schemas, which IL-R7 forbids without a named bump.
  - `target` is the closed enum `["popper","neutral"]` in `src/gnd/ilp.schema.json:254–258` (the `gnd-ilp-export/1` `export.json` index) and in `src/gnd/ilp-import.schema.json:30–34` (`gnd-ilp-import/1`).
  - Plan IL-R7 (line 82) keeps those wires byte-identical "unless a phase spec names the change and its version bump". Plan §5 (lines 310–316) lists only CLI goldens, a docs section and new IL3/IL4 schemas for IL2–IL5.
  - Every adapter phase therefore makes an unplanned wire change, and the enums become a second, unchecked copy of the registry.
  - Repair, in two parts:
    - Plan §5 decides now whether widening the enums is a compatible `/1` change or a `/2` bump.
    - IL1 adds a T2 check that both schema enums equal the registry targets, so later phases cannot drift.

- **R2-F7** (hardening, high; plan level): the IL1 registry and the shared service cannot carry IL3/IL4 as the plan describes.
  - Plan IL-R3 (line 78) says every adapter is one entry with `render` taking the neutral form to files. Spec line 69 types `render` over the labelled neutral dict, and line 71 has `contract: Literal["labelled-clauses"]`.
  - IL4 (plan lines 166–177) exports from `--population POP` with no labels. Today:
    - `gnd export ilp` has `--labels` `required=True` (`commands/export.py:106`);
    - `_prepare` refuses any manifest that is not class-mode (`ilp_service.py:141`);
    - `gnd import ilp-rules` requires `--labels` and a run record with per-example coverage (`checking.py:447–450`, `ilp_service.py:322–327`);
    - `_placeholder` binds `prepared.manifest.sha256` (`ilp_service.py:229–231`).
  - IL3 renders from populations into a feature table, not into the neutral form either.
  - Neither phase's CLI shape is planned (mutually exclusive `--labels`/`--population`? a new import subcommand?), nor its RF1 golden impact.
  - Repair: make IL1's `Learner` contract field and `render` input open, so IL3/IL4 can add a sibling contract without reshaping the dataclass. Plan IL4 should name its CLI surface and its RF1/RF5 consequences now.

- **R2-F8** (hardening, medium): IL5 has tests but "no source module", and `gnd.agents` cannot record or pin a model id.
  - Plan line 213 puts the proposer in an `evidence/IL5/` script only. IL5-C1/C2 (lines 279–284) then require a deterministic prompt builder with a golden digest and a hostile-fixture test. Tests under `tests/` would have to import Python from `.gnd-planning/`; the only precedent loads JSON (`tests/test_rf4_review_regressions.py:12`).
  - The neutralizer it must reuse, `verbalize._neutralize` (IK-R5), is private.
  - `gnd.agents` offers only `claude` and `codex` (`src/gnd/agents.py:53–55`). Their closed argv has no model flag (`agents.py:149–175`), and the result records the CLI version, not a model. IL5-C3's "named agent adapter and model id" (line 285) is not something `gnd.agents` provides.
  - The import uses `--target neutral`, so `method` becomes `ilp-neutral` (`ilp_service.py:328`), which does not identify the LLM.
  - Repair, either of:
    - (a) Give the prompt builder a source home in the `export` lane plus a layer-map row.
    - (b) Make IL5-C1 a check over the evidence script's output digest only.
  - In both cases, state how the model id is recorded (for example the CLI default as reported, in `learner.version`), and whether `method` should distinguish the proposer.

- **R2-F9** (hardening, medium): the live-run steps do not fit `run_bounded_process` or the parser input.
  - Spec IL1-D4 (line 127) fixes only a wall clock and a 16 MiB output cap. `ProcessLimits` requires six fields: timeout, terminate grace, and stdin, stdout, stderr and total byte limits (`src/gnd/process.py:34–44`). `run_bounded_process` is `async` and takes a trusted argv tuple plus an explicit `env` (`process.py:385–392`).
  - Spec line 105 says "the printed program saved verbatim" and then imports it with `--target popper`. Popper's console output normally wraps the program in banner and score lines (`****` / `Precision:…`), and `_TOKEN` has no `*`. A verbatim save would fail as `unparsable` for a reason outside the adapter.
  - Also, `CLAUSES_CAP` is 1 MiB (`ilp_service.py:51`), well below the 16 MiB capture cap.
  - Repair:
    - Fix all six limits in IL1-D4.
    - Specify how the script extracts the program block, or calls Popper's API, and retain the raw stdout separately.
    - Note the 1 MiB clauses cap.

- **R2-F10** (completeness, medium): T5 does not discharge the "IK6 join space" row it claims.
  - The carried residual is that the refunds example's stand-in learner join branch has no case: "this model yields 40 comparison candidates and 0 joins; the join code is example code with no case" (`induced-knowledge/010-phase-IK6.md:164–166`; `src/gnd/examples/refunds/stand_in_learner.py:70–72`, where every argument of Q must join P).
  - The importer's connectivity check already exists (`ilp_rewrite.py`, `disconnected-body`). A hand-written joining clause over `f_refund_amount`/`f_refund_channel` through the shared `t_refund` variable tests the importer, not the learner join space. A probe export shows the three predicates all share `t_refund`.
  - Repair, either of:
    - (a) T5 says it closes the importer half only and carries the stand-in learner row.
    - (b) Add a fixture that produces at least one stand-in join candidate.

- **R2-F11** (completeness, medium): the IL1 gate and the plan's consumer list leave out existing pinning tests and per-phase controls.
  - The spec's gate (line 144) leaves `<IK6 walk and RF1 CLI golden files> <layer and RF5 controls>` as placeholders, though all of them exist today:
    - `tests/test_ik6_walk.py`, `tests/test_rf1_cli_pins.py`, `tests/test_rf5_commands.py`;
    - `tests/test_rf1_layering.py`, `tests/test_gnd_arch.py`, `tests/test_rf6_query_policy.py`;
    - `tests/test_public_built_inventory.py`.
  - `tests/test_ik_close.py` imports `ilp_popper.parse_program` and monkeypatches `ilp_service._load_candidate` (lines 110, 150–158). It is an affected consumer missing from plan §9 (line 357).
  - `tests/test_ilp_bridge.py:393–409` pins source order by token (`"learner-mismatch"`, `"_prepare("`, …). The registry rewrite must keep those tokens.
  - In the plan, the RF6 query ceiling (310 of 320, `test_rf6_query_policy.py:178`) and the schema inventory (`tests/support/runtime_schema_inventory.py`) appear only at IL6-C3 (line 296). IL3/IL4's new `fact_types` reads and schemas would fail those controls in their own phases first.
  - Repair: name the files in the IL1 gate now (my run of the first four passes: 513 tests). Plan §9 should carry RF5, RF6 and schema-inventory controls in every phase.

- **R2-F12** (completeness, low): the DAG, the risk table and T7 disagree with each other.
  - The DAG (line 197) shows IL2–IL5 in parallel, but lines 202–203 serialize them in the D4 order, and D4 is only "proposed" (line 387). The DAG should show the serial chain IL2 → IL5 → IL3 → IL4, conditional on D4.
  - The risk control (line 322) promises a check of the wheel metadata. Spec T7 (line 141) checks only `pyproject.toml`. Either add the wheel check (for example in the installed-candidate lane) or narrow the risk text.

Verified correct:
- `ilp_service.LEARNER` has no user outside its module and is not in `__all__` (`ilp_service.py:48,56,319–321`).
- `_unquote`, `_prepare` and `_read_clauses` exist as named.
- The `live` marker exists and is deselected by default (`pyproject.toml:73,81`).
- `gnd.process.run_bounded_process` and `gnd.agents.invoke_agent` exist, and both modules are in the infrastructure layer.
- An unknown `--target` exits 64.
- The IK2 `method` field is a free string (`coverage.schema.json:539–541`), so `ilp-ilasp` and similar are schema-valid.
- The new module homes fit the `export` lane with zero allowances.
