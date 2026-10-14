# Phase PL12 spec: the model's rules as two readable PyRel programs

## 1. Status

Owner-directed (2026-10-14): "write two versions, one that will require lqp and
one that can run without LQP". Delegated approval under the milestone's default
approval (`001-plan-gate.md`) and amendment A1's "rules as PyRel requirements"
appendix. Implementable.

## 2. Provenance

- Plan amendment A1, appendices "how all five examples run on PyRel" and "rules
  as PyRel requirements".
- Probes run 2026-10-14 with PyRel 1.30.1 and DuckDB 1.5.5:
  - `require` is ignored on DuckDB under both `require_mode` values.
  - The logic reasoner lowers `where(D).require(C)` to `D ∧ ¬C ⇒ Error`
    (`require_errors.py`).
  - PyRel's front-end compiles each `require` to a `Require` node with `domain`
    and `check`.
  - Recursive `define` and `aggregates.sum(...).per(...)` run locally.
- The local "LQP" connection type is internal-only, so the LQP version cannot be
  executed here.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner | two versions: an LQP program built on `require`, and a program that runs without LQP | §6 `--rules lqp`, `--rules duckdb` |
| Owner (earlier) | rules written as PyRel logic, not fetch-and-check | both programs state every rule as `where(...).require(...)`; DuckDB runs the requirement's denial form |
| A1 standing rule 5 (one home) | both versions come from one requirement object | §6.1; single-source test (§8, row 3) |
| PL-R4 | honest labels | each program's header says which engine enforces the rules and which does not |
| Agreement | the DuckDB version agrees with GND | §8, row 1 |
| LQP verifiability without an engine | each rule compiles to exactly one PyRel `Require` whose domain and check match the requirement object | §8, row 2 |

## 4. Standing rules, bound

1. **Totality.** The generator reads only a model that has already passed
   `load_model`. It refuses an unsupported construct by name (`ExportInputError`).
   The generated programs cap population reads at 1 MiB.
2. **Bounds.** Generation is linear in model size.
3. **Validation order.** Model validation, then the family check, then rendering.
4. **One walk.** One function lowers every constraint family to a `Requirement`.
   Two renderers consume that list.
5. **One home.** The `Requirement` list is the rule's single structured home for
   these programs. The checker runtime (`pyrel_runtime.py`) is unchanged in this
   phase and is tied to it by the agreement test. Making the runtime consume the
   list is an open-questions row targeted at PL13.
6. **Measurement.** The probes are listed in §2.

## 5. Goal

| Command | Expected |
|---|---|
| `gnd export pyrel MODEL --rules duckdb --out rules.py` | exit 0 |
| `"$GND_PYREL_PYTHON" rules.py POPULATION` | one line per rule; witnesses in GND's shape; exit 1 on an alethic violation, 2 on vacuous or unknown, 0 otherwise |
| `gnd export pyrel MODEL --rules lqp --out rules_lqp.py` | exit 0 |
| `"$GND_PYREL_PYTHON" rules_lqp.py --compile` | compiles with PyRel's front-end and prints each `Require` as compiled; exit 0 |
| `rules_lqp.py POPULATION --connection NAME` | runs on a RelationalAI engine with `require_mode="report"`; not executable in this environment |

## 6. Design

### 6.1 `src/gnd/export/pyrel_rules.py` (~400 lines)

- `Atom(relation, args)`: `args` items are a variable name `$x` or a literal.
- `Requirement(id, family, modality, quote, domain: tuple[Atom|Compare], check: Check, witness: tuple[str, ...], vacuous_when: tuple[str, tuple[str, ...]])`.
- `Check` kinds:

| Kind | Requirement form | Denial form |
|---|---|---|
| `holds` | `require(atom)` | `not_(atom)` |
| `absent` | `require(not_(atom))` | `atom` |
| `compare` | `require(left op right)` | `left negated-op right` |
| `same` | `require(a == b)` | `a != b` |

- `requirements(model) -> list[Requirement]` lowers each family:

| Family | Domain | Check |
|---|---|---|
| guarded | antecedent atoms | consequent |
| mandatory | `<type>_any(x)` | `holds fact(x, ...)` |
| subset | the left-hand atoms | `holds` right-hand atom |
| value | the fact | `holds <id>_allowed(x)` |
| internal uniqueness, non-spanning | two atoms sharing the key | `same` per non-key role |

- Refused with a named `ExportInputError`: every other family in this phase
  (frequency, ring, exclusion, and so on are PL13); structured derivations with
  `where`, `aggregate` or `clauses`; operations.
- Spanning uniqueness is skipped with a comment, since sets cannot hold
  duplicates. GND reports it.
- `render(model, target) -> str`. Both targets share the header, fact-type
  relationships, loaders, `<type>_any` universes (one `define` per role played)
  and `define` rules for structured derived fact types.
  - **`duckdb`:** each rule as a comment `where(...).require(...)`, then the denial
    query and a call to `report(...)`.
  - **`lqp`:** each rule as executable `m.where(...).require(...)`; config with
    `require_mode="report"` and `reasoners.logic.use_lqp=True`; a `--compile`
    mode; and a `--connection` mode that collects PyRel's requirement warnings.

### 6.2 CLI

`gnd export pyrel MODEL --out FILE [--rules duckdb|lqp]`. Without `--rules`,
the export is unchanged.

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | One emitted program with a mode, or two programs | two programs, as the owner asked; readable side by side |
| D2 | Duplicate-row semantics | sets; spanning uniqueness left to GND, and the header says so |
| D3 | LQP verification without an engine | front-end compile to `Require` nodes plus a structural match; execution is labelled engine-unverified |

## 8. Tests

`tests/test_pyrel_rules.py`. Rows marked oracle are `pyrel_oracle`.

| Case | Expected |
|---|---|
| 1. DuckDB program on the 11 BookRec and Expense corpus populations: statuses, witnesses and exit equal `gnd.api.check` (oracle) | pass |
| 2. LQP program `--compile` on BookRec, Expense and currency models: `Require` count equals the requirement count; domain relation names and check relation names match the requirement object (oracle) | pass |
| 3. Single source: the denial query and the requirement text come from the same `Requirement`, checked through each rule's printed `require` comment in the DuckDB program and its executable line in the LQP program | pass |
| 4. Unsupported family refused by name | exit 3 |
| 5. CLI writes new files only (an existing path exits 11); without `--rules`, behaviour is unchanged | pass |

## 9. Out of scope

Frequency, ring, exclusion, equality, xor, cardinality, subtype, recursion,
aggregates, calendar, reference populations and plans (PL13–PL15). Real
LQP-engine execution (owner lane).

## 10. Size

~400 source lines, ~200 test lines.

## 11. Approval instrument

This prose plus the §8 cases.

## Owner gate

Delegated approval (auto=true), 2026-10-14, under the owner's direction to
"write two versions, one that will require lqp and one that can run without
LQP". No spec panel.

## Implementation findings

- F1 PyRel's front-end compiles each statement passed to `require(...)` into its
  own `Require` node, so a uniqueness rule with two non-key roles compiles to two.
  `--compile` now checks against the expected count per rule.
- F2 Measured: GND treats a fact list missing from `covers` as empty, even when
  the document contains rows for it. The DuckDB program now keeps only covered
  lists and refuses a population that declares no `covers`. The first draft's
  invented `unknown` status was wrong and is removed.
- F3 The legacy LQP compiler documents error rules only for `unique_fields`
  requirements. The direct compiler lowers every requirement to
  `domain and not check => Error`. The LQP program therefore selects
  `reasoners.logic.lqp.compiler = "direct"`.
- F4 Refuted premise (§6.1): the first draft rendered structured derivations as
  `define`. GND compares claimed derived facts with computed ones (exit 4 on a
  mismatch), which a `define` does not reproduce. Derived models are now refused
  by name and move to PL13.
- F5 RF6 query policy: model reads go through `ModelIndex`. A constraint's own
  role list is read through a new static `ModelIndex.constraint_roles`, so the
  module adds no counted exception (headroom was 3 reads).
- F6 CLI pins: the RF1 goldens for `gnd export pyrel` help, exit probe and the CLI
  tree were updated for the new option, together with `goldens.sha256` and
  `MANIFEST_SHA256`. A fresh capture also differed on unrelated goldens
  (`gnd check` help order, datetime helpers); that drift predates this phase and
  was not taken.
