# Round 2 — Reader 2: implementability, homes and layers

**Digests matched.** Plan r2 is `e0668e30…3bb9` and IL1 spec r2 is `4a06f583…f5af8`.

**Verdict: approve-with-fixes.** All six of my round-1 blockers are resolved by the r2 bytes. r2's own changes introduce four hardening defects and one completeness gap. None of them is blocking.

**Scope.** I diffed r1 against r2 snapshots under `evidence/` and checked the result against code at `63f7f1f`:
- `commands/export.py`, `commands/checking.py`
- `ilp_service.py`, `ilp_popper.py`, `ilp_rewrite.py`, `ilp.py`
- `model_index.py`, `model/_validation.py`, `process.py`
- `tools/gnd_entrypoints.json`, `tools/gnd_layers.json`
- the RF1 goldens and both schemas
- `tests/test_ilp_bridge.py`, `tests/test_ik_close.py`, `tests/test_rf1_cli_pins.py`

I probed the regex with a scratch script at `<scratchpad>/review2/reader-2/probe.py`. I changed no repository file.

## Round-1 blockers

| Finding | Status | Evidence |
|---|---|---|
| R2-F1 `EXPORT_TARGETS` dropped `neutral` | **resolved** | Spec 128 adds an `exports` field. Spec 134 makes `EXPORT_TARGETS` the `exports=True` targets → `("popper","neutral")`. Spec 142 sets `neutral: exports=True, render=None`. Plan 203 agrees. This matches `export.py:108` and the IK6 walk's `--target neutral`. |
| R2-F2 RF5 entry-point edge from `choices=` | **resolved** | Spec 158–168 and plan 211–213 keep the literal `choices=("popper","neutral")` and make no `gnd_entrypoints.json` change. T2 (spec 313) uses parser introspection, which already has a precedent in `test_rf1_cli_pins.py:80–88`. The gate (spec 331) names `test_rf5_commands.py` and `test_gnd_arch.py`. There is no import at parser-construction time. |
| R2-F3 sorted order vs RF1 goldens | **resolved** | Spec 133 and plan 195–196 use declaration order: popper, neutral, then appended targets. T1b (spec 312) pins `popper, neutral`. This matches `{popper,neutral}` in `goldens/cli-help` and `cli-exit/gnd_export_ilp.json` and `gnd_import_ilp-rules.py31{1,3,4}.json`. |
| R2-F4 octal fix must change `_TOKEN` | **resolved** | Spec 65, 200–204 and plan 393 add `\\[0-7]{1,7}\\` before `\\.` (`ilp_popper.py:34`). My probe of that regex tokenizes `'\001\'`, `'\101\'`, `'\7\'` and `'\4177777\'` whole. The boundary case `'a\1\'),g(A,B,'b')` yields `'a\1\'`, so the octal reading wins as T4 (spec 316) expects. |
| R2-F5 T4 beyond-Unicode case | **resolved** | T4b (spec 317) uses `'\4200000\'`. `int('4200000',8)` is greater than 0x10FFFF. `'\4177777\'` is exactly 0x10FFFF and is accepted. `'\154000\'` is 0xD800, a surrogate. |
| R2-F6 schema `target` enums | **resolved** (D9) | Plan IL-R7 (128) and §5 (508–511) widen both enums within `/1`, one phase at a time. Spec 82, 162–165 and T2 pin both enums to the registry. The enums are at `ilp.schema.json:254–258` and `ilp-import.schema.json:30–34`, as cited. A defect in how T2 pins them is R2-2-F1 below. |

Other gate checks:
- Every file in the spec's literal gate command (spec 331) exists, except `tests/test_ilp_learners.py`, which the spec creates.
- The six `ProcessLimits` names in spec 228 match `process.py:39–44`.
- `ModelIndex.supertype_closure` excludes the type itself (`model_index.py:264–274`), so spec 189's `{t} | …` is correct.

## Self-inflicted findings (r2-introduced only)

- **R2-2-F1** (hardening, medium): T2's single equality rule conflicts with r2's own IL4 design.
  - **Claim:** Spec 135 defines `IMPORT_TARGETS` as "every target". T2 (spec 162–165, 313) requires that the `import ilp-rules` choices and both schema enums equal it. But plan 291–297 imports `amie` through a new `gnd import mined-rules`, not `ilp-rules`.
  - **Effect when IL4 lands:** to keep T2 green, `ilp-rules` would have to accept `--target amie`, even though it requires `--labels`/`--reported-coverage` (`checking.py:447–452`). And `ilp-import.schema.json` would list `amie` while its `command` const stays `"import ilp-rules"`.
  - **A second problem:** the export-index enum (`ilp.schema.json:254`) is pinned to `IMPORT_TARGETS`, not `EXPORT_TARGETS`. Any later import-only target, such as a possible `llm`, would make the two drift.
  - **Reproduce:** read spec 133–135 and 313 against plan 206 and 291–297.
  - **Repair:**
    - Define `IMPORT_TARGETS` as the entries with `contract == "labelled-clauses"`.
    - Pin the `ilp.schema.json` enum to `EXPORT_TARGETS`.
    - Have IL4 name its report schema or `command` value.

- **R2-2-F2** (hardening, medium): the join check's type source is not reachable from where the spec puts it.
  - **Claim:** Spec 170–193 places check 9b inside `ilp_rewrite`, reading closures through `ModelIndex.supertype_closure`. But `rewrite(clause, index, neutral, columns)` (`ilp_rewrite.py:64–66`) receives no model or index.
  - **Why the neutral form cannot supply it:** its `types[]` rows carry `object_type` but no `subtype_of` (`ilp.py:133–147`).
  - **What breaks:** the spec names no signature change. The existing helper at `tests/test_ilp_bridge.py:554` calls `rewrite` with four positional arguments, so a new required parameter would break T1 ("unchanged pass").
  - **Repair:**
    - Compute a closure map once where `ModelIndex` already exists (`ilp.py:113–115`, or `_prepare`).
    - Carry it on the prepared state, not on the `gnd-ilp/1` wire (IL-R7).
    - Pass it to `rewrite` as a keyword-only parameter with a default.
    - State all of this in spec §6.

- **R2-2-F3** (hardening, medium): T9's "assert the recorded … report SHA-256" cannot be reproduced.
  - **Claim:** The import report embeds the paths as given on the command line: `inputs.*.path` and `proposal` (`ilp_service.py:456–461`).
  - **What differs between the two runs:** the evidence run happens in scratch, and the retained `import-report.json` is redacted with `<scratch>` placeholders (spec 251–253, IL-R10). A default-gate replay under a pytest tmp dir writes different paths.
  - **Result:** the digests cannot match.
  - **Reproduce:** read `ilp_service.py:456–461` against spec 251 and 325.
  - **Repair, either of:**
    - (a) Run both the evidence import and the replay from a fixed cwd with identical relative paths and fixed `--actor`/`--requested-at`.
    - (b) Assert the digest of a path-normalized report (path fields removed), plus the exit and the per-clause rows.

- **R2-2-F4** (hardening, low): T4b's 8-digit case cannot get the octal-specific message with the specified `_TOKEN` change.
  - **Claim:** T4b (spec 317) and C3 (plan 396–397) require every refusal to carry the octal-specific message. On its own, `'\12345670\'` fails the new alternative `\\[0-7]{1,7}\\`. `\\.` then eats the closing `\'`, so `_Parser.__init__` raises the generic ``unexpected "'"`` (`ilp_popper.py:91–92`).
  - **Context dependence:** if a later quote follows on the line, the token instead spans `'\12345670\'),g(A,B,'`. In that case only `_unquote` can name the octal problem.
  - **What does work:** `'\101'` (unclosed) does reach `_unquote`, so that case is achievable.
  - **Reproduce:** with the spec's regex, `Q.match(r"'\12345670\'")` returns `None`.
  - **Repair, either of:**
    - (a) Add a diagnostic tokenizer alternative for `\\[0-7]+` that is not a valid closed form, and refuse it with the octal message.
    - (b) Let T4b expect the generic tokenizer message for this case.

- **R2-2-F5** (completeness, low): r2's new IL4 command text leaves out its own RF1 and RF5 effects.
  - **Golden impact:** making `--labels` non-required on `gnd export ilp` (plan 291–293) changes the existing help golden's usage line. It also changes the `unknown_flag` exit golden, whose stderr reads "required: model, --labels, --target, --out" (`cli-exit/gnd_export_ilp.json`). Plan §5 (509, 514) mentions only new targets and new golden files.
  - **Argparse limit:** argparse cannot express "the target decides which one is required", so this becomes a post-parse check. Its exit (64) should be stated.
  - **Entry-point binding:** `service_bindings` in `gnd_entrypoints.json` are keyed by command module, and `import` subcommands live in `gnd.commands.checking`, which is already bound to `ilp_service`. So "bound in `gnd_entrypoints.json`" (plan 296, 372) is a no-op unless a new command module is meant.
  - **Repair:** in plan §4 IL4 and §5, name the changed existing goldens, the post-parse exit, and the home module of `mined-rules`.
