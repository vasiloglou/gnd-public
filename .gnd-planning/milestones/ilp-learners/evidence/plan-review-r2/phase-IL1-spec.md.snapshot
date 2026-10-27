# IL1 — Learner registry, join check and a real Popper run

## 1. Status

**Draft r2 (p1), awaiting the plan's confirmation round, plan approval and then
this phase's owner gate.**
- **Nothing exists yet.** Nothing is implemented, installed or run.
- **Before any install,** IL1-D3 (the install commands and downloads) and
  IL1-D8 (the licences) must be ruled.

## 2. Provenance

- **Plan:** [ilp-learners-plan.md](ilp-learners-plan.md) r2, §0, §2 "The
  learner registry" and "The type-confused join check", and §4 IL1.
  - **The plan's review:** r1 was reviewed in round 1
    ([disposition](plan-review-r1-disposition.md)).
  - **The owner's rulings,** 2026-10-27 (o): D2, D8–D12, in plan §10.
- **This spec:**
  - r1 (SHA-256 `59629173…b027`) was read by the same four readers.
  - **r2 applies the disposition's themes A, B, C, G (spec part), H and I, and
    D12. r2 bytes carry no review opinion (p1).**
- **Inherited:**
  - the IK5 spec (`../../induced-knowledge/notes/phase-IK5-spec.md`) §6,
    IK5-D9, IK5-D12 and IK5-D13;
  - records `../../induced-knowledge/007-phase-IK5.md` and `010-phase-IK6.md`
    (164–166);
  - the close record `../../induced-knowledge/012-milestone-close.md`: rows
    IK5-Q5, IK5-Q2 and "IK6 join space".
- **Source inspected at `63f7f1f`:**
  - `src/gnd/export/ilp_service.py`: `LEARNER`, `_prepare`, `_read_clauses`,
    `_cmd_import_ilp_rules`;
  - `src/gnd/export/ilp_popper.py`: `_TOKEN`, `_unquote`, `parse_program`;
  - `src/gnd/export/ilp_rewrite.py`: checks 1–10;
  - `src/gnd/export/ilp.py`: `export_tree`;
  - `src/gnd/commands/export.py:108` and `src/gnd/commands/checking.py:452`;
  - the `target` enums in `src/gnd/ilp.schema.json:254–258` and
    `src/gnd/ilp-import.schema.json:30–34`;
  - `src/gnd/model/_validation.py`: `_ancestor_closure`, and the
    `semantic:op-term-type-compat` rule;
  - `src/gnd/process.py`: `ProcessLimits`;
  - `src/gnd/examples/refunds/stand_in_learner.py`;
  - `tests/test_ilp_bridge.py`: the T10 source-order pins;
  - `tests/test_ik_close.py`: `joined_hits` and `DOWNSTREAM_JOINED`.

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| IL1-C1: registry in declaration order, no learner-name branch, fake entry reaches render/method/learner check, CLI choices and schema enums equal the registry, goldens byte-identical except listed C2 cases | plan §4 (p1) | §6 registry; T1, T1b, T2, T3 |
| IL1-C2: `type-confused-join` for every target; compatible joins unchanged; neutral record naming a registered learner refuses | plan §4 (p1); D12 (o) | §6 join check, neutral binding; T5, T5b |
| IL1-C3: tokenizer and `_unquote`; every escape form the pinned SWI writes; boundary and token-boundary cases | plan §4 (p1); IK5-Q2 | §6 escapes; T4 |
| IL1-C4: one live run under IL-R9; one outcome from the closed list; retained artefacts; default-gate replay | plan §4 (p1); IK5-Q5; D2 (o) | §6 live run; T6 (live), T9 |
| IL1-C5: a stand-in learner join candidate, or the row stays carried with its reason | plan §4 (p1); 010:164–166 | §6 join space; T11 |
| IK2 residual: does real learner output fit the induction block without loss | IK2 spec §15 via IK5 spec §3 | live-run record question 3 |
| IL-R1 to IL-R11 and IK-R1 to IK-R12 | plan §0 | §4 |
| IK5-D12 (o): no GND command runs a learner | IK5 spec §7 | kept (plan D3 proposed (a)) |
| IK5-D9 (o), D10 (o): all-or-nothing | IK5 spec §7; plan §10 | unchanged; a C2 refusal refuses the whole import |

## 4. Rules bound to IL1 (p1: every plan §0 rule by name)

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | **Changed loaders:** the Popper tokenizer (`_TOKEN`) and the quoted-atom reader (`_unquote`). Every octal form outside the grammar exits 3 with line and column and an octal-specific message, never a traceback (T4 hostile cases). **Two new readers,** each capped before it reads and total: the replay test's reader of the live record (JSON through the RF7 policy) and the evidence script's program-block extractor. |
| 2 Algorithm bound | **The join check** is linear in literals × join sites per clause, and K ≤ 32 (IK5-D14); its work joins the import's existing work counter (T5c). **`_unquote`** stays linear in the token. |
| 3 Validation order | **The join check** runs after check 9 and before check 10, so no existing refusal changes name. The `test_ilp_bridge.py` T10 token order is unchanged. **The neutral learner check** sits at the existing `learner-mismatch` site. |
| 4 One walk | **One registry** serves export, clause reading, the learner binding and the CLI equality test. **One join check** serves every target. |
| 5 One home | `docs/reference/ilp-bridge.md` stays the normative home. The fragment table gains the `type-confused-join` row there only. |
| 6 Measurement | **C1** is decided by golden bytes. **C4** is decided by a replay test over committed bytes, so the live run is a claim that can fail (T9). |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1 | T7 checks `pyproject.toml` and the installed `gnd` distribution's `Requires-Dist`. |
| IL-R2 | **The script** is `evidence/IL1/run_popper.py`, under `run_bounded_process`. **The test** is `tests/test_ilp_live.py`, marked `live`. **Installs** use a scratch prefix and approved downloads only (IL1-D3). |
| IL-R3 | The join check lives in `ilp_rewrite`; no adapter has its own. |
| IL-R4 | The run record's coverage comes from SWI evaluating `bk.pl` plus the extracted program. Popper's printed scores are kept verbatim and compared in the record. The script never calls GND to make the record. |
| IL-R5 | Popper's, SWI-Prolog's and clingo's licences are recorded from upstream URLs before download (IL1-D8). |
| IL-R6 | Popper's stdout is untrusted. Only the extracted block reaches the capped parser (1 MiB, `CLAUSES_CAP`). |
| IL-R7 | IK5 wires are unchanged. No enum widens in IL1, but T2 pins both enums to the registry. |
| IL-R8 | The input is the IK6 refunds example only, with its export digest recorded. |
| IL-R9 | §6 "Live run" fixes the outcome list, settings, limits and the amendment path. |
| IL-R10 | T8 scans the milestone directory. The script passes `HOME`, `USER` and `TMPDIR` into the bounded environment and writes `<scratch>` placeholders. |
| IL-R11 | A `type-confused-join` refusal refuses the whole import. |

**Inherited rules (IK-R).**

| Rule | Binding |
|---|---|
| IK-R1 | Admission is unchanged: `_envelope` writes `induced`/`proposed`/`deontic`, and `_enforce_d12` gates it. IL1 adds refusals, never admissions. |
| IK-R2 | Unchanged. GND computes coverage and support; the live record's sets are compared. |
| IK-R3 | Goldens are byte-identical, except IK5 corpus cases that the join check newly refuses. Those are listed in the record as an intended change under D12 (o). |
| IK-R4 | No ORM schema change. |
| IK-R5 | No new rendered free text. |
| IK-R6 | No new population reads. The join check reads the in-memory neutral form. |
| IK-R7 | `gnd.export.ilp_learners` is in the `export` lane. No new command edge (literal `choices=`). The allowance count stays 0. The join check reads type closures through ModelIndex; any new RF6 query site is entered in the census, within the ceiling. |
| IK-R8 | Popper runs only from the evidence script, bounded. |
| IK-R9 | This table and the standing-rules table. |
| IK-R10 | T8. |
| IK-R11 | Live provenance is written by the unchanged import and carries opaque ids. |
| IK-R12 | The live-run limits and settings below are fixed before the run. |

## 5. Goal

**Export and import, through one registry.** On every IK5 and IK6 fixture,
`gnd export ilp --target {popper,neutral}` and `gnd import ilp-rules --target
{popper,neutral}` exit and write exactly as at `63f7f1f`. The only exceptions
are clauses that newly exit 3 `type-confused-join`, which are listed.

**The parser.** It reads SWI octal escapes.

**The live run.** One real Popper run over the IK6 refunds export ends in one
outcome from the closed list. A default-gate test replays its committed bytes
and gets the recorded exit.

## 6. Design

### Registry (`src/gnd/export/ilp_learners.py`, new, ~70 lines)

```python
@dataclass(frozen=True)
class Learner:
    target: str                      # the --target spelling
    learner: str | None              # required run-record learner.name; None: any name that is not another entry's learner
    method: str                      # IK2 method token: f"ilp-{target}"
    exports: bool                    # gnd export ilp accepts this target
    render: Callable[[dict[str, Any]], dict[str, bytes]] | None   # None: no files beyond neutral.json
    parse: Callable[[str], dict[str, Any]] | None                  # None: the input is gnd-ilp-clauses/1 JSON
    contract: str                    # "labelled-clauses"; IL4 adds "unlabelled-horn"

LEARNERS: Mapping[str, Learner]      # declaration order: "popper", "neutral"; later targets appended
EXPORT_TARGETS: tuple[str, ...]      # targets with exports=True, in declaration order -> ("popper", "neutral")
IMPORT_TARGETS: tuple[str, ...]      # every target, in declaration order               -> ("popper", "neutral")
def learner(target: str) -> Learner  # KeyError is an internal error (argparse already refused)
```

**The two entries.**
- `popper`: `learner="popper"`, `exports=True`, `render=ilp_popper.render`,
  `parse=ilp_popper.parse_program`.
- `neutral`: `learner=None`, `exports=True`, `render=None`, `parse=None`.

**Changes in `ilp_service`.**
- `LEARNER` is removed. It has no user outside the module and is not in
  `__all__` (IL1-D2).
- `_prepare` calls `learner(target).render`.
- `_read_clauses` calls `learner(target).parse`, or otherwise reads JSON.
- `method` comes from the entry.
- **The learner check:**
  - For an entry with `learner` set, `learner.name` must equal it.
  - For `neutral`, `learner.name` must not equal any entry's `learner`.
  - Either failure is exit 3 `learner-mismatch`, at the existing site (p1).
- **The tokens pinned by `test_ilp_bridge.py` T10 stay:** `_read_clauses(`,
  `_prepare(` and `learner-mismatch`, in their pinned order.

**The CLI (p1).**
- `commands/export.py` and `commands/checking.py` keep their literal
  `choices=("popper", "neutral")`. Importing the registry at
  parser-construction time would add an entry-point edge that RF5 rejects,
  and would load `jsonschema` on every `gnd` call.
- T2 asserts, by parser introspection, that each `choices` equals
  `EXPORT_TARGETS` / `IMPORT_TARGETS`. It also asserts that the `target` enums
  of `ilp.schema.json` and `ilp-import.schema.json` equal `IMPORT_TARGETS`
  (IL-R7).

**Layers.** `gnd.export.ilp_learners` goes in the `export` lane, with no
`gnd_entrypoints.json` change.

### Type-confused join check (`ilp_rewrite.py`, ~40 lines) (p1, D12 (o))

**Placement:** a new check **9b**, after check 9 (`constant-spelling`) and
before check 10 (`invalid-guarded`).

**The rule.** For each variable other than X:
1. Collect its join sites: every (predicate, argument position) it occupies in
   an atom.
2. Map each site to its object type through the neutral form's `predicates[].types`
   and `types[].object_type`.
3. The variable is well-typed if the ancestor closures of every pair of its
   sites' object types intersect. This is the predicate that
   `semantic:op-term-type-compat` uses (`model/_validation.py`
   `_ancestor_closure`).
4. Otherwise the clause refuses with exit 3,
   `type-confused-join: clause K: variable V joins <type A> and <type B>`.

**Comparison operands** are already typed by check 5 and are not re-checked.

**The closure** is `{t} | ModelIndex.supertype_closure(t)`. The existing
`supertype_closure` excludes `t` itself, which is why `t` is added. It is the
same transitive `subtype_of` walk as `_ancestor_closure`, read through the
shared ModelIndex snapshot (AGENTS.md) rather than copied (IL1-D7). If this
adds an RF6 query site, it is entered in the RF6 census in this phase.

**Consequence:**
- every target gets the check, including `neutral` (the shipped gap);
- admission stays all-or-nothing, so one confused clause refuses the import
  (IL-R11).

### Octal escapes (`ilp_popper._TOKEN` and `_unquote`, ~15 lines) (p1)

**The tokenizer.** The quoted-atom alternative gains `\\[0-7]{1,7}\\`, placed
before the catch-all `\\.`. Today `\\.` consumes the closing `\'` of
`'\001\'`, and the token fails before `_unquote` runs.

**`_unquote`** reads the same form. It applies the hex form's scalar check:
- `> 0x10FFFF` refuses as beyond Unicode;
- `0xD800–0xDFFF` refuses as a surrogate.

The message is `unparsable: line L, column C: an octal escape …` in each case.

**Other control escapes.** SWI may also write `\a \b \f \v \r` and others. The
pinned SWI version's `writeq` output for code points 0–31, 127 and one
supplementary character is recorded at the gate. Every form it uses gets a
case in T4, and every form it uses that `_ESCAPES` lacks is added.

**Deliberate strictness.** An unclosed octal escape (`'\101'`, which SWI itself
reads) is refused. GND reads only what SWI *writes*.

### Live run (`evidence/IL1/run_popper.py`, evidence only) (p1: rewritten)

**Fixed before the run (IL-R9, IK-R12).**

| Item | Value |
|---|---|
| Input | `src/gnd/examples/refunds/model.orm.yaml` + its `labels.json`, exported with `--target popper`; the export digest E is recorded |
| Popper settings | the rendered `bias.pl` unchanged; Popper's own timeout 540 s, spelled as the pinned version's option (recorded at the gate); all other options at the pinned version's defaults, full argv recorded |
| `ProcessLimits` | `timeout_seconds` 600, `terminate_grace_seconds` 10, `stdin_limit_bytes` 0, `stdout_limit_bytes` 16 MiB, `stderr_limit_bytes` 4 MiB, `total_output_limit_bytes` 20 MiB |
| Environment | explicit `env` with `PATH` limited to the scratch prefix, plus `HOME`, `USER` and `TMPDIR` so they are redacted (IL-R10) |
| Extraction | the program block is the maximal run of lines matching `^wrong\(` … `\.$` after Popper's solution banner; raw stdout is retained separately. More than `CLAUSES_CAP` (1 MiB) means outcome `unparsable` |

**The closed outcome list.** Exactly one outcome is recorded.

| Outcome | Condition |
|---|---|
| `rendering-rejected` | Popper exits non-zero before search, citing the input files |
| `no-solution` | Popper exits 0 and prints no program |
| `learner-timeout` | Popper reports its own timeout |
| `wall-clock-kill` | `run_bounded_process` terminates it |
| `unparsable` | the extracted block is refused by the parser |
| `refused:<name>` | `gnd import ilp-rules` exits 3 with the named refusal |
| `admitted` | `gnd import ilp-rules` exits 0 |

**The run record.**
- `coverage` is computed by SWI (`swipl` loading `bk.pl` plus the program, and
  querying `wrong/1` per example). It is labelled "independent evaluation
  (SWI)".
- Popper's printed scores (tp, fn, tn, fp, precision, recall) are kept verbatim
  and compared with GND's counts in the record.

**Retained** in `evidence/IL1/live/`, with relative paths and `<scratch>`
placeholders:
- `raw-stdout.txt` and `raw-stderr.txt` (after redaction);
- `program.pl`;
- `run.json`;
- `import-report.json`;
- `outcome.json`, which holds:
  - the outcome;
  - E;
  - the tool versions and licences;
  - the argv;
  - the limits;
  - the invocation number;
  - the provenance of each number;
  - "single run, reproducibility not measured".

**Invocations and fixes.**
- Every invocation is numbered and retained. Invocation 1 after the gate is the
  run of record.
- A second run needs an owner ruling and is reported beside the first.
- A rendering or settings fix is an owner-recorded amendment that names the
  changed goldens and the `ADAPTER_VERSION` bump.
- A parser-only fix that changes no golden stays in IL1.

**The record answers three questions:**
1. Does Popper accept the rendering?
2. Does the output parse and import, or which named refusal does it hit?
3. Does every learned clause fit the induction block without loss (the IK2
   residual)?

### Join space (p1)

- **The importer half** is already closed: IK5 case I2 imports a two-fact-type
  join.
- **The stand-in learner** (`stand_in_learner.py:70–78`) proposes a join only
  when every argument type of Q occurs among P's.
- **T11** adds a synthetic fixture model under `tests/fixtures/ilp_learners/il1/`
  with two fact types over the same object types. The stand-in learner must
  yield at least one join candidate there, and that candidate must import with
  exit 0.
- **If no such fixture exists** within the stand-in learner's rule, the row
  stays carried with that reason.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IL1-D1 | Approval instrument | **Corpus-first:** the T4 escape cases, T5 join cases and the T9 replay format are written first. **Prose:** this spec's tables | corpus for T4 and T5; prose otherwise |
| IL1-D2 | `ilp_service.LEARNER` | **Remove:** it has no outside user and is not exported. **Alias:** a shim row for an unseen importer | remove |
| IL1-D3 | Installs and downloads | Named here at the gate, each with its upstream URL, filename, size and SHA-256. Proposed shape: a scratch `uv venv` with `popper-ilp` at a pinned version; SWI-Prolog and clingo as prebuilt archives or conda-forge packages in the same scratch prefix. No system package manager and no `sudo` (D2 (o)) | **open (owner, at the gate)** |
| IL1-D4 | Live-run limits | the §6 table, fixed before the run | as stated |
| IL1-D5 | Base and branch | `claude/il1-learner-registry` from B = main at the gate | named at the gate |
| IL1-D6 (p1) | Where the join check goes in the order | **9b (after constant-spelling):** no existing refusal changes name. **After check 4:** earlier refusal, but corpus cases may change refusal name | 9b |
| IL1-D7 (p1) | How the rewriter gets type closures | **`ModelIndex.supertype_closure` plus the type itself:** the shared query path AGENTS.md prefers; may add one RF6 query site. **A public alias of `_validation._ancestor_closure`:** the validator's own function, but a new public name in `gnd.model` | ModelIndex |
| IL1-D8 (p1) | Licences | Recorded from upstream before download. Expected permissive (Popper MIT; SWI-Prolog BSD-2; clingo MIT), to be confirmed; anything else stops (IL-R5) | open (recorded at the gate) |

## 8. Tests

| ID | File | Case | Expected |
|---|---|---|---|
| T1 | `tests/test_ilp_bridge.py` (existing) | the whole IK5 corpus | unchanged pass, except cases listed as C2-refused (then updated, with each listed in the record) |
| T1b | `tests/test_ik6_walk.py`, `tests/test_rf1_cli_pins.py` (existing) | IK6 walk; `export ilp`/`import ilp-rules` help and exit goldens (order `popper, neutral`) | byte-identical |
| T2 | `tests/test_ilp_learners.py` (new) | parser introspection: export and import `choices` equal `EXPORT_TARGETS`/`IMPORT_TARGETS`, both `("popper", "neutral")`; both schema `target` enums equal `IMPORT_TARGETS` | pass; fails if any drifts |
| T3 | same | a monkeypatched fake entry `fake` (render writes one file; `learner="fake"`) reaches the export tree, the `method` token `ilp-fake` and the `learner-mismatch` text; `ilp_service` source has no `"popper"` literal | pass |
| T3b | same | `--target bogus` on export and import | exit 64 |
| T4 | same (corpus `tests/fixtures/ilp_learners/il1/escapes.json`) | accepted: `'\001\'`, `'\101\'`, `'\7\'`, `'\4177777\'` (U+10FFFF); token boundary `wrong(A):- f(A,B,'\001\'),g(A,B,'x').` → two constants; `wrong(A):- f(A,B,'a\1\'),g(A,B,'b').` → constants `a` + U+0001 and `b` (the octal reading wins over the escaped-quote reading); each further SWI form recorded at the gate | parse |
| T4b | same | refused, each with the octal-specific message and line/column: `'\12345670\'` (8 digits), `'\101'` (unclosed: deliberate strictness), `'\4200000\'` (0x110000, beyond Unicode), `'\154000\'` (0xD800, surrogate) | exit 3 |
| T5 | same (corpus `il1/joins/`) | `neutral` and `popper` clauses joining a refund id with an amount through one variable | exit 3 `type-confused-join`, nothing written |
| T5b | same | a compatible join (same object type; a subtype with its supertype) | exit 0, proposal as before |
| T5c | same | a 32-clause, 16-literal clause file | the work counter stays within the IK5 ceiling |
| T5d | same | a neutral run record naming `popper` | exit 3 `learner-mismatch` |
| T6 | `tests/test_ilp_live.py` (new, `live`) | the live run | evidence only |
| T7 | `tests/test_ilp_learners.py` | `pyproject.toml` dependencies and optional groups, and `importlib.metadata.requires("gnd")`, name no learner (`popper`, `ilasp`, `fastlas`, `clingo`, `swipl`, `amie`, `imodels`, `corels`) | pass |
| T8 | `tests/test_ilp_learners.py` | every tracked file under `.gnd-planning/milestones/ilp-learners/` has no absolute home-directory path (the macOS and Linux home roots, as patterns assembled in the test so this spec does not match itself) and no local username, and no `joined_hits` match against `DOWNSTREAM_JOINED` (imported from the IK close test's helper, moved to `tests/support/` if needed); a planted negative control is caught | pass |
| T9 | `tests/test_ilp_learners.py` (default gate) | replay: read `evidence/IL1/live/outcome.json` (capped, RF7 JSON); recompute E from the model and labels; if a program exists, re-run `gnd import ilp-rules --target popper` over `program.pl` and `run.json` and assert the recorded exit and report SHA-256; otherwise assert the outcome is one of the closed list; assert every required field is present | pass; fails if the record and the bytes disagree |
| T11 | same | stand-in learner over the IL1 join fixture | at least one join candidate, which imports with exit 0, or the row carried with its reason |

**Gate command (literal):**

```
uv run pytest -q -p no:randomly tests/test_ilp_bridge.py tests/test_ilp_learners.py tests/test_ik6_walk.py tests/test_ik_close.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_public_built_inventory.py tests/test_schema_sync.py
```

The expected exit is 0. `tests/test_ik_close.py` is included because it imports
`parse_program` and patches `ilp_service._load_candidate`.

## 9. Out of scope for this phase

- every adapter other than Popper and `neutral`;
- a GND command that runs a learner (plan D3);
- reference-bearing exports (plan D7);
- any wire-format version change; enum widening starts in IL2;
- a rendering or settings change, unless the live run leads to an
  owner-recorded amendment (IL-R9).

## 10. Size

Estimate (p1):
- ~130 source lines: registry, join check, escapes and learner check;
- ~350 test lines, plus the escape and join corpus;
- one evidence script of ~200 lines.

## 11. Approval instrument

Corpus-first for T4 and T5: escape cases and join clauses, with expected exits
written before the code. Prose otherwise (IL1-D1).
