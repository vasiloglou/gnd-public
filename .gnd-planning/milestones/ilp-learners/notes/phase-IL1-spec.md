# IL1 — Learner registry, join check and a real Popper run

## 1. Status

**Draft r3 (p2), awaiting plan approval and then this phase's owner gate.**
- **Nothing exists yet.** Nothing is implemented, installed or run.
- **Before any install,** IL1-D3 (the install commands and downloads) and
  IL1-D8 (the licences) must be ruled.

## 2. Provenance

- **Plan:** [ilp-learners-plan.md](ilp-learners-plan.md) r3, §0, §2 "The
  learner registry" and "The type-confused join check", and §4 IL1.
  - **The plan's review:** r1 was reviewed in round 1
    ([disposition](plan-review-r1-disposition.md)), and r2 in the
    confirmation round ([disposition](plan-review-r2-disposition.md)) (p2).
  - **The owner's rulings,** 2026-10-27 (o): D2, D8–D12, and D13 (p2), in plan
    §10.
- **This spec:**
  - r1 (SHA-256 `59629173…b027`) was read in round 1.
  - r2 (SHA-256 `4a06f583…f5af8`) was read in round 2: four
    approve-with-fixes (p2).
  - **r3 applies the round-2 disposition's themes A–F and I, and D13, at the
    owner's direction (o): "Apply themes A–I as r3 with no further review
    round, D13 yes." r3 bytes carry no review opinion (p2).**
- **Change tags:** `(p1)` marks r2 changes, `(p2)` marks r3 changes, and `(o)`
  marks owner words.
- **Inherited:**
  - the IK5 spec (`../../induced-knowledge/notes/phase-IK5-spec.md`) §6,
    IK5-D9, IK5-D12 and IK5-D13;
  - records `../../induced-knowledge/007-phase-IK5.md` and `010-phase-IK6.md`
    (164–166);
  - the close record `../../induced-knowledge/012-milestone-close.md`: rows
    IK5-Q5, IK5-Q2 and "IK6 join space".
- **Source inspected at `63f7f1f`:**
  - `src/gnd/export/ilp_service.py`: `LEARNER`, `_prepare`, `_read_clauses`,
    `_cmd_import_ilp_rules`, and the report and proposal emission
    (`:416–462`) (p2);
  - `src/gnd/export/ilp_popper.py`: `_TOKEN`, `_unquote`, `parse_program`;
  - `src/gnd/export/ilp_rewrite.py`: `rewrite` (`:62–64`), `_vars` and
    `_anonymous` (`:55–61`), checks 1–10 (p2);
  - `src/gnd/export/ilp.py`: `schema`, `export_tree`;
  - `src/gnd/commands/export.py:106–108` and `src/gnd/commands/checking.py:452`;
  - the `target` enums in `src/gnd/ilp.schema.json:254–258` and
    `src/gnd/ilp-import.schema.json:30–34`;
  - `src/gnd/model_index.py:264–274` (`supertype_closure`) and
    `src/gnd/model/_validation.py` (`_ancestor_closure`,
    `semantic:op-term-type-compat`);
  - `src/gnd/process.py`: `ProcessLimits` (`:34–44`) and `_sensitive_values`
    (`:277–285`) (p2);
  - `src/gnd/examples/refunds/stand_in_learner.py`;
  - `tests/test_ilp_bridge.py`: the T10 source-order pins, the four-argument
    `rewrite` helper (`:552–554`), and the determinism test (`:433–443`) (p2);
  - `tests/test_ik_close.py`: `joined_hits` and `DOWNSTREAM_JOINED`.

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| IL1-C1: registry in declaration order, no learner-name branch, fake entry reaches render/method/learner check, export choices and `ilp.schema.json` equal `EXPORT_TARGETS`, import choices and `ilp-import.schema.json` equal `IMPORT_TARGETS` (p2), goldens byte-identical except listed C2 cases | plan §4 | §6 registry; T1, T1b, T2, T3 |
| IL1-C2: `type-confused-join` for every target, including comparison types (D13 (o)) (p2); compatible joins and `_` unchanged (p2); neutral record naming a registered learner refuses | plan §4; D12 (o), D13 (o) | §6 join check, neutral binding; T5, T5b, T5d, T5e |
| IL1-C3: tokenizer and `_unquote`; every escape form the pinned SWI writes; boundary, digit-count (p2) and token-boundary cases | plan §4; IK5-Q2 | §6 escapes; T4, T4b |
| IL1-C4: one live run under IL-R9; one `termination` and one `import` value (p2); retained artefacts; default-gate replay with shared extractor and fixed arguments (p2) | plan §4; IK5-Q5; D2 (o) | §6 live run; T6 (live), T9 |
| IL1-C5: a stand-in learner join candidate, or the row stays carried with its reason | plan §4; 010:164–166 | §6 join space; T11 |
| IK2 residual: does real learner output fit the induction block without loss | IK2 spec §15 via IK5 spec §3 | live-run record question 3 |
| IL-R1 to IL-R11 and IK-R1 to IK-R12 | plan §0 | §4 |
| IK5-D12 (o): no GND command runs a learner | IK5 spec §7 | kept (plan D3 proposed (a)) |
| IK5-D9 (o), D10 (o): all-or-nothing | IK5 spec §7; plan §10 | unchanged; a C2 refusal refuses the whole import |

## 4. Rules bound to IL1 (every plan §0 rule by name)

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | **Changed loaders:** the Popper tokenizer (`_TOKEN`) and the quoted-atom reader (`_unquote`). Every octal form outside the grammar exits 3 with line and column and an octal-specific message, never a traceback (T4b). **Two new readers,** each capped before it reads and total: the replay test's reader of the live record (JSON through the RF7 policy) and the shared program-block extractor (p2: one function, used by both the script and T9). |
| 2 Algorithm bound | **The join check** is linear in literals × join sites per clause, and K ≤ 32 (IK5-D14); its work joins the import's existing work counter (T5c). **The closure map** is built once per import, linear in object types × subtype depth (p2). **`_unquote`** stays linear in the token. |
| 3 Validation order | **The join check** runs after check 9 and before check 10, so no existing refusal changes name. The `test_ilp_bridge.py` T10 token order is unchanged. **The neutral learner check** sits at the existing `learner-mismatch` site. |
| 4 One walk | **One registry** serves export, clause reading, the learner binding and the CLI and enum equality tests. **One join-check function** serves every labelled target and IL4's Horn-rule mapping (p2). |
| 5 One home | `docs/reference/ilp-bridge.md` stays the normative home. The fragment table gains the `type-confused-join` row there only. |
| 6 Measurement | **C1** is decided by golden bytes. **C4** is decided by a replay test over committed bytes, with fixed arguments and the shared extractor, so the live run is a claim that can fail (T9) (p2). |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1 | T7 checks `pyproject.toml` and the `Requires-Dist` of a wheel built into a temporary directory (p2). |
| IL-R2 | **The script** is `evidence/IL1/run_popper.py`, under `run_bounded_process`. **The test** is `tests/test_ilp_live.py`, marked `live`. **Installs** use a scratch prefix and approved downloads only (IL1-D3). |
| IL-R3 | The join check is one function in `ilp_rewrite`; no adapter has its own. |
| IL-R4 | The run record's coverage comes from SWI evaluating `bk.pl` plus the extracted program. Popper's printed scores are kept verbatim and compared in the record. The script never calls GND to make the record. |
| IL-R5 | Popper's, SWI-Prolog's and clingo's licences are recorded from upstream URLs before download (IL1-D8). |
| IL-R6 | Popper's stdout is untrusted. Only the extracted block reaches the capped parser (1 MiB, `CLAUSES_CAP`). |
| IL-R7 | IK5 wires are unchanged. No enum widens in IL1. T2 pins `ilp.schema.json` to `EXPORT_TARGETS` and `ilp-import.schema.json` to `IMPORT_TARGETS` (p2). |
| IL-R8 | The input is the IK6 refunds example only, with its export digest recorded. |
| IL-R9 | §6 "Live run" fixes the two outcome fields, the extractor, settings, limits, fixed import arguments and the amendment path (p2). |
| IL-R10 | **The script** passes `HOME`, `USER` and `TMPDIR` into the bounded environment, and substitutes `<scratch>` and `<home>` itself in every file it writes, because `run_bounded_process` redacts only values of 4 or more bytes and only the child's output (p2). **T8** is the backstop. |
| IL-R11 | A `type-confused-join` refusal refuses the whole import. |

**Inherited rules (IK-R).**

| Rule | Binding |
|---|---|
| IK-R1 | Admission is unchanged: `_envelope` writes `induced`/`proposed`/`deontic`, and `_enforce_d12` gates it. IL1 adds refusals, never admissions. |
| IK-R2 | Unchanged. GND computes coverage and support; the live record's sets are compared. |
| IK-R3 | Goldens are byte-identical, except IK5 corpus cases that the join check newly refuses. Those are listed in the record as an intended change under D12 (o) and D13 (o). |
| IK-R4 | No ORM schema change. |
| IK-R5 | No new rendered free text. |
| IK-R6 | No new population reads. The join check reads the in-memory neutral form and the closure map. |
| IK-R7 | `gnd.export.ilp_learners` is in the `export` lane. No new command edge (literal `choices=`). The allowance count stays 0. The closure map is read through ModelIndex in `_prepare`; any new RF6 query site is entered in the census, within the ceiling. |
| IK-R8 | Popper runs only from the evidence script, bounded. |
| IK-R9 | This table and the standing-rules table. |
| IK-R10 | T8. |
| IK-R11 | Live provenance is written by the unchanged import and carries opaque ids. |
| IK-R12 | The live-run limits, settings and fixed arguments below are fixed before the run. |

## 5. Goal

**Export and import, through one registry.** On every IK5 and IK6 fixture,
`gnd export ilp --target {popper,neutral}` and `gnd import ilp-rules --target
{popper,neutral}` exit and write exactly as at `63f7f1f`. The only exceptions
are clauses that newly exit 3 `type-confused-join`, which are listed.

**The parser.** It reads SWI octal escapes.

**The live run.** One real Popper run over the IK6 refunds export records one
`termination` value and one `import` value (p2). A default-gate test replays
its committed bytes and gets the recorded result.

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
EXPORT_TARGETS: tuple[str, ...]      # exports=True, in declaration order                         -> ("popper", "neutral")
IMPORT_TARGETS: tuple[str, ...]      # contract == "labelled-clauses", in declaration order (p2)  -> ("popper", "neutral")
def learner(target: str) -> Learner  # KeyError is an internal error (argparse already refused)
```

**`IMPORT_TARGETS` (p2)** is exactly the set that `gnd import ilp-rules`
accepts. Later entries are:
- `llm`: `exports=False`, so it is in `IMPORT_TARGETS` only;
- `amie`: `contract="unlabelled-horn"`, so it is in `EXPORT_TARGETS` only, and
  imported by `gnd import mined-rules`.

**The two entries.**
- `popper`: `learner="popper"`, `exports=True`, `render=ilp_popper.render`,
  `parse=ilp_popper.parse_program`.
- `neutral`: `learner=None`, `exports=True`, `render=None`, `parse=None`.

**Changes in `ilp_service`.**
- `LEARNER` is removed. It has no user outside the module and is not in
  `__all__` (IL1-D2).
- `_prepare` calls `learner(target).render` and builds the closure map (below)
  (p2).
- `_read_clauses` calls `learner(target).parse`, or otherwise reads JSON.
- `method` comes from the entry.
- **The learner check:**
  - For an entry with `learner` set, `learner.name` must equal it.
  - For `neutral`, `learner.name` must not equal any entry's `learner`.
  - Either failure is exit 3 `learner-mismatch`, at the existing site.
- **The tokens pinned by `test_ilp_bridge.py` T10 stay:** `_read_clauses(`,
  `_prepare(` and `learner-mismatch`, in their pinned order.

**The CLI.**
- `commands/export.py` and `commands/checking.py` keep their literal
  `choices=("popper", "neutral")`. Importing the registry at
  parser-construction time would add an entry-point edge that RF5 rejects,
  and would load `jsonschema` on every `gnd` call.
- **T2** asserts, by parser introspection:
  - the `export ilp` choices and the `ilp.schema.json` `target` enum equal
    `EXPORT_TARGETS`;
  - the `import ilp-rules` choices and the `ilp-import.schema.json` `target`
    enum equal `IMPORT_TARGETS` (p2).

**Layers.** `gnd.export.ilp_learners` goes in the `export` lane, with no
`gnd_entrypoints.json` change.

### Type-confused join check (`ilp_rewrite.py`, ~60 lines) (D12 (o), D13 (o))

**One shared function (p2):**

```python
def check_join_types(
    atoms: list[dict[str, Any]], compares: list[tuple[dict[str, Any], str | None]],
    index: int, neutral: dict[str, Any], *, closures: Mapping[str, frozenset[str]],
) -> None   # raises the type-confused-join refusal
```

**Who calls it (p2).**
- **`rewrite`** gains a keyword-only `closures: Mapping[str, frozenset[str]] |
  None = None` and calls the function as check **9b**, after check 9
  (`constant-spelling`) and before check 10 (`invalid-guarded`).
- **When `closures` is `None`,** 9b is skipped. The existing four-argument
  callers (`tests/test_ilp_bridge.py:552–554`) keep working, but the import
  always passes the map.
- **IL4's Horn-rule mapping** calls the same function.

**The closure map (p2).**
- **What it holds:** `{object type: {t} | ModelIndex.supertype_closure(t)}`.
- **Where it is built:** once, in `_prepare`, where the model is loaded.
- **Where it travels:** on `_Prepared`, never on the `gnd-ilp/1` wire
  (IL-R7). The neutral form's `types[]` carry `object_type` but not
  `subtype_of`, so the wire could not supply it anyway.
- **Why `{t} |`:** `supertype_closure` excludes `t`, so adding it gives
  exactly `_ancestor_closure`.

**The rule.** For each named variable other than X (p2: **`_` is excluded**,
because each `_` occurrence is its own fresh variable, as `_vars` and
`_anonymous` already treat it):
1. Collect its join sites.
   - **Atom positions:** every (predicate, argument position) it occupies in
     an atom, mapped to an object type through the neutral form's
     `predicates[].types` and `types[].object_type`.
   - **Comparisons (p2, D13 (o)):** if it is an operand of a comparison
     predicate with a declared type (for example `gt_t_amount`), that type's
     object type.
2. The variable is well-typed if the closures of every pair of its sites'
   object types intersect. This is the predicate that
   `semantic:op-term-type-compat` uses.
3. Otherwise the clause refuses with exit 3,
   `type-confused-join: clause K: variable V joins <type A> and <type B>`.

**Consequence:**
- every target gets the check, including `neutral` (the shipped gap);
- admission stays all-or-nothing, so one confused clause refuses the import
  (IL-R11).

### Octal escapes (`ilp_popper._TOKEN` and `_unquote`, ~20 lines)

**The tokenizer (p2).**
- **The alternative:** the quoted-atom alternative gains `\\[0-7]+\\`, placed
  before the catch-all `\\.`. Today `\\.` consumes the closing `\'` of
  `'\001\'`, and the token fails before `_unquote` runs.
- **Any digit count:** the alternative takes any number of digits, so an
  over-long escape still forms a token and reaches `_unquote`, where it gets
  the octal message.

**`_unquote`** reads the same form. It refuses, each with
`unparsable: line L, column C: an octal escape …`:
- more than 7 digits (p2);
- a value `> 0x10FFFF` (beyond Unicode);
- a value in `0xD800–0xDFFF` (a surrogate).

**Other control escapes.** SWI may also write `\a \b \f \v \r` and others. The
pinned SWI version's `writeq` output for code points 0–31, 127 and one
supplementary character is recorded at the gate. Every form it uses gets a
case in T4, and every form it uses that `_ESCAPES` lacks is added.

**Deliberate strictness.** An unclosed octal escape (`'\101'`, which SWI itself
reads) is refused. GND reads only what SWI *writes*.

### Live run (`evidence/IL1/run_popper.py`, evidence only)

**Fixed before the run (IL-R9, IK-R12).**

| Item | Value |
|---|---|
| Input | `src/gnd/examples/refunds/model.orm.yaml` + its `labels.json`, exported with `--target popper`; the export digest E is recorded |
| Popper settings | the rendered `bias.pl` unchanged; Popper's own timeout 540 s, spelled as the pinned version's option (recorded at the gate); all other options at the pinned version's defaults, full argv recorded |
| `ProcessLimits` | `timeout_seconds` 600, `terminate_grace_seconds` 10, `stdin_limit_bytes` 0, `stdout_limit_bytes` 16 MiB, `stderr_limit_bytes` 4 MiB, `total_output_limit_bytes` 20 MiB |
| Environment | explicit `env` with `PATH` limited to the scratch prefix, plus `HOME`, `USER` and `TMPDIR`; the script also substitutes `<scratch>` and `<home>` itself in every file it writes (IL-R10) (p2) |
| Extraction (p2) | `extract_program(stdout: str) -> str`, in `gnd.export.ilp_popper`, shared by the script and T9. Its banner string is recorded from the pinned Popper version at the gate. The program is **the first maximal run of lines matching `^wrong\(.*\.$` after the last banner**; with no banner or no such line it returns `""`. Raw stdout is retained separately |
| Import arguments (p2) | `--target popper --format json --requested-at 2026-01-01T00:00:00Z --actor ilp-live`, with relative paths `program.pl`, `run.json`, `model.orm.yaml`, `labels.json` and `--out proposal.json` from a fixed working directory |

**The outcome: two fields (p2).** Exactly one value of each is recorded.

| Field | Value | Condition |
|---|---|---|
| `termination` | `rendering-rejected` | Popper exits non-zero before search, citing the input files |
| | `completed` | Popper exits 0 |
| | `learner-timeout` | Popper reports its own timeout (a best-so-far program may still be printed) |
| | `wall-clock-kill` | `run_bounded_process` terminates it at the timeout |
| | `output-limit` | `run_bounded_process` terminates it at an output limit |
| `import` | `none` | `extract_program` returns `""` |
| | `refused:<name>` | `gnd import ilp-rules` exits 3; the name is the importer's own, including `refused:unparsable` and the clauses-cap refusal |
| | `admitted` | `gnd import ilp-rules` exits 0 |

**The run record.**
- `coverage` is computed by SWI (`swipl` loading `bk.pl` plus the program, and
  querying `wrong/1` per example). It is labelled "independent evaluation
  (SWI)".
- Popper's printed scores (tp, fn, tn, fp, precision, recall) are kept verbatim
  and compared with GND's counts in the record.

**Retained** in `evidence/IL1/live/`, with relative paths and `<scratch>`,
`<home>` placeholders:
- `raw-stdout.txt` and `raw-stderr.txt` (after redaction and substitution);
- `program.pl` (empty if `import: none`);
- `run.json`;
- **the import result (p2):**
  - `import-report.json` and `proposal.json` if the import exited 0;
  - `import-stderr.txt` (the refusal line) if it exited 3;
  - nothing if `import: none`;
- `outcome.json`, which holds:
  - `termination` and `import`;
  - E;
  - the tool versions and licences;
  - the argv;
  - the limits;
  - the fixed import arguments;
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

### Join space

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
| IL1-D6 | Where the join check goes in the order | **9b (after constant-spelling):** no existing refusal changes name. **After check 4:** earlier refusal, but corpus cases may change refusal name | 9b |
| IL1-D7 | How the join check gets type closures | **A closure map from `ModelIndex.supertype_closure` plus the type itself, built in `_prepare`, passed keyword-only (p2):** the shared query path AGENTS.md prefers; may add one RF6 query site. **A public alias of `_validation._ancestor_closure`:** the validator's own function, but a new public name in `gnd.model` | ModelIndex closure map |
| IL1-D8 | Licences | Recorded from upstream before download. Expected permissive (Popper MIT; SWI-Prolog BSD-2; clingo MIT), to be confirmed; anything else stops (IL-R5) | open (recorded at the gate) |

## 8. Tests

| ID | File | Case | Expected |
|---|---|---|---|
| T1 | `tests/test_ilp_bridge.py` (existing) | the whole IK5 corpus | unchanged pass, except cases listed as C2-refused (then updated, with each listed in the record) |
| T1b | `tests/test_ik6_walk.py`, `tests/test_rf1_cli_pins.py` (existing) | IK6 walk; `export ilp`/`import ilp-rules` help and exit goldens (order `popper, neutral`) | byte-identical |
| T2 | `tests/test_ilp_learners.py` (new) | parser introspection: `export ilp` choices and the `ilp.schema.json` enum equal `EXPORT_TARGETS`; `import ilp-rules` choices and the `ilp-import.schema.json` enum equal `IMPORT_TARGETS`; both are `("popper", "neutral")` today (p2) | pass; fails if any drifts |
| T3 | same | a monkeypatched fake entry `fake` (render writes one file; `learner="fake"`) reaches the export tree, the `method` token `ilp-fake` and the `learner-mismatch` text; `ilp_service` source has no `"popper"` literal | pass |
| T3b | same | `--target bogus` on export and import | exit 64 |
| T4 | same (corpus `tests/fixtures/ilp_learners/il1/escapes.json`) | accepted: `'\001\'`, `'\101\'`, `'\7\'`, `'\4177777\'` (U+10FFFF); token boundary `wrong(A):- f(A,B,'\001\'),g(A,B,'x').` → two constants; `wrong(A):- f(A,B,'a\1\'),g(A,B,'b').` → constants `a` + U+0001 and `b` (the octal reading wins over the escaped-quote reading); each further SWI form recorded at the gate | parse |
| T4b | same | refused, each with the octal-specific message and line/column: `'\12345670\'` (8 digits) alone, and `wrong(A):- f(A,B,'\12345670\'),g(A,B,'x').` (8 digits followed by another quote) (p2); `'\101'` (unclosed: deliberate strictness); `'\4200000\'` (0x110000, beyond Unicode); `'\154000\'` (0xD800, surrogate) | exit 3 |
| T5 | same (corpus `il1/joins/`) | `neutral` and `popper` clauses joining a refund id with an amount through one variable | exit 3 `type-confused-join`, nothing written |
| T5b | same | a compatible join (same object type; a subtype with its supertype); a clause with `_` at two incompatible object types (p2) | exit 0, proposal as before |
| T5c | same | a 32-clause, 16-literal clause file | the work counter stays within the IK5 ceiling |
| T5d | same | a neutral run record naming `popper` | exit 3 `learner-mismatch` |
| T5e (p2) | same | a comparison whose declared type (`gt_t_<other>`) is a different integer value type from its operand's role type, in a fixture model with two integer value types | exit 3 `type-confused-join` (D13 (o)) |
| T5f (p2) | same | `rewrite` called with four positional arguments (no `closures`) on a type-confused clause | returns as at `63f7f1f` (9b skipped); the import path always passes `closures` |
| T6 | `tests/test_ilp_live.py` (new, `live`) | the live run | evidence only |
| T7 | `tests/test_ilp_learners.py` | `pyproject.toml` dependencies and optional groups, and the `Requires-Dist` lines of a wheel built with `uv build --wheel` into a temporary directory (p2), name no learner (`popper`, `ilasp`, `fastlas`, `clingo`, `swipl`, `amie`, `imodels`, `corels`) | pass |
| T8 | `tests/test_ilp_learners.py` | every tracked file under `.gnd-planning/milestones/ilp-learners/` has no absolute home-directory path (the macOS and Linux home roots, as patterns assembled in the test so this spec does not match itself); no local username as a whole path component, whatever its length (p2); and no `joined_hits` match against `DOWNSTREAM_JOINED` (imported from the IK close test's helper, moved to `tests/support/` if needed); a planted negative control is caught | pass |
| T9 (p2) | `tests/test_ilp_learners.py` (default gate) | replay. Read `evidence/IL1/live/outcome.json` (capped, RF7 JSON) and assert every required field. Recompute E from the model and labels. Assert `extract_program(raw-stdout.txt)` equals `program.pl` (or `""`). If `import` is not `none`: copy the committed inputs into a temporary directory laid out as recorded, re-run `gnd import ilp-rules` with the recorded fixed arguments from there, and assert the recorded exit. On exit 0, also assert the SHA-256 of the report with every `path` field and `proposal` normalized, and the SHA-256 of `proposal.json`. On exit 3, assert the refusal line equals `import-stderr.txt` | pass; fails if the record and the bytes disagree |
| T11 | same | stand-in learner over the IL1 join fixture | at least one join candidate, which imports with exit 0, or the row carried with its reason |

**Gate command (literal):**

```
uv run pytest -q -p no:randomly tests/test_ilp_bridge.py tests/test_ilp_learners.py tests/test_ik6_walk.py tests/test_ik_close.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_public_built_inventory.py tests/test_schema_sync.py
```

The expected exit is 0. `tests/test_ik_close.py` is included because it imports
`parse_program` and patches `ilp_service._load_candidate`.

## 9. Out of scope for this phase

- every adapter other than Popper and `neutral`;
- IL4's call of the join-check function (IL4 owns that call and its test) (p2);
- a GND command that runs a learner (plan D3);
- reference-bearing exports (plan D7);
- any wire-format version change; enum widening starts in IL2;
- a rendering or settings change, unless the live run leads to an
  owner-recorded amendment (IL-R9).

## 10. Size

Estimate (p2):
- ~160 source lines: registry, join-check function and closure map, escapes,
  extractor and learner check;
- ~420 test lines, plus the escape and join corpus;
- one evidence script of ~200 lines.

## 11. Approval instrument

Corpus-first for T4 and T5: escape cases and join clauses, with expected exits
written before the code. Prose otherwise (IL1-D1).

## 12. Owner gate preparation (2026-10-27, appended after approval)

The owner approved r3 on 2026-10-27 (`001-plan-gate.md`), over the bytes before
this section. The owner then selected the phase (o): "process-phase IL1
ilp-learners". Sections 1–11 are unchanged. This section prepares the three
decisions the approval left open: IL1-D3, IL1-D5 and IL1-D8.

**How these facts were gathered:**
- **Sources:** read-only metadata queries on 2026-10-27, to the PyPI JSON API,
  the GitHub API and the SWI-Prolog download server.
- **Nothing downloaded or installed:** nothing was downloaded beyond metadata,
  and nothing was installed.
- **Machine:** macOS 26.6.2 on arm64. No `swipl`, `clingo`, `popper`, conda or
  micromamba is present. A uv-managed CPython 3.14.3 and the system C compiler
  are present.

### Base commit (IL1-D5)

**`main` has moved** to `077f46e` (the evolve-loading follow-up, PRs #46 and
#47) since the spec's inspection commit `63f7f1f`. `git diff 63f7f1f 077f46e`
touches:
- no ILP source, CLI or schema file;
- no RF1 golden;
- no entry-point file.

**What did change:** `tests/test_ik_close.py` changed one docstring and one
YAML case, unrelated to `parse_program` and `_load_candidate`. `tools/gnd_layers.json` gained
`gnd.model._documents`. Every source citation in §2 still holds at `077f46e`.

### Installs and downloads (IL1-D3)

**Popper v5.0.1 constraints:**
- **Python:** it requires Python ≥ 3.14 and builds a Cython extension.
- **Prolog bridge:** it needs SWI-Prolog through `janus_swi`, which is
  published only as a source distribution and builds against a local
  `swipl`.
- **No Homebrew:** conda-forge has `swi-prolog` for `linux-64` only. Without
  Homebrew (D2 (o)), SWI-Prolog therefore comes from its upstream macOS disk
  image.

**Proposed scratch layout.** `<scratch>` is
`<scratchpad>/il1-live/`, outside the repository. It has no profile or PATH
edits; `PATH` is set per command only.

**1. Download SWI-Prolog 10.0.2.**
- **File:** `swipl-10.0.2-1.fat.dmg` from
  `https://www.swi-prolog.org/download/stable/bin/`.
- **Size and digest:** 34,301,763 bytes; SHA-256
  `bf775f0b8d7880f4908dee513316013ef42a73793be392814fde2a0a8e9ddc5d`, from the
  upstream `.sha256` file. It is verified after download.
- **Into the scratch prefix:**
  - attach the image read-only at a scratch mount point, with no Finder
    window (`hdiutil attach -readonly -nobrowse -mountpoint`);
  - copy `SWI-Prolog.app` into `<scratch>`;
  - detach the image.
- **Nothing goes to `/Applications`.**

**2. Create the Python environment.** `uv venv --python 3.14
<scratch>/venv`, using the uv-managed CPython already present.

**3. Install Popper v5.0.1.**
- **Pinned by commit:**
  `git+https://github.com/logic-and-learning-lab/Popper@578a4e26a22006b9325fe819486242f7fafc3195`.
  That is the commit tag `v5.0.1` points to; the tarball has no published
  digest, so the commit is the integrity anchor.
- **With `--no-deps`:** the dependencies come from step 4 (see the
  `pypblib` row below).

**4. Install the dependencies, hash-pinned.**
- **The lock:** a lock generated with `uv pip compile --generate-hashes` from
  the top-level pins below. The lock is committed as evidence before install,
  and installed with `--require-hashes`.
- **The build:** the two source distributions build with the system C
  compiler, with `PATH` including `<scratch>/SWI-Prolog.app/Contents/MacOS`
  for `janus_swi`.

| Package | Pin | File (macOS arm64, CPython 3.14) | Bytes | SHA-256 |
|---|---|---|---|---|
| clingo | 5.8.2 | `clingo-5.8.2-cp314-cp314-macosx_11_0_arm64.whl` | 1,623,758 | `772569446f6538a3647656fc93b6a8c85d756df3c82100a58340e51fa8d0013c` |
| bitarray | 3.12.3 | `bitarray-3.12.3-cp314-cp314-macosx_11_0_arm64.whl` | 182,582 | `b4901a544afd45993520babe2c2a61f87e4c0d98e5e6100e80eb7fd667fd92ff` |
| python-sat | 1.9.dev17 (the only current release line on PyPI is a pre-release) | `python_sat-1.9.dev17-cp314-cp314-macosx_11_0_arm64.whl` | 2,410,387 | `b220d55d4b5e95993c80b6b9332bcc87127e7dc901abb674145a39540c1c7ead` |
| ortools | 9.15.6755 | `ortools-9.15.6755-cp314-cp314-macosx_11_0_arm64.whl` | 21,923,649 | `1a0677270b0cd317a6b8dae42514264eaf5da5756c5bc7215eeea409424577df` |
| cykhash | 2.0.1 | `cykhash-2.0.1.tar.gz` (sdist; builds locally) | 44,895 | `b4794bc9f549114d8cf1d856d9f64e08ff5f246bf043cf369fdb414e9ceb97f7` |
| janus-swi | 1.5.3 | `janus_swi-1.5.3.tar.gz` (sdist; builds against the scratch SWI) | 90,117 | `2ce9867bb1e0cbab7737c8e2a7af3268f2241251e5b0eb955726c829ae995f8d` |
| Cython (build only) | 3.3.0 | `cython-3.3.0-cp314-cp314-macosx_11_0_arm64.whl` | 3,186,700 | `0deedc2e9a5a664e1adfa4c2d310aa7b54903e1a647c274b6c9213f77a02d637` |
| cffi (clingo) | 2.1.1 | `cffi-2.1.1-cp314-cp314-macosx_11_0_arm64.whl` | 184,962 | `661c298b4821edebead0c91edd2b00374d67ad7c5a1f7a91d4442633b79d6a72` |

`ortools` brings further transitive packages (for example `numpy`,
`protobuf`, `absl-py`). Their exact files and digests appear only in the
committed lock, so approving this row approves that lock as generated.

**The `pypblib` row.**
- **What Popper declares:** Popper v5.0.1 declares `pypblib` as a dependency.
- **Licence:** PyPI shows **no licence** for `pypblib` 0.0.4, and its homepage
  (`arcadia.hardlog.udl.cat`) redirects.
- **No usable build:** it ships no macOS wheel; its only source distribution
  is from 2019.
- **Not used by Popper:** a scan of every `popper/*.py` file at `v5.0.1` finds
  no import of `pblib` or `pypblib`. Popper uses `pysat.card` and
  `pysat.solvers`, which do not need it, and `python-sat` itself makes `pblib`
  an optional extra.
- **Proposed:** install Popper with `--no-deps` and leave `pypblib` out
  (IL1-D9 below).

### Licences (IL1-D8)

Each licence was recorded on 2026-10-27, before any download (IL-R5).

| Component | Licence | Source |
|---|---|---|
| Popper v5.0.1 | MIT | GitHub API, `repos/logic-and-learning-lab/Popper`, `license.spdx_id` |
| SWI-Prolog 10.0.2 | BSD-2-Clause ("Simplified BSD") | `github.com/SWI-Prolog/swipl-devel` `LICENSE`. The app bundle may carry third-party library notices; they are read and recorded at install |
| clingo 5.8.2 | MIT | PyPI metadata; `github.com/potassco/clingo` |
| janus-swi 1.5.3 | BSD-2-Clause | PyPI metadata |
| bitarray 3.12.3 | PSF-2.0 | PyPI metadata |
| python-sat 1.9.dev17 | MIT | PyPI metadata |
| ortools 9.15.6755 | Apache-2.0 | PyPI metadata |
| cykhash 2.0.1 | MIT | PyPI metadata |
| cffi 2.1.1 | MIT-0 | PyPI metadata |
| Cython 3.3.0 (build only) | Apache-2.0 | PyPI metadata |
| pypblib 0.0.4 | **none declared** | PyPI metadata; homepage redirects |

**Assessment.**
- **Permissive:** every component except `pypblib` carries a permissive OSI
  licence.
- **No click-through:** no component needs registration or a click-through.
- **`pypblib`:** under IL-R5, its missing licence stops for the owner's
  ruling.
- **Not committed:** no binary or source of any component is committed.

### New decision surfaced at the gate

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IL1-D9 | `pypblib`, which Popper declares but never imports, and which has no declared licence | **(a) Leave it out:** install Popper with `--no-deps` plus the step 4 lock. The record says so. If a Popper code path needs it at run time, that is `termination: rendering-rejected` or a crash, recorded under IL-R9. **(b) Install it:** the owner accepts the unknown licence, and the 2019 sdist must build on Python 3.14, which is untested | (a) |

### Instrument and panel

- **IL1-D1** (corpus-first for T4 and T5) was approved with r3.
- **No review panel** over the spec bytes is proposed. The plan review already
  read r1 and r2, and the process-phase default omits a phase-spec panel.

## 13. Owner gate record (2026-10-27)

The owner answered the gate questions in the session on 2026-10-27 (o).

| ID | Question as asked | Owner's answer | Ruling |
|---|---|---|---|
| IL1-D3, IL1-D8 | "approve the scratch installs and downloads in spec §12 (SWI-Prolog 10.0.2 disk image, Popper v5.0.1 at commit 578a4e26, and the hash-pinned Python lock), with the licences as recorded?" | "Approve as listed" | **The installs and downloads in §12 are approved, in a scratch prefix only.** The lock generated at install is covered as generated, and is committed before install. **The §12 licences are accepted** for the components installed. |
| IL1-D9 | "Popper declares pypblib but never imports it, and pypblib has no declared licence. How should it be handled?" | "Leave it out" | **(a):** Popper is installed with `--no-deps` plus the lock, and `pypblib` is not installed. The live record states this. |
| IL1-D5 | "where should IL1's implementation branch start?" | "After PR #48 merges" | **The IL1 branch is `claude/il1-learner-registry`,** created from `main` after PR #48 merges. Its base commit B is the resulting `main` head, recorded in the IL1 record. |

**Panel:** none over the spec bytes (§12, proposed and not contested).

**What this record leaves unchanged:**
- **The approved r3 sections:** this section and §12 are appended after
  approval and change no approved sentence.
- **Order:** implementation begins only after PR #48 merges, on the new
  branch. No install happens before the evidence-script step of §6.

## 14. Implementation findings (recorded as found)

**Base commit B = `45c8603`** (the merge of PR #48), on branch
`claude/il1-learner-registry` (IL1-D5 (o)).

**IL1-F1 (2026-10-27): the neutral learner rule refutes the byte-identity
premise.** Found while reading the IK5 corpus before writing the T5 cases.
- **The spec's claim:** IL1-C2 and §6 "The learner check" refuse a
  `--target neutral` run record whose `learner.name` is a registered learner's
  (round 1, R1-F7). §5 and IK-R3 then claim every IK5 golden is unchanged
  except type-confused clauses.
- **What the corpus holds:** the approved IK5 corpus imports 13 cases through
  `--target neutral`: I1, I4, B1, B2, B4, B5, F03, F05, F07 and M1–M4. 30 of
  its 31 run records name `popper`.
- **The consequence:** the rule would turn I1, the corpus's main admitted case,
  from exit 0 into exit 3 `learner-mismatch`, along with every other
  neutral import that reaches the learner check.
- **The cost:** that changes approved expected answers of a closed milestone,
  which returns them to the owner gate.
- **Readings:**
  - **(a) Leave the neutral learner check out of IL1.** `neutral` keeps IK5's
    behaviour (any learner name). The `method` token, `ilp-neutral`, already
    tells a neutral import apart. The case R1-F7 cared about, an LLM's
    proposal, gets its own `llm` entry and learner check in IL5 (plan §2), so
    an LLM import is never `ilp-neutral`. **Residual:** a neutral run record
    can still name `popper` as its inducer. That stays as IK5 shipped it, and
    is recorded as an accepted residual.
  - **(b) Keep the rule and rename the learner in the 13 corpus run records**
    (for example to `authored`). Each run record's bytes change, so every
    affected proposal's evidence digest and the corpus goldens change too. A
    closed milestone's approved fixtures are rewritten.
- **Proposed:** (a). Until the owner rules, the T5d case is held, and
  nothing else in IL1 depends on it.

**IL1-F1 ruling (o), 2026-10-27.**
- **The question as asked:** "How should IL1 handle it?"
- **The owner's answer:** "Drop it from IL1".
- **What applies:** reading (a). The neutral learner check is left out of IL1,
  T5d is withdrawn, and `neutral`'s learner binding stays as IK5 shipped it.
- **Accepted residual:** a neutral run record may name a registered learner as
  its inducer; `method: ilp-neutral` marks the path.
- **IL5** carries the LLM learner check on its own `llm` entry.

**IL1-F2 (2026-10-27): SWI-Prolog bundles an LGPL component.**
- **What was found:** the approved download verified exactly (34,301,763
  bytes; SHA-256 `bf775f0b…dc5d`). SWI-Prolog's own `license.` report on the
  installed copy says the binary "contains components covered by the GNU
  Lesser Public License": `libgmp`, linked dynamically.
- **Why it stopped:** that is OSI but not permissive, so it stopped under
  IL-R5.
- **Owner ruling (o), 2026-10-27:** "Accept for local use". It is used in the
  scratch folder only; nothing is bundled, committed or redistributed.

**IL1-F3 (2026-10-27): the host's default SDK does not link.**
- **The failure:** building `janus-swi` (and any C extension) failed in the
  linker with `tapi error: malformed file`. The default
  `MacOSX27.0.sdk`'s `libSystem.tbd` names an `arm64e.x1` architecture that
  the installed linker (ld-1267, Command Line Tools 26.6) does not know.
- **The workaround:** the builds ran with `SDKROOT` set, for those commands
  only, to the installed `MacOSX26.5.sdk`.
- **Scope:** there is no system change and no new download; this stays within
  IL1-D3 (o). It is a host fact, not a GND defect.

**IL1-F4 (2026-10-27): Popper logs its solution to stderr.**
- **The premise refuted:** §6's extraction rule assumed stdout.
- **What Popper v5.0.1 does** (`popper/logger.py`, `popper/util.py`
  `print_prog_score`): the solution block goes through a logging handler to
  **stderr**, each line prefixed with elapsed seconds (`12.3s `), as the
  banner, a scores line, the rules, then a closing rule of stars. Only
  `NO SOLUTION` is printed to stdout.
- **The adaptation:** `ilp_popper.extract_program` reads the log text, strips
  the prefix, and takes the first maximal run of `wrong(...).` lines after the
  last `********** SOLUTION **********`.
- **What does not change:** no approved answer or golden.

**IL1-F5 (2026-10-27): Popper's version metadata.**
- **The mismatch:** at commit `578a4e2` (tag `v5.0.1`), Popper's
  `pyproject.toml` still says version `5.0.0`, so the installed metadata
  reports 5.0.0.
- **What the run record says:** the learner version is `5.0.1+578a4e2`, after
  the tag and commit.
- **Other facts:** the package installs no console script, so the run uses
  upstream `popper.py`'s entry code with `-c`. Popper v5.0.1's source has no
  `magic` handling at all, although the IK5 rendering writes
  `magic_value_type(...)`; the run of record settles what that means.

**IL1-F6 (2026-10-27): a near-miss on privacy.**
- **What happened:** the first commit of `requirements.lock` carried ten
  `# via -r <absolute path>` comments with the host home path. The check after
  committing caught it.
- **The fix:** the lines were rewritten to `-r requirements.in`, and the commit
  amended before any push. No copy exists on the remote.
- **The control:** T8 would also have refused it at the gate.

**IL1-F7 (2026-10-27): the run of record.**

Invocation 1 is the run of record: `termination: rendering-rejected`,
`import: none`. Its files are in
`evidence/IL1/live/invocation-1/`.

**What happened:**
- **Load and search:** Popper v5.0.1 loaded the IK5 rendering of the IK6
  refunds export (E as recorded) and began its search.
- **The crash:** after 18.0 s it exited 1 with an uncaught
  `janus_swi.janus.PrologError: </2: Arguments are not sufficiently
  instantiated`. Its tester had called a rendered comparison predicate
  (`lt_t_amount(A,B) :- A < B`) with an unbound argument.
- **Stdout:** it held one line, `ERROR detecting pointless relations >/2: …`.
- **No program:** none was printed, so nothing was imported or evaluated by
  SWI.

**The record's three questions:**
1. **No: Popper v5.0.1 does not accept the IK5 rendering.**
   - **Comparisons need constants:** the rendering expresses comparisons
     against constants through `magic_value_type(t_…)`, and v5.0.1 has no
     magic-value support (IL1-F5).
   - **Nothing binds the constant:** the second argument of every comparison
     is free, and Prolog arithmetic raises on it.
   - **A warning too:** SWI also warns that `bk.pl`'s clauses are not
     contiguous per predicate, because the export orders facts by example
     first. This is a warning only.
2. **No program,** so neither parse nor import was reached.
3. **The IK2 residual is not tested** by this run.

**The closed-list label.**
- **The label:** the script maps any non-zero exit to `rendering-rejected`.
- **Where the definition does not fit:** §6 defines that value as an exit
  "before search, citing the input files". This run exited non-zero
  **during** search.
- **Why it is still the closest member:** the cause is the rendering, and no
  other member of the closed list fits. The deviation is recorded here, not
  hidden.

**The evidence repair.**
- **The leak:** the first sanitization missed scratch paths whose user
  component `run_bounded_process` had already masked as `***`.
- **The fix:** before any commit, the retained files were re-sanitized with
  the script's new `SCRATCH_PATH` rule (only `raw-stderr.txt` changed), and
  the script now applies that rule itself.

**What IL-R9 says next:** a rendering fix is an owner-recorded amendment that
names the changed goldens and the `ADAPTER_VERSION` bump, and a second run
needs an owner ruling.
