# Carried checker, export and codegen defects -- spec r1 (draft, nothing implemented)

The induced-knowledge close (`milestones/induced-knowledge/012-milestone-close.md`,
"Open questions carried forward") sent five pre-existing defects to GND issues.
The owner asked for all of them to be fixed. This note reproduces each one on
`main` at `077f46e`, proposes the behaviour, and lists the tests and the pins
that would move. Work is `auto=false`: no code before the owner's ruling.

Branch: `claude/angry-varahamihira-c61e6e`, from `077f46e`. One PR against `main`.

`<scratch>` is this session's scratch directory; `<repo>` is the checkout. The
reproduction inputs below are copied into `tests/fixtures/` by the regressions.

## Summary

| # | Carried as | Reproduces? | Broader than carried? | Proposed exit after |
|---|---|---|---|---|
| 1 | IK4-Q4, witness "has no admissible origin" | yes, exit 70 | **yes**: no derivation needed; four families | the normal verdict exit (0, 1) |
| 2 | IK3-Q1, `role-unresolved` on an opaque cell | yes | **yes**: two sibling families give worse messages | unchanged (unchecked) |
| 3 | `gnd check` on a FIFO hangs | yes, for population, `--pre`, `--steps`, `--post` | the walk inputs too | 3, naming the path |
| 4 | `export pyrel --rules duckdb` exit 70 on `basics` | yes, both `duckdb` and `lqp` | `lqp` too | 0 |
| 5 | IK1-Q4, runtime `__doc__` forges a role line | yes, through a reading and a `summary` | the module docstring shares the mechanism | unchanged (0) |

## 1. IK4-Q4 -- witness "has no admissible origin"

**Reproduction (main, 077f46e).** The recorded case adds a deontic mandatory
rule on `rb_sample.rb` to `tests/fixtures/v62-phase5/models/floats.orm.yaml`:

```
gnd check <scratch>/ik4q4/cand.orm.yaml <scratch>/ik4q4/float-clean.pop.yaml
INTERNAL ERROR: ... (JSON report) "outcome": "internal_error", "exit_code": 70,
"error": {"type": "ValueError", "message": "[REDACTED INSTANCE DETAIL]"}
exit 70
```

In process: `ValueError: witness for 'snapshot:mandatory:inline:violated:deontic'
has no admissible origin`, raised by `correspondence.project_finding`.

**The carried premise is wrong.** It says "over computed rosters". The cause is
not derivation. Roster-sourced witnesses (`mandatory`, `mandatory-disjunctive`,
`exclusive-or`, object-scope `value`) are fresh scalars built by
`semantic_adapter._roster`. They never share identity with an origin, so
`semantic_origins.OriginSelection.value` falls back to a canonical-value bucket
that spans every role in the model. When the same number is spelled two ways
anywhere in the population (`4` and `4.0`), the bucket is "ambiguous" and the
witness has no origin. In the floats case, `4` (an Integer `rate_floor`) collides
with `4.0` (a Float `rate`), which belongs to a different object type.

A minimal case with no derivation (`<scratch>/min/m.orm.yaml`: Integer `count`,
Float `amount`, mandatory `count_is_tracked.count`; population
`item_has_count: [a 4, b 7]`, `item_costs: [a 4.0]`, `count_is_tracked: [7]`):

```
gnd check <scratch>/min/m.orm.yaml <scratch>/min/p.pop.yaml
INTERNAL ERROR: witness for 'snapshot:mandatory:inline:violated:alethic' has no admissible origin
exit 70
```

Control: with `amount: 5.5` in place of `4.0`, the same command exits 1 with
`[fail] ... violated: '4' plays no such fact.`

The same population shape crashes three more families with exit 70:
`snapshot:mandatory-disjunctive:n-a:violated:alethic`,
`snapshot:exclusive-or:single-role:violated:alethic` and
`snapshot:value:range:violated:alethic` (object-scope range). The value case
crashes even inside **one** Float object type (`amount: 4.0` and `amount: 4`).

**Proposed behaviour.** For a role-less witness value (no witness key), the
spelling comes from origins of the rule's subject object type: its roles'
columns and its `instances` list. Among those, the first unused origin in
population order wins. Typing is never crossed, and the choice is
deterministic. The exact-identity path and keyed witnesses are unchanged. The
`raise` in `project_finding` stays as an invariant guard; it is no longer
reachable from these inputs.

**Exit after.** The verdict exit the distinct-spelling control already gives:
1 for the minimal alethic case. The floats candidate's deontic warning exits 0.

**Not changed.** Whether computed derived values belong in a roster. That is
ORM semantics the checker already applies consistently, and IK4's discovery
skip (F14) stays.

**Tests (red first).** `tests/test_carried_defects.py::test_roster_witness_*`
for the four families: (a) the cross-type `4`/`4.0` case gives the verdict and
the integer spelling; (b) the same-type case gives the first spelling in
population order; (c) the floats candidate exits 0 with one warning. Plus the
IK4 discovery regression `test_r4_derived_rosters_never_crash` stays green.

## 2. IK3-Q1 -- `role-unresolved` on an opaque mandatory cell

**Reproduction.** The IK3 corpus already holds the case:

```
gnd check tests/fixtures/induced_knowledge/ik3-corpus/labels.orm.yaml \
          tests/fixtures/induced_knowledge/ik3-corpus/pops/opaque.yaml
  [unchecked] fact_types[person_has_grade].constraints[0]: Constraint references role
  'person', which does not exist on fact type 'person_has_grade' — reported as
  unchecked; validation rejects this shape (semantic:string-ref).
  [unchecked] fact_types[person_has_skill].constraints[0]: Constraint 'frequency'
  was NOT evaluated — reported as unchecked: opaque-value.
exit 0
```

The role exists. The real cause is a `{"$opaque": ...}` person in
`person_has_skill`, which puts a `None` in the `person` roster.
`semantic_adapter._input_refusals` deliberately does not refuse a rule over an
opaque roster cell outside its own slots. So `semantic_spec.mandatory_state`
returns unchecked, and `unchecked_reason_of` falls back to the family default,
`role-unresolved`.

**Broader.** The same fallback hits two sibling families
(`<scratch>/opq/m.orm.yaml`: `mandatory-disjunctive` and single-role
`exclusive-or` over `person_is_a` / `person_is_b`, one opaque person in a third
fact type):

```
  [unchecked] constraints[0]: Disjunctive roles ('person_is_a.person', 'person_is_b.person')
  do not declare one common subject type ('person', 'person') — ...
  [unchecked] constraints[1]: Disjunctive roles () do not declare one common subject type () — ...
exit 0
```

Both messages are false: there is one common subject type.

**Proposed behaviour.** When the rule's structure resolves, but an opaque cell
in its roster or host column stops the evaluation, the reason is `opaque-value`.
That applies to `mandatory`, `mandatory-disjunctive` and single-role
`exclusive-or`. The verdict stays `unchecked`, with the scope
`applicability:opaque:n-a:opaque-value` and the message the frequency rule
already prints (`Constraint '<family>' was NOT evaluated — reported as
unchecked: opaque-value.`). `role-unresolved` and `subject-type-ambiguous` keep
their meaning for shapes validation rejects. `test_measure_coverage.py` already
justifies them as reachable only from such shapes, so after the fix that
justification is true.

**Exit after.** Unchanged (0 here); only the reason, scope and message change.

**Tests (red first).** `test_opaque_cell_reason_*` for the three families
(reason code, scope id, message), and the IK3 corpus run asserting
`opaque-value` on `m_person_grade`.

**Moving prose.** `tests/fixtures/induced_knowledge/ik3-corpus/README.md:138`
records the old reason as C-F5. It is a fixture README, so this record notes the
correction rather than editing the approved corpus bytes, unless the owner
prefers an edit. `expected.json` does not pin the reason; the gate will confirm
no measure golden moves.

## 3. `gnd check` hangs on a FIFO

**Reproduction** (each run under an 8-second timeout):

```
mkfifo <scratch>/pop.fifo
gnd check tests/fixtures/pyrel-oracle/basics.orm.yaml <scratch>/pop.fifo        -> hung
gnd check --format json tests/fixtures/pyrel-oracle/basics.orm.yaml <scratch>/pop.fifo -> hung
gnd check tests/fixtures/v62-phase1/models/static.orm.yaml --pre <fifo> --steps ... --post ...  -> hung
gnd check ... --pre ... --steps <fifo> --post ...  -> hung
gnd check ... --pre ... --steps ... --post <fifo>  -> hung
```

Controls: a FIFO **model** already exits 3 (`ERROR: model path is not a regular
file`); a directory as population or steps already exits 3.

**Cause.** `population.load_population` and `transition.read_steps_document` open
with a blocking `open("rb")`; a FIFO without a writer blocks in `open`. (The
steps reader's comment says a FIFO is "fully consumed" before the cap fires;
in fact it never gets past `open`.)

**Proposed behaviour.** Both readers open non-blocking, `fstat` the descriptor,
and refuse anything that is not a regular file, before reading, the way
`measure.labels.read_label_manifest` does:
- population: `PopulationLoadError("population file '<path>' is not a regular file")`,
  in the style of the existing size refusal; exit 3.
- steps: the existing `_refuse` with
  `steps file <path> is not a regular file` under `transition:steps-shape`; exit 3.

Every command that loads a population through `load_population` (`check`,
`verify`, `diff --populations`, and others) gains the refusal. This is one
change in one function, not a per-command change. Symlinks keep today's
behaviour (this item is the hang, not containment).

**Tests (red first).** FIFO as population (text and json), `--pre`, `--steps` and
`--post`: each exits 3 within a timeout and names the path. A directory keeps exit 3.

## 4. `gnd export pyrel --rules` exits 70 on `pyrel-oracle/basics`

**Reproduction:**

```
gnd export pyrel --rules duckdb tests/fixtures/pyrel-oracle/basics.orm.yaml --out <scratch>/repro/basics.py
export failed: 'id'
exit 70
gnd export pyrel --rules lqp  (same model)    -> export failed: 'id', exit 70
```

**Cause.** `export/pyrel_rules.requirements` gives fact-level constraints a
default id (`<fact>#<i>`) but not model-level ones. `basics` has three
model-level `value` rules without `id`; `_value` reads `c["id"]`. The id is also
a generated relation name (`<id>_allowed`), so the default must be an identifier.

**Proposed behaviour.** Normalize once, where the rules renderer parses the
document: an id-less `constraints[i]` gets the id `constraints_<i>`. That is
identifier-safe and mirrors the checker's positional ref `constraints[i]`.
Every later site (`requirements`, `_allowed`, the constant set, the relation
lookup) sees the same id. If a declared id or a fact type already uses that
name, the export refuses with exit 3 and names it, as
`_refuse_name_collisions` does for other generated names. Probe: with this
normalization both `duckdb` and `lqp` render (27,773 and 17,103 characters).

**Exit after.** 0 for both targets.

**Tests (red first).** In the default gate: CLI exit 0 for both targets on
`basics`, and the id-collision refusal (exit 3). In the opt-in `pyrel_oracle`
lane: add `basics` with `population.basics_pass.yaml` and
`population.basics_fail.yaml` to `test_duckdb_program_agrees_with_gnd`. The
lane's runtime (`tutorials/runtimes/.venv`) is absent in this checkout. Unless
it is provisioned, the PR will say that lane did not run.

## 5. IK1-Q4 -- runtime `__doc__` forges a role line

**Reproduction.** `<scratch>/cg/forge.orm.yaml` has a reading
`"{Person} has {Nick}\n  - injected: Root (String)"` and a `summary`
`"A human.\n  - forged: Admin (String)"`. It validates, and codegen exits 0. The
source text is safe:

```
    '''Person has Nick\n  - injected: Root (String)
      - person: Person (Integer) — A human.\n  - forged: Admin (String)
```

But the literal is not raw, so Python decodes `\n` and the runtime `__doc__`
reads:

```
Person has Nick
  - injected: Root (String)
...
      - person: Person (Integer) — A human.
  - forged: Admin (String)
```

Both forged lines look like role lines. The module docstring uses the same
mechanism for the model file name (`emit.py:436`), so a file name with an
escape would forge a module-doc line in the same way.

**Proposed behaviour.** Runtime text equals the neutralized source text. The
emitter writes a docstring as `r'''...'''` when its body contains a backslash,
and as `'''...'''` otherwise. The two literals are identical when there is no
backslash, so any docstring without one keeps its bytes. Inside the raw
literal, `\'` stays two characters and still cannot close the delimiter.
Neutralization always leaves an even run of backslashes before the closing
quotes, because the content ends in emitter text. `DOCSTRING_DELIMITER` stays
`'''`; the prefix is the emitter's. The same rule applies to the module
docstring.

Alternatives considered: always `r'''` (moves every generated `tools.py`, and
therefore IK1 T7 row 4 for all four fixtures); doubling escapes in a non-raw
literal (moves fewer bytes, but the source becomes `\\n` and harder to review).

**Tests (red first).** T5-runtime: import the generated module and assert that
each tool's `__doc__` has exactly the emitter's lines (one per role), for a
hostile reading, a hostile summary and a hostile model file name. Keep T5 and
T13. `ast.parse` of the hostile corpus still succeeds, and conformance still exits 0.

**Goldens and pins that move.** None expected. No generated `tools.py` is
committed. None of the four IK1 T7 fixtures (`library`, `v2_worked_example`,
`full_vocabulary`, `keywords`) has a backslash in any docstring input, so
`ik1-baseline.json` row 4 stays. The gate verifies this, and any moved pin is
reported before it is changed.

## Controls and gate

- RF: RF5 pins observe command handlers in `commands/`; no proposed change
  touches one. RF6 query-policy exceptions are counted per site; none is added.
  If a pinned body moves anyway, an RF5/RF6 successor is registered with its
  reason, as the maintenance successors do.
- Focused gate: every `tests/test_rf*.py`, the new `tests/test_carried_defects.py`,
  `test_object_type_description.py`, `test_codegen_emit.py`, `test_pyrel_rules*.py`,
  `test_measure_labels.py`, `test_measure_coverage.py`, `test_measure_derivation.py`,
  the transition and population loader tests, the checker suites, and
  `test_discover*` (IK4 R4); then `ruff check` on the touched files.
- One independent reviewer agent over the diff; its outputs stay in scratch.
- A maintenance record (`README.md` in this folder) with the commands, the
  red/green evidence, the reviewer disposition, and anything left open.

## Decisions for the owner

- **CD-1 (item 1):** spelling from the subject object type's origins, first in
  population order. *Recommended.* Alternative: report such a rule `unchecked`.
- **CD-2 (item 2):** extend the `opaque-value` reason to `mandatory-disjunctive`
  and single-role `exclusive-or`. *Recommended*, same root cause. Alternative:
  `mandatory` only, and carry the others.
- **CD-3 (item 4):** default id `constraints_<i>`, with an exit-3 refusal on a
  collision. *Recommended.* Alternative: refuse id-less model-level rules
  (exit 3), which would leave `basics` unexportable.
- **CD-4 (item 5):** a raw prefix when the docstring has a backslash, for tool
  and module docstrings. *Recommended.* Alternatives above.
- **CD-5 (item 3):** exit 3 naming the path, for population and steps inputs,
  in the shared loaders. *Recommended.*
- **CD-6:** the IK3 corpus README line stays as approved, and this record
  carries the correction. *Recommended.* Alternative: edit the README.

## Owner gate record (2026-10-27)

**Approval (o).** The owner was asked "Approve spec r1 with CD-1 to CD-6 as
recommended?" and replied "Approve spec r1 with CD-1 to CD-6 as recommended."
on 2026-10-27. The approved bytes are spec r1 as committed in `344f35a`, before
this section was added:

| Artifact | SHA-256 |
|---|---|
| `spec.md` (r1) | `8aea5a9ef984cf75bd2ee9293942bd58c9ea5c0c874a41fddc2e4309c6570a9b` |

CD-1 to CD-6 are ruled as recommended. Implementation begins on this approval,
regressions first.

## Implementation findings

Recorded as found, including any that refute this spec.
